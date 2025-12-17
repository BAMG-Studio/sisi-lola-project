#!/usr/bin/env python3
"""
Manual Video Transcription Submitter

This script submits videos to RecCloud for transcription using manually provided
Dropbox shared links.

HOW TO GET SHARED LINKS:
1. Go to dropbox.com and navigate to your video
2. Right-click the video and select "Copy link"
3. The link will look like: https://www.dropbox.com/scl/fi/xxx/video.mp4?rlkey=yyy&dl=0
4. Change dl=0 to dl=1 at the end for direct download

USAGE:
1. Edit the VIDEOS dictionary below with your video names and links
2. Run: python submit_videos_manual.py
3. Wait for transcriptions to complete
4. Run: python download_transcripts.py
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime

RECCLOUD_API_KEY = 'wxbgr07ikdtvgnws4'
API_URL = 'https://techhk.aoscdn.com/api/tasks/audio/recognition'

# Edit this dictionary with your videos
# Format: 'video_name': 'https://www.dropbox.com/scl/fi/...?dl=1'
VIDEOS = {
    # Already completed:
    # 'authentic_video_001': '8ef57367-6d0a-4179-afac-eef2b1b2dc73',  # DONE
    
    # Add your videos here (remember to use dl=1 at the end!):
    # 'authentic_video_002': 'https://www.dropbox.com/scl/fi/j7y2peffuhj5dzoddz7a3/authentic_video_002.mp4?rlkey=xxx&dl=1',
    # 'authentic_video_003': 'https://www.dropbox.com/scl/fi/xxx/authentic_video_003.mp4?rlkey=xxx&dl=1',
    # etc.
}

OUTPUT_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/transcriptions')


def submit_video(name: str, url: str) -> str:
    """Submit a video to RecCloud for transcription."""
    headers = {'X-API-KEY': RECCLOUD_API_KEY}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, data={'url': url}, timeout=60)
            
            if response.status_code == 429:
                wait_time = 60 * (attempt + 1)
                print(f"  ⏳ Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            result = response.json()
            task_id = result.get('data', {}).get('task_id') or result.get('task_id')
            return task_id
            
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
    
    return None


def main():
    if not VIDEOS:
        print("=" * 60)
        print("NO VIDEOS CONFIGURED")
        print("=" * 60)
        print("\nPlease edit this script and add your videos to the VIDEOS dictionary.")
        print("\nExample:")
        print("  VIDEOS = {")
        print("      'authentic_video_002': 'https://www.dropbox.com/scl/fi/xxx/video.mp4?rlkey=yyy&dl=1',")
        print("  }")
        print("\nTo get a Dropbox shared link:")
        print("  1. Go to dropbox.com")
        print("  2. Right-click your video → Copy link")
        print("  3. Change ?dl=0 to ?dl=1 at the end")
        return
    
    print("=" * 60)
    print("SUBMITTING VIDEOS TO RECCLOUD")
    print("=" * 60)
    
    results = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for i, (name, url) in enumerate(VIDEOS.items()):
        print(f"\n[{i+1}/{len(VIDEOS)}] {name}")
        print(f"  📎 URL: {url[:60]}...")
        
        task_id = submit_video(name, url)
        
        if task_id:
            print(f"  ✅ Task ID: {task_id}")
            results.append({
                'name': name,
                'url': url,
                'task_id': task_id,
                'status': 'submitted',
                'submitted_at': datetime.now().isoformat()
            })
        else:
            print(f"  ❌ Failed to submit")
            results.append({
                'name': name,
                'url': url,
                'status': 'failed'
            })
        
        # Wait between requests
        if i < len(VIDEOS) - 1:
            print(f"  ⏳ Waiting 15 seconds...")
            time.sleep(15)
    
    # Save results
    results_path = OUTPUT_DIR / 'manual_submission_results.json'
    with open(results_path, 'w') as f:
        json.dump({
            'submitted_at': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    submitted = sum(1 for r in results if r['status'] == 'submitted')
    failed = sum(1 for r in results if r['status'] == 'failed')
    print(f"✅ Submitted: {submitted}")
    print(f"❌ Failed: {failed}")
    
    if submitted > 0:
        print("\n📋 Task IDs to add to download_transcripts.py:")
        for r in results:
            if r.get('task_id'):
                print(f"    '{r['name']}': '{r['task_id']}',")
    
    print(f"\n📁 Results saved to: {results_path}")
    print("\nNext steps:")
    print("  1. Wait 5-15 minutes for transcriptions to complete")
    print("  2. Add the task IDs above to download_transcripts.py")
    print("  3. Run: python download_transcripts.py")


if __name__ == "__main__":
    main()
