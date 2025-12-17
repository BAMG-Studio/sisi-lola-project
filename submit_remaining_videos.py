#!/usr/bin/env python3
"""
Submit remaining videos to RecCloud for transcription.
Uses form data (not JSON) which works better with RecCloud API.
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
import dropbox

load_dotenv()

RECCLOUD_API_KEY = os.getenv("RECCLOUD_API_KEY", "wxbgr07ikdtvgnws4")
API_URL = "https://techhk.aoscdn.com/api/tasks/audio/recognition"

# Initialize Dropbox
dbx = dropbox.Dropbox(
    app_key=os.getenv('DROPBOX_APP_KEY'),
    app_secret=os.getenv('DROPBOX_APP_SECRET'),
    oauth2_refresh_token=os.getenv('DROPBOX_REFRESH_TOKEN')
)

# Already submitted task IDs
already_submitted = {
    'authentic_video_001': '8ef57367-6d0a-4179-afac-eef2b1b2dc73',
}

# Videos to process
videos = [
    {'name': 'authentic_video_002', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_002.mp4', 'category': 'authentic'},
    {'name': 'authentic_video_003', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_003.mp4', 'category': 'authentic'},
    {'name': 'authentic_video_004', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_004.mp4', 'category': 'authentic'},
    {'name': 'authentic_video_005', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_005.mp4', 'category': 'authentic'},
    {'name': 'authentic_video_006', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_006.mp4', 'category': 'authentic'},
    {'name': 'authentic_video_007', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_007.mp4', 'category': 'authentic'},
    {'name': 'authentic_video_008', 'dropbox_path': '/Sisi_Lola/06_RENDER_OUTPUT/authentic_video_008.mp4', 'category': 'authentic'},
    {'name': 'heygen_20251126_143538', 'dropbox_path': '/Sisi_Lola/youtube_videos/heygen_20251126_143538.mp4', 'category': 'heygen'},
    {'name': 'heygen_20251126_181318', 'dropbox_path': '/Sisi_Lola/youtube_videos/heygen_20251126_181318.mp4', 'category': 'heygen'},
    {'name': 'The danger of a single story', 'dropbox_path': '/Sisi_Lola/ml_training/external_videos/tier1_ted/The danger of a single story.mp4', 'category': 'ted'},
]

def get_shared_link(dropbox_path: str) -> str:
    """Get Dropbox shared link with dl=1 for direct download."""
    try:
        import dropbox.exceptions
        
        try:
            shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            url = shared_link.url
        except dropbox.exceptions.ApiError as e:
            if "shared_link_already_exists" in str(e):
                links = dbx.sharing_list_shared_links(path=dropbox_path)
                if links.links:
                    url = links.links[0].url
                else:
                    return None
            else:
                raise
        
        # Ensure dl=1 for direct download
        if "?dl=0" in url:
            url = url.replace("?dl=0", "?dl=1")
        elif "&dl=0" in url:
            url = url.replace("&dl=0", "&dl=1")
        elif "dl=" not in url:
            url = url + ("&dl=1" if "?" in url else "?dl=1")
        
        return url
    except Exception as e:
        print(f"  ❌ Error getting shared link: {e}")
        return None


def submit_video(url: str) -> str:
    """Submit video to RecCloud using form data."""
    headers = {"X-API-KEY": RECCLOUD_API_KEY}
    
    # Use form data, not JSON - this works better
    data = {"url": url}
    
    try:
        response = requests.post(API_URL, headers=headers, data=data, timeout=60)
        
        if response.status_code == 429:
            print("  ⏳ Rate limited, waiting 60 seconds...")
            time.sleep(60)
            response = requests.post(API_URL, headers=headers, data=data, timeout=60)
        
        response.raise_for_status()
        result = response.json()
        task_id = result.get("data", {}).get("task_id") or result.get("task_id")
        return task_id
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("SUBMITTING REMAINING VIDEOS TO RECCLOUD")
    print("=" * 60)
    
    results = []
    
    for i, video in enumerate(videos):
        name = video['name']
        
        # Skip already submitted
        if name in already_submitted:
            print(f"\n[{i+1}/{len(videos)}] {name} - Already submitted ✅")
            results.append({
                'name': name,
                'category': video['category'],
                'task_id': already_submitted[name],
                'status': 'already_submitted'
            })
            continue
        
        print(f"\n[{i+1}/{len(videos)}] {name}")
        print(f"  📁 Getting shared link for: {video['dropbox_path']}")
        
        url = get_shared_link(video['dropbox_path'])
        if not url:
            print(f"  ❌ Could not get shared link")
            results.append({
                'name': name,
                'category': video['category'],
                'task_id': None,
                'status': 'failed',
                'error': 'No shared link'
            })
            continue
        
        print(f"  🔗 URL: {url[:70]}...")
        print(f"  🎬 Submitting to RecCloud...")
        
        task_id = submit_video(url)
        
        if task_id:
            print(f"  ✅ Task ID: {task_id}")
            results.append({
                'name': name,
                'category': video['category'],
                'task_id': task_id,
                'status': 'submitted',
                'submitted_at': datetime.now().isoformat()
            })
        else:
            print(f"  ❌ Failed to submit")
            results.append({
                'name': name,
                'category': video['category'],
                'task_id': None,
                'status': 'failed'
            })
        
        # Wait between requests to avoid rate limiting
        if i < len(videos) - 1:
            print(f"  ⏳ Waiting 15 seconds before next request...")
            time.sleep(15)
    
    # Save results
    output_path = Path("ml_training/datasets/transcriptions/submission_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            'submitted_at': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    submitted = sum(1 for r in results if r['status'] in ['submitted', 'already_submitted'])
    failed = sum(1 for r in results if r['status'] == 'failed')
    print(f"✅ Submitted: {submitted}")
    print(f"❌ Failed: {failed}")
    print(f"\nTask IDs:")
    for r in results:
        if r.get('task_id'):
            print(f"  {r['name']}: {r['task_id']}")
    
    print(f"\n📁 Results saved to: {output_path}")


if __name__ == "__main__":
    main()
