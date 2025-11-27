# SISI LOLA MULTILINGUAL VOICE ENGINE - IMPLEMENTATION GUIDE
**Quick Start Guide for Natural Multi-Language Voice**

## 🎯 IMMEDIATE ACTIONS (This Week)

### 1. Test Current Code-Switching Detection (5 minutes)

```bash
cd sisi_lola_api/app/utils

# Test language detector
python language_detector.py

# Expected output: Language detection for mixed Yoruba/English
```

### 2. Test Prosody Injection (5 minutes)

```bash
# Test prosody processor
python prosody_processor.py

# Expected output: Italian/Swahili with Nigerian flavor
```

### 3. Clone Sisi Lola's Voice in ElevenLabs (30 minutes)

**Steps:**
1. **Record 1-minute sample:**
   ```
   Equipment: Good USB microphone (Blue Yeti or similar)
   Script: Use 04_AUDIO_CORE/01_Voice_Samples/SCRIPT_professional_introduction.txt
   
   Tips:
   - Quiet room (use blankets/pillows to dampen echo)
   - Speak naturally, warm tone
   - Record in WAV format (48kHz)
   ```

2. **Upload to ElevenLabs:**
   - Go to: https://elevenlabs.io/voice-lab
   - Click "Add Voice" → "Instant Voice Cloning"
   - Upload your 1-minute recording
   - Name it: "Sisi Lola - Original"
   - Get the Voice ID (e.g., `abc123xyz...`)

3. **Update API configuration:**
   ```python
   # Edit: sisi_lola_api/app/config.py
   
   VOICE_ID = "YOUR_NEW_VOICE_ID"  # Replace with cloned voice ID
   ```

4. **Test the voice:**
   ```bash
   cd sisi_lola_api
   python test_audio_generation.py
   
   # Listen to: assets/generated/audio/test_sisi_lola_intro.mp3
   ```

---

## 📚 WEEK 1-2: Enhanced API Testing

### Enable the V2 Audio Endpoint

**1. Update main.py to include audio_v2 router:**

```python
# Edit: sisi_lola_api/app/main.py

from app.routers import chat, images, videos, agent, audio, audio_v2

app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(audio_v2.router, prefix="/audio/v2", tags=["audio-v2"])  # ADD THIS
```

**2. Restart the API server:**

```bash
cd sisi_lola_api
source venv/bin/activate  # WSL
uvicorn app.main:app --reload
```

**3. Test enhanced features:**

```bash
# Test 1: Code-switching detection
curl -X POST "http://localhost:8000/audio/v2/speak" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Shey you understand this AI thing? È rí gé oh!",
    "code_switching": true,
    "emotion": "excited"
  }'

# Test 2: Multi-language with prosody
curl -X POST "http://localhost:8000/audio/v2/speak" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ciao bella! Come stai oggi?",
    "languages": ["it"],
    "accent": "nigerian-yoruba"
  }'

# Test 3: Get status
curl "http://localhost:8000/audio/v2/"
```

---

## 🔬 WEEK 3-4: XTTS V2 Setup (Advanced)

### Install Coqui TTS

```bash
cd sisi_lola_api

# Create separate environment for voice engine
python -m venv venv_voice_engine
source venv_voice_engine/bin/activate

# Install XTTS dependencies
pip install TTS==0.22.0
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Test installation
tts --list_models

# Expected: See 'tts_models/multilingual/multi-dataset/xtts_v2' in list
```

### Test Zero-Shot Voice Cloning (No Training)

```bash
# Use your 1-minute ElevenLabs recording
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "Hello, I'm Sisi Lola speaking Italian with my Nigerian voice!" \
    --speaker_wav "path/to/sisi_lola_voice_sample.wav" \
    --language_idx "en" \
    --out_path test_xtts_english.wav

# Now test Italian (same voice!)
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "Ciao! Sono Sisi Lola!" \
    --speaker_wav "path/to/sisi_lola_voice_sample.wav" \
    --language_idx "it" \
    --out_path test_xtts_italian.wav

# Compare: Both should sound like the same person!
```

---

## 🎙️ WEEK 5-6: Voice Training Data Collection

### Option A: DIY Recording (Budget: $0-500)

**Equipment:**
- Blue Yeti USB Microphone ($130)
- Pop filter ($15)
- Boom arm + shock mount ($40)
- Room dampening (blankets/foam) ($50)

**Recording Schedule (3-5 hours total):**

```
Session 1 (2 hours): Emotional Range
- Use all 10 scripts in 04_AUDIO_CORE/01_Voice_Samples/
- Record each script 3 times (varied delivery)
- Total: 30 recordings × 30 seconds = 15 minutes

Session 2 (2 hours): Yoruba & Code-Switching
- Read Yoruba proverbs (collect 50 proverbs)
- Nigerian Pidgin conversations
- Code-switching examples (Yorunglish)
- Total: ~20 minutes of Yoruba-specific content

Session 3 (1 hour): Technical Content
- Read AI/tech articles in Nigerian accent
- Explain technical concepts casually
- Total: ~10 minutes
```

**Process recordings:**

```bash
cd 00_PROJECT_CORE/Scripts/voice_training

# Convert and segment recordings
python prepare_training_data.py \
  --input_dir "path/to/raw/recordings" \
  --output_dir "../../datasets/voice_training_data"

# Output: voice_training_data/
#   ├── wavs/ (500-1000 clips)
#   └── metadata.csv
```

### Option B: Professional Voice Actor (Budget: $1,000-1,500)

**Platforms:**
- Fiverr (search: "Nigerian voice actor")
- Voices.com
- Voice123

**Brief for voice actor:**
```
Need: 3-5 hours of high-quality voice recordings
Speaker: Nigerian woman, age 28-40, Yoruba speaker
Accent: Nigerian-British (Lagos to London spectrum)
Tone: Warm, authoritative, tech-savvy

Deliverables:
- 10 scripted recordings (varied emotions) - Provided
- 30 mins Yoruba speech (proverbs, conversation)
- 30 mins Nigerian Pidgin
- 30 mins code-switching examples
- 60 mins technical/professional content

Format: WAV, 48kHz, 24-bit, mono
Environment: Professional studio recording
```

---

## 🚀 WEEK 7-8: XTTS Fine-Tuning

### Download African Language Datasets

```bash
cd 00_PROJECT_CORE/Scripts/voice_training

# Make script executable
chmod +x download_datasets.sh

# Run download script
bash download_datasets.sh

# This downloads:
# - MENYO-20k (Yoruba-English)
# - Fleurs (Yoruba ASR)
# - MasakhaNER (Hausa, Igbo, Yoruba)
```

### Fine-Tune XTTS Model

```bash
# Coming soon: train_xtts_sisi_lola.py
# This will:
# 1. Load pre-trained XTTS v2
# 2. Fine-tune on Sisi Lola's voice samples
# 3. Train for Yoruba/Nigerian accent
# 4. Save custom model
```

---

## 📊 SUCCESS METRICS

### Phase 1: ElevenLabs Enhancement (Week 1-2)
- ✅ Custom Sisi Lola voice cloned (MOS >4.0)
- ✅ Code-switching detection working
- ✅ Nigerian prosody injection tested
- ✅ API v2 endpoints functional

### Phase 2: XTTS Setup (Week 3-4)
- ✅ XTTS environment installed
- ✅ Zero-shot cloning tested (multiple languages)
- ✅ Cross-lingual timbre verified

### Phase 3: Training (Week 5-8)
- ✅ 3-5 hours voice recordings collected
- ✅ Training data prepared (500+ clips)
- ✅ Fine-tuned model (Nigerian accent locked)
- ✅ Multi-language quality validated

---

## 🎯 EXPECTED RESULTS

### Before (Current ElevenLabs)
```
English: ✅ Natural
Yoruba: ⚠️ Generic accent, mispronunciation
Italian: ❌ Different voice, no Nigerian flavor
Code-switching: ⚠️ Awkward transitions
```

### After (XTTS + Training)
```
English: ✅ Natural, Nigerian accent
Yoruba: ✅ Native-sounding, correct tones
Italian: ✅ Same voice, Nigerian flavor ("Oh bella!")
Swahili: ✅ Same voice, Nigerian rhythm
Code-switching: ✅ Seamless (Yorunglish fluent)
```

---

## 🔧 TROUBLESHOOTING

### Issue: "ELEVENLABS_API_KEY not set"
```bash
# Create .env file in sisi_lola_api/
echo "ELEVENLABS_API_KEY=your_key_here" >> .env
```

### Issue: "Module 'TTS' not found"
```bash
# Install in voice engine environment
source venv_voice_engine/bin/activate
pip install TTS==0.22.0
```

### Issue: "CUDA out of memory" (XTTS training)
```bash
# Reduce batch size in training config
# Edit: config.json
"batch_size": 2  # Reduce from 4 to 2
```

### Issue: "Poor audio quality"
```bash
# Check input audio
python -c "
import librosa
import soundfile as sf

audio, sr = librosa.load('your_audio.wav', sr=None)
print(f'Sample rate: {sr}Hz')
print(f'Duration: {len(audio)/sr:.2f}s')
print(f'RMS: {np.sqrt(np.mean(audio**2)):.4f}')
"
# Target: sr=48000Hz, RMS=0.1-0.3
```

---

## 📞 NEXT STEPS

**Today:**
1. Test language_detector.py and prosody_processor.py
2. Record 1-minute voice sample
3. Clone voice in ElevenLabs

**This Week:**
4. Update API with new VOICE_ID
5. Test enhanced /audio/v2/speak endpoint
6. Validate code-switching detection

**Next 2 Weeks:**
7. Set up XTTS v2 environment
8. Test zero-shot voice cloning
9. Plan professional voice actor session

**Month 2:**
10. Collect 3-5 hours training data
11. Download African language datasets
12. Fine-tune XTTS model
13. Deploy production voice engine

---

**Questions? Check:**
- Architecture Doc: `00_PROJECT_CORE/Documentation/MULTILINGUAL_VOICE_ENGINE_ARCHITECTURE.md`
- Code Examples: `sisi_lola_api/app/utils/`
- Training Scripts: `00_PROJECT_CORE/Scripts/voice_training/`
