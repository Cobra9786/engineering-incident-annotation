from incident_intelligence.evaluation import exact_field_accuracy
from incident_intelligence.models import IncidentAnnotation


def make_record(severity: str) -> IncidentAnnotation:
    return IncidentAnnotation(
        schema_version="1.0.0",
        incident_id="INC-X",
        report="Pressure dropped unexpectedly during operation.",
        component="pump",
        failure_mode="pressure_drop",
        severity=severity,
        urgency="within_24_hours",
        probable_cause="unknown",
        evidence=["pressure dropped unexpectedly"],
        recommended_action="inspect the system",
        confidence=0.8,
        abstain=False,
        requires_human_review=True,
        review_notes="",
    )


def test_accuracy() -> None:
    expected = [
        make_record("medium"),
        make_record("high"),
    ]

    predicted = [
        make_record("medium"),
        make_record("medium"),
    ]

    assert (
        exact_field_accuracy(
            expected,
            predicted,
            "severity",
        )
        == 0.5
    )