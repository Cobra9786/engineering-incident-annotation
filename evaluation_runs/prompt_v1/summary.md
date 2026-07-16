# Prompt Baseline v1

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- Run timestamp: `2026-07-16T16:07:50.105106+00:00`
- Held-out incidents: 4
- Valid predictions: 3
- Invalid predictions: 1
- JSON and contract validity: 75.0%
- Exact record match rate: 0.0%
- Average latency: 2.462 seconds

## Field Accuracy

| Field | Accuracy |
|---|---:|
| `component` | 50.0% |
| `failure_mode` | 0.0% |
| `severity` | 25.0% |
| `urgency` | 25.0% |
| `abstain` | 75.0% |
| `requires_human_review` | 50.0% |

## Incident Results

### INC-0003

- Status: invalid prediction
- Error: `model prediction failed business validation: invalid failure_mode: wiring_loose`
- Latency: 3.184 seconds

### INC-0018

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`, `severity`, `urgency`, `requires_human_review`
- `failure_mode`: expected `mechanical_jam`, predicted `line_leak`
- `severity`: expected `high`, predicted `low`
- `urgency`: expected `immediate`, predicted `routine`
- `requires_human_review`: expected `True`, predicted `False`
- Latency: 2.288 seconds

### INC-0009

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `failure_mode`
- `component`: expected `pressure_sensor`, predicted `unknown`
- `failure_mode`: expected `calibration_drift`, predicted `software_fault`
- Latency: 2.133 seconds

### INC-0010

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`, `severity`, `urgency`
- `failure_mode`: expected `pressure_drop`, predicted `line_leak`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- Latency: 2.242 seconds

## Interpretation

This run is the prompt-only reference baseline. Future RAG, LoRA, and LoRA-plus-RAG configurations must be evaluated against the same held-out records and the same annotation contract.
