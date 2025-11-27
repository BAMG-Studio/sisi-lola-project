# SISI LOLA - MULTILINGUAL VOICE ENGINE ARCHITECTURE
**Project:** Natural Multi-Language & Accent System  
**Version:** 1.0  
**Date:** November 24, 2025  
**Status:** Architecture Design Phase

---

## EXECUTIVE SUMMARY

This document outlines the technical architecture for transforming Sisi Lola from a single-language ElevenLabs-based TTS system into a **cross-lingual, accent-preserving, code-switching voice engine** capable of maintaining vocal identity across Yoruba, English, Italian, Swahili, Hausa, Igbo, and other African languages.

**Key Innovation:** Unlike generic TTS that uses different voices per language, Sisi Lola will speak Italian with her Nigerian vocal timbre, seamlessly code-switch between Yoruba and English mid-sentence, and maintain emotional prosody across all languages.

---

## CURRENT STATE ANALYSIS

### Existing Infrastructure (ElevenLabs-Based)
```
Current Pipeline:
Text Input → Perplexity Accent Localization → ElevenLabs TTS → Audio Output

Strengths:
✓ High-quality voice synthesis
✓ Good English prosody
✓ Nigerian accent localization via Perplexity
✓ Professional-grade audio output

Limitations:
✗ Single voice per language (no cross-lingual timbre preservation)
✗ Limited code-switching (Yoruba/English mixing)
✗ Cannot speak Italian/Swahili with Nigerian accent
✗ No fine-grained control over prosody
✗ Expensive at scale
```

### Voice Sample Inventory
**Location:** `04_AUDIO_CORE/01_Voice_Samples/`
```
10 Prepared Scripts:
- Professional Introduction (formal English)
- Casual Conversational (relaxed English)
- Nigerian Pidgin Authentic (code-switching)
- Excited Announcement
- Thoughtful Analysis
- Humorous Anecdote
- Empathetic Support
- Call to Action
- Tech Review Intro
- Meditation/ASMR

Status: Text scripts ready, awaiting voice actor recording
```

---

## PROPOSED ARCHITECTURE: THE "SISI LOLA VOICE ENGINE"

### Three-Tier System

```
┌─────────────────────────────────────────────────────────────┐
│                   TIER 1: BRAIN (NLU)                       │
│  Aya 101 / AfroLM + GPT-4 (Multilingual Understanding)     │
│  ↓ Detects language, intent, emotion, code-switching       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               TIER 2: VOICE ENGINE (TTS)                    │
│  Coqui XTTS v2 (Cross-Lingual Voice Cloning)              │
│  ↓ Generates speech with Sisi Lola's timbre in any lang   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 TIER 3: EARS (ASR)                          │
│  Fine-Tuned Whisper v3 (Code-Switching Recognition)       │
│  ↓ Understands Nigerian-accented speech & Yorunglish      │
└─────────────────────────────────────────────────────────────┘
```

---

## TIER 2 DEEP DIVE: COQUI XTTS V2 INTEGRATION

### Why Coqui XTTS v2?

| Feature | ElevenLabs | Coqui XTTS v2 |
|---------|------------|---------------|
| **Cross-Lingual Voice Cloning** | ❌ No (different voices per language) | ✅ Yes (same timbre across 13+ languages) |
| **Code-Switching (Yoruba+English)** | ⚠️ Limited | ✅ Native support |
| **Fine-Tuning on Custom Accent** | ❌ No | ✅ Yes (train on Nigerian accent) |
| **Offline/Local Deployment** | ❌ Cloud only | ✅ Self-hosted |
| **Cost at Scale** | 💰 Expensive ($0.30/1K chars) | 💰 Free (GPU cost only) |
| **Yoruba Language Support** | ⚠️ Via phonetic tricks | ✅ Direct support |
| **Emotional Prosody Control** | ⚠️ Limited | ✅ Fine-grained |

**Decision:** Hybrid approach initially, migrate to XTTS for production.

---

## IMPLEMENTATION ROADMAP

### PHASE 1: DATA COLLECTION & VOICE CLONING (Weeks 1-2)

#### Step 1.1: Record "Lola Source" Voice Actor
**Goal:** Capture 3-5 hours of high-quality Nigerian-accented audio

**Recording Specs:**
- **Format:** 48kHz, 24-bit WAV (mono)
- **Environment:** Professional studio (or treated space)
- **Microphone:** Neumann TLM 103 or equivalent
- **Voice Talent:** Nigerian woman, Yoruba speaker, age 28-40

**Recording Schedule:**
```
Session 1 (2 hours): 
  - 10 prepared scripts (varied emotions)
  - 30 mins Yoruba proverbs
  - 30 mins Nigerian Pidgin conversation
  - 30 mins code-switching samples

Session 2 (2 hours):
  - Technical content (AI, tech, business)
  - Conversational English (neutral accent)
  - Emotional range (happy, sad, excited, thoughtful)

Session 3 (1 hour):
  - Whispered speech (ASMR)
  - Energetic/hype delivery
  - Formal presentation style
```

**Scripts Location:** Already prepared in `04_AUDIO_CORE/01_Voice_Samples/`

#### Step 1.2: ElevenLabs Voice Cloning (Quick Win)
**Immediate Action (This Week):**
```bash
# 1. Record 1 minute of high-quality audio (professional intro script)
# 2. Upload to ElevenLabs Voice Lab
# 3. Train custom Sisi Lola voice
# 4. Replace VOICE_ID in config.py
# 5. Test with existing /audio/speak endpoint
```

**Current VOICE_ID:** `21m00Tcm4TlvDq8ikWAM` (Rachel - placeholder)  
**New VOICE_ID:** `[Custom-Sisi-Lola-ID]` (after cloning)

---

### PHASE 2: COQUI XTTS V2 SETUP (Weeks 3-4)

#### Step 2.1: Environment Setup
```bash
# Create dedicated voice engine environment
cd sisi_lola_api
python -m venv venv_voice_engine
source venv_voice_engine/bin/activate  # WSL

# Install Coqui TTS
pip install TTS==0.22.0  # Latest stable with XTTS v2
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118  # GPU support

# Test installation
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "Hello, I'm Sisi Lola" \
    --speaker_wav sample_voice.wav \
    --language_idx en \
    --out_path test_output.wav
```

#### Step 2.2: Fine-Tuning on Nigerian Accent
**Dataset Structure:**
```
voice_training_data/
├── metadata.csv              # Text transcriptions
├── wavs/
│   ├── lola_0001.wav         # Professional intro
│   ├── lola_0002.wav         # Casual chat
│   ├── lola_0003.wav         # Nigerian Pidgin
│   └── ... (500-1000 clips)
└── yoruba/
    ├── yoruba_0001.wav
    ├── yoruba_0002.wav
    └── ... (Yoruba-specific)
```

**metadata.csv Format:**
```csv
filename|text|speaker_id|language
lola_0001|Hello and welcome. I'm Sisi Lola...|sisi_lola|en
lola_0003|Ah ah! Wetin dey happen?|sisi_lola|yo-en
yoruba_0001|Báwo ni? Ṣé àlàáfíà ni?|sisi_lola|yo
```

**Fine-Tuning Script:**
```python
# tools/train_sisi_lola_voice.py
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs

config = XttsConfig()
config.load_json("recipes/sisi_lola/config.json")

# Training args
config.batch_size = 4
config.num_epochs = 1000
config.num_speakers = 1  # Just Sisi Lola
config.languages = ["en", "yo", "it", "sw", "ha", "ig"]  # Target languages

# Start training
model = Xtts.init_from_config(config)
trainer = Trainer(
    TrainerArgs(),
    config,
    output_path="models/sisi_lola_xtts_v2/",
    model=model
)
trainer.fit()
```

**Expected Training Time:** 24-48 hours on RTX 3090 or A100

---

### PHASE 3: CODE-SWITCHING & MULTI-LANGUAGE PIPELINE (Weeks 5-6)

#### Step 3.1: Language Detection & Segmentation
**Problem:** Sisi Lola needs to detect when user code-switches  
**Example Input:** "Shey you understand this AI thing? It's not that deep oh!"  
**Required Output:** 
- Segment 1: "Shey you understand this AI thing?" → Yoruba-English mix
- Segment 2: "It's not that deep oh!" → Nigerian Pidgin English

**Solution: Multi-Model Detection**
```python
# app/utils/language_detector.py
import fasttext
from transformers import pipeline

class SisiLolaLanguageDetector:
    def __init__(self):
        # FastText for quick detection
        self.fasttext_model = fasttext.load_model('lid.176.bin')
        
        # Hugging Face for code-switching
        self.cs_detector = pipeline(
            "token-classification",
            model="microsoft/xlm-roberta-base"  # Fine-tune on Nigerian data
        )
    
    def detect_code_switching(self, text: str):
        """
        Returns:
        [
            {"text": "Shey you understand", "lang": "yo-en", "confidence": 0.89},
            {"text": "this AI thing?", "lang": "en", "confidence": 0.95},
            {"text": "oh!", "lang": "yo", "confidence": 0.82}
        ]
        """
        # Implementation using token classification
        tokens = self.cs_detector(text)
        return self._merge_segments(tokens)
```

#### Step 3.2: Prosody-Aware Text Processing
**Goal:** Ensure natural flow when switching languages

**Strategy:**
1. **Sentence Boundary Detection:** Don't break mid-thought
2. **Emotion Preservation:** Maintain excitement across language switch
3. **Rhythm Matching:** Ensure Nigerian cadence in all languages

```python
# app/utils/prosody_processor.py
class ProsodyProcessor:
    def __init__(self):
        self.yoruba_particles = ["oh", "sha", "sef", "na", "o"]
        self.emphasis_markers = ["!", "?", "..."]
    
    def apply_nigerian_prosody(self, text: str, target_lang: str):
        """
        If target_lang = "it" (Italian), inject Nigerian rhythm:
        
        Input:  "Buongiorno! Come stai?"
        Output: "Buongiorno oh! Come stai, abi?"
                (^ maintains Nigerian flavor)
        """
        # Light injection of Nigerian particles
        # Keep grammar correct but add cultural markers
        pass
```

---

### PHASE 4: AFRICAN LANGUAGE DATASETS (Weeks 7-8)

#### Required Datasets for Training

| Dataset | Language | Size | Use Case |
|---------|----------|------|----------|
| **MENYO-20k** | Yoruba-English | 20K parallel sentences | Fine-tuning NLU & TTS |
| **Lagos-NWU** | Nigerian English | 10 hours audio | ASR training for accent |
| **Fleurs** | Yoruba | 5 hours labeled | Pronunciation & prosody |
| **JW300** | Yoruba | 300K sentences | Grammar structure (use cautiously) |
| **NaijaNLP** | Nigerian Pidgin | 50K tweets/texts | Sentiment & slang |
| **MasakhaNER** | Hausa, Igbo, Yoruba | NER dataset | Named entity handling |
| **Swahili ALFFA** | Swahili | 11 hours | Swahili TTS/ASR |

**Download & Preparation Script:**
```bash
# tools/download_datasets.sh
#!/bin/bash

# Create datasets directory
mkdir -p datasets/african_languages

# MENYO-20k (Yoruba-English)
wget https://github.com/dadelani/menyo-20k_MT/archive/main.zip
unzip main.zip -d datasets/menyo20k

# Lagos-NWU (Nigerian English ASR)
git clone https://github.com/Speech-Lab-IITM/Lagos-NWU-conversational-speech-corpus
mv Lagos-NWU* datasets/lagos_nwu

# Fleurs (Yoruba subset)
pip install datasets
python -c "from datasets import load_dataset; \
           ds = load_dataset('google/fleurs', 'yo_ng'); \
           ds.save_to_disk('datasets/fleurs_yoruba')"

# NaijaNLP (Nigerian Pidgin)
git clone https://github.com/hausanlp/NaijaNLP
mv NaijaNLP datasets/naija_nlp
```

---

### PHASE 5: INTEGRATION & API ENDPOINTS (Week 9)

#### New API Structure
```
sisi_lola_api/
├── app/
│   ├── routers/
│   │   ├── audio.py                  # Existing (ElevenLabs)
│   │   ├── audio_v2.py               # NEW: XTTS-based
│   │   └── voice_training.py         # NEW: Training interface
│   ├── models/
│   │   ├── xtts_sisi_lola/          # Trained model weights
│   │   └── whisper_nigerian/        # Fine-tuned ASR
│   ├── utils/
│   │   ├── language_detector.py      # NEW
│   │   ├── prosody_processor.py      # NEW
│   │   └── code_switching.py         # NEW
└── datasets/                         # Training data
```

#### Updated API Endpoints

**1. Enhanced /audio/speak (Backward Compatible)**
```python
# POST /audio/speak
{
  "text": "Shey you dey feel this vibe? È rí gé!",
  "accent": "nigerian-yoruba",
  "languages": ["en", "yo"],          # NEW: Auto-detect if empty
  "engine": "elevenlabs",             # or "xtts"
  "code_switching": true,             # NEW: Enable seamless mixing
  "emotion": "excited"                # NEW: Prosody control
}

Response:
{
  "audio_base64": "...",
  "detected_languages": ["en", "yo"],
  "segments": [
    {"text": "Shey you dey feel this vibe?", "lang": "en-NG"},
    {"text": "È rí gé!", "lang": "yo"}
  ],
  "engine_used": "xtts_v2"
}
```

**2. New /audio/multilingual**
```python
# POST /audio/multilingual
{
  "text": "Good morning everyone",
  "target_languages": ["en", "yo", "it", "sw"],  # Speak in all 4
  "preserve_timbre": true,                        # Keep Sisi's voice
  "cultural_adaptation": "light"                  # Add local flavor
}

Response:
{
  "audio_files": {
    "en": "audio_base64_english",
    "yo": "audio_base64_yoruba",
    "it": "audio_base64_italian",  # Italian with Nigerian accent!
    "sw": "audio_base64_swahili"
  }
}
```

**3. New /audio/train (Voice Model Management)**
```python
# POST /audio/train/upload-sample
# Upload voice recordings for fine-tuning

# GET /audio/train/status
# Check training progress

# POST /audio/train/start
# Trigger fine-tuning job
```

---

## TECHNICAL SPECIFICATIONS

### Hardware Requirements

**Development/Testing:**
- CPU: 8+ cores
- RAM: 32GB
- GPU: NVIDIA RTX 3060 (12GB VRAM) minimum
- Storage: 100GB SSD

**Production:**
- GPU: NVIDIA A100 (40GB) or RTX 4090
- RAM: 64GB
- Storage: 500GB NVMe SSD
- Network: Low-latency inference (<500ms)

### Performance Benchmarks

| Metric | ElevenLabs (Current) | XTTS v2 (Target) |
|--------|---------------------|------------------|
| **Latency** | 2-4 seconds | 1-3 seconds (local) |
| **Quality (MOS)** | 4.2/5.0 | 4.0/5.0 |
| **Cost (1M characters)** | $300 | $50 (GPU) |
| **Languages Supported** | 28 | 13 (expandable) |
| **Custom Accent** | No | Yes |
| **Code-Switching** | No | Yes |

---

## VOICE QUALITY VALIDATION

### Testing Protocol

**1. Naturalness Test (MOS - Mean Opinion Score)**
- Record 20 samples in each language
- Blind listening test with 50+ participants
- Target Score: >4.0/5.0

**2. Accent Preservation Test**
- Generate Italian speech with Nigerian accent
- Compare to native Italian TTS
- Verify: "Should sound like Nigerian speaking Italian, not Italian native"

**3. Code-Switching Fluency Test**
- Generate 50 mixed Yoruba-English sentences
- Check for: Smooth transitions, no robotic pauses, natural prosody

**4. Emotional Range Test**
- Same text in 7 emotions: Happy, Sad, Excited, Calm, Angry, Thoughtful, Playful
- Verify distinct prosodic patterns

---

## RISK MITIGATION

### Potential Challenges & Solutions

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Insufficient Training Data** | High | Partner with Nigerian universities for recordings |
| **Yoruba Diacritics Handling** | Medium | Use Unicode normalization + custom preprocessing |
| **GPU Cost for Real-Time TTS** | High | Hybrid: XTTS for quality, ElevenLabs for fallback |
| **Accent Drift Over Time** | Medium | Version control models, A/B testing |
| **Code-Switching Edge Cases** | Low | Collect edge cases, retrain quarterly |

---

## COST ANALYSIS

### Year 1 Budget (USD)

**One-Time Costs:**
- Voice Actor Recording (3 sessions): $3,000
- GPU Server (RTX A6000): $5,000
- Dataset Licensing: $500
- **Subtotal:** $8,500

**Recurring Costs:**
- GPU Cloud (A100 80hrs/month): $240/month = $2,880/year
- ElevenLabs (Fallback, 500K chars/month): $120/month = $1,440/year
- Storage (500GB): $20/month = $240/year
- **Subtotal:** $4,560/year

**Total Year 1:** $13,060

**Break-Even vs. ElevenLabs Only:**
- ElevenLabs at scale (5M chars/month): $1,500/month = $18,000/year
- **Savings with XTTS:** $4,440/year (+ better quality)

---

## SUCCESS METRICS

### Phase 1 (Weeks 1-4)
- ✅ 5 hours of Sisi Lola voice recordings completed
- ✅ ElevenLabs custom voice cloned (MOS >4.0)
- ✅ XTTS v2 environment set up and tested

### Phase 2 (Weeks 5-8)
- ✅ Fine-tuned XTTS model (Nigerian accent preserved)
- ✅ Code-switching detection accuracy >85%
- ✅ Yoruba TTS quality matches English

### Phase 3 (Weeks 9-12)
- ✅ API endpoints deployed and documented
- ✅ Italian/Swahili synthesis with Nigerian timbre
- ✅ Production-ready inference (<2s latency)

---

## NEXT IMMEDIATE ACTIONS

### This Week (Priority 1)
1. **Record 1-minute ElevenLabs voice sample**
   - Use: `SCRIPT_professional_introduction.txt`
   - Equipment: Good USB microphone (Blue Yeti or better)
   - Environment: Quiet room (use blankets for dampening)

2. **Clone voice in ElevenLabs**
   - Upload to Voice Lab
   - Get new VOICE_ID
   - Update `sisi_lola_api/app/config.py`

3. **Test enhanced audio endpoint**
   ```bash
   # Update .env with ElevenLabs key
   # Run: python test_audio_generation.py
   ```

### Next Week (Priority 2)
4. **Set up XTTS v2 development environment**
   - Install dependencies
   - Download pre-trained model
   - Run baseline tests

5. **Prepare dataset download scripts**
   - Test MENYO-20k download
   - Verify Lagos-NWU access

### Week 3-4 (Priority 3)
6. **Schedule professional voice actor sessions**
   - Search: Nigerian voice talent on Fiverr/Voices.com
   - Budget: $1,000-$1,500 for quality recording

---

## RESOURCES & REFERENCES

### Code Repositories
- **Coqui TTS:** https://github.com/coqui-ai/TTS
- **XTTS v2 Docs:** https://docs.coqui.ai/en/latest/models/xtts.html
- **Whisper Fine-Tuning:** https://github.com/openai/whisper

### Datasets
- **MENYO-20k:** https://github.com/dadelani/menyo-20k_MT
- **Lagos-NWU:** https://github.com/Speech-Lab-IITM/Lagos-NWU
- **Fleurs (Yoruba):** https://huggingface.co/datasets/google/fleurs
- **NaijaNLP:** https://github.com/hausanlp/NaijaNLP

### Academic Papers
1. "XTTS: A Massively Multilingual Zero-Shot Text-to-Speech Model" (Coqui AI, 2023)
2. "Towards African Language NLP" (Masakhane Initiative, 2023)
3. "Code-Switching in Nigerian Pidgin" (Adegbite & Akindele, 2021)

---

## CONCLUSION

This architecture transforms Sisi Lola from a **monolingual TTS system** into a **culturally-aware, multilingual voice AI** that:

✅ Speaks Italian with a Nigerian accent (cross-lingual timbre)  
✅ Seamlessly mixes Yoruba and English mid-sentence  
✅ Understands code-switching in user input  
✅ Maintains emotional prosody across languages  
✅ Scales cost-effectively for production  

**Timeline:** 12 weeks to full deployment  
**Investment:** ~$13K Year 1  
**ROI:** Unique voice AI with no direct competitors in African language space  

---

**Document Owner:** Sisi Lola AI Team  
**Last Updated:** November 24, 2025  
**Next Review:** December 1, 2025
