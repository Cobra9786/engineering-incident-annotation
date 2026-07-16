import json
from pathlib import Path
from .models import IncidentAnnotation

def load_annotations(path:Path)->list[IncidentAnnotation]:
    payload=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload,list): raise ValueError("dataset root must be a JSON array")
    return [IncidentAnnotation.from_dict(item) for item in payload]

def validate_annotations(records:list[IncidentAnnotation])->list[str]:
    errors=[]; seen=set()
    for record in records:
        if record.incident_id in seen: errors.append(f"{record.incident_id}: duplicate incident_id")
        seen.add(record.incident_id)
        errors.extend(f"{record.incident_id}: {e}" for e in record.validate())
    return errors
