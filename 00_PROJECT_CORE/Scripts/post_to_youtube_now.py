"""Post to YouTube - Auto-retry with wait"""
import json
import time
from pathlib import Path
from multi_platform_poster import MultiPlatformPoster

content_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue"
content_files = sorted(content_dir.glob("content_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
latest_content = content_files[0]

with open(latest_content, 'r', encoding='utf-8') as f:
    content = json.load(f)

packages = content.get('content_packages', [])
youtube_pkg = next((p for p in packages if p['platform'] == 'youtube'), None)

video_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "generated"
latest_video = max(video_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)

media_assets = {'youtube': str(latest_video)}

print(f"[INFO] Content: {latest_content.name}")
print(f"[INFO] Video: {latest_video.name}")
print(f"[INFO] Title: {youtube_pkg['caption'].split(chr(10))[0][:100]}")

poster = MultiPlatformPoster()

for attempt in range(3):
    print(f"\n[ATTEMPT {attempt + 1}/3] Posting to YouTube...")
    result = poster.post_content_package(youtube_pkg, media_assets)
    
    if result['status'] == 'success':
        print(f"\n[SUCCESS] Video posted!")
        print(f"[URL] {result.get('url', 'N/A')}")
        break
    elif 'recently' in result.get('message', ''):
        print(f"[WAIT] API propagating, waiting 30 seconds...")
        time.sleep(30)
    else:
        print(f"[ERROR] {result.get('message', 'Unknown error')}")
        break
