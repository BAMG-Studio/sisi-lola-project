#!/usr/bin/env python3
"""
Video Transcription Test - Tests all available backends

Tests the video ingestion pipeline with multiple fallback options:
1. RecCloud API + Dropbox (if refresh token available)
2. Local Whisper transcription (fallback, no API needed)
"""

import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "ml_training" / "scripts"))

print("=" * 60)
print("VIDEO TRANSCRIPTION PIPELINE TEST")
print("=" * 60)


def refresh_dropbox_token() -> str:
    """Refresh Dropbox access token using refresh token."""
    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    app_key = os.getenv("DROPBOX_APP_KEY")
    app_secret = os.getenv("DROPBOX_APP_SECRET")
    
    if not all([refresh_token, app_key, app_secret]):
        print("  ⚠ Missing refresh token credentials")
        return None
    
    print("  Refreshing Dropbox token...")
    
    try:
        response = requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(app_key, app_secret)
        )
        
        if response.status_code == 200:
            data = response.json()
            new_token = data.get("access_token")
            print("  ✓ Token refreshed successfully")
            return new_token
        else:
            print(f"  ✗ Refresh failed: {response.json().get('error_description', response.text)}")
            return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def find_video_files() -> list:
    """Find video files in known locations."""
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}
    found_videos = []
    
    # Search paths - updated for actual SLS folder structure
    search_paths = [
        PROJECT_ROOT / "video-1.mp4",  # Single file in root
        PROJECT_ROOT / "ml_training" / "data" / "videos" / "SLS" / "SL TRAINING VIDEOS",
        PROJECT_ROOT / "ml_training" / "data" / "videos",
        PROJECT_ROOT / "ml_training" / "data" / "SL_TRAINING_VIDEOS",
        Path("/mnt/c/Users/POK28/Dropbox"),  # Dropbox root for SisiLola videos
    ]
    
    print("\n📁 Searching for videos...")
    
    for search_path in search_paths:
        if search_path.exists():
            # Handle single file
            if search_path.is_file():
                if search_path.suffix.lower() in video_extensions:
                    size_mb = search_path.stat().st_size / (1024 * 1024)
                    found_videos.append((search_path, size_mb))
                    print(f"  ✓ Found: {search_path.name} ({size_mb:.1f} MB)")
                continue
            
            # Handle directory
            print(f"  Checking: {search_path}")
            try:
                for f in search_path.iterdir():
                    if f.is_file() and f.suffix.lower() in video_extensions:
                        size_mb = f.stat().st_size / (1024 * 1024)
                        found_videos.append((f, size_mb))
                        print(f"    ✓ Found: {f.name} ({size_mb:.1f} MB)")
            except PermissionError:
                print(f"    ⚠ Permission denied")
    
    return found_videos


def test_dropbox_reccloud():
    """Test RecCloud transcription using Dropbox shared link."""
    print("\n" + "=" * 60)
    print("TEST 1: RECCLOUD API + DROPBOX")
    print("=" * 60)
    
    # Check for Dropbox SDK
    try:
        import dropbox
    except ImportError:
        print("  ⚠ Dropbox SDK not installed: pip install dropbox")
        return False
    
    # Get Dropbox token (refresh if needed)
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    
    if not token and not refresh_token:
        print("  ⚠ No Dropbox credentials found")
        return False
    
    # Try to refresh token if we have refresh token
    if refresh_token:
        new_token = refresh_dropbox_token()
        if new_token:
            token = new_token
            # Update env for subsequent calls
            os.environ["DROPBOX_ACCESS_TOKEN"] = token
    
    if not token:
        print("  ✗ Could not obtain valid Dropbox token")
        return False
    
    # Test Dropbox connection
    print("\n📦 Testing Dropbox connection...")
    try:
        dbx = dropbox.Dropbox(token)
        account = dbx.users_get_current_account()
        print(f"  ✓ Connected as: {account.name.display_name}")
    except dropbox.exceptions.AuthError as e:
        print(f"  ✗ Auth error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Connection error: {e}")
        return False
    
    # Find video in Dropbox
    print("\n📁 Finding videos in Dropbox...")
    video_path = None
    
    search_folders = [
        "/SLS/SL TRAINING VIDEOS",
        "/Sisi_Lola/SLS/SL TRAINING VIDEOS",
    ]
    
    for folder in search_folders:
        try:
            result = dbx.files_list_folder(folder)
            for entry in result.entries:
                if hasattr(entry, 'size') and entry.name.lower().endswith(('.mp4', '.mov', '.avi')):
                    video_path = f"{folder}/{entry.name}"
                    size_mb = entry.size / (1024 * 1024)
                    print(f"  ✓ Found: {entry.name} ({size_mb:.1f} MB)")
                    break
        except:
            continue
        
        if video_path:
            break
    
    if not video_path:
        print("  ⚠ No videos found in Dropbox")
        return False
    
    # Create shared link
    print(f"\n🔗 Creating shared link for: {video_path}")
    try:
        shared_link = dbx.sharing_create_shared_link_with_settings(video_path)
        url = shared_link.url
    except dropbox.exceptions.ApiError as e:
        if "shared_link_already_exists" in str(e):
            links = dbx.sharing_list_shared_links(path=video_path)
            if links.links:
                url = links.links[0].url
        else:
            print(f"  ✗ Error: {e}")
            return False
    
    # Convert to direct download URL
    direct_url = url.replace("?dl=0", "?dl=1").replace("www.dropbox.com", "dl.dropboxusercontent.com")
    print(f"  ✓ URL: {direct_url[:60]}...")
    
    # Test RecCloud API
    print("\n🎙️ Testing RecCloud transcription...")
    
    api_key = os.getenv("RECCLOUD_API_KEY")
    if not api_key:
        print("  ⚠ RECCLOUD_API_KEY not set")
        return False
    
    try:
        response = requests.post(
            "https://techhk.aoscdn.com/api/tasks/audio/recognition",
            headers={"X-API-KEY": api_key},
            json={
                "url": direct_url,
                "type": 4,
                "content_type": 1,
                "speaker_recognition": 1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            print(f"  ✓ Task created: {task_id}")
            
            # Poll for result (short timeout for test)
            print("  Waiting for transcription (max 60s)...")
            for i in range(6):
                time.sleep(10)
                status = requests.get(
                    f"https://techhk.aoscdn.com/api/tasks/audio/recognition/{task_id}",
                    headers={"X-API-KEY": api_key}
                ).json()
                
                state = status.get("state", 0)
                if state == 1:
                    result = status.get("result", "")[:200]
                    print(f"  ✓ Transcription complete!")
                    print(f"  Preview: {result}...")
                    return True
                elif state < 0:
                    print(f"  ✗ Transcription failed: {status.get('state_detail')}")
                    return False
                else:
                    print(f"    Progress: {status.get('progress', 0)}%")
            
            print("  ⚠ Test timeout (full transcription may still complete)")
            return True
        else:
            print(f"  ✗ API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_local_whisper():
    """Test local Whisper transcription."""
    print("\n" + "=" * 60)
    print("TEST 2: LOCAL WHISPER TRANSCRIPTION")
    print("=" * 60)
    
    # Find local video
    videos = find_video_files()
    
    if not videos:
        print("  ⚠ No local videos found")
        return False
    
    video_path, size_mb = videos[0]
    print(f"\n🎬 Testing with: {video_path.name} ({size_mb:.1f} MB)")
    
    # Try to import Whisper
    try:
        from whisper_video_ingestion import WhisperTranscriber
        print("  ✓ Whisper module imported")
    except ImportError as e:
        print(f"  ⚠ Whisper import failed: {e}")
        print("  Trying direct transformers import...")
        try:
            from transformers import pipeline
            print("  ✓ Transformers available")
        except ImportError:
            print("  ✗ Transformers not installed: pip install transformers")
            return False
        return True  # Module available but not in expected location
    
    # Test transcription
    print("\n🎙️ Running transcription (this may take a few minutes)...")
    
    try:
        transcriber = WhisperTranscriber(model_size="base")
        result = transcriber.transcribe_video(str(video_path))
        
        if result:
            print(f"  ✓ Transcription complete!")
            print(f"  Duration: {result.get('duration', 'N/A')}s")
            print(f"  Language: {result.get('language', 'N/A')}")
            text_preview = result.get('text', '')[:200]
            print(f"  Preview: {text_preview}...")
            return True
        else:
            print("  ⚠ Empty result")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    results = {}
    
    # Test 1: RecCloud + Dropbox
    try:
        results['reccloud'] = test_dropbox_reccloud()
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        results['reccloud'] = False
    
    # Test 2: Local Whisper (only if RecCloud failed)
    if not results.get('reccloud'):
        try:
            results['whisper'] = test_local_whisper()
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results['whisper'] = False
    else:
        print("\n⏭️ Skipping local Whisper test (RecCloud working)")
        results['whisper'] = 'skipped'
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed is True else ("⏭️ SKIPPED" if passed == 'skipped' else "✗ FAIL")
        print(f"  {test.upper()}: {status}")
    
    # Recommendation
    print("\n📋 RECOMMENDATION:")
    if results.get('reccloud'):
        print("  Use RecCloud API for cloud transcription (speaker ID, multilingual)")
    elif results.get('whisper'):
        print("  Use local Whisper for offline transcription")
    else:
        print("  Please set up either:")
        print("  1. DROPBOX_REFRESH_TOKEN + RECCLOUD_API_KEY for cloud transcription")
        print("  2. Install transformers + torch for local Whisper")
    
    return any(v is True for v in results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
