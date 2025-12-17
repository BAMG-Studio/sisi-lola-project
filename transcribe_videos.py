#!/usr/bin/env python3
"""
Sisi Lola Video Transcription Script
=====================================
Submits videos to RecCloud for transcription using Dropbox shared links.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
RECCLOUD_API_KEY = os.getenv("RECCLOUD_API_KEY")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

RECCLOUD_BASE_URL = "https://techhk.aoscdn.com/api"

# Video directories
PROJECT_ROOT = Path(__file__).parent
RENDER_OUTPUT = PROJECT_ROOT / "06_RENDER_OUTPUT"
EXTERNAL_VIDEOS = PROJECT_ROOT / "ml_training" / "external_videos"
OUTPUT_DIR = PROJECT_ROOT / "ml_training" / "datasets" / "transcriptions"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_dropbox_client():
    """Get authenticated Dropbox client."""
    try:
        import dropbox
        if DROPBOX_APP_KEY and DROPBOX_REFRESH_TOKEN:
            dbx = dropbox.Dropbox(
                app_key=DROPBOX_APP_KEY,
                oauth2_refresh_token=DROPBOX_REFRESH_TOKEN
            )
            # Test connection
            account = dbx.users_get_current_account()
            print(f"✅ Connected to Dropbox as: {account.name.display_name}")
            return dbx
    except Exception as e:
        print(f"❌ Dropbox connection failed: {e}")
    return None


def get_dropbox_shared_link(dbx, local_path: str) -> str:
    """Create or get Dropbox shared link for a file."""
    # Convert Windows path to Dropbox path
    local_path = str(local_path).replace("\\", "/")
    
    # Find Dropbox portion of path
    if "Dropbox" in local_path:
        idx = local_path.find("Dropbox")
        dropbox_path = "/" + local_path[idx + len("Dropbox") + 1:]
    elif "dropbox" in local_path.lower():
        idx = local_path.lower().find("dropbox")
        dropbox_path = "/" + local_path[idx + len("dropbox") + 1:]
    else:
        print(f"❌ Not a Dropbox path: {local_path}")
        return None
    
    # Clean up path
    dropbox_path = dropbox_path.replace("//", "/").replace("C:/Users/POK28/", "")
    if dropbox_path.startswith("/Dropbox"):
        dropbox_path = dropbox_path[8:]  # Remove /Dropbox
    
    print(f"📁 Dropbox path: {dropbox_path}")
    
    try:
        # Try to create shared link
        import dropbox.exceptions
        
        try:
            shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            # CRITICAL: Use ?dl=1 for direct download, not ?dl=0
            url = shared_link.url.replace("?dl=0", "?dl=1").replace("&dl=0", "&dl=1")
            if "dl=1" not in url:
                url = url + ("&dl=1" if "?" in url else "?dl=1")
            print(f"✅ Created shared link: {url[:60]}...")
            return url
        except dropbox.exceptions.ApiError as e:
            if "shared_link_already_exists" in str(e):
                # Get existing link
                links = dbx.sharing_list_shared_links(path=dropbox_path)
                if links.links:
                    url = links.links[0].url.replace("?dl=0", "?dl=1").replace("&dl=0", "&dl=1")
                    if "dl=1" not in url:
                        url = url + ("&dl=1" if "?" in url else "?dl=1")
                    print(f"✅ Using existing shared link: {url[:60]}...")
                    return url
            print(f"❌ Dropbox API error: {e}")
            return None
    except Exception as e:
        print(f"❌ Error creating shared link: {e}")
        return None


def create_transcription_task(video_url: str, language: str = "auto") -> dict:
    """Create RecCloud transcription task."""
    print(f"🎬 Creating transcription task for: {video_url[:60]}...")
    
    headers = {
        "X-API-KEY": RECCLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url,
        "type": 4,  # 4 = audio/video transcription
        "content_type": 1,  # 1 = video
        "speaker_recognition": 1  # Enable speaker diarization
    }
    
    if language != "auto":
        payload["language"] = language
    
    try:
        response = requests.post(
            f"{RECCLOUD_BASE_URL}/tasks/audio/recognition",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Handle nested response format: {"status": 200, "data": {"task_id": "..."}}
        task_id = result.get("task_id") or (result.get("data", {}).get("task_id"))
        
        if task_id:
            print(f"✅ Task created: {task_id}")
            return {"task_id": task_id, "raw_response": result}
        else:
            print(f"❌ No task_id in response: {result}")
            return None
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None


def check_task_status(task_id: str) -> dict:
    """Check RecCloud task status."""
    headers = {
        "X-API-KEY": RECCLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{RECCLOUD_BASE_URL}/tasks/{task_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error checking task status: {e}")
        return None


def find_videos_to_process():
    """Find all videos to process."""
    videos = []
    
    # 1. Sisi Lola authentic videos
    authentic_dir = RENDER_OUTPUT
    if authentic_dir.exists():
        for video in authentic_dir.glob("authentic_video_*.mp4"):
            videos.append({
                "path": video,
                "category": "sisi_lola_authentic",
                "name": video.stem
            })
    
    # 2. YouTube/HeyGen videos
    youtube_dir = RENDER_OUTPUT / "youtube_videos"
    if youtube_dir.exists():
        for video in youtube_dir.glob("*.mp4"):
            videos.append({
                "path": video,
                "category": "sisi_lola_youtube",
                "name": video.stem
            })
    
    # 3. External TED Talk (completed download)
    ted_dir = EXTERNAL_VIDEOS / "tier1_ted"
    if ted_dir.exists():
        for video in ted_dir.glob("*.mp4"):
            videos.append({
                "path": video,
                "category": "external_ted",
                "name": video.stem
            })
    
    return videos


def save_job_manifest(jobs: list):
    """Save job manifest for tracking."""
    manifest_path = OUTPUT_DIR / "transcription_jobs.json"
    manifest = {
        "created": datetime.now().isoformat(),
        "jobs": jobs
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, default=str)
    
    print(f"📝 Saved job manifest to: {manifest_path}")


def main():
    print("=" * 60)
    print("SISI LOLA VIDEO TRANSCRIPTION")
    print("=" * 60)
    
    # Check API key
    if not RECCLOUD_API_KEY:
        print("❌ RECCLOUD_API_KEY not set!")
        return
    
    print(f"✅ RecCloud API Key: {RECCLOUD_API_KEY[:10]}...")
    
    # Connect to Dropbox
    dbx = get_dropbox_client()
    if not dbx:
        print("❌ Cannot proceed without Dropbox connection")
        return
    
    # Find videos
    videos = find_videos_to_process()
    print(f"\n📹 Found {len(videos)} videos to process:")
    for v in videos:
        print(f"   - [{v['category']}] {v['name']}")
    
    if not videos:
        print("❌ No videos found!")
        return
    
    # Process each video
    jobs = []
    for i, video in enumerate(videos, 1):
        print(f"\n{'=' * 60}")
        print(f"Processing {i}/{len(videos)}: {video['name']}")
        print("=" * 60)
        
        # Get Dropbox shared link
        shared_url = get_dropbox_shared_link(dbx, str(video['path']))
        
        if not shared_url:
            print(f"⏩ Skipping: Could not get shared link")
            jobs.append({
                "video": video['name'],
                "category": video['category'],
                "status": "failed",
                "error": "Could not create Dropbox shared link"
            })
            continue
        
        # Create transcription task
        result = create_transcription_task(shared_url, language="auto")
        
        if result and result.get("task_id"):
            jobs.append({
                "video": video['name'],
                "category": video['category'],
                "path": str(video['path']),
                "dropbox_url": shared_url,
                "task_id": result['task_id'],
                "status": "submitted",
                "submitted_at": datetime.now().isoformat()
            })
        else:
            jobs.append({
                "video": video['name'],
                "category": video['category'],
                "status": "failed",
                "error": "RecCloud task creation failed"
            })
        
        # Small delay between requests to avoid rate limiting
        time.sleep(5)
    
    # Save manifest
    save_job_manifest(jobs)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    submitted = sum(1 for j in jobs if j['status'] == 'submitted')
    failed = sum(1 for j in jobs if j['status'] == 'failed')
    print(f"✅ Submitted: {submitted}")
    print(f"❌ Failed: {failed}")
    print(f"\n📁 Job manifest saved to: {OUTPUT_DIR / 'transcription_jobs.json'}")
    print("\nTo check status, run:")
    print("  python check_transcription_status.py")


if __name__ == "__main__":
    main()
