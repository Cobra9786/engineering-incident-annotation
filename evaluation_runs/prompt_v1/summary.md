# Prompt Baseline v1

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- Run timestamp: `2026-07-16T18:49:43.245406+00:00`
- Held-out incidents: 4
- Valid predictions: 3
- Invalid predictions: 1
- JSON and contract validity: 75.0%
- Exact record match rate: 0.0%
- Average latency: 2.445 seconds

## Classification Metrics

Macro averages give every ground-truth class equal importance. Invalid responses are represented as `__invalid__`.

| Field | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Exact Match |
|---|---:|---:|---:|---:|---:|
| `component` | 66.7% | 66.7% | 66.7% | 50.0% | 50.0% |
| `failure_mode` | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| `severity` | 11.1% | 33.3% | 16.7% | 12.5% | 25.0% |
| `urgency` | 11.1% | 33.3% | 16.7% | 12.5% | 25.0% |

## Per-Class Metrics

### `component`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `pressure_sensor` | 0.0% | 0.0% | 0.0% | 2 |
| `reservoir` | 100.0% | 100.0% | 100.0% | 1 |
| `valve` | 100.0% | 100.0% | 100.0% | 1 |

### `failure_mode`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `calibration_drift` | 0.0% | 0.0% | 0.0% | 1 |
| `mechanical_jam` | 0.0% | 0.0% | 0.0% | 1 |
| `pressure_drop` | 0.0% | 0.0% | 0.0% | 1 |
| `signal_loss` | 0.0% | 0.0% | 0.0% | 1 |

### `severity`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `high` | 0.0% | 0.0% | 0.0% | 1 |
| `low` | 33.3% | 100.0% | 50.0% | 1 |
| `medium` | 0.0% | 0.0% | 0.0% | 2 |

### `urgency`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `immediate` | 0.0% | 0.0% | 0.0% | 1 |
| `routine` | 33.3% | 100.0% | 50.0% | 1 |
| `within_24_hours` | 0.0% | 0.0% | 0.0% | 2 |

## Confusion Matrices

Rows are ground-truth classes. Columns are predicted classes.

### `component`

| Actual \ Predicted | `pressure_sensor` | `reservoir` | `unknown` | `valve` | `__invalid__` |
|---|---:|---:|---:|---:|---:|
| `pressure_sensor` | 0 | 0 | 1 | 0 | 1 |
| `reservoir` | 0 | 1 | 0 | 0 | 0 |
| `unknown` | 0 | 0 | 0 | 0 | 0 |
| `valve` | 0 | 0 | 0 | 1 | 0 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 |

### `failure_mode`

| Actual \ Predicted | `calibration_drift` | `line_leak` | `mechanical_jam` | `pressure_drop` | `signal_loss` | `software_fault` | `__invalid__` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `calibration_drift` | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| `line_leak` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `mechanical_jam` | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `pressure_drop` | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `signal_loss` | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `software_fault` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### `severity`

| Actual \ Predicted | `high` | `low` | `medium` | `__invalid__` |
|---|---:|---:|---:|---:|
| `high` | 0 | 1 | 0 | 0 |
| `low` | 0 | 1 | 0 | 0 |
| `medium` | 0 | 1 | 0 | 1 |
| `__invalid__` | 0 | 0 | 0 | 0 |

### `urgency`

| Actual \ Predicted | `immediate` | `routine` | `within_24_hours` | `__invalid__` |
|---|---:|---:|---:|---:|
| `immediate` | 0 | 1 | 0 | 0 |
| `routine` | 0 | 1 | 0 | 0 |
| `within_24_hours` | 0 | 1 | 0 | 1 |
| `__invalid__` | 0 | 0 | 0 | 0 |

## Incident Results

### INC-0003

- Status: invalid prediction
- Error: `model prediction failed business validation: invalid failure_mode: wiring_loose`
- Latency: 3.123 seconds

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
- Latency: 2.126 seconds

### INC-0010

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`, `severity`, `urgency`
- `failure_mode`: expected `pressure_drop`, predicted `line_leak`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- Latency: 2.242 seconds

## Interpretation

This run is the prompt-only reference baseline. Future RAG, LoRA, and LoRA-plus-RAG systems must use the same held-out records, contract, and evaluation metrics.
