"""Upload Existing Video with New Authentic Yoruba Script"""
import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("UPLOAD EXISTING VIDEO WITH AUTHENTIC YORUBA METADATA")
print("=" * 70)

# Use existing HeyGen video with new authentic script
video_file = "../../06_RENDER_OUTPUT/youtube_videos/heygen_20251126_181318.mp4"
script_file = "../../07_RAW_WORKSPACE/authentic_script_001.txt"

if not os.path.exists(video_file):
    print(f"✗ Video not found: {video_file}")
    sys.exit(1)

if not os.path.exists(script_file):
    print(f"✗ Script not found: {script_file}")
    sys.exit(1)

# Read script
with open(script_file, "r", encoding="utf-8") as f:
    script = f.read()

print(f"✓ Video: {video_file}")
print(f"✓ Script: {script_file}")
print(f"\nScript preview:\n{script[:300]}...\n")

# Upload to YouTube
print("Uploading to YouTube...")
token_file = "token_youtube.json"
if not os.path.exists(token_file):
    print(f"✗ YouTube token not found: {token_file}")
    print("  Run: python youtube_oauth_complete.py")
    sys.exit(1)

creds = Credentials.from_authorized_user_file(token_file)
youtube = build('youtube', 'v3', credentials=creds)

video_metadata = {
    'snippet': {
        'title': 'African Fashion Meets AI Technology - Sisi Lola (Yoruba/English)',
        'description': f'''Ẹ káàbọ̀! Welcome to Sisi Lola's authentic Yoruba/Yorunglish channel!

{script[:500]}...

🌍 Topics:
- AI in African fashion design
- Modern ankara pattern creation
- Technology meets tradition
- Yoruba/Nigerian Pidgin/English mix

Subscribe for authentic Afro-futuristic content!

#SisiLola #AfricanFashion #AITechnology #Ankara #Yoruba #Nigerian #AfricanInnovation''',
        'tags': ['African Fashion', 'AI', 'Ankara', 'Yoruba', 'Nigerian', 'Sisi Lola', 'Afrofuturism'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public',
        'selfDeclaredMadeForKids': False
    }
}

media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/mp4')
request = youtube.videos().insert(
    part='snippet,status',
    body=video_metadata,
    media_body=media
)

response = None
print("Uploading...")
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"  Progress: {int(status.progress() * 100)}%")

video_id = response['id']
video_url = f"https://youtube.com/watch?v={video_id}"

print("\n" + "=" * 70)
print("SUCCESS! AUTHENTIC SISI LOLA VIDEO PUBLISHED")
print("=" * 70)
print(f"Video URL: {video_url}")
print(f"Video ID: {video_id}")
print(f"\nThis video now has authentic Yoruba/Yorunglish metadata!")
print("Future videos will use fully authentic Yoruba voice + avatar.")
