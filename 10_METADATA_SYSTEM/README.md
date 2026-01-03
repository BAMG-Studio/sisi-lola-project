# ═══════════════════════════════════════════════════════════════════════════════
#                    SISI LOLA METADATA SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
#              AWS Glue / Apache Atlas Style Data Catalog
# ═══════════════════════════════════════════════════════════════════════════════

## 📋 Overview

The Sisi Lola Metadata System provides centralized asset tracking and data 
cataloging across the entire AI pipeline. Inspired by AWS Glue and Apache Atlas,
it offers:

- **Metadata Store**: SQLite-based asset registration and querying
- **Data Catalog**: Discovery, profiling, and dataset management
- **Lineage Tracker**: Transformation history and model provenance
- **Nigerian Content Classification**: Automatic dialect detection

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          METADATA SYSTEM                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        METADATA STORE                                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐ │ │
│  │  │  Assets  │  │  Lineage │  │  Quality │  │  Nigerian Analysis       │ │ │
│  │  │   Table  │  │   Table  │  │  History │  │      Table               │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────────────┘ │ │
│  │                         SQLite + FTS5                                    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         DATA CATALOG                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │ │
│  │  │   Discovery  │  │   Schemas    │  │   Profiling                  │  │ │
│  │  │    Service   │  │   Registry   │  │   & Statistics               │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                       LINEAGE TRACKER                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │ │
│  │  │Transformation│  │    Model     │  │   Impact                     │  │ │
│  │  │   Records    │  │  Provenance  │  │   Analysis                   │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Basic Usage

```python
from metadata_system import (
    MetadataStore,
    DataCatalog,
    LineageTracker,
    NigerianContentClassifier,
    AssetType,
    NigerianLanguage,
    register_video,
    register_audio
)

# Initialize components
store = MetadataStore("sisi_lola_metadata.db")
catalog = DataCatalog(store)
tracker = LineageTracker("lineage_data")
classifier = NigerianContentClassifier()

# Register a video
video_id = register_video(
    store,
    name="Lagos Tech Talk EP 15",
    storage_path="/data/videos/lagos_tech_15.mp4",
    duration_seconds=1800,
    size_bytes=500_000_000,
    language=NigerianLanguage.PIDGIN,
    source_url="https://youtube.com/watch?v=example"
)

# Register derived audio
audio_id = register_audio(
    store,
    name="Lagos Tech Talk - Audio",
    storage_path="/data/audio/lagos_tech_15.wav",
    duration_seconds=1800,
    language=NigerianLanguage.PIDGIN,
    parent_video_id=video_id
)

# Record the transformation
tracker.record_audio_extraction(video_id, audio_id)
```

### Nigerian Content Classification

```python
# Classify text for Nigerian content
result = classifier.classify_text("How you dey? I dey fine o!")

print(result)
# {
#     'primary_language': NigerianLanguage.PIDGIN,
#     'confidence': 0.85,
#     'is_nigerian': True,
#     'nigerian_score': 0.9,
#     'detected_markers': ['dey', 'how', 'dey']
# }
```

### Dataset Management

```python
# Create a logical dataset from assets
dataset_id = catalog.register_dataset(
    name="Nigerian Voice Training Dataset v1",
    description="Curated Nigerian voice samples for TTS training",
    asset_ids=[audio_id_1, audio_id_2, audio_id_3, ...],
    tags=["voice", "nigerian", "pidgin", "training"]
)

# Profile the dataset
profile = catalog.profile_dataset(dataset_id)
print(f"Nigerian content ratio: {profile.nigerian_content_ratio:.1%}")
print(f"Language distribution: {profile.language_distribution}")
```

### Lineage & Provenance

```python
# Record model training
tracker.record_training(
    dataset_ids=["dataset_001", "dataset_002"],
    model_asset_id="model_voice_001",
    model_name="sisi-lola-voice-v1",
    model_type="voice_lora",
    training_config={'epochs': 10, 'lr': 1e-4},
    metrics={'wer': 0.08, 'cer': 0.03},
    nigerian_ratio=0.85,
    dialects=['pidgin', 'yoruba']
)

# Get impact analysis
impact = tracker.impact_analysis("video_001")
print(f"Descendants: {impact['descendant_count']}")
print(f"Models impacted: {impact['models_impacted']}")

# Generate lineage report
report = tracker.generate_lineage_report("video_001")
```

---

## 📊 Asset Types

| Type | Description | Typical Sources |
|------|-------------|-----------------|
| VIDEO | Video files | YouTube, User uploads |
| AUDIO | Audio files | Extracted, Recorded |
| IMAGE | Image files | Generated, Frames |
| TRANSCRIPT | Text transcriptions | Whisper, Manual |
| MODEL | Trained models | Modal training |
| CHECKPOINT | Training checkpoints | Modal training |
| LORA | LoRA adapters | Fine-tuning |
| DATASET | Logical datasets | Curated collections |
| FEEDBACK | User feedback | Webhook collector |
| CONFIG | Configuration files | System configs |

---

## 🇳🇬 Nigerian Language Support

The system automatically detects and classifies Nigerian content:

- **Pidgin English**: "wetin dey happen", "how you dey"
- **Yoruba-influenced**: Tonal markers, borrowed words
- **Hausa-influenced**: Greeting patterns, consonants
- **Igbo-influenced**: Vowel harmonies, expressions

Nigerian content receives a **1.5x training weight bonus** in the feedback loop.

---

## 🔍 Search Capabilities

### Full-Text Search
```python
# Search across all assets
results = store.search_assets(query="lagos tech")
```

### Filtered Search
```python
# Find high-quality Nigerian audio
results = store.search_assets(
    asset_type=AssetType.AUDIO,
    language=NigerianLanguage.PIDGIN,
    min_quality=0.8,
    is_nigerian=True
)
```

### Training Dataset Discovery
```python
# Get datasets ready for training
datasets = catalog.get_training_datasets(
    min_quality=0.7,
    require_nigerian=True,
    min_samples=100
)
```

---

## 📈 Statistics & Monitoring

```python
# Get system-wide statistics
stats = store.get_statistics()

print(stats)
# {
#     'by_type': {'video': 1234, 'audio': 1180, ...},
#     'by_language': {'pidgin': 5234, 'english': 3421, ...},
#     'nigerian': {
#         'total': 15000,
#         'nigerian_count': 12456,
#         'percentage': 83.04,
#         'avg_score': 0.82
#     },
#     'quality_distribution': {'high': 10000, 'medium': 4000, 'low': 1000},
#     'storage': {'total_bytes': 500_000_000_000, 'total_duration_hours': 1250.5}
# }

# Get catalog summary
summary = catalog.get_summary()
```

---

## 🔗 Integration Points

### With Feedback Loop (09_FEEDBACK_LOOP)
```python
# Register feedback as asset
from metadata_store import AssetMetadata, AssetType

feedback_metadata = AssetMetadata(
    asset_id=generate_asset_id(AssetType.FEEDBACK),
    asset_type=AssetType.FEEDBACK,
    name=f"feedback_{prediction_id}",
    storage_path="feedback_data.db",
    is_nigerian=is_nigerian_content,
    quality_score=rating / 5.0,
    properties={'prediction_id': prediction_id, 'rating': rating}
)
store.register_asset(feedback_metadata)
```

### With Training Pipeline (08_MLOPS_PIPELINE)
```python
# After training completes
tracker.record_training(
    dataset_ids=training_dataset_ids,
    model_asset_id=new_model_id,
    model_name=model_name,
    model_type="voice_lora",
    training_config=config,
    metrics=training_metrics
)
```

### With Ingestion Pipeline
```python
# After ingesting YouTube video
video_id = register_video(
    store,
    name=video_title,
    storage_path=local_path,
    duration_seconds=duration,
    source_url=youtube_url
)
```

---

## 📁 File Structure

```
10_METADATA_SYSTEM/
├── __init__.py              # Module exports
├── metadata_store.py        # Core SQLite metadata storage
├── data_catalog.py          # Data catalog & discovery
├── lineage_tracker.py       # Transformation & provenance tracking
└── README.md               # This file
```

---

## 🎯 Key Features

1. **Unified Asset Registry**: Single source of truth for all assets
2. **Nigerian Content Detection**: Automatic classification with bonus weighting
3. **Full Lineage Tracking**: Know exactly where every asset came from
4. **Model Provenance**: Track training data and metrics for all models
5. **Impact Analysis**: Understand downstream effects of any asset
6. **Full-Text Search**: Fast discovery using SQLite FTS5
7. **Quality Tracking**: Historical quality metrics for trend analysis
8. **Dataset Management**: Logical grouping with profiling

---

## 🔧 Configuration

The system uses sensible defaults but can be configured:

```python
# Custom database path
store = MetadataStore("custom/path/metadata.db")

# Custom lineage storage
tracker = LineageTracker("custom/lineage/path")

# Nigerian keyword customization
classifier = NigerianContentClassifier()
classifier.pidgin_markers.extend(['custom', 'markers'])
```

---

## 📝 Version History

- **v1.0** - Initial release with core metadata, catalog, and lineage features

---

*Part of the Sisi Lola Nigerian AI System*
