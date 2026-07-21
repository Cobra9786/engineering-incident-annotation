# Deterministic Severity and Urgency Policy

Severity and urgency express operational business policy, so they are assigned by deterministic Python rules after the model prediction has passed the existing parser and schema checks. The model remains responsible for engineering diagnosis: component, failure mode, probable cause, evidence, recommended action, confidence, abstention, and review signals.

The inference boundary is therefore: report → diagnostics retrieval and model inference → parsed annotation → deterministic severity/urgency policy → final annotation. Policy application replaces only severity and urgency; it also records the matching rule identifier and rationale for evaluation audit trails.

Rules are evaluated in priority order: explicit critical conditions, explicit high-impact conditions, the control-valve rule, medium conditions, low conditions, then a low/routine fallback. Add future business rules as explicit phrase sets, focused predicates, and ordered `_Rule` entries. Avoid broad substring tests or inferred safety conditions.

This separation makes operational decisions repeatable, independently testable, and auditable while allowing the foundation model to focus on evidence-grounded engineering diagnosis.
