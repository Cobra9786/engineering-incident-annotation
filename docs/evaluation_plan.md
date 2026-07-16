# Evaluation Plan

## Model variants
1. prompt-only baseline
2. RAG-enhanced baseline
3. LoRA-adapted model
4. optional quantized local model

## Metrics
- JSON validity
- schema compliance
- exact field accuracy
- macro F1
- false escalation rate
- missed critical-incident rate
- hallucinated evidence rate
- abstention precision and recall
- latency and inference cost
- reviewer disagreement and correction rate

A system is not successful merely because aggregate accuracy is high. Missed critical incidents, fabricated evidence, and unjustified escalation must be measured separately.
