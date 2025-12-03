# Sisi Lola Nigerian Training System

## Overview

Complete training pipeline for Sisi Lola's Nigerian/African-focused brain (LLM) and voice (TTS) using:

- **Brain**: N-ATLaS-LLM (8B) + AfriBERTa + Aya-23
- **Voice**: XTTS-v2 with Nigerian accent fine-tuning
- **Languages**: Yoruba, Nigerian Pidgin, Nigerian English, Hausa, Igbo

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SISI LOLA SYSTEM                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐            │
│  │   N-ATLaS    │         │   XTTS-v2    │            │
│  │   (Brain)    │◄───────►│   (Voice)    │            │
│  │              │         │              │            │
│  │ • Yoruba     │         │ • Lagos      │            │
│  │ • Pidgin     │         │   accent     │            │
│  │ • Naija EN   │         │ • Multi-lang │            │
│  └──────────────┘         └──────────────┘            │
│         │                        │                     │
│         ▼                        ▼                     │
│  ┌──────────────────────────────────────┐             │
│  │      LoRA Adapters (Retrainable)     │             │
│  └──────────────────────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd ml_training
pip install -r requirements_nigerian.txt
```

### 2. Set Environment Variables

```bash
export HUGGINGFACE_TOKEN="your_token_here"
```

Or add to `.env`:
```
HUGGINGFACE_TOKEN=hf_xxxxx
```

### 3. Prepare Training Data

**Voice Samples** (minimum 5 required):
- Place `.wav` files in `04_AUDIO_CORE/voice_samples/`
- Create matching `.txt` transcripts
- Recommended: 10-30 samples, 5-30 seconds each

**Personality Data**:
- Edit `ml_training/datasets/sisi_lola_personality.txt`
- Add Nigerian slang, expressions, cultural references

**Conversation Data**:
- Add to `api_customization/datasets/sisi_lola_conversations.json`

### 4. Run Training

**Full Training** (Brain + Voice):
```bash
python ml_training/scripts/unified_training_orchestrator.py --mode full
```

**Brain Only**:
```bash
python ml_training/scripts/train_nigerian_brain.py
```

**Voice Only**:
```bash
python ml_training/scripts/train_nigerian_voice.py
```

## Training Modes

### Brain Training (N-ATLaS)

- **Model**: NCAIR1/N-ATLaS-8B (Llama-3 based)
- **Method**: LoRA fine-tuning (4-bit quantization)
- **Data**: NaijaSenti + Sisi Lola personality + conversations
- **Output**: `ml_training/checkpoints/natlas_lora/`
- **Time**: ~2-4 hours on GPU

**System Prompt**:
```
You are Sisi Lola, a hyper-realistic Nigerian virtual host from Lagos.
You speak primarily in fluent Yoruba and 'Yorunglish' (code-mixing Yoruba 
and Nigerian English), and you also understand and speak Nigerian Pidgin 
and other Nigerian languages. Always sound like a witty, playful Lagos 
babe in her late 20s: street-smart, funny, and dramatic, but never rude.
```

### Voice Training (XTTS-v2)

- **Model**: Coqui XTTS-v2 (multilingual TTS)
- **Method**: Fine-tuning on Sisi Lola voice samples
- **Accent**: Lagos Nigerian (Yoruba-influenced English)
- **Output**: `ml_training/checkpoints/xtts_sisi_lola/`
- **Time**: ~4-8 hours on GPU

**Voice Style**:
- High-energy Lagos Yoruba babe
- Fast, expressive, playful delivery
- Frequent laughter and dramatic emphasis
- Natural Lagos conversation pacing

## Configuration

Edit `ml_training/configs/nigerian_models_config.yaml`:

```yaml
brain_models:
  primary:
    name: "N-ATLaS-LLM"
    model_id: "NCAIR1/N-ATLaS-8B"
    languages: ["yoruba", "pidgin", "nigerian_english"]

voice_models:
  primary:
    name: "XTTS-v2"
    model_id: "coqui/XTTS-v2"
    voice_reference: "04_AUDIO_CORE/voice_samples/"

training:
  brain:
    adapter_type: "LoRA"
    rank: 16
    alpha: 32
  
  voice:
    fine_tune_steps: 10000
    batch_size: 8
    learning_rate: 1e-5
```

## Inference

### Text Generation

```python
from ml_training.scripts.inference_nigerian import SisiLolaInference

sisi = SisiLolaInference()
response = sisi.generate_text("Bawo ni? Tell me about Lagos")
print(response)
```

### Voice Generation

```python
sisi = SisiLolaInference()
audio = sisi.generate_speech(
    "Welcome to my channel, omo!",
    output_path="output.wav",
    language="yo"
)
```

### Complete Chat

```python
sisi = SisiLolaInference()
result = sisi.chat(
    "Wetin be your favorite food?",
    generate_audio=True,
    language="yo"
)
# Returns: {"text": "...", "audio": "path/to/audio.wav"}
```

## GitHub Actions Workflow

Automated training pipeline runs:

- **On Push**: When datasets or voice samples change
- **Scheduled**: Weekly on Sundays at 2 AM UTC
- **Manual**: Via workflow_dispatch

**Trigger manually**:
```bash
gh workflow run nigerian_training_pipeline.yml \
  -f training_mode=full \
  -f skip_existing=true
```

## Model Outputs

### Brain (LoRA Adapter)
```
ml_training/checkpoints/natlas_lora/
├── adapter_config.json
├── adapter_model.bin
├── metadata.json
└── tokenizer files
```

### Voice (XTTS Checkpoint)
```
ml_training/checkpoints/xtts_sisi_lola/
├── model.pth
├── config.json
├── metadata.json
└── speaker_embeddings/
```

### Deployment Config
```
ml_training/outputs/production_config.json
```

## Datasets Used

### NaijaSenti
- **Source**: HausaNLP/NaijaSenti
- **Size**: ~120k tweets
- **Languages**: Hausa, Igbo, Nigerian Pidgin, Yoruba
- **Use**: Sentiment analysis, cultural context

### Yoruba Speech Corpus
- **Sources**: OpenSLR, Lagos-NWU
- **Dialects**: Lagos, Ibadan, Oyo
- **Use**: Voice training, accent validation

### Custom Datasets
- Sisi Lola personality traits
- Conversation examples
- Nigerian slang dictionary

## Retraining

### When to Retrain

- New voice samples added (>10 new samples)
- Personality updates needed
- Language coverage expansion
- Performance degradation detected

### Incremental Training

```bash
# Train only on new data
python ml_training/scripts/unified_training_orchestrator.py \
  --mode full \
  --skip-existing
```

### Full Retraining

```bash
# Retrain from scratch
rm -rf ml_training/checkpoints/*
python ml_training/scripts/unified_training_orchestrator.py --mode full
```

## Monitoring

Training logs saved to:
```
ml_training/logs/training_report_YYYYMMDD_HHMMSS.json
```

Includes:
- Training events timeline
- Model configurations
- Performance metrics
- Deployment status

## Troubleshooting

### GPU Memory Issues
- Reduce batch size in config
- Use gradient checkpointing
- Enable CPU offloading

### Voice Quality Issues
- Add more diverse voice samples
- Increase training steps
- Validate sample quality (22050 Hz, clear audio)

### Language Mixing Problems
- Add more code-switching examples
- Adjust system prompt
- Fine-tune language detection

## Next Steps

1. ✅ Train initial models
2. ✅ Validate Nigerian accent quality
3. ⏳ Integrate with production API
4. ⏳ Deploy to HuggingFace Hub
5. ⏳ Set up continuous retraining
6. ⏳ Expand to Swahili, Amharic

## Resources

- [N-ATLaS Paper](https://arxiv.org/abs/2024.natlas)
- [XTTS-v2 Docs](https://docs.coqui.ai/en/latest/models/xtts.html)
- [NaijaSenti Dataset](https://huggingface.co/datasets/HausaNLP/NaijaSenti)
- [AfriBERTa](https://github.com/castorini/afriberta)

## Support

For issues or questions:
- Check logs in `ml_training/logs/`
- Review training reports
- Validate prerequisites with orchestrator

---

**Status**: Ready for training
**Version**: 1.0.0
**Last Updated**: 2024
