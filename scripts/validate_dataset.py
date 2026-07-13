#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from incident_intelligence.dataset import load_annotations,validate_annotations

def main()->int:
    records=load_annotations(ROOT/"data"/"annotated"/"incidents.json")
    errors=validate_annotations(records)
    if errors:
        print("Dataset validation failed:")
        for e in errors: print(f"- {e}")
        return 1
    print(f"Dataset valid: {len(records)} incident records")
    return 0
if __name__=="__main__": raise SystemExit(main())
