"""Main orchestrator for Sisi Lola Social Media Automation
Coordinates all social media bots and manages cross-platform posting.
"""

import os
from dotenv import load_dotenv
from instagram_bot import InstagramBot
from facebook_bot import FacebookBot
from youtube_bot import YouTubeBot
from twitter_bot import TwitterBot
from tiktok_bot import TikTokBot
from reddit_bot import RedditBot
from twitch_bot import TwitchBot
import schedule
import time
from datetime import datetime

load_dotenv()

class SocialMediaOrchestrator:
    def __init__(self):
        print("\n🚀 Initializing Sisi Lola Social Media Automation System...")
        
        self.bots = {}
        self._initialize_bots()
    
    def _initialize_bots(self):
        """Initialize all available social media bots"""
        
        # Instagram
        try:
            self.bots['instagram'] = InstagramBot()
            print("✅ Instagram Bot initialized")
        except Exception as e:
            print(f"❌ Instagram Bot failed: {e}")
        
        # Facebook
        try:
            self.bots['facebook'] = FacebookBot()
            print("✅ Facebook Bot initialized")
        except Exception as e:
            print(f"❌ Facebook Bot failed: {e}")
        
        # YouTube
        try:
            self.bots['youtube'] = YouTubeBot()
            print("✅ YouTube Bot initialized")
        except Exception as e:
            print(f"❌ YouTube Bot failed: {e}")
        
        # Twitter
        try:
            self.bots['twitter'] = TwitterBot()
            print("✅ Twitter Bot initialized")
        except Exception as e:
            print(f"❌ Twitter Bot failed: {e}")
        
        # TikTok
        try:
            self.bots['tiktok'] = TikTokBot()
            print("✅ TikTok Bot initialized")
        except Exception as e:
            print(f"❌ TikTok Bot failed: {e}")
        
        # Reddit
        try:
            self.bots['reddit'] = RedditBot()
            print("✅ Reddit Bot initialized")
        except Exception as e:
            print(f"❌ Reddit Bot failed: {e}")
        
        # Twitch
        try:
            self.bots['twitch'] = TwitchBot()
            print("✅ Twitch Bot initialized")
        except Exception as e:
            print(f"❌ Twitch Bot failed: {e}")
    
    def post_to_all(self, content: dict):
        """Post content to all platforms"""
        results = {}
        
        for platform, bot in self.bots.items():
            try:
                if platform == 'instagram' and 'image' in content:
                    result = bot.post_photo(
                        content['image'],
                        content.get('caption', '')
                    )
                    results[platform] = result
                
                elif platform == 'facebook':
                    if 'image' in content:
                        result = bot.post_photo(
                            content['image'],
                            content.get('caption', '')
                        )
                    else:
                        result = bot.post_text(content.get('text', ''))
                    results[platform] = result
                
                elif platform == 'twitter' and 'text' in content:
                    if 'image' in content:
                        result = bot.post_tweet_with_media(
                            content['text'],
                            content['image']
                        )
                    else:
                        result = bot.post_tweet(content['text'])
                    results[platform] = result
                
                elif platform == 'reddit' and 'subreddit' in content:
                    if 'image' in content:
                        result = bot.submit_image_post(
                            content['subreddit'],
                            content.get('title', ''),
                            content['image']
                        )
                    else:
                        result = bot.submit_text_post(
                            content['subreddit'],
                            content.get('title', ''),
                            content.get('text', '')
                        )
                    results[platform] = result
                
                print(f"✅ Posted to {platform}")
            
            except Exception as e:
                print(f"❌ Failed to post to {platform}: {e}")
                results[platform] = {'error': str(e)}
        
        return results
    
    def schedule_post(self, content: dict, schedule_time: str):
        """Schedule a post for all platforms"""
        schedule.every().day.at(schedule_time).do(
            self.post_to_all, content=content
        )
        print(f"📅 Post scheduled for {schedule_time}")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        print("⏰ Scheduler started. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    orchestrator = SocialMediaOrchestrator()
    
    print("\n" + "="*50)
    print("🌟 SISI LOLA SOCIAL MEDIA AUTOMATION READY! 🌟")
    print("="*50)
    print(f"\nActive Bots: {len(orchestrator.bots)}")
    print(f"Platforms: {', '.join(orchestrator.bots.keys())}")
    print("\nFor usage examples, see AUTOMATION_README.md")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
