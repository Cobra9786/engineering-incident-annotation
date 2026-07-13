# Roadmap

## Phase 1: Ground truth
Finalize schema, annotate 50 pressure-related incidents, document edge cases, validate every record, and create deterministic splits.

## Phase 2: Baseline inference
Implement a prompt template, generate structured predictions, preserve raw responses, and score held-out cases.

## Phase 3: Retrieval
Index prior incidents and equipment documentation; require evidence grounded in retrieved text.

## Phase 4: Adaptation
Train a LoRA adapter and compare prompt-only, RAG, and LoRA runs.

## Phase 5: Workflow
Add human approval, ticket proposals, and an audit trail. Do not permit autonomous high-risk action.

## Phase 6: Deployment
Add FastAPI, PostgreSQL, Docker, authentication, metrics, tracing, and a Rust ingestion service.
