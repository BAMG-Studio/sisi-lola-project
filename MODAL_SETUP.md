# Modal.com Cloud GPU Training Setup

## Overview

Sisi Lola now uses Modal.com for cloud GPU training. This replaces GitHub Codespaces GPU (deprecated August 2025) and eliminates 6+ hour CPU training times.

### Key Benefits
- **T4 GPU**: 16GB VRAM, trains in ~5 seconds vs 6+ hours on CPU
- **$30 Free Credits**: ~60 training runs included
- **Cost Effective**: ~$0.50/run after free tier
- **Auto Push**: Trained models push directly to HuggingFace Hub

## Quick Start

### Option 1: Run from Windows (Batch File)
```batch
RUN_MODAL_TRAINING.bat
```

### Option 2: Run from Terminal
```bash
# Activate training environment
.venv_training\Scripts\activate

# Run brain training only (~5 min)
modal run ml_training/modal_train.py

# Run full pipeline (brain + voice) (~10 min)
modal run ml_training/modal_train.py --full-pipeline
```

### Option 3: Trigger from GitHub Actions
Go to: https://github.com/BAMG-Studio/sisi-lola-project/actions/workflows/modal_training.yml

Click "Run workflow" → Select options → Run

## Local Setup (Already Done)

```bash
# Create Python 3.10 environment
python -m venv .venv_training

# Activate
.venv_training\Scripts\activate

# Install Modal
pip install modal

# Authenticate (opens browser)
modal token new
```

## GitHub Actions Setup

Add these secrets to your repository:
1. Go to: https://github.com/BAMG-Studio/sisi-lola-project/settings/secrets/actions
2. Add:
   - `MODAL_TOKEN_ID`: `ak-Ms5z3j16TceQuZqb0vkvbY`
   - `MODAL_TOKEN_SECRET`: `as-bv17CDOXQngRi1qucH2Vy0`

The workflow runs automatically on:
- Push to `ml_training/` folder
- Weekly schedule (Sundays at 2 AM UTC)
- Manual trigger from Actions tab

## Files Created

| File | Purpose |
|------|---------|
| `ml_training/modal_train.py` | Modal training script with GPU functions |
| `.github/workflows/modal_training.yml` | GitHub Actions CI workflow |
| `RUN_MODAL_TRAINING.bat` | Windows batch file for easy training |

## Modal Dashboard

View runs and usage at: https://modal.com/apps/bamg-studio/main

## Trained Models

- Brain: https://huggingface.co/sisilolalive/sisi-lola-brain
- Voice: https://huggingface.co/sisilolalive/sisi-lola-voice

## Cost Tracking

| GPU | Cost/Hour | Typical Run | Est. Cost |
|-----|-----------|-------------|-----------|
| T4 (default) | $0.59 | 5 min | ~$0.05 |
| A10G | $1.10 | 3 min | ~$0.06 |
| A100 | $3.13 | 1 min | ~$0.05 |

With $30 free credits, you get approximately 60+ training runs.

## Training Output

Example successful run:
```
============================================================
🧠 SISI LOLA BRAIN TRAINING ON MODAL
============================================================
✅ GPU: Tesla T4 (15.6GB)
✅ Logged in to HuggingFace
📦 Loading base model: gpt2
🎯 LoRA target modules: ['c_attn', 'c_proj']
📊 Trainable parameters: 1,622,016

🚀 Starting training...
{'loss': 9.33, 'train_runtime': 3.76s, 'epoch': 3.0}

💾 Saving model to /models/natlas_lora
📤 Pushing to HuggingFace Hub: sisilolalive/sisi-lola-brain
✅ Pushed to https://huggingface.co/sisilolalive/sisi-lola-brain
```

## Troubleshooting

### "Modal not authenticated"
```bash
modal token new
```

### "Image build failed"
Modal caches images. Retry the run - second attempt is faster.

### "GPU quota exceeded"
Wait for free credits to reset or upgrade to paid tier.
