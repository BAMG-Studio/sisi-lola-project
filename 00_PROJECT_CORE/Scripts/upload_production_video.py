"""Upload Production Video to YouTube"""
import sys
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

# Find latest production video
video_dir = Path("../../06_RENDER_OUTPUT/talking_videos")
videos = sorted(video_dir.glob("sisi_production_*.mp4"), key=os.path.getmtime, reverse=True)

if not videos:
    print("No production videos found")
    sys.exit(1)

video_file = str(videos[0])
print(f"Uploading: {video_file}")

# Upload
creds = Credentials.from_authorized_user_file("token_youtube.json")
youtube = build('youtube', 'v3', credentials=creds)

metadata = {
    'snippet': {
        'title': 'African Tech Innovation - Sisi Lola (Yoruba/English)',
        'description': '''Ẹ káàbọ̀! Welcome to authentic Sisi Lola content!

Beautiful Sisi Lola avatar with natural Yoruba/Yorunglish voice and professional lip-sync.

Topics: African technology, innovation, culture

#SisiLola #Yoruba #Nigerian #AfricanTech #AI''',
        'tags': ['Sisi Lola', 'Yoruba', 'Nigerian', 'African Tech', 'AI'],
        'categoryId': '28'
    },
    'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
}

media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/mp4')
request = youtube.videos().insert(part='snippet,status', body=metadata, media_body=media)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Progress: {int(status.progress() * 100)}%")

video_id = response['id']
print(f"\nSUCCESS! https://youtube.com/watch?v={video_id}")
