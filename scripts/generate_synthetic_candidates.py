#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.synthetic_data import (
    DEFAULT_GENERATION_SEED,
    generate_candidates,
)


DEFAULT_OUTPUT = ROOT / "data" / "candidates" / "generated_incident_candidates.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic review candidates.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=DEFAULT_GENERATION_SEED)
    args = parser.parse_args()

    candidates = generate_candidates(seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidates, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(candidates)} pending candidates: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
