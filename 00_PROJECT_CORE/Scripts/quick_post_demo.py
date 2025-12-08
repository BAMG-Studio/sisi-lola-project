"""
Quick Demo: Post Generated Content to YouTube
"""

import json
from pathlib import Path
from multi_platform_poster import MultiPlatformPoster

# Find the most recent content file
content_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue"
content_files = sorted(content_dir.glob("content_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

if not content_files:
    print("[ERROR] No content files found. Run sisi_lola_content_generator.py first")
    exit(1)

latest_content = content_files[0]
print(f"[INFO] Using content file: {latest_content.name}")

# Load content
with open(latest_content, 'r', encoding='utf-8') as f:
    content = json.load(f)

packages = content.get('content_packages', [])
print(f"[INFO] Found {len(packages)} platform packages")

# Display what we have
print("\n" + "="*70)
print("AVAILABLE CONTENT PACKAGES")
print("="*70)
for i, pkg in enumerate(packages, 1):
    print(f"{i}. {pkg['platform'].upper()}")
    print(f"   Angle: {pkg['angle'][:80]}")
    hook_preview = pkg['hook'][:80].encode('ascii', 'ignore').decode('ascii')
    print(f"   Hook: {hook_preview}...")
    print()

# Check for existing videos
video_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "generated"
videos = list(video_dir.glob("*.mp4"))

print("="*70)
print(f"AVAILABLE VIDEOS: {len(videos)} files")
print("="*70)

if videos:
    latest_video = max(videos, key=lambda p: p.stat().st_mtime)
    print(f"[INFO] Will use: {latest_video.name}")
    
    # Prepare media assets
    media_assets = {
        'youtube': str(latest_video),
        'tiktok': str(latest_video),
        'instagram': str(latest_video)
    }
    
    print("\n" + "="*70)
    print("READY TO POST")
    print("="*70)
    print(f"Content: {latest_content.name}")
    print(f"Video: {latest_video.name}")
    print(f"Platforms: {len(packages)}")
    
    response = input("\nPost to YouTube now? (y/n): ").strip().lower()
    
    if response == 'y':
        poster = MultiPlatformPoster()
        
        # Find YouTube package
        youtube_pkg = next((p for p in packages if p['platform'] == 'youtube'), None)
        
        if youtube_pkg:
            print("\n[POSTING] Uploading to YouTube...")
            result = poster.post_content_package(youtube_pkg, media_assets)
            
            print("\n" + "="*70)
            print("RESULT")
            print("="*70)
            print(json.dumps(result, indent=2))
        else:
            print("[ERROR] No YouTube package found in content")
    else:
        print("[CANCELLED] Post cancelled by user")
else:
    print("[WARNING] No video files found in 03_MEDIA_ASSETS/generated/")
    print("[INFO] Content packages are ready, but need video files to post")
    print("\nYou can:")
    print("  1. Add video files to 03_MEDIA_ASSETS/generated/")
    print("  2. Or integrate HeyGen/Runway to generate videos automatically")
