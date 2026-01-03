# 🎓 Sisi Lola Training Data Infrastructure v3.0

## Overview

This document describes the comprehensive training data infrastructure for the Sisi Lola AI project, including:

- **50+ Nigerian Data Sources** - Voice, video, and cultural content
- **Nightly Automated Ingestion** - From YouTube, RSS, HuggingFace
- **Quality Scoring System** - Gold/Silver/Bronze tiers
- **DVC Data Versioning** - Track dataset changes over time
- **Docker-based Training** - Reproducible environments
- **Metrics Dashboard** - Real-time monitoring

---

## 🗂️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SISI LOLA TRAINING INFRASTRUCTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    📥 DATA INGESTION LAYER                          │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  YouTube    │  │    RSS      │  │ HuggingFace │  │   Voice   │  │   │
│  │  │  Channels   │  │   Feeds     │  │  Datasets   │  │  Datasets │  │   │
│  │  │  (10+)      │  │   (5+)      │  │   (20+)     │  │   (20+)   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  │            │              │              │               │          │   │
│  │            └──────────────┴──────────────┴───────────────┘          │   │
│  │                                    │                                │   │
│  │                         ┌──────────▼──────────┐                     │   │
│  │                         │  nightly_ingestion  │                     │   │
│  │                         │       .py           │                     │   │
│  │                         └──────────┬──────────┘                     │   │
│  └─────────────────────────────────────┼───────────────────────────────┘   │
│                                        │                                    │
│  ┌─────────────────────────────────────┼───────────────────────────────┐   │
│  │                    📊 QUALITY & VERSIONING                          │   │
│  │                                     │                               │   │
│  │  ┌──────────────────┐    ┌─────────▼─────────┐    ┌──────────────┐ │   │
│  │  │  Quality Scorer  │───▶│   SQLite DB       │───▶│  DVC Track   │ │   │
│  │  │  (0-100 score)   │    │   ingestion.db    │    │  + Version   │ │   │
│  │  └──────────────────┘    └───────────────────┘    └──────────────┘ │   │
│  │           │                                              │          │   │
│  │  ┌────────┴────────┐                         ┌───────────▼────────┐│   │
│  │  │ Gold  │Silver│Bronze│                     │   S3 / HuggingFace ││   │
│  │  │ (80+) │(60+) │(<60) │                     │      Remote        ││   │
│  │  └──────────────────┘                        └────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🐳 DOCKER TRAINING LAYER                          │   │
│  │                                                                      │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                   docker-compose.training.yml                  │  │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ ┌───────────┐  │  │   │
│  │  │  │Training │ │Ingestion│ │Dashboard│ │ MinIO │ │  MLflow   │  │  │   │
│  │  │  │  GPU    │ │ Service │ │Streamlit│ │  S3   │ │ Tracking  │  │  │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └───────┘ └───────────┘  │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
sisi-lola-project/
├── ml_training/
│   ├── configs/
│   │   └── nigerian_data_sources.yaml    # 50+ Nigerian sources registry
│   ├── scripts/
│   │   ├── nightly_ingestion.py          # Main ingestion orchestrator
│   │   └── metrics_dashboard.py          # Streamlit dashboard
│   └── datasets/
│       └── ingested/                     # Downloaded/processed data
├── .github/workflows/
│   ├── nightly_video_ingestion.yml       # Nightly ingestion workflow
│   └── unified_training.yml              # Training pipeline
├── Dockerfile.training                    # Multi-stage Docker build
├── docker-compose.training.yml            # Training infrastructure
└── .dvc/
    └── config                            # DVC remotes configuration
```

---

## 🌍 Nigerian Data Sources (50+)

### Voice Datasets (Primary)
| Dataset | Languages | Description |
|---------|-----------|-------------|
| MMS-TTS | Yoruba, Hausa, Igbo, Pidgin | Meta's Massively Multilingual Speech |
| FLEURS | Yoruba, Hausa, Igbo | Google's 102-language benchmark |
| Common Voice | Yoruba, Hausa, Igbo | Mozilla crowdsourced voice |
| OpenSLR | Yoruba | Nigerian language corpus |

### Voice Datasets (Secondary)
| Dataset | Languages | Description |
|---------|-----------|-------------|
| AfriVoices | Multiple | Pan-African voice corpus |
| Yoruba Speech Corpus | Yoruba | Academic recordings |
| VOA Hausa | Hausa | Voice of America news |
| BBC Pidgin | Pidgin | BBC World Service |
| Naija TTS | Pidgin | Nigerian Pidgin synthesis |

### YouTube Channels (Video + Audio)
| Channel | Content Type | Focus |
|---------|--------------|-------|
| Tunde Ednut | Entertainment | Nigerian pop culture |
| Mark Angel Comedy | Comedy | Nigerian skits |
| Broda Shaggi | Comedy | Pidgin comedy |
| Taaooma | Comedy | Family comedy |
| Emmanuella | Comedy | Kids comedy |
| YBNL Nation | Music | Nigerian music |
| Mavin Records | Music | Afrobeats |
| Pulse Nigeria | News | Current affairs |
| Channels TV | News | Nigerian news |

### RSS Feeds (Text)
| Source | Content | Language |
|--------|---------|----------|
| BBC Pidgin | News | Pidgin |
| VOA Hausa | News | Hausa |
| Punch Nigeria | News | English/Pidgin |
| Premium Times | News | English |

---

## 🚀 Quick Start

### 1. Run Ingestion Locally

```bash
cd ml_training/scripts

# Ingest from all sources (max 100 items each)
python nightly_ingestion.py --sources all --max-items 100 --stats

# Ingest only voice datasets
python nightly_ingestion.py --sources huggingface --max-items 50

# Initialize DVC and version data
python nightly_ingestion.py --dvc-init --dvc-version
```

### 2. Run with Docker

```bash
# Build training image
docker build -f Dockerfile.training --target training -t sisi-lola-training .

# Run ingestion service
docker-compose -f docker-compose.training.yml up ingestion

# Start full training infrastructure
docker-compose -f docker-compose.training.yml up -d
```

### 3. Access Dashboard

```bash
# Local
streamlit run ml_training/scripts/metrics_dashboard.py

# Docker
docker-compose -f docker-compose.training.yml up dashboard
# Open http://localhost:8501
```

### 4. Manual GitHub Actions Trigger

1. Go to **Actions** → **Nightly Data Ingestion**
2. Click **Run workflow**
3. Select options:
   - Sources: `all`, `youtube`, `rss`, `huggingface`, `voice`
   - Max items: `100` (default)
   - Min quality: `60` (0-100 scale)
   - Enable DVC: `true`

---

## 📊 Quality Scoring System

Each ingested item is scored 0-100 and classified into tiers:

| Tier | Score | Priority | Description |
|------|-------|----------|-------------|
| 🥇 Gold | 80-100 | Highest | Premium quality, use for fine-tuning |
| 🥈 Silver | 60-79 | Medium | Good quality, use for pre-training |
| 🥉 Bronze | 0-59 | Low | May need filtering or augmentation |

### Scoring Criteria

**Audio Quality:**
- Duration (5-30 min optimal)
- Sample rate (16kHz+)
- Clear speech (no background noise)
- Nigerian accent presence

**Video Quality:**
- Resolution (720p+)
- Has audio track
- Nigerian content
- Cultural relevance

**Text Quality:**
- Word count (100-5000 optimal)
- Language detection (Nigerian languages)
- Encoding (UTF-8)

---

## 🔄 DVC Data Versioning

### Configure Remotes

```bash
# S3 Remote (primary)
dvc remote add -d s3_remote s3://sisi-lola-datasets/training
dvc remote modify s3_remote region us-east-1

# HuggingFace Remote (secondary)
dvc remote add hf_remote hf://SisiLolaAI/training-data

# Local Remote (development)
dvc remote add local_remote /tmp/dvc-storage
```

### Track Data

```bash
# Add data to tracking
dvc add ml_training/datasets/ingested

# Push to remote
dvc push

# Pull data
dvc pull

# View history
dvc diff HEAD~1
```

---

## 🐳 Docker Services

### Training Service (GPU)
```bash
docker-compose -f docker-compose.training.yml up training
```
- NVIDIA GPU support
- Full ML stack (PyTorch, transformers, TTS)
- Mounts: datasets, models, configs

### Ingestion Service
```bash
docker-compose -f docker-compose.training.yml up ingestion
```
- Runs nightly ingestion
- Auto-restarts on failure
- Logs to stdout

### Dashboard Service
```bash
docker-compose -f docker-compose.training.yml up dashboard
```
- Streamlit metrics dashboard
- Available at http://localhost:8501
- Real-time monitoring

### MinIO (S3 Compatible)
```bash
docker-compose -f docker-compose.training.yml up minio
```
- Local S3 storage for DVC
- Console: http://localhost:9001
- API: http://localhost:9000

### MLflow (Experiment Tracking)
```bash
docker-compose -f docker-compose.training.yml up mlflow
```
- Experiment tracking
- Model registry
- UI: http://localhost:5000

---

## 📈 Metrics Dashboard

The Streamlit dashboard provides:

1. **Overview Tab**
   - Total voice/video/text items
   - Training runs count
   - Data distribution charts

2. **Data Ingestion Tab**
   - Recent ingestion runs
   - Daily trends
   - Language distribution

3. **Training Runs Tab**
   - Active/completed runs
   - Validation scores
   - Loss curves

4. **Cost Tracking Tab**
   - Modal/Replicate costs
   - Per-model breakdown
   - Daily spending

5. **Quality Metrics Tab**
   - Score distribution
   - Tier breakdown
   - Source quality ranking

---

## 🔧 GitHub Actions Workflows

### Nightly Data Ingestion (`nightly_video_ingestion.yml`)

**Schedule:** Every night at 2 AM UTC

**Jobs:**
1. `ingest-data` - Multi-source ingestion with quality scoring
2. `analyze-and-sync` - Quality analysis + HuggingFace sync
3. `notify` - Summary notifications

**Inputs:**
- `sources`: all, youtube, rss, huggingface, voice
- `max_items`: Maximum items per source
- `min_quality`: Minimum quality threshold
- `enable_dvc`: Enable data versioning

### Unified Training (`unified_training.yml`)

**Schedule:** Every 2 days at 2 AM UTC

**Jobs:**
1. `check-data` - Verify new training data
2. `curate-data` - Process and filter
3. `modal-training` - GPU training on Modal
4. `validate-models` - Model validation
5. `update-production` - Deploy to HuggingFace

---

## 🔑 Required Secrets

Add these to GitHub Repository Secrets:

| Secret | Purpose |
|--------|---------|
| `HF_TOKEN` | HuggingFace API token |
| `MODAL_TOKEN_ID` | Modal authentication |
| `MODAL_TOKEN_SECRET` | Modal authentication |
| `AWS_ACCESS_KEY_ID` | S3/DVC storage |
| `AWS_SECRET_ACCESS_KEY` | S3/DVC storage |
| `AWS_REGION` | S3 bucket region |

---

## 📋 Next Steps

1. **Push Workflow Updates**
   ```bash
   git add .github/workflows/
   git commit -m "Update workflows for comprehensive ingestion"
   git push origin main
   ```

2. **Configure AWS S3 Bucket**
   - Create bucket: `sisi-lola-datasets`
   - Add IAM credentials to GitHub secrets

3. **Create HuggingFace Dataset Repo**
   - Create: `SisiLolaAI/training-data`
   - Add HF_TOKEN to secrets

4. **Run Initial Ingestion**
   - Manually trigger workflow
   - Monitor in Actions tab
   - Check dashboard for results

---

## 📞 Support

For issues or questions:
- Open GitHub Issue
- Check workflow run logs
- Review dashboard metrics

---

*Last Updated: Auto-generated by Training Infrastructure Setup*
