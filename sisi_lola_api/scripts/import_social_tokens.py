#!/usr/bin/env python3
"""
=============================================================================
SISI LOLA - Import ALL API Tokens from .env to Database
=============================================================================
Run: python -m sisi_lola_api.scripts.import_social_tokens
=============================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file - it's in sisi_lola_api/.env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)
print(f"📂 Loading .env from: {env_path}")

# Import after loading .env
from sisi_lola_api.app.services.auth_store import save_social_token, get_social_token, init_db

# Initialize the database
init_db()

# Define token mappings based on actual .env variable names
TOKEN_MAPPINGS = [
    # === SOCIAL PLATFORMS ===
    {
        "platform": "instagram",
        "access_token_var": "INSTAGRAM_ACCESS_TOKEN",
        "account_id_var": "INSTAGRAM_BUSINESS_ACCOUNT_ID",
    },
    {
        "platform": "tiktok",
        "access_token_var": "TIKTOK_ACCESS_TOKEN",
        "account_id_var": "TIKTOK_APP_ID",
    },
    {
        "platform": "youtube",
        "access_token_var": "YOUTUBE_API_KEY",  # Using API key for now
        "account_id_var": "YOUTUBE_CHANNEL_ID",
    },
    {
        "platform": "facebook",
        "access_token_var": "FACEBOOK_APP_SECRET",  # Need Page Access Token ideally
        "account_id_var": "FACEBOOK_PAGE_ID",
    },
    {
        "platform": "twitch",
        "access_token_var": "TWITCH_CLIENT_SECRET",
        "account_id_var": "TWITCH_CLIENT_ID",
    },
    {
        "platform": "discord",
        "access_token_var": "DISCORD_BOT_TOKEN",
        "account_id_var": "DISCORD_APP_ID",
    },
    # === AI SERVICES ===
    {
        "platform": "openai",
        "access_token_var": "OPENAI_API_KEY",
    },
    {
        "platform": "elevenlabs",
        "access_token_var": "ELEVENLABS_API_KEY",
    },
    {
        "platform": "cohere",
        "access_token_var": "COHERE_API_KEY",
    },
    {
        "platform": "heygen",
        "access_token_var": "HEYGEN_API_KEY",
    },
    {
        "platform": "perplexity",
        "access_token_var": "PERPLEXITY_API_KEY",
    },
    {
        "platform": "klingai",
        "access_token_var": "KLINGAI_ACCESS_KEY",
    },
    {
        "platform": "did",
        "access_token_var": "DID_API_KEY",
    },
    {
        "platform": "openrouter",
        "access_token_var": "OPEN_ROUTER_API",
    },
]


def import_tokens():
    """Import tokens from .env to database"""
    print("\n" + "=" * 60)
    print("🔐 IMPORTING ALL API TOKENS TO DATABASE")
    print("=" * 60 + "\n")
    
    imported = 0
    skipped = 0
    
    print("📱 SOCIAL PLATFORMS:")
    print("-" * 40)
    
    for mapping in TOKEN_MAPPINGS[:6]:  # Social platforms
        platform = mapping["platform"]
        token = os.getenv(mapping["access_token_var"])
        
        if token and token != "PLACEHOLDER_UPDATE_AFTER_OAUTH":
            save_social_token(
                platform=platform,
                access_token=token,
                refresh_token=None,
                expires_in=0
            )
            print(f"  ✅ {platform.upper()}: Token saved ({token[:10]}...)")
            imported += 1
        else:
            status = "PLACEHOLDER" if token else "NOT FOUND"
            print(f"  ⏭️  {platform.upper()}: {status} ({mapping['access_token_var']})")
            skipped += 1
    
    print("\n🤖 AI SERVICES:")
    print("-" * 40)
    
    for mapping in TOKEN_MAPPINGS[6:]:  # AI services
        platform = mapping["platform"]
        token = os.getenv(mapping["access_token_var"])
        
        if token:
            save_social_token(
                platform=platform,
                access_token=token,
                refresh_token=None,
                expires_in=0
            )
            print(f"  ✅ {platform.upper()}: Token saved ({token[:10]}...)")
            imported += 1
        else:
            print(f"  ⏭️  {platform.upper()}: NOT FOUND ({mapping['access_token_var']})")
            skipped += 1
    
    # Special check for Gemini
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        save_social_token(platform="gemini", access_token=gemini_key, refresh_token=None, expires_in=0)
        print(f"  ✅ GEMINI: Token saved ({gemini_key[:10]}...)")
        imported += 1
    else:
        print(f"  ⏭️  GEMINI: NOT FOUND (GEMINI_API_KEY)")
        skipped += 1
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {imported} imported, {skipped} skipped")
    print("=" * 60)
    
    # Summary by category
    print("\n🔍 QUICK PLATFORM CHECK:")
    key_platforms = ["instagram", "tiktok", "youtube", "elevenlabs", "openai"]
    for p in key_platforms:
        data = get_social_token(p)
        status = f"✅ Ready ({data['access_token'][:8]}...)" if data else "❌ Not configured"
        print(f"  {p.upper()}: {status}")


if __name__ == "__main__":
    import_tokens()
