"""
SISI LOLA CREDENTIAL VERIFIER (EXTENDED)
========================================
Verifies connectivity and authentication for Sisi Lola's expanded ecosystem.
Includes TikTok, Twitch, YouTube, and Discord.
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import httpx

# Load .env
PROJECT_ROOT = Path(__file__).parent
ENV_PATH = PROJECT_ROOT / "sisi_lola_api" / ".env"
load_dotenv(ENV_PATH)

def log_status(service, status, details=""):
    icon = "✅" if status == "PASS" else ("⚠️" if status == "WARNING" else "❌")
    print(f"{icon} {service.ljust(20)}: {status.ljust(8)} {details}")

async def verify_elevenlabs():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        log_status("ElevenLabs", "FAIL", "Missing ELEVENLABS_API_KEY")
        return
    
    url = "https://api.elevenlabs.io/v1/user"
    headers = {"xi-api-key": api_key}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                log_status("ElevenLabs", "PASS", "API Key is valid")
            else:
                log_status("ElevenLabs", "FAIL", f"HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        log_status("ElevenLabs", "FAIL", str(e))

async def verify_tiktok():
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    
    if not client_key or not client_secret:
        log_status("TikTok", "WARNING", "Missing client_key or client_secret")
        return

    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, data=data)
            if resp.status_code == 200:
                log_status("TikTok", "PASS", "Client credentials valid")
            else:
                log_status("TikTok", "FAIL", f"HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        log_status("TikTok", "FAIL", str(e))

async def verify_twitch():
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        log_status("Twitch", "WARNING", "Missing client_id or client_secret")
        return

    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, params=params)
            if resp.status_code == 200:
                log_status("Twitch", "PASS", "Client credentials valid")
            else:
                log_status("Twitch", "FAIL", f"HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        log_status("Twitch", "FAIL", str(e))

async def verify_discord():
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        log_status("Discord", "FAIL", "Missing DISCORD_BOT_TOKEN")
        return

    url = "https://discord.com/api/v10/users/@me"
    headers = {"Authorization": f"Bot {bot_token}"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                user = resp.json()
                log_status("Discord", "PASS", f"Bot {user['username']} active")
            else:
                log_status("Discord", "FAIL", f"HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        log_status("Discord", "FAIL", str(e))

async def verify_youtube():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        log_status("YouTube", "FAIL", "Missing YOUTUBE_API_KEY")
        return
    
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id=Ks-_Mh1QhMc&key={api_key}"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                log_status("YouTube", "PASS", "API Key is valid and active")
            else:
                log_status("YouTube", "FAIL", f"HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        log_status("YouTube", "FAIL", str(e))

async def main():
    print("\n" + "="*70)
    print("SISI LOLA FULL STACK CREDENTIAL VERIFICATION")
    print("="*70 + "\n")
    
    await verify_elevenlabs()
    await verify_tiktok()
    await verify_twitch()
    await verify_discord()
    await verify_youtube()
    
    print("\n" + "="*70)
    print("Verification Completed.")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
