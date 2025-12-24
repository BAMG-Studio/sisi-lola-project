"""TikTok Automation Bot for Sisi Lola
Handles video uploads and content management on TikTok.
"""

import os
import requests
from typing import Dict, List
import json

class TikTokBot:
    def __init__(self):
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        self.api_version = 'v2'
        self.base_url = f'https://open.tiktokapis.com/{self.api_version}'
    
    def upload_video(self, video_path: str, caption: str, 
                     privacy_level: str = 'PUBLIC_TO_EVERYONE') -> Dict:
        """Upload video to TikTok"""
        # Step 1: Initialize upload
        init_url = f'{self.base_url}/post/publish/video/init/'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        init_data = {
            'post_info': {
                'title': caption,
                'privacy_level': privacy_level,
                'disable_duet': False,
                'disable_comment': False,
                'disable_stitch': False,
                'video_cover_timestamp_ms': 1000
            },
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': os.path.getsize(video_path),
                'chunk_size': 10000000,
                'total_chunk_count': 1
            }
        }
        
        response = requests.post(init_url, headers=headers, json=init_data)
        init_response = response.json()
        
        if 'data' in init_response:
            upload_url = init_response['data']['upload_url']
            
            # Step 2: Upload video
            with open(video_path, 'rb') as video_file:
                upload_response = requests.put(upload_url, data=video_file)
            
            return {
                'status': 'success',
                'publish_id': init_response['data'].get('publish_id'),
                'upload_response': upload_response.status_code
            }
        
        return init_response
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        url = f'{self.base_url}/user/info/'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        params = {
            'fields': 'open_id,union_id,avatar_url,display_name,follower_count,following_count,likes_count,video_count'
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    def get_video_list(self, max_count: int = 20) -> List[Dict]:
        """Get list of user's videos"""
        url = f'{self.base_url}/video/list/'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        params = {
            'fields': 'id,create_time,cover_image_url,share_url,video_description,duration,height,width,title,embed_html,embed_link',
            'max_count': max_count
        }
        
        response = requests.post(url, headers=headers, json=params)
        return response.json().get('data', {}).get('videos', [])

if __name__ == "__main__":
    bot = TikTokBot()
    print("TikTok Bot initialized successfully!")
