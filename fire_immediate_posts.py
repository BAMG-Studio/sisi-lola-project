"""
SISI LOLA IMMEDIATE POSTING SCRIPT
====================================
This script triggers the immediate posting of VIBE001 through VIBE010 
across all configured platforms, bypassing the schedule.
"""

import asyncio
import os
from pathlib import Path
from sisi_lola_api.app.services.automated_posting import AutomatedPostingService, post_now

async def fire_all_vibes():
    service = AutomatedPostingService()
    vibes = ["VIBE001", "VIBE002", "VIBE003", "VIBE004", "VIBE005", 
             "VIBE006", "VIBE007", "VIBE008", "VIBE009", "VIBE010"]
    
    print("\n🚀 SISI LOLA: FIRING ALL VIBES IMMEDIATELY!")
    print("="*60)
    
    for vibe_id in vibes:
        vibe = service.get_vibe(vibe_id)
        if not vibe:
            print(f"⚠️ Vibe {vibe_id} not found, skipping...")
            continue
            
        platforms = vibe.get("platforms", [])
        for platform in platforms:
            print(f"📤 Posting {vibe_id} to {platform}...")
            # Using the production service to post
            # Note: In a real environment, this actually hits the APIs
            result = await service.post_vibe(vibe_id, platform)
            if result.success:
                print(f"   ✅ Success!")
            else:
                print(f"   ❌ Failed: {result.error}")
                
    print("\n" + "="*60)
    print("✅ ALL VIBES PROCESSED!")

if __name__ == "__main__":
    asyncio.run(fire_all_vibes())
