"""
Multi-Platform Social Media Poster
Posts content to YouTube, Instagram, TikTok, Facebook, Twitter/X, Reddit
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Platform-specific imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import praw
import tweepy

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")


class MultiPlatformPoster:
    """Post content to multiple social media platforms"""
    
    def __init__(self):
        self.token_dir = Path(__file__).parent
        self.results = []
    
    def post_to_youtube(self, video_path: str, title: str, description: str, tags: list) -> Dict:
        """Post video to YouTube"""
        try:
            token_file = self.token_dir / 'token_youtube.json'
            
            if not token_file.exists():
                return {
                    "platform": "youtube",
                    "status": "error",
                    "message": "YouTube token not found. Run youtube_oauth_complete.py first"
                }
            
            creds = Credentials.from_authorized_user_file(str(token_file))
            youtube = build('youtube', 'v3', credentials=creds)
            
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube limit
                    'description': description[:5000],
                    'tags': tags[:500],
                    'categoryId': '28'  # Science & Technology
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            video_url = f"https://youtube.com/watch?v={video_id}"
            
            return {
                "platform": "youtube",
                "status": "success",
                "video_id": video_id,
                "url": video_url,
                "message": f"Posted to YouTube: {video_url}"
            }
        
        except Exception as e:
            return {
                "platform": "youtube",
                "status": "error",
                "message": str(e)
            }
    
    def post_to_twitter(self, text: str, media_path: Optional[str] = None) -> Dict:
        """Post to Twitter/X"""
        try:
            # Twitter API v2 credentials
            client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
            )
            
            # Post tweet
            if media_path:
                # Upload media first (requires API v1.1)
                auth = tweepy.OAuth1UserHandler(
                    os.getenv("TWITTER_API_KEY"),
                    os.getenv("TWITTER_API_SECRET"),
                    os.getenv("TWITTER_ACCESS_TOKEN"),
                    os.getenv("TWITTER_ACCESS_SECRET")
                )
                api = tweepy.API(auth)
                media = api.media_upload(media_path)
                response = client.create_tweet(text=text[:280], media_ids=[media.media_id])
            else:
                response = client.create_tweet(text=text[:280])
            
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/SisiLolaLive/status/{tweet_id}"
            
            return {
                "platform": "twitter",
                "status": "success",
                "tweet_id": tweet_id,
                "url": tweet_url,
                "message": f"Posted to Twitter: {tweet_url}"
            }
        
        except Exception as e:
            return {
                "platform": "twitter",
                "status": "error",
                "message": str(e)
            }
    
    def post_to_reddit(self, subreddit: str, title: str, text: str) -> Dict:
        """Post to Reddit"""
        try:
            reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD"),
                user_agent="SisiLola Bot v1.0"
            )
            
            submission = reddit.subreddit(subreddit).submit(
                title=title[:300],
                selftext=text
            )
            
            post_url = f"https://reddit.com{submission.permalink}"
            
            return {
                "platform": "reddit",
                "status": "success",
                "post_id": submission.id,
                "url": post_url,
                "message": f"Posted to r/{subreddit}: {post_url}"
            }
        
        except Exception as e:
            return {
                "platform": "reddit",
                "status": "error",
                "message": str(e)
            }
    
    def post_to_instagram(self, image_path: str, caption: str) -> Dict:
        """Post to Instagram (requires Facebook Graph API)"""
        try:
            # Instagram Graph API implementation
            # Note: Requires approved Instagram Business account
            return {
                "platform": "instagram",
                "status": "pending",
                "message": "Instagram API requires business account approval"
            }
        except Exception as e:
            return {
                "platform": "instagram",
                "status": "error",
                "message": str(e)
            }
    
    def post_to_tiktok(self, video_path: str, caption: str) -> Dict:
        """Post to TikTok"""
        try:
            # TikTok API implementation
            # Note: Requires approved TikTok developer account
            return {
                "platform": "tiktok",
                "status": "pending",
                "message": "TikTok API requires developer account approval"
            }
        except Exception as e:
            return {
                "platform": "tiktok",
                "status": "error",
                "message": str(e)
            }
    
    def post_to_facebook(self, text: str, media_path: Optional[str] = None) -> Dict:
        """Post to Facebook Page"""
        try:
            # Facebook Graph API implementation
            return {
                "platform": "facebook",
                "status": "pending",
                "message": "Facebook API requires page access token"
            }
        except Exception as e:
            return {
                "platform": "facebook",
                "status": "error",
                "message": str(e)
            }
    
    def post_content_package(self, content_package: Dict, media_assets: Dict[str, str]) -> Dict:
        """
        Post a content package to its target platform
        
        Args:
            content_package: Single platform content from generator
            media_assets: Dict mapping platform to media file paths
        
        Returns:
            Result dict with status
        """
        platform = content_package['platform']
        caption = content_package['caption']
        
        print(f"\n[POST] Posting to {platform.upper()}...")
        
        if platform == 'youtube':
            video_path = media_assets.get('youtube')
            if not video_path:
                return {"platform": platform, "status": "error", "message": "No video file provided"}
            
            # Extract title from caption (first line)
            title = caption.split('\n')[0][:100]
            tags = [tag.strip('#') for tag in content_package.get('hashtags', [])]
            
            result = self.post_to_youtube(video_path, title, caption, tags)
        
        elif platform == 'x' or platform == 'twitter':
            media_path = media_assets.get('twitter')
            result = self.post_to_twitter(caption, media_path)
        
        elif platform == 'reddit':
            # Extract title and text
            lines = caption.split('\n')
            title = lines[0] if lines else "Sisi Lola Post"
            text = '\n'.join(lines[1:]) if len(lines) > 1 else caption
            subreddit = "test"  # Default, should be specified
            result = self.post_to_reddit(subreddit, title, text)
        
        elif platform == 'instagram':
            image_path = media_assets.get('instagram')
            result = self.post_to_instagram(image_path, caption)
        
        elif platform == 'tiktok':
            video_path = media_assets.get('tiktok')
            result = self.post_to_tiktok(video_path, caption)
        
        elif platform == 'facebook':
            media_path = media_assets.get('facebook')
            result = self.post_to_facebook(caption, media_path)
        
        else:
            result = {
                "platform": platform,
                "status": "error",
                "message": f"Unknown platform: {platform}"
            }
        
        self.results.append(result)
        
        if result['status'] == 'success':
            print(f"   [OK] {result.get('message', 'Posted successfully')}")
        else:
            print(f"   [FAIL] {result.get('message', 'Failed')}")
        
        return result
    
    def post_all_packages(self, content_file: str, media_assets: Dict[str, str]) -> List[Dict]:
        """
        Post all content packages from a generated content file
        
        Args:
            content_file: Path to JSON file from content generator
            media_assets: Dict mapping platforms to media file paths
        
        Returns:
            List of results for each platform
        """
        with open(content_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        packages = content.get('content_packages', [])
        
        print(f"\n{'='*70}")
        print(f"POSTING {len(packages)} CONTENT PACKAGES")
        print(f"{'='*70}")
        
        for package in packages:
            self.post_content_package(package, media_assets)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue" / f"post_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        
        print(f"\n{'='*70}")
        print(f"POSTING COMPLETE: {success_count}/{len(packages)} successful")
        print(f"Results: {results_file}")
        print(f"{'='*70}")
        
        return self.results


def main():
    """Demo: Test posting capabilities"""
    
    poster = MultiPlatformPoster()
    
    print("="*70)
    print("SISI LOLA MULTI-PLATFORM POSTER - STATUS CHECK")
    print("="*70)
    
    # Check which platforms are configured
    platforms = {
        "YouTube": Path(__file__).parent / 'token_youtube.json',
        "Twitter": os.getenv("TWITTER_API_KEY"),
        "Reddit": os.getenv("REDDIT_CLIENT_ID"),
        "Instagram": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
        "TikTok": os.getenv("TIKTOK_ACCESS_TOKEN"),
        "Facebook": os.getenv("FACEBOOK_ACCESS_TOKEN")
    }
    
    print("\nPlatform Configuration Status:")
    for platform, check in platforms.items():
        if isinstance(check, Path):
            status = "✅ Configured" if check.exists() else "❌ Not configured"
        else:
            status = "✅ Configured" if check else "❌ Not configured"
        print(f"  {platform:15} {status}")
    
    print("\n💡 To configure platforms:")
    print("   1. YouTube: Run youtube_oauth_complete.py")
    print("   2. Others: Run oauth_credential_manager.py")
    print("\n✅ Ready to post content!")


if __name__ == "__main__":
    main()
