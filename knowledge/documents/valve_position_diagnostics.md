# Valve Position Diagnostics

Compare commanded valve position with physical position feedback.

When the controller commands substantial opening but physical feedback remains near closed, the valve or actuator may be mechanically stuck.

This pattern supports:

- component: `valve`
- failure mode: `mechanical_jam`

Do not classify the event as a line leak unless the report contains evidence of escaping fluid, visible leakage, or unexplained material loss.