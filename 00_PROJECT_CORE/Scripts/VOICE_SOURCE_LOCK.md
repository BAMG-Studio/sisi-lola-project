# VOICE SOURCE LOCK - PRODUCTION STANDARD

**Date**: 2025-12-06  
**Status**: LOCKED

---

## APPROVED VOICE SOURCE

**File**: `04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav`

**Specifications**:
- Duration: 5-7 minutes
- Language: 60% Yoruba, 30% Nigerian Pidgin, 10% English
- Accent: Natural Nigerian-British
- Quality: Production-ready
- Format: WAV, 44.1kHz

---

## NAMING CONVENTION

All production voice files MUST follow:
```
sisi_lola_yorunglish_female_[DESCRIPTOR].wav
```

Examples:
- `sisi_lola_yorunglish_female_LONG.wav` ✅ (APPROVED)
- `sisi_lola_yorunglish_female_SHORT.wav` ✅
- `sisi_lola_yorunglish_female_INTRO.wav` ✅

---

## PRODUCTION PIPELINE LOCK

All scripts MUST use this path:
```python
VOICE_SOURCE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
```

**DO NOT USE**:
- ❌ Placeholder WAV files
- ❌ Test samples
- ❌ Generic TTS output
- ❌ Old recordings

---

## AVATAR SOURCE LOCK

**HeyGen Avatar ID**: `046a63da7b20403c8c6bb51dbda12f65`

**Exported Frame Path** (for Wav2Lip):
```python
AVATAR_FRAME = "../../01_AVATAR_DNA/sisi_lola_heygen_frame.jpg"
```

**Specifications**:
- Resolution: 1920x1080 (will be resized for Wav2Lip)
- Format: JPG
- Source: HeyGen custom Sisi Lola model
- Style: Front-facing, professional, 2-piece ankara

---

## VALIDATION CHECKLIST

Before ANY video generation:
- [ ] Voice file exists at locked path
- [ ] Voice file is 5+ minutes duration
- [ ] Avatar frame exported from HeyGen
- [ ] Avatar shows Sisi Lola in ankara attire
- [ ] No placeholder or test files used

---

**LOCKED BY**: Production Pipeline  
**APPROVED BY**: User Requirement  
**ENFORCEMENT**: All generation scripts must validate these paths before execution
