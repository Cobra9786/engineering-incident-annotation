from dataclasses import asdict

from incident_intelligence.models import IncidentAnnotation

# The script owns production evaluation orchestration, so load its public helper.
from scripts.evaluate_rag_baseline import apply_deterministic_policy


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
