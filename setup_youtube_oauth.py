import os
import json
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def setup_youtube():
    """Shows basic usage of the YouTube API.
    Lists the names and IDs of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('youtube_token.json'):
        creds = Credentials.from_authorized_user_file('youtube_token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("❌ ERROR: 'client_secrets.json' not found!")
                print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print("2. Create an OAuth 2.0 Client ID (Desktop App)")
                print("3. Download the JSON and rename it to 'client_secrets.json' in this folder.")
                return

            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            # Use open_browser=False for WSL/Console environments
            creds = flow.run_local_server(port=0, open_browser=False)
        
        # Save the credentials for the next run
        with open('youtube_token.json', 'w') as token:
            token.write(creds.to_json())

    print("\n✅ YouTube OAuth Setup Complete!")
    print("Your token is saved in 'youtube_token.json'.")
    print("Sisi Lola can now use this to upload Shorts automatically.")

if __name__ == '__main__':
    setup_youtube()
