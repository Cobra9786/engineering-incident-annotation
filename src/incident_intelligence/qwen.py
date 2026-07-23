from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

DEFAULT_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"

@dataclass(frozen=True)
class GenerationResult:
    text: str
    latency_seconds: float
    prompt_tokens: int
    generated_tokens: int
    model_id: str


class QwenIncidentGenerator:
    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
    ) -> None:
        self.model_id = model_id

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
        )

        if torch.cuda.is_available():
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=quantization_config,
                device_map="auto",
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                dtype=torch.float32,
                device_map="cpu",
            )

        self.model.eval()

    def generate(
        self,
        prompt: str,
        *,
        max_new_tokens: int = 512,
    ) -> GenerationResult:
        messages: list[dict[str, str]] = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        chat_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs: dict[str, Any] = self.tokenizer(
            chat_text,
            return_tensors="pt",
        )

        model_device = next(self.model.parameters()).device
        inputs = {
            name: tensor.to(model_device)
            for name, tensor in inputs.items()
        }

        prompt_tokens = int(inputs["input_ids"].shape[-1])

        started = perf_counter()

        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        latency_seconds = perf_counter() - started

        generated_ids = outputs[0][prompt_tokens:]

        text = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        ).strip()

        return GenerationResult(
            text=text,
            latency_seconds=latency_seconds,
            prompt_tokens=prompt_tokens,
            generated_tokens=int(generated_ids.shape[-1]),
            model_id=self.model_id,
        )