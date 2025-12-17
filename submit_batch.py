#!/usr/bin/env python3
"""Submit videos to RecCloud with proper rate limiting."""

import requests
import time
import json
from pathlib import Path
from datetime import datetime

API_KEY = 'wxbgr07ikdtvgnws4'
API_URL = 'https://techhk.aoscdn.com/api/tasks/audio/recognition'

# Videos to submit (dl=1 for direct download)
VIDEOS = {
    'authentic_video_003': 'https://www.dropbox.com/scl/fi/yh1f82znevd69sjmln2z7/authentic_video_003.mp4?rlkey=s3a88s7qlxkem68a50k9z08iw&st=k7st3f9t&dl=1',
}

# Already submitted
COMPLETED = {
    'authentic_video_001': '8ef57367-6d0a-4179-afac-eef2b1b2dc73',
    'authentic_video_002': '47d4405b-4ed3-4d03-9ad4-f9cb86f57c97',
}

OUTPUT_DIR = Path('ml_training/datasets/transcriptions')

def submit_video(name, url):
    """Submit a video with retry on rate limit."""
    headers = {'X-API-KEY': API_KEY}
    
    for attempt in range(5):
        try:
            response = requests.post(API_URL, headers=headers, data={'url': url}, timeout=60)
            
            if response.status_code == 200:
                task_id = response.json().get('data', {}).get('task_id')
                return task_id
            elif response.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"  ⏳ Rate limited. Waiting {wait}s (attempt {attempt+1}/5)...")
                time.sleep(wait)
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:100]}")
                return None
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            time.sleep(10)
    
    return None

def main():
    print("=" * 60)
    print("SUBMITTING VIDEOS TO RECCLOUD")
    print("=" * 60)
    
    results = dict(COMPLETED)
    
    for i, (name, url) in enumerate(VIDEOS.items()):
        if name in COMPLETED:
            print(f"\n[{i+1}/{len(VIDEOS)}] {name} - Already submitted ✅")
            continue
        
        print(f"\n[{i+1}/{len(VIDEOS)}] {name}")
        print(f"  🔗 URL: {url[:60]}...")
        
        task_id = submit_video(name, url)
        
        if task_id:
            print(f"  ✅ Task ID: {task_id}")
            results[name] = task_id
        else:
            print(f"  ❌ Failed")
        
        # Wait between submissions
        if i < len(VIDEOS) - 1:
            print("  ⏳ Waiting 20 seconds...")
            time.sleep(20)
    
    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_file = OUTPUT_DIR / 'task_ids.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("ALL TASK IDs")
    print("=" * 60)
    for name, tid in results.items():
        print(f"  {name}: {tid}")
    print(f"\nSaved to: {results_file}")

if __name__ == "__main__":
    main()
