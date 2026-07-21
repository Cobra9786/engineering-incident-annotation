# Pressure Sensor Diagnostics

## Signal loss

When an electronic pressure reading falls to zero or becomes unavailable while an independent mechanical gauge remains stable, the process pressure may be normal. Inspect wiring, connectors, transmitter power, communications, and signal conditioning.

Classify the primary failure mode as `signal_loss` when the measurement disappears or becomes unavailable because of wiring, connection, power, or communications problems.

A loose connector is a probable cause. It is not itself the failure-mode taxonomy value.

## Calibration drift

A repeatable offset between a pressure transmitter and a trusted calibrated reference across multiple operating points supports `calibration_drift`.

Calibration drift differs from signal loss:

- calibration drift produces a consistent but incorrect measurement
- signal loss produces a missing, zero, intermittent, or unavailable measurement