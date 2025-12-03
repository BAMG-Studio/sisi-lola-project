#!/usr/bin/env python3
"""
ElevenLabs Voice Cloning Automation
Upload voice samples and create custom Sisi Lola voice
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('sisi_lola_api/.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

def create_voice(name, description, voice_samples_dir):
    """Create custom voice from audio samples"""
    print(f"Creating voice: {name}")
    
    samples_path = Path(voice_samples_dir)
    audio_files = list(samples_path.glob('*.wav')) + list(samples_path.glob('*.mp3'))
    
    if not audio_files:
        print(f"Error: No audio files found in {voice_samples_dir}")
        return None
    
    print(f"Found {len(audio_files)} audio samples")
    
    # Prepare files for upload
    files = []
    for i, audio_file in enumerate(audio_files[:25]):  # Max 25 samples
        files.append(('files', (audio_file.name, open(audio_file, 'rb'), 'audio/mpeg')))
    
    data = {
        'name': name,
        'description': description,
        'labels': '{"use_case": "virtual_host", "character": "sisi_lola"}'
    }
    
    headers = {'xi-api-key': ELEVENLABS_API_KEY}
    
    try:
        response = requests.post(
            f"{ELEVENLABS_API_URL}/voices/add",
            headers=headers,
            data=data,
            files=files
        )
        
        if response.status_code == 200:
            voice_data = response.json()
            voice_id = voice_data.get('voice_id')
            print(f"✓ Voice created successfully!")
            print(f"  Voice ID: {voice_id}")
            print(f"  Name: {name}")
            
            # Save voice ID to config
            save_voice_id(voice_id)
            return voice_id
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error creating voice: {e}")
        return None
    finally:
        # Close file handles
        for _, file_tuple in files:
            file_tuple[1].close()

def save_voice_id(voice_id):
    """Save voice ID to .env file"""
    env_file = Path('sisi_lola_api/.env')
    
    with open(env_file, 'a') as f:
        f.write(f"\n# ElevenLabs Custom Voice\n")
        f.write(f"ELEVENLABS_SISI_LOLA_VOICE_ID={voice_id}\n")
    
    print(f"✓ Voice ID saved to .env")

def list_voices():
    """List all available voices"""
    headers = {'xi-api-key': ELEVENLABS_API_KEY}
    
    response = requests.get(f"{ELEVENLABS_API_URL}/voices", headers=headers)
    
    if response.status_code == 200:
        voices = response.json().get('voices', [])
        print(f"\nAvailable voices ({len(voices)}):")
        for voice in voices:
            print(f"  - {voice['name']} (ID: {voice['voice_id']})")
    else:
        print(f"Error listing voices: {response.status_code}")

def test_voice(voice_id, text="Hello! I'm Sisi Lola, your AI virtual host."):
    """Test generated voice"""
    print(f"\nTesting voice: {voice_id}")
    
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.75
        }
    }
    
    response = requests.post(
        f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        output_file = Path('api_customization/voice_cloning/test_output.mp3')
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✓ Test audio saved: {output_file}")
    else:
        print(f"Error testing voice: {response.status_code}")

def main():
    print("=" * 60)
    print("ELEVENLABS VOICE CLONING")
    print("=" * 60)
    
    if not ELEVENLABS_API_KEY:
        print("Error: ELEVENLABS_API_KEY not found in .env")
        return 1
    
    # Check for voice samples
    samples_dir = '04_AUDIO_CORE/01_Voice_Samples'
    
    if not Path(samples_dir).exists():
        print(f"Error: Voice samples directory not found: {samples_dir}")
        print("\nPlease add voice samples to this directory first.")
        return 1
    
    # Create voice
    voice_id = create_voice(
        name="Sisi Lola",
        description="Custom voice for Sisi Lola AI virtual host",
        voice_samples_dir=samples_dir
    )
    
    if voice_id:
        # Test the voice
        test_voice(voice_id)
        
        # List all voices
        list_voices()
        
        print("\n" + "=" * 60)
        print("VOICE CLONING COMPLETE!")
        print("=" * 60)
        print(f"Voice ID: {voice_id}")
        print("Use this ID in your API calls for Sisi Lola's voice")
        
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
