#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.dataset import load_annotations
from incident_intelligence.knowledge import load_knowledge_documents
from incident_intelligence.models import IncidentAnnotation
from incident_intelligence.parser import PredictionParseError, parse_incident_prediction
from incident_intelligence.prompt import build_incident_prompt
from incident_intelligence.qwen import DEFAULT_MODEL_ID, QwenIncidentGenerator
from incident_intelligence.retrieval import SemanticKnowledgeRetriever
from incident_intelligence.severity_policy import (
    SeverityDecision,
    assign_severity_and_urgency,
)


DEFAULT_HELD_OUT_PATH = ROOT / "data" / "splits" / "held_out_test.json"
DEFAULT_KNOWLEDGE_DIR = ROOT / "knowledge" / "documents"
DEFAULT_OUTPUT_PATH = ROOT / "artifacts" / "evaluation" / "rag_baseline_comparison.json"
SCORED_FIELDS = (
    "component",
    "failure_mode",
    "severity",
    "urgency",
    "abstain",
    "requires_human_review",
)
VARIANTS = ("prompt_only", "diagnostics_only", "diagnostics_plus_policy")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare prompt-only, diagnostic retrieval, and deterministic policy inference."
    )
    parser.add_argument("--held-out", type=Path, default=DEFAULT_HELD_OUT_PATH)
    parser.add_argument("--knowledge-dir", type=Path, default=DEFAULT_KNOWLEDGE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


def apply_deterministic_policy(
    prediction: IncidentAnnotation,
) -> tuple[IncidentAnnotation, SeverityDecision]:
    """Apply severity policy and reconcile dependent review state."""
    decision = assign_severity_and_urgency(
        report=prediction.report,
        component=prediction.component,
        failure_mode=prediction.failure_mode,
    )
    requires_human_review = (
        prediction.abstain
        or decision.severity in {"high", "critical"}
        or prediction.probable_cause == "unknown"
    )
    review_notes = _reconcile_review_notes(
        prediction=prediction,
        final_severity=decision.severity,
        requires_human_review=requires_human_review,
    )
    return (
        replace(
            prediction,
            severity=decision.severity,
            urgency=decision.urgency,
            requires_human_review=requires_human_review,
            review_notes=review_notes,
        ),
        decision,
    )


def _reconcile_review_notes(
    *,
    prediction: IncidentAnnotation,
    final_severity: str,
    requires_human_review: bool,
) -> str:
    if not requires_human_review:
        return ""

    severity_changed = prediction.severity != final_severity
    normalized_notes = " ".join(prediction.review_notes.casefold().split())
    cites_old_severity = severity_changed and (
        f"{prediction.severity} severity" in normalized_notes
        or f"severity is {prediction.severity}" in normalized_notes
    )
    if not cites_old_severity:
        return prediction.review_notes

    if prediction.abstain:
        return "Human review required because the model abstained."
    if final_severity in {"high", "critical"}:
        return "Human review required by final severity."
    return "Human review required because probable cause is unknown."


def timestamped_output_path(
    stable_output_path: Path,
    *,
    run_timestamp: datetime,
    top_k: int,
) -> Path:
    timestamp = run_timestamp.astimezone(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return stable_output_path.with_name(
        f"{stable_output_path.stem}_{timestamp}_topk{top_k}"
        f"{stable_output_path.suffix}"
    )


def _generate_and_parse(
    *,
    generator: QwenIncidentGenerator,
    expected: IncidentAnnotation,
    knowledge_context: str | None,
    max_new_tokens: int,
) -> tuple[dict[str, Any], IncidentAnnotation | None]:
    prompt = build_incident_prompt(
        incident_id=expected.incident_id,
        report=expected.report,
        knowledge_context=knowledge_context,
    )
    generation = generator.generate(prompt, max_new_tokens=max_new_tokens)
    result: dict[str, Any] = {
        "raw_model_output": generation.text,
        "parse_valid": False,
        "validation_error": None,
        "prediction": None,
        "prompt_tokens": generation.prompt_tokens,
        "generated_tokens": generation.generated_tokens,
        "latency_seconds": generation.latency_seconds,
    }
    try:
        prediction = parse_incident_prediction(
            generation.text,
            incident_id=expected.incident_id,
            report=expected.report,
        )
    except PredictionParseError as error:
        result["validation_error"] = str(error)
        return result, None

    result["parse_valid"] = True
    result["prediction"] = asdict(prediction)
    return result, prediction


def _policy_result(
    diagnostic_result: dict[str, Any],
    prediction: IncidentAnnotation | None,
) -> dict[str, Any]:
    result = dict(diagnostic_result)
    result["source_variant"] = "diagnostics_only"
    result["policy"] = None
    if prediction is None:
        return result

    final_prediction, decision = apply_deterministic_policy(prediction)
    result["prediction"] = asdict(final_prediction)
    result["policy"] = {
        "rule_id": decision.rule_id,
        "rationale": decision.rationale,
        "severity_before_policy": prediction.severity,
        "urgency_before_policy": prediction.urgency,
        "severity_after_policy": final_prediction.severity,
        "urgency_after_policy": final_prediction.urgency,
    }
    post_policy_errors = final_prediction.validate()
    result["post_policy_valid"] = not post_policy_errors
    result["post_policy_validation_errors"] = post_policy_errors
    return result


def _field_accuracy(
    records: list[dict[str, Any]],
    variant: str,
    field: str,
) -> float:
    return sum(
        _variant_is_valid(record["variants"][variant], variant)
        and record["variants"][variant]["prediction"][field]
        == record["ground_truth"][field]
        for record in records
    ) / len(records)


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        variant: {
            "validity_rate": sum(
                _variant_is_valid(record["variants"][variant], variant)
                for record in records
            ) / len(records),
            "field_accuracy": {
                field: _field_accuracy(records, variant, field)
                for field in SCORED_FIELDS
            },
        }
        for variant in VARIANTS
    }


def _variant_is_valid(result: dict[str, Any], variant: str) -> bool:
    if variant == "diagnostics_plus_policy":
        return bool(result.get("post_policy_valid", False))
    return bool(result["parse_valid"])


def main() -> int:
    args = parse_args()
    run_timestamp = datetime.now(UTC)
    expected_records = load_annotations(args.held_out)
    if not expected_records:
        raise ValueError("held-out dataset is empty")

    documents = [
        document
        for document in load_knowledge_documents(args.knowledge_dir)
        if document.document_id != "severity_and_urgency_guidance"
    ]
    if not documents:
        raise ValueError("no diagnostic knowledge documents found")

    retriever = SemanticKnowledgeRetriever(documents)
    generator = QwenIncidentGenerator(model_id=args.model_id)
    records: list[dict[str, Any]] = []

    for index, expected in enumerate(expected_records, start=1):
        print(f"[{index}/{len(expected_records)}] {expected.incident_id}")
        retrieved = retriever.retrieve(expected.report, top_k=args.top_k)
        context = "\n\n".join(item.text for item in retrieved)

        prompt_result, _ = _generate_and_parse(
            generator=generator,
            expected=expected,
            knowledge_context=None,
            max_new_tokens=args.max_new_tokens,
        )
        diagnostics_result, diagnostics_prediction = _generate_and_parse(
            generator=generator,
            expected=expected,
            knowledge_context=context,
            max_new_tokens=args.max_new_tokens,
        )
        records.append(
            {
                "incident_id": expected.incident_id,
                "ground_truth": asdict(expected),
                "retrieved_diagnostics": [asdict(item) for item in retrieved],
                "variants": {
                    "prompt_only": prompt_result,
                    "diagnostics_only": diagnostics_result,
                    "diagnostics_plus_policy": _policy_result(
                        diagnostics_result, diagnostics_prediction
                    ),
                },
            }
        )

    payload = {
        "run": {
            "timestamp": run_timestamp.isoformat(),
            "model_id": args.model_id,
            "held_out_path": str(args.held_out),
            "knowledge_directory": str(args.knowledge_dir),
            "severity_guidance_retrieved": False,
            "primary_variant": "diagnostics_plus_policy",
            "top_k": args.top_k,
        },
        "summary": _summary(records),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    serialized_payload = json.dumps(payload, indent=2) + "\n"
    timestamped_output = timestamped_output_path(
        args.output,
        run_timestamp=run_timestamp,
        top_k=args.top_k,
    )
    with timestamped_output.open("x", encoding="utf-8") as artifact_file:
        artifact_file.write(serialized_payload)
    args.output.write_text(serialized_payload, encoding="utf-8")

    print(json.dumps(payload["summary"], indent=2))
    print(f"Timestamped artifact: {timestamped_output}")
    print(f"Latest stable alias: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
