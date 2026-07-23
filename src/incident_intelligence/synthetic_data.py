from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from .models import CURRENT_SCHEMA_VERSION, IncidentAnnotation
from .severity_policy import assign_severity_and_urgency


DEFAULT_GENERATION_SEED = 20260722
VARIATIONS_PER_FAMILY = 4


@dataclass(frozen=True)
class Scenario:
    component: str
    failure_mode: str
    probable_cause: str
    symptom: str
    action: str
    provisional_severity: str
    abstain: bool = False


COMPONENT_LABELS = {
    "pump": "pump",
    "valve": "control valve",
    "pressure_sensor": "pressure transmitter",
    "temperature_sensor": "temperature probe",
    "motor": "drive motor",
    "actuator": "control actuator",
    "battery": "backup battery",
    "controller": "process controller",
    "hydraulic_cylinder": "hydraulic cylinder",
    "power_supply": "DC power supply",
    "communications_link": "fieldbus link",
    "pipeline": "process line",
    "reservoir": "fluid reservoir",
    "filter": "inlet filter",
    "unknown": "monitored system",
}


FAILURE_DETAILS = {
    "pressure_drop": (
        "pressure declined below its operating band",
        "inspect the supply path and verify pressure",
    ),
    "seal_leak": (
        "fluid collected around the shaft seal",
        "isolate the unit and replace the damaged seal",
    ),
    "line_leak": (
        "fluid was observed escaping from a line connection",
        "isolate the line and repair the connection",
    ),
    "blockage": (
        "differential pressure rose across the restricted path",
        "isolate and clear the restriction",
    ),
    "cavitation": (
        "pressure oscillated while a rattling sound came from the inlet",
        "stop the unit and restore adequate inlet supply",
    ),
    "calibration_drift": (
        "the reading held a repeatable offset from a calibrated reference",
        "recalibrate the instrument and verify its range",
    ),
    "signal_loss": (
        "the electronic reading disappeared while an independent indication remained steady",
        "inspect signal wiring and verify instrument output",
    ),
    "power_loss": (
        "the unit became unpowered and input voltage measured zero",
        "isolate the circuit and restore power after inspection",
    ),
    "overheating": (
        "temperature exceeded the normal limit and continued rising",
        "remove load and inspect cooling and lubrication",
    ),
    "mechanical_jam": (
        "commanded movement stopped before the requested position",
        "isolate and inspect the mechanical drive",
    ),
    "configuration_error": (
        "the device operated according to settings that differed from the approved control configuration",
        "restore the approved settings and verify commanded operation",
    ),
    "corrosion": (
        "inspection found deep corrosion and measurable wall loss",
        "isolate and assess the corroded section",
    ),
    "software_fault": (
        "the control software produced behavior inconsistent with verified inputs and approved settings",
        "isolate the software change, restore the verified release, and retest",
    ),
    "valve_misconfiguration": (
        "the valve position differed from the approved physical operating lineup",
        "restore the approved valve lineup and verify flow",
    ),
    "normal_depressurization": (
        "pressure decreased after the approved venting step began",
        "record the expected event and continue monitoring",
    ),
    "unknown": (
        "two independent observations conflicted and no corroborating data was available",
        "collect independent measurements before diagnosing",
    ),
}


CAUSES = {
    "pressure_drop": "insufficient fluid supply",
    "seal_leak": "degraded shaft seal",
    "line_leak": "failed line connection",
    "blockage": "accumulated debris",
    "cavitation": "restricted inlet supply",
    "calibration_drift": "instrument calibration drift",
    "signal_loss": "loose signal connector",
    "power_loss": "open upstream electrical circuit",
    "overheating": "restricted cooling airflow",
    "mechanical_jam": "seized mechanical linkage",
    "corrosion": "long-term environmental exposure",
    "software_fault": "defective software or firmware behavior",
    "configuration_error": "incorrect device or control settings",
    "valve_misconfiguration": "incorrect physical valve lineup",
    "normal_depressurization": "approved shutdown procedure",
    "unknown": "unknown",
}


# Forty families of four records make exact 120/20/20 grouped splits possible.
SCENARIO_PAIRS = (
    ("pump", "seal_leak"),
    ("pump", "cavitation"),
    ("pump", "mechanical_jam"),
    ("pump", "overheating"),
    ("valve", "mechanical_jam"),
    ("valve", "valve_misconfiguration"),
    ("valve", "line_leak"),
    ("pressure_sensor", "signal_loss"),
    ("pressure_sensor", "calibration_drift"),
    ("temperature_sensor", "signal_loss"),
    ("temperature_sensor", "calibration_drift"),
    ("motor", "overheating"),
    ("motor", "mechanical_jam"),
    ("motor", "power_loss"),
    ("actuator", "configuration_error"),
    ("battery", "power_loss"),
    ("battery", "overheating"),
    ("controller", "software_fault"),
    ("controller", "signal_loss"),
    ("controller", "configuration_error"),
    ("hydraulic_cylinder", "seal_leak"),
    ("hydraulic_cylinder", "mechanical_jam"),
    ("hydraulic_cylinder", "pressure_drop"),
    ("power_supply", "power_loss"),
    ("power_supply", "overheating"),
    ("communications_link", "signal_loss"),
    ("communications_link", "software_fault"),
    ("pipeline", "line_leak"),
    ("pipeline", "corrosion"),
    ("pipeline", "normal_depressurization"),
    ("reservoir", "pressure_drop"),
    ("reservoir", "line_leak"),
    ("filter", "blockage"),
    ("filter", "pressure_drop"),
    ("pump", "pressure_drop"),
    ("valve", "blockage"),
    ("unknown", "unknown"),
    ("unknown", "pressure_drop"),
    ("pressure_sensor", "unknown"),
    ("pipeline", "unknown"),
)


# Explicit pairs are stable when SCENARIO_PAIRS is reordered.
UNKNOWN_CAUSE_PAIRS = {
    ("valve", "line_leak"),
    ("actuator", "configuration_error"),
    ("hydraulic_cylinder", "pressure_drop"),
    ("reservoir", "pressure_drop"),
}


if len(SCENARIO_PAIRS) != 40:
    raise RuntimeError(
        "SCENARIO_PAIRS must contain exactly 40 families "
        "for the fixed 120/20/20 split"
    )


def _scenario(index: int, component: str, failure_mode: str) -> Scenario:
    severity_cycle = ("low", "medium", "high", "critical")
    provisional_severity = severity_cycle[index % len(severity_cycle)]

    difficult_negative = failure_mode in {
        "calibration_drift",
        "signal_loss",
        "software_fault",
        "configuration_error",
        "normal_depressurization",
        "valve_misconfiguration",
    }
    if difficult_negative and index % 4 in {2, 3}:
        provisional_severity = "low" if index % 2 else "medium"

    abstain = component == "unknown" or failure_mode == "unknown"
    unknown_cause = (component, failure_mode) in UNKNOWN_CAUSE_PAIRS
    probable_cause = (
        "unknown" if abstain or unknown_cause else CAUSES[failure_mode]
    )
    symptom, action = FAILURE_DETAILS[failure_mode]

    return Scenario(
        component=component,
        failure_mode=failure_mode,
        probable_cause=probable_cause,
        symptom=symptom,
        action=action,
        provisional_severity=provisional_severity,
        abstain=abstain,
    )


def _impact_sentence(severity: str) -> str:
    return {
        "low": "Operation is stable, and routine maintenance is appropriate.",
        "medium": (
            "Operation is degraded, but the equipment remains operational "
            "and should be corrected soon."
        ),
        "high": (
            "Production is interrupted, and immediate corrective action is required."
        ),
        "critical": (
            "An emergency shutdown is active because the condition presents "
            "imminent danger to personnel."
        ),
    }[severity]


def _build_report(
    scenario: Scenario,
    *,
    variation_id: int,
    reading: int,
    severity: str,
) -> tuple[str, list[str]]:
    component = COMPONENT_LABELS[scenario.component]
    observation = (
        f"The {component} {scenario.symptom} under event reference {reading}."
    )
    impact = _impact_sentence(severity)

    if scenario.abstain:
        observation = (
            f"Under event reference {reading}, one indication implicated the "
            f"{component}, but a second independent indication contradicted it."
        )
        impact = (
            "The available evidence conflicts, and the affected component or failure "
            "mode cannot be determined reliably."
        )

    styles = (
        f"Operator log: {observation} {impact}",
        (
            f"Work order narrative — {observation} "
            f"Follow-up inspection recorded the impact. {impact}"
        ),
        f"Telemetry review found the following condition. {observation} {impact}",
        (
            "Shift handoff report: technicians compared local indications with the "
            f"control-room display. {observation} "
            f"No unrelated alarms were active. {impact}"
        ),
    )
    return styles[variation_id - 1], [observation, impact]


def generate_candidates(
    *,
    seed: int = DEFAULT_GENERATION_SEED,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    candidates: list[dict[str, Any]] = []
    incident_number = 1

    indexed_pairs = list(enumerate(SCENARIO_PAIRS))
    rng.shuffle(indexed_pairs)

    for original_index, (component, failure_mode) in indexed_pairs:
        scenario = _scenario(original_index, component, failure_mode)
        family = f"family-{original_index + 1:03d}-{component}-{failure_mode}"
        readings = rng.sample(range(1000, 9999), VARIATIONS_PER_FAMILY)

        for variation_id, reading in enumerate(readings, start=1):
            provisional_report, _ = _build_report(
                scenario,
                variation_id=variation_id,
                reading=reading,
                severity=scenario.provisional_severity,
            )
            policy_decision = assign_severity_and_urgency(
                report=provisional_report,
                component=scenario.component,
                failure_mode=scenario.failure_mode,
            )

            # Rebuild with the policy-authoritative severity so report wording,
            # evidence, and annotation labels cannot contradict each other.
            report, evidence = _build_report(
                scenario,
                variation_id=variation_id,
                reading=reading,
                severity=policy_decision.severity,
            )

            requires_review = (
                scenario.abstain
                or scenario.probable_cause == "unknown"
                or policy_decision.severity in {"high", "critical"}
            )
            annotation = IncidentAnnotation(
                schema_version=CURRENT_SCHEMA_VERSION,
                incident_id=f"SYN-{incident_number:04d}",
                report=report,
                component=scenario.component,
                failure_mode=scenario.failure_mode,
                severity=policy_decision.severity,
                urgency=policy_decision.urgency,
                probable_cause=scenario.probable_cause,
                evidence=evidence,
                recommended_action=scenario.action,
                confidence=(
                    0.45
                    if scenario.abstain
                    else round(rng.uniform(0.72, 0.98), 2)
                ),
                abstain=scenario.abstain,
                requires_human_review=requires_review,
                review_notes=(
                    "Conflicting evidence requires expert adjudication."
                    if scenario.abstain
                    else (
                        "Probable cause requires expert confirmation."
                        if scenario.probable_cause == "unknown"
                        else (
                            "Final severity requires human review."
                            if policy_decision.severity in {"high", "critical"}
                            else ""
                        )
                    )
                ),
            )
            candidates.append(
                {
                    "annotation": asdict(annotation),
                    "generation_metadata": {
                        "generator": "deterministic_template_v1",
                        "seed": seed,
                        "scenario_family": family,
                        "variation_id": variation_id,
                    },
                    "review": {
                        "status": "pending",
                        "reviewer": "",
                        "notes": "",
                    },
                }
            )
            incident_number += 1

    return candidates


def promote_approved_candidates(
    candidates: list[dict[str, Any]],
) -> tuple[list[IncidentAnnotation], dict[str, dict[str, Any]]]:
    annotations: list[IncidentAnnotation] = []
    metadata: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if candidate.get("review", {}).get("status") != "approved":
            continue
        annotation = IncidentAnnotation.from_dict(candidate["annotation"])
        errors = annotation.validate()
        if errors:
            raise ValueError(
                f"{annotation.incident_id}: approved candidate is invalid: "
                + "; ".join(errors)
            )
        annotations.append(annotation)
        metadata[annotation.incident_id] = dict(candidate["generation_metadata"])
    return annotations, metadata


def grouped_split(
    annotations: list[IncidentAnnotation],
    metadata: dict[str, dict[str, Any]],
    *,
    train_size: int = 120,
    validation_size: int = 20,
    held_out_size: int = 20,
    seed: int = DEFAULT_GENERATION_SEED,
) -> dict[str, list[IncidentAnnotation]]:
    target_total = train_size + validation_size + held_out_size
    if len(annotations) != target_total:
        raise ValueError(
            f"exact split requires {target_total} approved records, got {len(annotations)}"
        )

    families: dict[str, list[IncidentAnnotation]] = defaultdict(list)
    for annotation in annotations:
        try:
            family = str(metadata[annotation.incident_id]["scenario_family"])
        except KeyError as error:
            raise ValueError(
                f"missing scenario_family metadata for {annotation.incident_id}"
            ) from error
        families[family].append(annotation)

    ordered = list(families.items())
    random.Random(seed).shuffle(ordered)
    validation_families = _select_families(ordered, validation_size)
    if validation_families is None:
        sizes = sorted(len(rows) for rows in families.values())
        raise ValueError(
            "exact grouped split is impossible without splitting a scenario family; "
            f"family sizes are {sizes}"
        )
    remaining = [item for item in ordered if item[0] not in validation_families]
    held_out_families = _select_families(remaining, held_out_size)
    if held_out_families is None:
        sizes = sorted(len(rows) for rows in families.values())
        raise ValueError(
            "exact grouped split is impossible without splitting a scenario family; "
            f"family sizes are {sizes}"
        )

    splits = {"train": [], "validation": [], "held_out_test": []}
    for family, rows in ordered:
        if family in validation_families:
            splits["validation"].extend(rows)
        elif family in held_out_families:
            splits["held_out_test"].extend(rows)
        else:
            splits["train"].extend(rows)

    actual = {name: len(rows) for name, rows in splits.items()}
    expected = {
        "train": train_size,
        "validation": validation_size,
        "held_out_test": held_out_size,
    }
    if actual != expected:
        raise ValueError(f"exact grouped split failed: expected {expected}, got {actual}")
    return splits


def assert_no_protected_leakage(
    generated: list[IncidentAnnotation],
    protected_held_out: list[IncidentAnnotation],
) -> None:
    protected_ids = {record.incident_id for record in protected_held_out}
    protected_reports = {
        " ".join(record.report.casefold().split())
        for record in protected_held_out
    }
    for record in generated:
        if record.incident_id in protected_ids:
            raise ValueError(
                f"generated record reuses protected held-out ID: {record.incident_id}"
            )
        normalized_report = " ".join(record.report.casefold().split())
        if normalized_report in protected_reports:
            raise ValueError(
                f"generated record duplicates protected held-out report: {record.incident_id}"
            )


def _select_families(
    families: list[tuple[str, list[IncidentAnnotation]]],
    target: int,
) -> set[str] | None:
    reachable: dict[int, set[str]] = {0: set()}
    for family, rows in families:
        for total, selected in list(reachable.items())[::-1]:
            new_total = total + len(rows)
            if new_total <= target and new_total not in reachable:
                reachable[new_total] = {*selected, family}
    return reachable.get(target)