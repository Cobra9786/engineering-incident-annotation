#!/usr/bin/env python3

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from incident_intelligence.parser import (
    PredictionParseError,
    parse_incident_prediction,
)
from incident_intelligence.prompt import build_incident_prompt
from incident_intelligence.qwen import QwenIncidentGenerator


def main() -> int:
    raw_path = ROOT / "data" / "raw" / "incidents.jsonl"

    first_line = raw_path.read_text(
        encoding="utf-8"
    ).splitlines()[0]

    raw_record = json.loads(first_line)

    prompt = build_incident_prompt(
        incident_id=raw_record["incident_id"],
        report=raw_record["report"],
    )

    generator = QwenIncidentGenerator()
    result = generator.generate(prompt)

    print("Raw model output:")
    print(result.text)
    print()
    print(f"Model: {result.model_id}")
    print(f"Prompt tokens: {result.prompt_tokens}")
    print(f"Generated tokens: {result.generated_tokens}")
    print(f"Latency: {result.latency_seconds:.3f} seconds")

    try:
        prediction = parse_incident_prediction(
            result.text,
            incident_id=raw_record["incident_id"],
            report=raw_record["report"],
        )
    except PredictionParseError as error:
        print()
        print(f"Prediction invalid: {error}")
        return 1

    print()
    print("Parsed prediction:")
    print(
        json.dumps(
            prediction.__dict__,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())