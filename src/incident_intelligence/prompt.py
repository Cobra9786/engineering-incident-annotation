from __future__ import annotations

import json

from .models import (
    ALLOWED_COMPONENTS,
    ALLOWED_FAILURE_MODES,
    ALLOWED_SEVERITIES,
    ALLOWED_URGENCIES,
)


SYSTEM_PROMPT = """
You are an engineering incident triage assistant.

Analyze one engineering incident report and return exactly one JSON object.

Type requirements:

- component must be one string, never an array
- failure_mode must be one string, never an array
- severity must be one string
- urgency must be one string
- probable_cause must be one string
- evidence must be an array of strings
- recommended_action must be one string
- confidence must be a number from 0.0 through 1.0
- abstain must be a boolean
- requires_human_review must be a boolean
- review_notes must be one string

Classification rules:

- Select one primary component.
- Select one primary failure mode.
- Do not return multiple alternatives.
- Use only evidence contained in the report.
- Do not invent measurements, components, causes, or observations.
- Use "unknown" when the evidence does not support a conclusion.
- Set abstain to true when a reliable conclusion cannot be made.
- Set requires_human_review to true when:
  - abstain is true
  - severity is high or critical
  - probable_cause is unknown
- Critical severity requires immediate urgency.
- Evidence items must closely paraphrase the report.
- Return every required field.
- Do not return schema_version, incident_id, or report.
- Return JSON only.
- Do not use Markdown fences.
""".strip()


def build_incident_prompt(
    *,
    incident_id: str,
    report: str,
) -> str:
    output_template = {
        "component": "pump",
        "failure_mode": "seal_leak",
        "severity": "high",
        "urgency": "immediate",
        "probable_cause": "output shaft seal failure",
        "evidence": [
            "pressure dropped after startup",
            "oil was visible around the output shaft seal",
        ],
        "recommended_action": (
            "shut down and inspect the output shaft seal"
        ),
        "confidence": 0.95,
        "abstain": False,
        "requires_human_review": True,
        "review_notes": (
            "Visible oil at the shaft seal supports a physical leak."
        ),
    }

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Incident ID: {incident_id}\n\n"
        "Allowed component values:\n"
        f"{', '.join(sorted(ALLOWED_COMPONENTS))}\n\n"
        "Allowed failure-mode values:\n"
        f"{', '.join(sorted(ALLOWED_FAILURE_MODES))}\n\n"
        "Allowed severity values:\n"
        f"{', '.join(sorted(ALLOWED_SEVERITIES))}\n\n"
        "Allowed urgency values:\n"
        f"{', '.join(sorted(ALLOWED_URGENCIES))}\n\n"
        "Required JSON shape example:\n"
        f"{json.dumps(output_template, indent=2)}\n\n"
        "The example values above are illustrative only. "
        "Replace every value using the actual incident report.\n\n"
        "Incident report:\n"
        f"{report}\n\n"
        "Return the completed JSON object."
    )