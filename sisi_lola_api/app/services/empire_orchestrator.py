"""
SISI LOLA ORCHESTRATOR - THE MEDIA EMPIRE LOGIC
==============================================
This service implements the "Strategic North Star" for Sisi Lola.
Handling:
1. Production Pipelines (Radio, Tutor, Clinic)
2. Distribution Routing (Social OAuth)
3. Intelligence Feed (Daily Gist)
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class WorkMode(str, Enum):
    RADIO_HOST = "radio_host"       # Daily 5-10 min shows
    CULTURE_TUTOR = "culture_tutor" # Tongue twister / Proverb of the day
    HUSTLE_CLINIC = "hustle_clinic" # Relationship & Work advice
    BRAND_AVATAR = "brand_avatar"   # Explainer videos for partners
    CONCERT_HOST = "concert_host"   # Afrobeats compère

class MediaEmpireOrchestrator:
    def __init__(self):
        self.active_mode = WorkMode.RADIO_HOST
        from .gist_hunter import GistHunter
        from ..utils.aunty_wisdom import AUNTY_WISDOM, get_wisdom_for_topic
        from ..utils.rvc_manager import rvc_manager
        from .story_world_engine import story_engine
        from .brand_avatar_service import brand_service
        
        self.hunter = GistHunter()
        self.rvc = rvc_manager
        self.wisdom_lookup = get_wisdom_for_topic
        self.story_engine = story_engine
        self.brand_service = brand_service

    async def prepare_morning_show(self, duration_mins: int = 5) -> Dict[str, Any]:
        """Produce the full script and sequence for the Morning Show"""
        print(f"🎙️ EMPIRE: Producing {duration_mins}min Morning Show...")
        
        # 1. Fetch live gist
        gists = await self.hunter.gather_all_daily_gist()
        briefing = self.hunter.generate_daily_briefing(gists)
        
        # 2. Structure the show
        show_structure = {
            "title": f"Sisi Lola Morning Vibe - {datetime.now().strftime('%Y-%m-%d')}",
            "segments": [
                {"type": "intro", "duration": 30, "description": "High energy Yoruba-English welcome"},
                {"type": "news_headlines", "content": briefing, "duration": 120},
                {"type": "afrobeats_gossip", "duration": 90, "description": "Latest Burna/Wizkid/Davido gist"},
                {"type": "aunty_advice_mini", "duration": 60, "topic": "Daily Hustle"},
                {"type": "outro", "duration": 30}
            ]
        }
        return show_structure

    async def generate_culture_lesson(self, category: str = "proverbs") -> Dict[str, Any]:
        """Generate a market-ready culture lesson script"""
        print(f"📖 EMPIRE: Generating Culture Lesson: {category}")
        
        from ..utils.aunty_wisdom import AUNTY_WISDOM
        import random
        
        if category == "proverbs":
            lesson = random.choice(AUNTY_WISDOM["yorunglish_proverbs"])
            return {
                "lesson_type": "proverb",
                "native": lesson["native"],
                "pidgin": lesson["pidgin"],
                "meaning": lesson["meaning"],
                "script": f"Oya, today's Yoruba proverb is: {lesson['native']}. In simple English, it means {lesson['meaning']}. My people, pay attention!"
            }
        return {"error": "Category not found"}

    async def route_hustle_clinic(self, user_query: str) -> str:
        """Get the full Aunty Sisi advice for a user query"""
        advice = self.wisdom_lookup(user_query)
        return f"Daughter/Son, hear me well. {advice} No go let Lagos show you pepper!"

    async def setup_concert_collab(self, artist_skin: str, track_title: str):
        """Prepare RVC assets for a virtual concert collaboration"""
        print(f"🎤 EMPIRE: Setting up collab with {artist_skin} for '{track_title}'")
        skin_info = self.rvc.get_skin_paths(artist_skin)
        if not skin_info:
            return {"error": "Voice skin not found"}
        return {
            "artist": artist_skin,
            "track": track_title,
            "rvc_config": skin_info
        }

    async def produce_anthology_episode(self, ep_no: int):
        """Director's cut for the Story-World series"""
        return await self.story_engine.generate_episode_script(ep_no)

    async def produce_brand_campaign(self, brand: str, features: List[str]):
        """Commercial production for brands"""
        return await self.brand_service.produce_explainer(brand, features)

# Singleton instance
orchestrator = MediaEmpireOrchestrator()
