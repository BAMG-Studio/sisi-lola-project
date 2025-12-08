#!/usr/bin/env python3
"""
Test YouTube Posting
Verifies that the YouTube integration works with the new credentials.
Uploads a video as PRIVATE.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add Scripts directory to path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "sisi_lola_api" / ".env")

from unified_api_poster import UnifiedAPIPoster, PostContent

def test_youtube_upload():
    print("🚀 Starting YouTube Upload Test...")
    
    # 1. Setup paths
    media_dir = PROJECT_ROOT / "03_MEDIA_ASSETS" / "generated"
    video_path = media_dir / "static_video_Voice_Sample_Formal_Presentation.mp4"
    
    if not video_path.exists():
        print(f"❌ Error: Test video not found at {video_path}")
        return

    print(f"📦 Using video: {video_path.name}")
    
    # 2. Initialize Poster
    poster = UnifiedAPIPoster()
    
    # 3. Create Content
    content = PostContent(
        title="Sisi Lola - System Test (Private)",
        caption="This is a test upload from the Sisi Lola Automation System.\n\n#SisiLola #Test",
        media_path=str(video_path),
        media_type="video",
        tags=["test", "automation"],
        platform_overrides={
            "youtube": {
                "privacyStatus": "private"  # IMPORTANT: Upload as private
            }
        }
    )
    
    # 4. Execute Post
    print("\n📤 Uploading to YouTube (Private)...")
    results = poster.post_to_all_platforms(content, platforms=['YouTube'])
    
    # 5. Report
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    for result in results:
        if result.success:
            print(f"✅ SUCCESS: {result.platform}")
            print(f"   Video ID: {result.post_id}")
            print(f"   URL: {result.post_url}")
            print("   Note: Video is PRIVATE. You must be logged in to view it.")
        else:
            print(f"❌ FAILED: {result.platform}")
            print(f"   Error: {result.error_message}")
            
    print("="*60)

if __name__ == "__main__":
    test_youtube_upload()
