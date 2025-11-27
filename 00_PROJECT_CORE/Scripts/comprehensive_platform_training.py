#!/usr/bin/env python3
"""
Comprehensive Platform Training for Sisi Lola
Trains voice across HeyGen, Google AI Studio, ElevenLabs, and all platforms
"""
import os
import json
from pathlib import Path
from yoruba_tts_engine import SisiLolaVoiceEngine

OUTPUT_DIR = Path(__file__).parent.parent / 'trained_models' / 'platform_training'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Comprehensive training phrases (Yoruba + Yorunglish + Pidgin)
TRAINING_CORPUS = {
    'yoruba_pure': [
        "Ẹ káàbọ̀! Mo ni Sisi Lola.",
        "Báwo ni? Ṣé àlàáfíà ni?",
        "Àwa ọmọ Yorùbá, a ní àṣà tó dára púpọ̀.",
        "Ẹ gbọ́ ọ̀rọ̀ yìí dáadáa.",
        "Àṣà wa ni! Ẹ jẹ́ ká ṣe àjọyọ̀ rẹ̀.",
        "Ẹ ṣeun gan-an! Má ríi yín lọ́la.",
        "Ó dára púpọ̀! Ẹ wò ó!",
        "Àwa ló máa ṣe é! Áfríkà tó ń bọ̀ yìí máa dára.",
        "Ẹ subscribe sí channel mi o!",
        "Ẹ má gbàgbé láti like àti share."
    ],
    'yorunglish': [
        "Hello everybody! Ẹ káàbọ̀! Welcome to my channel!",
        "I am Sisi Lola and I dey very happy say you come here today!",
        "Make I tell you small story about our culture.",
        "Àṣà wa, our culture, e get plenty things wey dey make am special.",
        "E choke! This one sweet me die!",
        "Ẹ gbọ́ ọ̀rọ̀ yìí: innovation tí ó wà ní Áfríkà kò lẹ́gbẹ́!",
        "We go do am! Àwa ló máa ṣe é!",
        "Subscribe and join the Sisi Lola family!",
        "Thank you plenty! Ẹ ṣeun gan-an!",
        "Let's celebrate Africa together! Ẹ jẹ́ ká ṣe àjọyọ̀!"
    ],
    'pidgin_heavy': [
        "Wetin dey happen? How una dey?",
        "Make we talk about African innovation today.",
        "This thing sweet me die! E choke!",
        "You know say M-Pesa start from Africa?",
        "We dey here, we dey strong!",
        "No be small thing! African culture na something else!",
        "Make una subscribe o! E no cost anything!",
        "I swear, this one pass me!",
        "We go do am! Nothing fit stop us!",
        "One love! Ubuntu! We dey together!"
    ],
    'professional': [
        "Welcome to Sisi Lola's channel, your guide to African culture and innovation.",
        "Today, we explore the rich tapestry of African heritage.",
        "African innovation is transforming the global landscape.",
        "From fintech to fashion, Africa is leading the way.",
        "Subscribe for weekly insights into African excellence.",
        "Join our community of cultural ambassadors.",
        "Let's celebrate the diversity and creativity of Africa.",
        "Thank you for being part of this journey.",
        "Together, we amplify African voices.",
        "Stay connected for more inspiring content."
    ]
}

def generate_platform_training_data():
    """Generate training data for all platforms"""
    print("=" * 60)
    print("COMPREHENSIVE PLATFORM TRAINING")
    print("=" * 60)
    
    engine = SisiLolaVoiceEngine()
    
    platforms = {
        'heygen': {
            'format': 'text',
            'max_length': 500,
            'voice_style': 'conversational'
        },
        'google_ai_studio': {
            'format': 'ssml',
            'speaker': 'KORE',
            'language': 'yo-NG'
        },
        'elevenlabs': {
            'format': 'text',
            'voice_id': '21m00Tcm4TlvDq8ikWAM',
            'model': 'eleven_multilingual_v2'
        },
        'youtube': {
            'format': 'captions',
            'language': 'yo'
        },
        'tiktok': {
            'format': 'short_form',
            'max_duration': 60
        },
        'instagram': {
            'format': 'short_form',
            'max_duration': 90
        }
    }
    
    results = {}
    
    for platform, config in platforms.items():
        print(f"\n[PLATFORM] {platform.upper()}")
        platform_dir = OUTPUT_DIR / platform
        platform_dir.mkdir(exist_ok=True)
        
        platform_samples = []
        
        # Generate samples for each category
        for category, phrases in TRAINING_CORPUS.items():
            print(f"  [CATEGORY] {category}: {len(phrases)} phrases")
            
            for i, phrase in enumerate(phrases, 1):
                # Generate audio
                audio_path = platform_dir / f'{category}_{i:02d}.wav'
                try:
                    engine.generate_speech(phrase, audio_path)
                    
                    platform_samples.append({
                        'id': f'{platform}_{category}_{i:02d}',
                        'text': phrase,
                        'category': category,
                        'audio': str(audio_path),
                        'platform_config': config
                    })
                except Exception as e:
                    print(f"    [ERROR] {phrase[:30]}...: {e}")
        
        # Save platform manifest
        manifest_path = platform_dir / 'training_manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(platform_samples, f, indent=2, ensure_ascii=False)
        
        results[platform] = {
            'samples': len(platform_samples),
            'manifest': str(manifest_path),
            'config': config
        }
        
        print(f"  [OK] {len(platform_samples)} samples generated")
    
    return results

def create_heygen_upload_package():
    """Create HeyGen voice upload package"""
    print("\n[HEYGEN] Creating voice upload package...")
    
    heygen_upload = OUTPUT_DIR / 'heygen_voice_upload'
    heygen_upload.mkdir(exist_ok=True)
    
    # Select best samples for voice cloning (diverse, clear, representative)
    upload_samples = [
        ("yoruba_pure", "Ẹ káàbọ̀! Mo ni Sisi Lola."),
        ("yorunglish", "Hello everybody! Ẹ káàbọ̀! Welcome to my channel!"),
        ("yorunglish", "I am Sisi Lola and I dey very happy say you come here today!"),
        ("pidgin_heavy", "Make we talk about African innovation today."),
        ("yoruba_pure", "Àwa ọmọ Yorùbá, a ní àṣà tó dára púpọ̀."),
        ("yorunglish", "E choke! This one sweet me die!"),
        ("professional", "Welcome to Sisi Lola's channel, your guide to African culture and innovation."),
        ("pidgin_heavy", "We dey here, we dey strong!"),
        ("yoruba_pure", "Ẹ ṣeun gan-an! Má ríi yín lọ́la."),
        ("yorunglish", "Let's celebrate Africa together! Ẹ jẹ́ ká ṣe àjọyọ̀!")
    ]
    
    for i, (category, text) in enumerate(upload_samples, 1):
        sample_file = heygen_upload / f'voice_sample_{i:02d}.txt'
        sample_file.write_text(text, encoding='utf-8')
    
    # Create upload instructions
    instructions = heygen_upload / 'HEYGEN_UPLOAD_GUIDE.md'
    with open(instructions, 'w', encoding='utf-8') as f:
        f.write(f"""# HeyGen Custom Voice Upload Guide

## Package Contents
- {len(upload_samples)} voice samples (text files)
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
Generated: {Path(__file__).parent.parent.parent}
Platform: HeyGen Custom Voice Training
""")
    
    print(f"[OK] {len(upload_samples)} samples ready")
    print(f"[INFO] Location: {heygen_upload}")
    
    return heygen_upload

if __name__ == '__main__':
    # Generate training data for all platforms
    results = generate_platform_training_data()
    
    # Create HeyGen upload package
    heygen_pkg = create_heygen_upload_package()
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] Platform training complete!")
    print("=" * 60)
    print(f"Platforms: {len(results)}")
    print(f"Total samples: {sum(r['samples'] for r in results.values())}")
    print(f"\nHeyGen upload package: {heygen_pkg}")
    print("\nNext steps:")
    print("1. Upload voice samples to HeyGen")
    print("2. Configure Google AI Studio KORE voice")
    print("3. Train ElevenLabs custom voice")
    print("4. Deploy to YouTube, TikTok, Instagram")
