import os
import sys
import sqlite3
import json
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "sisi_lola_api"))

# Load environment variables
load_dotenv(PROJECT_ROOT / "sisi_lola_api" / ".env")

from app.utils.heygen import start_heygen_video, poll_heygen_video

DB_PATH = os.environ.get('PROJECT_DB_PATH', str(PROJECT_ROOT / "00_PROJECT_CORE" / "PROJECT_DB.sqlite"))
MEDIA_OUTPUT_DIR = PROJECT_ROOT / "03_MEDIA_ASSETS" / "generated"
MEDIA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_video_for_post(post_id: int, title: str, caption: str, platform: str):
    """Generate video using HeyGen API"""
    print(f"\n🎬 Generating video for Post {post_id}: {title}")
    
    # Determine aspect ratio based on platform
    aspect_ratio = "9:16" if platform in ['TikTok', 'Instagram', 'YouTube'] else "16:9"
    
    # Use title + caption as script (truncated to reasonable length for demo)
    # In production, we'd use a dedicated script field
    script = f"{title}. {caption}"[:500] 
    
    try:
        print(f"   Requesting HeyGen generation (Ratio: {aspect_ratio})...")
        start_response = await start_heygen_video(
            script=script,
            aspect_ratio=aspect_ratio,
            caption=True
        )
        
        video_id = start_response.get("data", {}).get("video_id")
        if not video_id:
            print(f"❌ Failed to start generation: {start_response}")
            return None
            
        print(f"   Job started! Video ID: {video_id}")
        print("   Polling for completion (this may take a few minutes)...")
        
        result = await poll_heygen_video(video_id)
        video_url = result.get("data", {}).get("video_url")
        
        if video_url:
            print(f"✅ Generation Complete! URL: {video_url}")
            
            # Download the video
            import requests
            response = requests.get(video_url)
            filename = f"post_{post_id}_{int(time.time())}.mp4"
            filepath = MEDIA_OUTPUT_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            print(f"💾 Saved to: {filepath}")
            return str(filepath)
            
        else:
            print(f"❌ Failed to get video URL from result: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return None

async def process_pending_posts():
    print("🚀 Starting Live Content Production...")
    
    # Check for HeyGen API Key
    if not os.getenv("HEYGEN_API_KEY"):
        print("❌ Error: HEYGEN_API_KEY not found in .env")
        print("Please add your HeyGen API Key to sisi_lola_api/.env to enable live generation.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Fetch pending posts that don't have a custom media path (or have the placeholder)
    cursor.execute("SELECT * FROM scheduled_posts WHERE status = 'pending' ORDER BY priority DESC")
    posts = [dict(row) for row in cursor.fetchall()]
    
    if not posts:
        print("No pending posts found.")
        conn.close()
        return

    print(f"Found {len(posts)} pending posts.")
    
    for post in posts:
        # Skip if already has a real generated file (simple check for 'generated' in path)
        if post['media_path'] and 'generated' in post['media_path']:
            print(f"⏩ Skipping Post {post['id']} (Already has generated media)")
            continue
            
        # Parse platforms to determine aspect ratio preference
        platforms = json.loads(post['platforms']) if post['platforms'] else ['Instagram']
        primary_platform = platforms[0] if platforms else 'Instagram'
        
        # Generate Video
        video_path = await generate_video_for_post(
            post['id'], 
            post['title'], 
            post['caption'], 
            primary_platform
        )
        
        if video_path:
            # Update DB
            cursor.execute(
                "UPDATE scheduled_posts SET media_path = ? WHERE id = ?", 
                (video_path, post['id'])
            )
            conn.commit()
            print(f"✅ Updated Post {post['id']} with new media path.")
            
            # Stop after one for testing purposes
            print("🛑 Stopping after one generation for verification.")
            break
        else:
            print(f"⚠️  Skipping DB update for Post {post['id']} due to generation failure.")
            
    conn.close()
    print("\n🏁 Content Production Run Complete.")

if __name__ == "__main__":
    asyncio.run(process_pending_posts())
