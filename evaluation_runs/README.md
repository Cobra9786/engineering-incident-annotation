# Evaluation Runs

Each directory records one reproducible model configuration evaluated against the fixed held-out test set.

## Planned configurations

1. `prompt_v1`
   - Qwen prompt-only baseline

2. `rag_v1`
   - Qwen with retrieved manuals, failure guidance, and similar incidents

3. `lora_v1`
   - Qwen with a trained LoRA adapter

4. `lora_rag_v1`
   - LoRA-adapted Qwen with retrieved domain context

All configurations use the same:

- annotation schema
- parser
- business validation
- held-out test records
- exact-match metrics

This allows changes in model behavior to be compared without changing the benchmark.