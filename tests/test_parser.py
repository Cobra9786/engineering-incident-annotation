import json

import pytest

from incident_intelligence.parser import (
    PredictionParseError,
    extract_json_object,
    parse_incident_prediction,
)

TEST_INCIDENT_ID = "INC-TEST"
TEST_REPORT = (
    "Pump discharge pressure dropped and oil was "
    "visible near the shaft seal."
)


def valid_payload() -> dict[str, object]:
    return {
        "component": "pump",
        "failure_mode": "seal_leak",
        "severity": "high",
        "urgency": "immediate",
        "probable_cause": "shaft seal failure",
        "evidence": [
            "discharge pressure dropped",
            "oil was visible near the shaft seal",
        ],
        "recommended_action": (
            "shut down and inspect the shaft seal"
        ),
        "confidence": 0.96,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "Visible oil supports a physical seal leak."
        ),
    }


def test_extract_json_object() -> None:
    payload = valid_payload()
    text = json.dumps(payload)

    assert extract_json_object(text) == payload


def test_extract_json_from_markdown_fence() -> None:
    payload = valid_payload()
    text = "```json\n" + json.dumps(payload) + "\n```"

    assert extract_json_object(text) == payload


def test_parse_valid_prediction() -> None:
    prediction = parse_incident_prediction(
        json.dumps(valid_payload()),
        incident_id=TEST_INCIDENT_ID,
        report=TEST_REPORT,
    )

    assert prediction.failure_mode == "seal_leak"


def test_missing_json_is_rejected() -> None:
    with pytest.raises(
        PredictionParseError,
        match="did not contain a JSON object",
    ):
        extract_json_object("No structured result available.")


def test_array_component_is_rejected() -> None:
    payload = valid_payload()
    payload["component"] = ["pump", "pipeline"]

    with pytest.raises(
        PredictionParseError,
        match="component must be a string",
    ):
        parse_incident_prediction(
            json.dumps(payload),
            incident_id=TEST_INCIDENT_ID,
            report=TEST_REPORT,
        )


def test_array_failure_mode_is_rejected() -> None:
    payload = valid_payload()
    payload["failure_mode"] = ["pressure_drop"]

    with pytest.raises(
        PredictionParseError,
        match="failure_mode must be a string",
    ):
        parse_incident_prediction(
            json.dumps(payload),
            incident_id=TEST_INCIDENT_ID,
            report=TEST_REPORT,
        )