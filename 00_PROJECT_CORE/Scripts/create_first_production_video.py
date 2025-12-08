"""Create First Production Sisi Lola Video - GPT-4o + Existing Assets"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
from pathlib import Path

load_dotenv("../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
VOICE_SAMPLE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
AVATAR_REF = "../../01_AVATAR_DNA/01_Reference_Sheets"
OUTPUT = "../../06_RENDER_OUTPUT/sisi_lola_production_001.mp4"

print("🎬 SISI LOLA PRODUCTION VIDEO #1")
print("=" * 60)

# Step 1: Generate Yoruba script
print("\n📝 Generating Yoruba script with GPT-4o...")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "system",
        "content": """You are Sisi Lola, Nigerian AI influencer in 2-piece ankara attire.
        Generate 7-minute video script about African tech innovation.
        
        STRICT LANGUAGE RATIO:
        - 60% Yoruba (use ẹ, ọ, ṣ, authentic greetings, proverbs)
        - 30% Nigerian Pidgin (dey, don, go, fit, wahala, wetin)
        - 10% English (technical terms only)
        
        Style: Afro-futuristic, confident, culturally proud
        Tone: Warm, engaging, educational
        
        Include:
        - Yoruba greeting (Ẹ káàbọ̀)
        - Cultural references
        - Tech innovation examples
        - Call to action"""
    }],
    max_tokens=2000,
    temperature=0.7
)

script = response.choices[0].message.content
cost = response.usage.total_tokens * 0.0000025

print(f"✅ Script generated (${cost:.4f})")
print(f"📊 Length: {len(script)} chars, {len(script.split())} words")
print(f"\n📄 SCRIPT PREVIEW:\n{script[:300]}...\n")

# Save script
script_path = "../../07_RAW_WORKSPACE/script_001.txt"
Path(script_path).parent.mkdir(parents=True, exist_ok=True)
with open(script_path, "w", encoding="utf-8") as f:
    f.write(script)
print(f"💾 Script saved: {script_path}")

# Step 2: Use existing voice sample
print(f"\n🎤 Using existing Yoruba voice sample...")
if not os.path.exists(VOICE_SAMPLE):
    print(f"⚠️  Voice sample not found: {VOICE_SAMPLE}")
    print("   Using placeholder - replace with actual sample")
    VOICE_SAMPLE = "placeholder_audio.wav"

# Step 3: Create video with FFmpeg
print(f"\n🎥 Creating video with static avatar...")
avatar_files = list(Path(AVATAR_REF).glob("*.png")) + list(Path(AVATAR_REF).glob("*.jpg"))
if avatar_files:
    avatar_img = str(avatar_files[0])
    print(f"   Using avatar: {avatar_img}")
    
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", avatar_img,
        "-i", VOICE_SAMPLE,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-t", "420",  # 7 minutes
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Video created: {OUTPUT}")
    else:
        print(f"❌ FFmpeg error: {result.stderr[:200]}")
else:
    print(f"⚠️  No avatar images found in {AVATAR_REF}")

print("\n" + "=" * 60)
print("🎊 PRODUCTION VIDEO #1 COMPLETE")
print(f"📁 Script: {script_path}")
print(f"🎬 Video: {OUTPUT}")
print(f"💰 Cost: ${cost:.4f}")
print("\n🚀 Next: Upload to YouTube with youtube_content_uploader.py")
