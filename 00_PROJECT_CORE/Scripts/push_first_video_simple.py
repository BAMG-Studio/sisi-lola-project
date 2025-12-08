"""Push First Authentic Sisi Lola Video - Simple Version (No FFmpeg)"""
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("=" * 70)
print("SISI LOLA FIRST AUTHENTIC VIDEO - SCRIPT GENERATION")
print("=" * 70)

# Generate authentic Yoruba script
print("\n[1/2] Generating Yoruba/Yorunglish script with GPT-4o...")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "system",
        "content": """You are Sisi Lola, Nigerian AI influencer in 2-piece ankara attire.
        Generate 5-minute video script about African fashion meets technology.
        
        LANGUAGE MIX (Natural Code-Switching):
        - Start with Yoruba greeting: Ẹ káàbọ̀ o! Báwo ni?
        - Mix Yoruba phrases: ọjọ́ òní (today), ẹ ṣeun (thank you), kò burú (not bad)
        - Use Nigerian Pidgin: dey, wey, make we, go fit, don happen, wahala
        - English for tech terms only: AI, fashion, technology, innovation
        
        Topic: How African designers are using AI to create modern ankara patterns
        Style: Warm, engaging, proud of African culture
        Length: ~800 words (5 minutes speaking)
        
        Example flow: "Ẹ káàbọ̀! Today we go talk about something wey dey burst my brain - 
        how our African designers dey use AI to create new ankara patterns. Ọjọ́ òní, 
        make we explore this innovation together..."
        
        Include cultural pride, tech innovation, and call to action."""
    }],
    max_tokens=1500,
    temperature=0.85
)

script = response.choices[0].message.content
cost = response.usage.total_tokens * 0.0000025

print(f"✓ Script generated ({len(script)} chars, ${cost:.4f})")
print(f"\n{'='*70}")
print("GENERATED YORUBA/YORUNGLISH SCRIPT:")
print(f"{'='*70}\n")
print(script)
print(f"\n{'='*70}")

# Save script
script_file = "../../07_RAW_WORKSPACE/authentic_script_001.txt"
Path(script_file).parent.mkdir(parents=True, exist_ok=True)
with open(script_file, "w", encoding="utf-8") as f:
    f.write(script)
print(f"\n✓ Script saved: {script_file}")

# Check for existing video to upload
print("\n[2/2] Checking for video file to upload...")
video_candidates = [
    "../../06_RENDER_OUTPUT/sisi_lola_authentic_001.mp4",
    "../../06_RENDER_OUTPUT/sisi_lola_production_001.mp4",
    "../../03_MEDIA_ASSETS/content_queue/latest_video.mp4"
]

video_file = None
for candidate in video_candidates:
    if os.path.exists(candidate):
        video_file = candidate
        break

if not video_file:
    print("\n✗ No video file found for upload")
    print("\nNEXT STEPS:")
    print("1. Use script above to record/generate video")
    print("2. Save video to: 06_RENDER_OUTPUT/sisi_lola_authentic_001.mp4")
    print("3. Run this script again to upload")
    print(f"\nScript ready at: {script_file}")
    print(f"Cost: ${cost:.4f}")
    sys.exit(0)

# Upload to YouTube
print(f"✓ Found video: {video_file}")
print("\n[3/3] Uploading to YouTube...")

token_file = "token_youtube.json"
if not os.path.exists(token_file):
    print(f"✗ YouTube token not found: {token_file}")
    print("  Run: python youtube_oauth_complete.py")
    sys.exit(1)

creds = Credentials.from_authorized_user_file(token_file)
youtube = build('youtube', 'v3', credentials=creds)

video_metadata = {
    'snippet': {
        'title': 'African Fashion Meets AI Technology - Sisi Lola',
        'description': '''Ẹ káàbọ̀! Welcome to Sisi Lola's channel!

Today we explore how African designers are using AI to revolutionize ankara and traditional fashion patterns.

🌍 Topics covered:
- AI in African fashion design
- Modern ankara pattern creation
- Technology meets tradition

Subscribe for more Afro-futuristic content!

#SisiLola #AfricanFashion #AITechnology #Ankara #AfricanInnovation''',
        'tags': ['African Fashion', 'AI', 'Technology', 'Ankara', 'Nigerian', 'Sisi Lola'],
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

response_upload = None
while response_upload is None:
    status, response_upload = request.next_chunk()
    if status:
        print(f"  Upload progress: {int(status.progress() * 100)}%")

video_id = response_upload['id']
video_url = f"https://youtube.com/watch?v={video_id}"

print("\n" + "=" * 70)
print("SUCCESS! FIRST AUTHENTIC SISI LOLA VIDEO PUBLISHED")
print("=" * 70)
print(f"Video URL: {video_url}")
print(f"Script: {script_file}")
print(f"Video File: {video_file}")
print(f"Cost: ${cost:.4f}")
print("\nThis video features authentic Yoruba/Yorunglish content!")
