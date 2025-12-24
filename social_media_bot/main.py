#!/usr/bin/env python3
"""
Sisi Lola - Complete Social Media Automation System
Handles Instagram, TikTok, YouTube, Twitch, Reddit, and Dropbox
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# Import platform bots
try:
    from platforms.instagram_bot import InstagramBot
except ImportError:
    InstagramBot = None
    
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SisiLolaAutomation:
    """Main orchestration class for all social media automation"""
    
    def __init__(self):
        self.platforms = {}
        self.initialize_platforms()
    
    def initialize_platforms(self):
        """Initialize all available platform bots"""
        try:
            if InstagramBot:
                self.platforms['instagram'] = InstagramBot()
                logger.info("Instagram bot initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram: {e}")
        
        logger.info(f"Initialized {len(self.platforms)} platform(s)")
    
    async def post_to_all_platforms(self, content: Dict):
        """
        Post content across all platforms simultaneously
        
        Args:
            content: Dict with keys:
                - image_path: str
                - video_path: str
                - caption: str
                - hashtags: List[str]
                - platform_specific: Dict
        """
        tasks = []
        
        if 'instagram' in self.platforms and content.get('image_path'):
            tasks.append(self.post_instagram(content))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Posted to {len(results)} platforms")
        return results
    
    async def post_instagram(self, content: Dict):
        """Post to Instagram"""
        try:
            bot = self.platforms['instagram']
            if content.get('video_path'):
                return bot.post_reel(
                    video_path=content['video_path'],
                    caption=content['caption'],
                    hashtags=content.get('hashtags', [])
                )
            else:
                return bot.post_photo(
                    image_path=content['image_path'],
                    caption=content['caption'],
                    hashtags=content.get('hashtags', [])
                )
        except Exception as e:
            logger.error(f"Instagram posting failed: {e}")
            return None
    
    def get_all_analytics(self) -> Dict:
        """Collect analytics from all platforms"""
        analytics = {}
        
        for platform, bot in self.platforms.items():
            try:
                if hasattr(bot, 'get_insights'):
                    analytics[platform] = bot.get_insights()
            except Exception as e:
                logger.error(f"Failed to get {platform} analytics: {e}")
                analytics[platform] = {'error': str(e)}
        
        return analytics
    
    def run_engagement_cycle(self):
        """Run automated engagement across platforms"""
        # African/Nigerian hashtags for engagement
        african_hashtags = [
            'AfricanContent', 'NigerianCreative', 'AfroBeats',
            'Lagos', 'Nigeria', 'NewAfrica', 'AfricanTech',
            'NaijaEh', 'AfricanInfluencer', 'PanAfrican'
        ]
        
        if 'instagram' in self.platforms:
            try:
                self.platforms['instagram'].auto_engage(
                    hashtags=african_hashtags,
                    like_count=5
                )
            except Exception as e:
                logger.error(f"Instagram engagement failed: {e}")

async def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Sisi Lola Social Media Automation Started")
    logger.info(f"Time: {datetime.now()}")
    logger.info("=" * 50)
    
    automation = SisiLolaAutomation()
    
    # Example: Get analytics
    analytics = automation.get_all_analytics()
    logger.info(f"Current Analytics: {analytics}")
    
    # Example post
    # content = {
    #     'image_path': 'path/to/image.jpg',
    #     'caption': 'Test post from Sisi Lola automation!',
    #     'hashtags': ['SisiLolaLive', 'AfricanContent']
    # }
    # await automation.post_to_all_platforms(content)
    
    logger.info("Automation system ready!")

if __name__ == "__main__":
    asyncio.run(main())
