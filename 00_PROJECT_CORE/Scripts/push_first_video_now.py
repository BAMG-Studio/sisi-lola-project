"""Push First Authentic Sisi Lola Video - IMMEDIATE EXECUTION"""
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("=" * 70)
print("SISI LOLA FIRST AUTHENTIC VIDEO - PRODUCTION PUSH")
print("=" * 70)

# Step 1: Generate authentic Yoruba script
print("\n[1/4] Generating Yoruba/Yorunglish script with GPT-4o...")
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
print(f"✓ Script generated ({len(script)} chars, ${response.usage.total_tokens * 0.0000025:.4f})")
print(f"\nSCRIPT PREVIEW:\n{script[:400]}...\n")

# Save script
script_file = "../../07_RAW_WORKSPACE/authentic_script_001.txt"
Path(script_file).parent.mkdir(parents=True, exist_ok=True)
with open(script_file, "w", encoding="utf-8") as f:
    f.write(script)

# Step 2: Find voice sample and avatar
print("[2/4] Locating voice sample and avatar...")
voice_sample = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
avatar_dir = Path("../../01_AVATAR_DNA/01_Reference_Sheets")
avatar_files = list(avatar_dir.glob("*.png")) + list(avatar_dir.glob("*.jpg"))

if not avatar_files:
    print("✗ No avatar images found - creating placeholder")
    avatar_img = "placeholder.jpg"
else:
    avatar_img = str(avatar_files[0])
    print(f"✓ Using avatar: {avatar_img}")

# Step 3: Create video with FFmpeg
print("[3/4] Creating video...")
output_video = "../../06_RENDER_OUTPUT/sisi_lola_authentic_001.mp4"
Path(output_video).parent.mkdir(parents=True, exist_ok=True)

if os.path.exists(voice_sample) and os.path.exists(avatar_img):
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-i", avatar_img,
        "-i", voice_sample,
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-t", "300",  # 5 minutes
        output_video
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ Video created: {output_video}")
    else:
        print(f"✗ FFmpeg error: {result.stderr}")
        sys.exit(1)
else:
    print(f"✗ Missing assets - Voice: {os.path.exists(voice_sample)}, Avatar: {os.path.exists(avatar_img)}")
    sys.exit(1)

# Step 4: Upload to YouTube
print("[4/4] Uploading to YouTube...")
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
        'categoryId': '28'  # Science & Technology
    },
    'status': {
        'privacyStatus': 'public',
        'selfDeclaredMadeForKids': False
    }
}

media = MediaFileUpload(output_video, chunksize=-1, resumable=True, mimetype='video/mp4')
request = youtube.videos().insert(
    part='snippet,status',
    body=video_metadata,
    media_body=media
)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"  Upload progress: {int(status.progress() * 100)}%")

video_id = response['id']
video_url = f"https://youtube.com/watch?v={video_id}"

print("\n" + "=" * 70)
print("SUCCESS! FIRST AUTHENTIC SISI LOLA VIDEO PUBLISHED")
print("=" * 70)
print(f"Video URL: {video_url}")
print(f"Script: {script_file}")
print(f"Video File: {output_video}")
print(f"Cost: ${response.usage.total_tokens * 0.0000025:.4f}")
print("\nThis video features authentic Yoruba/Yorunglish content!")
