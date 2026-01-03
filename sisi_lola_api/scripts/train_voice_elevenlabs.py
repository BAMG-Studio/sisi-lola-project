#!/usr/bin/env python3
"""
=============================================================================
🎙️ ELEVENLABS VOICE CLONING TOOL
=============================================================================
Clones Sisi Lola's voice using the best selected samples.
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_MODELS_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_models"
SAMPLES_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_samples" / "selected_best"

API_KEY = os.getenv("ELEVENLABS_API_KEY")

def clone_voice():
    print("============================================================")
    print("🎙️ ELEVENLABS VOICE CLONING: Sisi Lola")
    print("============================================================")
    
    if not API_KEY:
        print("❌ ELEVENLABS_API_KEY not found in .env!")
        return

    # 1. Collect Samples
    sample_files = list(SAMPLES_FOLDER.glob("*.wav"))
    if not sample_files:
        print(f"❌ No samples found in {SAMPLES_FOLDER}")
        return

    print(f"📁 Found {len(sample_files)} sample files.")
    
    # Limit to top 5 samples to avoid payload issues (ElevenLabs allows up to 25, but 5-10 is often optimal)
    selected_samples = sample_files[:10]
    
    files = {}
    for i, sample_path in enumerate(selected_samples):
        print(f"   Adding: {sample_path.name}")
        files[f'files'] = (sample_path.name, open(sample_path, 'rb'), 'audio/wav')
        
    # We need to send multiple files with the same key 'files'
    # Requests handles this if we pass a list of tuples
    files_payload = [
        ('files', (p.name, open(p, 'rb'), 'audio/wav')) for p in selected_samples
    ]

    data = {
        "name": "Sisi Lola (Authentic V5)",
        "description": "Authentic Nigerian English Female. Energetic, storytelling, warm, slightly pidgin.",
        "labels": '{"accent": "Nigerian", "gender": "Female", "age": "Young", "use_case": "Storytelling"}'
    }

    print("\n🚀 Uploading to ElevenLabs...")
    
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "xi-api-key": API_KEY
    }

    try:
        response = requests.post(url, headers=headers, data=data, files=files_payload)
        
        if response.status_code == 200:
            voice_id = response.json()['voice_id']
            print("\n🎉 SUCCESS! Voice Cloned.")
            print(f"   🆔 Voice ID: {voice_id}")
            print(f"   💾 Saved reference info to voice_models folder.")
            
            # Save ID for later use
            with open(VOICE_MODELS_FOLDER / "elevenlabs_voice_id.txt", "w") as f:
                f.write(voice_id)
                
            return voice_id
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    clone_voice()
