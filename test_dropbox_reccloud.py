#!/usr/bin/env python3
"""
Test video transcription with local Whisper (primary) and RecCloud (fallback).
Updated to use local video files from parent Dropbox folder.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Video search paths
VIDEO_PATHS = [
    Path("/mnt/c/Users/POK28/Dropbox"),  # Parent Dropbox folder with Sisi Lola videos
    PROJECT_ROOT,  # Project root has video-1.mp4
    PROJECT_ROOT / "ml_training" / "data" / "videos",
    PROJECT_ROOT / "SLS" / "SL TRAINING VIDEOS",
]

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def find_local_videos():
    """Find video files in local paths."""
    print("\n📁 Searching for local video files...")
    videos = []
    
    for search_path in VIDEO_PATHS:
        if search_path.exists():
            print(f"  Checking: {search_path}")
            for ext in VIDEO_EXTENSIONS:
                found = list(search_path.glob(f"*{ext}"))
                for v in found:
                    if v.is_file():
                        size_mb = v.stat().st_size / (1024 * 1024)
                        videos.append((v, size_mb))
                        print(f"    ✓ {v.name} ({size_mb:.1f} MB)")
    
    return videos


def test_whisper_transcription(video_path: Path, max_duration: int = 60):
    """Test local Whisper transcription on a video."""
    try:
        import whisper
        import subprocess
        import tempfile
        
        print(f"\n🎙️ Testing Whisper transcription...")
        print(f"  Video: {video_path.name}")
        
        # Extract audio using ffmpeg
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_path = tmp.name
        
        print("  Extracting audio with ffmpeg...")
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-t", str(max_duration),  # Limit duration for testing
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ❌ FFmpeg error: {result.stderr[:200]}")
            return None
        
        print("  Loading Whisper model (base)...")
        model = whisper.load_model("base")
        
        print("  Transcribing...")
        result = model.transcribe(audio_path, language="en")
        
        # Clean up
        os.unlink(audio_path)
        
        transcript = result.get("text", "")
        print(f"\n  ✓ Transcription complete ({len(transcript)} chars)")
        print(f"  Preview: {transcript[:300]}...")
        
        return transcript
        
    except ImportError:
        print("  ⚠️ Whisper not installed. Install with: pip install openai-whisper")
        return None
    except Exception as e:
        print(f"  ❌ Whisper error: {e}")
        return None


def test_dropbox_connection():
    """Test Dropbox API connection and list files."""
    import dropbox
    
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not token:
        print("❌ DROPBOX_ACCESS_TOKEN not set")
        return None
    
    print(f"✓ Token found: {token[:20]}...")
    
    try:
        dbx = dropbox.Dropbox(token)
        
        # Test account info
        account = dbx.users_get_current_account()
        print(f"✓ Connected as: {account.name.display_name}")
        print(f"  Email: {account.email}")
        
        # List SL TRAINING VIDEOS folder
        folder_path = "/Sisi_Lola/SLS/SL TRAINING VIDEOS"
        print(f"\n📁 Listing: {folder_path}")
        
        try:
            result = dbx.files_list_folder(folder_path)
            for entry in result.entries:
                if hasattr(entry, 'size'):
                    size_mb = entry.size / (1024 * 1024)
                    print(f"  📹 {entry.name} ({size_mb:.1f} MB)")
                else:
                    print(f"  📁 {entry.name}/")
            
            return dbx
            
        except dropbox.exceptions.ApiError as e:
            print(f"❌ Folder listing failed: {e}")
            # Try listing root to find correct path
            print("\n📁 Listing root folder...")
            result = dbx.files_list_folder("")
            for entry in result.entries:
                print(f"  - {entry.name}")
            return dbx
            
    except Exception as e:
        print(f"❌ Dropbox connection failed: {e}")
        return None


def create_shared_link(dbx, file_path: str) -> str:
    """Create or get existing shared link for a file."""
    import dropbox
    
    print(f"\n🔗 Creating shared link for: {file_path}")
    
    try:
        # Try to create new shared link
        shared_link = dbx.sharing_create_shared_link_with_settings(file_path)
        url = shared_link.url
        print(f"✓ New shared link created")
        
    except dropbox.exceptions.ApiError as e:
        if "shared_link_already_exists" in str(e):
            # Get existing shared link
            links = dbx.sharing_list_shared_links(path=file_path)
            if links.links:
                url = links.links[0].url
                print(f"✓ Using existing shared link")
            else:
                raise Exception("No shared links found")
        else:
            raise
    
    # Convert to direct download URL
    direct_url = url.replace("?dl=0", "?dl=1").replace("www.dropbox.com", "dl.dropboxusercontent.com")
    print(f"  URL: {direct_url[:60]}...")
    
    return direct_url


def test_reccloud_transcription(video_url: str):
    """Test RecCloud transcription with a video URL."""
    import requests
    
    api_key = os.getenv("RECCLOUD_API_KEY")
    if not api_key:
        print("❌ RECCLOUD_API_KEY not set")
        return
    
    print(f"\n🎙️ Testing RecCloud transcription...")
    print(f"  API Key: {api_key[:8]}...")
    
    # Create transcription task
    base_url = "https://techhk.aoscdn.com/api"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url,
        "type": 4,
        "content_type": 1,
        "speaker_recognition": 1
    }
    
    print(f"  Creating task...")
    
    try:
        response = requests.post(
            f"{base_url}/tasks/audio/recognition",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"  Response status: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✓ Task created: {task_id}")
            return task_id
        else:
            print(f"❌ Task creation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ RecCloud API error: {e}")
        return None


def poll_task_status(task_id: str, max_polls: int = 30, interval: int = 10):
    """Poll task status until completion."""
    import requests
    import time
    
    api_key = os.getenv("RECCLOUD_API_KEY")
    base_url = "https://techhk.aoscdn.com/api"
    headers = {"X-API-KEY": api_key}
    
    print(f"\n⏳ Polling task status...")
    
    for i in range(max_polls):
        try:
            response = requests.get(
                f"{base_url}/tasks/audio/recognition/{task_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                state = result.get("state", 0)
                progress = result.get("progress", 0)
                
                if state == 1:  # Complete
                    print(f"\n✓ Transcription complete!")
                    duration = result.get("duration", 0)
                    source_lang = result.get("source_language", "unknown")
                    transcript = result.get("result", "")
                    
                    print(f"  Duration: {duration}s")
                    print(f"  Language: {source_lang}")
                    print(f"  Transcript ({len(transcript)} chars):")
                    print(f"  {transcript[:500]}...")
                    
                    return result
                    
                elif state < 0:  # Failed
                    print(f"❌ Task failed: {result.get('state_detail', 'Unknown')}")
                    return None
                    
                else:
                    print(f"  [{i+1}/{max_polls}] Progress: {progress}%")
                    time.sleep(interval)
            else:
                print(f"  Status check failed: {response.status_code}")
                time.sleep(interval)
                
        except Exception as e:
            print(f"  Poll error: {e}")
            time.sleep(interval)
    
    print("❌ Polling timeout")
    return None


def main():
    print("=" * 60)
    print("VIDEO TRANSCRIPTION TEST")
    print("Primary: Local Whisper | Fallback: RecCloud API")
    print("=" * 60)
    
    # Find local videos
    videos = find_local_videos()
    
    if not videos:
        print("\n❌ No video files found!")
        return
    
    print(f"\n📹 Found {len(videos)} video(s)")
    
    # Select a video for testing (prefer smaller files for faster testing)
    videos.sort(key=lambda x: x[1])  # Sort by size
    test_video, size_mb = videos[0]
    
    print(f"\n🎬 Selected for test: {test_video.name} ({size_mb:.1f} MB)")
    
    # Test 1: Local Whisper transcription
    print("\n" + "-" * 40)
    print("TEST 1: Local Whisper Transcription")
    print("-" * 40)
    
    transcript = test_whisper_transcription(test_video, max_duration=30)
    
    if transcript:
        print("\n✅ LOCAL WHISPER TEST PASSED!")
        
        # Save transcript
        output_path = PROJECT_ROOT / "ml_training" / "data" / "transcripts"
        output_path.mkdir(parents=True, exist_ok=True)
        
        transcript_file = output_path / f"{test_video.stem}_transcript.txt"
        transcript_file.write_text(transcript)
        print(f"  Saved to: {transcript_file}")
    else:
        print("\n⚠️ Whisper test skipped or failed")
        print("  Trying Dropbox + RecCloud fallback...")
        
        # Test 2: Dropbox + RecCloud (fallback)
        print("\n" + "-" * 40)
        print("TEST 2: Dropbox + RecCloud API")
        print("-" * 40)
        
        dbx = test_dropbox_connection()
        if dbx:
            # Use the first video found
            video_path = f"/Sisi_Lola/{test_video.relative_to(PROJECT_ROOT.parent)}"
            try:
                video_url = create_shared_link(dbx, video_path)
                task_id = test_reccloud_transcription(video_url)
                
                if task_id:
                    result = poll_task_status(task_id)
                    if result:
                        print("\n✅ RECCLOUD TEST PASSED!")
            except Exception as e:
                print(f"  ❌ RecCloud fallback failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
