#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.dataset import load_annotations
from incident_intelligence.models import IncidentAnnotation
from incident_intelligence.parser import (
    PredictionParseError,
    parse_incident_prediction,
)
from incident_intelligence.prompt import build_incident_prompt
from incident_intelligence.qwen import (
    DEFAULT_MODEL_ID,
    QwenIncidentGenerator,
)


DEFAULT_HELD_OUT_PATH = (
    ROOT / "data" / "splits" / "held_out_test.json"
)

DEFAULT_OUTPUT_DIR = (
    ROOT / "evaluation_runs" / "prompt_v1"
)

EXACT_MATCH_FIELDS = (
    "component",
    "failure_mode",
    "severity",
    "urgency",
    "abstain",
    "requires_human_review",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the local Qwen prompt-only baseline across "
            "the held-out engineering incident dataset."
        )
    )

    parser.add_argument(
        "--held-out",
        type=Path,
        default=DEFAULT_HELD_OUT_PATH,
        help="Path to the held-out ground-truth JSON file.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for predictions, metrics, and summary.",
    )

    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Hugging Face model ID.",
    )

    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
        help="Maximum number of generated tokens per incident.",
    )

    return parser.parse_args()


def field_matches(
    expected: IncidentAnnotation,
    predicted: IncidentAnnotation,
) -> dict[str, bool]:
    return {
        field: getattr(expected, field) == getattr(predicted, field)
        for field in EXACT_MATCH_FIELDS
    }


def run_one_incident(
    *,
    generator: QwenIncidentGenerator,
    expected: IncidentAnnotation,
    max_new_tokens: int,
) -> dict[str, Any]:
    prompt = build_incident_prompt(
        incident_id=expected.incident_id,
        report=expected.report,
    )

    generation = generator.generate(
        prompt,
        max_new_tokens=max_new_tokens,
    )

    result: dict[str, Any] = {
        "incident_id": expected.incident_id,
        "model_id": generation.model_id,
        "ground_truth": asdict(expected),
        "raw_model_output": generation.text,
        "prompt_tokens": generation.prompt_tokens,
        "generated_tokens": generation.generated_tokens,
        "latency_seconds": generation.latency_seconds,
        "parse_valid": False,
        "prediction": None,
        "validation_error": None,
        "field_matches": {
            field: False
            for field in EXACT_MATCH_FIELDS
        },
    }

    try:
        prediction = parse_incident_prediction(
            generation.text,
            incident_id=expected.incident_id,
            report=expected.report,
        )
    except PredictionParseError as error:
        result["validation_error"] = str(error)
        return result

    result["parse_valid"] = True
    result["prediction"] = asdict(prediction)
    result["field_matches"] = field_matches(
        expected,
        prediction,
    )

    return result


def calculate_metrics(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    if not results:
        raise ValueError("cannot calculate metrics for an empty run")

    total = len(results)
    valid_results = [
        result
        for result in results
        if result["parse_valid"]
    ]

    valid_count = len(valid_results)

    field_accuracy = {
        field: (
            sum(
                bool(result["field_matches"][field])
                for result in results
            )
            / total
        )
        for field in EXACT_MATCH_FIELDS
    }

    conditional_field_accuracy = {
        field: (
            sum(
                bool(result["field_matches"][field])
                for result in valid_results
            )
            / valid_count
            if valid_count
            else 0.0
        )
        for field in EXACT_MATCH_FIELDS
    }

    latencies = [
        float(result["latency_seconds"])
        for result in results
    ]

    prompt_tokens = [
        int(result["prompt_tokens"])
        for result in results
    ]

    generated_tokens = [
        int(result["generated_tokens"])
        for result in results
    ]

    exact_record_matches = sum(
        result["parse_valid"]
        and all(result["field_matches"].values())
        for result in results
    )

    return {
        "held_out_count": total,
        "valid_prediction_count": valid_count,
        "invalid_prediction_count": total - valid_count,
        "json_and_contract_validity_rate": valid_count / total,
        "exact_record_match_rate": exact_record_matches / total,
        "field_accuracy_all_incidents": field_accuracy,
        "field_accuracy_valid_predictions_only": (
            conditional_field_accuracy
        ),
        "average_latency_seconds": mean(latencies),
        "minimum_latency_seconds": min(latencies),
        "maximum_latency_seconds": max(latencies),
        "total_prompt_tokens": sum(prompt_tokens),
        "total_generated_tokens": sum(generated_tokens),
        "average_prompt_tokens": mean(prompt_tokens),
        "average_generated_tokens": mean(generated_tokens),
    }


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_summary(
    *,
    model_id: str,
    run_timestamp: str,
    metrics: dict[str, Any],
    results: list[dict[str, Any]],
) -> str:
    lines = [
        "# Prompt Baseline v1",
        "",
        f"- Model: `{model_id}`",
        f"- Run timestamp: `{run_timestamp}`",
        (
            "- Held-out incidents: "
            f"{metrics['held_out_count']}"
        ),
        (
            "- Valid predictions: "
            f"{metrics['valid_prediction_count']}"
        ),
        (
            "- Invalid predictions: "
            f"{metrics['invalid_prediction_count']}"
        ),
        (
            "- JSON and contract validity: "
            f"{format_percent(metrics['json_and_contract_validity_rate'])}"
        ),
        (
            "- Exact record match rate: "
            f"{format_percent(metrics['exact_record_match_rate'])}"
        ),
        (
            "- Average latency: "
            f"{metrics['average_latency_seconds']:.3f} seconds"
        ),
        "",
        "## Field Accuracy",
        "",
        "| Field | Accuracy |",
        "|---|---:|",
    ]

    field_accuracy = metrics[
        "field_accuracy_all_incidents"
    ]

    for field in EXACT_MATCH_FIELDS:
        lines.append(
            f"| `{field}` | "
            f"{format_percent(field_accuracy[field])} |"
        )

    lines.extend(
        [
            "",
            "## Incident Results",
            "",
        ]
    )

    for result in results:
        incident_id = result["incident_id"]

        lines.append(f"### {incident_id}")
        lines.append("")

        if not result["parse_valid"]:
            lines.append(
                f"- Status: invalid prediction"
            )
            lines.append(
                "- Error: "
                f"`{result['validation_error']}`"
            )
            lines.append(
                "- Latency: "
                f"{result['latency_seconds']:.3f} seconds"
            )
            lines.append("")
            continue

        mismatches = [
            field
            for field, matched
            in result["field_matches"].items()
            if not matched
        ]

        if mismatches:
            lines.append(
                "- Status: valid prediction with mismatches"
            )
            lines.append(
                "- Mismatched fields: "
                + ", ".join(
                    f"`{field}`"
                    for field in mismatches
                )
            )
        else:
            lines.append(
                "- Status: exact match on scored fields"
            )

        ground_truth = result["ground_truth"]
        prediction = result["prediction"]

        for field in EXACT_MATCH_FIELDS:
            if result["field_matches"][field]:
                continue

            lines.append(
                f"- `{field}`: "
                f"expected `{ground_truth[field]}`, "
                f"predicted `{prediction[field]}`"
            )

        lines.append(
            "- Latency: "
            f"{result['latency_seconds']:.3f} seconds"
        )
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "This run is the prompt-only reference baseline. "
                "Future RAG, LoRA, and LoRA-plus-RAG configurations "
                "must be evaluated against the same held-out records "
                "and the same annotation contract."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def write_json(
    path: Path,
    payload: object,
) -> None:
    path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()

    if not args.held_out.exists():
        print(
            f"Held-out dataset does not exist: {args.held_out}",
            file=sys.stderr,
        )
        return 1

    expected_records = load_annotations(
        args.held_out
    )

    if not expected_records:
        print(
            "Held-out dataset is empty.",
            file=sys.stderr,
        )
        return 1

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    generator = QwenIncidentGenerator(
        model_id=args.model_id,
    )

    run_timestamp = datetime.now(UTC).isoformat()

    results: list[dict[str, Any]] = []

    for index, expected in enumerate(
        expected_records,
        start=1,
    ):
        print(
            f"[{index}/{len(expected_records)}] "
            f"Running {expected.incident_id}..."
        )

        result = run_one_incident(
            generator=generator,
            expected=expected,
            max_new_tokens=args.max_new_tokens,
        )

        results.append(result)

        status = (
            "valid"
            if result["parse_valid"]
            else "invalid"
        )

        print(
            f"  {status}; "
            f"{result['latency_seconds']:.3f} seconds"
        )

    metrics = calculate_metrics(results)

    run_metadata = {
        "run_name": "prompt_v1",
        "run_timestamp": run_timestamp,
        "model_id": args.model_id,
        "held_out_path": str(
            args.held_out.relative_to(ROOT)
        ),
        "max_new_tokens": args.max_new_tokens,
        "generation_mode": "greedy",
        "temperature": None,
        "do_sample": False,
    }

    predictions_payload = {
        "run": run_metadata,
        "results": results,
    }

    metrics_payload = {
        "run": run_metadata,
        "metrics": metrics,
    }

    summary = build_summary(
        model_id=args.model_id,
        run_timestamp=run_timestamp,
        metrics=metrics,
        results=results,
    )

    write_json(
        args.output_dir / "predictions.json",
        predictions_payload,
    )

    write_json(
        args.output_dir / "metrics.json",
        metrics_payload,
    )

    (
        args.output_dir / "summary.md"
    ).write_text(
        summary,
        encoding="utf-8",
    )

    print()
    print("Baseline run complete.")
    print(
        "Validity rate: "
        f"{format_percent(metrics['json_and_contract_validity_rate'])}"
    )
    print(
        "Average latency: "
        f"{metrics['average_latency_seconds']:.3f} seconds"
    )
    print(f"Results: {args.output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())