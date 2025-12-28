"""
SISI LOLA SUPREME VIBE SCHEDULER
=================================
The autonomous loop that:
1. Hunts for hot gists.
2. Selects the most 'engaging' topic using Gemini 3.
3. Automatically generates Supreme Media (Veo, Lyria, Imagen).
4. Populates the Content Queue for human approval.
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from sisi_lola_api.app.database import SessionLocal, ContentQueue, User
from sisi_lola_api.app.services.gist_hunter import GistHunter
from sisi_lola_api.app.services.google_creative_service import get_google_creative_service
from sisi_lola_api.app.services.unified_inference import get_inference_service
from sisi_lola_api.app.config import SisiLolaDNA

class VibeScheduler:
    def __init__(self):
        self.hunter = GistHunter()
        self.creative = get_google_creative_service()
        self.inference = get_inference_service()
        self.dna = SisiLolaDNA()

    async def run_autonomous_loop(self, scope: str = "nigeria"):
        """Perform a full autonomous content generation pass"""
        print(f"🚀 [VIBE LOOP] Starting autonomous pass for {scope.upper()}...")
        
        # 1. Sync Radar
        briefing = await self.hunter.sync_radar_v2(scope)
        
        # 2. Select Hot Topic & Write Script
        selection_prompt = (
            f"Based on this briefing:\n{briefing}\n\n"
            "Pick the single most RELEVANT and JUICY topic for Sisi Lola to talk about."
            "Write a short, high-energy 30-second script in Sisi's voice (Yorunglish/Pidgin)."
            "Also provide a visual prompt for a video and an image."
            "Respond ONLY in JSON format: "
            '{"topic": "...", "script": "...", "video_prompt": "...", "image_prompt": "...", "target_platform": "instagram"}'
        )
        
        raw_selection = await self.inference._generate_with_gemini(
            selection_prompt, 
            system_prompt=f"You are the Creative Director for {self.dna.NAME}. Use Gemini 3 reasoning."
        )
        
        try:
            # Clean JSON if wrapped in markdown
            if "```json" in raw_selection:
                raw_selection = raw_selection.split("```json")[1].split("```")[0].strip()
            
            content_plan = json.loads(raw_selection)
        except Exception as e:
            print(f"❌ [VIBE LOOP] Failed to parse content plan: {e}")
            return

        print(f"💎 [VIBE LOOP] Content Plan Created: {content_plan['topic']}")

        # 3. Generate Supreme Media in Parallel
        print("🎨 [VIBE LOOP] Triggering Supreme Media Generation...")
        
        video_task = self.creative.generate_vibe_video(content_plan['video_prompt'])
        image_task = self.creative.generate_supreme_snapshot(content_plan['image_prompt'])
        music_task = self.creative.generate_vibe_music(f"Afrobeats for {content_plan['topic']}")
        
        video_res, image_res, music_res = await asyncio.gather(video_task, image_task, music_task)

        # 4. Save to Content Queue
        db = SessionLocal()
        try:
            # Find system user or first admin
            admin = db.query(User).first()
            
            metadata = {
                "autonomous": True,
                "scope": scope,
                "video_model": video_res.get("model") if video_res["success"] else "FAILED",
                "image_model": image_res.get("model") if image_res["success"] else "FAILED",
                "has_audio": music_res["success"],
                "video_asset": video_res.get("video_base64")[:100] + "..." if video_res["success"] else None,
                "image_asset": image_res.get("image_base64")[:100] + "..." if image_res["success"] else None,
            }

            queue_item = ContentQueue(
                title=f"Autonomous: {content_plan['topic']}",
                script=content_plan['script'],
                platform=content_plan.get('target_platform', 'instagram'),
                status="pending_approval",
                created_by=admin.id if admin else None,
                metadata_=metadata
            )
            
            db.add(queue_item)
            db.commit()
            print(f"✅ [VIBE LOOP] Content queued for approval! Item ID: {queue_item.id}")
        except Exception as e:
            print(f"❌ [VIBE LOOP] Database error: {e}")
            db.rollback()
        finally:
            db.close()

# Singleton
vibe_scheduler = VibeScheduler()

async def main():
    # Test run
    await vibe_scheduler.run_autonomous_loop("nigeria")

if __name__ == "__main__":
    asyncio.run(main())
