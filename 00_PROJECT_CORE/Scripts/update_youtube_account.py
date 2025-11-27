import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '00_PROJECT_CORE', 'PROJECT_DB.sqlite')

SCHEMA_HINT = """
This script expects the accounts table with columns similar to:
- platform (TEXT PRIMARY KEY per platform)
- handle (TEXT)
- profile_url (TEXT)
- email (TEXT)
- account_status (TEXT)
- verification_email (TEXT)
- verification_phone (TEXT)
- verification_2fa (TEXT)
- profile_picture_uploaded (INTEGER)
- banner_uploaded (INTEGER)
- followers (INTEGER)
- posts_count (INTEGER)
- channel_id (TEXT)
- website (TEXT)
- instagram (TEXT)
- tiktok (TEXT)
"""

YOUTUBE = {
    'platform': 'YouTube',
    'handle': os.getenv('YOUTUBE_HANDLE', '@SisiLolaLive'),
    'profile_url': os.getenv('YOUTUBE_PROFILE_URL', 'https://www.youtube.com/@SisiLolaLive'),
    'email': os.getenv('YOUTUBE_EMAIL', 'sisilolalive@gmail.com'),
    'channel_id': os.getenv('YOUTUBE_CHANNEL_ID', 'UCeWcJZHozas9rpr7XkBR7gA'),
    'verification_email': 'Yes',
    'verification_phone': 'No',
    'verification_2fa': 'No',
    'profile_picture_uploaded': 1,
    'banner_uploaded': 1,
    'followers': int(os.getenv('YOUTUBE_SUBSCRIBER_COUNT', '0')),
    'posts_count': int(os.getenv('YOUTUBE_POST_COUNT', '0')),
    'website': os.getenv('YOUTUBE_LINK_WEBSITE', 'sisilola.io'),
    'instagram': os.getenv('YOUTUBE_LINK_INSTAGRAM', '@sisilolalive'),
    'tiktok': os.getenv('YOUTUBE_LINK_TIKTOK', '@sisilolalive'),
}

def ensure_tables(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        platform TEXT PRIMARY KEY,
        handle TEXT,
        profile_url TEXT,
        email TEXT,
        account_status TEXT,
        verification_email TEXT,
        verification_phone TEXT,
        verification_2fa TEXT,
        profile_picture_uploaded INTEGER,
        banner_uploaded INTEGER,
        followers INTEGER,
        posts_count INTEGER,
        channel_id TEXT,
        website TEXT,
        instagram TEXT,
        tiktok TEXT
    )
    """)
    conn.commit()

def upsert_youtube(conn):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO accounts (
            platform, handle, profile_url, email, account_status,
            verification_email, verification_phone, verification_2fa,
            profile_picture_uploaded, banner_uploaded, followers, posts_count,
            channel_id, website, instagram, tiktok
        ) VALUES (
            :platform, :handle, :profile_url, :email, 'created',
            :verification_email, :verification_phone, :verification_2fa,
            :profile_picture_uploaded, :banner_uploaded, :followers, :posts_count,
            :channel_id, :website, :instagram, :tiktok
        ) ON CONFLICT(platform) DO UPDATE SET
            handle=excluded.handle,
            profile_url=excluded.profile_url,
            email=excluded.email,
            account_status='created',
            verification_email=excluded.verification_email,
            verification_phone=excluded.verification_phone,
            verification_2fa=excluded.verification_2fa,
            profile_picture_uploaded=excluded.profile_picture_uploaded,
            banner_uploaded=excluded.banner_uploaded,
            followers=excluded.followers,
            posts_count=excluded.posts_count,
            channel_id=excluded.channel_id,
            website=excluded.website,
            instagram=excluded.instagram,
            tiktok=excluded.tiktok
    """, YOUTUBE)
    conn.commit()

    # Log activity if table exists
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            timestamp TEXT,
            platform TEXT,
            action TEXT,
            details TEXT
        )
        """)
        cur.execute(
            "INSERT INTO activity_log (timestamp, platform, action, details) VALUES (?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                'YouTube',
                'update_account',
                f"Updated YouTube account for {YOUTUBE['handle']}"
            )
        )
        conn.commit()
    except Exception:
        pass

if __name__ == '__main__':
    # Allow override via env var PROJECT_DB_PATH if present
    db_path = os.getenv('PROJECT_DB_PATH', DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        ensure_tables(conn)
        upsert_youtube(conn)
        print(f"YouTube account upserted. DB: {db_path}")
    finally:
        conn.close()
