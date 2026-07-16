# Engineering Incident Intelligence and Evaluation Platform

A production-oriented Applied AI portfolio project for engineering incident triage.

This repository demonstrates the full lifecycle: domain taxonomy, evidence-grounded annotation, structured extraction, prompt-only/RAG/LoRA/local-model comparison, reproducible evaluation, human review, and eventual API deployment.

## First milestone

The first milestone establishes the ground-truth and evaluation layer:

- typed incident annotation schema
- documented taxonomy and abstention policy
- sample pressure-drop incidents
- dataset validation
- deterministic train/validation/test splitting
- baseline evaluation interfaces

No model claims should be made until this layer is stable.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/validate_dataset.py
python scripts/split_dataset.py
pytest
```

## Roadmap

1. Ground truth and evaluation foundation
2. Prompt-only structured-output baseline
3. Retrieval-augmented triage
4. LoRA comparison
5. Human-in-the-loop workflow
6. FastAPI/PostgreSQL/Docker deployment
7. Quantized local-model evaluation

## Portfolio positioning

This project demonstrates Applied AI engineering, AI evaluation, dataset curation, structured outputs, RAG, human-in-the-loop design, LoRA, production API design, and Python/Rust integration.
