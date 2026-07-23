# Synthetic Dataset Review Workflow

Synthetic data follows a gated workflow:

1. **Raw generation:** `python scripts/generate_synthetic_candidates.py` deterministically creates 160 candidates with a fixed seed. Each candidate wraps an unchanged `IncidentAnnotation` plus separate generation metadata (`scenario_family`, `variation_id`) and a pending review record.
2. **Candidate review:** a qualified reviewer checks the report, diagnosis, evidence, action, and policy fields. The reviewer changes `review.status` to `approved` only after correcting any unsupported label. Pending or rejected candidates remain outside reviewed data.
3. **Approval promotion:** `python scripts/promote_approved_candidates.py` validates and promotes only explicitly approved annotations. Its annotation JSON contains no generation or review fields; a separate metadata sidecar retains scenario-family grouping.
4. **Grouped split:** `python scripts/split_generated_dataset.py` creates separate 120/20/20 train, validation, and held-out files. It keeps each scenario family in one split, fails if exact sizes are impossible, and checks against the existing protected held-out set.
5. **Training and evaluation:** only reviewed, promoted splits may be used. Synthetic candidates are never ground truth merely because they were generated. This task does not train a model.

Run `python scripts/report_generated_dataset.py` to inspect vocabulary coverage, review status, duplicates, split overlap, and scenario-family leakage. Existing `data/ground_truth` and `data/splits/held_out_test.json` remain unchanged.
