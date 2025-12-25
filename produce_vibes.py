#!/usr/bin/env python3
"""
QUICK RUN: Produce Sisi Lola Vibes
===================================
Run this script to produce all 10 vibes with voice audio.

Usage:
    python produce_vibes.py           # Produce all vibes
    python produce_vibes.py VIBE001   # Produce specific vibe
    python produce_vibes.py --list    # List all vibes

Requires: ELEVENLABS_API_KEY in .env
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Also try adding sisi_lola_api to path
sys.path.insert(0, str(project_root / "sisi_lola_api"))

from sisi_lola_api.app.services.vibe_production import VibeProductionService


async def main():
    # Explicitly set paths from project root
    vibes_file = project_root / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"
    output_dir = project_root / "03_MEDIA_ASSETS" / "produced_vibes"
    
    print(f"📂 Vibes file: {vibes_file}")
    print(f"📂 Exists: {vibes_file.exists()}")
    
    service = VibeProductionService(vibes_file=vibes_file, output_dir=output_dir)
    
    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--list":
            print("\n📋 SISI LOLA VIBES - New Africa Campaign\n" + "="*50)
            vibes = service.vibes_data.get("vibes", [])
            for v in vibes:
                print(f"   {v['vibe_id']}: {v['title']}")
                print(f"      ⏱️ {v['duration_seconds']}s | 🎯 {v.get('viral_potential', 'N/A')}")
                print(f"      📱 {', '.join(v['platforms'][:2])}")
                print()
            return
        
        elif arg.startswith("VIBE"):
            # Produce specific vibe
            print(f"\n🎬 Producing {arg}...")
            asset = await service.produce_vibe(arg)
            if asset:
                print(f"\n✅ Complete!")
                print(f"   Status: {asset.status}")
                if asset.audio_path:
                    print(f"   Audio: {asset.audio_path}")
                print(f"\n📝 Script:\n{asset.script[:200]}...")
            return
    
    # Default: produce all
    print("\n🚀 PRODUCING ALL 10 VIBES...")
    assets = await service.produce_batch()
    
    print(f"\n✅ BATCH COMPLETE!")
    print(f"   Produced: {len([a for a in assets if a.status == 'produced'])}")
    print(f"   Check: 03_MEDIA_ASSETS/produced_vibes/")


if __name__ == "__main__":
    asyncio.run(main())
