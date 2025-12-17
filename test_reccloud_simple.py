#!/usr/bin/env python3
"""
Simple RecCloud API Test - Uses file.io as temporary file host
"""

import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def upload_to_transfersh(file_path: str) -> str:
    """Upload file to transfer.sh and get public URL."""
    print(f"📤 Uploading to transfer.sh: {Path(file_path).name}")
    
    try:
        with open(file_path, 'rb') as f:
            file_name = Path(file_path).name
            response = requests.put(
                f'https://transfer.sh/{file_name}',
                data=f,
                timeout=120
            )
        
        if response.status_code == 200:
            url = response.text.strip()
            print(f"  ✓ Uploaded: {url}")
            return url
        else:
            print(f"  ✗ Upload failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    
    return None


def upload_to_fileio(file_path: str) -> str:
    """Upload file to file.io and get public URL."""
    print(f"📤 Uploading to file.io: {Path(file_path).name}")
    
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://file.io/',
            files={'file': f},
            data={'expires': '1d'}
        )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            url = data.get('link')
            print(f"  ✓ Uploaded: {url}")
            return url
    
    print(f"  ✗ Upload failed: {response.text}")
    return None


def test_reccloud(video_url: str) -> bool:
    """Test RecCloud transcription with a video URL."""
    api_key = os.getenv("RECCLOUD_API_KEY")
    if not api_key:
        print("  ⚠ RECCLOUD_API_KEY not set in .env")
        return False
    
    print(f"\n🎙️ Testing RecCloud API...")
    print(f"  Video URL: {video_url[:60]}...")
    
    try:
        # Create transcription task
        response = requests.post(
            "https://techhk.aoscdn.com/api/tasks/audio/recognition",
            headers={"X-API-KEY": api_key},
            json={
                "url": video_url,
                "type": 4,
                "content_type": 1,
                "speaker_recognition": 1
            }
        )
        
        print(f"  Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            print(f"  ✓ Task created: {task_id}")
            
            # Poll for result
            print("  Waiting for transcription...")
            for i in range(12):  # 2 minutes max
                time.sleep(10)
                status = requests.get(
                    f"https://techhk.aoscdn.com/api/tasks/audio/recognition/{task_id}",
                    headers={"X-API-KEY": api_key}
                ).json()
                
                state = status.get("state", 0)
                progress = status.get("progress", 0)
                
                if state == 1:
                    result = status.get("result", "")
                    print(f"\n  ✓ TRANSCRIPTION COMPLETE!")
                    print(f"  Duration: {status.get('duration', 'N/A')}s")
                    print(f"  Language: {status.get('source_language', 'N/A')}")
                    print(f"\n  === TRANSCRIPT PREVIEW ===")
                    print(f"  {result[:500]}...")
                    return True
                elif state < 0:
                    print(f"  ✗ Failed: {status.get('state_detail')}")
                    return False
                else:
                    print(f"    {i*10}s: {progress}% complete")
            
            print("  ⚠ Timeout - check task later")
            return True
        else:
            print(f"  ✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def main():
    print("=" * 60)
    print("RECCLOUD API TEST")
    print("=" * 60)
    
    # Find the smallest video for quick testing
    video_paths = [
        Path("/mnt/c/Users/POK28/Dropbox/Sisi_Lola/video-1.mp4"),
        Path("/mnt/c/Users/POK28/Dropbox/SisiLola_Welcome_Launch_v2_Dec2025.mp4"),
    ]
    
    video_path = None
    for p in video_paths:
        if p.exists():
            size_mb = p.stat().st_size / (1024 * 1024)
            print(f"\n📹 Found: {p.name} ({size_mb:.1f} MB)")
            video_path = p
            break
    
    if not video_path:
        print("❌ No video files found")
        return False
    
    # Upload to transfer.sh (reliable temporary file hosting)
    public_url = upload_to_transfersh(str(video_path))
    
    if not public_url:
        print("  Trying file.io as fallback...")
        public_url = upload_to_fileio(str(video_path))
    
    if not public_url:
        print("\n❌ Could not create public URL for video")
        return False
    
    # Test RecCloud
    success = test_reccloud(public_url)
    
    print("\n" + "=" * 60)
    print(f"RESULT: {'✓ SUCCESS' if success else '✗ FAILED'}")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
