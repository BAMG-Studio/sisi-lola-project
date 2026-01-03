# 🔄 Sisi Lola Feedback Loop

## Complete Replicate → Modal Training Pipeline

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                  REPLICATE → MODAL FEEDBACK LOOP                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌──────────────┐    Webhook    ┌──────────────┐   Trigger   ┌──────────────┐ ║
║  │  REPLICATE   │ ───────────► │ FEEDBACK LOOP │ ──────────► │    MODAL     │ ║
║  │  Inference   │              │   Pipeline    │             │   Training   │ ║
║  │              │              │               │             │              │ ║
║  │ 🧠 Brain     │              │ 📥 Collect    │             │ 🏋️ Voice     │ ║
║  │ 👁️ Eyes      │ ◄─────────── │ 🔍 Curate     │ ◄────────── │ 🎬 Video     │ ║
║  │ 🗣️ Voice     │   Better     │ 📊 Quality    │  Improved   │ 🖼️ Image     │ ║
║  │ 🎬 Video     │   Models     │ 🚀 Trigger    │   Models    │ 📝 Text      │ ║
║  │ 💜 Heart     │              │ 📈 Monitor    │             │              │ ║
║  └──────────────┘              └──────────────┘             └──────────────┘ ║
║                                       │                                       ║
║                               ┌───────▼───────┐                              ║
║                               │  🇳🇬 Nigerian  │                              ║
║                               │   Priority    │                              ║
║                               │   (1.5x)      │                              ║
║                               └───────────────┘                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 📦 Directory Structure

```
09_FEEDBACK_LOOP/
├── orchestrator.py              # Main orchestrator - ties everything together
├── README.md                    # This file
│
├── replicate_client/
│   └── sisi_lola_replicate.py   # Unified Replicate client (Brain, Eyes, Voice, Heart)
│
├── webhook_service/
│   └── app.py                   # FastAPI webhook receiver
│
├── data_processor/
│   ├── collector.py             # Feedback collection from multiple sources
│   └── curator.py               # Quality filtering and curation
│
├── retraining_triggers/
│   ├── modal_training.py        # Modal GPU training jobs
│   └── scheduler.py             # Intelligent trigger scheduling
│
└── config/
    └── feedback_config.yaml     # Master configuration
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install modal replicate fastapi httpx pyyaml
```

### 2. Set Environment Variables

```bash
# Required
export REPLICATE_API_TOKEN="r8_xxxx"
export MODAL_TOKEN_ID="xxx"
export MODAL_TOKEN_SECRET="xxx"

# Optional - for webhook verification
export REPLICATE_WEBHOOK_SECRET="whsec_xxxx"
export GITHUB_TOKEN="ghp_xxxx"
```

### 3. Run the Orchestrator

```bash
# Check status
python orchestrator.py --action status

# Run curation cycle
python orchestrator.py --action curate

# Check training triggers
python orchestrator.py --action trigger

# Run full cycle
python orchestrator.py --action cycle
```

## 🧠 Components

### Replicate Client (`replicate_client/sisi_lola_replicate.py`)

**Complete Sisi Lola integration with state-of-the-art models:**

```python
from replicate_client.sisi_lola_replicate import SisiLolaReplicate

sisi = SisiLolaReplicate()

# Generate image with character consistency (SEED 45822)
image = await sisi.eyes.generate_image(
    "Nigerian tech presenter in Lagos studio",
    include_character=True
)

# Generate voice with Nigerian accent
audio = await sisi.voice.speak("How far, my people!")

# Create talking video (Omni-Human - NOT wav2lip!)
video = await sisi.video.create_talking_video(image, audio)

# Chat with Nigerian cultural awareness
response = await sisi.brain.think("Wetin dey happen for tech today?")
```

**Modalities:**
- 🧠 **Brain** - Text/Chat with Nigerian Pidgin understanding
- 👁️ **Eyes** - Image generation with character consistency
- 🗣️ **Voice** - TTS with Nigerian accent, voice cloning
- 🎬 **Video** - State-of-the-art talking videos (Omni-Human)
- 💜 **Heart** - Cultural sentiment and personality

### Webhook Service (`webhook_service/app.py`)

**FastAPI server for Replicate webhooks:**

```bash
# Start the webhook server
uvicorn webhook_service.app:app --host 0.0.0.0 --port 8000

# Endpoints
POST /webhooks/replicate    # Receive Replicate predictions
POST /feedback/explicit     # Collect user ratings
GET  /metrics              # Prometheus metrics
GET  /health               # Health check
```

### Feedback Collector (`data_processor/collector.py`)

**Multi-source feedback collection:**

```python
from data_processor.collector import FeedbackCollectorService, FeedbackCategory

service = FeedbackCollectorService()

# Collect from Replicate webhook
service.collect_webhook(replicate_payload)

# Collect explicit user rating
service.collect_rating(
    content_id="pred_123",
    rating=0.9,
    category=FeedbackCategory.VOICE,
    comment="Great Nigerian accent!"
)

# Collect engagement signal
service.collect_share(
    content_id="pred_123",
    category=FeedbackCategory.VIDEO,
    platform="whatsapp"
)
```

### Feedback Curator (`data_processor/curator.py`)

**Quality filtering with Nigerian content bonus:**

```python
from data_processor.curator import FeedbackCurator, CurationConfig

config = CurationConfig(
    min_quality_score=0.6,
    training_quality_threshold=0.75,
    nigerian_content_bonus=0.15  # 15% bonus for Nigerian content!
)

curator = FeedbackCurator(db, config)

# Process pending feedback
results = curator.process_pending(limit=100)
# Returns: {"accepted": 85, "rejected": 15, "training_ready": 60}
```

### Training Scheduler (`retraining_triggers/scheduler.py`)

**Intelligent training trigger evaluation:**

```python
from retraining_triggers.scheduler import TrainingScheduler

scheduler = TrainingScheduler()

# Check if training should be triggered
results = await scheduler.check_and_trigger(category="voice")

# Triggers are based on:
# - Feedback volume (≥50 training-ready items)
# - Quality scores (avg ≥0.7)
# - Time since last training (≤7 days)
# - Nigerian content bonus (1.5x weight)
# - Daily cost limit ($50)
```

### Modal Training (`retraining_triggers/modal_training.py`)

**Modal GPU training jobs:**

```python
from retraining_triggers.modal_training import ModalTrainingClient

client = ModalTrainingClient()

# Upload training data
data_path = client.upload_data(training_data, "voice")

# Start voice training
result = client.start_voice_training(
    data_path,
    batch_size=8,
    max_steps=1000,
    use_lora=True
)

# Check status
status = client.check_status(result["job_id"])
```

## 🇳🇬 Nigerian Content Priority

The feedback loop gives **1.5x weight** to Nigerian content:

| Marker Type | Examples |
|-------------|----------|
| Pidgin | how far, no wahala, wetin, abeg, oya |
| Yoruba | e kaaro, bawo ni, pele |
| Hausa | sannu, yaya, da godiya |
| Igbo | kedu, nno, daalu |
| Nigerian English | Lagos, Naija, gist, oga |

**Example:**
- 30 Nigerian-content items = 45 effective items (1.5x)
- Meets the 50-item threshold for training!

## 💰 Cost Management

Training costs are carefully managed:

| Category | Cost/Hour | Max Hours | Max Cost |
|----------|-----------|-----------|----------|
| Voice | $3.00 | 2 | $6.00 |
| Video | $4.00 | 4 | $16.00 |
| Image | $3.00 | 2 | $6.00 |

**Daily limit:** $50 USD

Training pauses when limit is reached and resumes the next day.

## 📊 Monitoring Dashboard

View the Streamlit dashboard at:
```
sisi_lola_chat/pages/07_🔄_Feedback_Loop.py
```

Features:
- Real-time feedback statistics
- Quality score distribution
- Nigerian content analytics
- Training history
- Cost tracking

## 🔌 GitHub Actions Integration

The feedback loop integrates with existing workflows:

```yaml
# .github/workflows/unified_training.yml
on:
  repository_dispatch:
    types: [training_triggered]

# Payload from feedback loop:
client_payload:
  category: voice
  run_id: voice_20240115_120000
  training_ready_count: 75
  avg_quality: 0.82
```

## 📝 Configuration

Edit `config/feedback_config.yaml`:

```yaml
# Quality thresholds
quality_filter:
  min_quality_score: 0.6
  training_quality_threshold: 0.75
  
  # Nigerian bonus
  nigerian:
    enabled: true
    bonus_score: 0.15

# Retraining triggers
retraining:
  thresholds:
    min_training_ready_items: 50
  timing:
    min_hours_between_training: 24
  cost:
    max_daily_usd: 50.0
```

## 🎯 State-of-the-Art Models

**We use the BEST models - NOT wav2lip!**

| Modality | Model | Quality |
|----------|-------|---------|
| Video | ByteDance Omni-Human | Production |
| Voice | MiniMax Speech-02-HD | Production |
| Voice Clone | XTTS-v2 | High |
| Image | SeeDream-3 | Highest |
| Image (Fast) | Flux Schnell | Fast |
| LLM | Qwen 2.5 | Production |

## 🔄 Complete Flow Example

```python
import asyncio
from orchestrator import FeedbackLoopOrchestrator

async def main():
    # Initialize
    orchestrator = FeedbackLoopOrchestrator()
    
    # 1. User generates content via Replicate
    # (Replicate sends webhook to our server)
    
    # 2. Webhook is processed
    await orchestrator.process_webhook(webhook_payload)
    
    # 3. Run curation to filter quality
    await orchestrator.run_curation_cycle()
    
    # 4. Check if training should trigger
    results = await orchestrator.check_training_triggers()
    
    # 5. If triggered, Modal runs training
    # 6. Better models are deployed back to Replicate
    # 7. Loop continues!
    
    print("✅ Feedback loop complete!")

asyncio.run(main())
```

## 🛡️ Error Handling

The system is designed to be resilient:

- ✅ Graceful component fallbacks
- ✅ Automatic retry for API calls
- ✅ PII detection and redaction
- ✅ Duplicate detection
- ✅ Cost limits to prevent overruns
- ✅ Detailed logging

## 📈 Metrics

Available at `/metrics`:

- `feedback_total` - Total feedback items
- `feedback_quality_avg` - Average quality score
- `training_runs_total` - Total training runs
- `training_cost_daily` - Daily training cost

---

**Made with 💜 for Nigerian AI**

*Sisi Lola - Your AI Sister from Lagos*
