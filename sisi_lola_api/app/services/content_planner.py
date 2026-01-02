"""
SISI LOLA CONTENT PLANNER
=========================
Intelligent content scheduling and optimization service.

Features:
- Multi-platform scheduling (TikTok, Instagram, YouTube)
- Optimal posting time calculation
- Content calendar management
- Trend analysis and recommendations
- Batch production planning
"""

import os
import json
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class Platform(Enum):
    """Supported social platforms"""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class ContentType(Enum):
    """Types of content"""
    SHORT_VIDEO = "short_video"
    LONG_VIDEO = "long_video"
    STORY = "story"
    POST = "post"
    LIVE = "live"


class VibeCategory(Enum):
    """Content vibe categories"""
    TECH_REVIEW = "tech_review"
    CULTURAL = "cultural"
    ENTERTAINMENT = "entertainment"
    SPIRITUAL = "spiritual"
    EDUCATIONAL = "educational"
    TRENDING = "trending"


@dataclass
class TimeSlot:
    """Optimal posting time slot"""
    hour: int
    engagement_score: float
    audience_active: float
    competition_level: float


@dataclass
class ContentItem:
    """A piece of content in the calendar"""
    id: str
    title: str
    script: str
    vibe_category: VibeCategory
    content_type: ContentType
    platforms: List[Platform]
    scheduled_time: Optional[datetime]
    status: str
    tags: List[str]
    metrics: Dict[str, Any]


OPTIMAL_TIMES_BY_PLATFORM: Dict[str, List[TimeSlot]] = {
    "tiktok": [
        TimeSlot(hour=7, engagement_score=0.75, audience_active=0.60, competition_level=0.40),
        TimeSlot(hour=12, engagement_score=0.85, audience_active=0.80, competition_level=0.70),
        TimeSlot(hour=18, engagement_score=0.90, audience_active=0.85, competition_level=0.65),
        TimeSlot(hour=20, engagement_score=0.95, audience_active=0.90, competition_level=0.55),
    ],
    "instagram": [
        TimeSlot(hour=8, engagement_score=0.70, audience_active=0.65, competition_level=0.50),
        TimeSlot(hour=12, engagement_score=0.80, audience_active=0.75, competition_level=0.60),
        TimeSlot(hour=17, engagement_score=0.85, audience_active=0.80, competition_level=0.55),
        TimeSlot(hour=19, engagement_score=0.90, audience_active=0.85, competition_level=0.50),
    ],
    "youtube": [
        TimeSlot(hour=10, engagement_score=0.70, audience_active=0.60, competition_level=0.45),
        TimeSlot(hour=14, engagement_score=0.80, audience_active=0.70, competition_level=0.50),
        TimeSlot(hour=17, engagement_score=0.85, audience_active=0.80, competition_level=0.60),
        TimeSlot(hour=20, engagement_score=0.90, audience_active=0.85, competition_level=0.55),
    ],
}

DAY_MULTIPLIERS = {0: 0.85, 1: 0.90, 2: 0.95, 3: 1.00, 4: 1.05, 5: 0.95, 6: 0.90}

TRENDING_CATEGORIES = {
    "tech": ["iPhone 15 reviews", "Best budget phones 2024", "AI tools for students", "How to make money online"],
    "cultural": ["Afrobeats updates", "Nigerian wedding trends", "Japa chronicles", "Lagos life"],
    "entertainment": ["BBNaija highlights", "Nollywood reviews", "Skit maker drama", "Celebrity news"],
    "educational": ["Study abroad tips", "JAMB/WAEC prep", "Scholarship alerts", "Career advice"],
}


class ContentPlanner:
    """Intelligent content planning and scheduling service"""
    
    def __init__(self):
        self.calendar: Dict[str, ContentItem] = {}
        self.content_counter = 0
    
    def get_optimal_posting_time(
        self,
        platform: str,
        content_type: ContentType = ContentType.SHORT_VIDEO,
        target_date: Optional[datetime] = None,
        avoid_times: Optional[List[datetime]] = None
    ) -> Tuple[datetime, Dict[str, Any]]:
        """Calculate optimal posting time for content"""
        if target_date is None:
            target_date = datetime.now() + timedelta(days=1)
        
        platform_times = OPTIMAL_TIMES_BY_PLATFORM.get(platform, OPTIMAL_TIMES_BY_PLATFORM["tiktok"])
        day_mult = DAY_MULTIPLIERS.get(target_date.weekday(), 1.0)
        
        scored_slots = []
        for slot in platform_times:
            potential_time = target_date.replace(hour=slot.hour, minute=0, second=0, microsecond=0)
            
            if avoid_times and any(abs((potential_time - t).total_seconds()) < 3600 for t in avoid_times):
                continue
            
            score = (slot.engagement_score * 0.5 + slot.audience_active * 0.3 + (1 - slot.competition_level) * 0.2) * day_mult
            scored_slots.append((potential_time, slot, score))
        
        if not scored_slots:
            best_slot = platform_times[0]
            best_time = target_date.replace(hour=best_slot.hour, minute=0, second=0)
            score = best_slot.engagement_score * day_mult
        else:
            scored_slots.sort(key=lambda x: x[2], reverse=True)
            best_time, best_slot, score = scored_slots[0]
        
        analysis = {
            "platform": platform,
            "optimal_time": best_time.isoformat(),
            "expected_engagement": f"{score:.0%}",
            "audience_active": f"{best_slot.audience_active:.0%}",
            "competition": f"{best_slot.competition_level:.0%}",
        }
        
        return best_time, analysis
    
    def create_content_item(
        self,
        title: str,
        script: str,
        vibe_category: str = "entertainment",
        platforms: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> ContentItem:
        """Create a new content item for the calendar"""
        self.content_counter += 1
        
        item = ContentItem(
            id=f"SISI-{self.content_counter:04d}",
            title=title,
            script=script,
            vibe_category=VibeCategory(vibe_category),
            content_type=ContentType.SHORT_VIDEO,
            platforms=[Platform(p) for p in (platforms or ["tiktok", "instagram"])],
            scheduled_time=scheduled_time,
            status="draft",
            tags=tags or [],
            metrics={},
        )
        
        self.calendar[item.id] = item
        return item
    
    def schedule_content(self, content_id: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """Schedule content for optimal posting time"""
        if content_id not in self.calendar:
            raise ValueError(f"Content {content_id} not found")
        
        item = self.calendar[content_id]
        avoid_times = [c.scheduled_time for c in self.calendar.values() if c.scheduled_time and c.id != content_id]
        target_platform = platform or item.platforms[0].value
        
        optimal_time, analysis = self.get_optimal_posting_time(target_platform, item.content_type, avoid_times=avoid_times)
        
        item.scheduled_time = optimal_time
        item.status = "scheduled"
        
        return {"content_id": content_id, "title": item.title, "scheduled_time": optimal_time.isoformat(), "platform": target_platform, "analysis": analysis}
    
    def get_weekly_calendar(self, start_date: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get weekly content calendar"""
        if start_date is None:
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
        
        week = {}
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_key = day.strftime("%A, %B %d")
            week[day_key] = []
        
        for item in self.calendar.values():
            if item.scheduled_time:
                day_key = item.scheduled_time.strftime("%A, %B %d")
                if day_key in week:
                    week[day_key].append({"id": item.id, "title": item.title, "time": item.scheduled_time.strftime("%H:%M"), "platforms": [p.value for p in item.platforms], "status": item.status})
        
        for day_key in week:
            week[day_key].sort(key=lambda x: x["time"])
        
        return week
    
    def generate_content_ideas(self, category: str = "tech", count: int = 5) -> List[Dict[str, Any]]:
        """Generate content ideas based on trending topics"""
        topics = TRENDING_CATEGORIES.get(category, TRENDING_CATEGORIES["tech"])
        
        ideas = []
        for topic in topics[:count]:
            script = self._generate_script_for_topic(topic, category)
            ideas.append({"topic": topic, "category": category, "suggested_script": script, "recommended_platforms": ["tiktok", "instagram"], "estimated_production_time": "5 minutes", "trend_score": 0.85})
        
        return ideas
    
    def _generate_script_for_topic(self, topic: str, category: str) -> str:
        """Generate Sisi Lola style script for topic"""
        import random
        intros = ["Ehen! Make I yarn you about", "Oya, gather round o! Today we dey talk about", "Chai! You no go believe this one about"]
        outros = ["So wetin you think? Drop comment make we yarn!", "That's the tea o! Like and follow for more gist!", "Na so e be! Share am give your people!"]
        
        return f"{random.choice(intros)} {topic}. [MAIN CONTENT HERE] {random.choice(outros)}"
    
    def plan_batch_production(self, content_count: int = 7, category: str = "tech") -> Dict[str, Any]:
        """Plan a batch production session"""
        ideas = self.generate_content_ideas(category, content_count)
        
        time_per_video = 4
        total_time = content_count * time_per_video
        cost_per_video = 0.50
        total_cost = content_count * cost_per_video
        
        schedule = []
        base_time = datetime.now() + timedelta(days=1)
        
        for i, idea in enumerate(ideas):
            item = self.create_content_item(title=idea["topic"], script=idea["suggested_script"], vibe_category=category)
            result = self.schedule_content(item.id)
            schedule.append(result)
            base_time = base_time + timedelta(days=1)
        
        return {
            "batch_id": f"BATCH-{datetime.now().strftime('%Y%m%d')}",
            "content_count": content_count,
            "category": category,
            "estimated_production_time": f"{total_time} minutes",
            "estimated_cost": f"${total_cost:.2f}",
            "schedule": schedule,
            "recommendations": ["Record all scripts in one session for consistency", "Prepare backgrounds and thumbnails beforehand", "Schedule during optimal engagement windows"]
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of content calendar and analytics"""
        total = len(self.calendar)
        scheduled = sum(1 for c in self.calendar.values() if c.status == "scheduled")
        published = sum(1 for c in self.calendar.values() if c.status == "published")
        draft = sum(1 for c in self.calendar.values() if c.status == "draft")
        
        categories = {}
        for item in self.calendar.values():
            cat = item.vibe_category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        return {"total_content": total, "scheduled": scheduled, "published": published, "draft": draft, "by_category": categories}


_planner: Optional[ContentPlanner] = None

def get_content_planner() -> ContentPlanner:
    """Get singleton content planner instance"""
    global _planner
    if _planner is None:
        _planner = ContentPlanner()
    return _planner


if __name__ == "__main__":
    planner = get_content_planner()
    print("SISI LOLA CONTENT PLANNER")
    print("=" * 40)
    
    for platform in ["tiktok", "instagram", "youtube"]:
        optimal_time, analysis = planner.get_optimal_posting_time(platform)
        print(f"  {platform.upper()}: {optimal_time.strftime('%A %H:%M')} - {analysis['expected_engagement']}")
    
    ideas = planner.generate_content_ideas("tech", count=3)
    for idea in ideas:
        print(f"  - {idea['topic']}")
