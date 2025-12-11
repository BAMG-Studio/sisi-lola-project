# Voice Dataset Download Status

## Summary

Voice datasets have been downloaded from Google's FLEURS dataset for Nigerian language voice training.

## Downloaded Data

### FLEURS Yoruba (yo_ng)
- **Female samples**: 55
- **Male samples**: 45  
- **Total duration**: ~25 minutes
- **Status**: ✅ Complete

### FLEURS Hausa (ha_ng)
- **Status**: ⏳ Pending (dataset download may be slow)

### FLEURS Igbo (ig_ng)
- **Status**: ⏳ Pending (dataset download may be slow)

## Speaker Reference Candidates

15 top-quality female Yoruba voice samples have been selected for Sisi Lola voice cloning:

| Rank | File | Duration | Quality Score |
|------|------|----------|---------------|
| 1 | candidate_01_fleurs_yoruba_15.1s_q0.55.wav | 15.1s | 0.55 |
| 2 | candidate_02_fleurs_yoruba_11.4s_q0.54.wav | 11.4s | 0.54 |
| 3 | candidate_03_fleurs_yoruba_18.1s_q0.52.wav | 18.1s | 0.52 |
| 4-15 | Various | 10.8s-18.0s | 0.48-0.49 |

**Location**: `ml_training/data/voice_samples/speaker_reference_candidates/`

## Selection Criteria

Samples were scored based on:
- **Duration**: 10-30 seconds (optimal for XTTS voice cloning)
- **Silence ratio**: Lower silence = better score
- **Volume level**: Adequate volume for clear speech
- **Quality score**: Combined metric (0-1 scale)

## Next Steps

1. **Listen to candidates**: Review the 15 speaker reference candidates
2. **Select best voice**: Choose the voice that best represents Sisi Lola's personality
3. **Create speaker_reference.wav**: Copy selected candidate as `speaker_reference.wav`
4. **Train XTTS model**: Use the reference audio in Modal voice training

## Scripts Created

- `download_fleurs.py` - Downloads FLEURS Nigerian language datasets
- `create_speaker_reference.py` - Creates speaker reference candidates
- `run_voice_download.bat` - Windows batch file for download

## Dataset Sources

- **FLEURS**: Google's multilingual speech dataset
  - High-quality recordings
  - Gender-labeled
  - Multiple Nigerian languages (Yoruba, Hausa, Igbo)
  - HuggingFace: `google/fleurs`

## Audio Specifications

- Sample rate: 22050 Hz (resampled for XTTS compatibility)
- Format: WAV
- Channels: Mono
