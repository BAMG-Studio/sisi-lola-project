#!/usr/bin/env python3
"""
Dropbox OAuth2 Token Generator

This script helps you get a new Dropbox refresh token.

BEFORE RUNNING:
1. Go to https://www.dropbox.com/developers/apps
2. Create a new app or use existing one
3. Under Settings, note your App key and App secret
4. Under Permissions, enable: files.content.read, sharing.read, sharing.write

HOW TO USE:
1. Run this script: python get_dropbox_token.py
2. Enter your App Key and App Secret when prompted
3. Open the URL in your browser
4. Authorize the app
5. Copy the authorization code
6. Paste it here
7. The script will show you the tokens to add to .env
"""

import os
import webbrowser
from urllib.parse import urlencode

def main():
    print("=" * 60)
    print("DROPBOX OAUTH2 TOKEN GENERATOR")
    print("=" * 60)
    
    # Check if credentials are in .env
    app_key = os.getenv('DROPBOX_APP_KEY', '')
    app_secret = os.getenv('DROPBOX_APP_SECRET', '')
    
    if not app_key:
        print("\n📋 Step 1: Enter your Dropbox App Key")
        app_key = input("App Key: ").strip()
    else:
        print(f"\n✅ Using App Key from .env: {app_key[:5]}...")
        use_existing = input("Use this? (y/n): ").strip().lower()
        if use_existing != 'y':
            app_key = input("Enter new App Key: ").strip()
    
    if not app_secret:
        print("\n📋 Step 2: Enter your Dropbox App Secret")
        app_secret = input("App Secret: ").strip()
    else:
        print(f"✅ Using App Secret from .env: {app_secret[:5]}...")
        use_existing = input("Use this? (y/n): ").strip().lower()
        if use_existing != 'y':
            app_secret = input("Enter new App Secret: ").strip()
    
    # Build authorization URL
    auth_url = (
        f"https://www.dropbox.com/oauth2/authorize?"
        f"client_id={app_key}&"
        f"response_type=code&"
        f"token_access_type=offline"
    )
    
    print("\n" + "=" * 60)
    print("📋 Step 3: Authorize the app")
    print("=" * 60)
    print("\nOpen this URL in your browser:")
    print(f"\n{auth_url}\n")
    
    try:
        webbrowser.open(auth_url)
        print("(Browser should open automatically)")
    except:
        print("(Please copy and paste the URL above)")
    
    print("\n" + "=" * 60)
    print("📋 Step 4: Enter authorization code")
    print("=" * 60)
    auth_code = input("\nPaste the authorization code here: ").strip()
    
    # Exchange code for tokens
    print("\n🔄 Exchanging code for tokens...")
    
    import requests
    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": app_key,
            "client_secret": app_secret,
        }
    )
    
    if response.status_code != 200:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    access_token = data.get("access_token", "")
    refresh_token = data.get("refresh_token", "")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Here are your tokens:")
    print("=" * 60)
    
    print(f"\nDROPBOX_APP_KEY={app_key}")
    print(f"DROPBOX_APP_SECRET={app_secret}")
    print(f"DROPBOX_ACCESS_TOKEN={access_token}")
    print(f"DROPBOX_REFRESH_TOKEN={refresh_token}")
    
    # Offer to update .env
    print("\n" + "=" * 60)
    update = input("Update .env file with these values? (y/n): ").strip().lower()
    
    if update == 'y':
        env_path = ".env"
        
        # Read existing .env
        existing = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing[key] = value
        
        # Update values
        existing['DROPBOX_APP_KEY'] = app_key
        existing['DROPBOX_APP_SECRET'] = app_secret
        existing['DROPBOX_ACCESS_TOKEN'] = access_token
        existing['DROPBOX_REFRESH_TOKEN'] = refresh_token
        
        # Write back
        with open(env_path, 'w') as f:
            for key, value in existing.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Updated {env_path}")
    
    print("\n✅ Done! You can now run the transcription scripts.")

if __name__ == "__main__":
    main()
