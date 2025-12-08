import os
import sys
import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv

# Add Scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "sisi_lola_api" / ".env")

from unified_api_poster import UnifiedAPIPoster, PostContent

DB_PATH = os.environ.get('PROJECT_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PROJECT_DB.sqlite'))
SAMPLE_VIDEO = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '03_MEDIA_ASSETS', 'CLI_HeyGen', 'test_heygen_intro_v2.mp4')

def prepare_and_push():
    print("🚀 Starting Content Push Sequence...")
    
    if not os.path.exists(SAMPLE_VIDEO):
        print(f"❌ Error: Sample video not found at {SAMPLE_VIDEO}")
        return

    print(f"📦 Using media asset: {os.path.basename(SAMPLE_VIDEO)}")
    
    # 1. Update pending posts with media path
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # cursor.execute("UPDATE scheduled_posts SET media_path = ? WHERE status = 'pending'", (SAMPLE_VIDEO,))
    # updated_count = cursor.rowcount
    # conn.commit()
    # print(f"✅ Attached media to {updated_count} pending posts.")
    print("ℹ️  Using existing media paths from database.")
    
    # 2. Fetch pending posts
    cursor.execute("SELECT * FROM scheduled_posts WHERE status = 'pending' ORDER BY priority DESC")
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not posts:
        print("No pending posts to push.")
        return

    # 3. Initialize Poster
    poster = UnifiedAPIPoster(db_path=DB_PATH)
    
    print(f"\nAttempting to push {len(posts)} posts to all platforms...")
    print("⚠️  Note: This will attempt LIVE posting. Ensure credentials are set.")
    
    for post in posts:
        print(f"\n{'='*60}")
        print(f"Processing Post ID {post['id']}: {post['title']}")
        print(f"{'='*60}")
        
        # Parse platforms
        platforms = json.loads(post['platforms']) if post['platforms'] else []
        tags = json.loads(post['tags']) if post['tags'] else []
        hashtags = json.loads(post['hashtags']) if post['hashtags'] else []
        
        content = PostContent(
            title=post['title'],
            caption=post['caption'],
            media_path=post['media_path'],
            media_type=post['media_type'],
            tags=tags,
            hashtags=hashtags
        )
        
        # Execute Push
        results = poster.post_to_all_platforms(content, platforms=platforms)
        
        # Check if any succeeded
        success_count = sum(1 for r in results if r.success)
        if success_count > 0:
            print(f"✨ Post {post['id']} partially successful ({success_count}/{len(platforms)} platforms)")
            # Update status to posted (or partial)
            # For now, we leave as pending if not fully successful, or could mark 'posted'
        else:
            print(f"⚠️  Post {post['id']} failed on all targets.")

    print("\n🏁 Push Sequence Complete.")
    poster.print_summary()

if __name__ == "__main__":
    prepare_and_push()
