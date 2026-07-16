# Annotation Guidelines

## Objective
Create consistent, evidence-grounded incident annotations for model training and evaluation.

## Rules
1. Annotate only information supported by the report.
2. Separate observed evidence from inferred probable cause.
3. Prefer `unknown` over unsupported certainty.
4. Use one primary failure mode per record.
5. Record secondary conditions in `evidence`.
6. Set `abstain=true` when the report is too ambiguous.
7. Never invent measurements, components, or maintenance history.
8. Recommended actions must be proportional to the evidence.
9. High-severity or safety-related cases require human review.
10. Confidence reflects annotation certainty, not model confidence.

## Pressure-drop guidance
Use `pressure_drop` only when measured pressure fell below an expected value or declined unexpectedly. Do not use it for reduced flow alone, a known faulty gauge, unmeasured pressure, or normal depressurization.

## Probable cause
Annotate a probable cause only when direct evidence or a strong domain indicator supports it. Oil around a shaft seal supports `seal_leak`; erratic telemetry alone does not prove a physical leak.

## Abstention
Set `abstain=true` when the component cannot be identified, multiple primary failures are equally plausible, the report is contradictory, or required measurements are missing. Abstained records must require human review.
