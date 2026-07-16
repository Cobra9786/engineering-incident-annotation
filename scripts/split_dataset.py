#!/usr/bin/env python3

from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "ground_truth" / "incidents.json"
OUTPUT_DIR = ROOT / "data" / "splits"

records = json.loads(SOURCE.read_text(encoding="utf-8"))

random.Random(20260713).shuffle(records)

train_end = round(len(records) * 0.6)
validation_end = train_end + round(len(records) * 0.2)

splits = {
    "train.json": records[:train_end],
    "validation.json": records[train_end:validation_end],
    "held_out_test.json": records[validation_end:],
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for name, rows in splits.items():
    path = OUTPUT_DIR / name
    path.write_text(
        json.dumps(rows, indent=2) + "\n",
        encoding="utf-8",
    )
    print(name, len(rows))