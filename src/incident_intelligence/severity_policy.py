from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SeverityDecision:
    severity: str
    urgency: str
    rule_id: str
    rationale: str


@dataclass(frozen=True)
class _PolicyContext:
    report: str
    component: str
    failure_mode: str


@dataclass(frozen=True)
class _Rule:
    rule_id: str
    severity: str
    urgency: str
    rationale: str
    matches: Callable[[_PolicyContext], bool]


def _normalize(text: str) -> str:
    """Normalize prose while retaining word boundaries for exact phrases."""
    return " ".join(re.findall(r"[a-z0-9]+", text.casefold()))


def _contains_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    padded_text = f" {text} "
    return any(
        f" {_normalize(phrase)} " in padded_text
        for phrase in phrases
    )


def _contains_all_groups(
    text: str,
    *phrase_groups: tuple[str, ...],
) -> bool:
    return all(_contains_phrase(text, group) for group in phrase_groups)


PEOPLE_DANGER_PHRASES = (
    "imminent danger to people",
    "imminent danger to personnel",
    "immediate danger to people",
    "immediate danger to personnel",
    "life threatening danger",
)

HAZARDOUS_RELEASE_PHRASES = (
    "active hazardous material release",
    "hazardous material is being released",
    "active toxic release",
    "active chemical release",
)

CATASTROPHIC_FAILURE_PHRASES = (
    "catastrophic equipment failure",
    "equipment has failed catastrophically",
    "catastrophic failure in progress",
)

EMERGENCY_PHRASES = (
    "emergency shutdown",
    "emergency response",
    "emergency responders",
)

RAPID_FAILURE_PHRASES = (
    "rapidly progressing failure",
    "failure is progressing rapidly",
    "deteriorating rapidly",
)

IMMEDIATE_INTERVENTION_PHRASES = (
    "requires immediate intervention",
    "immediate intervention is required",
    "needs immediate intervention",
)

INTERRUPTION_PHRASES = (
    "production interruption",
    "production is interrupted",
    "production has stopped",
    "service interruption",
    "service is interrupted",
    "normal operation is interrupted",
    "normal operations are interrupted",
)

EQUIPMENT_DAMAGE_PHRASES = (
    "active equipment damage",
    "equipment is being damaged",
    "likely equipment damage",
    "equipment damage is likely",
    "will damage equipment",
)

WORSENING_PHRASES = (
    "actively worsening",
    "failure is worsening",
    "condition is worsening",
    "continues to worsen",
)

OPERATIONAL_HAZARD_PHRASES = (
    "significant operational hazard",
    "major operational hazard",
)

IMMEDIATE_ACTION_PHRASES = (
    "immediate corrective action is required",
    "requires immediate corrective action",
    "corrective action is required immediately",
)

COMMAND_PHRASES = (
    "commanded valve position",
    "commanded position",
    "controller commands",
    "commanded to open",
    "commanded to close",
)

POSITION_MISMATCH_PHRASES = (
    "physical position feedback remains",
    "position feedback remains",
    "actual position remains",
    "failed to reach commanded position",
    "does not match the commanded position",
    "did not follow its command",
)

CONTROL_LOSS_PHRASES = (
    "pressure loss",
    "pressure is low",
    "pressure remains low",
    "downstream pressure is low",
    "pressure downstream of the control valve is low",
    "flow loss",
    "flow is low",
    "loss of flow",
    "process control loss",
    "loss of process control",
    "normal operation is interrupted",
    "normal operations are interrupted",
)

DEGRADED_OPERATION_PHRASES = (
    "operation is degraded",
    "operations are degraded",
    "degraded operation",
    "reduced operating capacity",
)

UNRELIABLE_INSTRUMENT_PHRASES = (
    "instrumentation is unavailable",
    "instrumentation is unreliable",
    "reading is unavailable",
    "signal is unavailable",
    "unreliable reading",
)

NEEDED_SOON_PHRASES = (
    "corrective action is needed soon",
    "requires correction soon",
    "should be corrected soon",
)

OPERATIONAL_BUT_UNRESOLVED_PHRASES = (
    "remains operational but",
    "still operational but",
    "should not remain unresolved",
)

MINOR_PHRASES = (
    "minor impact",
    "impact is minor",
    "minor issue",
)

STABLE_PHRASES = (
    "operation is stable",
    "operations are stable",
    "system is stable",
    "stable operation",
)

ROUTINE_PHRASES = (
    "routine calibration",
    "routine maintenance",
    "next scheduled maintenance",
)


def _is_rapid_immediate_failure(context: _PolicyContext) -> bool:
    return _contains_all_groups(
        context.report,
        RAPID_FAILURE_PHRASES,
        IMMEDIATE_INTERVENTION_PHRASES,
    )


def _is_commanded_valve_mismatch(context: _PolicyContext) -> bool:
    return (
        context.component == "valve"
        and context.failure_mode == "mechanical_jam"
        and _contains_all_groups(
            context.report,
            COMMAND_PHRASES,
            POSITION_MISMATCH_PHRASES,
            CONTROL_LOSS_PHRASES,
        )
    )


def _failure_mode_is(*failure_modes: str) -> Callable[[_PolicyContext], bool]:
    return lambda context: context.failure_mode in failure_modes


def _report_contains(*phrases: str) -> Callable[[_PolicyContext], bool]:
    return lambda context: _contains_phrase(context.report, phrases)


RULES = (
    _Rule(
        "critical.imminent_people_danger",
        "critical",
        "immediate",
        "The report explicitly states imminent danger to people.",
        _report_contains(*PEOPLE_DANGER_PHRASES),
    ),
    _Rule(
        "critical.active_hazardous_release",
        "critical",
        "immediate",
        "The report explicitly states an active hazardous material release.",
        _report_contains(*HAZARDOUS_RELEASE_PHRASES),
    ),
    _Rule(
        "critical.catastrophic_failure",
        "critical",
        "immediate",
        "The report explicitly states catastrophic equipment failure.",
        _report_contains(*CATASTROPHIC_FAILURE_PHRASES),
    ),
    _Rule(
        "critical.emergency_action",
        "critical",
        "immediate",
        "The report explicitly states an emergency shutdown or response.",
        _report_contains(*EMERGENCY_PHRASES),
    ),
    _Rule(
        "critical.rapid_failure_immediate_intervention",
        "critical",
        "immediate",
        "A rapidly progressing failure explicitly requires immediate intervention.",
        _is_rapid_immediate_failure,
    ),
    _Rule(
        "high.explicit_operational_impact",
        "high",
        "immediate",
        "The report explicitly states interruption, damage, worsening, hazard, or immediate corrective action.",
        _report_contains(
            *INTERRUPTION_PHRASES,
            *EQUIPMENT_DAMAGE_PHRASES,
            *WORSENING_PHRASES,
            *OPERATIONAL_HAZARD_PHRASES,
            *IMMEDIATE_ACTION_PHRASES,
        ),
    ),
    _Rule(
        "high.commanded_valve_mismatch_with_control_loss",
        "high",
        "immediate",
        "A jammed valve has an explicit command/position mismatch and resulting process loss.",
        _is_commanded_valve_mismatch,
    ),
    _Rule(
        "medium.degraded_or_unreliable_operation",
        "medium",
        "within_24_hours",
        "The report explicitly describes degraded operation, unreliable instrumentation, or correction needed soon.",
        _report_contains(
            *DEGRADED_OPERATION_PHRASES,
            *UNRELIABLE_INSTRUMENT_PHRASES,
            *NEEDED_SOON_PHRASES,
            *OPERATIONAL_BUT_UNRESOLVED_PHRASES,
        ),
    ),
    _Rule(
        "medium.diagnostic_failure_mode",
        "medium",
        "within_24_hours",
        "The diagnosed failure mode is signal loss or pressure drop and no higher-priority rule matched.",
        _failure_mode_is("signal_loss", "pressure_drop"),
    ),
    _Rule(
        "low.calibration_drift",
        "low",
        "routine",
        "The diagnosed failure mode is calibration drift and no higher-priority rule matched.",
        _failure_mode_is("calibration_drift"),
    ),
    _Rule(
        "low.explicit_minor_stable_routine",
        "low",
        "routine",
        "The report explicitly describes minor impact, stable operation, or routine work.",
        _report_contains(*MINOR_PHRASES, *STABLE_PHRASES, *ROUTINE_PHRASES),
    ),
)


def assign_severity_and_urgency(
    *,
    report: str,
    component: str,
    failure_mode: str,
) -> SeverityDecision:
    """Apply the first matching severity rule in documented priority order."""
    context = _PolicyContext(
        report=_normalize(report),
        component=component.casefold().strip(),
        failure_mode=failure_mode.casefold().strip(),
    )

    for rule in RULES:
        if rule.matches(context):
            return SeverityDecision(
                severity=rule.severity,
                urgency=rule.urgency,
                rule_id=rule.rule_id,
                rationale=rule.rationale,
            )

    return SeverityDecision(
        severity="low",
        urgency="routine",
        rule_id="low.fallback",
        rationale=(
            "No explicit critical, high, medium, or low policy rule matched; "
            "the deterministic fallback applies."
        ),
    )
