#!/usr/bin/env python3
"""
YouTube Content Uploader for Sisi Lola
Uploads videos/shorts to YouTube using OAuth credentials
"""
import os
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_credentials():
    """Get or refresh YouTube OAuth credentials"""
    creds = None
    token_path = Path(__file__).parent / 'youtube_token.pickle'
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Create client_secrets.json from .env
            client_config = {
                "installed": {
                    "client_id": os.getenv('YOUTUBE_OAUTH_CLIENT_ID'),
                    "client_secret": os.getenv('YOUTUBE_OAUTH_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def upload_video(video_path, title, description, tags=None, category_id="22", privacy="public"):
    """Upload video to YouTube"""
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress() * 100)}% complete")
    
    video_id = response['id']
    print(f"✅ Uploaded: https://youtu.be/{video_id}")
    return video_id

def upload_short(video_path, title, description):
    """Upload YouTube Short (adds #Shorts tag)"""
    return upload_video(
        video_path,
        f"{title} #Shorts",
        f"{description}\n\n#Shorts #SisiLola #AfricanCulture",
        tags=['Shorts', 'SisiLola', 'AfricanCulture'],
        privacy="public"
    )

if __name__ == '__main__':
    # Load .env
    env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
    
    print("YouTube uploader ready. Use upload_video() or upload_short() functions.")
