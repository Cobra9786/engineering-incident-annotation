#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.dataset import load_annotations, validate_annotations


EXPECTED_RECORD_COUNT = 160
EXPECTED_FAMILY_COUNT = 40
RECORDS_PER_FAMILY = 4

TRAIN_FAMILIES = 30
VALIDATION_FAMILIES = 5
HELD_OUT_FAMILIES = 5

DEFAULT_SEED = 20260723

INCIDENT_ID_PATTERN = re.compile(r"^SYN-(\d{4})$")


def incident_number(record: Any) -> int:
    match = INCIDENT_ID_PATTERN.fullmatch(record.incident_id)
    if match is None:
        raise ValueError(
            f"Unexpected incident ID format: {record.incident_id!r}. "
            "Expected IDs such as SYN-0001."
        )

    return int(match.group(1))


def validate_source_records(records: list[Any]) -> list[Any]:
    errors = validate_annotations(records)
    if errors:
        raise ValueError(
            "Ground-truth dataset validation failed:\n"
            + "\n".join(f"- {error}" for error in errors)
        )

    if len(records) != EXPECTED_RECORD_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_RECORD_COUNT} records, found {len(records)}."
        )

    ordered_records = sorted(records, key=incident_number)

    incident_ids = [record.incident_id for record in ordered_records]
    if len(set(incident_ids)) != len(incident_ids):
        raise ValueError("Duplicate incident IDs were found.")

    numbers = [incident_number(record) for record in ordered_records]
    expected_numbers = list(range(1, EXPECTED_RECORD_COUNT + 1))

    if numbers != expected_numbers:
        missing = sorted(set(expected_numbers) - set(numbers))
        unexpected = sorted(set(numbers) - set(expected_numbers))

        raise ValueError(
            "Incident IDs are not the expected contiguous range "
            "SYN-0001 through SYN-0160. "
            f"Missing numbers: {missing or 'none'}; "
            f"unexpected numbers: {unexpected or 'none'}."
        )

    return ordered_records


def build_families(records: list[Any]) -> list[list[Any]]:
    families = [
        records[index : index + RECORDS_PER_FAMILY]
        for index in range(0, len(records), RECORDS_PER_FAMILY)
    ]

    if len(families) != EXPECTED_FAMILY_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_FAMILY_COUNT} scenario families, "
            f"found {len(families)}."
        )

    for family_index, family in enumerate(families, start=1):
        if len(family) != RECORDS_PER_FAMILY:
            raise ValueError(
                f"Scenario family {family_index} contains {len(family)} "
                f"records instead of {RECORDS_PER_FAMILY}."
            )

        numbers = [incident_number(record) for record in family]
        expected_start = ((family_index - 1) * RECORDS_PER_FAMILY) + 1
        expected = list(
            range(expected_start, expected_start + RECORDS_PER_FAMILY)
        )

        if numbers != expected:
            raise ValueError(
                f"Scenario family {family_index} has incident numbers "
                f"{numbers}; expected {expected}."
            )

    return families


def flatten(families: list[list[Any]]) -> list[Any]:
    return [record for family in families for record in family]


def assert_no_family_leakage(
    split_families: dict[str, list[list[Any]]],
) -> None:
    ownership: dict[str, str] = {}

    for split_name, families in split_families.items():
        for family in families:
            family_key = family[0].incident_id

            if family_key in ownership:
                raise ValueError(
                    f"Scenario family {family_key} appears in both "
                    f"{ownership[family_key]} and {split_name}."
                )

            ownership[family_key] = split_name

    if len(ownership) != EXPECTED_FAMILY_COUNT:
        raise ValueError(
            f"Expected ownership for {EXPECTED_FAMILY_COUNT} families, "
            f"found {len(ownership)}."
        )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create deterministic, scenario-family-grouped splits from "
            "the canonical 160-record ground-truth dataset."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "ground_truth" / "incidents.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "splits",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing split files.",
    )
    args = parser.parse_args()

    output_paths = {
        "train": args.output_dir / "train.json",
        "validation": args.output_dir / "validation.json",
        "held_out_test": args.output_dir / "held_out_test.json",
    }
    manifest_path = args.output_dir / "split_manifest.json"

    existing_paths = [
        path
        for path in [*output_paths.values(), manifest_path]
        if path.exists()
    ]

    if existing_paths and not args.force:
        formatted = "\n".join(f"- {path}" for path in existing_paths)
        raise FileExistsError(
            "Split output files already exist:\n"
            f"{formatted}\n"
            "Use --force only after confirming they may be replaced."
        )

    records = load_annotations(args.input)
    ordered_records = validate_source_records(records)
    families = build_families(ordered_records)

    random.Random(args.seed).shuffle(families)

    split_families = {
        "train": families[:TRAIN_FAMILIES],
        "validation": families[
            TRAIN_FAMILIES : TRAIN_FAMILIES + VALIDATION_FAMILIES
        ],
        "held_out_test": families[
            TRAIN_FAMILIES + VALIDATION_FAMILIES :
        ],
    }

    expected_family_counts = {
        "train": TRAIN_FAMILIES,
        "validation": VALIDATION_FAMILIES,
        "held_out_test": HELD_OUT_FAMILIES,
    }

    for split_name, expected_count in expected_family_counts.items():
        actual_count = len(split_families[split_name])
        if actual_count != expected_count:
            raise ValueError(
                f"{split_name} has {actual_count} families; "
                f"expected {expected_count}."
            )

    assert_no_family_leakage(split_families)

    split_records = {
        split_name: flatten(grouped_families)
        for split_name, grouped_families in split_families.items()
    }

    expected_record_counts = {
        "train": 120,
        "validation": 20,
        "held_out_test": 20,
    }

    all_output_ids: list[str] = []

    for split_name, split_rows in split_records.items():
        expected_count = expected_record_counts[split_name]

        if len(split_rows) != expected_count:
            raise ValueError(
                f"{split_name} has {len(split_rows)} records; "
                f"expected {expected_count}."
            )

        errors = validate_annotations(split_rows)
        if errors:
            raise ValueError(
                f"{split_name} validation failed:\n"
                + "\n".join(f"- {error}" for error in errors)
            )

        all_output_ids.extend(record.incident_id for record in split_rows)

    source_ids = {record.incident_id for record in ordered_records}
    output_ids = set(all_output_ids)

    if len(all_output_ids) != len(output_ids):
        raise ValueError("A record appears in more than one split.")

    if output_ids != source_ids:
        missing = sorted(source_ids - output_ids)
        unexpected = sorted(output_ids - source_ids)

        raise ValueError(
            "Split records do not exactly match the source records. "
            f"Missing: {missing or 'none'}; "
            f"unexpected: {unexpected or 'none'}."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for split_name, split_rows in split_records.items():
        path = output_paths[split_name]
        write_json(path, [asdict(record) for record in split_rows])

        print(
            f"{split_name}: "
            f"{len(split_families[split_name])} families, "
            f"{len(split_rows)} records -> {path}"
        )

    manifest = {
        "schema_version": "1.0.0",
        "source": str(args.input.relative_to(ROOT)),
        "seed": args.seed,
        "grouping_rule": (
            "Each consecutive set of four incident IDs represents one "
            "scenario family: SYN-0001..0004, SYN-0005..0008, etc."
        ),
        "records_per_family": RECORDS_PER_FAMILY,
        "source_record_count": len(ordered_records),
        "splits": {
            split_name: {
                "family_count": len(grouped_families),
                "record_count": len(split_records[split_name]),
                "families": [
                    [record.incident_id for record in family]
                    for family in grouped_families
                ],
            }
            for split_name, grouped_families in split_families.items()
        },
    }

    write_json(manifest_path, manifest)
    print(f"manifest -> {manifest_path}")

    print("Grouped split completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())