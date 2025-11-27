#!/usr/bin/env python3
"""
Auto-generate and upload video (no prompts)
"""
import os
import sys
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
    print("[1/4] Generating script...")
    
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
    script_path = OUTPUT_DIR / f'script_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    script_path.write_text(script)
    print(f"[OK] Script: {len(script)} chars")
    
    return script

def generate_heygen_video(script):
    print("[2/4] Generating HeyGen video...")
    
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
            'dimension': {'width': 1280, 'height': 720},
            'aspect_ratio': '16:9',
            'test': False
        }
    )
    
    if response.status_code != 200:
        print(f"[ERROR] HeyGen API: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if 'data' not in result or 'video_id' not in result.get('data', {}):
        print(f"[ERROR] No video_id: {result}")
        return None
    
    video_id = result['data']['video_id']
    print(f"[OK] Video ID: {video_id}")
    
    # Poll for completion
    for i in range(60):  # 10 minutes max
        time.sleep(10)
        
        status_response = requests.get(
            f'https://api.heygen.com/v1/video_status.get?video_id={video_id}',
            headers={'X-Api-Key': os.getenv('HEYGEN_API_KEY')}
        )
        
        status_data = status_response.json()
        status = status_data.get('data', {}).get('status')
        
        print(f"[WAIT] Status: {status} ({i*10}s)")
        
        if status == 'completed':
            video_url = status_data['data']['video_url']
            video_response = requests.get(video_url)
            video_path = OUTPUT_DIR / f'heygen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
            video_path.write_bytes(video_response.content)
            print(f"[OK] Downloaded: {video_path.name}")
            return video_path
        
        elif status == 'failed':
            print(f"[ERROR] Failed: {status_data}")
            return None
    
    print("[ERROR] Timeout")
    return None

def upload_to_youtube(video_path, script):
    print("[3/4] Uploading to YouTube...")
    
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
        category_id="22",
        privacy="public"
    )
    
    print(f"[OK] YouTube ID: {video_id}")
    return video_id

def main():
    print("=" * 60)
    print("AUTO VIDEO GENERATION & UPLOAD")
    print("=" * 60)
    
    try:
        script = generate_script()
        video_path = generate_heygen_video(script)
        
        if not video_path:
            print("[ERROR] Video generation failed")
            return
        
        video_id = upload_to_youtube(video_path, script)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Video live!")
        print("=" * 60)
        print(f"URL: https://youtu.be/{video_id}")
        print(f"Video: {video_path}")
        
        # Log
        log_path = OUTPUT_DIR / f'upload_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        log_path.write_text(f"""
SUCCESS
=======
Date: {datetime.now().isoformat()}
Video ID: {video_id}
URL: https://youtu.be/{video_id}
Script: {script}
""")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
