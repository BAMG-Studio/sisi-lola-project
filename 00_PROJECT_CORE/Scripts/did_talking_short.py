"""Generate SHORT Talking Video with D-ID (1 minute test)"""
import os
import sys
import requests
import time
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DID_API_KEY = "c2lzaWxvbGFsaXZlQGdtYWlsLmNvbQ:zle2VViqAaufcybCE0Nm-"
VOICE_SAMPLE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
AVATAR_IMAGE = "../../01_AVATAR_DNA/01_Reference_Sheets/SisiLola_Reference_Sheet_v01.png"
OUTPUT_DIR = "../../06_RENDER_OUTPUT/talking_videos"
FFMPEG = r"C:\Users\POK28\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

# Trim audio to 1 minute
print("Trimming audio to 1 minute...")
short_audio = "../../07_RAW_WORKSPACE/voice_1min.wav"
Path(short_audio).parent.mkdir(parents=True, exist_ok=True)

subprocess.run([
    FFMPEG, "-y", "-i", VOICE_SAMPLE,
    "-t", "60", "-c", "copy",
    short_audio
], check=True, capture_output=True)

print("Audio trimmed")

# Upload image
headers = {"Authorization": f"Basic {DID_API_KEY}"}

with open(AVATAR_IMAGE, 'rb') as f:
    response = requests.post(
        "https://api.d-id.com/images",
        headers=headers,
        files={"image": f}
    )

image_url = response.json()['url']
print(f"Image uploaded: {image_url}")

# Create video
with open(short_audio, 'rb') as audio_file:
    files = {
        'source_url': (None, image_url),
        'audio': ('audio.wav', audio_file, 'audio/wav')
    }
    data = {'config': '{"fluent": true, "pad_audio": 0}'}
    
    response = requests.post(
        "https://api.d-id.com/talks",
        headers=headers,
        files=files,
        data=data
    )

if response.status_code not in [200, 201]:
    print(f"Error: {response.text}")
    sys.exit(1)

talk_id = response.json()['id']
print(f"Video generation started: {talk_id}")

# Poll
while True:
    status_response = requests.get(
        f"https://api.d-id.com/talks/{talk_id}",
        headers=headers
    )
    
    status = status_response.json()['status']
    
    if status == 'done':
        video_url = status_response.json()['result_url']
        break
    elif status == 'error':
        print(f"Error: {status_response.json()}")
        sys.exit(1)
    
    print(f"Status: {status}...")
    time.sleep(5)

# Download
output_file = os.path.join(OUTPUT_DIR, "sisi_did_talking_1min.mp4")
Path(output_file).parent.mkdir(parents=True, exist_ok=True)

response = requests.get(video_url, stream=True)
with open(output_file, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"\nSUCCESS! Video created: {output_file}")
print("Duration: 1 minute (test)")
print("Features: Sisi Lola + Yoruba voice + lip-sync")
