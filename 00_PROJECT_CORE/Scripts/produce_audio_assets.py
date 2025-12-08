import os
import sys
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / "sisi_lola_api" / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MANIFEST_FILE = PROJECT_ROOT / "MASTER_ASSET_MANIFEST.csv"

def generate_audio_assets():
    print("🎙️ Starting Audio Asset Generation...")
    
    if not ELEVENLABS_API_KEY:
        print("❌ Error: ELEVENLABS_API_KEY not found in .env")
        return

    # Read manifest
    assets_to_generate = []
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category'] == '04_AUDIO_CORE' and row['Status'] == 'Pending Generation':
                assets_to_generate.append(row)
    
    print(f"Found {len(assets_to_generate)} pending audio assets.")
    
    for asset in assets_to_generate:
        print(f"\nProcessing: {asset['Filename']}")
        
        # Determine voice/model based on subcategory
        # For simplicity, we'll use a default voice for samples and sound generation for soundscapes if available
        # ElevenLabs is primarily TTS, but has sound generation too.
        
        output_path = PROJECT_ROOT / asset['Category'] / asset['Subcategory'] / asset['Filename']
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
             print(f"⏩ Skipping (File exists): {output_path}")
             continue

        try:
            if "Voice_Sample" in asset['Filename']:
                # Text-to-Speech Generation
                # We need a script. The prompt says "Voice recording: Sisi Lola speaking in..."
                # We'll generate a sample text based on the context.
                
                context = asset['Filename'].replace("Voice_Sample_", "").replace(".wav", "")
                text = f"Hello, this is Sisi Lola. I am speaking in a {context.replace('_', ' ')} tone. Welcome to the future of African storytelling."
                
                url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" # Default Rachel voice as placeholder if ID not in env
                # Check for specific voice ID in env
                voice_id = os.getenv("HEYGEN_VOICE_ID") # Using HeyGen voice ID might not work for ElevenLabs, check env
                # The .env has HEYGEN_VOICE_ID but not ELEVENLABS_VOICE_ID. 
                # We'll use a standard ID or the one from .env if it looks like an ElevenLabs ID.
                # ElevenLabs IDs are usually short strings.
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVENLABS_API_KEY
                }
                
                data = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
                
                response = requests.post(url, json=data, headers=headers)
                
            elif "Soundscape" in asset['Filename']:
                 # Sound Generation (ElevenLabs has a sound generation API now, or we skip)
                 print("⚠️  Soundscape generation requires specific model. Skipping for now.")
                 continue
            else:
                 print("⚠️  Unknown audio type. Skipping.")
                 continue

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Generated: {output_path}")
                # Update manifest status (in memory for now, or write back)
                # For production, we should update the CSV.
            else:
                print(f"❌ Failed: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n🏁 Audio Generation Complete.")

if __name__ == "__main__":
    generate_audio_assets()
