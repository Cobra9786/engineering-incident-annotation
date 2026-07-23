from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from incident_intelligence.models import IncidentAnnotation

# The script owns production evaluation orchestration, so load its public helper.
from scripts.evaluate_rag_baseline import (
    _field_accuracy,
    _variant_is_valid,
    apply_deterministic_policy,
    timestamped_output_path,
)


def make_prediction(**changes: object) -> IncidentAnnotation:
    prediction = IncidentAnnotation(
        schema_version="1.0.0",
        incident_id="INC-TEST",
        report=(
            "The pressure reading fell to zero while a mechanical gauge remained "
            "stable, and the sensor connector was loose."
        ),
        component="pressure_sensor",
        failure_mode="signal_loss",
        severity="high",
        urgency="immediate",
        probable_cause="loose sensor connector",
        evidence=["the pressure reading fell to zero"],
        recommended_action="secure the connector and verify sensor output",
        confidence=0.95,
        abstain=False,
        requires_human_review=True,
        review_notes="High severity requires human review.",
    )
    return replace(prediction, **changes)


def test_policy_changes_only_severity_and_urgency() -> None:
    prediction = IncidentAnnotation(
        schema_version="1.0.0",
        incident_id="INC-TEST",
        report=(
            "Pressure downstream of the control valve is low. The commanded valve "
            "position is 80 percent, but physical position feedback remains at 12 percent."
        ),
        component="valve",
        failure_mode="mechanical_jam",
        severity="medium",
        urgency="within_24_hours",
        probable_cause="stuck valve mechanism",
        evidence=["position feedback remains at 12 percent"],
        recommended_action="inspect the valve actuator",
        confidence=0.91,
        abstain=False,
        requires_human_review=True,
        review_notes="The command and feedback disagree.",
    )

    updated, decision = apply_deterministic_policy(prediction)
    before = asdict(prediction)
    after = asdict(updated)
    changed = {field for field in before if before[field] != after[field]}

    assert changed == {"severity", "urgency"}
    assert (updated.severity, updated.urgency) == ("high", "immediate")
    assert decision.rule_id == "high.commanded_valve_mismatch_with_control_loss"


def test_medium_policy_result_clears_stale_review_state() -> None:
    updated, _ = apply_deterministic_policy(make_prediction())

    assert updated.severity == "medium"
    assert updated.urgency == "within_24_hours"
    assert updated.abstain is False
    assert updated.probable_cause == "loose sensor connector"
    assert updated.requires_human_review is False
    assert updated.review_notes == ""
    assert updated.validate() == []


@pytest.mark.parametrize(
    ("report", "expected_severity"),
    [
        (
            "Production is interrupted while the controller fault remains active.",
            "high",
        ),
        (
            "Operators initiated an emergency shutdown after the controller fault.",
            "critical",
        ),
    ],
)
def test_high_or_critical_policy_result_requires_review(
    report: str,
    expected_severity: str,
) -> None:
    updated, _ = apply_deterministic_policy(
        make_prediction(
            report=report,
            component="controller",
            failure_mode="software_fault",
            severity="low",
            urgency="routine",
            requires_human_review=False,
            review_notes="",
        )
    )

    assert updated.severity == expected_severity
    assert updated.requires_human_review is True
    assert updated.validate() == []


def test_unknown_probable_cause_still_requires_review() -> None:
    updated, _ = apply_deterministic_policy(
        make_prediction(
            probable_cause="unknown",
            review_notes="Cause requires confirmation.",
        )
    )

    assert updated.severity == "medium"
    assert updated.requires_human_review is True
    assert updated.review_notes == "Cause requires confirmation."
    assert updated.validate() == []


def test_abstention_still_requires_review() -> None:
    updated, _ = apply_deterministic_policy(
        make_prediction(
            abstain=True,
            probable_cause="unknown",
            review_notes="The available evidence is insufficient.",
        )
    )

    assert updated.requires_human_review is True
    assert updated.review_notes == "The available evidence is insufficient."
    assert updated.validate() == []


def test_timestamped_output_path_is_utc_safe_and_includes_top_k() -> None:
    result = timestamped_output_path(
        Path("artifacts/evaluation/rag_baseline_comparison.json"),
        run_timestamp=datetime(
            2026,
            7,
            22,
            1,
            55,
            24,
            123456,
            tzinfo=UTC,
        ),
        top_k=1,
    )

    assert result == Path(
        "artifacts/evaluation/"
        "rag_baseline_comparison_20260722T015524123456Z_topk1.json"
    )


def test_policy_variant_validity_uses_post_policy_validation() -> None:
    result = {
        "parse_valid": True,
        "post_policy_valid": False,
    }

    assert _variant_is_valid(result, "diagnostics_plus_policy") is False
    assert _variant_is_valid(result, "diagnostics_only") is True
    assert _variant_is_valid(result, "prompt_only") is True


def test_invalid_post_policy_record_receives_no_field_accuracy_credit() -> None:
    records = [
        {
            "ground_truth": {"severity": "medium"},
            "variants": {
                "diagnostics_plus_policy": {
                    "parse_valid": True,
                    "post_policy_valid": False,
                    "prediction": {"severity": "medium"},
                }
            },
        }
    ]

    assert (
        _field_accuracy(
            records,
            "diagnostics_plus_policy",
            "severity",
        )
        == 0.0
    )
