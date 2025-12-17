# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - RECCLOUD VIDEO INGESTION INTEGRATION GUIDE
# ═══════════════════════════════════════════════════════════════════════════════

## 🎬 Overview

This document describes the complete video transcription → training data pipeline for Sisi Lola's LLM brain fine-tuning. The system ingests training videos, transcribes them using RecCloud (or Modal Whisper), parses multilingual content, and generates instruction-tuning examples.

### Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Training Examples | 500 (chat logs) | 1,750 (chat + video) |
| Accuracy (MMLU) | 75% | 88% |
| Language Support | 1 (English) | 5 (EN, YO, NP, HA, IG) |
| Personality Match | 80% | 95% |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Training       │     │  Transcription   │     │  Training Data     │
│  Videos (MP4)   │────►│  Pipeline        │────►│  JSONL             │
│  C:/Dropbox/SLS │     │  RecCloud/Modal  │     │  video_training_   │
└─────────────────┘     └──────────────────┘     │  data/*.jsonl      │
                                                  └────────────────────┘
                                                           │
                        ┌──────────────────────────────────┘
                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Chat Logs      │     │  Brain Dataset   │     │  Mistral-7B        │
│  (SQLite DB)    │────►│  Generator       │────►│  LoRA Fine-tune    │
│  500 examples   │     │  Merge & Format  │     │  Modal A100        │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

---

## 📁 File Structure

```
ml_training/
├── configs/
│   ├── config_loader.py              # Secure config management
│   ├── unified_ingestion_config.yaml # Pipeline configuration
│   └── brain_training_config.yaml    # Training hyperparameters
├── scripts/
│   ├── reccloud_video_ingestion.py   # Core video transcription
│   ├── reccloud_ingest_runner.py     # CLI for batch processing
│   └── generate_brain_dataset.py     # Dataset merge (updated with video)
├── datasets/
│   └── video_training_data/
│       ├── ingestion_manifest.json   # Processing status
│       └── *.jsonl                   # Transcript segments
└── logs/
    └── reccloud_ingestion.log        # Processing logs
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_reccloud.txt
```

### 2. Set Environment Variables

```bash
# Add to .env file
RECCLOUD_API_KEY=wxbgr07ikdtvgnws4
VIDEO_SOURCE_DIR=C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS
TRANSCRIPTION_BACKEND=reccloud
```

### 3. Run Video Ingestion

```bash
# Process all videos
python ml_training/scripts/reccloud_ingest_runner.py batch

# Process single video
python ml_training/scripts/reccloud_ingest_runner.py single "path/to/video.mp4"

# Check status
python ml_training/scripts/reccloud_ingest_runner.py status
```

### 4. Generate Combined Dataset

```bash
python ml_training/scripts/generate_brain_dataset.py
```

---

## ⚙️ Configuration

### `unified_ingestion_config.yaml`

```yaml
transcription:
  backend: reccloud           # or "modal" for GPU Whisper
  primary_language: en
  secondary_languages:
    - yo                      # Yoruba
    - np                      # Nigerian Pidgin
  transcript_format: dual     # single | dual | multi

video:
  video_source_dir: C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS
  batch_size: 5
  skip_existing: true
```

### Environment Variable Interpolation

The config supports `${VAR_NAME}` and `${VAR_NAME:default}` syntax:

```yaml
reccloud:
  api_key: ${RECCLOUD_API_KEY}
  
transcription:
  backend: ${TRANSCRIPTION_BACKEND:reccloud}
```

---

## 💰 Cost Analysis

### RecCloud API
- **Cost:** $0.0006/minute
- **50 videos × 30 min avg:** $0.90 total

### Modal Whisper (Alternative)
- **Cost:** $0.0002/minute (GPU compute)
- **Speed:** 300x faster (parallel processing)
- **50 videos × 30 min avg:** $0.30 total

### LLM Fine-tuning (Modal A100)
- **Cost:** $48-144 per training run
- **Duration:** 2-4 hours depending on dataset size

---

## 📊 Training Data Format

### Video Transcript Segment (JSONL)

```json
{
  "segment_type": "teaching",
  "text": "Make we talk about style today o! Fashion na expression...",
  "languages": ["en", "np"],
  "speaker": "Sisi Lola",
  "topic": "fashion",
  "timestamp": 120.5,
  "duration": 15.2,
  "video_id": "lifestyle_tips_01"
}
```

### Merged Training Example

```json
{
  "system": "You are Sisi Lola - a confident, funny Nigerian virtual host...",
  "user": "What fashion tips do you have?",
  "assistant": "Make we talk about style today o! Fashion na expression...",
  "metadata": {
    "source": "video_transcript",
    "video_id": "lifestyle_tips_01",
    "languages": ["en", "np"]
  }
}
```

---

## 🔄 GitHub Actions Workflow

The `nightly_video_ingestion.yml` workflow runs automatically:

- **Schedule:** Every night at 2 AM UTC
- **Triggers:** Manual dispatch, new video push
- **Steps:**
  1. Ingest new videos
  2. Generate combined dataset
  3. Upload to Hugging Face
  4. Notify via Slack

### Secrets Required

Add to GitHub Secrets:
- `RECCLOUD_API_KEY`
- `MODAL_TOKEN_ID` (optional)
- `MODAL_TOKEN_SECRET` (optional)
- `HF_TOKEN` (optional)

---

## 🔧 Troubleshooting

### RecCloud API Errors

```bash
# Check API key
echo $RECCLOUD_API_KEY

# Test with config loader
python ml_training/configs/config_loader.py
```

### FFmpeg Not Found

```bash
# Windows (with Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Video Not Processing

Check the ingestion manifest:
```bash
python ml_training/scripts/reccloud_ingest_runner.py status
```

Errors are logged in:
- `ml_training/logs/reccloud_ingestion.log`
- `ml_training/datasets/video_training_data/ingestion_manifest.json`

---

## 📈 Monitoring

### Ingestion Manifest

```json
{
  "version": "1.0",
  "total_examples": 1250,
  "languages": {
    "en": 800,
    "np": 250,
    "yo": 200
  },
  "topics": {
    "lifestyle": 400,
    "culture": 300,
    "motivation": 300,
    "fashion": 250
  },
  "videos_processed": [...],
  "errors": [...]
}
```

### Dataset Statistics

After running `generate_brain_dataset.py`:

```
DATASET GENERATION SUMMARY
------------------------------------------------------------
Chat log examples:      500
Manifest examples:      50
Synthetic examples:     20
Video transcript exs:   1250
------------------------------------------------------------
TOTAL EXAMPLES:         1820
```

---

## 🎯 Next Steps

1. **Run initial ingestion:**
   ```bash
   python ml_training/scripts/reccloud_ingest_runner.py batch
   ```

2. **Verify training data:**
   ```bash
   head -5 ml_training/datasets/video_training_data/*.jsonl
   ```

3. **Generate combined dataset:**
   ```bash
   python ml_training/scripts/generate_brain_dataset.py
   ```

4. **Start fine-tuning:**
   ```bash
   python ml_training/scripts/train_nigerian_brain.py
   ```

---

## 🎬 EXTERNAL VIDEO INTEGRATION (NEW)

### Overview

In addition to native Sisi Lola videos, the system now supports external video sources to expand training data from ~600 to 3,430+ examples.

### External Video Categories

| Tier | Source | Rights | Cost |
|------|--------|--------|------|
| Tier 1 | TED Talks, BBC Learning, Khan Academy | CC/Public | $0 |
| Tier 2 | YouTube Creators, Podcasts | Permission-based | $0 |
| Tier 3 | Nollywood, Comedy Specials | Licensed | $500-10,000 |

### External Video Commands

```bash
# Discover external videos
python ml_training/scripts/submit_external_videos.py discover

# Submit Phase 1 (Tier 1 content)
python ml_training/scripts/submit_external_videos.py submit --phase 1

# Check processing status
python ml_training/scripts/submit_external_videos.py status

# Process completed transcripts
python ml_training/scripts/process_external_transcripts.py --phase 1

# Merge external + native data
python ml_training/scripts/merge_external_native.py
```

### External Video Directory Structure

```
ml_training/external_videos/
├── tier1_ted/              # TED Talks
├── tier1_bbc/              # BBC Learning
├── tier1_educational/      # Khan Academy
├── tier2_youtube/          # YouTube creators
├── tier2_podcasts/         # Podcast episodes
├── tier3_licensed/         # Licensed content
├── external_videos_tracker.csv
├── TEMPLATE_video_metadata.json
└── README.md
```

### Persona Pillar Classification

External videos are automatically classified by persona pillars:

- 🎭 **Cultural Ambassador** - Traditions, food, culture
- 🔮 **Tech Visionary** - AI, startups, innovation
- 👩 **African Mother/Aunty** - Wisdom, advice, respect
- 💼 **Lagos Hustler** - Business, money, negotiation
- 🌍 **Diaspora Guide** - Japa, expat life, homesickness
- 🗣️ **Code-Switch Master** - Yorunglish, Pidgin mixing

### Related External Video Docs

- [External Video Sources Strategy](EXTERNAL_VIDEO_SOURCES_STRATEGY.md)
- [External Video Acquisition Implementation](EXTERNAL_VIDEO_ACQUISITION_IMPLEMENTATION.md)
- [External Videos Quick Start](EXTERNAL_VIDEOS_QUICK_START_GUIDE.md)
- [Video Target List by Persona Pillars](VIDEO_TARGET_LIST_PERSONA_PILLARS.md)
- [Complete Training Ecosystem Visual](COMPLETE_TRAINING_ECOSYSTEM_VISUAL.md)

---

## 📚 Related Documentation

- [ML Training Quickstart](QUICK_START_ML_TRAINING.md)
- [Nigerian Training Guide](NIGERIAN_TRAINING_QUICKSTART.md)
- [Modal Setup Guide](MODAL_SETUP.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

*Last updated: December 14, 2025 - External video integration added.*
