# HeyGen Custom Voice Upload Guide

## Package Contents
- 10 voice samples (text files)
- Diverse mix: Yoruba, Yorunglish, Pidgin, Professional

## Upload Steps

### 1. Access HeyGen Dashboard
- Go to: https://app.heygen.com
- Navigate to: Voice Library → Custom Voices

### 2. Upload Voice Samples
- Click "Create Custom Voice"
- Upload all voice_sample_*.txt files
- Or record audio for each sample

### 3. Voice Configuration
- **Name:** Sisi Lola - Yoruba Lagos Female
- **Language:** Yoruba (yo-NG) / Nigerian English
- **Gender:** Female
- **Age:** Young Adult (25-35)
- **Accent:** Lagos/Southwestern Nigerian
- **Style:** Conversational, Engaging, Spontaneous

### 4. Voice Characteristics
- **Tone:** Warm, authentic, energetic
- **Pace:** Natural, with emphasis on key phrases
- **Code-switching:** Yoruba + English + Pidgin
- **Personality:** Young urban host, pop culture aware

### 5. Training (Pro Plan Required)
- Submit for training
- Wait 24-48 hours for processing
- Test voice with sample scripts

### 6. After Training
- Copy new voice_id from HeyGen
- Update .env file:
  ```
  HEYGEN_VOICE_ID=<new_custom_voice_id>
  ```
- Test with: `python generate_first_video.py`

## Voice Sample Categories

1. **Yoruba Pure** (3 samples)
   - Traditional greetings and phrases
   - Cultural authenticity

2. **Yorunglish** (4 samples)
   - Code-switching Yoruba + English
   - Natural Lagos speech pattern

3. **Pidgin Heavy** (2 samples)
   - Nigerian Pidgin English
   - Relatable, spontaneous

4. **Professional** (1 sample)
   - Clear, articulate English
   - Formal content delivery

## Quality Checklist
- [ ] All samples uploaded
- [ ] Voice name set correctly
- [ ] Language configured (yo-NG)
- [ ] Gender set to Female
- [ ] Training submitted
- [ ] Voice ID copied to .env
- [ ] Test generation successful

## Support
- HeyGen Support: support@heygen.com
- Documentation: https://docs.heygen.com

---
Generated: c:\Users\POK28\Dropbox\Sisi_Lola
Platform: HeyGen Custom Voice Training
