# N-ATLaS Model Setup Guide for Sisi Lola

## Model Information
- **Repository:** https://huggingface.co/NCAIR1/N-ATLaS
- **Languages:** 517 African languages
- **Priority:** Yoruba (yor_Latn)
- **Type:** Seq2Seq Translation Model

---

## Setup Steps

### 1. Request Access to N-ATLaS Model

1. Go to: https://huggingface.co/NCAIR1/N-ATLaS
2. Click **"Request Access"** button
3. Fill out the access request form
4. Wait for approval (usually 24-48 hours)

### 2. Get HuggingFace Access Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name: `sisi-lola-natlas`
4. Type: **Read**
5. Copy the token (starts with `hf_...`)

### 3. Authenticate HuggingFace CLI

```bash
# Install HuggingFace CLI
pip install huggingface_hub[cli]

# Login with your token
huggingface-cli login

# Paste your token when prompted
```

### 4. Clone N-ATLaS Repository

```bash
cd c:\Users\POK28\Dropbox\Sisi_Lola\00_PROJECT_CORE

# Clone the model
git clone https://huggingface.co/NCAIR1/N-ATLaS

# Or use HuggingFace Hub
huggingface-cli download NCAIR1/N-ATLaS
```

### 5. Update Training Script

Once you have access, the model will load automatically:

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# This will now work with authentication
tokenizer = AutoTokenizer.from_pretrained("NCAIR1/N-ATLaS")
model = AutoModelForSeq2SeqLM.from_pretrained("NCAIR1/N-ATLaS")
```

---

## Alternative: Use Existing Yoruba TTS (Current)

While waiting for N-ATLaS access, continue using:

```bash
# Current working system
python comprehensive_platform_training.py
```

This uses:
- Facebook MMS-TTS-YOR (already working)
- ElevenLabs (already configured)
- Google AI Studio KORE voice (configured)

---

## N-ATLaS Training Commands (After Access)

### Train on Yoruba Priority
```bash
python natlas_multilingual_trainer.py --language yor_Latn --priority high
```

### Train All African Languages
```bash
python natlas_multilingual_trainer.py --all-languages
```

### Export for Platforms
```bash
python natlas_multilingual_trainer.py --export heygen,google_ai,elevenlabs
```

---

## Supported Languages in N-ATLaS

### Priority for Sisi Lola:
1. **yor_Latn** - Yoruba (Latin script) ← PRIMARY
2. **eng_Latn** - English
3. **pcm_Latn** - Nigerian Pidgin
4. **ibo_Latn** - Igbo
5. **hau_Latn** - Hausa
6. **swa_Latn** - Swahili
7. **amh_Ethi** - Amharic
8. **fra_Latn** - French (West Africa)

### Additional African Languages (517 total):
- All major African languages
- Regional dialects
- Code-switching support

---

## Current Status

### ✅ Working Now (No N-ATLaS Required)
- Yoruba TTS (Facebook MMS)
- Yorunglish voice samples
- Platform training (HeyGen, Google AI, ElevenLabs)
- Voice samples generated (10+ samples)

### ⏳ Pending N-ATLaS Access
- 517 African language support
- Advanced multilingual training
- Cross-language voice synthesis
- Enhanced code-switching

---

## Troubleshooting

### Error: "Cannot access gated repo"
**Solution:** Request access at https://huggingface.co/NCAIR1/N-ATLaS

### Error: "401 Unauthorized"
**Solution:** Run `huggingface-cli login` with your token

### Error: "Model not found"
**Solution:** Wait for access approval, then re-run

---

## Next Steps

### Immediate (While Waiting for N-ATLaS)
1. ✅ Use existing Yoruba TTS system
2. ✅ Generate platform training samples
3. ✅ Upload voice samples to HeyGen
4. ✅ Configure Google AI Studio KORE voice

### After N-ATLaS Access
1. Re-run `natlas_multilingual_trainer.py`
2. Train on all 517 African languages
3. Export enhanced voice models
4. Deploy to all platforms

---

## Commands Summary

```bash
# Setup authentication
python setup_natlas_access.py
huggingface-cli login

# Request access (manual)
# Visit: https://huggingface.co/NCAIR1/N-ATLaS

# Current training (works now)
python comprehensive_platform_training.py

# N-ATLaS training (after access)
python natlas_multilingual_trainer.py
```

---

**Status:** Waiting for N-ATLaS access approval  
**Alternative:** Using Facebook MMS-TTS-YOR (fully functional)  
**Next:** Request access, authenticate, then train on 517 languages
