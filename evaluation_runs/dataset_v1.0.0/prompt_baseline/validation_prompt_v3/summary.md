# Prompt-Only Baseline — Dataset v1.0.0

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Run timestamp: `2026-07-23T19:01:43.860194+00:00`
- Dataset split: `validation`
- Incidents: 20
- Valid predictions: 20
- Invalid predictions: 0
- JSON and contract validity: 100.0%
- Exact record match rate: 10.0%
- Average latency: 5.195 seconds

## Classification Metrics

Macro averages give every ground-truth class equal importance. Invalid responses are represented as `__invalid__`.

| Field | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Exact Match |
|---|---:|---:|---:|---:|---:|
| `component` | 100.0% | 85.0% | 88.0% | 88.0% | 85.0% |
| `failure_mode` | 100.0% | 95.0% | 97.1% | 97.1% | 95.0% |
| `severity` | 51.1% | 41.7% | 36.5% | 43.8% | 50.0% |
| `urgency` | 90.9% | 87.5% | 87.0% | 84.5% | 85.0% |

## Per-Class Metrics

### `component`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `controller` | 100.0% | 25.0% | 40.0% | 4 |
| `filter` | 100.0% | 100.0% | 100.0% | 4 |
| `power_supply` | 100.0% | 100.0% | 100.0% | 4 |
| `pump` | 100.0% | 100.0% | 100.0% | 4 |
| `temperature_sensor` | 100.0% | 100.0% | 100.0% | 4 |

### `failure_mode`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `blockage` | 100.0% | 75.0% | 85.7% | 4 |
| `calibration_drift` | 100.0% | 100.0% | 100.0% | 4 |
| `overheating` | 100.0% | 100.0% | 100.0% | 4 |
| `seal_leak` | 100.0% | 100.0% | 100.0% | 4 |
| `valve_misconfiguration` | 100.0% | 100.0% | 100.0% | 4 |

### `severity`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `high` | 100.0% | 25.0% | 40.0% | 8 |
| `low` | 0.0% | 0.0% | 0.0% | 4 |
| `medium` | 53.3% | 100.0% | 69.6% | 8 |

### `urgency`

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `immediate` | 100.0% | 62.5% | 76.9% | 8 |
| `routine` | 100.0% | 100.0% | 100.0% | 4 |
| `within_24_hours` | 72.7% | 100.0% | 84.2% | 8 |

## Confusion Matrices

Rows are ground-truth classes. Columns are predicted classes.

### `component`

| Actual \ Predicted | `controller` | `filter` | `power_supply` | `pump` | `temperature_sensor` | `valve` |
|---|---:|---:|---:|---:|---:|---:|
| `controller` | 1 | 0 | 0 | 0 | 0 | 3 |
| `filter` | 0 | 4 | 0 | 0 | 0 | 0 |
| `power_supply` | 0 | 0 | 4 | 0 | 0 | 0 |
| `pump` | 0 | 0 | 0 | 4 | 0 | 0 |
| `temperature_sensor` | 0 | 0 | 0 | 0 | 4 | 0 |
| `valve` | 0 | 0 | 0 | 0 | 0 | 0 |

### `failure_mode`

| Actual \ Predicted | `blockage` | `calibration_drift` | `overheating` | `pressure_drop` | `seal_leak` | `valve_misconfiguration` |
|---|---:|---:|---:|---:|---:|---:|
| `blockage` | 3 | 0 | 0 | 1 | 0 | 0 |
| `calibration_drift` | 0 | 4 | 0 | 0 | 0 | 0 |
| `overheating` | 0 | 0 | 4 | 0 | 0 | 0 |
| `pressure_drop` | 0 | 0 | 0 | 0 | 0 | 0 |
| `seal_leak` | 0 | 0 | 0 | 0 | 4 | 0 |
| `valve_misconfiguration` | 0 | 0 | 0 | 0 | 0 | 4 |

### `severity`

| Actual \ Predicted | `critical` | `high` | `low` | `medium` |
|---|---:|---:|---:|---:|
| `critical` | 0 | 0 | 0 | 0 |
| `high` | 3 | 2 | 0 | 3 |
| `low` | 0 | 0 | 0 | 4 |
| `medium` | 0 | 0 | 0 | 8 |

### `urgency`

| Actual \ Predicted | `immediate` | `routine` | `within_24_hours` |
|---|---:|---:|---:|
| `immediate` | 5 | 0 | 3 |
| `routine` | 0 | 4 | 0 |
| `within_24_hours` | 0 | 0 | 8 |

## Incident Results

### SYN-0049

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.889 seconds

### SYN-0050

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.023 seconds

### SYN-0051

- Status: valid prediction with mismatches
- Mismatched fields: `component`, `requires_human_review`
- `component`: expected `controller`, predicted `valve`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.914 seconds

### SYN-0052

- Status: valid prediction with mismatches
- Mismatched fields: `requires_human_review`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.114 seconds

### SYN-0041

- Status: valid prediction with mismatches
- Mismatched fields: `requires_human_review`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.097 seconds

### SYN-0042

- Status: valid prediction with mismatches
- Mismatched fields: `requires_human_review`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.321 seconds

### SYN-0043

- Status: valid prediction with mismatches
- Mismatched fields: `requires_human_review`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.188 seconds

### SYN-0044

- Status: valid prediction with mismatches
- Mismatched fields: `requires_human_review`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.455 seconds

### SYN-0017

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`
- `severity`: expected `high`, predicted `medium`
- `urgency`: expected `immediate`, predicted `within_24_hours`
- Latency: 5.165 seconds

### SYN-0018

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `urgency`
- `severity`: expected `high`, predicted `medium`
- `urgency`: expected `immediate`, predicted `within_24_hours`
- Latency: 5.441 seconds

### SYN-0019

- Status: exact match on scored fields
- Latency: 5.450 seconds

### SYN-0020

- Status: valid prediction with mismatches
- Mismatched fields: `failure_mode`, `severity`, `urgency`
- `failure_mode`: expected `blockage`, predicted `pressure_drop`
- `severity`: expected `high`, predicted `medium`
- `urgency`: expected `immediate`, predicted `within_24_hours`
- Latency: 5.297 seconds

### SYN-0109

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.933 seconds

### SYN-0110

- Status: exact match on scored fields
- Latency: 4.965 seconds

### SYN-0111

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 4.962 seconds

### SYN-0112

- Status: valid prediction with mismatches
- Mismatched fields: `severity`
- `severity`: expected `high`, predicted `critical`
- Latency: 5.224 seconds

### SYN-0013

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `requires_human_review`
- `severity`: expected `low`, predicted `medium`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.866 seconds

### SYN-0014

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `requires_human_review`
- `severity`: expected `low`, predicted `medium`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 4.992 seconds

### SYN-0015

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `requires_human_review`
- `severity`: expected `low`, predicted `medium`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.080 seconds

### SYN-0016

- Status: valid prediction with mismatches
- Mismatched fields: `severity`, `requires_human_review`
- `severity`: expected `low`, predicted `medium`
- `requires_human_review`: expected `False`, predicted `True`
- Latency: 5.524 seconds

## Interpretation

This run evaluates the prompt-only system on the validation split. General prompt, parser, and generation issues may be investigated using these results. The held-out split must remain untouched until the baseline configuration is frozen.
