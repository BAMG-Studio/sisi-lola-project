"""
YouTube OAuth Token Generator
Completes the OAuth flow and saves tokens for automated posting
"""

import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube']

def get_youtube_credentials():
    """Complete YouTube OAuth flow and save tokens"""
    
    # Path to save tokens
    token_file = Path(__file__).parent / 'token_youtube.json'
    
    # OAuth client configuration
    client_config = {
        "installed": {
            "client_id": "163606189898-uts4nnb1u38b13785n7gmgq0j20m79ed.apps.googleusercontent.com",
            "client_secret": "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",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    creds = None
    
    # Check if token file exists
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            print(f"[OK] Loaded existing credentials from {token_file}")
        except Exception as e:
            print(f"[WARN] Could not load existing credentials: {e}")
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[INFO] Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("\n[START] Starting YouTube OAuth flow...")
            print("[NOTE] Your browser will open for authorization")
            print("[NOTE] Select the 'Sisi Lola' account (sisilolalive@gmail.com)")
            print("[NOTE] Click 'Continue' on the unverified app warning")
            print("[NOTE] Grant all YouTube permissions\n")
            
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri='http://localhost:8080/'
            )
            
            creds = flow.run_local_server(port=8080, prompt='consent')
        
        # Save credentials
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        
        print(f"\n[SUCCESS] YouTube OAuth tokens saved to: {token_file}")
        print("[INFO] Token will auto-refresh when expired")
    
    # Display token info
    print("\n" + "="*70)
    print("YOUTUBE OAUTH STATUS")
    print("="*70)
    print(f"Token Valid: {'Yes' if creds.valid else 'No'}")
    print(f"Token File: {token_file}")
    print(f"Scopes: {', '.join(SCOPES)}")
    print("="*70)
    
    return creds

if __name__ == "__main__":
    print("="*70)
    print("SISI LOLA - YOUTUBE OAUTH TOKEN GENERATOR")
    print("="*70)
    
    try:
        creds = get_youtube_credentials()
        print("\n[SUCCESS] YouTube integration is ready for automated posting!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\n[TROUBLESHOOTING]")
        print("   1. Ensure sisilolalive@gmail.com is added as a test user")
        print("   2. Check that http://localhost:8080/ is in redirect URIs")
        print("   3. Make sure port 8080 is not in use")
