# Prompt-Only Baseline — Dataset v1.0.0

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Run timestamp: `2026-07-23T18:18:21.438527+00:00`
- Dataset split: `validation`
- Incidents: 20
- Valid predictions: 10
- Invalid predictions: 10
- JSON and contract validity: 50.0%
- Exact record match rate: 0.0%
- Average latency: 4.705 seconds

## Classification Metrics

Macro averages give every ground-truth class equal importance. Invalid responses are represented as `__invalid__`.

| Field | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Exact Match |
|---|---:|---:|---:|---:|---:|
| `component` | 80.0% | 50.0% | 56.0% | 56.0% | 50.0% |
| `failure_mode` | 60.0% | 30.0% | 36.0% | 36.0% | 30.0% |
| `severity` | 22.2% | 16.7% | 19.0% | 22.9% | 20.0% |
| `urgency` | 26.7% | 33.3% | 29.6% | 35.6% | 40.0% |

## Per-Class Metrics

### `component`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `controller` | 0.0% | 0.0% | 0.0% | 4 |
| `filter` | 100.0% | 100.0% | 100.0% | 4 |
| `power_supply` | 100.0% | 100.0% | 100.0% | 4 |
| `pump` | 100.0% | 25.0% | 40.0% | 4 |
| `temperature_sensor` | 100.0% | 25.0% | 40.0% | 4 |

### `failure_mode`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `blockage` | 0.0% | 0.0% | 0.0% | 4 |
| `calibration_drift` | 100.0% | 25.0% | 40.0% | 4 |
| `overheating` | 100.0% | 100.0% | 100.0% | 4 |
| `seal_leak` | 100.0% | 25.0% | 40.0% | 4 |
| `valve_misconfiguration` | 0.0% | 0.0% | 0.0% | 4 |

### `severity`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `high` | 66.7% | 50.0% | 57.1% | 8 |
| `low` | 0.0% | 0.0% | 0.0% | 4 |
| `medium` | 0.0% | 0.0% | 0.0% | 8 |

### `urgency`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `immediate` | 80.0% | 100.0% | 88.9% | 8 |
| `routine` | 0.0% | 0.0% | 0.0% | 4 |
| `within_24_hours` | 0.0% | 0.0% | 0.0% | 8 |

## Confusion Matrices

Rows are ground-truth classes. Columns are predicted classes.

### `component`

| Actual \ Predicted | `controller` | `filter` | `power_supply` | `pump` | `temperature_sensor` | `__invalid__` |
|---|---:|---:|---:|---:|---:|---:|
| `controller` | 0 | 0 | 0 | 0 | 0 | 4 |
| `filter` | 0 | 4 | 0 | 0 | 0 | 0 |
| `power_supply` | 0 | 0 | 4 | 0 | 0 | 0 |
| `pump` | 0 | 0 | 0 | 1 | 0 | 3 |
| `temperature_sensor` | 0 | 0 | 0 | 0 | 1 | 3 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 | 0 |

### `failure_mode`

| Actual \ Predicted | `blockage` | `calibration_drift` | `cavitation` | `overheating` | `seal_leak` | `valve_misconfiguration` | `__invalid__` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `blockage` | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| `calibration_drift` | 0 | 1 | 0 | 0 | 0 | 0 | 3 |
| `cavitation` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `overheating` | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| `seal_leak` | 0 | 0 | 0 | 0 | 1 | 0 | 3 |
| `valve_misconfiguration` | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### `severity`

| Actual \ Predicted | `critical` | `high` | `low` | `medium` | `__invalid__` |
|---|---:|---:|---:|---:|---:|
| `critical` | 0 | 0 | 0 | 0 | 0 |
| `high` | 4 | 4 | 0 | 0 | 0 |
| `low` | 0 | 1 | 0 | 0 | 3 |
| `medium` | 0 | 1 | 0 | 0 | 7 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 |

### `urgency`

| Actual \ Predicted | `immediate` | `routine` | `within_24_hours` | `__invalid__` |
|---|---:|---:|---:|---:|
| `immediate` | 8 | 0 | 0 | 0 |
| `routine` | 1 | 0 | 0 | 3 |
| `within_24_hours` | 1 | 0 | 0 | 7 |
| `__invalid__` | 0 | 0 | 0 | 0 |

## Incident Results

### SYN-0049

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 5.969 seconds

### SYN-0050

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.311 seconds

### SYN-0051

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.491 seconds

### SYN-0052

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 5.334 seconds

### SYN-0041

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`, `requires_human_review`
- `severity`: expected `medium`, predicted `high`
- `urgency`: expected `within_24_hours`, predicted `immediate`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.561 seconds

### SYN-0042

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.397 seconds

### SYN-0043

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.319 seconds

### SYN-0044

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.626 seconds

### SYN-0017

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `cavitation`
- Latency: 4.909 seconds

### SYN-0018

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `cavitation`
- Latency: 4.314 seconds

### SYN-0019

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `cavitation`
- Latency: 4.756 seconds

### SYN-0020

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `cavitation`
- Latency: 4.707 seconds

### SYN-0109

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.665 seconds

### SYN-0110

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.834 seconds

### SYN-0111

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.604 seconds

### SYN-0112

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 5.317 seconds

### SYN-0013

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`, `requires_human_review`
- `severity`: expected `low`, predicted `high`
- `urgency`: expected `routine`, predicted `immediate`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.662 seconds

### SYN-0014

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.317 seconds

### SYN-0015

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.179 seconds

### SYN-0016

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.821 seconds

## Interpretation

This run evaluates the prompt-only system on the validation split. General prompt, parser, and generation issues may be investigated using these results. The held-out split must remain untouched until the baseline configuration is frozen.
