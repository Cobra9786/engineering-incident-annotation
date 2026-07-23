from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pytest

from incident_intelligence.dataset import load_annotations, validate_annotations
from incident_intelligence.models import IncidentAnnotation
from incident_intelligence.synthetic_data import (
    SCENARIO_PAIRS,
    VARIATIONS_PER_FAMILY,
    generate_candidates,
    grouped_split,
    promote_approved_candidates,
)

def _approved_candidates() -> list[dict[str, object]]:
    candidates = generate_candidates()
    for candidate in candidates:
        candidate["review"]["status"] = "approved"
        candidate["review"]["reviewer"] = "test-reviewer"
    return candidates

def test_generation_preserves_fixed_dataset_size():
    candidates = generate_candidates()

    assert len(candidates) == 160


def test_scenario_pairs_preserve_fixed_split_size():
    assert len(SCENARIO_PAIRS) == 40
    assert len(SCENARIO_PAIRS) * VARIATIONS_PER_FAMILY == 160


def test_generation_is_deterministic() -> None:
    assert generate_candidates(seed=42) == generate_candidates(seed=42)
    assert generate_candidates(seed=42) != generate_candidates(seed=43)


def test_generated_annotations_are_contract_valid() -> None:
    candidates = generate_candidates()
    annotations = [
        IncidentAnnotation.from_dict(candidate["annotation"])
        for candidate in candidates
    ]

    assert len(annotations) == 160
    assert validate_annotations(annotations) == []
    assert all(set(candidate["annotation"]) == set(asdict(annotations[index]))
               for index, candidate in enumerate(candidates))


def test_generated_ids_and_normalized_reports_are_unique() -> None:
    candidates = generate_candidates()
    ids = [candidate["annotation"]["incident_id"] for candidate in candidates]
    reports = [
        " ".join(candidate["annotation"]["report"].casefold().split())
        for candidate in candidates
    ]

    assert len(ids) == len(set(ids)) == 160
    assert len(reports) == len(set(reports)) == 160


def test_pending_candidates_are_not_automatically_promoted() -> None:
    annotations, metadata = promote_approved_candidates(generate_candidates())

    assert annotations == []
    assert metadata == {}


def test_grouped_split_has_exact_sizes_and_family_isolation() -> None:
    annotations, metadata = promote_approved_candidates(_approved_candidates())
    splits = grouped_split(annotations, metadata)

    assert {name: len(rows) for name, rows in splits.items()} == {
        "train": 120,
        "validation": 20,
        "held_out_test": 20,
    }
    family_split: dict[str, str] = {}
    for split_name, rows in splits.items():
        for row in rows:
            family = metadata[row.incident_id]["scenario_family"]
            assert family_split.setdefault(family, split_name) == split_name


def test_grouped_split_fails_clearly_for_wrong_record_count() -> None:
    annotations, metadata = promote_approved_candidates(_approved_candidates())

    with pytest.raises(ValueError, match="exact split requires 160"):
        grouped_split(annotations[:-1], metadata)


def test_grouped_split_fails_when_family_sizes_make_targets_impossible() -> None:
    annotations, metadata = promote_approved_candidates(_approved_candidates())
    for index, annotation in enumerate(annotations):
        metadata[annotation.incident_id]["scenario_family"] = (
            "one-record-family" if index == 0 else "remaining-records"
        )

    with pytest.raises(ValueError, match="impossible without splitting"):
        grouped_split(annotations, metadata)


def test_ground_truth_splits_are_disjoint_and_complete() -> None:
    root = Path(__file__).resolve().parents[1]

    ground_truth = load_annotations(
        root / "data" / "ground_truth" / "incidents.json"
    )
    train = load_annotations(root / "data" / "splits" / "train.json")
    validation = load_annotations(
        root / "data" / "splits" / "validation.json"
    )
    held_out = load_annotations(
        root / "data" / "splits" / "held_out_test.json"
    )

    train_ids = {record.incident_id for record in train}
    validation_ids = {record.incident_id for record in validation}
    held_out_ids = {record.incident_id for record in held_out}
    ground_truth_ids = {
        record.incident_id for record in ground_truth
    }

    assert len(train) == 120
    assert len(validation) == 20
    assert len(held_out) == 20

    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(held_out_ids)
    assert validation_ids.isdisjoint(held_out_ids)

    combined_ids = train_ids | validation_ids | held_out_ids

    assert combined_ids == ground_truth_ids
    assert len(combined_ids) == 160

def test_scenario_families_do_not_cross_splits() -> None:
    root = Path(__file__).resolve().parents[1]

    splits = {
        "train": load_annotations(
            root / "data" / "splits" / "train.json"
        ),
        "validation": load_annotations(
            root / "data" / "splits" / "validation.json"
        ),
        "held_out_test": load_annotations(
            root / "data" / "splits" / "held_out_test.json"
        ),
    }

    family_owners: dict[int, str] = {}

    for split_name, records in splits.items():
        for record in records:
            incident_number = int(record.incident_id.removeprefix("SYN-"))

            # SYN-0001..0004 = family 1,
            # SYN-0005..0008 = family 2, etc.
            family_number = (incident_number - 1) // 4

            existing_owner = family_owners.get(family_number)

            if existing_owner is not None:
                assert existing_owner == split_name

            family_owners[family_number] = split_name

    assert len(family_owners) == 40