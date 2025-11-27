#!/usr/bin/env python3
"""
Generate First Sisi Lola Video
- Script generation with OpenAI
- Voice synthesis with ElevenLabs (African accent)
- Avatar video with HeyGen
- Afrobeat background music
- Upload to YouTube
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Load environment
env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

OUTPUT_DIR = Path(__file__).parent.parent.parent / '06_RENDER_OUTPUT' / 'youtube_videos'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_script():
    """Generate video script with OpenAI"""
    print("[SCRIPT] Generating script...")
    
    prompt = """Create a 60-second introduction script for Sisi Lola, an AI-powered African cultural ambassador.

Requirements:
- Warm, authentic African voice
- Introduce who Sisi Lola is
- Mission: celebrate African culture, innovation, community
- Invite viewers to subscribe and join the journey
- Natural, conversational tone
- Include African greetings (Jambo, Sawubona)

Format: Just the script text, no stage directions."""

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}",
            'Content-Type': 'application/json'
        },
        json={
            'model': 'gpt-4',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.8
        }
    )
    
    script = response.json()['choices'][0]['message']['content']
    
    # Save script
    script_path = OUTPUT_DIR / f'script_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    script_path.write_text(script)
    print(f"[OK] Script saved: {script_path}")
    
    return script

def generate_voice(script):
    """Generate voice with ElevenLabs"""
    print("[VOICE] Generating voice...")
    
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('HEYGEN_VOICE_ID')}",
        headers={
            'xi-api-key': os.getenv('ELEVENLABS_API_KEY'),
            'Content-Type': 'application/json'
        },
        json={
            'text': script,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75,
                'style': 0.5,
                'use_speaker_boost': True
            }
        }
    )
    
    audio_path = OUTPUT_DIR / f'voice_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp3'
    audio_path.write_bytes(response.content)
    print(f"[OK] Voice saved: {audio_path}")
    
    return audio_path

def generate_heygen_video(script):
    """Generate avatar video with HeyGen"""
    print("[VIDEO] Generating HeyGen video...")
    
    response = requests.post(
        'https://api.heygen.com/v2/video/generate',
        headers={
            'X-Api-Key': os.getenv('HEYGEN_API_KEY'),
            'Content-Type': 'application/json'
        },
        json={
            'video_inputs': [{
                'character': {
                    'type': 'avatar',
                    'avatar_id': os.getenv('HEYGEN_AVATAR_ID'),
                    'avatar_style': 'normal'
                },
                'voice': {
                    'type': 'text',
                    'input_text': script,
                    'voice_id': os.getenv('HEYGEN_VOICE_ID')
                },
                'background': {
                    'type': 'color',
                    'value': '#1a1a2e'
                }
            }],
            'dimension': {
                'width': 1280,
                'height': 720
            },
            'aspect_ratio': '16:9',
            'test': False
        }
    )
    
    if response.status_code != 200:
        print(f"[ERROR] HeyGen API error: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if 'data' not in result or 'video_id' not in result.get('data', {}):
        print(f"[ERROR] HeyGen response missing video_id: {result}")
        return None
    
    video_id = result['data']['video_id']
    
    print(f"[WAIT] Video generating... ID: {video_id}")
    
    # Poll for completion
    max_wait = 600  # 10 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status_response = requests.get(
            f'https://api.heygen.com/v1/video_status.get?video_id={video_id}',
            headers={'X-Api-Key': os.getenv('HEYGEN_API_KEY')}
        )
        
        status_data = status_response.json()
        status = status_data.get('data', {}).get('status')
        
        if status == 'completed':
            video_url = status_data['data']['video_url']
            print(f"[OK] Video ready: {video_url}")
            
            # Download video
            video_response = requests.get(video_url)
            video_path = OUTPUT_DIR / f'heygen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
            video_path.write_bytes(video_response.content)
            print(f"[OK] Video downloaded: {video_path}")
            
            return video_path
        
        elif status == 'failed':
            print(f"[ERROR] Video generation failed: {status_data}")
            return None
        
        print(f"[WAIT] Status: {status}... waiting 10s")
        time.sleep(10)
    
    print("[ERROR] Timeout waiting for video")
    return None

def add_afrobeat_music(video_path):
    """Add Afrobeat background music (placeholder - requires ffmpeg)"""
    print("[MUSIC] Adding Afrobeat music...")
    
    # Note: This requires ffmpeg and a music file
    # For now, return original video
    print("[WARN] Music mixing requires ffmpeg - skipping for now")
    print("   Manual: Use video editor to add Afrobeat track at 20% volume")
    
    return video_path

def upload_to_youtube(video_path, script):
    """Upload video to YouTube"""
    print("[UPLOAD] Uploading to YouTube...")
    
    from youtube_content_uploader import upload_video
    
    title = "Meet Sisi Lola - Your AI Guide to African Culture 🌍"
    description = f"""Jambo! Welcome to my channel! 🌍✨

{script[:200]}...

I'm Sisi Lola, your AI-powered guide to African culture, innovation, and community. Join me as we celebrate the richness of African heritage, explore modern African innovation, and build connections across the continent and diaspora.

🔔 Subscribe for:
• Cultural deep dives & storytelling
• African innovation spotlights
• Community conversations
• Music, art, fashion features

Let's celebrate Africa together!

#SisiLola #AfricanCulture #AIInfluencer #Africa #Innovation #Community #Afrobeat"""

    tags = [
        'Sisi Lola', 'African Culture', 'AI Influencer', 'Africa', 
        'African Innovation', 'Afrobeat', 'Pan African', 'African Heritage',
        'Cultural Ambassador', 'African Community'
    ]
    
    video_id = upload_video(
        video_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        category_id="22",  # People & Blogs
        privacy="public"
    )
    
    return video_id

def main():
    """Generate and upload first video"""
    print("=" * 60)
    print("SISI LOLA - FIRST VIDEO GENERATION")
    print("=" * 60)
    
    log_path = OUTPUT_DIR / f'generation_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    try:
        # Step 1: Generate script
        script = generate_script()
        
        # Step 2: Generate HeyGen video
        video_path = generate_heygen_video(script)
        
        if not video_path:
            print("[ERROR] Video generation failed")
            return
        
        # Step 3: Add music (manual for now)
        final_video = add_afrobeat_music(video_path)
        
        # Step 4: Upload to YouTube
        print("\n" + "=" * 60)
        print("READY TO UPLOAD")
        print("=" * 60)
        print(f"Video: {final_video}")
        print(f"Script: {script[:100]}...")
        
        confirm = input("\nUpload to YouTube? (yes/no): ")
        
        if confirm.lower() == 'yes':
            video_id = upload_to_youtube(final_video, script)
            
            # Log success
            log_path.write_text(f"""
GENERATION SUCCESS
==================
Date: {datetime.now().isoformat()}
Script: {script}
Video: {final_video}
YouTube ID: {video_id}
URL: https://youtu.be/{video_id}
""")
            
            print("\n" + "=" * 60)
            print("[SUCCESS] Video uploaded!")
            print("=" * 60)
            print(f"Video live: https://youtu.be/{video_id}")
            print(f"Log: {log_path}")
        else:
            print("Upload cancelled. Video saved locally.")
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        log_path.write_text(f"ERROR: {e}\n{datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
