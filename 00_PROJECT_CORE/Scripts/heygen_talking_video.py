"""Generate Talking Video with HeyGen + Yoruba Voice - WORKS NOW"""
import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
VOICE_SAMPLE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
OUTPUT_DIR = "../../06_RENDER_OUTPUT/talking_videos"

def upload_audio_to_heygen(audio_path):
    """Upload Yoruba voice sample to HeyGen"""
    
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    
    with open(audio_path, 'rb') as f:
        files = {"file": f}
        response = requests.post(
            "https://api.heygen.com/v1/audio.upload",
            headers=headers,
            files=files
        )
    
    if response.status_code != 200:
        raise Exception(f"Audio upload failed: {response.text}")
    
    audio_id = response.json()['data']['audio_id']
    print(f"  Audio uploaded: {audio_id}")
    return audio_id

def create_talking_video(audio_id):
    """Create talking video with HeyGen"""
    
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": "Hada_Casual_Front_public"  # Using public avatar
            },
            "voice": {
                "type": "audio",
                "audio_id": audio_id
            }
        }],
        "dimension": {
            "width": 1920,
            "height": 1080
        },
        "aspect_ratio": "16:9"
    }
    
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"Video generation failed: {response.text}")
    
    video_id = response.json()['data']['video_id']
    print(f"  Video generation started: {video_id}")
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers=headers
        )
        
        status_data = status_response.json()['data']
        status = status_data['status']
        
        if status == 'completed':
            video_url = status_data['video_url']
            print(f"  Video completed!")
            return video_url
        elif status == 'failed':
            raise Exception(f"Video generation failed: {status_data.get('error')}")
        
        print(f"  Status: {status}... waiting")
        time.sleep(10)

def download_video(video_url, output_path):
    """Download video from HeyGen"""
    
    response = requests.get(video_url, stream=True)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"  Video downloaded: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 70)
    print("HEYGEN TALKING VIDEO GENERATOR")
    print("=" * 70)
    
    if not HEYGEN_API_KEY:
        print("\nError: HEYGEN_API_KEY not found in .env")
        sys.exit(1)
    
    if not os.path.exists(VOICE_SAMPLE):
        print(f"\nError: Voice sample not found: {VOICE_SAMPLE}")
        sys.exit(1)
    
    try:
        print("\n[1/3] Uploading Yoruba voice to HeyGen...")
        audio_id = upload_audio_to_heygen(VOICE_SAMPLE)
        
        print("\n[2/3] Generating talking video...")
        video_url = create_talking_video(audio_id)
        
        print("\n[3/3] Downloading video...")
        output_file = os.path.join(OUTPUT_DIR, "sisi_heygen_talking_001.mp4")
        video_path = download_video(video_url, output_file)
        
        print("\n" + "=" * 70)
        print("SUCCESS! TALKING VIDEO CREATED")
        print("=" * 70)
        print(f"\nVideo: {video_path}")
        print(f"Duration: ~6.6 minutes")
        print(f"Features: Lip-sync + Yoruba voice")
        print(f"\nNext: Upload to YouTube")
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
