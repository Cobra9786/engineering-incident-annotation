from __future__ import annotations

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
- Treat the current incident report as the only source of case evidence.
- Retrieved diagnostic context is reference guidance, not evidence about this case.
- Do not copy facts, measurements, observations, or case details from examples or knowledge documents.
- Evidence must come only from the current incident report and closely paraphrase it.
- Never invent unsupported evidence, measurements, components, causes, or observations.
- Set probable_cause to "unknown" unless the current incident report supports it.
- Set abstain to true when a reliable conclusion cannot be made.
- Set requires_human_review to true when:
  - abstain is true
  - severity is high or critical
  - probable_cause is unknown
- Critical severity requires immediate urgency.
- Return every required field.
- Do not return schema_version, incident_id, or report.
- Return JSON only.
- Do not use Markdown fences.
""".strip()


def build_incident_prompt(
    *,
    incident_id: str,
    report: str,
    knowledge_context: str | None = None,
) -> str:
    context_section = ""
    if knowledge_context:
        context_section = (
            "Retrieved diagnostic guidance:\n"
            f"{knowledge_context.strip()}\n\n"
            "Use this only as reference guidance for interpreting the diagnosis. "
            "It is not evidence about this case. Do not copy facts from it into "
            "evidence or probable_cause.\n\n"
        )

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
        "Return all fields listed in the type requirements above.\n\n"
        f"{context_section}"
        "Incident report:\n"
        f"{report}\n\n"
        "Return the completed JSON object."
    )
