#!/usr/bin/env python3

from pathlib import Path
import json
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.dataset import (
    load_annotations,
    validate_annotations,
)


def validate_json_schema() -> list[str]:
    schema_path = (
        ROOT
        / "schemas"
        / "incident_annotation.schema.json"
    )
    dataset_path = (
        ROOT
        / "data"
        / "ground_truth"
        / "incidents.json"
    )

    schema = json.loads(
        schema_path.read_text(encoding="utf-8")
    )
    records = json.loads(
        dataset_path.read_text(encoding="utf-8")
    )

    validator = Draft202012Validator(schema)
    errors: list[str] = []

    for index, record in enumerate(records):
        incident_id = record.get(
            "incident_id",
            f"record-{index}",
        )

        for error in sorted(
            validator.iter_errors(record),
            key=lambda item: list(item.path),
        ):
            location = ".".join(
                str(part)
                for part in error.path
            )

            suffix = f" at {location}" if location else ""

            errors.append(
                f"{incident_id}: {error.message}{suffix}"
            )

    return errors


def main() -> int:
    dataset_path = (
        ROOT
        / "data"
        / "ground_truth"
        / "incidents.json"
    )

    records = load_annotations(dataset_path)

    errors = [
        *validate_json_schema(),
        *validate_annotations(records),
    ]

    if errors:
        print("Dataset validation failed:")

        for error in errors:
            print(f"- {error}")

        return 1

    print(
        "Dataset valid: "
        f"{len(records)} incident records "
        "using schema version 1.0.0"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())