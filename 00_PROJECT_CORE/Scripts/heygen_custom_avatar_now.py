"""Generate Video with HeyGen Custom Sisi Lola Avatar + Yoruba Script"""
import os
import sys
import requests
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../../sisi_lola_api/.env")

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_AVATAR_ID = "046a63da7b20403c8c6bb51dbda12f65"  # Custom Sisi Lola
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("=" * 70)
print("HEYGEN CUSTOM SISI LOLA AVATAR - YORUBA VIDEO")
print("=" * 70)

# Generate Yoruba script
print("\n[1/3] Generating Yoruba script...")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "system",
        "content": """You are Sisi Lola, Nigerian AI influencer.
        Generate 2-minute script about African tech innovation.
        
        LANGUAGE: 60% Yoruba, 30% Nigerian Pidgin, 10% English
        YORUBA: Ẹ káàbọ̀, Báwo ni, Ọjọ́ òní, Ẹ ṣeun, Ó dára púpọ̀
        PIDGIN: dey, don, go fit, make we, wetin, wahala
        
        Natural code-switching. Warm, engaging tone."""
    }],
    max_tokens=800,
    temperature=0.85
)

script = response.choices[0].message.content
print(f"✓ Script: {len(script)} chars")
print(f"Preview: {script[:200]}...")

# Create video with HeyGen
print("\n[2/3] Creating video with HeyGen custom avatar...")
headers = {
    "X-Api-Key": HEYGEN_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "video_inputs": [{
        "character": {
            "type": "avatar",
            "avatar_id": HEYGEN_AVATAR_ID,
            "avatar_style": "normal"
        },
        "voice": {
            "type": "text",
            "input_text": script,
            "voice_id": "af_sky_en_female_professional"  # Natural female voice
        }
    }],
    "dimension": {"width": 1920, "height": 1080},
    "aspect_ratio": "16:9"
}

response = requests.post(
    "https://api.heygen.com/v2/video/generate",
    headers=headers,
    json=payload
)

if response.status_code != 200:
    print(f"Error: {response.text}")
    sys.exit(1)

video_id = response.json()['data']['video_id']
print(f"✓ Video generation started: {video_id}")

# Poll for completion
print("\n[3/3] Waiting for video (2-3 minutes)...")
while True:
    status_response = requests.get(
        f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
        headers=headers
    )
    
    status_data = status_response.json()['data']
    status = status_data['status']
    
    if status == 'completed':
        video_url = status_data['video_url']
        
        # Download
        output_file = "../../06_RENDER_OUTPUT/talking_videos/sisi_heygen_custom_001.mp4"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        video_response = requests.get(video_url, stream=True)
        with open(output_file, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("\n" + "=" * 70)
        print("SUCCESS! CUSTOM SISI LOLA VIDEO CREATED")
        print("=" * 70)
        print(f"\nVideo: {output_file}")
        print(f"Avatar: Custom Sisi Lola (beautiful, professional)")
        print(f"Duration: ~2 minutes")
        print(f"Features: Lip-sync + Yoruba script")
        break
    elif status == 'failed':
        print(f"Error: {status_data.get('error')}")
        sys.exit(1)
    
    print(f"  Status: {status}...")
    time.sleep(10)
