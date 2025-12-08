"""Generate 5 Improved Yoruba Scripts + Upload Existing Videos"""
import os
import sys
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
- 60% YORUBA: Ẹ káàbọ̀, Báwo ni, Ọjọ́ òní, Ẹ ṣeun, Kò burú, Mo dúpẹ́, Ó dára púpọ̀, Ṣé o gbọ́
- 30% NIGERIAN PIDGIN: dey, wey, make we, go fit, don happen, wahala, wetin, no be small thing
- 10% ENGLISH: Only technical terms

STRUCTURE:
1. Opening: Ẹ káàbọ̀ o! Báwo ni ẹ ṣe wà? Mo dúpẹ́!
2. Main: Heavy Yoruba with Pidgin transitions
3. Closing: Ẹ ṣeun púpọ̀! Ẹ ṣọra!

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

def upload_to_youtube(video_file, title, script):
    creds = Credentials.from_authorized_user_file("token_youtube.json")
    youtube = build('youtube', 'v3', credentials=creds)
    
    metadata = {
        'snippet': {
            'title': title,
            'description': f"Ẹ káàbọ̀! {script[:400]}...\n\n#SisiLola #AfricanTech #Yoruba #Nigerian #AI",
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
print("BATCH SCRIPT GENERATION + UPLOAD - 5 VIDEOS")
print("=" * 70)

# Use existing HeyGen videos
existing_videos = [
    "../../06_RENDER_OUTPUT/youtube_videos/heygen_20251126_143538.mp4",
    "../../06_RENDER_OUTPUT/youtube_videos/heygen_20251126_181318.mp4"
]

total_cost = 0
videos_uploaded = []

for i, topic in enumerate(TOPICS[:2], 1):  # Upload 2 videos with new scripts
    print(f"\n[{i}/2] {topic}")
    
    # Generate improved script
    print("  Generating improved Yoruba script...")
    script, cost = generate_script(topic)
    total_cost += cost
    
    script_file = f"../../07_RAW_WORKSPACE/improved_script_{i:03d}.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(f"TOPIC: {topic}\n\n{script}")
    print(f"  ✓ Script saved (${cost:.4f})")
    print(f"  Preview: {script[:150]}...")
    
    # Upload with new metadata
    if i <= len(existing_videos):
        video_file = existing_videos[i-1]
        if os.path.exists(video_file):
            print(f"  Uploading {Path(video_file).name}...")
            title = f"{topic.title()} - Sisi Lola (Yoruba/English)"
            url = upload_to_youtube(video_file, title, script)
            videos_uploaded.append(url)
            print(f"  ✓ Uploaded: {url}")
        else:
            print(f"  ✗ Video not found: {video_file}")

print("\n" + "=" * 70)
print(f"✓ BATCH COMPLETE - {len(videos_uploaded)} VIDEOS PUBLISHED")
print("=" * 70)
print(f"Total Cost: ${total_cost:.4f}")
print("\nVideo URLs:")
for i, url in enumerate(videos_uploaded, 1):
    print(f"{i}. {url}")
print("\nNOTE: FFmpeg needs shell restart. Remaining 3 videos will be generated after restart.")
