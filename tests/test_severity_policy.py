from incident_intelligence.severity_policy import assign_severity_and_urgency


def decide(report: str, component: str, failure_mode: str):
    return assign_severity_and_urgency(
        report=report,
        component=component,
        failure_mode=failure_mode,
    )


def test_signal_loss_is_medium() -> None:
    result = decide(
        "The electronic pressure reading fell to zero while the mechanical gauge remained stable.",
        "pressure_sensor",
        "signal_loss",
    )
    assert (result.severity, result.urgency) == ("medium", "within_24_hours")


def test_calibration_drift_is_low() -> None:
    result = decide(
        "The transmitter has a repeatable offset against a calibrated reference across its range.",
        "pressure_sensor",
        "calibration_drift",
    )
    assert (result.severity, result.urgency) == ("low", "routine")


def test_reservoir_pressure_drop_is_medium() -> None:
    result = decide(
        "Pressure fell as the reservoir approached empty and recovered after refill.",
        "reservoir",
        "pressure_drop",
    )
    assert (result.severity, result.urgency) == ("medium", "within_24_hours")


def test_commanded_valve_mismatch_with_pressure_loss_is_high() -> None:
    result = decide(
        "Downstream pressure is low. The commanded valve position is 80 percent, but physical position feedback remains at 12 percent.",
        "valve",
        "mechanical_jam",
    )
    assert (result.severity, result.urgency) == ("high", "immediate")


def test_valve_jam_without_operational_impact_is_not_high() -> None:
    result = decide(
        "During inspection the valve stem was found stuck, with no process effects described.",
        "valve",
        "mechanical_jam",
    )
    assert (result.severity, result.urgency) == ("low", "routine")


def test_explicit_emergency_shutdown_is_critical() -> None:
    result = decide(
        "Operators initiated an emergency shutdown after the pump began shaking violently.",
        "pump",
        "mechanical_jam",
    )
    assert (result.severity, result.urgency) == ("critical", "immediate")


def test_explicit_imminent_danger_is_critical() -> None:
    result = decide(
        "The damaged support presents imminent danger to personnel in the work area.",
        "pipeline",
        "corrosion",
    )
    assert (result.severity, result.urgency) == ("critical", "immediate")


def test_generic_fallback_is_low() -> None:
    result = decide(
        "A technician observed an unusual controller message during a weekly check.",
        "controller",
        "software_fault",
    )
    assert (result.severity, result.urgency, result.rule_id) == (
        "low", "routine", "low.fallback"
    )


def test_critical_precedes_domain_specific_high() -> None:
    result = decide(
        "An emergency shutdown began because downstream pressure is low. The commanded valve position is 80 percent, but physical position feedback remains at 12 percent.",
        "valve",
        "mechanical_jam",
    )
    assert result.severity == "critical"
    assert result.rule_id == "critical.emergency_action"
