"""COMPLETE TALKING VIDEO PIPELINE - Script to YouTube"""
import sys
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from yoruba_validator import validate_yoruba_ratio
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
VOICE_SAMPLE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
AVATAR_IMAGE = "../../01_AVATAR_DNA/01_Reference_Sheets/SisiLola_Reference_Sheet_v01.png"
WAV2LIP_DIR = "../../wav2lip_workspace/Wav2Lip"

def generate_yoruba_script(topic):
    """Generate 7-minute Yoruba script"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": f"""You are Sisi Lola, Nigerian AI influencer in 2-piece ankara attire.

Generate 7-minute script (2000+ words) with 60% Yoruba, 30% Pidgin, 10% English.

YORUBA PHRASES: Ẹ káàbọ̀ o! Báwo ni ẹ ṣe wà? Mo dúpẹ́. Ọjọ́ òní. Ó dára púpọ̀. Ṣé ẹ gbọ́?
PIDGIN: dey, don, go fit, make we, wetin, wahala, no be small thing
ENGLISH: Only technical terms

Topic: {topic}
Length: 2000+ words for 7 minutes"""
        }],
        max_tokens=4000,
        temperature=0.85
    )
    return response.choices[0].message.content, response.usage.total_tokens * 0.0000025

def generate_talking_video(face_image, audio_file, output_file):
    """Generate talking video with Wav2Lip"""
    checkpoint = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip_gan.pth")
    
    cmd = [
        sys.executable,
        os.path.join(WAV2LIP_DIR, "inference.py"),
        "--checkpoint_path", checkpoint,
        "--face", face_image,
        "--audio", audio_file,
        "--outfile", output_file,
        "--fps", "25",
        "--pads", "0", "10", "0", "0"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WAV2LIP_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Wav2Lip failed: {result.stderr}")
    
    return output_file

def upload_to_youtube(video_file, title, script):
    """Upload to YouTube"""
    creds = Credentials.from_authorized_user_file("token_youtube.json")
    youtube = build('youtube', 'v3', credentials=creds)
    
    metadata = {
        'snippet': {
            'title': title,
            'description': f"Ẹ káàbọ̀! {script[:400]}...\n\n#SisiLola #Yoruba #Nigerian #AfricanTech",
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
    
    return f"https://youtube.com/watch?v={response['id']}"

# EXECUTE PIPELINE
if __name__ == "__main__":
    topics = [
        "African fintech revolution transforming mobile banking",
        "Nigerian tech startups solving healthcare challenges"
    ]
    
    print("=" * 70)
    print("COMPLETE TALKING VIDEO PIPELINE")
    print("=" * 70)
    
    # Check Wav2Lip setup
    if not os.path.exists(WAV2LIP_DIR):
        print("\n✗ Wav2Lip not installed. Run: python setup_wav2lip.py")
        sys.exit(1)
    
    total_cost = 0
    videos = []
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[VIDEO {i}/{len(topics)}] {topic}")
        print("-" * 70)
        
        # Generate script
        print("[1/4] Generating Yoruba script...")
        script, cost = generate_yoruba_script(topic)
        total_cost += cost
        validation = validate_yoruba_ratio(script)
        print(f"  ✓ Script: {validation['yoruba']}% Yoruba (${cost:.4f})")
        
        # Save script
        script_file = f"../../07_RAW_WORKSPACE/talking_script_{i:03d}.txt"
        Path(script_file).parent.mkdir(parents=True, exist_ok=True)
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(f"TOPIC: {topic}\n\n{script}")
        
        # Generate talking video
        print("[2/4] Generating talking video with Wav2Lip...")
        output_file = f"../../06_RENDER_OUTPUT/talking_videos/sisi_talking_{i:03d}.mp4"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            video_path = generate_talking_video(AVATAR_IMAGE, VOICE_SAMPLE, output_file)
            print(f"  ✓ Talking video created")
        except Exception as e:
            print(f"  ✗ Video generation failed: {e}")
            continue
        
        # Upload to YouTube
        print("[3/4] Uploading to YouTube...")
        title = f"{topic[:60]}... - Sisi Lola (Yoruba/English)"
        try:
            url = upload_to_youtube(video_path, title, script)
            videos.append(url)
            print(f"  ✓ Published: {url}")
        except Exception as e:
            print(f"  ✗ Upload failed: {e}")
        
        print("[4/4] ✓ COMPLETE")
    
    print("\n" + "=" * 70)
    print(f"✓ {len(videos)} TALKING VIDEOS PUBLISHED")
    print("=" * 70)
    print(f"Cost: ${total_cost:.4f}\n")
    for i, url in enumerate(videos, 1):
        print(f"{i}. {url}")
