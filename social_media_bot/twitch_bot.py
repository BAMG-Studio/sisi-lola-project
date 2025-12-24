"""Twitch Automation Bot for Sisi Lola
Handles Twitch streaming automation and chat management.
"""

import os
import requests
from typing import Dict, List
from datetime import datetime

class TwitchBot:
    def __init__(self):
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.access_token = None
        self.base_url = 'https://api.twitch.tv/helix'
        self._get_access_token()
    
    def _get_access_token(self):
        """Get OAuth access token"""
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
    
    def _get_headers(self) -> Dict:
        """Get authorization headers"""
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def get_user_info(self, username: str = None) -> Dict:
        """Get Twitch user information"""
        url = f'{self.base_url}/users'
        params = {}
        if username:
            params['login'] = username
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            data = response.json().get('data', [])
            return data[0] if data else {}
        return {}
    
    def get_streams(self, user_login: str = None, limit: int = 20) -> List[Dict]:
        """Get live streams"""
        url = f'{self.base_url}/streams'
        params = {'first': limit}
        if user_login:
            params['user_login'] = user_login
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    
    def get_videos(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get videos from a channel"""
        url = f'{self.base_url}/videos'
        params = {
            'user_id': user_id,
            'first': limit
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    
    def get_clips(self, broadcaster_id: str, limit: int = 20) -> List[Dict]:
        """Get clips from a channel"""
        url = f'{self.base_url}/clips'
        params = {
            'broadcaster_id': broadcaster_id,
            'first': limit
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    
    def search_channels(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for channels"""
        url = f'{self.base_url}/search/channels'
        params = {
            'query': query,
            'first': limit
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []

if __name__ == "__main__":
    bot = TwitchBot()
    print("Twitch Bot initialized successfully!")
