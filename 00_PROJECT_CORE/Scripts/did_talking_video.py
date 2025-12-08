"""Generate Talking Video with D-ID API - PRODUCTION READY"""
import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")

DID_API_KEY = "c2lzaWxvbGFsaXZlQGdtYWlsLmNvbQ:zle2VViqAaufcybCE0Nm-"
VOICE_SAMPLE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
AVATAR_IMAGE = "../../01_AVATAR_DNA/01_Reference_Sheets/SisiLola_Reference_Sheet_v01.png"
OUTPUT_DIR = "../../06_RENDER_OUTPUT/talking_videos"

def upload_image_to_did(image_path):
    """Upload Sisi Lola image to D-ID"""
    
    headers = {"Authorization": f"Basic {DID_API_KEY}"}
    
    with open(image_path, 'rb') as f:
        files = {"image": f}
        response = requests.post(
            "https://api.d-id.com/images",
            headers=headers,
            files=files
        )
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Image upload failed: {response.text}")
    
    image_url = response.json()['url']
    print(f"  Image uploaded: {image_url}")
    return image_url

def upload_audio_to_did(audio_path):
    """Upload Yoruba voice to D-ID"""
    
    headers = {"Authorization": f"Basic {DID_API_KEY}"}
    
    with open(audio_path, 'rb') as f:
        files = {"audio": f}
        response = requests.post(
            "https://api.d-id.com/audios",
            headers=headers,
            files=files
        )
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Audio upload failed: {response.text}")
    
    audio_url = response.json()['url']
    print(f"  Audio uploaded: {audio_url}")
    return audio_url

def create_talking_video_from_file(image_url, audio_path):
    """Create talking video with D-ID using local audio file"""
    
    headers = {"Authorization": f"Basic {DID_API_KEY}"}
    
    with open(audio_path, 'rb') as audio_file:
        files = {
            'source_url': (None, image_url),
            'audio': ('audio.wav', audio_file, 'audio/wav')
        }
        
        data = {
            'config': '{"fluent": true, "pad_audio": 0, "stitch": true}'
        }
    
        response = requests.post(
            "https://api.d-id.com/talks",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Video creation failed: {response.text}")
    
    talk_id = response.json()['id']
    print(f"  Video generation started: {talk_id}")
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f"https://api.d-id.com/talks/{talk_id}",
            headers=headers
        )
        
        status_data = status_response.json()
        status = status_data['status']
        
        if status == 'done':
            video_url = status_data['result_url']
            print(f"  Video completed!")
            return video_url
        elif status == 'error':
            raise Exception(f"Video generation failed: {status_data.get('error')}")
        
        print(f"  Status: {status}... waiting")
        time.sleep(5)

def download_video(video_url, output_path):
    """Download video from D-ID"""
    
    response = requests.get(video_url, stream=True)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"  Video downloaded: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 70)
    print("D-ID TALKING VIDEO GENERATOR - SISI LOLA")
    print("=" * 70)
    
    if not os.path.exists(VOICE_SAMPLE):
        print(f"\nError: Voice sample not found: {VOICE_SAMPLE}")
        sys.exit(1)
    
    if not os.path.exists(AVATAR_IMAGE):
        print(f"\nError: Avatar image not found: {AVATAR_IMAGE}")
        sys.exit(1)
    
    try:
        print("\n[1/4] Uploading Sisi Lola avatar image...")
        image_url = upload_image_to_did(AVATAR_IMAGE)
        
        print("\n[2/4] Generating talking video with lip-sync...")
        video_url = create_talking_video_from_file(image_url, VOICE_SAMPLE)
        
        print("\n[4/4] Downloading video...")
        output_file = os.path.join(OUTPUT_DIR, "sisi_did_talking_001.mp4")
        video_path = download_video(video_url, output_file)
        
        print("\n" + "=" * 70)
        print("SUCCESS! TALKING VIDEO CREATED")
        print("=" * 70)
        print(f"\nVideo: {video_path}")
        print(f"Duration: ~6.6 minutes")
        print(f"Features:")
        print(f"  - Sisi Lola Ankara avatar")
        print(f"  - Yoruba voice with lip-sync")
        print(f"  - Professional quality")
        print(f"\nNext: Upload to YouTube")
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
