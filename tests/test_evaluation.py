from incident_intelligence.evaluation import exact_field_accuracy
from incident_intelligence.models import IncidentAnnotation

def r(severity):
    return IncidentAnnotation("X","Pressure dropped unexpectedly.","pump","pressure_drop",severity,"within_24_hours","unknown",["pressure dropped"],"inspect",0.8,False,severity=="high")

def test_accuracy(): assert exact_field_accuracy([r("medium"),r("high")],[r("medium"),r("medium")],"severity")==0.5
