import json
import os
import sqlite3
from datetime import datetime, timezone

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'platforms_config.json')
DB_PATH = os.environ.get('PROJECT_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PROJECT_DB.sqlite'))

def ensure_tables(conn):
    cur = conn.cursor()
    # Accounts table
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
        tiktok TEXT,
        facebook TEXT,
        youtube TEXT,
        twitch TEXT,
        reddit TEXT
    )
    """)
    
    # Activity Log table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        timestamp TEXT,
        platform TEXT,
        action TEXT,
        details TEXT
    )
    """)
    conn.commit()

def ingest_platform(conn, data):
    cur = conn.cursor()
    
    # Map JSON fields to DB columns
    platform = data.get('platform_name')
    handle = data.get('handle')
    profile_url = data.get('profile_url')
    email = data.get('email')
    channel_id = data.get('channel_id')
    
    ver = data.get('verification', {})
    assets = data.get('assets', {})
    metrics = data.get('metrics', {})
    links = data.get('links', {})
    
    # Prepare values
    vals = {
        'platform': platform,
        'handle': handle,
        'profile_url': profile_url,
        'email': email,
        'account_status': 'active',
        'verification_email': 'Yes' if ver.get('email') else 'No',
        'verification_phone': 'Yes' if ver.get('phone') else 'No',
        'verification_2fa': 'Yes' if ver.get('two_fa') else 'No',
        'profile_picture_uploaded': 1 if assets.get('profile_picture') else 0,
        'banner_uploaded': 1 if assets.get('banner') else 0,
        'followers': metrics.get('followers', 0),
        'posts_count': metrics.get('posts', 0),
        'channel_id': channel_id,
        'website': links.get('website', ''),
        'instagram': links.get('instagram', ''),
        'tiktok': links.get('tiktok', ''),
        'facebook': links.get('facebook', ''),
        'youtube': links.get('youtube', ''),
        'twitch': links.get('twitch', ''),
        'reddit': links.get('reddit', '')
    }

    # Upsert
    cur.execute("""
        INSERT INTO accounts (
            platform, handle, profile_url, email, account_status,
            verification_email, verification_phone, verification_2fa,
            profile_picture_uploaded, banner_uploaded, followers, posts_count,
            channel_id, website, instagram, tiktok, facebook, youtube, twitch, reddit
        ) VALUES (
            :platform, :handle, :profile_url, :email, :account_status,
            :verification_email, :verification_phone, :verification_2fa,
            :profile_picture_uploaded, :banner_uploaded, :followers, :posts_count,
            :channel_id, :website, :instagram, :tiktok, :facebook, :youtube, :twitch, :reddit
        ) ON CONFLICT(platform) DO UPDATE SET
            handle=excluded.handle,
            profile_url=excluded.profile_url,
            email=excluded.email,
            account_status=excluded.account_status,
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
            tiktok=excluded.tiktok,
            facebook=excluded.facebook,
            youtube=excluded.youtube,
            twitch=excluded.twitch,
            reddit=excluded.reddit
    """, vals)
    
    # Log
    cur.execute(
        "INSERT INTO activity_log (timestamp, platform, action, details) VALUES (?, ?, ?, ?)",
        (
            datetime.now(timezone.utc).isoformat(),
            platform,
            'batch_ingest',
            f"Updated {platform} account: {handle}"
        )
    )
    conn.commit()
    print(f"✅ Ingested {platform}")

def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found: {CONFIG_FILE}")
        return

    print(f"Reading config from {CONFIG_FILE}...")
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    print(f"Connecting to DB at {DB_PATH}...")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    try:
        ensure_tables(conn)
        for platform_data in config.get('platforms', []):
            ingest_platform(conn, platform_data)
        print("\n🎉 Batch ingestion complete!")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
