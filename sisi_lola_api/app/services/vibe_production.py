"""
SISI LOLA VIBE PRODUCTION SERVICE
==================================
Automated production pipeline for the 10-Vibe New Africa Campaign.
Integrates with ElevenLabs for voice synthesis and content queue for scheduling.
"""

import os
import json
import asyncio
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

# Nigerian Voice IDs from ElevenLabs (pre-identified)
NIGERIAN_VOICES = {
    "lola": "21m00Tcm4TlvDq8ikWAM",  # Primary voice - warm, confident
    "eno": "pNInz6obpgDQGcFmaJgB",   # Soft, gentle alternative
    "bukola": "XrExE9yKIg1WjnnlVkGX", # Clear, educational tone
}


@dataclass
class VibeAsset:
    """A produced vibe ready for posting"""
    vibe_id: str
    title: str
    audio_path: Optional[str] = None
    audio_base64: Optional[str] = None
    script: str = ""
    caption: str = ""
    hashtags: List[str] = None
    platforms: List[str] = None
    scheduled_date: str = ""
    status: str = "pending"
    duration_seconds: float = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class VibeProductionService:
    """
    Production service for Sisi Lola vibes.
    
    Usage:
        service = VibeProductionService()
        
        # Produce a single vibe
        asset = await service.produce_vibe("VIBE001")
        
        # Produce all vibes in batch
        assets = await service.produce_batch()
    """
    
    def __init__(self, 
                 vibes_file: Optional[Path] = None,
                 output_dir: Optional[Path] = None):
        
        # Calculate project root (sisi_lola_api is inside Sisi_Lola)
        project_root = Path(__file__).parent.parent.parent.parent  # services -> app -> sisi_lola_api -> Sisi_Lola
        
        self.vibes_file = vibes_file or project_root / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"
        self.output_dir = output_dir or project_root / "03_MEDIA_ASSETS" / "produced_vibes"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📂 Looking for vibes at: {self.vibes_file}")
        print(f"📂 File exists: {self.vibes_file.exists()}")
        
        self.vibes_data = self._load_vibes()
        self.voice_id = NIGERIAN_VOICES.get("lola", "21m00Tcm4TlvDq8ikWAM")
        
    def _load_vibes(self) -> Dict:
        """Load vibes batch from JSON"""
        if self.vibes_file.exists():
            with open(self.vibes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"vibes": []}
    
    def get_vibe(self, vibe_id: str) -> Optional[Dict]:
        """Get a specific vibe by ID"""
        for vibe in self.vibes_data.get("vibes", []):
            if vibe.get("vibe_id") == vibe_id:
                return vibe
        return None
    
    async def generate_voice(self, 
                            text: str, 
                            voice_id: Optional[str] = None,
                            output_path: Optional[Path] = None) -> Optional[bytes]:
        """
        Generate voice audio using ElevenLabs API.
        
        Args:
            text: Script text to synthesize
            voice_id: ElevenLabs voice ID (defaults to Lola)
            output_path: Optional path to save the audio file
            
        Returns:
            Audio bytes if successful, None otherwise
        """
        if not ELEVENLABS_API_KEY:
            print("⚠️ ELEVENLABS_API_KEY not set, skipping voice generation")
            return None
        
        voice = voice_id or self.voice_id
        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        # Voice settings optimized for Nigerian English
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.6,
                "use_speaker_boost": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    
                    if output_path:
                        with open(output_path, 'wb') as f:
                            f.write(audio_bytes)
                        print(f"✅ Audio saved: {output_path.name}")
                    
                    return audio_bytes
                else:
                    print(f"❌ ElevenLabs Error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Voice generation error: {e}")
            return None
    
    async def produce_vibe(self, vibe_id: str) -> Optional[VibeAsset]:
        """
        Produce a single vibe (generate audio + prepare assets).
        
        Args:
            vibe_id: The vibe ID (e.g., "VIBE001")
            
        Returns:
            VibeAsset with all production data
        """
        vibe = self.get_vibe(vibe_id)
        if not vibe:
            print(f"❌ Vibe {vibe_id} not found")
            return None
        
        print(f"\n🎬 Producing {vibe_id}: {vibe.get('title')}")
        print(f"   Duration: {vibe.get('duration_seconds')}s")
        print(f"   Platforms: {', '.join(vibe.get('platforms', []))}")
        
        # Extract script
        script = vibe.get("voiceover_script", "")
        
        # Generate audio
        audio_filename = f"{vibe_id}_{datetime.now().strftime('%Y%m%d')}.mp3"
        audio_path = self.output_dir / audio_filename
        
        audio_bytes = await self.generate_voice(script, output_path=audio_path)
        
        # Create asset
        asset = VibeAsset(
            vibe_id=vibe_id,
            title=vibe.get("title", ""),
            audio_path=str(audio_path) if audio_bytes else None,
            script=script,
            caption=vibe.get("caption", ""),
            hashtags=vibe.get("hashtags", []),
            platforms=vibe.get("platforms", []),
            scheduled_date=vibe.get("scheduled_date", ""),
            status="produced" if audio_bytes else "script_only",
            duration_seconds=vibe.get("duration_seconds", 0)
        )
        
        # Save asset metadata
        metadata_path = self.output_dir / f"{vibe_id}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(asset.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Produced: {asset.status}")
        return asset
    
    async def produce_batch(self, 
                           vibe_ids: Optional[List[str]] = None,
                           max_concurrent: int = 3) -> List[VibeAsset]:
        """
        Produce multiple vibes in batch.
        
        Args:
            vibe_ids: List of vibe IDs to produce (None = all)
            max_concurrent: Max concurrent API calls
            
        Returns:
            List of produced VibeAssets
        """
        if vibe_ids is None:
            vibe_ids = [v["vibe_id"] for v in self.vibes_data.get("vibes", [])]
        
        print(f"\n{'='*60}")
        print(f"🚀 SISI LOLA VIBE BATCH PRODUCTION")
        print(f"   Vibes to produce: {len(vibe_ids)}")
        print(f"{'='*60}")
        
        assets = []
        
        # Process in batches to respect rate limits
        for i in range(0, len(vibe_ids), max_concurrent):
            batch = vibe_ids[i:i + max_concurrent]
            tasks = [self.produce_vibe(vid) for vid in batch]
            results = await asyncio.gather(*tasks)
            assets.extend([a for a in results if a])
            
            # Small delay between batches
            if i + max_concurrent < len(vibe_ids):
                await asyncio.sleep(2)
        
        # Save batch summary
        summary = {
            "produced_at": datetime.now().isoformat(),
            "total_vibes": len(vibe_ids),
            "successful": len([a for a in assets if a.status == "produced"]),
            "script_only": len([a for a in assets if a.status == "script_only"]),
            "assets": [a.to_dict() for a in assets]
        }
        
        summary_path = self.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"✅ BATCH COMPLETE")
        print(f"   Produced: {summary['successful']}/{summary['total_vibes']}")
        print(f"   Script only: {summary['script_only']}")
        print(f"   Summary: {summary_path.name}")
        print(f"{'='*60}")
        
        return assets
    
    def get_deployment_calendar(self) -> Dict:
        """Get the deployment calendar from vibes data"""
        return self.vibes_data.get("deployment_calendar", {})
    
    def get_next_scheduled_vibe(self) -> Optional[Dict]:
        """Get the next vibe scheduled for posting"""
        now = datetime.now()
        calendar = self.get_deployment_calendar()
        
        upcoming = []
        for week, dates in calendar.items():
            for date_str, vibe_info in dates.items():
                scheduled = datetime.fromisoformat(vibe_info.get("time_wat", date_str + "T00:00:00"))
                if scheduled > now:
                    vibe = self.get_vibe(vibe_info["vibe_id"])
                    if vibe:
                        upcoming.append({
                            "scheduled": scheduled,
                            "vibe": vibe,
                            "platform": vibe_info.get("primary_platform")
                        })
        
        if upcoming:
            upcoming.sort(key=lambda x: x["scheduled"])
            return upcoming[0]
        return None


# API Integration for existing services
async def produce_vibe_for_api(vibe_id: str) -> Dict[str, Any]:
    """
    API-friendly function to produce a single vibe.
    Can be called from FastAPI endpoints.
    """
    service = VibeProductionService()
    asset = await service.produce_vibe(vibe_id)
    
    if asset:
        return {
            "success": True,
            "vibe_id": asset.vibe_id,
            "title": asset.title,
            "status": asset.status,
            "audio_path": asset.audio_path,
            "script": asset.script,
            "caption": asset.caption,
            "hashtags": asset.hashtags
        }
    return {"success": False, "error": f"Failed to produce vibe {vibe_id}"}


async def produce_all_vibes() -> Dict[str, Any]:
    """Produce all vibes in batch"""
    service = VibeProductionService()
    assets = await service.produce_batch()
    
    return {
        "success": True,
        "total": len(assets),
        "produced": len([a for a in assets if a.status == "produced"]),
        "vibes": [a.vibe_id for a in assets]
    }


def main():
    """Demo: Produce sample vibes"""
    import asyncio
    
    print("="*60)
    print("SISI LOLA VIBE PRODUCTION SERVICE - DEMO")
    print("="*60)
    
    service = VibeProductionService()
    
    # Show loaded vibes
    vibes = service.vibes_data.get("vibes", [])
    print(f"\n📋 Loaded {len(vibes)} vibes:")
    for v in vibes:
        print(f"   {v['vibe_id']}: {v['title']} ({v['duration_seconds']}s)")
    
    # Get next scheduled
    next_vibe = service.get_next_scheduled_vibe()
    if next_vibe:
        print(f"\n⏰ Next scheduled: {next_vibe['vibe']['title']}")
        print(f"   Platform: {next_vibe['platform']}")
        print(f"   Date: {next_vibe['scheduled']}")
    
    # Produce first vibe as demo (if API key available)
    if ELEVENLABS_API_KEY:
        print("\n🎬 Producing VIBE001 as demo...")
        asset = asyncio.run(service.produce_vibe("VIBE001"))
        if asset:
            print(f"   Result: {asset.status}")
            if asset.audio_path:
                print(f"   Audio: {asset.audio_path}")
    else:
        print("\n⚠️ Set ELEVENLABS_API_KEY to enable voice production")
        print("   Scripts are still available for manual production")


if __name__ == "__main__":
    main()
