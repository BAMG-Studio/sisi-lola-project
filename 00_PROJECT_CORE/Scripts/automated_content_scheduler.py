"""
Automated Content Scheduler
Intelligent scheduling with queue management, mix compliance, and optimal timing
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random


class ContentType(Enum):
    """Content categorization"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    COMMUNITY = "community"
    PROMOTIONAL = "promotional"


class ScheduleStatus(Enum):
    """Schedule status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledPost:
    """Scheduled post data model"""
    id: Optional[int] = None
    title: str = ""
    caption: str = ""
    media_path: Optional[str] = None
    media_type: str = "video"
    content_type: str = ContentType.EDUCATIONAL.value
    platforms: List[str] = None
    schedule_time: Optional[str] = None
    status: str = ScheduleStatus.PENDING.value
    created_at: Optional[str] = None
    posted_at: Optional[str] = None
    tags: List[str] = None
    hashtags: List[str] = None
    priority: int = 5
    notes: Optional[str] = None


class OptimalTimingEngine:
    """Calculates optimal posting times for each platform"""
    
    # Best posting times (hour in 24h format) for each platform
    PLATFORM_BEST_TIMES = {
        'YouTube': [14, 15, 16, 18, 19, 20],  # 2-8 PM
        'Instagram': [11, 12, 13, 17, 18, 19],  # 11 AM-1 PM, 5-7 PM
        'TikTok': [9, 12, 15, 18, 21],  # 9 AM, 12 PM, 3 PM, 6 PM, 9 PM
        'Facebook': [13, 14, 15, 18, 19],  # 1-3 PM, 6-7 PM
        'Twitch': [19, 20, 21, 22],  # 7-10 PM (evening)
        'Reddit': [7, 8, 9, 12, 17, 18],  # Morning and evening
        'Vumistream': [19, 20, 21],  # Evening (African time)
        'Twiva': [10, 11, 12, 14, 15],  # Business hours
        'Wowzi': [10, 11, 12, 14, 15]  # Business hours
    }
    
    # Best days of week (0=Monday, 6=Sunday) for each platform
    PLATFORM_BEST_DAYS = {
        'YouTube': [1, 2, 3, 4, 5],  # Tuesday-Saturday
        'Instagram': [0, 1, 2, 3, 4],  # Monday-Friday
        'TikTok': [1, 2, 3, 4, 5, 6],  # All week
        'Facebook': [0, 1, 2, 3],  # Monday-Thursday
        'Twitch': [4, 5, 6],  # Friday-Sunday
        'Reddit': [0, 1, 2, 3, 4],  # Weekdays
        'Vumistream': [4, 5, 6],  # Weekends
        'Twiva': [0, 1, 2, 3, 4],  # Weekdays
        'Wowzi': [0, 1, 2, 3, 4]  # Weekdays
    }
    
    @staticmethod
    def get_optimal_time(platform: str, days_ahead: int = 1) -> datetime:
        """
        Calculate optimal posting time for a platform
        
        Args:
            platform: Platform name
            days_ahead: How many days in the future to schedule
        
        Returns:
            Optimal datetime for posting
        """
        base_time = datetime.now() + timedelta(days=days_ahead)
        
        # Find next best day
        best_days = OptimalTimingEngine.PLATFORM_BEST_DAYS.get(platform, [0, 1, 2, 3, 4])
        current_day = base_time.weekday()
        
        # If current day is not optimal, find next best day
        if current_day not in best_days:
            days_to_add = 1
            while (current_day + days_to_add) % 7 not in best_days:
                days_to_add += 1
            base_time += timedelta(days=days_to_add)
        
        # Select random hour from best times
        best_hours = OptimalTimingEngine.PLATFORM_BEST_TIMES.get(platform, [12, 14, 16, 18])
        optimal_hour = random.choice(best_hours)
        
        # Set time
        optimal_time = base_time.replace(
            hour=optimal_hour,
            minute=random.randint(0, 59),
            second=0,
            microsecond=0
        )
        
        return optimal_time
    
    @staticmethod
    def generate_staggered_schedule(platforms: List[str], base_time: datetime = None) -> Dict[str, datetime]:
        """
        Generate staggered posting times across platforms
        Spaces posts 15-30 minutes apart
        
        Args:
            platforms: List of platform names
            base_time: Starting time (defaults to now + 1 hour)
        
        Returns:
            Dictionary mapping platform to scheduled time
        """
        if base_time is None:
            base_time = datetime.now() + timedelta(hours=1)
        
        schedule = {}
        current_time = base_time
        
        for platform in platforms:
            schedule[platform] = current_time
            # Stagger by 15-30 minutes
            current_time += timedelta(minutes=random.randint(15, 30))
        
        return schedule


class AutomatedContentScheduler:
    """
    Automated content scheduling system with:
    - Intelligent queue management
    - Content mix compliance
    - Optimal timing
    - Priority-based scheduling
    - Platform-specific optimization
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_path = Path(__file__).parent.parent
            db_path = base_path / "05_BRANDING_ARTIFACTS" / "content_schedule.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()
        
        # Content mix targets
        self.content_mix_targets = {
            ContentType.EDUCATIONAL.value: 0.40,
            ContentType.ENTERTAINMENT.value: 0.30,
            ContentType.COMMUNITY.value: 0.20,
            ContentType.PROMOTIONAL.value: 0.10
        }
    
    def initialize_database(self):
        """Create database tables"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Scheduled posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                caption TEXT NOT NULL,
                media_path TEXT,
                media_type TEXT DEFAULT 'video',
                content_type TEXT NOT NULL,
                platforms TEXT,
                schedule_time TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                posted_at TEXT,
                tags TEXT,
                hashtags TEXT,
                priority INTEGER DEFAULT 5,
                notes TEXT
            )
        ''')
        
        # Platform schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                schedule_time TEXT NOT NULL,
                posted BOOLEAN DEFAULT 0,
                post_id_on_platform TEXT,
                post_url TEXT,
                error_message TEXT,
                FOREIGN KEY (post_id) REFERENCES scheduled_posts(id)
            )
        ''')
        
        # Content mix tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_mix_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                content_type TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                percentage REAL DEFAULT 0.0,
                UNIQUE(date, content_type)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_post(self, post: ScheduledPost, auto_schedule: bool = True) -> int:
        """
        Add post to queue
        
        Args:
            post: ScheduledPost object
            auto_schedule: If True, automatically calculate optimal schedule time
        
        Returns:
            Post ID
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Set created_at if not provided
        if post.created_at is None:
            post.created_at = datetime.now().isoformat()
        
        # Auto-schedule if requested and no schedule time provided
        if auto_schedule and post.schedule_time is None:
            # Find next available slot based on content mix
            post.schedule_time = self._calculate_next_slot(post.content_type)
        
        # Convert lists to JSON strings
        platforms_json = json.dumps(post.platforms) if post.platforms else json.dumps([])
        tags_json = json.dumps(post.tags) if post.tags else json.dumps([])
        hashtags_json = json.dumps(post.hashtags) if post.hashtags else json.dumps([])
        
        cursor.execute('''
            INSERT INTO scheduled_posts (
                title, caption, media_path, media_type, content_type,
                platforms, schedule_time, status, created_at, tags,
                hashtags, priority, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.title, post.caption, post.media_path, post.media_type,
            post.content_type, platforms_json, post.schedule_time,
            post.status, post.created_at, tags_json, hashtags_json,
            post.priority, post.notes
        ))
        
        post_id = cursor.lastrowid
        
        # Create platform-specific schedules if platforms specified
        if post.platforms and post.schedule_time:
            self._create_platform_schedules(cursor, post_id, post.platforms, post.schedule_time)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Post added to queue (ID: {post_id})")
        print(f"   Title: {post.title}")
        print(f"   Scheduled: {post.schedule_time}")
        print(f"   Platforms: {', '.join(post.platforms) if post.platforms else 'None'}")
        
        return post_id
    
    def _create_platform_schedules(self, cursor, post_id: int, platforms: List[str], base_time: str):
        """Create staggered platform-specific schedules"""
        base_datetime = datetime.fromisoformat(base_time)
        
        # Generate staggered schedule
        staggered_schedule = OptimalTimingEngine.generate_staggered_schedule(
            platforms, base_datetime
        )
        
        for platform, schedule_time in staggered_schedule.items():
            cursor.execute('''
                INSERT INTO platform_schedules (
                    post_id, platform, schedule_time
                ) VALUES (?, ?, ?)
            ''', (post_id, platform, schedule_time.isoformat()))
    
    def _calculate_next_slot(self, content_type: str) -> str:
        """
        Calculate next available time slot based on content mix compliance
        Ensures we don't over-post one content type
        
        Args:
            content_type: Type of content being scheduled
        
        Returns:
            ISO format datetime string
        """
        # Get current mix
        current_mix = self.get_content_mix_current()
        
        # Determine days ahead based on queue density
        target_percentage = self.content_mix_targets.get(content_type, 0.25)
        current_percentage = current_mix.get(content_type, 0)
        
        # If we're over quota, schedule further out
        if current_percentage > target_percentage:
            days_ahead = random.randint(3, 7)
        elif current_percentage < target_percentage * 0.5:
            # Under quota - schedule soon
            days_ahead = random.randint(1, 2)
        else:
            # Within range - normal scheduling
            days_ahead = random.randint(1, 3)
        
        # Use optimal timing engine
        optimal_time = OptimalTimingEngine.get_optimal_time('Instagram', days_ahead)
        
        return optimal_time.isoformat()
    
    def get_pending_posts(self, limit: int = 50) -> List[Dict]:
        """Get all pending posts"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scheduled_posts
            WHERE status = 'pending' OR status = 'scheduled'
            ORDER BY priority DESC, schedule_time ASC
            LIMIT ?
        ''', (limit,))
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for post in posts:
            post['platforms'] = json.loads(post['platforms']) if post['platforms'] else []
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
            post['hashtags'] = json.loads(post['hashtags']) if post['hashtags'] else []
        
        return posts
    
    def get_posts_due_now(self, window_minutes: int = 30) -> List[Dict]:
        """
        Get posts due for posting within the time window
        
        Args:
            window_minutes: Time window in minutes
        
        Returns:
            List of posts ready to post
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now()
        window_end = now + timedelta(minutes=window_minutes)
        
        cursor.execute('''
            SELECT * FROM scheduled_posts
            WHERE status = 'scheduled'
            AND schedule_time <= ?
            AND schedule_time >= ?
            ORDER BY priority DESC, schedule_time ASC
        ''', (window_end.isoformat(), now.isoformat()))
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for post in posts:
            post['platforms'] = json.loads(post['platforms']) if post['platforms'] else []
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
            post['hashtags'] = json.loads(post['hashtags']) if post['hashtags'] else []
        
        return posts
    
    def update_post_status(self, post_id: int, status: ScheduleStatus, posted_at: str = None) -> bool:
        """Update post status"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if posted_at is None and status == ScheduleStatus.POSTED:
            posted_at = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE scheduled_posts
            SET status = ?, posted_at = ?
            WHERE id = ?
        ''', (status.value, posted_at, post_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update_platform_schedule(self, post_id: int, platform: str, 
                                 posted: bool = True, post_url: str = None,
                                 error_message: str = None) -> bool:
        """Update platform-specific posting status"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE platform_schedules
            SET posted = ?, post_url = ?, error_message = ?
            WHERE post_id = ? AND platform = ?
        ''', (posted, post_url, error_message, post_id, platform))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_content_mix_current(self) -> Dict[str, float]:
        """
        Get current content mix percentages for upcoming scheduled posts
        
        Returns:
            Dictionary mapping content type to percentage
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content_type, COUNT(*) as count
            FROM scheduled_posts
            WHERE status IN ('pending', 'scheduled')
            GROUP BY content_type
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        total = sum(row[1] for row in rows)
        if total == 0:
            return {}
        
        mix = {row[0]: row[1] / total for row in rows}
        return mix
    
    def check_content_mix_compliance(self) -> Dict:
        """
        Check if scheduled content meets target mix
        
        Returns:
            Dictionary with compliance status and recommendations
        """
        current_mix = self.get_content_mix_current()
        
        compliance = {
            'compliant': True,
            'current_mix': current_mix,
            'target_mix': self.content_mix_targets,
            'issues': [],
            'recommendations': []
        }
        
        for content_type, target_pct in self.content_mix_targets.items():
            current_pct = current_mix.get(content_type, 0)
            difference = abs(current_pct - target_pct)
            
            if difference > 0.15:  # More than 15% off target
                compliance['compliant'] = False
                if current_pct < target_pct:
                    compliance['issues'].append(
                        f"Need more {content_type} content ({current_pct:.1%} vs {target_pct:.1%})"
                    )
                    compliance['recommendations'].append(
                        f"Schedule {int((target_pct - current_pct) * 20)} more {content_type} posts"
                    )
                else:
                    compliance['issues'].append(
                        f"Too much {content_type} content ({current_pct:.1%} vs {target_pct:.1%})"
                    )
        
        return compliance
    
    def generate_weekly_schedule(self, num_posts_per_day: int = 2) -> List[ScheduledPost]:
        """
        Generate a balanced weekly schedule
        
        Args:
            num_posts_per_day: Number of posts per day
        
        Returns:
            List of ScheduledPost objects
        """
        posts = []
        platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Reddit']
        
        # Calculate posts per content type for the week
        total_posts = num_posts_per_day * 7
        posts_by_type = {}
        
        for content_type, percentage in self.content_mix_targets.items():
            posts_by_type[content_type] = int(total_posts * percentage)
        
        # Generate posts
        post_templates = {
            ContentType.EDUCATIONAL.value: [
                "African Innovation: ",
                "Tech Tutorial: ",
                "Cultural Deep Dive: ",
                "How It Works: "
            ],
            ContentType.ENTERTAINMENT.value: [
                "Behind the Scenes: ",
                "Fun Facts: ",
                "Story Time: ",
                "Trending: "
            ],
            ContentType.COMMUNITY.value: [
                "Community Spotlight: ",
                "Q&A Session: ",
                "Fan Feature: ",
                "Weekly Roundup: "
            ],
            ContentType.PROMOTIONAL.value: [
                "New Content Alert: ",
                "Special Announcement: ",
                "Collaboration: "
            ]
        }
        
        day_counter = 0
        for content_type, count in posts_by_type.items():
            for i in range(count):
                template = random.choice(post_templates[content_type])
                
                post = ScheduledPost(
                    title=f"{template}Episode {day_counter + 1}",
                    caption=f"Amazing content about African culture and innovation! #{content_type}",
                    media_type="video",
                    content_type=content_type,
                    platforms=platforms,
                    priority=random.randint(3, 7),
                    status=ScheduleStatus.PENDING.value
                )
                
                posts.append(post)
                day_counter += 1
        
        return posts
    
    def export_calendar(self, filepath: str = None):
        """Export schedule to CSV calendar format"""
        if filepath is None:
            filepath = Path(__file__).parent.parent / "03_MEDIA_ASSETS" / "content_queue" / "schedule_calendar.csv"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        posts = self.get_pending_posts(limit=1000)
        
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Time', 'Title', 'Type', 'Platforms', 'Status', 'Priority'])
            
            for post in posts:
                if post['schedule_time']:
                    dt = datetime.fromisoformat(post['schedule_time'])
                    writer.writerow([
                        dt.strftime('%Y-%m-%d'),
                        dt.strftime('%H:%M'),
                        post['title'],
                        post['content_type'],
                        ', '.join(post['platforms']),
                        post['status'],
                        post['priority']
                    ])
        
        print(f"📅 Calendar exported to: {filepath}")
        return filepath
    
    def print_schedule_summary(self):
        """Print schedule summary"""
        pending = self.get_pending_posts()
        due_now = self.get_posts_due_now()
        mix_check = self.check_content_mix_compliance()
        
        print("=" * 60)
        print("CONTENT SCHEDULE SUMMARY")
        print("=" * 60)
        print(f"Pending Posts: {len(pending)}")
        print(f"Due Now (30 min): {len(due_now)}")
        print(f"\nContent Mix Compliance: {'✅ YES' if mix_check['compliant'] else '❌ NO'}")
        print("\nCurrent Mix:")
        for content_type, percentage in mix_check['current_mix'].items():
            target = mix_check['target_mix'].get(content_type, 0)
            print(f"  {content_type}: {percentage:.1%} (target: {target:.1%})")
        
        if mix_check['recommendations']:
            print("\nRecommendations:")
            for rec in mix_check['recommendations']:
                print(f"  • {rec}")
        
        print("\nUpcoming Posts (Next 5):")
        print("-" * 60)
        for post in pending[:5]:
            schedule_time = post['schedule_time']
            if schedule_time:
                dt = datetime.fromisoformat(schedule_time)
                print(f"{dt.strftime('%b %d, %H:%M')} - {post['title']}")
                print(f"  Type: {post['content_type']} | Priority: {post['priority']}")
        
        print("=" * 60)


def main():
    """Example usage"""
    scheduler = AutomatedContentScheduler()
    
    # Add sample posts
    platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Reddit']
    
    posts = [
        ScheduledPost(
            title="African Innovation: Lagos Tech Scene",
            caption="Discover the incredible tech innovation happening in Lagos! 🌍 #AfricanTech",
            media_type="video",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=platforms,
            priority=8
        ),
        ScheduledPost(
            title="Behind the Scenes: Creating AI Content",
            caption="See how I create content as an AI! 🤖 #BehindTheScenes",
            media_type="video",
            content_type=ContentType.ENTERTAINMENT.value,
            platforms=platforms,
            priority=6
        ),
        ScheduledPost(
            title="Community Q&A: Your Questions Answered",
            caption="Thanks for all your amazing questions! Let's dive in! 💬 #Community",
            media_type="video",
            content_type=ContentType.COMMUNITY.value,
            platforms=platforms,
            priority=7
        ),
    ]
    
    # Add posts to schedule
    for post in posts:
        scheduler.add_post(post, auto_schedule=True)
    
    # Print summary
    scheduler.print_schedule_summary()
    
    # Export calendar
    scheduler.export_calendar()
    
    # Check compliance
    compliance = scheduler.check_content_mix_compliance()
    print(f"\n✅ Content mix compliant: {compliance['compliant']}")


if __name__ == "__main__":
    main()
