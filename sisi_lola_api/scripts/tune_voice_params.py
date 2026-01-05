#!/usr/bin/env python3
"""
=============================================================================
🎛️ ELEVENLABS VOICE TUNER
=============================================================================
Generates 4 variations of a short phrase with different settings
to find the "Sweet Spot" for Sisi Lola's Nigerian accent.
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_models" / "tuning_tests"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# Voice ID from previous step - Attempt to load from saved file
def get_voice_id():
    id_file = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_models" / "elevenlabs_voice_id.txt"
    if id_file.exists():
        return id_file.read_text().strip()
    return "e3EHR2GS90EO276k1OCA" # Fallback

VOICE_ID = get_voice_id()
API_KEY = os.getenv("ELEVENLABS_API_KEY")

TEST_PHRASE = "Ah! How far my people? Una do well o. Lagos traffic today make me tire, but we move!"

SETTINGS_VARIATIONS = {
    "A_Balanced":       {"stability": 0.50, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True},
    "B_HighExpression": {"stability": 0.35, "similarity_boost": 0.80, "style": 0.5, "use_speaker_boost": True},
    "C_OverTheTop":     {"stability": 0.30, "similarity_boost": 0.90, "style": 0.8, "use_speaker_boost": True},
    "D_Stable_Clear":   {"stability": 0.70, "similarity_boost": 0.50, "style": 0.0, "use_speaker_boost": True},
}

def generate_variation(name, settings):
    print(f"⏳ Generating Variation: {name}...")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": TEST_PHRASE,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": settings
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        filename = OUTPUT_FOLDER / f"test_{name}.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"   ✅ Saved: {filename.name}")
    else:
        print(f"   ❌ Failed: {response.text}")

def main():
    print("============================================================")
    print("🎛️ SISI LOLA VOICE TUNER - Generating 4 Variations")
    print("============================================================")
    print(f"📝 Phrase: '{TEST_PHRASE}'\n")

    for name, settings in SETTINGS_VARIATIONS.items():
        generate_variation(name, settings)

    print("\n🎉 DONE! Check the folder: 03_MEDIA_ASSETS/voice_models/tuning_tests")
    print("👉 Listen to A, B, C, D and tell me which one sounds best!")

if __name__ == "__main__":
    main()
