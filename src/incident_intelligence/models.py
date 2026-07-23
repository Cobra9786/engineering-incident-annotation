from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CURRENT_SCHEMA_VERSION = "1.0.0"

ALLOWED_COMPONENTS = {
    "pump",
    "valve",
    "pressure_sensor",
    "temperature_sensor",
    "motor",
    "actuator",
    "battery",
    "controller",
    "hydraulic_cylinder",
    "power_supply",
    "communications_link",
    "pipeline",
    "reservoir",
    "filter",
    "unknown",
}

ALLOWED_FAILURE_MODES = {
    "pressure_drop",
    "seal_leak",
    "line_leak",
    "blockage",
    "cavitation",
    "calibration_drift",
    "signal_loss",
    "power_loss",
    "overheating",
    "mechanical_jam",
    "corrosion",
    "software_fault",
    "configuration_error",
    "valve_misconfiguration",
    "normal_depressurization",
    "unknown",
}

ALLOWED_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}

ALLOWED_URGENCIES = {
    "routine",
    "within_24_hours",
    "immediate",
}


@dataclass(frozen=True)
class IncidentAnnotation:
    schema_version: str
    incident_id: str
    report: str
    component: str
    failure_mode: str
    severity: str
    urgency: str
    probable_cause: str
    evidence: list[str]
    recommended_action: str
    confidence: float
    abstain: bool
    requires_human_review: bool
    review_notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IncidentAnnotation:
        return cls(**data)

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.incident_id.strip():
            errors.append("incident_id must not be empty")

        if len(self.report.strip()) < 10:
            errors.append("report must contain at least 10 characters")

        if not isinstance(self.component, str):
            errors.append("component must be a string")
        elif self.component not in ALLOWED_COMPONENTS:
            errors.append(f"invalid component: {self.component}")

        if not isinstance(self.failure_mode, str):
            errors.append("failure_mode must be a string")
        elif self.failure_mode not in ALLOWED_FAILURE_MODES:
            errors.append(
                f"invalid failure_mode: {self.failure_mode}"
            )

        if not isinstance(self.severity, str):
            errors.append("severity must be a string")
        elif self.severity not in ALLOWED_SEVERITIES:
            errors.append(f"invalid severity: {self.severity}")

        if not isinstance(self.urgency, str):
            errors.append("urgency must be a string")
        elif self.urgency not in ALLOWED_URGENCIES:
            errors.append(f"invalid urgency: {self.urgency}")

        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be between 0.0 and 1.0")

        if not isinstance(self.evidence, list):
            errors.append("evidence must be a list")
        elif not self.evidence:
            errors.append("evidence must contain at least one item")
        elif any(
            not isinstance(item, str) or not item.strip()
            for item in self.evidence
        ):
            errors.append(
                "evidence items must be non-empty strings"
            )

        if any(not item.strip() for item in self.evidence):
            errors.append("evidence items must not be blank")

        if self.abstain and not self.requires_human_review:
            errors.append("abstained records must require human review")

        if self.abstain and not self.review_notes.strip():
            errors.append("abstained records must include review_notes")

        if self.probable_cause == "unknown" and not self.requires_human_review:
            errors.append("unknown probable cause must require human review")

        if self.severity in {"high", "critical"} and not self.requires_human_review:
            errors.append(
                "high and critical records must require human review"
            )

        if self.severity == "critical" and self.urgency != "immediate":
            errors.append("critical incidents must have immediate urgency")

        if self.schema_version != CURRENT_SCHEMA_VERSION:
            errors.append(
                "schema_version must be "
                f"{CURRENT_SCHEMA_VERSION}, got {self.schema_version}"
            )

        return errors