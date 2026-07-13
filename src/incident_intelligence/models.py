from dataclasses import dataclass
from typing import Any

ALLOWED_SEVERITIES={"low","medium","high","critical"}
ALLOWED_URGENCIES={"routine","within_24_hours","immediate"}

@dataclass(frozen=True)
class IncidentAnnotation:
    incident_id:str
    report:str
    component:str
    failure_mode:str
    severity:str
    urgency:str
    probable_cause:str
    evidence:list[str]
    recommended_action:str
    confidence:float
    abstain:bool
    requires_human_review:bool
    review_notes:str=""

    @classmethod
    def from_dict(cls,data:dict[str,Any])->"IncidentAnnotation":
        return cls(**data)

    def validate(self)->list[str]:
        errors=[]
        if not self.incident_id.strip(): errors.append("incident_id must not be empty")
        if len(self.report.strip())<10: errors.append("report must contain at least 10 characters")
        if self.severity not in ALLOWED_SEVERITIES: errors.append(f"invalid severity: {self.severity}")
        if self.urgency not in ALLOWED_URGENCIES: errors.append(f"invalid urgency: {self.urgency}")
        if not 0.0<=self.confidence<=1.0: errors.append("confidence must be between 0.0 and 1.0")
        if not self.evidence: errors.append("evidence must contain at least one item")
        if self.abstain and not self.requires_human_review: errors.append("abstained records must require human review")
        if self.severity in {"high","critical"} and not self.requires_human_review: errors.append("high and critical records must require human review")
        return errors
