#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "data" / "candidates" / "generated_incident_candidates.json"
DEFAULT_SPLIT_DIR = ROOT / "data" / "generated_splits"


def _normalized_report(report: str) -> str:
    return " ".join(report.casefold().split())


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def build_report(
    candidates: list[dict[str, Any]],
    split_payloads: dict[str, list[dict[str, Any]]],
    protected_held_out: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    annotations = [candidate["annotation"] for candidate in candidates]
    families = [
        str(candidate["generation_metadata"]["scenario_family"])
        for candidate in candidates
    ]
    summary: dict[str, Any] = {
        "total_records": len(annotations),
        "component_counts": dict(sorted(Counter(row["component"] for row in annotations).items())),
        "failure_mode_counts": dict(sorted(Counter(row["failure_mode"] for row in annotations).items())),
        "severity_counts": dict(sorted(Counter(row["severity"] for row in annotations).items())),
        "urgency_counts": dict(sorted(Counter(row["urgency"] for row in annotations).items())),
        "abstain_counts": dict(sorted(Counter(str(row["abstain"]).lower() for row in annotations).items())),
        "requires_human_review_counts": dict(
            sorted(Counter(str(row["requires_human_review"]).lower() for row in annotations).items())
        ),
        "scenario_family_count": len(set(families)),
        "scenario_family_sizes": dict(sorted(Counter(families).items())),
        "duplicate_incident_ids": _duplicates([row["incident_id"] for row in annotations]),
        "duplicate_normalized_reports": _duplicates(
            [_normalized_report(row["report"]) for row in annotations]
        ),
        "review_status_counts": dict(
            sorted(Counter(candidate["review"]["status"] for candidate in candidates).items())
        ),
    }

    split_ids: dict[str, set[str]] = {
        name: {row["incident_id"] for row in rows}
        for name, rows in split_payloads.items()
    }
    overlaps: dict[str, list[str]] = {}
    names = sorted(split_ids)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            shared = sorted(split_ids[first] & split_ids[second])
            if shared:
                overlaps[f"{first}__{second}"] = shared

    family_by_id = {
        candidate["annotation"]["incident_id"]: candidate["generation_metadata"][
            "scenario_family"
        ]
        for candidate in candidates
    }
    family_splits: dict[str, set[str]] = {}
    for split_name, ids in split_ids.items():
        for incident_id in ids:
            if incident_id in family_by_id:
                family_splits.setdefault(family_by_id[incident_id], set()).add(split_name)
    leaked_families = {
        family: sorted(split_names)
        for family, split_names in family_splits.items()
        if len(split_names) > 1
    }
    summary["splits"] = {
        "counts": {name: len(rows) for name, rows in split_payloads.items()},
        "incident_id_overlap": overlaps,
        "scenario_family_leakage": leaked_families,
    }
    protected_held_out = protected_held_out or []
    protected_ids = {row["incident_id"] for row in protected_held_out}
    protected_reports = {
        _normalized_report(row["report"])
        for row in protected_held_out
    }
    summary["protected_held_out_leakage"] = {
        "incident_ids": sorted(
            row["incident_id"]
            for row in annotations
            if row["incident_id"] in protected_ids
        ),
        "normalized_reports": sorted(
            row["incident_id"]
            for row in annotations
            if _normalized_report(row["report"]) in protected_reports
        ),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Report generated candidate coverage and leakage.")
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument(
        "--protected-held-out",
        type=Path,
        default=ROOT / "data" / "splits" / "held_out_test.json",
    )
    args = parser.parse_args()

    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    split_payloads = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(args.split_dir.glob("*.json"))
    } if args.split_dir.exists() else {}
    protected_held_out = json.loads(
        args.protected_held_out.read_text(encoding="utf-8")
    )
    print(
        json.dumps(
            build_report(candidates, split_payloads, protected_held_out),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
