"""
Content Queue Management System
Organize, schedule, and track content across all platforms
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import csv


class ContentType(Enum):
    """Content type categorization"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    COMMUNITY = "community"
    PROMOTIONAL = "promotional"
    SPECIAL_EVENT = "special_event"


class ContentStatus(Enum):
    """Content creation and publishing status"""
    IDEA = "idea"
    PLANNED = "planned"
    IN_PRODUCTION = "in_production"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Platform(Enum):
    """Social media platforms"""
    YOUTUBE = "YouTube"
    INSTAGRAM = "Instagram"
    TIKTOK = "TikTok"
    FACEBOOK = "Facebook"
    TWITCH = "Twitch"
    REDDIT = "Reddit"
    VUMISTREAM = "Vumistream"
    TWIVA = "Twiva"
    TWITTER = "Twitter"


@dataclass
class ContentItem:
    """Individual content piece"""
    content_id: str
    title: str
    content_type: str
    platforms: List[str]
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    media_file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    status: str = ContentStatus.IDEA.value
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    published_date: Optional[str] = None
    performance_notes: str = ""
    engagement_rate: float = 0.0
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    notes: str = ""


class ContentQueueManager:
    """Manage content queue and calendar"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.queue_file = self.data_dir / "content_queue.json"
        self.calendar_file = self.data_dir / "content_calendar.csv"
        
        self.queue: List[ContentItem] = []
        self.load_queue()
    
    def load_queue(self):
        """Load content queue from file"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r') as f:
                data = json.load(f)
                self.queue = [ContentItem(**item) for item in data]
        else:
            self.queue = []
    
    def save_queue(self):
        """Save content queue to file"""
        with open(self.queue_file, 'w') as f:
            json.dump([asdict(item) for item in self.queue], f, indent=2)
    
    def add_content(self, content: ContentItem) -> bool:
        """Add content to queue"""
        # Check for duplicate ID
        if any(item.content_id == content.content_id for item in self.queue):
            return False
        
        self.queue.append(content)
        self.save_queue()
        return True
    
    def update_content(self, content_id: str, **kwargs) -> bool:
        """Update content item"""
        for i, item in enumerate(self.queue):
            if item.content_id == content_id:
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                self.save_queue()
                return True
        return False
    
    def delete_content(self, content_id: str) -> bool:
        """Remove content from queue"""
        original_length = len(self.queue)
        self.queue = [item for item in self.queue if item.content_id != content_id]
        
        if len(self.queue) < original_length:
            self.save_queue()
            return True
        return False
    
    def get_content(self, content_id: str) -> Optional[ContentItem]:
        """Get specific content item"""
        for item in self.queue:
            if item.content_id == content_id:
                return item
        return None
    
    def get_by_status(self, status: ContentStatus) -> List[ContentItem]:
        """Get all content with specific status"""
        return [item for item in self.queue if item.status == status.value]
    
    def get_by_type(self, content_type: ContentType) -> List[ContentItem]:
        """Get all content of specific type"""
        return [item for item in self.queue if item.content_type == content_type.value]
    
    def get_by_platform(self, platform: Platform) -> List[ContentItem]:
        """Get all content for specific platform"""
        return [item for item in self.queue if platform.value in item.platforms]
    
    def get_scheduled_content(self, start_date: datetime = None, 
                            end_date: datetime = None) -> List[ContentItem]:
        """Get scheduled content within date range"""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=14)
        
        scheduled = []
        for item in self.queue:
            if item.scheduled_date:
                try:
                    item_date = datetime.fromisoformat(item.scheduled_date)
                    if start_date <= item_date <= end_date:
                        scheduled.append(item)
                except:
                    pass
        
        return sorted(scheduled, key=lambda x: x.scheduled_date)
    
    def schedule_content(self, content_id: str, date: datetime, time: str = "09:00") -> bool:
        """Schedule content for specific date and time"""
        return self.update_content(
            content_id,
            scheduled_date=date.isoformat(),
            scheduled_time=time,
            status=ContentStatus.SCHEDULED.value
        )
    
    def mark_published(self, content_id: str) -> bool:
        """Mark content as published"""
        return self.update_content(
            content_id,
            status=ContentStatus.PUBLISHED.value,
            published_date=datetime.now().isoformat()
        )
    
    def generate_calendar_csv(self):
        """Generate CSV calendar file"""
        with open(self.calendar_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Content ID', 'Title', 'Type', 'Platforms', 'Status',
                'Scheduled Date', 'Scheduled Time', 'Caption', 'Hashtags',
                'Media File', 'Notes'
            ])
            
            for item in sorted(self.queue, 
                             key=lambda x: x.scheduled_date or "9999-99-99"):
                writer.writerow([
                    item.content_id,
                    item.title,
                    item.content_type,
                    ', '.join(item.platforms),
                    item.status,
                    item.scheduled_date or '',
                    item.scheduled_time or '',
                    item.caption[:100] + '...' if len(item.caption) > 100 else item.caption,
                    ' '.join(item.hashtags),
                    item.media_file_path or '',
                    item.notes
                ])
    
    def get_content_mix_stats(self, days: int = 7) -> Dict:
        """Get content mix statistics for upcoming period"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        scheduled = self.get_scheduled_content(start_date, end_date)
        
        type_counts = {t.value: 0 for t in ContentType}
        platform_counts = {p.value: 0 for p in Platform}
        
        for item in scheduled:
            type_counts[item.content_type] = type_counts.get(item.content_type, 0) + 1
            for platform in item.platforms:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        total = len(scheduled)
        
        return {
            'total_scheduled': total,
            'by_type': type_counts,
            'by_platform': platform_counts,
            'type_percentages': {
                k: (v / total * 100) if total > 0 else 0 
                for k, v in type_counts.items()
            }
        }
    
    def check_content_mix_compliance(self, days: int = 7) -> Dict:
        """
        Check if content mix meets recommended strategy:
        40% Educational, 30% Entertainment, 20% Community, 10% Promotional
        """
        stats = self.get_content_mix_stats(days)
        percentages = stats['type_percentages']
        
        targets = {
            'educational': 40,
            'entertainment': 30,
            'community': 20,
            'promotional': 10,
            'special_event': 0
        }
        
        compliance = {}
        for content_type, target in targets.items():
            actual = percentages.get(content_type, 0)
            diff = actual - target
            compliant = abs(diff) <= 10  # Within 10% tolerance
            
            compliance[content_type] = {
                'target': target,
                'actual': actual,
                'difference': diff,
                'compliant': compliant
            }
        
        return {
            'overall_compliant': all(c['compliant'] for c in compliance.values()),
            'by_type': compliance
        }
    
    def suggest_next_content(self, days_ahead: int = 14) -> List[str]:
        """Suggest what type of content to create next based on mix"""
        compliance = self.check_content_mix_compliance(days_ahead)
        
        suggestions = []
        
        for content_type, data in compliance['by_type'].items():
            if data['difference'] < -5:  # More than 5% under target
                suggestions.append(
                    f"Create more {content_type} content "
                    f"(currently {data['actual']:.1f}%, target {data['target']}%)"
                )
        
        if not suggestions:
            suggestions.append("Content mix is balanced! Create any type you prefer.")
        
        return suggestions
    
    def generate_weekly_plan(self, start_date: datetime = None) -> Dict:
        """Generate posting plan for a week"""
        if start_date is None:
            start_date = datetime.now()
        
        # Recommended posting frequency
        daily_posts = {
            'Instagram': 1,
            'TikTok': 2,
            'Facebook': 1,
            'YouTube': 1,  # Shorts or community
            'Vumistream': 0,  # Live streams, not daily posts
            'Twitch': 0,  # Live streams
            'Reddit': 0,  # Manual, as needed
            'Twiva': 0,  # Campaign-based
        }
        
        plan = {}
        
        for day in range(7):
            date = start_date + timedelta(days=day)
            date_key = date.strftime('%Y-%m-%d (%A)')
            plan[date_key] = []
            
            for platform, count in daily_posts.items():
                for post_num in range(count):
                    plan[date_key].append({
                        'platform': platform,
                        'time': '09:00' if post_num == 0 else '18:00',
                        'type': 'TBD',
                        'status': 'empty'
                    })
        
        return plan
    
    def export_buffer_format(self, output_path: Path = None) -> Path:
        """Export scheduled content in Buffer-compatible CSV format"""
        if output_path is None:
            output_path = self.data_dir / "buffer_import.csv"
        
        scheduled = self.get_by_status(ContentStatus.SCHEDULED)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Text', 'Profile', 'Scheduled At', 'Media', 'Link'
            ])
            
            for item in scheduled:
                for platform in item.platforms:
                    # Combine caption and hashtags
                    text = f"{item.caption}\n\n{' '.join(item.hashtags)}"
                    
                    # Format scheduled datetime
                    scheduled_dt = f"{item.scheduled_date} {item.scheduled_time}"
                    
                    writer.writerow([
                        text,
                        platform,
                        scheduled_dt,
                        item.media_file_path or '',
                        ''
                    ])
        
        return output_path
    
    def generate_report(self) -> str:
        """Generate text report of content queue status"""
        total = len(self.queue)
        by_status = {}
        
        for status in ContentStatus:
            count = len(self.get_by_status(status))
            by_status[status.value] = count
        
        stats = self.get_content_mix_stats(14)
        compliance = self.check_content_mix_compliance(14)
        
        report = []
        report.append("=" * 60)
        report.append("SISI LOLA CONTENT QUEUE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Content Items: {total}")
        report.append("")
        report.append("BY STATUS:")
        for status, count in by_status.items():
            report.append(f"  {status}: {count}")
        
        report.append("")
        report.append("NEXT 14 DAYS SCHEDULED:")
        report.append(f"  Total: {stats['total_scheduled']}")
        report.append("")
        report.append("  By Type:")
        for content_type, count in stats['by_type'].items():
            pct = stats['type_percentages'][content_type]
            report.append(f"    {content_type}: {count} ({pct:.1f}%)")
        
        report.append("")
        report.append("  By Platform:")
        for platform, count in stats['by_platform'].items():
            report.append(f"    {platform}: {count}")
        
        report.append("")
        report.append("CONTENT MIX COMPLIANCE:")
        report.append(f"  Overall: {'✓ COMPLIANT' if compliance['overall_compliant'] else '✗ NEEDS ADJUSTMENT'}")
        report.append("")
        for content_type, data in compliance['by_type'].items():
            status = '✓' if data['compliant'] else '✗'
            report.append(
                f"  {status} {content_type}: {data['actual']:.1f}% "
                f"(target: {data['target']}%)"
            )
        
        report.append("")
        report.append("SUGGESTIONS:")
        for suggestion in self.suggest_next_content():
            report.append(f"  • {suggestion}")
        
        return "\n".join(report)


def seed_sample_content():
    """Create sample content for testing"""
    manager = ContentQueueManager()
    
    sample_content = [
        ContentItem(
            content_id="EDU001",
            title="African Language of the Week: Swahili",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram", "TikTok", "Facebook"],
            caption="Good morning! 🌍 Today we're learning Swahili basics. Jambo means hello! What languages do you speak?",
            hashtags=["#SisiLola", "#AfricanLanguages", "#Swahili", "#CulturalEducation"],
            scheduled_date=(datetime.now() + timedelta(days=1)).isoformat(),
            scheduled_time="09:00",
            status=ContentStatus.READY.value
        ),
        ContentItem(
            content_id="ENT001",
            title="Top 5 Afrobeats Tracks This Week",
            content_type=ContentType.ENTERTAINMENT.value,
            platforms=["Instagram", "TikTok", "YouTube"],
            caption="🎵 This week's Afrobeats hits are FIRE! Which one is your favorite?",
            hashtags=["#Afrobeats", "#AfricanMusic", "#SisiLola"],
            scheduled_date=(datetime.now() + timedelta(days=2)).isoformat(),
            scheduled_time="18:00",
            status=ContentStatus.PLANNED.value
        ),
        ContentItem(
            content_id="COM001",
            title="Community Q&A: Where Are You From?",
            content_type=ContentType.COMMUNITY.value,
            platforms=["Instagram", "Facebook", "Reddit"],
            caption="Let's get to know each other! 💛 Drop your city/country below!",
            hashtags=["#Community", "#SisiLola", "#AfricanCommunity"],
            scheduled_date=(datetime.now() + timedelta(days=3)).isoformat(),
            scheduled_time="12:00",
            status=ContentStatus.READY.value
        ),
        ContentItem(
            content_id="EDU002",
            title="African Innovation Spotlight: M-Pesa",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["YouTube", "Instagram", "LinkedIn"],
            caption="Did you know M-Pesa revolutionized mobile money? 📱💰 Let's talk about African fintech innovation!",
            hashtags=["#AfricanInnovation", "#Fintech", "#MPesa", "#SisiLola"],
            scheduled_date=(datetime.now() + timedelta(days=4)).isoformat(),
            scheduled_time="15:00",
            status=ContentStatus.IN_PRODUCTION.value
        ),
    ]
    
    for content in sample_content:
        manager.add_content(content)
    
    return manager


def main():
    """Initialize content queue system"""
    print("Initializing Sisi Lola Content Queue Manager...")
    
    manager = seed_sample_content()
    
    print("\nGenerated Report:")
    print(manager.generate_report())
    
    # Generate calendar
    manager.generate_calendar_csv()
    print(f"\n✓ Calendar CSV generated: {manager.calendar_file}")
    
    # Generate Buffer export
    buffer_file = manager.export_buffer_format()
    print(f"✓ Buffer import file generated: {buffer_file}")
    
    # Show weekly plan
    print("\n" + "=" * 60)
    print("WEEKLY POSTING PLAN TEMPLATE:")
    print("=" * 60)
    plan = manager.generate_weekly_plan()
    for date, posts in plan.items():
        print(f"\n{date}:")
        for post in posts:
            print(f"  {post['time']} - {post['platform']}")


if __name__ == "__main__":
    main()
