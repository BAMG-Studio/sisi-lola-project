"""FINAL PRODUCTION PIPELINE - Beautiful Sisi Lola + Yoruba Voice"""
import subprocess
import sys
import os
import time
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

# LOCKED SOURCES
VOICE_SOURCE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
AVATAR_FRAME = "../../01_AVATAR_DNA/sisi_lola_heygen_frame.jpg"
WAV2LIP_DIR = "../../wav2lip_workspace/Wav2Lip"
CHECKPOINT = f"{WAV2LIP_DIR}/checkpoints/wav2lip_gan.pth"

print("=" * 70)
print("FINAL PRODUCTION PIPELINE")
print("=" * 70)
print("Beautiful Sisi Lola + Natural Yoruba Voice + Lip-Sync\n")

# Validate
if not os.path.exists(VOICE_SOURCE):
    print(f"[ERROR] Voice missing: {VOICE_SOURCE}")
    sys.exit(1)

if not os.path.exists(AVATAR_FRAME):
    print(f"[ERROR] Avatar missing: {AVATAR_FRAME}")
    sys.exit(1)

print(f"[OK] Voice: {VOICE_SOURCE}")
print(f"[OK] Avatar: {AVATAR_FRAME}")

# Generate video
output_file = f"../../06_RENDER_OUTPUT/talking_videos/sisi_final_{int(time.time())}.mp4"
Path(output_file).parent.mkdir(parents=True, exist_ok=True)

print(f"\n[GENERATING] {output_file}")
print("This takes 2-3 minutes...\n")

cmd = [
    "py", "-3.10",
    f"{WAV2LIP_DIR}/inference.py",
    "--checkpoint_path", CHECKPOINT,
    "--face", AVATAR_FRAME,
    "--audio", VOICE_SOURCE,
    "--outfile", output_file,
    "--fps", "25",
    "--pads", "0", "10", "0", "0",
    "--resize_factor", "1"
]

result = subprocess.run(cmd, cwd=WAV2LIP_DIR)

if result.returncode != 0:
    print("[ERROR] Generation failed")
    sys.exit(1)

# Convert temp result to final
temp_result = f"{WAV2LIP_DIR}/temp/result.avi"
ffmpeg = r"C:\Users\POK28\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

subprocess.run([
    ffmpeg, "-y", "-i", temp_result, "-i", VOICE_SOURCE,
    "-c:v", "libx264", "-c:a", "aac", "-shortest",
    output_file
], check=True, capture_output=True)

print(f"\n[OK] Video created: {output_file}")

# Upload to YouTube
print("\n[UPLOADING] To YouTube...")
creds = Credentials.from_authorized_user_file("token_youtube.json")
youtube = build('youtube', 'v3', credentials=creds)

metadata = {
    'snippet': {
        'title': 'African Tech Innovation - Sisi Lola (Yoruba/English)',
        'description': '''Ẹ káàbọ̀! Beautiful Sisi Lola with authentic Yoruba/Yorunglish voice!

Natural Nigerian accent, professional lip-sync, engaging content.

#SisiLola #Yoruba #Nigerian #AfricanTech''',
        'tags': ['Sisi Lola', 'Yoruba', 'Nigerian', 'African Tech'],
        'categoryId': '28'
    },
    'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
}

media = MediaFileUpload(output_file, chunksize=-1, resumable=True, mimetype='video/mp4')
request = youtube.videos().insert(part='snippet,status', body=metadata, media_body=media)

response = None
while response is None:
    status, response = request.next_chunk()

video_id = response['id']

print("\n" + "=" * 70)
print("SUCCESS! PRODUCTION VIDEO PUBLISHED")
print("=" * 70)
print(f"\nURL: https://youtube.com/watch?v={video_id}")
print(f"Video: {output_file}")
print(f"\nFeatures:")
print(f"  - Beautiful Sisi Lola avatar (HeyGen export)")
print(f"  - Natural Yoruba/Yorunglish voice")
print(f"  - Professional lip-sync")
print(f"  - 6.6 minute duration")
