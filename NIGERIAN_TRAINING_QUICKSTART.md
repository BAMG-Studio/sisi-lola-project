# 🚀 Sisi Lola Nigerian Training - Quick Start Guide

## What This Does

Trains Sisi Lola's **brain** (Nigerian-focused LLM) and **voice** (Nigerian accent TTS) using:

- **N-ATLaS-LLM**: Nigeria's official open-source LLM for Yoruba, Pidgin, Hausa, Igbo
- **XTTS-v2**: Cross-lingual voice cloning with Nigerian accent
- **NaijaSenti**: 120k Nigerian social media samples for cultural context
- **LoRA Adapters**: Efficient fine-tuning for easy retraining

## Prerequisites

✅ **Required**:
- Python 3.10+
- HuggingFace account & token
- 5+ voice samples in `04_AUDIO_CORE/voice_samples/`
- 8GB+ GPU (recommended) or CPU (slower)

✅ **Already Configured**:
- HuggingFace token in `.env`
- Voice samples exist
- Project structure ready

## One-Command Training

### Windows
```cmd
train_nigerian_models.bat
```

### Linux/Mac
```bash
chmod +x train_nigerian_models.sh
./train_nigerian_models.sh
```

That's it! The script will:
1. ✅ Install dependencies
2. ✅ Download N-ATLaS & XTTS models
3. ✅ Validate voice samples
4. ✅ Train brain (2-4 hours)
5. ✅ Train voice (4-8 hours)
6. ✅ Generate deployment config

## Manual Training

### Step 1: Setup
```bash
cd ml_training
pip install -r requirements_nigerian.txt
python scripts/setup_nigerian_models.py
```

### Step 2: Train
```bash
# Full training (brain + voice)
python scripts/unified_training_orchestrator.py --mode full

# Brain only
python scripts/train_nigerian_brain.py

# Voice only
python scripts/train_nigerian_voice.py
```

### Step 3: Test
```python
from ml_training.scripts.inference_nigerian import SisiLolaInference

sisi = SisiLolaInference()
result = sisi.chat("Bawo ni? Tell me about Lagos", generate_audio=True)
print(result['text'])
# Audio saved to result['audio']
```

## What Gets Trained

### 🧠 Brain (N-ATLaS + LoRA)
- **Input**: NaijaSenti + personality + conversations
- **Output**: `ml_training/checkpoints/natlas_lora/`
- **Size**: ~500MB (adapter only)
- **Languages**: Yoruba, Pidgin, Nigerian English, Hausa, Igbo
- **Personality**: Witty Lagos babe, street-smart, playful

### 🎤 Voice (XTTS-v2)
- **Input**: Your voice samples in `04_AUDIO_CORE/voice_samples/`
- **Output**: `ml_training/checkpoints/xtts_sisi_lola/`
- **Size**: ~1.5GB
- **Accent**: Lagos Nigerian (Yoruba-influenced)
- **Style**: High-energy, expressive, playful

## Configuration

Edit `ml_training/configs/nigerian_models_config.yaml`:

```yaml
# Adjust training parameters
training:
  brain:
    rank: 16          # LoRA rank (higher = more capacity)
    alpha: 32         # LoRA alpha
  
  voice:
    fine_tune_steps: 10000  # Training steps
    batch_size: 8           # Batch size
    learning_rate: 1e-5     # Learning rate
```

## Outputs

After training completes:

```
ml_training/
├── checkpoints/
│   ├── natlas_lora/          # Brain adapter
│   │   ├── adapter_model.bin
│   │   ├── adapter_config.json
│   │   └── metadata.json
│   └── xtts_sisi_lola/       # Voice model
│       ├── model.pth
│       ├── config.json
│       └── metadata.json
├── outputs/
│   └── production_config.json  # Deployment config
└── logs/
    └── training_report_*.json  # Training logs
```

## GitHub Actions (Automated)

The workflow `.github/workflows/nigerian_training_pipeline.yml` automatically:

- ✅ Trains on dataset changes
- ✅ Weekly retraining (Sundays 2 AM UTC)
- ✅ Uploads to HuggingFace Hub
- ✅ Generates reports

**Trigger manually**:
```bash
gh workflow run nigerian_training_pipeline.yml -f training_mode=full
```

## Retraining

### When to Retrain
- Added 10+ new voice samples
- Updated personality/conversations
- Performance degradation
- Expanding to new languages

### Quick Retrain
```bash
# Only train on new data
python scripts/unified_training_orchestrator.py --mode full --skip-existing
```

### Full Retrain
```bash
# Start from scratch
rm -rf ml_training/checkpoints/*
python scripts/unified_training_orchestrator.py --mode full
```

## Testing Inference

### Text Only
```python
from ml_training.scripts.inference_nigerian import SisiLolaInference

sisi = SisiLolaInference()
response = sisi.generate_text("Wetin be your favorite food?")
print(response)
# Output: "Omo, na jollof rice be my number one! Nigerian jollof o, not that Ghanaian one..."
```

### Voice Only
```python
sisi = SisiLolaInference()
audio = sisi.generate_speech(
    "Welcome to my channel, make we gist!",
    output_path="welcome.wav",
    language="yo"
)
```

### Complete Chat
```python
sisi = SisiLolaInference()
result = sisi.chat(
    "Explain blockchain in Yorunglish",
    generate_audio=True,
    language="yo"
)
print(result['text'])    # Text response
print(result['audio'])   # Audio file path
```

## Troubleshooting

### GPU Memory Error
```yaml
# Reduce batch size in config
training:
  brain:
    batch_size: 2  # Lower from 4
  voice:
    batch_size: 4  # Lower from 8
```

### Voice Quality Issues
1. Add more diverse samples (different emotions, speeds)
2. Ensure 22050 Hz sample rate
3. Remove background noise
4. Increase training steps

### Model Not Found
```bash
# Re-run setup
python ml_training/scripts/setup_nigerian_models.py
```

## Next Steps

1. ✅ Train models (this guide)
2. ⏳ Integrate with API (`sisi_lola_api/`)
3. ⏳ Deploy to production
4. ⏳ Add Swahili, Amharic support
5. ⏳ Continuous learning from user interactions

## Resources

- **N-ATLaS**: [NCAIR1/N-ATLaS-8B](https://huggingface.co/NCAIR1/N-ATLaS-8B)
- **XTTS-v2**: [Coqui TTS Docs](https://docs.coqui.ai/)
- **NaijaSenti**: [HausaNLP/NaijaSenti](https://huggingface.co/datasets/HausaNLP/NaijaSenti)
- **Full Docs**: `ml_training/README_NIGERIAN_TRAINING.md`

## Support

Check logs:
```bash
# Training logs
cat ml_training/logs/training_report_*.json

# Model metadata
cat ml_training/checkpoints/natlas_lora/metadata.json
cat ml_training/checkpoints/xtts_sisi_lola/metadata.json
```

---

**Ready to train?** Run `train_nigerian_models.bat` (Windows) or `./train_nigerian_models.sh` (Unix)

**Estimated Time**: 6-12 hours total (can run overnight)

**GPU Recommended**: Yes (10x faster than CPU)
