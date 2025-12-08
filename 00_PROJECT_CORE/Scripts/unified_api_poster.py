"""
Unified API Poster for All 9 Social Media Platforms
Handles automated posting with platform-specific formatting and error handling
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sqlite3

# Import platform-specific libraries
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("Warning: YouTube API library not installed. Run: pip install google-api-python-client google-auth-oauthlib")

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("Warning: Reddit API library not installed. Run: pip install praw")


@dataclass
class PostContent:
    """Universal content structure"""
    title: str
    caption: str
    media_path: Optional[str] = None
    media_type: str = "video"  # video, image, text
    tags: List[str] = None
    hashtags: List[str] = None
    thumbnail_path: Optional[str] = None
    schedule_time: Optional[str] = None
    platform_overrides: Dict[str, Dict] = None


@dataclass
class PostResult:
    """Result of a posting attempt"""
    platform: str
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class CredentialManager:
    """Secure credential management for all platforms"""
    
    def __init__(self):
        self.credentials = {}
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from environment variables"""
        # YouTube
        self.credentials['youtube'] = {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
            'access_token': os.getenv('YOUTUBE_ACCESS_TOKEN')
        }
        
        # Instagram
        self.credentials['instagram'] = {
            'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
            'business_account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        }
        
        # TikTok
        self.credentials['tiktok'] = {
            'access_token': os.getenv('TIKTOK_ACCESS_TOKEN'),
            'open_id': os.getenv('TIKTOK_OPEN_ID')
        }
        
        # Facebook
        self.credentials['facebook'] = {
            'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),
            'page_id': os.getenv('FACEBOOK_PAGE_ID')
        }
        
        # Twitch
        self.credentials['twitch'] = {
            'client_id': os.getenv('TWITCH_CLIENT_ID'),
            'client_secret': os.getenv('TWITCH_CLIENT_SECRET'),
            'access_token': os.getenv('TWITCH_ACCESS_TOKEN'),
            'broadcaster_id': os.getenv('TWITCH_BROADCASTER_ID')
        }
        
        # Reddit
        self.credentials['reddit'] = {
            'client_id': os.getenv('REDDIT_CLIENT_ID'),
            'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'username': os.getenv('REDDIT_USERNAME'),
            'password': os.getenv('REDDIT_PASSWORD'),
            'user_agent': 'SisiLola/1.0 by sisilola'
        }
    
    def get(self, platform: str) -> Dict:
        """Get credentials for specific platform"""
        return self.credentials.get(platform.lower(), {})
    
    def is_configured(self, platform: str) -> bool:
        """Check if platform has valid credentials"""
        creds = self.get(platform)
        if not creds:
            return False
        # Check for essential keys
        essential_keys = {
            'youtube': ['access_token'],
            'instagram': ['access_token', 'business_account_id'],
            'tiktok': ['access_token', 'open_id'],
            'facebook': ['access_token', 'page_id'],
            'twitch': ['access_token', 'broadcaster_id'],
            'reddit': ['client_id', 'client_secret', 'username', 'password']
        }
        required = essential_keys.get(platform.lower(), [])
        return all(creds.get(key) for key in required)


class UnifiedAPIPoster:
    """Unified posting system for all 9 platforms"""
    
    def __init__(self, db_path: str = None):
        self.creds = CredentialManager()
        
        # Database connection
        if db_path is None:
            base_path = Path(__file__).parent.parent
            db_path = base_path / "05_BRANDING_ARTIFACTS" / "sisi_lola_accounts.db"
        self.db_path = Path(db_path)
        
        # Results tracking
        self.results: List[PostResult] = []
    
    def post_to_all_platforms(self, content: PostContent, platforms: List[str] = None) -> List[PostResult]:
        """
        Post content to multiple platforms
        
        Args:
            content: PostContent object with universal content structure
            platforms: List of platform names (if None, posts to all configured platforms)
        
        Returns:
            List of PostResult objects
        """
        if platforms is None:
            platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitch', 'Reddit',
                        'Vumistream', 'Twiva', 'Wowzi']
        
        self.results = []
        
        for platform in platforms:
            print(f"\n{'='*60}")
            print(f"Posting to {platform}...")
            print(f"{'='*60}")
            
            try:
                result = self._post_to_platform(platform, content)
                self.results.append(result)
                
                if result.success:
                    print(f"✅ SUCCESS: Posted to {platform}")
                    if result.post_url:
                        print(f"   URL: {result.post_url}")
                else:
                    print(f"❌ FAILED: {result.error_message}")
                
                # Log to database
                self._log_post_attempt(result)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                error_result = PostResult(
                    platform=platform,
                    success=False,
                    error_message=f"Unexpected error: {str(e)}"
                )
                self.results.append(error_result)
                print(f"❌ ERROR: {str(e)}")
        
        return self.results
    
    def _post_to_platform(self, platform: str, content: PostContent) -> PostResult:
        """Route to platform-specific posting method"""
        platform_lower = platform.lower()
        
        # Check credentials
        if platform_lower in ['youtube', 'instagram', 'tiktok', 'facebook', 'twitch', 'reddit']:
            if not self.creds.is_configured(platform_lower):
                return PostResult(
                    platform=platform,
                    success=False,
                    error_message=f"Credentials not configured. Set {platform.upper()}_* environment variables."
                )
        
        # Route to platform-specific method
        posting_methods = {
            'youtube': self._post_to_youtube,
            'instagram': self._post_to_instagram,
            'tiktok': self._post_to_tiktok,
            'facebook': self._post_to_facebook,
            'twitch': self._post_to_twitch,
            'reddit': self._post_to_reddit,
            'vumistream': self._post_to_vumistream,
            'twiva': self._post_to_twiva,
            'wowzi': self._post_to_wowzi
        }
        
        method = posting_methods.get(platform_lower)
        if method:
            return method(content)
        else:
            return PostResult(
                platform=platform,
                success=False,
                error_message=f"Platform {platform} not supported"
            )
    
    # ============================================================================
    # YOUTUBE API INTEGRATION
    # ============================================================================
    
    def _post_to_youtube(self, content: PostContent) -> PostResult:
        """Post video to YouTube"""
        if not YOUTUBE_AVAILABLE:
            return PostResult(
                platform="YouTube",
                success=False,
                error_message="YouTube API library not installed"
            )
        
        try:
            creds_dict = self.creds.get('youtube')
            
            # Build credentials object
            creds = Credentials(
                token=creds_dict['access_token'],
                refresh_token=creds_dict['refresh_token'],
                client_id=creds_dict['client_id'],
                client_secret=creds_dict['client_secret'],
                token_uri='https://oauth2.googleapis.com/token'
            )
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            # Prepare video metadata
            privacy_status = 'public'
            if content.platform_overrides and 'youtube' in content.platform_overrides:
                privacy_status = content.platform_overrides['youtube'].get('privacyStatus', 'public')

            body = {
                'snippet': {
                    'title': content.title[:100],  # Max 100 chars
                    'description': content.caption[:5000],  # Max 5000 chars
                    'tags': content.tags[:500] if content.tags else [],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            media = MediaFileUpload(content.media_path, chunksize=-1, resumable=True)
            
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            
            return PostResult(
                platform="YouTube",
                success=True,
                post_id=video_id,
                post_url=f"https://youtube.com/watch?v={video_id}"
            )
            
        except Exception as e:
            return PostResult(
                platform="YouTube",
                success=False,
                error_message=str(e)
            )
    
    # ============================================================================
    # INSTAGRAM API INTEGRATION
    # ============================================================================
    
    def _post_to_instagram(self, content: PostContent) -> PostResult:
        """Post to Instagram (Reels or Image)"""
        try:
            creds = self.creds.get('instagram')
            access_token = creds['access_token']
            account_id = creds['business_account_id']
            
            # Step 1: Create media container
            if content.media_type == 'video':
                # Reels
                container_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
                container_params = {
                    'media_type': 'REELS',
                    'video_url': content.media_path,  # Must be publicly accessible URL
                    'caption': content.caption[:2200],
                    'access_token': access_token
                }
            else:
                # Image post
                container_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
                container_params = {
                    'image_url': content.media_path,  # Must be publicly accessible URL
                    'caption': content.caption[:2200],
                    'access_token': access_token
                }
            
            container_response = requests.post(container_url, params=container_params)
            container_data = container_response.json()
            
            if 'id' not in container_data:
                return PostResult(
                    platform="Instagram",
                    success=False,
                    error_message=f"Container creation failed: {container_data}"
                )
            
            creation_id = container_data['id']
            
            # Step 2: Publish media container
            publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            
            # Wait for media to process
            time.sleep(5)
            
            publish_response = requests.post(publish_url, params=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                media_id = publish_data['id']
                return PostResult(
                    platform="Instagram",
                    success=True,
                    post_id=media_id,
                    post_url=f"https://www.instagram.com/p/{media_id}/"
                )
            else:
                return PostResult(
                    platform="Instagram",
                    success=False,
                    error_message=f"Publishing failed: {publish_data}"
                )
            
        except Exception as e:
            return PostResult(
                platform="Instagram",
                success=False,
                error_message=str(e)
            )
    
    # ============================================================================
    # TIKTOK API INTEGRATION
    # ============================================================================
    
    def _post_to_tiktok(self, content: PostContent) -> PostResult:
        """Post video to TikTok"""
        try:
            creds = self.creds.get('tiktok')
            access_token = creds['access_token']
            open_id = creds['open_id']
            
            # TikTok requires chunked upload
            # Step 1: Initialize upload
            init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            post_info = {
                'title': content.title[:150],
                'privacy_level': 'SELF_ONLY',  # or PUBLIC_TO_EVERYONE
                'disable_duet': False,
                'disable_comment': False,
                'disable_stitch': False,
                'video_cover_timestamp_ms': 1000
            }
            
            init_data = {
                'post_info': post_info,
                'source_info': {
                    'source': 'FILE_UPLOAD',
                    'video_size': os.path.getsize(content.media_path),
                    'chunk_size': 10000000,  # 10MB chunks
                    'total_chunk_count': 1
                }
            }
            
            init_response = requests.post(init_url, headers=headers, json=init_data)
            init_result = init_response.json()
            
            if init_result.get('data', {}).get('publish_id'):
                publish_id = init_result['data']['publish_id']
                upload_url = init_result['data']['upload_url']
                
                # Step 2: Upload video
                with open(content.media_path, 'rb') as video_file:
                    upload_response = requests.put(upload_url, data=video_file)
                
                if upload_response.status_code == 200:
                    return PostResult(
                        platform="TikTok",
                        success=True,
                        post_id=publish_id,
                        post_url=f"https://www.tiktok.com/@sisilola"
                    )
                else:
                    return PostResult(
                        platform="TikTok",
                        success=False,
                        error_message=f"Upload failed: {upload_response.text}"
                    )
            else:
                return PostResult(
                    platform="TikTok",
                    success=False,
                    error_message=f"Init failed: {init_result}"
                )
            
        except Exception as e:
            return PostResult(
                platform="TikTok",
                success=False,
                error_message=str(e)
            )
    
    # ============================================================================
    # FACEBOOK API INTEGRATION
    # ============================================================================
    
    def _post_to_facebook(self, content: PostContent) -> PostResult:
        """Post to Facebook Page"""
        try:
            creds = self.creds.get('facebook')
            access_token = creds['access_token']
            page_id = creds['page_id']
            
            if content.media_type == 'video':
                # Video post
                url = f"https://graph.facebook.com/v18.0/{page_id}/videos"
                params = {
                    'description': content.caption,
                    'access_token': access_token
                }
                files = {'source': open(content.media_path, 'rb')}
                response = requests.post(url, params=params, files=files)
            elif content.media_type == 'image':
                # Photo post
                url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
                params = {
                    'caption': content.caption,
                    'access_token': access_token
                }
                files = {'source': open(content.media_path, 'rb')}
                response = requests.post(url, params=params, files=files)
            else:
                # Text post
                url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
                params = {
                    'message': content.caption,
                    'access_token': access_token
                }
                response = requests.post(url, params=params)
            
            result = response.json()
            
            if 'id' in result:
                post_id = result['id']
                return PostResult(
                    platform="Facebook",
                    success=True,
                    post_id=post_id,
                    post_url=f"https://www.facebook.com/{post_id}"
                )
            else:
                return PostResult(
                    platform="Facebook",
                    success=False,
                    error_message=f"Posting failed: {result}"
                )
            
        except Exception as e:
            return PostResult(
                platform="Facebook",
                success=False,
                error_message=str(e)
            )
    
    # ============================================================================
    # TWITCH API INTEGRATION
    # ============================================================================
    
    def _post_to_twitch(self, content: PostContent) -> PostResult:
        """
        Update Twitch channel info
        Note: Twitch is primarily for live streaming, not pre-recorded content posting
        This updates channel title/category for upcoming stream
        """
        try:
            creds = self.creds.get('twitch')
            access_token = creds['access_token']
            client_id = creds['client_id']
            broadcaster_id = creds['broadcaster_id']
            
            # Update channel information
            url = "https://api.twitch.tv/helix/channels"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Client-Id': client_id,
                'Content-Type': 'application/json'
            }
            
            # Extract game/category from tags
            game_name = "Just Chatting"  # Default category
            if content.tags and len(content.tags) > 0:
                game_name = content.tags[0]
            
            data = {
                'broadcaster_id': broadcaster_id,
                'title': content.title[:140],
                'game_id': game_name,  # Would need to look up game ID
                'broadcaster_language': 'en'
            }
            
            response = requests.patch(url, headers=headers, json=data)
            
            if response.status_code == 204:
                return PostResult(
                    platform="Twitch",
                    success=True,
                    post_url=f"https://www.twitch.tv/sisilola"
                )
            else:
                return PostResult(
                    platform="Twitch",
                    success=False,
                    error_message=f"Channel update failed: {response.text}"
                )
            
        except Exception as e:
            return PostResult(
                platform="Twitch",
                success=False,
                error_message=str(e)
            )
    
    # ============================================================================
    # REDDIT API INTEGRATION
    # ============================================================================
    
    def _post_to_reddit(self, content: PostContent) -> PostResult:
        """Post to Reddit"""
        if not REDDIT_AVAILABLE:
            return PostResult(
                platform="Reddit",
                success=False,
                error_message="Reddit API library (praw) not installed"
            )
        
        try:
            creds = self.creds.get('reddit')
            
            reddit = praw.Reddit(
                client_id=creds['client_id'],
                client_secret=creds['client_secret'],
                username=creds['username'],
                password=creds['password'],
                user_agent=creds['user_agent']
            )
            
            # Target subreddit (customize based on content)
            subreddit_name = 'AfricanCulture'  # Example
            subreddit = reddit.subreddit(subreddit_name)
            
            if content.media_type == 'text':
                # Text post
                submission = subreddit.submit(
                    title=content.title,
                    selftext=content.caption
                )
            elif content.media_type == 'image':
                # Image post
                submission = subreddit.submit_image(
                    title=content.title,
                    image_path=content.media_path
                )
            elif content.media_type == 'video':
                # Video post
                submission = subreddit.submit_video(
                    title=content.title,
                    video_path=content.media_path
                )
            
            return PostResult(
                platform="Reddit",
                success=True,
                post_id=submission.id,
                post_url=submission.url
            )
            
        except Exception as e:
            return PostResult(
                platform="Reddit",
                success=False,
                error_message=str(e)
            )
    
    # ============================================================================
    # AFRICAN PLATFORMS (MANUAL WORKFLOWS)
    # ============================================================================
    
    def _post_to_vumistream(self, content: PostContent) -> PostResult:
        """
        Vumistream manual workflow guide
        Live streaming platform - requires OBS/streaming software
        """
        instructions = f"""
        VUMISTREAM MANUAL POSTING REQUIRED
        
        Platform: Live Streaming (African)
        Content: {content.title}
        
        Steps:
        1. Open OBS Studio or streaming software
        2. Configure stream key from Vumistream dashboard
        3. Set stream title: {content.title}
        4. Add stream description: {content.caption[:500]}
        5. Start stream and deliver content live
        6. Engage with live chat
        7. End stream and save VOD
        
        Monetization: Immediate (pay-per-view, tips, subscriptions)
        """
        
        print(instructions)
        
        return PostResult(
            platform="Vumistream",
            success=False,
            error_message="Manual posting required - Live streaming platform. Check console for instructions."
        )
    
    def _post_to_twiva(self, content: PostContent) -> PostResult:
        """
        Twiva manual workflow guide
        Affiliate/influencer platform
        """
        instructions = f"""
        TWIVA MANUAL POSTING REQUIRED
        
        Platform: Affiliate Marketing (African)
        Content: {content.title}
        
        Steps:
        1. Log into Twiva dashboard at https://twiva.africa
        2. Browse available campaigns matching your content
        3. Apply to campaign relevant to: {content.title}
        4. Create sponsored content integrating brand message
        5. Post to your primary platforms (Instagram, TikTok, Facebook)
        6. Track affiliate link clicks and conversions
        7. Submit proof of posting to Twiva
        
        Monetization: Commission-based (5-20% per sale)
        """
        
        print(instructions)
        
        return PostResult(
            platform="Twiva",
            success=False,
            error_message="Manual posting required - Affiliate platform. Check console for instructions."
        )
    
    def _post_to_wowzi(self, content: PostContent) -> PostResult:
        """
        Wowzi manual workflow guide
        Influencer marketing platform
        """
        instructions = f"""
        WOWZI MANUAL POSTING REQUIRED
        
        Platform: Influencer Marketplace (African)
        Content: {content.title}
        
        Steps:
        1. Log into Wowzi app or dashboard
        2. Browse available brand campaigns
        3. Apply to campaigns matching: {content.title}
        4. Follow brand content guidelines
        5. Create branded content as specified
        6. Post to approved platforms
        7. Submit content for brand approval
        8. Receive payment upon approval
        
        Monetization: Per-campaign payments (varies by brand)
        """
        
        print(instructions)
        
        return PostResult(
            platform="Wowzi",
            success=False,
            error_message="Manual posting required - Influencer platform. Check console for instructions."
        )
    
    # ============================================================================
    # DATABASE LOGGING
    # ============================================================================
    
    def _log_post_attempt(self, result: PostResult):
        """Log posting attempt to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_log (platform_name, activity_type, 
                                         activity_description, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result.platform,
                'post_attempt',
                f"Post: {result.post_id if result.success else result.error_message}",
                result.timestamp,
                'success' if result.success else 'failed'
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not log to database: {e}")
    
    # ============================================================================
    # REPORTING
    # ============================================================================
    
    def generate_report(self) -> Dict:
        """Generate posting summary report"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_platforms': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'results': [
                {
                    'platform': r.platform,
                    'success': r.success,
                    'post_url': r.post_url,
                    'error': r.error_message
                }
                for r in self.results
            ]
        }
        
        return report
    
    def print_summary(self):
        """Print posting summary to console"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("POSTING SUMMARY")
        print("="*60)
        print(f"Total Platforms: {report['total_platforms']}")
        print(f"✅ Successful: {report['successful']}")
        print(f"❌ Failed: {report['failed']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        print("\nDETAILS:")
        print("-"*60)
        
        for result in report['results']:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['platform']}")
            if result['success'] and result['post_url']:
                print(f"   URL: {result['post_url']}")
            elif not result['success']:
                print(f"   Error: {result['error']}")
        
        print("="*60)


def main():
    """Example usage"""
    # Create sample content
    content = PostContent(
        title="Celebrating African Innovation: Tech in Lagos",
        caption="""
        🌍 Discover how Lagos is becoming Africa's tech hub!
        
        Join me as we explore the incredible innovation happening across the continent.
        From fintech to AI, African creators are leading the way.
        
        #AfricanTech #Innovation #Lagos #TechHub #AfricanCulture
        """,
        media_path="/path/to/video.mp4",
        media_type="video",
        tags=["technology", "innovation", "africa"],
        hashtags=["AfricanTech", "Innovation", "Lagos"]
    )
    
    # Initialize poster
    poster = UnifiedAPIPoster()
    
    # Post to specific platforms (those with credentials configured)
    platforms_to_post = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Reddit']
    
    results = poster.post_to_all_platforms(content, platforms=platforms_to_post)
    
    # Print summary
    poster.print_summary()
    
    # Save report
    report = poster.generate_report()
    report_path = Path(__file__).parent.parent / "08_MLOPS_PIPELINE" / "reports" / f"posting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Report saved: {report_path}")


if __name__ == "__main__":
    main()
