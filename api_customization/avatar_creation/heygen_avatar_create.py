#!/usr/bin/env python3
"""
HeyGen Custom Avatar Creation
Upload video and create custom Sisi Lola avatar
"""

import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('sisi_lola_api/.env')

HEYGEN_API_KEY = os.getenv('HEYGEN_API_KEY')
HEYGEN_API_URL = "https://api.heygen.com/v2"

def upload_video(video_path):
    """Upload video for avatar creation"""
    print(f"Uploading video: {video_path}")
    
    headers = {'x-api-key': HEYGEN_API_KEY}
    
    with open(video_path, 'rb') as video_file:
        files = {'file': (Path(video_path).name, video_file, 'video/mp4')}
        
        response = requests.post(
            f"{HEYGEN_API_URL}/avatars/upload",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        data = response.json()
        upload_id = data.get('data', {}).get('upload_id')
        print(f"✓ Video uploaded: {upload_id}")
        return upload_id
    else:
        print(f"Error uploading video: {response.status_code}")
        print(response.text)
        return None

def create_avatar(upload_id, avatar_name):
    """Create avatar from uploaded video"""
    print(f"Creating avatar: {avatar_name}")
    
    headers = {
        'x-api-key': HEYGEN_API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'upload_id': upload_id,
        'avatar_name': avatar_name,
        'avatar_type': 'talking_photo'
    }
    
    response = requests.post(
        f"{HEYGEN_API_URL}/avatars",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        avatar_data = response.json()
        avatar_id = avatar_data.get('data', {}).get('avatar_id')
        print(f"✓ Avatar created: {avatar_id}")
        return avatar_id
    else:
        print(f"Error creating avatar: {response.status_code}")
        print(response.text)
        return None

def check_avatar_status(avatar_id):
    """Check avatar processing status"""
    headers = {'x-api-key': HEYGEN_API_KEY}
    
    response = requests.get(
        f"{HEYGEN_API_URL}/avatars/{avatar_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        status = data.get('data', {}).get('status')
        return status
    else:
        return None

def wait_for_avatar(avatar_id, timeout=600):
    """Wait for avatar to be ready"""
    print("Waiting for avatar processing...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = check_avatar_status(avatar_id)
        
        if status == 'completed':
            print("✓ Avatar ready!")
            return True
        elif status == 'failed':
            print("✗ Avatar processing failed")
            return False
        
        print(f"  Status: {status}...")
        time.sleep(10)
    
    print("✗ Timeout waiting for avatar")
    return False

def save_avatar_id(avatar_id):
    """Save avatar ID to .env"""
    env_file = Path('sisi_lola_api/.env')
    
    with open(env_file, 'a') as f:
        f.write(f"\n# HeyGen Custom Avatar\n")
        f.write(f"HEYGEN_SISI_LOLA_AVATAR_ID={avatar_id}\n")
    
    print(f"✓ Avatar ID saved to .env")

def list_avatars():
    """List all available avatars"""
    headers = {'x-api-key': HEYGEN_API_KEY}
    
    response = requests.get(f"{HEYGEN_API_URL}/avatars", headers=headers)
    
    if response.status_code == 200:
        avatars = response.json().get('data', {}).get('avatars', [])
        print(f"\nAvailable avatars ({len(avatars)}):")
        for avatar in avatars:
            print(f"  - {avatar.get('avatar_name')} (ID: {avatar.get('avatar_id')})")
    else:
        print(f"Error listing avatars: {response.status_code}")

def main():
    print("=" * 60)
    print("HEYGEN AVATAR CREATION")
    print("=" * 60)
    
    if not HEYGEN_API_KEY:
        print("Error: HEYGEN_API_KEY not found in .env")
        return 1
    
    # Check for video file
    video_dir = Path('01_AVATAR_DNA/03_Video_Samples')
    video_files = list(video_dir.glob('*.mp4')) if video_dir.exists() else []
    
    if not video_files:
        print(f"Error: No video files found in {video_dir}")
        print("\nPlease add a video sample (5-10 minutes) to this directory.")
        print("Requirements:")
        print("  - Clear face visibility")
        print("  - Good lighting")
        print("  - Minimal background noise")
        print("  - Speaking naturally")
        return 1
    
    video_path = video_files[0]
    print(f"Using video: {video_path}")
    
    # Upload video
    upload_id = upload_video(video_path)
    if not upload_id:
        return 1
    
    # Create avatar
    avatar_id = create_avatar(upload_id, "Sisi Lola Custom")
    if not avatar_id:
        return 1
    
    # Wait for processing
    if wait_for_avatar(avatar_id):
        save_avatar_id(avatar_id)
        list_avatars()
        
        print("\n" + "=" * 60)
        print("AVATAR CREATION COMPLETE!")
        print("=" * 60)
        print(f"Avatar ID: {avatar_id}")
        print("Use this ID in your API calls for Sisi Lola's avatar")
        
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
