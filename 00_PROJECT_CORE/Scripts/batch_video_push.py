"""Batch Generate and Upload 5 Videos - Complete Pipeline"""
import os
import sys
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOPICS = [
    "African tech startups revolutionizing agriculture",
    "Nigerian music industry meets AI production",
    "African fashion designers using 3D printing",
    "Lagos tech scene and innovation hubs",
    "African women in technology leadership"
]

YORUBA_PROMPT = """You are Sisi Lola, Nigerian AI influencer in 2-piece ankara attire.

CRITICAL: Generate script with MAJORITY YORUBA language.

LANGUAGE DISTRIBUTION (STRICT):
- 60% YORUBA: Ẹ káàbọ̀, Báwo ni, Ọjọ́ òní, Ẹ ṣeun, Kò burú, Mo dúpẹ́, Ó dára púpọ̀
- 30% NIGERIAN PIDGIN: dey, wey, make we, go fit, don happen, wahala, wetin
- 10% ENGLISH: Only technical terms

STRUCTURE:
1. Opening: Ẹ káàbọ̀ o! Báwo ni ẹ ṣe wà?
2. Main: Heavy Yoruba with Pidgin transitions
3. Closing: Ẹ ṣeun púpọ̀!

Topic: {topic}
Duration: 5 minutes (~750 words)
Style: Warm, culturally proud, engaging"""

def generate_script(topic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": YORUBA_PROMPT.format(topic=topic)}],
        max_tokens=2000,
        temperature=0.9
    )
    return response.choices[0].message.content, response.usage.total_tokens * 0.0000025

def create_video(script_file, video_file):
    voice = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
    avatar_dir = Path("../../01_AVATAR_DNA/01_Reference_Sheets")
    avatar = str(list(avatar_dir.glob("*.png"))[0])
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-i", avatar,
        "-i", voice,
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-t", "300",
        video_file
    ]
    subprocess.run(cmd, check=True)

def upload_to_youtube(video_file, title, description):
    creds = Credentials.from_authorized_user_file("token_youtube.json")
    youtube = build('youtube', 'v3', credentials=creds)
    
    metadata = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Sisi Lola', 'African Tech', 'Yoruba', 'Nigerian', 'AI', 'Innovation'],
            'categoryId': '28'
        },
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    }
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/mp4')
    request = youtube.videos().insert(part='snippet,status', body=metadata, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
    
    return f"https://youtube.com/watch?v={response['id']}"

print("=" * 70)
print("BATCH VIDEO GENERATION & UPLOAD - 5 VIDEOS")
print("=" * 70)

total_cost = 0
videos_uploaded = []

for i, topic in enumerate(TOPICS, 1):
    print(f"\n[{i}/5] {topic}")
    
    # Generate script
    print("  Generating script...")
    script, cost = generate_script(topic)
    total_cost += cost
    
    script_file = f"../../07_RAW_WORKSPACE/batch_script_{i:03d}.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(f"TOPIC: {topic}\n\n{script}")
    print(f"  ✓ Script saved (${cost:.4f})")
    
    # Create video
    print("  Creating video...")
    video_file = f"../../06_RENDER_OUTPUT/batch_video_{i:03d}.mp4"
    Path(video_file).parent.mkdir(parents=True, exist_ok=True)
    create_video(script_file, video_file)
    print(f"  ✓ Video created")
    
    # Upload
    print("  Uploading to YouTube...")
    title = f"{topic.title()} - Sisi Lola (Yoruba/English)"
    description = f"Ẹ káàbọ̀! {script[:300]}...\n\n#SisiLola #AfricanTech #Yoruba"
    url = upload_to_youtube(video_file, title, description)
    videos_uploaded.append(url)
    print(f"  ✓ Uploaded: {url}")

print("\n" + "=" * 70)
print("✓ BATCH COMPLETE - 5 VIDEOS PUBLISHED")
print("=" * 70)
print(f"Total Cost: ${total_cost:.4f}")
print("\nVideo URLs:")
for i, url in enumerate(videos_uploaded, 1):
    print(f"{i}. {url}")
