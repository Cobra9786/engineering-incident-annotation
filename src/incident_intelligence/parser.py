from __future__ import annotations

import json
from typing import Any

from .models import (
    CURRENT_SCHEMA_VERSION,
    IncidentAnnotation,
)


class PredictionParseError(ValueError):
    pass


MODEL_OUTPUT_FIELDS = {
    "component",
    "failure_mode",
    "severity",
    "urgency",
    "probable_cause",
    "evidence",
    "recommended_action",
    "confidence",
    "abstain",
    "requires_human_review",
    "review_notes",
}


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()

    if stripped.startswith("```"):
        lines = stripped.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        stripped = "\n".join(lines).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise PredictionParseError(
            "model response did not contain a JSON object"
        )

    candidate = stripped[start : end + 1]

    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise PredictionParseError(
            f"model response contained invalid JSON: {error}"
        ) from error

    if not isinstance(payload, dict):
        raise PredictionParseError(
            "model JSON root must be an object"
        )

    return payload


def validate_model_payload_types(
    payload: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    missing_fields = sorted(
        MODEL_OUTPUT_FIELDS - payload.keys()
    )

    for field in missing_fields:
        errors.append(f"missing required field: {field}")

    unexpected_fields = sorted(
        payload.keys() - MODEL_OUTPUT_FIELDS
    )

    for field in unexpected_fields:
        errors.append(f"unexpected model field: {field}")

    string_fields = {
        "component",
        "failure_mode",
        "severity",
        "urgency",
        "probable_cause",
        "recommended_action",
        "review_notes",
    }

    for field in string_fields:
        if field not in payload:
            continue

        value = payload[field]

        if not isinstance(value, str):
            errors.append(
                f"{field} must be a string, got "
                f"{type(value).__name__}"
            )

    boolean_fields = {
        "abstain",
        "requires_human_review",
    }

    for field in boolean_fields:
        if field not in payload:
            continue

        value = payload[field]

        if not isinstance(value, bool):
            errors.append(
                f"{field} must be a boolean, got "
                f"{type(value).__name__}"
            )

    if "confidence" in payload:
        confidence = payload["confidence"]

        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
        ):
            errors.append(
                "confidence must be a number, got "
                f"{type(confidence).__name__}"
            )

    if "evidence" in payload:
        evidence = payload["evidence"]

        if not isinstance(evidence, list):
            errors.append(
                "evidence must be an array, got "
                f"{type(evidence).__name__}"
            )
        elif not all(
            isinstance(item, str)
            for item in evidence
        ):
            errors.append(
                "every evidence item must be a string"
            )

    return errors


def parse_incident_prediction(
    text: str,
    *,
    incident_id: str,
    report: str,
) -> IncidentAnnotation:
    payload = extract_json_object(text)

    type_errors = validate_model_payload_types(payload)

    if type_errors:
        raise PredictionParseError(
            "model prediction failed type validation: "
            + "; ".join(type_errors)
        )

    complete_payload = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "incident_id": incident_id,
        "report": report,
        **payload,
    }

    try:
        prediction = IncidentAnnotation.from_dict(
            complete_payload
        )
    except TypeError as error:
        raise PredictionParseError(
            "model JSON did not match the annotation contract: "
            f"{error}"
        ) from error

    validation_errors = prediction.validate()

    if validation_errors:
        raise PredictionParseError(
            "model prediction failed business validation: "
            + "; ".join(validation_errors)
        )

    return prediction