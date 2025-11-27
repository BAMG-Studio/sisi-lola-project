#!/usr/bin/env python3
"""
Minimal platform account ingestion script
Usage: python3 ingest_platform_account.py <platform_name>
Reads from .env and updates PROJECT_DB.sqlite
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

def get_db_path():
    return os.environ.get('PROJECT_DB_PATH', 
                          str(Path(__file__).parent.parent / 'PROJECT_DB.sqlite'))

def init_tables(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts (
        platform TEXT PRIMARY KEY,
        handle TEXT,
        profile_url TEXT,
        email TEXT,
        created_date TEXT,
        email_verified INTEGER DEFAULT 0,
        phone_verified INTEGER DEFAULT 0,
        two_fa_enabled INTEGER DEFAULT 0,
        profile_picture INTEGER DEFAULT 0,
        banner_uploaded INTEGER DEFAULT 0,
        followers INTEGER DEFAULT 0,
        posts_count INTEGER DEFAULT 0,
        last_updated TEXT
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS credentials (
        platform TEXT PRIMARY KEY,
        api_key TEXT,
        client_id TEXT,
        client_secret TEXT,
        access_token TEXT,
        refresh_token TEXT,
        account_id TEXT,
        last_updated TEXT
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        platform TEXT,
        action TEXT,
        details TEXT,
        status TEXT
    )''')
    conn.commit()

def ingest_platform(platform_name):
    """Ingest platform from .env variables"""
    prefix = platform_name.upper().replace(' ', '_')
    
    # Load .env
    env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
    
    # Extract account data
    account_data = {
        'platform': platform_name,
        'handle': os.getenv(f'{prefix}_HANDLE', ''),
        'profile_url': os.getenv(f'{prefix}_PROFILE_URL', ''),
        'email': os.getenv(f'{prefix}_EMAIL', ''),
        'created_date': os.getenv(f'{prefix}_ACCOUNT_CREATED', ''),
        'email_verified': 1 if os.getenv(f'{prefix}_EMAIL_VERIFIED', 'false').lower() == 'true' else 0,
        'phone_verified': 1 if os.getenv(f'{prefix}_PHONE_VERIFIED', 'false').lower() == 'true' else 0,
        'two_fa_enabled': 1 if os.getenv(f'{prefix}_2FA_ENABLED', 'false').lower() == 'true' else 0,
        'profile_picture': 1 if os.getenv(f'{prefix}_PROFILE_PICTURE_UPLOADED', 'false').lower() == 'true' else 0,
        'banner_uploaded': 1 if os.getenv(f'{prefix}_BANNER_UPLOADED', 'false').lower() == 'true' else 0,
        'followers': int(os.getenv(f'{prefix}_FOLLOWER_COUNT', os.getenv(f'{prefix}_SUBSCRIBER_COUNT', '0'))),
        'posts_count': int(os.getenv(f'{prefix}_POST_COUNT', '0')),
        'last_updated': datetime.now(timezone.utc).isoformat()
    }
    
    # Extract credentials
    cred_data = {
        'platform': platform_name,
        'api_key': os.getenv(f'{prefix}_API_KEY', ''),
        'client_id': os.getenv(f'{prefix}_OAUTH_CLIENT_ID', os.getenv(f'{prefix}_CLIENT_ID', '')),
        'client_secret': os.getenv(f'{prefix}_OAUTH_CLIENT_SECRET', os.getenv(f'{prefix}_CLIENT_SECRET', '')),
        'access_token': os.getenv(f'{prefix}_ACCESS_TOKEN', ''),
        'refresh_token': os.getenv(f'{prefix}_REFRESH_TOKEN', ''),
        'account_id': os.getenv(f'{prefix}_CHANNEL_ID', os.getenv(f'{prefix}_ACCOUNT_ID', '')),
        'last_updated': datetime.now(timezone.utc).isoformat()
    }
    
    # Update DB
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    init_tables(conn)
    
    # Upsert account
    conn.execute('''INSERT OR REPLACE INTO accounts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                 tuple(account_data.values()))
    
    # Upsert credentials (only if at least one credential exists)
    if any([cred_data['api_key'], cred_data['client_id'], cred_data['access_token']]):
        conn.execute('''INSERT OR REPLACE INTO credentials VALUES (?,?,?,?,?,?,?,?)''',
                     tuple(cred_data.values()))
    
    # Log activity
    conn.execute('''INSERT INTO activity_log (timestamp, platform, action, details, status) 
                    VALUES (?,?,?,?,?)''',
                 (datetime.now(timezone.utc).isoformat(), platform_name, 'account_ingestion',
                  f'Handle: {account_data["handle"]}, Followers: {account_data["followers"]}', 'success'))
    
    conn.commit()
    conn.close()
    
    print(f"✅ {platform_name} ingested → {db_path}")
    print(f"   Handle: {account_data['handle']}")
    print(f"   Followers: {account_data['followers']}")
    print(f"   Verified: Email={bool(account_data['email_verified'])}, 2FA={bool(account_data['two_fa_enabled'])}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 ingest_platform_account.py <platform_name>")
        print("Example: python3 ingest_platform_account.py YouTube")
        sys.exit(1)
    
    ingest_platform(sys.argv[1])
