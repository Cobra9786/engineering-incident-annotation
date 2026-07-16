from __future__ import annotations

import json
from pathlib import Path

from .models import IncidentAnnotation


def load_annotations(path: Path) -> list[IncidentAnnotation]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError("dataset root must be a JSON array")

    return [IncidentAnnotation.from_dict(item) for item in payload]


def validate_annotations(records: list[IncidentAnnotation]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_reports: set[str] = set()

    for record in records:
        if record.incident_id in seen_ids:
            errors.append(f"{record.incident_id}: duplicate incident_id")
        seen_ids.add(record.incident_id)

        normalized_report = " ".join(record.report.lower().split())

        if normalized_report in seen_reports:
            errors.append(f"{record.incident_id}: duplicate report text")
        seen_reports.add(normalized_report)

        for error in record.validate():
            errors.append(f"{record.incident_id}: {error}")

    return errors