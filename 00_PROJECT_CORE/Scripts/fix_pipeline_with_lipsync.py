"""FIX PIPELINE: Add Lip-Sync with D-ID API (Immediate Solution)"""
import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")

# D-ID API (alternative to Wav2Lip, cloud-based, no GPU needed)
DID_API_KEY = "YOUR_DID_API_KEY"  # Get from https://studio.d-id.com
DID_API_URL = "https://api.d-id.com/talks"

def create_talking_video_did(image_path, audio_path, script_text):
    """Create talking video using D-ID API"""
    
    # Upload image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Upload audio
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    
    # Create talk
    headers = {
        "Authorization": f"Basic {DID_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "source_url": image_path,  # Or upload to cloud first
        "script": {
            "type": "audio",
            "audio_url": audio_path  # Or upload to cloud first
        },
        "config": {
            "fluent": True,
            "pad_audio": 0
        }
    }
    
    response = requests.post(DID_API_URL, json=payload, headers=headers)
    talk_id = response.json()['id']
    
    # Poll for completion
    while True:
        status_response = requests.get(f"{DID_API_URL}/{talk_id}", headers=headers)
        status = status_response.json()['status']
        
        if status == 'done':
            video_url = status_response.json()['result_url']
            return video_url
        elif status == 'error':
            raise Exception("D-ID video generation failed")
        
        time.sleep(5)

# IMMEDIATE WORKAROUND: Use HeyGen with Yoruba audio
def create_talking_video_heygen(script_text, audio_path):
    """Use HeyGen API with custom audio"""
    
    HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
    
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Upload audio to HeyGen
    with open(audio_path, 'rb') as f:
        audio_upload = requests.post(
            "https://api.heygen.com/v1/audio.upload",
            headers=headers,
            files={"file": f}
        )
    
    audio_id = audio_upload.json()['data']['audio_id']
    
    # Create video with custom audio
    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": os.getenv("HEYGEN_AVATAR_ID")
            },
            "voice": {
                "type": "audio",
                "audio_id": audio_id
            }
        }],
        "dimension": {
            "width": 1920,
            "height": 1080
        }
    }
    
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers=headers,
        json=payload
    )
    
    video_id = response.json()['data']['video_id']
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers=headers
        )
        
        status = status_response.json()['data']['status']
        
        if status == 'completed':
            video_url = status_response.json()['data']['video_url']
            return video_url
        elif status == 'failed':
            raise Exception("HeyGen video generation failed")
        
        time.sleep(10)

print("=" * 70)
print("LIP-SYNC PIPELINE FIX")
print("=" * 70)
print("\nOPTIONS:")
print("1. D-ID API ($0.30/video, cloud-based, no GPU)")
print("2. HeyGen with custom audio ($1/video, works now)")
print("3. Wav2Lip (free, requires GPU setup)")
print("\nRECOMMENDATION: Use HeyGen with custom Yoruba audio (Option 2)")
print("This gives lip-sync immediately while we set up Wav2Lip.")
