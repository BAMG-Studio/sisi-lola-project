"""Export Clean Sisi Lola Frame from HeyGen Avatar"""
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv("../../sisi_lola_api/.env")

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
AVATAR_ID = "046a63da7b20403c8c6bb51dbda12f65"
FRAME_PATH = Path("../../01_AVATAR_DNA/sisi_lola_heygen_frame.jpg")

headers = {
    "X-Api-Key": HEYGEN_API_KEY,
    "Content-Type": "application/json"
}

# Generate 1-second video to extract frame
payload = {
    "video_inputs": [{
        "character": {
            "type": "avatar",
            "avatar_id": AVATAR_ID
        },
        "voice": {
            "type": "text",
            "input_text": "Hello",
            "voice_id": "af_sky_en_female_professional"
        }
    }],
    "dimension": {"width": 1920, "height": 1080}
}

print("Generating HeyGen video to extract Sisi Lola frame...")
response = requests.post(
    "https://api.heygen.com/v2/video/generate",
    headers=headers,
    json=payload
)

if response.status_code == 200:
    video_id = response.json()['data']['video_id']
    print(f"Video ID: {video_id}")
    print("Waiting for completion...")
    
    import time
    while True:
        status_response = requests.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers=headers
        )
        
        status = status_response.json()['data']['status']
        if status == 'completed':
            video_url = status_response.json()['data']['video_url']
            
            # Download video
            temp_video = Path("../../07_RAW_WORKSPACE/heygen_temp.mp4")
            temp_video.parent.mkdir(parents=True, exist_ok=True)
            
            video_data = requests.get(video_url)
            with open(temp_video, 'wb') as f:
                f.write(video_data.content)
            
            print(f"Video downloaded: {temp_video}")
            print("\nExtract frame with FFmpeg:")
            print(f'ffmpeg -i "{temp_video}" -vf "select=eq(n\\,0)" -vframes 1 "{FRAME_PATH}"')
            break
        elif status == 'failed':
            print(f"Failed: {status_response.json()}")
            break
        
        time.sleep(5)
else:
    print(f"Error: {response.text}")
