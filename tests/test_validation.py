from dataclasses import replace
from pathlib import Path

from incident_intelligence.dataset import (
    load_annotations,
    validate_annotations,
)
from incident_intelligence.models import IncidentAnnotation


def make_valid_record() -> IncidentAnnotation:
    return IncidentAnnotation(
        incident_id="INC-TEST",
        report="Pump discharge pressure dropped unexpectedly during operation.",
        component="pump",
        failure_mode="pressure_drop",
        severity="medium",
        urgency="within_24_hours",
        probable_cause="unknown",
        evidence=["discharge pressure dropped unexpectedly"],
        recommended_action=(
            "inspect the system and collect additional evidence"
        ),
        confidence=0.75,
        abstain=True,
        requires_human_review=True,
        review_notes=(
            "The pressure loss is clear, but the cause is unknown."
        ),
    )


def test_sample_dataset_is_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    dataset_path = (
        root / "data" / "ground_truth" / "incidents.json"
    )

    records = load_annotations(dataset_path)

    assert validate_annotations(records) == []


def test_invalid_component_is_rejected() -> None:
    record = replace(
        make_valid_record(),
        component="warp_drive",
    )

    assert "invalid component: warp_drive" in record.validate()


def test_invalid_failure_mode_is_rejected() -> None:
    record = replace(
        make_valid_record(),
        failure_mode="dimensional_rift",
    )

    assert (
        "invalid failure_mode: dimensional_rift"
        in record.validate()
    )


def test_blank_evidence_is_rejected() -> None:
    record = replace(
        make_valid_record(),
        evidence=[""],
    )

    assert "evidence items must not be blank" in record.validate()


def test_abstention_requires_human_review() -> None:
    record = replace(
        make_valid_record(),
        requires_human_review=False,
    )

    assert (
        "abstained records must require human review"
        in record.validate()
    )


def test_abstention_requires_review_notes() -> None:
    record = replace(
        make_valid_record(),
        review_notes="",
    )

    assert (
        "abstained records must include review_notes"
        in record.validate()
    )


def test_unknown_cause_requires_human_review() -> None:
    record = replace(
        make_valid_record(),
        abstain=False,
        requires_human_review=False,
    )

    assert (
        "unknown probable cause must require human review"
        in record.validate()
    )


def test_critical_incident_requires_immediate_urgency() -> None:
    record = replace(
        make_valid_record(),
        severity="critical",
        urgency="within_24_hours",
    )

    assert (
        "critical incidents must have immediate urgency"
        in record.validate()
    )


def test_duplicate_incident_id_is_rejected() -> None:
    first = make_valid_record()
    second = replace(
        make_valid_record(),
        report="A different pressure incident occurred in the system.",
    )

    errors = validate_annotations([first, second])

    assert "INC-TEST: duplicate incident_id" in errors


def test_duplicate_report_text_is_rejected() -> None:
    first = make_valid_record()
    second = replace(
        make_valid_record(),
        incident_id="INC-TEST-2",
        report=(
            "  PUMP discharge pressure dropped unexpectedly "
            "during operation.  "
        ),
    )

    errors = validate_annotations([first, second])

    assert "INC-TEST-2: duplicate report text" in errors