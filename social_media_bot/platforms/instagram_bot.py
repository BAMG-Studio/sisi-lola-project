import os
import logging
from typing import List, Dict, Optional
from instagrapi import Client
from instagrapi.types import Media
from dotenv import load_dotenv
import time

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramBot:
    """Complete Instagram automation bot for Sisi Lola"""
    
    def __init__(self):
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.client = Client()
        self.session_file = 'config/instagram_session.json'
        self.login()
    
    def login(self):
        """Authenticate with Instagram using session or credentials"""
        try:
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                logger.info("Loaded existing Instagram session")
            else:
                self.client.login(self.username, self.password)
                self.client.dump_settings(self.session_file)
                logger.info(f"Successfully logged in as {self.username}")
        except Exception as e:
            logger.error(f"Failed to login: {e}")
            raise
    
    def post_photo(self, image_path: str, caption: str, hashtags: List[str] = None, location: Dict = None) -> Optional[Media]:
        """Post a photo to Instagram feed with Nigerian/African optimization"""
        try:
            if hashtags:
                # Add Sisi Lola branding hashtags
                default_hashtags = ['#SisiLolaLive', '#NewAfrica', '#AfricanContent', '#NigerianCreative']
                all_hashtags = list(set(hashtags + default_hashtags))
                caption += "\n\n" + " ".join([f"#{tag.strip('#')}" for tag in all_hashtags])
            
            media = self.client.photo_upload(
                path=image_path,
                caption=caption,
                location=location
            )
            logger.info(f"Photo posted successfully: {media.id}")
            return media
        except Exception as e:
            logger.error(f"Failed to post photo: {e}")
            return None
    
    def post_reel(self, video_path: str, caption: str, cover_path: Optional[str] = None, hashtags: List[str] = None) -> Optional[Media]:
        """Post a reel/video to Instagram"""
        try:
            if hashtags:
                default_hashtags = ['#SisiLolaLive', '#AfricanContent', '#Reels', '#AfricanCreator']
                all_hashtags = list(set(hashtags + default_hashtags))
                caption += "\n\n" + " ".join([f"#{tag.strip('#')}" for tag in all_hashtags])
            
            media = self.client.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=cover_path
            )
            logger.info(f"Reel posted successfully: {media.id}")
            return media
        except Exception as e:
            logger.error(f"Failed to post reel: {e}")
            return None
    
    def post_story(self, media_path: str, mentions: List[str] = None, links: List[str] = None) -> bool:
        """Post to Instagram story"""
        try:
            story = self.client.photo_upload_to_story(media_path, mentions=mentions or [])
            logger.info(f"Story posted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to post story: {e}")
            return False
    
    def get_comments(self, media_id: str, amount: int = 20) -> List[Dict]:
        """Get comments from a post"""
        try:
            comments = self.client.media_comments(media_id, amount=amount)
            return [{
                'user': c.user.username,
                'text': c.text,
                'created_at': c.created_at_utc,
                'pk': c.pk
            } for c in comments]
        except Exception as e:
            logger.error(f"Failed to get comments: {e}")
            return []
    
    def reply_to_comment(self, media_id: str, comment_id: str, text: str) -> bool:
        """Reply to a comment with AI-powered response"""
        try:
            self.client.media_comment(media_id, text, replied_to_comment_id=comment_id)
            logger.info(f"Replied to comment {comment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reply to comment: {e}")
            return False
    
    def auto_engage(self, hashtags: List[str], like_count: int = 10, comment_texts: List[str] = None):
        """Auto-engage with posts from specific hashtags (Nigerian/African content)"""
        default_comments = [
            "Amazing content! 🔥",
            "Love this! 💯",
            "Great post from Africa! 🌍",
            "This is the New Africa vibe! ✨",
            "Supporting African creators! 🙌"
        ]
        comments = comment_texts or default_comments
        
        for hashtag in hashtags:
            try:
                medias = self.client.hashtag_medias_recent(hashtag, amount=like_count)
                for media in medias:
                    try:
                        # Like the post
                        self.client.media_like(media.id)
                        logger.info(f"Liked post {media.id} from #{hashtag}")
                        
                        # Comment occasionally (20% chance)
                        if hash(media.id) % 5 == 0:
                            import random
                            comment = random.choice(comments)
                            self.client.media_comment(media.id, comment)
                            logger.info(f"Commented on post {media.id}")
                        
                        time.sleep(random.randint(10, 30))  # Rate limiting
                    except Exception as e:
                        logger.error(f"Failed to engage with {media.id}: {e}")
                        continue
            except Exception as e:
                logger.error(f"Failed to process hashtag #{hashtag}: {e}")
    
    def get_insights(self) -> Dict:
        """Get account insights and analytics"""
        try:
            user_info = self.client.user_info_by_username(self.username)
            return {
                'followers': user_info.follower_count,
                'following': user_info.following_count,
                'posts': user_info.media_count,
                'biography': user_info.biography
            }
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return {}

if __name__ == "__main__":
    bot = InstagramBot()
    print(bot.get_insights())
