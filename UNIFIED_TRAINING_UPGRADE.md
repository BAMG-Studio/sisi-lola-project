# UNIFIED TRAINING PIPELINE UPGRADE

**Date:** December 2024  
**Status:** ✅ IMPLEMENTED

---

## Overview

Upgraded the Sisi Lola training infrastructure from GPT-2 to a production-grade unified pipeline featuring:

- **Mistral-7B** with QLoRA fine-tuning for the brain model
- **XTTS-v2** speaker embedding extraction for voice cloning
- **Personality training** with multi-language support
- **Automated 2-day retraining cycle** via GitHub Actions

---

## Architecture Changes

### Before
```
├── modal_training.yml (GPT-2, T4 GPU, daily)
├── personality_training.yml (Separate)
├── nigerian_training_pipeline.yml (Weekly)
└── personality_training_minimal.yml
```

### After
```
├── unified_training.yml (Mistral-7B + XTTS + Personality, A100, every 2 days)
└── [deprecated workflows moved to .deprecated extension]
```

---

## New Components Created

### 1. `ml_training/modal_unified_training.py`
**Purpose:** Unified Modal.com training pipeline

**Key Features:**
- **3-Stage Training:**
  1. Personality Model (DistilGPT2 base, enhanced for cultural context)
  2. Brain Model (Mistral-7B with QLoRA 4-bit quantization)
  3. Voice Model (XTTS-v2 speaker embedding extraction)

- **Mistral-7B Configuration:**
  ```python
  BASE_MODEL = "mistralai/Mistral-7B-v0.1"
  LORA_CONFIG = {
      "r": 32,
      "alpha": 64,
      "dropout": 0.05,
      "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", 
                         "gate_proj", "up_proj", "down_proj"]
  }
  ```

- **GPU Requirements:**
  - Personality: T4 (16GB VRAM)
  - Brain (Mistral): A100-40GB
  - Voice: T4 (16GB VRAM)

### 2. `.github/workflows/unified_training.yml`
**Purpose:** Automated 2-day training schedule

**Schedule:** `0 2 */2 * *` (Every 2 days at 2 AM UTC)

**Jobs:**
1. `check-data` - Verify sufficient new training data
2. `curate-data` - Run data curation pipeline
3. `modal-training` - Execute unified training on Modal.com
4. `validate-models` - Validate trained models
5. `update-production` - Update production model registry
6. `notify` - Send Slack/email notifications

### 3. `04_AUDIO_CORE/voice_routing/voice_backend_router.py`
**Purpose:** Intelligent TTS engine routing based on language tags

**Language Tag System:**
| Tag | Language | Primary Engine | Fallback |
|-----|----------|----------------|----------|
| `[EN]` | English | XTTS-v2 | EdgeTTS |
| `[NP]` | Pidgin | YarnGPT | XTTS |
| `[YO]` | Yoruba | VITS-Yoruba | EdgeTTS |
| `[IG]` | Igbo | YarnGPT | EdgeTTS |
| `[HA]` | Hausa | YarnGPT | EdgeTTS |

**Usage:**
```python
from voice_backend_router import VoiceRouter

router = VoiceRouter()
audio = router.synthesize(
    text="Hello! [NP] How you dey? [/NP] [YO] Ẹ kú àárọ̀! [/YO]",
    output_path="output.wav"
)
```

---

## Deprecated Workflows

The following workflows have been renamed to `.deprecated`:

| Old Name | Status |
|----------|--------|
| `modal_training.yml` | → `modal_training.yml.deprecated` |
| `personality_training.yml` | → `personality_training.yml.deprecated` |
| `personality_training_minimal.yml` | → `personality_training_minimal.yml.deprecated` |
| `nigerian_training_pipeline.yml` | → `nigerian_training_pipeline.yml.deprecated` |
| `ml_training.yml.disabled` | Already disabled |

---

## HuggingFace Hub Targets

| Model | Repository |
|-------|------------|
| Personality | `sisilolalive/sisi-lola-personality` |
| Brain (Mistral) | `sisilolalive/sisi-lola-brain-mistral` |
| Voice (XTTS) | `sisilolalive/sisi-lola-voice-xtts` |

---

## Required Environment Variables

For GitHub Actions:
```yaml
MODAL_TOKEN_ID: ${{ secrets.MODAL_TOKEN_ID }}
MODAL_TOKEN_SECRET: ${{ secrets.MODAL_TOKEN_SECRET }}
HF_TOKEN: ${{ secrets.HF_TOKEN }}
```

For Local Development:
```bash
export MODAL_TOKEN_ID="your_modal_token_id"
export MODAL_TOKEN_SECRET="your_modal_token_secret"
export HF_TOKEN="your_huggingface_token"
export ELEVENLABS_API_KEY="optional_for_premium_tts"
```

---

## Training Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    SISI LOLA CHAT SYSTEM                        │
│  (User Interactions with rating/safety fields)                   │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               chat_data_logger.py → SQLite DB                    │
│  ml_training/data/chat_training_data.db                          │
│  Fields: session_id, user_text, assistant_text, rating,          │
│          safety_flag, do_not_train, language_tags                │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               ml_training/scripts/curate_chat_data.py            │
│  - Filters: rating >= 4, safety_flag = false, do_not_train = 0   │
│  - Exports to training/personality_training.jsonl                │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               unified_training.yml (GitHub Actions)              │
│  - Runs every 2 days                                             │
│  - Triggers Modal.com training                                   │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               modal_unified_training.py (Modal.com)              │
│  Stage 1: Personality (DistilGPT2)                               │
│  Stage 2: Brain (Mistral-7B + QLoRA)                             │
│  Stage 3: Voice (XTTS-v2 embeddings)                             │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│               HuggingFace Hub                                    │
│  sisilolalive/sisi-lola-personality                               │
│  sisilolalive/sisi-lola-brain-mistral                             │
│  sisilolalive/sisi-lola-voice-xtts                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Manual Training Commands

### Run on Modal.com
```bash
# Deploy and run
modal run ml_training/modal_unified_training.py

# Run specific stage
modal run ml_training/modal_unified_training.py::train_personality
modal run ml_training/modal_unified_training.py::train_brain
modal run ml_training/modal_unified_training.py::train_voice
```

### Test Voice Router
```bash
# Show status
python 04_AUDIO_CORE/voice_routing/voice_backend_router.py --status

# Synthesize text
python 04_AUDIO_CORE/voice_routing/voice_backend_router.py \
    --text "Hello! [NP] How you dey? [/NP]" \
    --output test.wav
```

---

## Next Steps

1. **Configure Modal.com secrets** in GitHub repository settings
2. **Create HuggingFace repositories** if they don't exist
3. **Add speaker reference WAV** for XTTS voice cloning
4. **Test the workflow** with a manual trigger
5. **Monitor first automated run** (scheduled every 2 days)

---

## Files Changed

| File | Action |
|------|--------|
| `ml_training/modal_unified_training.py` | Created |
| `.github/workflows/unified_training.yml` | Created |
| `04_AUDIO_CORE/voice_routing/voice_backend_router.py` | Created |
| `modal_training.yml` | Deprecated |
| `personality_training.yml` | Deprecated |
| `personality_training_minimal.yml` | Deprecated |
| `nigerian_training_pipeline.yml` | Deprecated |
