# 🔄 12_MODEL_SYNC - Complete Feedback Loop

This module closes the feedback loop between training and production:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SISI LOLA FEEDBACK LOOP                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌─────────────────┐     ┌──────────────┐             │
│   │   MODAL     │────▶│  HUGGINGFACE    │────▶│  REPLICATE   │             │
│   │  Training   │     │     Hub         │     │  Inference   │             │
│   └─────────────┘     └─────────────────┘     └──────────────┘             │
│         ▲                    │                       │                      │
│         │                    │                       ▼                      │
│         │               ┌────▼────┐           ┌──────────────┐             │
│         │               │   DVC   │           │    USERS     │             │
│         │               │ Storage │           │  Instagram   │             │
│         │               └─────────┘           │   Streamlit  │             │
│         │                                     └──────────────┘             │
│         │                                            │                      │
│         │                   ┌─────────────────┐      │                      │
│         └───────────────────│    FEEDBACK     │◀─────┘                      │
│                             │  Chat Logs      │                             │
│                             │  Engagement     │                             │
│                             └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📁 Module Structure

```
12_MODEL_SYNC/
├── __init__.py           # Module exports
├── huggingface_sync.py   # Push/pull models to HuggingFace Hub
├── replicate_sync.py     # Deploy models to Replicate
├── dvc_manager.py        # Track model versions with DVC
├── quality_validator.py  # Validate before production
├── inference_router.py   # Route via HF Inference Providers
└── README.md             # This file
```

## 🚀 Quick Start

### Push Model to HuggingFace Hub

```python
from 12_MODEL_SYNC import HuggingFaceSync

sync = HuggingFaceSync()
sync.push_model(
    model_path="./models/brain",
    model_type="brain",
    training_info={
        "base_model": "mistralai/Mistral-7B-Instruct-v0.3",
        "epochs": 3,
        "nigerian_focus": True
    }
)
```

### Deploy to Replicate

```python
from 12_MODEL_SYNC import ReplicateSync

sync = ReplicateSync()
sync.sync_from_huggingface(
    model_type="brain",
    version_tag="v1.2.0"
)
```

### Version with DVC

```python
from 12_MODEL_SYNC import DVCManager

dvc = DVCManager()
dvc.track_model("brain", "./models/brain")
dvc.create_version("v1.2.0", "brain", metrics={
    "accuracy": 0.94,
    "nigerian_score": 0.89
})
dvc.push_models()
```

### Validate Before Production

```python
from 12_MODEL_SYNC import QualityValidator

validator = QualityValidator()
report = validator.validate_all("brain", model_path="./models/brain")

if report["overall_passed"]:
    print("✅ Ready for production!")
else:
    print("⚠️ Review required")
```

### Route Inference

```python
from 12_MODEL_SYNC import InferenceRouter, RoutingStrategy

router = InferenceRouter()

# Use fastest provider
result = router.route("brain", "Hello!", strategy=RoutingStrategy.FASTEST)

# Use cheapest provider
result = router.route("brain", "Hello!", strategy=RoutingStrategy.CHEAPEST)

# Use specific provider
result = router.route("brain", "Hello!", 
                      strategy=RoutingStrategy.SPECIFIC, 
                      provider="groq")
```

## 🔧 CLI Usage

### HuggingFace Sync
```bash
python -m 12_MODEL_SYNC.huggingface_sync push --model-type brain --path ./models/brain
python -m 12_MODEL_SYNC.huggingface_sync pull --model-type brain --output ./local/brain
python -m 12_MODEL_SYNC.huggingface_sync info --model-type brain
```

### Replicate Sync
```bash
python -m 12_MODEL_SYNC.replicate_sync deploy --model-type brain --path ./models/brain
python -m 12_MODEL_SYNC.replicate_sync sync --model-type brain
```

### DVC Manager
```bash
python -m 12_MODEL_SYNC.dvc_manager init
python -m 12_MODEL_SYNC.dvc_manager track --model-type brain
python -m 12_MODEL_SYNC.dvc_manager version --model-type brain --version v1.0.0
python -m 12_MODEL_SYNC.dvc_manager push
```

### Quality Validator
```bash
python -m 12_MODEL_SYNC.quality_validator --model-type brain --path ./models/brain
```

### Inference Router
```bash
python -m 12_MODEL_SYNC.inference_router chat --prompt "How you dey?"
python -m 12_MODEL_SYNC.inference_router route --model-type brain --prompt "Hello" --strategy fastest
```

## 🔑 Environment Variables

```bash
# HuggingFace
export HUGGINGFACE_TOKEN=hf_xxx
export HF_TOKEN=hf_xxx

# Replicate
export REPLICATE_API_TOKEN=r8_xxx

# Inference Providers
export GROQ_API_KEY=gsk_xxx
export TOGETHER_API_KEY=xxx
```

## 🎯 Integration with Workflow

The `unified_training.yml` workflow uses these modules:

1. **After Training**: Push model to HuggingFace Hub
2. **Validation**: Run quality checks
3. **Deployment**: Sync to Replicate
4. **Versioning**: Tag with DVC

## 📊 Supported Models

| Model Type | HuggingFace Repo | Replicate Model |
|------------|------------------|-----------------|
| brain | sisilolalive/sisi-lola-brain-mistral | bamg-studio/sisi-lola-brain |
| voice | sisilolalive/sisi-lola-voice-xtts | cjwbw/xtts-v2 |
| producer | sisilolalive/sisi-lola-personality | - |
| vision | sisilolalive/sisi-lola-vision | - |

## 🌍 Nigerian Language Support

All modules are optimized for:
- 🇳🇬 **Nigerian Pidgin** (pcm)
- 🇳🇬 **Yoruba** (yo)
- 🇳🇬 **Hausa** (ha)
- 🇳🇬 **Igbo** (ig)
- 🇬🇧 **English** (en)

---
**Sisi Lola** - Nigeria's AI Content Creator 🇳🇬
