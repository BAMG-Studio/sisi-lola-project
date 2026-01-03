---
base_model: gpt2
library_name: peft
pipeline_tag: text-generation
license: apache-2.0
language:
- en
- pcm
- yo
tags:
- nigerian
- african
- personality
- chatbot
- lagos
- lora
- transformers
---

# Sisi Lola Brain - Nigerian AI Personality Adapter

## Model Details

### Model Description

Sisi Lola Brain is a LoRA (Low-Rank Adaptation) fine-tuned language model adapter designed to give AI assistants a warm, culturally-aware Nigerian personality. The adapter captures the linguistic patterns, cultural references, and communication style characteristic of a friendly Lagos-based virtual host.

- **Developed by:** BAMG Studio
- **Model type:** LoRA Adapter for Causal Language Models
- **Language(s):** English, Nigerian Pidgin (pcm), Yoruba (yo)
- **License:** Apache 2.0
- **Fine-tuned from:** GPT-2 (base), compatible with TinyLlama and other causal LMs
- **Repository:** [BAMG-Studio/sisi-lola-project](https://github.com/BAMG-Studio/sisi-lola-project)

### Model Sources

- **Repository:** https://github.com/BAMG-Studio/sisi-lola-project
- **Demo:** Coming soon

## Uses

### Direct Use

This adapter is designed to be loaded on top of a compatible base model (GPT-2, TinyLlama, or similar) to provide Nigerian-flavored conversational AI responses.

**Primary use cases:**
- Virtual assistant with Nigerian personality
- Cultural tourism chatbot for Lagos/Nigeria
- Nigerian language learning companion
- Entertainment and social media content generation

### Downstream Use

Can be integrated into:
- FastAPI/Flask chatbot backends
- Discord/Telegram bots
- Voice assistants (pair with Sisi Lola Voice model)
- Social media automation tools

### Out-of-Scope Use

This model should NOT be used for:
- Generating harmful, misleading, or offensive content
- Impersonating real individuals
- Any illegal activities
- Medical, legal, or financial advice

## How to Get Started with the Model

### Installation

\`\`\`bash
pip install transformers peft torch
\`\`\`

### Quick Start

\`\`\`python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Load Sisi Lola adapter
model = PeftModel.from_pretrained(base_model, "sisilolalive/sisi-lola-brain")

# Generate response
prompt = "How are you today?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=100, do_sample=True, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
\`\`\`

## Technical Specifications

### Model Architecture

| Parameter | Value |
|-----------|-------|
| **Adapter Type** | LoRA (Low-Rank Adaptation) |
| **LoRA Rank (r)** | 16 |
| **LoRA Alpha** | 32 |
| **Target Modules** | c_attn, c_proj (GPT-2) |
| **Trainable Parameters** | 1.6M (1.29% of base model) |
| **Total Parameters** | 126M (with GPT-2 base) |

### Training Details

| Parameter | Value |
|-----------|-------|
| **Training Framework** | Hugging Face Transformers + PEFT |
| **Hardware** | NVIDIA RTX 3060 (6GB VRAM) |
| **Training Time** | ~6 seconds |
| **Epochs** | 3 |
| **Batch Size** | 4 |
| **Learning Rate** | 2e-4 |

### Training Data

The model was trained on:
- Sisi Lola personality dataset (custom curated)
- Nigerian conversational patterns
- Lagos cultural references
- Nigerian Pidgin expressions

## Evaluation

### Qualitative Assessment

The model demonstrates:
- Natural Nigerian English patterns
- Appropriate use of Pidgin phrases
- Warm, welcoming conversational tone
- Cultural awareness of Lagos/Nigerian context

### Limitations

- Limited training data may result in repetitive patterns
- May not capture all Nigerian dialects equally
- Performance varies with base model choice

## Bias, Risks, and Limitations

### Known Biases

- Trained primarily on Lagos-centric content
- May underrepresent other Nigerian regions/cultures
- English-dominant with limited Yoruba/Igbo/Hausa

### Recommendations

- Use with content moderation for public deployments
- Combine with retrieval systems for factual accuracy
- Test thoroughly before production deployment

## Model Card Contact

- **Email:** sisilolalive@gmail.com
- **GitHub:** [BAMG-Studio/sisi-lola-project](https://github.com/BAMG-Studio/sisi-lola-project)
- **HuggingFace:** [sisilolalive](https://huggingface.co/sisilolalive)

---

*Sisi Lola - Your friendly Lagos virtual host* 🇳🇬
