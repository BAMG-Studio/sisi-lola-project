# Sisi Lola Nigerian Training Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SISI LOLA NIGERIAN AI SYSTEM                         │
│                         (Brain + Voice)                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │  NaijaSenti  │  │ Yoruba Audio │  │ Sisi Lola    │                │
│  │  (~120k)     │  │  Corpus      │  │ Personality  │                │
│  │              │  │              │  │              │                │
│  │ • Yoruba     │  │ • Lagos      │  │ • Slang      │                │
│  │ • Pidgin     │  │ • Ibadan     │  │ • Culture    │                │
│  │ • Hausa      │  │ • Oyo        │  │ • Voice DNA  │                │
│  │ • Igbo       │  │              │  │              │                │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
│         │                 │                  │                         │
│         └─────────────────┴──────────────────┘                         │
│                           │                                            │
└───────────────────────────┼────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      TRAINING PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────┐            │
│  │         unified_training_orchestrator.py               │            │
│  │         (Master Coordinator)                           │            │
│  └────────────────┬───────────────────┬───────────────────┘            │
│                   │                   │                                │
│         ┌─────────▼─────────┐  ┌──────▼──────────┐                    │
│         │  BRAIN TRAINING   │  │ VOICE TRAINING  │                    │
│         │                   │  │                 │                    │
│         │  N-ATLaS-8B       │  │  XTTS-v2        │                    │
│         │  + LoRA           │  │  Fine-tuning    │                    │
│         │                   │  │                 │                    │
│         │  • 4-bit quant    │  │  • Voice clone  │                    │
│         │  • Rank 16        │  │  • 22050 Hz     │                    │
│         │  • Alpha 32       │  │  • Lagos accent │                    │
│         │  • 2-4 hours      │  │  • 4-8 hours    │                    │
│         └─────────┬─────────┘  └──────┬──────────┘                    │
│                   │                   │                                │
│                   └─────────┬─────────┘                                │
│                             │                                          │
└─────────────────────────────┼──────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       MODEL OUTPUTS                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐         ┌──────────────────────┐            │
│  │  natlas_lora/        │         │  xtts_sisi_lola/     │            │
│  │                      │         │                      │            │
│  │  • adapter_model.bin │         │  • model.pth         │            │
│  │  • adapter_config    │         │  • config.json       │            │
│  │  • metadata.json     │         │  • speaker_embed/    │            │
│  │  • ~500MB            │         │  • ~1.5GB            │            │
│  └──────────┬───────────┘         └──────────┬───────────┘            │
│             │                                │                         │
│             └────────────┬───────────────────┘                         │
│                          │                                             │
│                          ▼                                             │
│              ┌───────────────────────┐                                 │
│              │  model_registry.json  │                                 │
│              │  (Version Control)    │                                 │
│              └───────────┬───────────┘                                 │
│                          │                                             │
└──────────────────────────┼─────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    INFERENCE ENGINE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │         inference_nigerian.py                        │              │
│  │         (SisiLolaInference)                          │              │
│  └────────────────┬─────────────────────────────────────┘              │
│                   │                                                    │
│         ┌─────────┴─────────┐                                          │
│         │                   │                                          │
│    ┌────▼────┐         ┌────▼────┐                                    │
│    │  Brain  │         │  Voice  │                                    │
│    │  (LLM)  │         │  (TTS)  │                                    │
│    │         │         │         │                                    │
│    │ Text    │────────▶│ Speech  │                                    │
│    │ Gen     │         │ Gen     │                                    │
│    └─────────┘         └─────────┘                                    │
│         │                   │                                          │
│         └─────────┬─────────┘                                          │
│                   │                                                    │
└───────────────────┼────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVICE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │         nigerian_models.py (Router)                  │              │
│  └──────────────────────────────────────────────────────┘              │
│                                                                         │
│  Endpoints:                                                             │
│  ┌────────────────────────────────────────────────────┐                │
│  │  POST /nigerian/chat                               │                │
│  │  → Full conversation (text + audio)                │                │
│  │                                                    │                │
│  │  POST /nigerian/generate-text                     │                │
│  │  → Text generation only                           │                │
│  │                                                    │                │
│  │  POST /nigerian/generate-speech                   │                │
│  │  → Speech synthesis only                          │                │
│  │                                                    │                │
│  │  GET /nigerian/health                             │                │
│  │  → Model health check                             │                │
│  └────────────────────────────────────────────────────┘                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATION & CI/CD                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  GitHub Actions Workflow                             │              │
│  │  (nigerian_training_pipeline.yml)                    │              │
│  └──────────────────────────────────────────────────────┘              │
│                                                                         │
│  Triggers:                                                              │
│  • 📅 Weekly (Sundays 2 AM UTC)                                        │
│  • 📝 On dataset changes                                               │
│  • 🎯 Manual dispatch                                                  │
│                                                                         │
│  Steps:                                                                 │
│  1. ✅ Check prerequisites                                             │
│  2. ✅ Train brain (N-ATLaS)                                           │
│  3. ✅ Train voice (XTTS)                                              │
│  4. ✅ Upload to HuggingFace Hub                                       │
│  5. ✅ Generate reports                                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Input
    │
    ▼
┌─────────────────┐
│  API Endpoint   │
│  /nigerian/chat │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Inference Engine       │
│  (inference_nigerian)   │
└────────┬────────────────┘
         │
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
┌──────────────────┐      ┌──────────────────┐
│  Brain (N-ATLaS) │      │  Voice (XTTS)    │
│  + LoRA Adapter  │      │  + Fine-tuned    │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         │ Text Response           │ Audio File
         │                         │
         └──────────┬──────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  JSON Response│
            │  {text, audio}│
            └───────────────┘
                    │
                    ▼
                User Output
```

## Training Flow

```
Start Training
    │
    ▼
┌─────────────────────┐
│  Setup & Validation │
│  • Check GPU        │
│  • Login HF         │
│  • Validate samples │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Download Models    │
│  • N-ATLaS-8B       │
│  • XTTS-v2          │
│  • NaijaSenti       │
└─────────┬───────────┘
          │
          ├──────────────────────────┐
          │                          │
          ▼                          ▼
┌──────────────────┐      ┌──────────────────┐
│  Brain Training  │      │  Voice Training  │
│  • Load base     │      │  • Load base     │
│  • Add LoRA      │      │  • Fine-tune     │
│  • Train 2-4h    │      │  • Train 4-8h    │
│  • Save adapter  │      │  • Save model    │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         └──────────┬──────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  Register Models │
         │  • Version track │
         │  • Set active    │
         │  • Export config │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Deploy to HF    │
         │  • Upload brain  │
         │  • Upload voice  │
         │  • Generate docs │
         └────────┬─────────┘
                  │
                  ▼
            Training Complete
```

## Language Support Matrix

```
┌──────────────┬─────────┬─────────┬──────────┬─────────┐
│   Language   │  Brain  │  Voice  │  Status  │ Dialect │
├──────────────┼─────────┼─────────┼──────────┼─────────┤
│   Yoruba     │    ✅   │    ✅   │  Active  │  Lagos  │
│   Pidgin     │    ✅   │    ✅   │  Active  │  Naija  │
│   Nigerian   │    ✅   │    ✅   │  Active  │  Lagos  │
│   English    │         │         │          │         │
│   Hausa      │    ✅   │    ⏳   │  Planned │  Kano   │
│   Igbo       │    ✅   │    ⏳   │  Planned │  Owerri │
│   Swahili    │    ⏳   │    ⏳   │  Future  │  Kenya  │
│   Amharic    │    ⏳   │    ⏳   │  Future  │  Addis  │
└──────────────┴─────────┴─────────┴──────────┴─────────┘
```

## Model Comparison

```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│     Metric      │   N-ATLaS    │    XTTS-v2   │   Combined   │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│  Base Size      │     8B       │    1.5GB     │     ~10GB    │
│  Adapter Size   │    500MB     │     N/A      │    500MB     │
│  Training Time  │    2-4h      │    4-8h      │    6-12h     │
│  Inference      │    1-2s      │    2-3s      │    3-5s      │
│  GPU Memory     │    8GB       │    6GB       │    10GB      │
│  Languages      │     5        │    Multi     │     5+       │
│  Retrainable    │     ✅       │     ✅       │     ✅       │
└─────────────────┴──────────────┴──────────────┴──────────────┘
```

## File Structure

```
Sisi_Lola/
├── ml_training/
│   ├── configs/
│   │   └── nigerian_models_config.yaml    # Configuration
│   ├── scripts/
│   │   ├── train_nigerian_brain.py        # Brain training
│   │   ├── train_nigerian_voice.py        # Voice training
│   │   ├── unified_training_orchestrator.py  # Coordinator
│   │   ├── inference_nigerian.py          # Inference engine
│   │   ├── model_registry.py              # Version control
│   │   ├── setup_nigerian_models.py       # Setup
│   │   └── integrate_with_api.py          # API integration
│   ├── checkpoints/
│   │   ├── natlas_lora/                   # Brain adapter
│   │   └── xtts_sisi_lola/                # Voice model
│   ├── datasets/
│   │   └── sisi_lola_personality.txt      # Personality data
│   ├── outputs/
│   │   ├── production_config.json         # Deployment config
│   │   └── model_registry.json            # Version tracking
│   └── logs/
│       └── training_report_*.json         # Training logs
│
├── .github/workflows/
│   └── nigerian_training_pipeline.yml     # CI/CD workflow
│
├── sisi_lola_api/
│   └── app/routers/
│       └── nigerian_models.py             # API endpoints
│
├── train_nigerian_models.bat              # Windows quick start
├── train_nigerian_models.sh               # Unix quick start
└── NIGERIAN_TRAINING_QUICKSTART.md        # Quick guide
```

---

**Architecture Version**: 1.0.0
**Last Updated**: 2024
