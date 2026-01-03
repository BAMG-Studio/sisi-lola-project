# ═══════════════════════════════════════════════════════════════════════════════
#                    SISI LOLA INTEGRATION MODULE
# ═══════════════════════════════════════════════════════════════════════════════
#               Unified Integration Layer for All Components
# ═══════════════════════════════════════════════════════════════════════════════

## 📋 Overview

This module provides the central integration layer that connects all Sisi Lola 
system components:

- **Master Orchestrator**: Event-driven component coordination
- **API Server**: Unified REST API for all operations
- **Event Bus**: Async event publishing and subscription
- **Cost Management**: $50/day limit enforcement
- **Health Monitoring**: Component status tracking

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          API SERVER (FastAPI)                                 │
│     /api/v1/chat  /api/v1/generate/*  /api/v1/training  /api/v1/feedback     │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        MASTER ORCHESTRATOR                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           EVENT BUS                                      │ │
│  │  content.ingested → content.processed → feedback.received → training.*  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Content   │  │  Training   │  │   Cost      │  │  Health             │ │
│  │   Manager   │  │   Manager   │  │   Manager   │  │  Monitor            │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
         │                  │                  │                  │
         ▼                  ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│ 08_MLOPS   │    │ 09_FEEDBACK │    │ 10_METADATA │    │  sisi_lola_chat │
│ PIPELINE   │    │    LOOP     │    │   SYSTEM    │    │   (Streamlit)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────────┘
```

---

## 🚀 Quick Start

### Start the API Server

```bash
cd 11_INTEGRATION
python api_server.py --port 8000
```

### Use the Orchestrator Programmatically

```python
from integration import SisiLolaOrchestrator

# Initialize
orchestrator = SisiLolaOrchestrator()
orchestrator.start()

# Generate content
result = await orchestrator.generate_content(
    modality='voice',
    prompt='How you dey?'
)

# Trigger training
result = await orchestrator.trigger_training(
    training_type='voice',
    dataset_ids=['dataset_001', 'dataset_002']
)

# Check health
health = orchestrator.get_system_health()
print(health)

# Stop
orchestrator.stop()
```

---

## 📡 API Endpoints

### Chat
```
POST /api/v1/chat
{
    "message": "How you dey?",
    "dialect": "pidgin",
    "dialect_intensity": 70,
    "response_mode": "voice"  // text, voice, or video
}
```

### Voice Generation
```
POST /api/v1/generate/voice
{
    "text": "How you dey?",
    "voice_id": "sisi_lola_v1",
    "speed": 1.0,
    "emotion": "friendly"
}
```

### Video Generation
```
POST /api/v1/generate/video
{
    "text": "How you dey?",  // or audio_url
    "duration_seconds": 10,
    "aspect_ratio": "9:16"
}
```

### Image Generation
```
POST /api/v1/generate/image
{
    "prompt": "Sisi Lola in Ankara outfit",
    "style": "photorealistic",
    "seed": 45822  // Character consistency
}
```

### Training
```
POST /api/v1/training/trigger
{
    "training_type": "voice",
    "dataset_ids": ["dataset_001"],
    "config": {"epochs": 10}
}
```

### Feedback
```
POST /api/v1/feedback
{
    "prediction_id": "pred_123",
    "rating": 5,
    "is_nigerian": true  // Gets 1.5x bonus
}
```

### Health
```
GET /health
GET /api/v1/stats
GET /api/v1/cost
```

---

## 📊 Event Types

| Event | Description | Payload |
|-------|-------------|---------|
| content.ingested | New content ingested | title, path, is_nigerian |
| content.processed | Content processing done | type, source_id, output_id |
| content.generated | AI content generated | modality, prompt, result |
| training.triggered | Training job triggered | training_type, dataset_ids |
| training.started | Training job started | job_id, config |
| training.completed | Training job finished | model_id, metrics |
| training.failed | Training job failed | job_id, error |
| feedback.received | User feedback submitted | prediction_id, rating |
| system.cost_warning | 80% budget reached | current, limit |
| system.cost_exceeded | Budget exceeded | current, limit |

---

## 💰 Cost Management

The system enforces a **$50/day** cost limit:

- Tracks all Replicate API costs
- Tracks Modal GPU costs
- Warns at 80% utilization
- Blocks requests when exceeded
- Resets daily at midnight

```python
# Check cost status
status = orchestrator.get_cost_status()
# {
#     'daily_cost': 25.50,
#     'cost_limit': 50.0,
#     'remaining': 24.50,
#     'utilization_percent': 51.0
# }
```

---

## 🇳🇬 Nigerian Content Handling

Nigerian content receives special treatment:

- **Auto-detection**: Dialect markers in text/audio
- **1.5x Training Weight**: More influence on model updates
- **Priority Processing**: Faster queue handling
- **Quality Bonus**: Higher scores in feedback loop

```python
# Nigerian detection in classifier
classifier = NigerianContentClassifier()
result = classifier.classify_text("Wetin dey happen?")
# {
#     'is_nigerian': True,
#     'primary_language': 'pidgin',
#     'nigerian_score': 0.92
# }
```

---

## 🏥 Health Monitoring

```python
health = orchestrator.get_system_health()
# {
#     'overall_status': 'healthy',
#     'components': {
#         'metadata_store': {'status': 'healthy', 'latency_ms': 5.2},
#         'event_bus': {'status': 'healthy', 'queue_size': 0}
#     },
#     'daily_cost': 12.50,
#     'cost_limit': 50.0,
#     'cost_utilization': 25.0
# }
```

---

## 🔧 Configuration

```yaml
# config.yaml
daily_cost_limit: 50.0
nigerian_bonus: 1.5
quality_threshold: 0.7
training_trigger_samples: 1000

components:
  metadata_store:
    db_path: data/metadata_store.db
  feedback_loop:
    db_path: data/feedback_data.db
  training:
    gpu_type: A100-40GB
    max_concurrent_jobs: 2
```

---

## 📁 File Structure

```
11_INTEGRATION/
├── __init__.py           # Module exports
├── orchestrator.py       # Master orchestrator with event bus
├── api_server.py         # FastAPI server
└── README.md            # This file
```

---

## 🔗 Component Dependencies

```
11_INTEGRATION (This Module)
├── 08_MLOPS_PIPELINE
│   ├── ingestion/youtube_scraper.py
│   ├── preprocessing/advanced_audio_processor.py
│   └── training/speech_to_speech_trainer.py
│
├── 09_FEEDBACK_LOOP
│   ├── replicate_client/sisi_lola_replicate.py
│   ├── webhook_service/app.py
│   ├── data_processor/collector.py
│   ├── data_processor/curator.py
│   └── retraining_triggers/scheduler.py
│
├── 10_METADATA_SYSTEM
│   ├── metadata_store.py
│   ├── data_catalog.py
│   └── lineage_tracker.py
│
└── sisi_lola_chat (Streamlit Dashboard)
    ├── Home.py
    └── pages/*
```

---

## 🎯 Key Features

1. **Event-Driven Architecture**: Loose coupling between components
2. **Async Processing**: Non-blocking operations
3. **Cost Control**: Hard budget limits
4. **Nigerian Priority**: 1.5x weight for Nigerian content
5. **Unified API**: Single entry point for all operations
6. **Health Monitoring**: Real-time component status
7. **Lineage Tracking**: Full data provenance

---

## 📝 Version History

- **v1.0** - Initial release with orchestrator and API server

---

*Part of the Sisi Lola Nigerian AI System*
