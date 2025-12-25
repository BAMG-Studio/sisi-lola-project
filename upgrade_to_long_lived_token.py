import os
import httpx
import asyncio
from dotenv import load_dotenv

async def upgrade_token():
    load_dotenv("sisi_lola_api/.env")
    
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    short_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    
    if not all([app_id, app_secret, short_token]):
        print("❌ Missing FACEBOOK_APP_ID, SECRET or TOKEN in .env")
        return

    print("🚀 Upgrading to Long-Lived Token (60 Days)...")
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            long_token = resp.json().get("access_token")
            # Update .env
            env_path = "sisi_lola_api/.env"
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            with open(env_path, "w") as f:
                for line in lines:
                    if line.startswith("INSTAGRAM_ACCESS_TOKEN="):
                        f.write(f"INSTAGRAM_ACCESS_TOKEN={long_token}\n")
                    else:
                        f.write(line)
            print("✅ SUCCESS! Your token is now Long-Lived (60 Days).")
            print("You can now fire the posts again.")
        else:
            print(f"❌ Failed to upgrade: {resp.text}")

if __name__ == "__main__":
    asyncio.run(upgrade_token())
