# MLOps Pipeline for Sisi Lola

Dataset management, preprocessing, and training pipelines for multilingual voice AI.

## 📚 Documentation

- **[TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)** - Complete technical reference (50+ pages)
- **[README.md](README.md)** - This file (quick reference)

## 🎯 What This Pipeline Does

**Technical:** Automates ingestion, preprocessing, validation, and manifest building for multilingual ASR/TTS training datasets across 9+ African languages.

**Layman:** Downloads voice recordings in African languages, cleans them up, checks quality, and prepares them for AI training. Like a factory that takes raw voice samples and turns them into organized training material.

## 🏗️ Structure

```
08_MLOPS_PIPELINE/
├── cli/                  # Command-line interface (Typer)
├── configs/              # Dataset configurations (YAML)
├── data/                 # Data directories (gitignored)
│   ├── raw/             # Downloaded datasets
│   ├── interim/         # Intermediate processing
│   ├── processed/       # Training-ready manifests
│   └── external/        # Manual downloads
├── docs/                 # Documentation
│   ├── README.md        # This file
│   └── TECHNICAL_GUIDE.md   # Complete technical reference
├── evaluation/           # Quality metrics and reports
│   ├── dataset_coverage_report.py   # Language/speaker coverage
│   └── audio_quality_report.py      # Audio validation
├── ingestion/            # Dataset downloaders
│   └── ingest_registry.py   # MENYO-20k, Fleurs, Common Voice, etc.
├── pipelines/            # Prefect workflows
│   └── flow_ingest_preprocess.py   # Full pipeline orchestration
├── preprocessing/        # Data preparation
│   ├── normalize_text.py           # Unicode NFC, whitespace cleanup
│   ├── code_switch.py              # Language boundary detection
│   ├── build_asr_manifest.py       # Whisper training manifest
│   └── build_tts_metadata.py       # XTTS training metadata
├── scripts/              # Utility scripts
│   └── quick_smoke_yo_pcm.sh   # Smoke test
├── tests/                # Unit tests (pytest)
│   ├── test_language_detector.py
│   ├── test_prosody_processor.py
│   ├── test_normalize_text.py
│   └── test_build_manifests.py
└── requirements.txt      # Python dependencies
```

## ⚡ Quick Start

### Installation

**Technical:**
```bash
cd 08_MLOPS_PIPELINE
pip install -r requirements.txt
huggingface-cli login  # Enter token from https://huggingface.co/settings/tokens
```

**Layman:** Install helper tools and log in to HuggingFace (free account) to download datasets.

### Basic Commands

```bash
# List available datasets
python cli/main.py datasets list

# Download all datasets (may take 30+ minutes)
python cli/main.py ingest all

# Download specific dataset
python cli/main.py ingest menyo20k
python cli/main.py ingest common_voice_africa

# Normalize text for Yoruba
python cli/main.py preprocess --lang yo --lower false

# Generate quality reports
python cli/main.py report coverage
```

## 🚀 Full Pipeline Workflow

**Technical:**
```bash
# 1. Ingest datasets
python cli/main.py ingest all

# 2. Build ASR manifest (for Whisper training)
python preprocessing/build_asr_manifest.py \
  --datasets fleurs common_voice \
  --output data/processed/asr_manifest_all.tsv

# 3. Build TTS metadata (for XTTS training)
python preprocessing/build_tts_metadata.py \
  --voice-dir ../04_AUDIO_CORE/01_Voice_Samples \
  --speaker-id sisi_lola \
  --output data/processed/tts_metadata.csv

# 4. Generate quality reports
python evaluation/dataset_coverage_report.py \
  --asr-manifest data/processed/asr_manifest_all.tsv \
  --output data/processed/reports/coverage.json

python evaluation/audio_quality_report.py \
  --voice-dir ../04_AUDIO_CORE/01_Voice_Samples \
  --output data/processed/reports/audio_quality.json

# 5. Run Prefect flow (automates 1-4)
python pipelines/flow_ingest_preprocess.py
```

**Layman:**
1. Download voice recordings: `python cli/main.py ingest all`
2. Create training recipe books: `python preprocessing/build_asr_manifest.py`
3. Check quality: `python evaluation/dataset_coverage_report.py`
4. Or run everything automatically: `python pipelines/flow_ingest_preprocess.py`

## 📊 Supported Datasets

| Dataset | Languages | Type | Size | Source |
|---------|-----------|------|------|--------|
| **MENYO-20k** | Yoruba-English | Parallel text | 20K pairs | GitHub |
| **Fleurs** | yo, sw (KE/TZ), fr | ASR | 5-10h/lang | HuggingFace |
| **Common Voice 17.0** | yo, ha, ig, sw, ak | ASR | 1-50h/lang | HuggingFace |
| **MasakhaNER** | yo, ha, ig | NER | 2K samples | HuggingFace |
| **ALFFA** | Swahili | ASR | ~10h | Manual |
| **Lagos-NWU** | Nigerian English | ASR | ~5h | Manual (request) |

**Technical:** All datasets configured in `configs/datasets.yaml` with download instructions.

**Layman:** We download voice recordings from 7+ online sources covering Yoruba, Swahili, Hausa, Igbo, and other African languages.

## 🧪 Testing

**Technical:**
```bash
# Run all unit tests
cd 08_MLOPS_PIPELINE
pytest tests/ -v

# Run specific test file
pytest tests/test_language_detector.py -v

# Run with coverage
pytest tests/ --cov=preprocessing --cov=evaluation --cov-report=html
```

**Layman:** 
```bash
pytest tests/ -v
```
This checks if all the code works correctly (like a spell-checker for code).

## 📈 Quality Metrics

### Dataset Coverage Report

**Technical:** Analyzes language distribution, speaker diversity, code-switching rate, text quality (diacritic coverage).

**Layman:** Checks if we have enough voice samples in each language and from enough different speakers.

Example output:
```
🌍 Language Coverage:
  yo        5000 samples   12.5h   25 speakers
  pcm       2000 samples    4.8h    8 speakers
  sw_ke     3500 samples    8.2h   15 speakers

📝 Text Quality:
  Yoruba diacritic coverage: 85.3%

💡 Recommendations:
  ⚠️ pcm: Only 4.8 hours. Need at least 5 hours for good ASR.
```

### Audio Quality Report

**Technical:** Validates sample rate, duration, RMS energy, clipping, SNR estimation.

**Layman:** Checks if recordings are clear, loud enough, and not distorted.

Example output:
```
🎤 AUDIO QUALITY REPORT
  Total files: 1000
  Good quality: 850 (85%)
  With warnings: 120
  Errors: 30

⚠️ Issues Found:
  too_quiet      45 files
  clipping       12 files
  low_snr        63 files
```

## 🔧 Configuration

### datasets.yaml

**Technical:** Defines dataset sources, subsets, and download methods.

```yaml
menyo20k:
  source: github
  url: https://github.com/dadelani/menyo-20k_MT
  languages: [yo, en]
  type: parallel

common_voice_africa:
  source: huggingface
  dataset_id: mozilla-foundation/common_voice_17_0
  subsets: [yo, ha, ig, sw, ak]
  type: asr
```

**Layman:** This file tells the system where to download datasets from (like bookmarks for voice recording websites).

### languages.yaml

**Technical:** Language metadata with ISO codes, regions, speakers.

```yaml
yo:
  name: Yoruba
  region: Nigeria
  speakers: 40M
  scripts: [Latin, diacritics]
  
pcm:
  name: Nigerian Pidgin
  region: Nigeria
  speakers: 75M
  scripts: [Latin]
```

**Layman:** This file describes each language (name, where it's spoken, how many people speak it).

## 🚨 Troubleshooting

### Common Issues

| Issue | Fix |
|-------|-----|
| `ConnectionError` during download | Run `huggingface-cli login` |
| `ModuleNotFoundError: librosa` | Run `pip install librosa soundfile` |
| Manifests show "0 samples" | Run `python cli/main.py ingest all` first |
| Yoruba diacritics broken | Set terminal encoding: `export LANG=en_US.UTF-8` |
| Audio files flagged as "too_quiet" | Re-record with higher mic gain or boost volume |

**Detailed troubleshooting:** See [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) Section 9.

## 📖 Further Reading

- **Architecture:** `../00_PROJECT_CORE/Documentation/MULTILINGUAL_VOICE_ENGINE_ARCHITECTURE.md`
- **Implementation Guide:** `../00_PROJECT_CORE/Documentation/IMPLEMENTATION_GUIDE_MULTILINGUAL_VOICE.md`
- **Quick Reference:** `../00_PROJECT_CORE/Documentation/QUICK_REFERENCE_MULTILINGUAL_VOICE.md`

## 🤝 Contributing

Run tests before committing:
```bash
pytest tests/ -v
python scripts/quick_smoke_yo_pcm.sh  # Smoke test
```

---

**Version:** 1.0  
**Last Updated:** 2024  
**Maintainer:** Sisi Lola Project Team

## 🎬 Video Actor/Characterization Pipeline

Sisi Lola's video-acting model covers a wide range of performances and expressive behaviors, specially trained for African influencer/actress/podcaster/journalist roles.

**Pipeline Structure:**
- `data/video_raw/` - Raw video clips
- `data/video_processed/` - Preprocessed frames/audio
- `data/video_annotated/` - Annotated clips with activity, attitude, role, emotion, cultural markers
- `configs/video_labels.yaml` - Label schema
- `preprocessing/prepare_video_dataset.py` - Frame/audio extraction
- `preprocessing/annotate_video_clips.py` - Annotation tool
- `training/train_video_actor_model.py` - Model training script
- `tests/` - Unit tests for each stage

**Supported Activities:** Reading, dancing, counseling, sleeping, eating, working out, running, driving, sky-diving, podcasting, reporting, vlogging, etc.
**Attitudes:** Confident, empathetic, energetic, calm, playful, serious, dramatic
**Roles:** Influencer, actress, podcaster, journalist
**Emotions:** Happy, sad, angry, surprised, neutral
**Cultural Markers:** Greeting, slang, fashion, social cue

**Usage:**
```bash
python preprocessing/prepare_video_dataset.py --input-dir data/video_raw --output-dir data/video_processed
python preprocessing/annotate_video_clips.py --input-dir data/video_processed --output-csv data/video_annotated/annotations.csv
python training/train_video_actor_model.py --data-dir data/video_processed --annotations data/video_annotated/annotations.csv --labels configs/video_labels.yaml --epochs 10
pytest tests/ -v
```

See [VIDEO_ACTOR_PIPELINE.md](VIDEO_ACTOR_PIPELINE.md) for full details and workflow.
