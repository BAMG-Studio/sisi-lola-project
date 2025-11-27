#!/usr/bin/env python3
"""
YouTube Analytics for Sisi Lola
Fetches channel metrics and video performance
"""
import os
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_credentials():
    """Load saved YouTube credentials"""
    token_path = Path(__file__).parent / 'youtube_token.pickle'
    if not token_path.exists():
        raise FileNotFoundError("Run youtube_content_uploader.py first to authenticate")
    
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def get_channel_stats():
    """Get channel statistics"""
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    request = youtube.channels().list(
        part='statistics,snippet',
        mine=True
    )
    response = request.execute()
    
    if response['items']:
        stats = response['items'][0]['statistics']
        snippet = response['items'][0]['snippet']
        return {
            'title': snippet['title'],
            'subscribers': int(stats.get('subscriberCount', 0)),
            'views': int(stats.get('viewCount', 0)),
            'videos': int(stats.get('videoCount', 0))
        }
    return None

def get_recent_videos(max_results=10):
    """Get recent uploaded videos"""
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    request = youtube.search().list(
        part='snippet',
        forMine=True,
        type='video',
        order='date',
        maxResults=max_results
    )
    response = request.execute()
    
    videos = []
    for item in response.get('items', []):
        videos.append({
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'published': item['snippet']['publishedAt'],
            'url': f"https://youtu.be/{item['id']['videoId']}"
        })
    
    return videos

def get_video_analytics(video_id):
    """Get analytics for specific video"""
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    request = youtube.videos().list(
        part='statistics,snippet',
        id=video_id
    )
    response = request.execute()
    
    if response['items']:
        stats = response['items'][0]['statistics']
        snippet = response['items'][0]['snippet']
        return {
            'title': snippet['title'],
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'published': snippet['publishedAt']
        }
    return None

if __name__ == '__main__':
    # Load .env
    env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
    
    try:
        stats = get_channel_stats()
        if stats:
            print(f"📊 {stats['title']}")
            print(f"   Subscribers: {stats['subscribers']}")
            print(f"   Views: {stats['views']}")
            print(f"   Videos: {stats['videos']}")
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
