import os
import httpx
import asyncio
from dotenv import load_dotenv

async def check_ig_details():
    load_dotenv("sisi_lola_api/.env")
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    
    if not token:
        print("❌ No Instagram Access Token found in .env")
        return

    print("🔍 Fetching Instagram Business Account details...")
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        "fields": "instagram_business_account,name",
        "access_token": token
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            ig_account = data.get("instagram_business_account")
            if ig_account:
                print(f"✅ Found IG Business Account! ID: {ig_account['id']}")
                print(f"Current FB Page Name: {data.get('name')}")
                if ig_account['id'] != os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID"):
                    print(f"⚠️  NOTE: Your .env has a DIFFERENT ID: {os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')}")
                    print(f"Updating .env with the correct ID...")
                    # Update .env
                    env_path = "sisi_lola_api/.env"
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                    with open(env_path, "w") as f:
                        for line in lines:
                            if line.startswith("INSTAGRAM_BUSINESS_ACCOUNT_ID="):
                                f.write(f"INSTAGRAM_BUSINESS_ACCOUNT_ID={ig_account['id']}\n")
                            else:
                                f.write(line)
                    print("✅ .env updated with correct IG ID.")
            else:
                print("❌ This FB Page has NO Instagram Business Account linked.")
        else:
            print(f"❌ Failed to fetch details: {resp.text}")

if __name__ == "__main__":
    asyncio.run(check_ig_details())
