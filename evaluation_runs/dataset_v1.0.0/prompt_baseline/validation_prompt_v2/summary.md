# Prompt-Only Baseline — Dataset v1.0.0

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Run timestamp: `2026-07-23T18:42:14.165085+00:00`
- Dataset split: `validation`
- Incidents: 20
- Valid predictions: 17
- Invalid predictions: 3
- JSON and contract validity: 85.0%
- Exact record match rate: 0.0%
- Average latency: 4.785 seconds

## Classification Metrics

Macro averages give every ground-truth class equal importance. Invalid responses are represented as `__invalid__`.

| Field | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Exact Match |
|---|---:|---:|---:|---:|---:|
| `component` | 80.0% | 65.0% | 68.0% | 68.0% | 65.0% |
| `failure_mode` | 80.0% | 50.0% | 56.0% | 56.0% | 50.0% |
| `severity` | 33.3% | 16.7% | 22.2% | 26.7% | 20.0% |
| `urgency` | 37.0% | 41.7% | 38.5% | 43.1% | 45.0% |

## Per-Class Metrics

### `component`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `controller` | 0.0% | 0.0% | 0.0% | 4 |
| `filter` | 100.0% | 100.0% | 100.0% | 4 |
| `power_supply` | 100.0% | 100.0% | 100.0% | 4 |
| `pump` | 100.0% | 25.0% | 40.0% | 4 |
| `temperature_sensor` | 100.0% | 100.0% | 100.0% | 4 |

### `failure_mode`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `blockage` | 0.0% | 0.0% | 0.0% | 4 |
| `calibration_drift` | 100.0% | 100.0% | 100.0% | 4 |
| `overheating` | 100.0% | 100.0% | 100.0% | 4 |
| `seal_leak` | 100.0% | 25.0% | 40.0% | 4 |
| `valve_misconfiguration` | 100.0% | 25.0% | 40.0% | 4 |

### `severity`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `high` | 100.0% | 50.0% | 66.7% | 8 |
| `low` | 0.0% | 0.0% | 0.0% | 4 |
| `medium` | 0.0% | 0.0% | 0.0% | 8 |

### `urgency`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `immediate` | 100.0% | 100.0% | 100.0% | 8 |
| `routine` | 11.1% | 25.0% | 15.4% | 4 |
| `within_24_hours` | 0.0% | 0.0% | 0.0% | 8 |

## Confusion Matrices

Rows are ground-truth classes. Columns are predicted classes.

### `component`

| Actual \ Predicted | `controller` | `filter` | `power_supply` | `pump` | `temperature_sensor` | `valve` | `__invalid__` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `controller` | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| `filter` | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| `power_supply` | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| `pump` | 0 | 0 | 0 | 1 | 0 | 0 | 3 |
| `temperature_sensor` | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| `valve` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### `failure_mode`

| Actual \ Predicted | `blockage` | `calibration_drift` | `cavitation` | `configuration_error` | `overheating` | `pressure_drop` | `seal_leak` | `valve_misconfiguration` | `__invalid__` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `blockage` | 0 | 0 | 1 | 0 | 0 | 3 | 0 | 0 | 0 |
| `calibration_drift` | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `cavitation` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `configuration_error` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `overheating` | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| `pressure_drop` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `seal_leak` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 3 |
| `valve_misconfiguration` | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 0 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### `severity`

| Actual \ Predicted | `critical` | `high` | `low` | `medium` | `__invalid__` |
|---|---:|---:|---:|---:|---:|
| `critical` | 0 | 0 | 0 | 0 | 0 |
| `high` | 4 | 4 | 0 | 0 | 0 |
| `low` | 0 | 0 | 0 | 1 | 3 |
| `medium` | 0 | 0 | 8 | 0 | 0 |
| `__invalid__` | 0 | 0 | 0 | 0 | 0 |

### `urgency`

| Actual \ Predicted | `immediate` | `routine` | `within_24_hours` | `__invalid__` |
|---|---:|---:|---:|---:|
| `immediate` | 8 | 0 | 0 | 0 |
| `routine` | 0 | 1 | 0 | 3 |
| `within_24_hours` | 0 | 8 | 0 | 0 |
| `__invalid__` | 0 | 0 | 0 | 0 |

## Incident Results

### SYN-0049

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `severity`, `urgency`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.930 seconds

### SYN-0050

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `failure_mode`, `severity`, `urgency`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `failure_mode`: expected `valve_misconfiguration`, predicted `configuration_error`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.435 seconds

### SYN-0051

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `failure_mode`, `severity`, `urgency`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `failure_mode`: expected `valve_misconfiguration`, predicted `configuration_error`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.385 seconds

### SYN-0052

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `failure_mode`, `severity`, `urgency`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `failure_mode`: expected `valve_misconfiguration`, predicted `configuration_error`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.796 seconds

### SYN-0041

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`, `requires_human_review`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.724 seconds

### SYN-0042

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`, `requires_human_review`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.984 seconds

### SYN-0043

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`, `requires_human_review`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.121 seconds

### SYN-0044

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`, `requires_human_review`
- `severity`: expected `medium`, predicted `low`
- `urgency`: expected `within_24_hours`, predicted `routine`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.142 seconds

### SYN-0017

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `pressure_drop`
- Latency: 4.709 seconds

### SYN-0018

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `pressure_drop`
- Latency: 4.394 seconds

### SYN-0019

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `cavitation`
- Latency: 4.716 seconds

### SYN-0020

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`
- `failure_mode`: expected `blockage`, predicted `pressure_drop`
- Latency: 4.859 seconds

### SYN-0109

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.778 seconds

### SYN-0110

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.705 seconds

### SYN-0111

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.821 seconds

### SYN-0112

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.861 seconds

### SYN-0013

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.132 seconds

### SYN-0014

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.745 seconds

### SYN-0015

- Status: invalid prediction
- Error: `model prediction failed business validation: unknown probable cause must require human review`
- Latency: 4.394 seconds

### SYN-0016

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `requires_human_review`
- `severity`: expected `low`, predicted `medium`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.068 seconds

## Interpretation

This run evaluates the prompt-only system on the validation split. General prompt, parser, and generation issues may be investigated using these results. The held-out split must remain untouched until the baseline configuration is frozen.
