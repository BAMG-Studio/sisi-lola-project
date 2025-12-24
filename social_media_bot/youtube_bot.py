"""YouTube Automation Bot for Sisi Lola
Handles video uploads, playlist management, and community posts.
"""

import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from typing import Dict, List, Optional

class YouTubeBot:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        elif self.refresh_token:
            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.youtube = build('youtube', 'v3', credentials=creds)
    
    def upload_video(self, video_path: str, title: str, description: str, 
                     tags: List[str], category_id: str = '22',
                     privacy_status: str = 'public') -> Dict:
        """Upload video to YouTube"""
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True,
                                mimetype='video/*')
        
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        return response
    
    def create_playlist(self, title: str, description: str, 
                       privacy_status: str = 'public') -> Dict:
        """Create a new playlist"""
        body = {
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        
        request = self.youtube.playlists().insert(
            part='snippet,status',
            body=body
        )
        
        return request.execute()
    
    def add_video_to_playlist(self, video_id: str, playlist_id: str) -> Dict:
        """Add video to playlist"""
        body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        
        request = self.youtube.playlistItems().insert(
            part='snippet',
            body=body
        )
        
        return request.execute()
    
    def get_channel_videos(self, max_results: int = 50) -> List[Dict]:
        """Get videos from channel"""
        request = self.youtube.search().list(
            part='snippet',
            forMine=True,
            type='video',
            maxResults=max_results
        )
        
        response = request.execute()
        return response.get('items', [])
    
    def get_video_statistics(self, video_id: str) -> Dict:
        """Get statistics for a video"""
        request = self.youtube.videos().list(
            part='statistics',
            id=video_id
        )
        
        response = request.execute()
        if response['items']:
            return response['items'][0]['statistics']
        return {}

if __name__ == "__main__":
    bot = YouTubeBot()
    print("YouTube Bot initialized successfully!")
