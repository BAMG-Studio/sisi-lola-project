# Sisi Lola Voice Dataset Curator

A comprehensive system for sourcing, validating, and integrating African language speech datasets into the Sisi Lola voice training pipeline.

## Overview

The Voice Dataset Curator provides:
- **Custom GPT**: ChatGPT-based assistant for finding and validating African voice datasets
- **API Endpoints**: REST API for ingesting curated datasets
- **Validation Tools**: Automated quality checks for Sisi Lola compatibility
- **Training Integration**: Seamless connection to XTTS-v2 voice training

## Quick Start

### 1. Set Up the Custom GPT

Create a new Custom GPT in ChatGPT with these settings:

**Name**: Sisi Lola Voice Dataset Curator

**Description**: Expert assistant for sourcing, validating, and preparing African language speech datasets for multilingual TTS and voice cloning.

**Instructions**: Copy from `CUSTOM_GPT_INSTRUCTIONS.md`

**Knowledge Files**: Upload these files from `ml_training/curator/`:
- `african_language_datasets_catalog.csv`
- `audio_processing_recipes.py`
- `dataset_licenses_guide.md`
- `language_coverage_matrix.json`

### 2. Start the API

```bash
cd sisi_lola_api
uvicorn app.main:app --reload
```

The curator endpoints will be available at:
- `GET /curator/health` - Health check
- `POST /curator/ingest` - Ingest curated manifest
- `GET /curator/datasets` - List registered datasets
- `GET /curator/coverage` - Language coverage report
- `GET /curator/catalog` - Browse known datasets
- `POST /curator/search` - Search datasets by filters

### 3. Use the Custom GPT

Ask the Curator GPT questions like:
- "Find me clean Yoruba speech samples for voice cloning (22050 Hz, WAV, 10-60s)"
- "What's the best Nigerian Pidgin dataset with commercial license?"
- "Compare BibleTTS vs NaijaVoices for Hausa TTS training"
- "How do I convert 48kHz FLAC files to 22050 Hz WAV for voice cloning?"

### 4. Ingest Curated Datasets

After the GPT provides recommendations, ingest them via API:

```bash
curl -X POST http://localhost:8000/curator/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "curated_yoruba_v1",
    "name": "Curated Yoruba for Sisi Lola",
    "language": "yoruba",
    "dialect": "lagos",
    "license": "CC-BY-SA-4.0",
    "commercial_ready": true,
    "samples": [
      {
        "audio_path": "yoruba_001.wav",
        "text": "Ẹ káàbọ̀!",
        "duration": 15.5,
        "quality_score": 0.85,
        "sisi_compatible": true
      }
    ]
  }'
```

### 5. Validate Samples

```bash
python ml_training/scripts/validate_curated_samples.py ./04_AUDIO_CORE/voice_samples/
```

### 6. Train with Curated Data

```bash
python ml_training/scripts/train_nigerian_voice.py
# Or to skip curated datasets:
python ml_training/scripts/train_nigerian_voice.py --no-curated
```

## Directory Structure

```
ml_training/curator/
├── african_language_datasets_catalog.csv  # Known datasets catalog
├── audio_processing_recipes.py            # Audio conversion scripts
├── curator_manifest_schema.py             # Python schema definitions
├── dataset_licenses_guide.md              # License guidance
├── language_coverage_matrix.json          # Coverage analysis
├── manifests/                             # Registered dataset manifests
│   └── *.json
└── README.md                              # This file

ml_training/datasets/curated/
├── training_queue.json                    # Datasets queued for training
└── {dataset_id}/                          # Downloaded audio files
    └── *.wav
```

## Manifest Schema

```json
{
  "dataset_id": "curated_yoruba_v1",
  "name": "Curated Yoruba Voice Samples",
  "version": "1.0.0",
  "language": "yoruba",
  "dialect": "lagos",
  "samples": [
    {
      "audio_path": "sample_001.wav",
      "text": "Ẹ káàbọ̀! Mo ń bọ̀ láti Lagos",
      "translation": "Welcome! I'm coming from Lagos",
      "duration": 15.5,
      "quality_score": 0.85,
      "speaker_gender": "female",
      "speaker_age_range": "28-40",
      "emotion": "excited",
      "dialect": "lagos",
      "sisi_compatible": true,
      "persona_match_score": 0.9
    }
  ],
  "audio_specs": {
    "sample_rate": 22050,
    "channels": 1,
    "format": "wav",
    "bit_depth": 16
  },
  "license": "CC-BY-SA-4.0",
  "commercial_ready": true,
  "attribution_text": "BibleTTS Dataset (CC-BY-SA 4.0)"
}
```

## Audio Requirements

| Parameter | Value | Notes |
|-----------|-------|-------|
| Sample Rate | 22050 Hz | XTTS-v2 standard |
| Channels | 1 (Mono) | Required |
| Format | WAV | PCM-16 preferred |
| Duration | 3-60 seconds | Optimal: 10-30 seconds |
| Quality | Clean speech | Minimal background noise |

## Priority Datasets

### High Priority (Commercial Ready)
1. **BibleTTS** - Studio quality, Hausa/Yoruba/Twi/Lingala
2. **Mozilla Common Voice Pidgin** - CC0 licensed Nigerian Pidgin
3. **Yoruba-LJSpeech** - 100+ hours studio Yoruba
4. **AfriSpeech-200** - Nigerian English accents

### Medium Priority
5. **FLEURS** - Multi-language research dataset
6. **OpenSLR-32** - South African languages
7. **OpenSLR-86** - Yoruba crowdsourced

### Known Gaps
- **Igbo**: Only 2 hours commercial-ready
- **Nigerian Pidgin**: Only 20 hours total
- **Yoruba dialects**: Only Lagos dialect covered

## API Reference

### POST /curator/ingest
Ingest a curated dataset manifest.

### GET /curator/datasets
List all registered datasets.

### GET /curator/datasets/{dataset_id}
Get details of a specific dataset.

### DELETE /curator/datasets/{dataset_id}
Remove a registered dataset.

### GET /curator/coverage
Get language coverage report with gap analysis.

### GET /curator/catalog
Browse the known datasets catalog.

### POST /curator/search
Search datasets with filters:
- `language`: Filter by language
- `quality_tier`: "studio", "filtered", "crowdsourced"
- `commercial_only`: Only commercial-ready datasets
- `min_hours`: Minimum duration in hours

### POST /curator/trigger-training
Queue datasets for the next training run.

## Validation Metrics

The validator checks:
- **Format**: WAV, 22050 Hz, mono
- **Duration**: 3-60 seconds (optimal 10-30s)
- **Quality**: Signal power, silence ratio, SNR estimate
- **Persona Match**: Female voice, Nigerian accent, energy level

## Contributing

To add new datasets to the catalog:

1. Edit `african_language_datasets_catalog.csv`
2. Update `language_coverage_matrix.json`
3. Test with the search API
4. Document license in `dataset_licenses_guide.md`

## License

This curator system is part of the Sisi Lola project.
Datasets have individual licenses - see `dataset_licenses_guide.md`.
