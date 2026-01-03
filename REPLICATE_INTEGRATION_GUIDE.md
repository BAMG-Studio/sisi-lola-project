# SISI LOLA - REPLICATE AI TOOLS INTEGRATION GUIDE
## One-Stop-Shop for All AI Capabilities

---

# REPLICATE OVERVIEW

Replicate is our **primary AI infrastructure provider**:
- ✅ Pay-per-use (no monthly subscriptions for GPU)
- ✅ 1000s of open-source AI models
- ✅ Production-ready APIs
- ✅ No Modal wahala!

---

# MODELS WE NEED FOR SISI LOLA

## 1. 🎙️ VOICE / TTS (Text-to-Speech)

### PRIMARY: minimax/speech-02-hd
- **Use Case**: High-quality voiceovers for videos
- **Features**: Emotional expression, natural prosody
- **Cost**: ~$0.015/1000 characters
- **Link**: https://replicate.com/minimax/speech-02-hd

### BACKUP: afiaka87/tortoise-tts
- **Use Case**: Open-source alternative
- **Features**: Slow but high quality
- **Link**: https://replicate.com/afiaka87/tortoise-tts

### VOICE CLONING: zsxkib/realistic-voice-cloning (RVC)
- **Use Case**: Clone authentic Nigerian voice from samples
- **Features**: Train on our downloaded voice samples
- **Process**: Upload samples → Train → Inference
- **Link**: https://replicate.com/zsxkib/realistic-voice-cloning

### ALTERNATIVE: lucataco/xtts-v2
- **Use Case**: Multilingual voice cloning
- **Features**: Clone voice in 6 seconds, 17 languages
- **Link**: https://replicate.com/lucataco/xtts-v2

---

## 2. 🎬 VIDEO GENERATION (Sisi Lola Moving/Talking)

### PRIMARY: bytedance/omni-human
- **Use Case**: Audio-driven realistic talking videos
- **Features**: Natural movement, expressions, professional quality
- **Input**: Image + Audio → Talking Video
- **Link**: https://replicate.com/bytedance/omni-human

### BACKUP: devxpy/cog-wav2lip
- **Use Case**: Lip-sync fallback
- **Features**: Fast, reliable lip-sync
- **Link**: https://replicate.com/devxpy/cog-wav2lip

### MOTION: stability-ai/stable-video-diffusion
- **Use Case**: Make static images move
- **Features**: Image-to-video with subtle motion
- **Link**: https://replicate.com/stability-ai/stable-video-diffusion

### FUTURE: Google Veo 3 (Coming May-July 2025)
- **Use Case**: High-quality video generation
- **Features**: 720p/1080p, 8 seconds, text-to-video
- **Status**: Not yet available

### FUTURE: Bytedance Seedance 1 Pro (Coming June 2025)
- **Use Case**: Advanced video generation
- **Features**: Up to 1080p, 5-10 seconds

---

## 3. 🖼️ IMAGE GENERATION

### PRIMARY: bytedance/seedream-3
- **Use Case**: Highest quality image generation
- **Features**: Best prompt following, visual quality
- **Link**: https://replicate.com/bytedance/seedream-3

### FAST: black-forest-labs/flux-schnell
- **Use Case**: Quick image generation (<2 seconds)
- **Link**: https://replicate.com/black-forest-labs/flux-schnell

### CUSTOMIZABLE: stability-ai/sdxl
- **Use Case**: Fine-tuned for specific styles (LoRA)
- **Features**: Train on Sisi Lola DNA images
- **Link**: https://replicate.com/stability-ai/sdxl

### TEXT-IN-IMAGE: ideogram-ai/ideogram-v3-turbo
- **Use Case**: Images with text/logos
- **Link**: https://replicate.com/ideogram-ai/ideogram-v3-turbo

### SVG/LOGOS: recraft-ai/recraft-v3-svg
- **Use Case**: Vector graphics, icons
- **Link**: https://replicate.com/recraft-ai/recraft-v3-svg

---

## 4. 📝 DOCUMENT PROCESSING (Immigration AI)

### OCR: abiruyt/text-extract-ocr
- **Use Case**: Extract text from passport, forms
- **Link**: https://replicate.com/abiruyt/text-extract-ocr

### PDF ANALYSIS: Use Gemini directly
- **Use Case**: Analyze legal documents
- **Features**: Long context window perfect for immigration forms

---

## 5. 🗣️ SPEECH-TO-TEXT (Voice Input)

### PRIMARY: openai/whisper
- **Use Case**: Transcribe Yoruba/Pidgin voice input
- **Features**: Multilingual, accurate
- **Link**: https://replicate.com/openai/whisper

---

# SISI LOLA WORKFLOW ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                               │
│  (Text, Voice, Document Upload)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    GEMINI 2.0 (Brain)                       │
│  - Conversation handling                                    │
│  - Long context for documents                               │
│  - Immigration knowledge                                    │
│  - Cultural understanding (Yorunglish)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    REPLICATE (Tools)                        │
├─────────────────────────────────────────────────────────────┤
│  Voice Generation   │  Video Generation  │  Image Gen      │
│  - minimax TTS      │  - OmniHuman       │  - Seedream-3   │
│  - Voice Cloning    │  - Wav2Lip         │  - FLUX         │
│  - XTTS-v2          │  - SVD             │  - SDXL         │
├─────────────────────────────────────────────────────────────┤
│  Document Processing │  Speech-to-Text                      │
│  - OCR               │  - Whisper                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT                                   │
│  - WhatsApp/Telegram Messages                               │
│  - Generated Videos (Social Media Content)                  │
│  - Filled Forms (PDF)                                       │
│  - Voice Messages (Audio)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

# ESTIMATED COSTS (Per Operation)

| Operation | Model | Est. Cost |
|-----------|-------|-----------|
| Generate Voice (1 min) | minimax/speech-02-hd | ~$0.10 |
| Clone Voice (training) | zsxkib/realistic-voice-cloning | ~$5.00 |
| Generate Talking Video (30s) | bytedance/omni-human | ~$0.50-1.00 |
| Lip Sync (30s) | devxpy/cog-wav2lip | ~$0.10-0.20 |
| Generate Image | bytedance/seedream-3 | ~$0.03 |
| Image to Video (4s) | stable-video-diffusion | ~$0.15 |
| Transcribe Audio (1 min) | openai/whisper | ~$0.01 |
| OCR Document | text-extract-ocr | ~$0.01 |

---

# IMPLEMENTATION PRIORITY

## Phase 1: Voice (THIS WEEK)
1. ✅ Download Nigerian voice samples (running now)
2. 🔲 Train voice clone on best female samples
3. 🔲 Test voice generation with Yorunglish scripts
4. 🔲 Integrate minimax TTS as backup

## Phase 2: Video (NEXT WEEK)
1. 🔲 Test OmniHuman with Sisi Lola DNA images
2. 🔲 Generate 3-minute talking videos
3. 🔲 Set up automated video production pipeline

## Phase 3: Full Integration (Week 3-4)
1. 🔲 WhatsApp Business API integration
2. 🔲 Voice input (Whisper) for Yoruba/Pidgin
3. 🔲 Document OCR for immigration forms
4. 🔲 Gemini multimodal pipeline

---

# REPLICATE API PATTERNS

## Basic Call Pattern
```python
import replicate

# Run a model
output = replicate.run(
    "bytedance/omni-human:version_id",
    input={
        "image": "data:image/jpeg;base64,{base64_image}",
        "audio": "data:audio/mpeg;base64,{base64_audio}"
    }
)
```

## Async Call Pattern (for long-running jobs)
```python
import replicate

# Create prediction
prediction = replicate.predictions.create(
    model="bytedance/omni-human",
    input={
        "image": image_url,
        "audio": audio_url
    }
)

# Poll for completion
while prediction.status not in ["succeeded", "failed", "canceled"]:
    prediction.reload()
    time.sleep(5)

# Get output
video_url = prediction.output
```

## Webhook Pattern (production)
```python
import replicate

# Create with webhook
prediction = replicate.predictions.create(
    model="bytedance/omni-human",
    input={...},
    webhook="https://sisi-lola-api.com/webhook/replicate",
    webhook_events_filter=["completed"]
)
```

---

# COMPARISON: REPLICATE vs MODAL vs OTHERS

| Feature | Replicate | Modal | HuggingFace |
|---------|-----------|-------|-------------|
| Pay-per-use | ✅ | ✅ | ✅ |
| Pre-built models | ✅ 1000s | ❌ DIY | ✅ Limited |
| Custom training | ✅ Easy | ✅ Advanced | ⚠️ Complex |
| African voice models | ✅ XTTS | ❌ | ⚠️ MMS-TTS (broken) |
| Video generation | ✅ Many | ❌ DIY | ⚠️ Limited |
| Reliability | ✅ High | ⚠️ Issues | ⚠️ Varies |
| API simplicity | ✅ Simple | ⚠️ Complex | ✅ Simple |
| Nigerian community | ✅ Growing | ❌ | ✅ Good |

**VERDICT: Replicate is our one-stop-shop** 🎯

---

# NEXT ACTIONS

1. **Voice Cloning Pipeline**
   - Select best Nigerian female voice samples
   - Train RVC model on Replicate
   - Test with Yorunglish scripts

2. **Video Production Pipeline**
   - Test OmniHuman with Sisi Lola images
   - Set up automated 3-minute video generation
   - Integrate with social media posting

3. **Immigration AI Pipeline**
   - Set up Whisper for voice input
   - Configure OCR for document processing
   - Build Gemini prompt templates for legal analysis

---

*Guide created December 2025*
*Replicate API Token: Already configured in scripts*
