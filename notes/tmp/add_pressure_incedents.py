import json
from pathlib import Path

ROOT = Path.cwd()

GROUND_TRUTH = (
    ROOT / "data" / "ground_truth" / "incidents.json"
)
RAW = ROOT / "data" / "raw" / "incidents.jsonl"

new_records = [
    {
        "incident_id": "INC-0006",
        "report": (
            "Pressure dropped 30 psi after a flexible hydraulic line "
            "ruptured near the actuator. Fluid was visible on the floor."
        ),
        "component": "pipeline",
        "failure_mode": "line_leak",
        "severity": "high",
        "urgency": "immediate",
        "probable_cause": "ruptured hydraulic line",
        "evidence": [
            "pressure dropped 30 psi",
            "flexible hydraulic line ruptured near the actuator",
            "fluid was visible on the floor"
        ],
        "recommended_action": (
            "isolate the hydraulic circuit and replace the damaged line"
        ),
        "confidence": 0.99,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "Visible line damage directly supports a physical leak."
        )
    },
    {
        "incident_id": "INC-0007",
        "report": (
            "Discharge pressure decreased after maintenance. The bypass "
            "valve position indicator shows the valve is fully open."
        ),
        "component": "valve",
        "failure_mode": "valve_misconfiguration",
        "severity": "medium",
        "urgency": "within_24_hours",
        "probable_cause": "bypass valve left open after maintenance",
        "evidence": [
            "discharge pressure decreased after maintenance",
            "bypass valve position indicator shows fully open"
        ],
        "recommended_action": (
            "verify the maintenance procedure and restore the approved "
            "bypass valve position"
        ),
        "confidence": 0.96,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "Valve position provides direct evidence of the configuration issue."
        )
    },
    {
        "incident_id": "INC-0008",
        "report": (
            "Pump inlet pressure is abnormally low while discharge pressure "
            "and motor current fluctuate. The inlet strainer is heavily fouled."
        ),
        "component": "filter",
        "failure_mode": "blockage",
        "severity": "high",
        "urgency": "immediate",
        "probable_cause": "blocked inlet strainer",
        "evidence": [
            "pump inlet pressure is abnormally low",
            "discharge pressure and motor current fluctuate",
            "inlet strainer is heavily fouled"
        ],
        "recommended_action": (
            "stop the pump and clean or replace the inlet strainer"
        ),
        "confidence": 0.97,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "The fouled inlet strainer explains the restricted supply."
        )
    },
    {
        "incident_id": "INC-0009",
        "report": (
            "The digital pressure transmitter reads 18 psi below a recently "
            "calibrated mechanical gauge across the full operating range."
        ),
        "component": "pressure_sensor",
        "failure_mode": "calibration_drift",
        "severity": "low",
        "urgency": "routine",
        "probable_cause": "pressure transmitter calibration drift",
        "evidence": [
            "digital transmitter reads 18 psi below mechanical gauge",
            "difference persists across the full operating range"
        ],
        "recommended_action": (
            "recalibrate the pressure transmitter and verify its output"
        ),
        "confidence": 0.98,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "A repeatable offset against a calibrated reference supports drift."
        )
    },
    {
        "incident_id": "INC-0010",
        "report": (
            "System pressure fell gradually as the reservoir level approached "
            "empty. Pressure recovered after the reservoir was refilled."
        ),
        "component": "reservoir",
        "failure_mode": "pressure_drop",
        "severity": "medium",
        "urgency": "within_24_hours",
        "probable_cause": "insufficient fluid in reservoir",
        "evidence": [
            "pressure fell as reservoir approached empty",
            "pressure recovered after reservoir refill"
        ],
        "recommended_action": (
            "inspect for fluid loss and verify the reservoir level monitoring"
        ),
        "confidence": 0.96,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "Recovery after refill strongly supports low fluid level."
        )
    },
    {
        "incident_id": "INC-0011",
        "report": (
            "Pressure decreased during a scheduled shutdown after the isolation "
            "valve was opened to depressurize the line."
        ),
        "component": "pipeline",
        "failure_mode": "normal_depressurization",
        "severity": "low",
        "urgency": "routine",
        "probable_cause": "planned shutdown procedure",
        "evidence": [
            "pressure decreased during scheduled shutdown",
            "isolation valve was opened to depressurize the line"
        ],
        "recommended_action": (
            "record the event as expected operation and continue monitoring"
        ),
        "confidence": 0.99,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "The pressure reduction was intentional and procedural."
        )
    },
    {
        "incident_id": "INC-0012",
        "report": (
            "Both pressure transmitters reported zero for twelve seconds while "
            "flow, motor current, and the mechanical gauge remained normal. "
            "The controller logged a communications timeout."
        ),
        "component": "communications_link",
        "failure_mode": "signal_loss",
        "severity": "medium",
        "urgency": "within_24_hours",
        "probable_cause": "temporary communications interruption",
        "evidence": [
            "both transmitters reported zero for twelve seconds",
            "flow and motor current remained normal",
            "mechanical gauge remained normal",
            "controller logged a communications timeout"
        ],
        "recommended_action": (
            "inspect the communications link and review timeout diagnostics"
        ),
        "confidence": 0.98,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "Independent process measurements remained normal."
        )
    },
    {
        "incident_id": "INC-0013",
        "report": (
            "Discharge pressure is low and the motor is not drawing current. "
            "The motor controller reports loss of incoming power."
        ),
        "component": "power_supply",
        "failure_mode": "power_loss",
        "severity": "high",
        "urgency": "immediate",
        "probable_cause": "loss of motor power supply",
        "evidence": [
            "discharge pressure is low",
            "motor is not drawing current",
            "motor controller reports loss of incoming power"
        ],
        "recommended_action": (
            "isolate the equipment and restore power only after electrical inspection"
        ),
        "confidence": 0.99,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "The pressure symptom is secondary to confirmed electrical power loss."
        )
    },
    {
        "incident_id": "INC-0014",
        "report": (
            "The supervisory display shows low pressure, but the PLC tag and "
            "local transmitter both show 125 psi. A recent software deployment "
            "changed the display scaling."
        ),
        "component": "controller",
        "failure_mode": "software_fault",
        "severity": "medium",
        "urgency": "within_24_hours",
        "probable_cause": "incorrect supervisory display scaling",
        "evidence": [
            "supervisory display shows low pressure",
            "PLC tag and local transmitter show 125 psi",
            "software deployment changed display scaling"
        ],
        "recommended_action": (
            "restore the verified scaling configuration and test the display"
        ),
        "confidence": 0.98,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "The process pressure is normal; only the display representation is wrong."
        )
    },
    {
        "incident_id": "INC-0015",
        "report": (
            "Pressure declined rapidly in a chemical transfer line. A toxic-gas "
            "monitor alarmed near the flange, and operators reported visible vapor."
        ),
        "component": "pipeline",
        "failure_mode": "line_leak",
        "severity": "critical",
        "urgency": "immediate",
        "probable_cause": "hazardous material release at flange",
        "evidence": [
            "pressure declined rapidly",
            "toxic-gas monitor alarmed near the flange",
            "operators reported visible vapor"
        ],
        "recommended_action": (
            "initiate emergency isolation and follow the hazardous-release procedure"
        ),
        "confidence": 0.99,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "Multiple direct indicators support a critical hazardous release."
        )
    },
    {
        "incident_id": "INC-0016",
        "report": (
            "Pressure is low, but one gauge indicates 60 psi and another indicates "
            "118 psi. No flow, temperature, valve-position, or inspection data "
            "is available."
        ),
        "component": "unknown",
        "failure_mode": "unknown",
        "severity": "medium",
        "urgency": "within_24_hours",
        "probable_cause": "unknown",
        "evidence": [
            "one gauge indicates 60 psi",
            "another gauge indicates 118 psi",
            "supporting process data is unavailable"
        ],
        "recommended_action": (
            "obtain an independent pressure measurement and inspect both instruments"
        ),
        "confidence": 0.42,
        "abstain": True,
        "requires_human_review": True,
        "review_notes": (
            "The readings conflict and there is insufficient corroborating evidence."
        )
    },
    {
        "incident_id": "INC-0017",
        "report": (
            "Pump discharge pressure dropped and casing temperature increased "
            "to 96 degrees Celsius. Grinding noise is present at the bearing housing."
        ),
        "component": "pump",
        "failure_mode": "mechanical_jam",
        "severity": "critical",
        "urgency": "immediate",
        "probable_cause": "internal mechanical or bearing failure",
        "evidence": [
            "discharge pressure dropped",
            "casing temperature increased to 96 degrees Celsius",
            "grinding noise is present at bearing housing"
        ],
        "recommended_action": (
            "shut down immediately and inspect the pump and bearings"
        ),
        "confidence": 0.96,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "Combined pressure, temperature, and noise evidence indicates severe damage."
        )
    },
    {
        "incident_id": "INC-0018",
        "report": (
            "Pressure downstream of the control valve is low. The commanded valve "
            "position is 80 percent, but the physical position feedback remains at "
            "12 percent."
        ),
        "component": "valve",
        "failure_mode": "mechanical_jam",
        "severity": "high",
        "urgency": "immediate",
        "probable_cause": "control valve failed to reach commanded position",
        "evidence": [
            "downstream pressure is low",
            "commanded valve position is 80 percent",
            "physical position feedback remains at 12 percent"
        ],
        "recommended_action": (
            "isolate the valve and inspect the actuator and valve mechanism"
        ),
        "confidence": 0.98,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "Position feedback confirms the valve did not follow its command."
        )
    },
    {
        "incident_id": "INC-0019",
        "report": (
            "Pressure fell by 8 psi during a cold-weather startup. It returned "
            "to the normal range within three minutes as fluid temperature increased."
        ),
        "component": "unknown",
        "failure_mode": "pressure_drop",
        "severity": "low",
        "urgency": "routine",
        "probable_cause": "temporary cold-start operating condition",
        "evidence": [
            "pressure fell by 8 psi during cold-weather startup",
            "pressure returned to normal within three minutes",
            "fluid temperature increased during recovery"
        ],
        "recommended_action": (
            "monitor future cold starts and compare against the approved operating envelope"
        ),
        "confidence": 0.86,
        "abstain": False,
        "requires_human_review": False,
        "review_notes": (
            "The brief self-correcting event is consistent with a transient condition."
        )
    },
    {
        "incident_id": "INC-0020",
        "report": (
            "Pressure dropped after maintenance. The seal area is dry, the bypass "
            "valve reports closed, the reservoir is full, and motor current is normal. "
            "No reliable flow measurement is available."
        ),
        "component": "unknown",
        "failure_mode": "pressure_drop",
        "severity": "medium",
        "urgency": "within_24_hours",
        "probable_cause": "unknown",
        "evidence": [
            "pressure dropped after maintenance",
            "seal area is dry",
            "bypass valve reports closed",
            "reservoir is full",
            "motor current is normal",
            "no reliable flow measurement is available"
        ],
        "recommended_action": (
            "verify pressure calibration and obtain a reliable flow measurement "
            "before diagnosing the cause"
        ),
        "confidence": 0.61,
        "abstain": True,
        "requires_human_review": True,
        "review_notes": (
            "Several common causes are unsupported, and a key process measurement is missing."
        )
    }
]

records = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))

existing_ids = {
    record["incident_id"]
    for record in records
}

duplicates = [
    record["incident_id"]
    for record in new_records
    if record["incident_id"] in existing_ids
]

if duplicates:
    raise SystemExit(
        f"Refusing to add duplicate incident IDs: {duplicates}"
    )

records.extend(new_records)

GROUND_TRUTH.write_text(
    json.dumps(records, indent=2) + "\n",
    encoding="utf-8",
)

with RAW.open("a", encoding="utf-8") as handle:
    for record in new_records:
        raw_record = {
            "incident_id": record["incident_id"],
            "report": record["report"],
        }
        handle.write(json.dumps(raw_record) + "\n")

print(f"Added {len(new_records)} incidents")
print(f"Ground-truth total: {len(records)}")
PY