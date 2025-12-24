"""Facebook Automation Bot for Sisi Lola
Handles Facebook page posting, story publishing, and engagement.
"""

import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
import json

class FacebookBot:
    def __init__(self):
        self.app_id = os.getenv('META_APP_ID')
        self.app_secret = os.getenv('META_APP_SECRET')
        self.page_access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        
    def post_text(self, message: str) -> Dict:
        """Post text to Facebook page"""
        url = f'{self.base_url}/{self.page_id}/feed'
        payload = {
            'message': message,
            'access_token': self.page_access_token
        }
        response = requests.post(url, data=payload)
        return response.json()
    
    def post_photo(self, image_path: str, caption: str) -> Dict:
        """Post photo to Facebook page"""
        url = f'{self.base_url}/{self.page_id}/photos'
        with open(image_path, 'rb') as image_file:
            files = {'source': image_file}
            payload = {
                'message': caption,
                'access_token': self.page_access_token
            }
            response = requests.post(url, files=files, data=payload)
        return response.json()
    
    def post_video(self, video_path: str, description: str) -> Dict:
        """Post video to Facebook page"""
        url = f'{self.base_url}/{self.page_id}/videos'
        with open(video_path, 'rb') as video_file:
            files = {'source': video_file}
            payload = {
                'description': description,
                'access_token': self.page_access_token
            }
            response = requests.post(url, files=files, data=payload)
        return response.json()
    
    def post_link(self, link: str, message: str) -> Dict:
        """Post link to Facebook page"""
        url = f'{self.base_url}/{self.page_id}/feed'
        payload = {
            'link': link,
            'message': message,
            'access_token': self.page_access_token
        }
        response = requests.post(url, data=payload)
        return response.json()
    
    def get_page_posts(self, limit: int = 25) -> List[Dict]:
        """Get recent posts from page"""
        url = f'{self.base_url}/{self.page_id}/posts'
        params = {
            'access_token': self.page_access_token,
            'limit': limit
        }
        response = requests.get(url, params=params)
        return response.json().get('data', [])
    
    def get_post_insights(self, post_id: str) -> Dict:
        """Get insights for a specific post"""
        url = f'{self.base_url}/{post_id}/insights'
        params = {
            'access_token': self.page_access_token,
            'metric': 'post_impressions,post_engaged_users,post_reactions_by_type_total'
        }
        response = requests.get(url, params=params)
        return response.json()

if __name__ == "__main__":
    bot = FacebookBot()
    print("Facebook Bot initialized successfully!")
    print(f"Page ID: {bot.page_id}")
