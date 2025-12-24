"""Twitter/X Automation Bot for Sisi Lola
Handles tweets, threads, and engagement on Twitter/X.
"""

import os
import tweepy
from typing import Dict, List, Optional

class TwitterBot:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Tweepy client (v2 API)
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        
        # Initialize v1 API for media uploads
        auth = tweepy.OAuth1UserHandler(
            self.api_key, self.api_secret,
            self.access_token, self.access_token_secret
        )
        self.api = tweepy.API(auth)
    
    def post_tweet(self, text: str) -> Dict:
        """Post a tweet"""
        response = self.client.create_tweet(text=text)
        return response.data
    
    def post_tweet_with_media(self, text: str, media_path: str) -> Dict:
        """Post tweet with image or video"""
        # Upload media
        media = self.api.media_upload(media_path)
        
        # Create tweet with media
        response = self.client.create_tweet(
            text=text,
            media_ids=[media.media_id]
        )
        return response.data
    
    def post_thread(self, tweets: List[str]) -> List[Dict]:
        """Post a thread of tweets"""
        responses = []
        previous_tweet_id = None
        
        for tweet_text in tweets:
            if previous_tweet_id:
                response = self.client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=previous_tweet_id
                )
            else:
                response = self.client.create_tweet(text=tweet_text)
            
            responses.append(response.data)
            previous_tweet_id = response.data['id']
        
        return responses
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> Dict:
        """Reply to a tweet"""
        response = self.client.create_tweet(
            text=text,
            in_reply_to_tweet_id=tweet_id
        )
        return response.data
    
    def get_user_tweets(self, user_id: str, max_results: int = 10) -> List[Dict]:
        """Get tweets from a user"""
        tweets = self.client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            tweet_fields=['created_at', 'public_metrics', 'text']
        )
        return tweets.data if tweets.data else []
    
    def get_my_info(self) -> Dict:
        """Get authenticated user information"""
        me = self.client.get_me(
            user_fields=['description', 'public_metrics', 'profile_image_url']
        )
        return me.data
    
    def search_tweets(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for tweets"""
        tweets = self.client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=['created_at', 'public_metrics', 'author_id']
        )
        return tweets.data if tweets.data else []

if __name__ == "__main__":
    bot = TwitterBot()
    print("Twitter Bot initialized successfully!")
    user_info = bot.get_my_info()
    print(f"Authenticated as: @{user_info.get('username')}")
