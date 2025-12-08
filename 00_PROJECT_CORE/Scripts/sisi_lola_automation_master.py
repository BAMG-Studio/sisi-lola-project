"""
Sisi Lola Automation Master
Complete workflow: Generate content → Create media → Post to all platforms
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Import our modules
from sisi_lola_content_generator import SisiLolaContentGenerator
from multi_platform_poster import MultiPlatformPoster

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")


class SisiLolaAutomationMaster:
    """Master orchestrator for Sisi Lola's automated content pipeline"""
    
    def __init__(self):
        self.content_generator = SisiLolaContentGenerator()
        self.poster = MultiPlatformPoster()
        self.queue_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue"
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
        self.schedule_file = self.queue_dir / "content_schedule.json"
        self.load_schedule()
    
    def load_schedule(self):
        """Load content schedule from file"""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {
                "queue": [],
                "posted": [],
                "failed": []
            }
    
    def save_schedule(self):
        """Save content schedule to file"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule, f, indent=2, ensure_ascii=False)
    
    def add_to_queue(
        self,
        core_topic: str,
        content_type_focus: str = "educational",
        campaign_tag: str = "#SisiLolaAIStudio",
        preferred_media: str = "short_video",
        scheduled_time: Optional[str] = None,
        source_link: Optional[str] = None
    ):
        """
        Add content idea to queue
        
        Args:
            core_topic: Main topic/idea
            content_type_focus: educational|story|opinion|tutorial|recap|motivational
            campaign_tag: Campaign hashtag
            preferred_media: image|short_video|carousel|text_only|mixed
            scheduled_time: ISO format datetime string (optional)
            source_link: Reference URL (optional)
        """
        
        item = {
            "id": f"content_{int(time.time())}",
            "core_topic": core_topic,
            "content_type_focus": content_type_focus,
            "campaign_tag": campaign_tag,
            "preferred_media": preferred_media,
            "scheduled_time": scheduled_time or datetime.now().isoformat(),
            "source_link": source_link,
            "status": "queued",
            "created_at": datetime.now().isoformat()
        }
        
        self.schedule["queue"].append(item)
        self.save_schedule()
        
        print(f"✅ Added to queue: {core_topic}")
        return item
    
    def generate_content_for_queue_item(self, item: Dict) -> Optional[Dict]:
        """Generate content for a queued item"""
        
        try:
            print(f"\n{'='*70}")
            print(f"GENERATING CONTENT")
            print(f"{'='*70}")
            print(f"Topic: {item['core_topic']}")
            print(f"Type: {item['content_type_focus']}")
            
            content = self.content_generator.generate_content(
                core_topic=item['core_topic'],
                content_type_focus=item['content_type_focus'],
                campaign_tag=item['campaign_tag'],
                preferred_media=item['preferred_media'],
                source_link=item.get('source_link')
            )
            
            item['content_file'] = str(self.content_generator.output_dir / f"content_{item['id']}.json")
            item['status'] = 'generated'
            self.save_schedule()
            
            return content
        
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            item['status'] = 'generation_failed'
            item['error'] = str(e)
            self.save_schedule()
            return None
    
    def create_media_assets(self, content: Dict, item: Dict) -> Dict[str, str]:
        """
        Create media assets for content (placeholder for now)
        In production, this would call HeyGen, Runway, etc.
        
        Returns:
            Dict mapping platform to media file path
        """
        
        print(f"\n📹 Creating media assets...")
        
        # For now, return placeholder paths
        # In production, integrate with:
        # - HeyGen for talking head videos
        # - Runway/Kling for b-roll
        # - DALL-E/Midjourney for images
        
        media_assets = {}
        
        # Check if we have existing generated videos
        generated_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "generated"
        
        if generated_dir.exists():
            videos = list(generated_dir.glob("*.mp4"))
            if videos:
                # Use most recent video as placeholder
                latest_video = max(videos, key=lambda p: p.stat().st_mtime)
                media_assets['youtube'] = str(latest_video)
                media_assets['tiktok'] = str(latest_video)
                media_assets['instagram'] = str(latest_video)
                print(f"   ✅ Using existing video: {latest_video.name}")
        
        item['media_assets'] = media_assets
        item['status'] = 'media_ready'
        self.save_schedule()
        
        return media_assets
    
    def post_content(self, item: Dict) -> List[Dict]:
        """Post content to all platforms"""
        
        content_file = item.get('content_file')
        media_assets = item.get('media_assets', {})
        
        if not content_file:
            print("❌ No content file found")
            return []
        
        results = self.poster.post_all_packages(content_file, media_assets)
        
        item['post_results'] = results
        item['status'] = 'posted'
        item['posted_at'] = datetime.now().isoformat()
        
        # Move to posted list
        self.schedule['queue'].remove(item)
        self.schedule['posted'].append(item)
        self.save_schedule()
        
        return results
    
    def process_queue(self, limit: int = None):
        """
        Process queued content items
        
        Args:
            limit: Max number of items to process (None = all)
        """
        
        print(f"\n{'='*70}")
        print("SISI LOLA AUTOMATION MASTER - PROCESSING QUEUE")
        print(f"{'='*70}")
        
        queue = self.schedule['queue']
        
        if not queue:
            print("\n📭 Queue is empty. Add items with add_to_queue()")
            return
        
        items_to_process = queue[:limit] if limit else queue
        
        print(f"\n📋 Processing {len(items_to_process)} items from queue")
        
        for i, item in enumerate(items_to_process, 1):
            print(f"\n{'='*70}")
            print(f"ITEM {i}/{len(items_to_process)}")
            print(f"{'='*70}")
            
            # Check if scheduled time has passed
            scheduled_time = datetime.fromisoformat(item['scheduled_time'])
            if scheduled_time > datetime.now():
                print(f"⏰ Scheduled for {scheduled_time}, skipping for now")
                continue
            
            # Generate content
            if item['status'] == 'queued':
                content = self.generate_content_for_queue_item(item)
                if not content:
                    continue
            
            # Create media
            if item['status'] == 'generated':
                with open(item['content_file'], 'r', encoding='utf-8') as f:
                    content = json.load(f)
                media_assets = self.create_media_assets(content, item)
            
            # Post to platforms
            if item['status'] == 'media_ready':
                results = self.post_content(item)
                
                success_count = sum(1 for r in results if r['status'] == 'success')
                print(f"\n✅ Posted to {success_count}/{len(results)} platforms")
        
        print(f"\n{'='*70}")
        print("QUEUE PROCESSING COMPLETE")
        print(f"{'='*70}")
        self.print_status()
    
    def print_status(self):
        """Print current status"""
        print(f"\n📊 AUTOMATION STATUS")
        print(f"   Queued: {len(self.schedule['queue'])}")
        print(f"   Posted: {len(self.schedule['posted'])}")
        print(f"   Failed: {len(self.schedule['failed'])}")
    
    def schedule_daily_content(self, days: int = 7):
        """
        Schedule content for the next N days
        
        Args:
            days: Number of days to schedule
        """
        
        # Sample topics (in production, pull from a content calendar)
        topic_templates = [
            {
                "core_topic": "3 AI tools that saved me 10 hours this week",
                "content_type_focus": "tutorial",
                "preferred_media": "short_video"
            },
            {
                "core_topic": "Why your automation is failing (and how to fix it)",
                "content_type_focus": "educational",
                "preferred_media": "carousel"
            },
            {
                "core_topic": "Building Sisi Lola: Behind the scenes of a virtual host",
                "content_type_focus": "story",
                "preferred_media": "short_video"
            },
            {
                "core_topic": "Cloud security mistakes that cost startups millions",
                "content_type_focus": "educational",
                "preferred_media": "short_video"
            },
            {
                "core_topic": "My morning routine as a virtual influencer",
                "content_type_focus": "motivational",
                "preferred_media": "short_video"
            }
        ]
        
        print(f"\n📅 Scheduling content for next {days} days...")
        
        for day in range(days):
            scheduled_time = datetime.now() + timedelta(days=day, hours=10)  # 10 AM each day
            
            # Rotate through topics
            topic = topic_templates[day % len(topic_templates)]
            
            self.add_to_queue(
                core_topic=topic['core_topic'],
                content_type_focus=topic['content_type_focus'],
                campaign_tag="#SisiLolaAIStudio",
                preferred_media=topic['preferred_media'],
                scheduled_time=scheduled_time.isoformat()
            )
        
        print(f"✅ Scheduled {days} content items")
        self.print_status()


def main():
    """Interactive menu"""
    
    master = SisiLolaAutomationMaster()
    
    while True:
        print(f"\n{'='*70}")
        print("SISI LOLA AUTOMATION MASTER")
        print(f"{'='*70}")
        print("\n1. Add single content to queue")
        print("2. Schedule 7 days of content")
        print("3. Process queue now")
        print("4. View status")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            topic = input("\nEnter topic: ").strip()
            if topic:
                master.add_to_queue(
                    core_topic=topic,
                    content_type_focus="educational",
                    preferred_media="short_video"
                )
        
        elif choice == '2':
            master.schedule_daily_content(days=7)
        
        elif choice == '3':
            limit = input("\nProcess how many items? (Enter for all): ").strip()
            limit = int(limit) if limit.isdigit() else None
            master.process_queue(limit=limit)
        
        elif choice == '4':
            master.print_status()
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
