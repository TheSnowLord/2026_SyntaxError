---
base_model: Qwen/Qwen2.5-0.5B-Instruct
library_name: peft
pipeline_tag: text-generation
tags:
- base_model:adapter:Qwen/Qwen2.5-0.5B-Instruct
- lora
- sft
- transformers
- trl
---

# AgentForge AI - Researcher Agent Model Card

## Model Details

### Model Description
The **Researcher Agent** is a specialized domain model fine-tuned for the AgentForge AI autonomous multi-agent orchestration platform. It is fine-tuned on top of Qwen/Qwen2.5-0.5B-Instruct using Hugging Face PEFT (LoRA).

- **Developed by:** SyntaxError Team (AgentForge AI)
- **Model type:** Causal Language Model Adapter (LoRA)
- **Language(s):** English, Python, JavaScript/React, SQL, Markdown
- **License:** Apache 2.0
- **Finetuned from model:** Qwen/Qwen2.5-0.5B-Instruct

## Uses

### Direct Use
Gathers architectural context and evaluates engineering specs.

### Ecosystem Integration
Used as Stage in the 5-stage AgentForge AI pipeline: Planner -> Decomposer -> Researcher -> Developer -> Evaluator.

## Training Details

### Training Data
Trained on research_data.jsonl containing high-quality domain system prompts and instruction-response pairs.

### Training Hyperparameters
- **Adapter Type:** LoRA (PEFT)
- **LoRA Rank (r):** 8
- **LoRA Alpha:** 16
- **Target Modules:** q_proj, k_proj, v_proj, o_proj
- **Learning Rate:** 2e-4
- **Precision:** float32 / float16

## Hardware & Environment
- **Hardware:** NVIDIA GeForce RTX 5060 Laptop GPU
- **Software:** PyTorch 2.6, PEFT 0.20.0, TRL 1.9.2, Transformers 5.14.1
### Framework versions

- PEFT 0.20.0