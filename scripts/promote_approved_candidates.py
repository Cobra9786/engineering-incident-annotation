#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.dataset import validate_annotations
from incident_intelligence.synthetic_data import promote_approved_candidates


DEFAULT_INPUT = ROOT / "data" / "candidates" / "generated_incident_candidates.json"
DEFAULT_OUTPUT = ROOT / "data" / "reviewed" / "generated_incidents.json"
DEFAULT_METADATA_OUTPUT = ROOT / "data" / "reviewed" / "generated_incidents.metadata.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote explicitly approved candidates.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata-output", type=Path, default=DEFAULT_METADATA_OUTPUT)
    args = parser.parse_args()

    candidates = json.loads(args.input.read_text(encoding="utf-8"))
    annotations, metadata = promote_approved_candidates(candidates)
    errors = validate_annotations(annotations)
    if errors:
        raise ValueError("approved candidate validation failed: " + "; ".join(errors))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([asdict(record) for record in annotations], indent=2) + "\n",
        encoding="utf-8",
    )
    args.metadata_output.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Promoted {len(annotations)} explicitly approved candidates: {args.output}")
    print(f"Split metadata sidecar: {args.metadata_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
