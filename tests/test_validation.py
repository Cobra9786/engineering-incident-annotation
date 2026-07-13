from pathlib import Path
from incident_intelligence.dataset import load_annotations,validate_annotations

def test_sample_dataset_is_valid():
    root=Path(__file__).resolve().parents[1]
    assert validate_annotations(load_annotations(root/"data"/"annotated"/"incidents.json"))==[]
