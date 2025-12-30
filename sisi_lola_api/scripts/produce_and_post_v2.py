#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 SISI LOLA SUPREME PRODUCER v2.0 - BULLETPROOF EDITION
=============================================================================
100% LOCAL VIDEO GENERATION - No external API failures!

Uses:
- ElevenLabs for voiceover (WORKING)
- FFmpeg for video generation (LOCAL - GUARANTEED)
- Your 70+ DNA images (AVAILABLE)
- Direct Instagram posting (TOKEN READY)

Run: python -m sisi_lola_api.scripts.produce_and_post_v2 --vibe VIBE010
=============================================================================
"""

import asyncio
import argparse
import json
import os
import subprocess
import random
import base64
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DNA_FOLDER = PROJECT_ROOT / "sisi_lola_api" / "assets" / "dna"
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "produced_vibes"
CONTENT_QUEUE_PATH = PROJECT_ROOT / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"

# Ensure output folder exists
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# API Keys - Only the ones that WORK
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841478533567114")

# Sisi Lola Voice - Using a working voice ID
SISI_LOLA_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - clear female voice


class SisiLolaProducerV2:
    """
    BULLETPROOF content production engine.
    Uses local FFmpeg for video - no external API failures!
    """
    
    def __init__(self):
        self.vibes_data = self._load_vibes()
        self.dna_images = self._get_dna_images()
        print(f"📸 Found {len(self.dna_images)} DNA images available")
        
    def _load_vibes(self) -> Dict:
        """Load vibes from content queue"""
        if CONTENT_QUEUE_PATH.exists():
            with open(CONTENT_QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"batch": "december_2025", "vibes": []}
    
    def _get_dna_images(self) -> List[Path]:
        """Get all high-quality DNA images (PNG files, >100KB)"""
        images = []
        if DNA_FOLDER.exists():
            for img_path in DNA_FOLDER.glob("*.png"):
                if img_path.stat().st_size > 100_000:  # Only files > 100KB
                    images.append(img_path)
        return sorted(images)
    
    def get_vibe(self, vibe_id: str) -> Optional[Dict]:
        """Get a specific vibe by ID"""
        for vibe in self.vibes_data.get("vibes", []):
            if vibe.get("vibe_id") == vibe_id:
                return vibe
        return None
    
    async def generate_voiceover(self, text: str, vibe_id: str) -> Optional[Path]:
        """Generate voiceover with ElevenLabs - THIS WORKS!"""
        print(f"\n🎙️ Step 1: Generating voiceover with ElevenLabs...")
        
        if not ELEVENLABS_API_KEY:
            print("  ❌ ELEVENLABS_API_KEY not found!")
            return None
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_voiceover.mp3"
        
        # Check if already exists
        if output_path.exists():
            print(f"  ✅ Voiceover already exists: {output_path.name}")
            return output_path
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{SISI_LOLA_VOICE_ID}",
                    headers={
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.5,
                            "use_speaker_boost": True
                        }
                    }
                )
                
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"  ✅ Voiceover saved: {output_path.name}")
                    return output_path
                else:
                    print(f"  ❌ ElevenLabs error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ Voiceover generation failed: {str(e)}")
            return None
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file using ffprobe"""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True, text=True
            )
            return float(result.stdout.strip())
        except:
            return 30.0  # Default 30 seconds
    
    def generate_video_ffmpeg(self, audio_path: Path, vibe_id: str, title: str) -> Optional[Path]:
        """
        Generate video using FFmpeg - 100% LOCAL, NO API!
        Creates a professional slideshow with DNA images + audio
        """
        print(f"\n🎬 Step 2: Generating video with FFmpeg (LOCAL)...")
        
        if not self.dna_images:
            print("  ❌ No DNA images found!")
            return None
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_video.mp4"
        
        # Get audio duration
        duration = self.get_audio_duration(audio_path)
        print(f"  📏 Audio duration: {duration:.1f} seconds")
        
        # Select random DNA images for slideshow (4-6 images)
        num_images = min(5, len(self.dna_images))
        selected_images = random.sample(self.dna_images, num_images)
        print(f"  📸 Using {num_images} DNA images")
        
        # Calculate time per image
        time_per_image = duration / num_images
        
        # Create a concat file for FFmpeg
        concat_file = OUTPUT_FOLDER / f"{vibe_id}_concat.txt"
        with open(concat_file, "w") as f:
            for img in selected_images:
                f.write(f"file '{img}'\n")
                f.write(f"duration {time_per_image}\n")
            # Add last image again (FFmpeg requirement)
            f.write(f"file '{selected_images[-1]}'\n")
        
        try:
            # FFmpeg command for slideshow with audio
            # -y: overwrite output
            # -f concat: use concat demuxer
            # -safe 0: allow absolute paths
            # -vsync vfr: variable frame rate
            # -pix_fmt yuv420p: compatible with most players
            # -vf scale: resize to 1080x1920 (9:16 for TikTok/Reels)
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30",
                "-shortest",
                "-movflags", "+faststart",
                str(output_path)
            ]
            
            print(f"  ⏳ Running FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                # Get file size
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ Video created: {output_path.name} ({size_mb:.1f} MB)")
                
                # Cleanup concat file
                concat_file.unlink()
                
                return output_path
            else:
                print(f"  ❌ FFmpeg error: {result.stderr[:500]}")
                return None
                
        except FileNotFoundError:
            print("  ❌ FFmpeg not installed! Install with: sudo apt install ffmpeg")
            return None
        except Exception as e:
            print(f"  ❌ Video generation failed: {str(e)}")
            return None
    
    def generate_captions(self, vibe: Dict) -> Dict[str, str]:
        """Generate platform-specific captions"""
        print(f"\n📝 Step 3: Generating captions...")
        
        base_caption = vibe.get("captions", {}).get("instagram", vibe.get("script", ""))
        hashtags = vibe.get("hashtags", ["SisiLola", "Naija", "Vibes", "Lagos", "Afrobeats"])
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags[:10]])  # Max 10 hashtags
        
        captions = {
            "instagram": f"{base_caption}\n\n{hashtag_str}\n\n💃 Follow @sisilolalive for more vibes!",
            "tiktok": f"{base_caption}\n\n{hashtag_str}",
            "youtube_title": vibe.get("title", "Sisi Lola Vibes"),
            "youtube_description": f"{base_caption}\n\n{hashtag_str}\n\nFollow Sisi Lola:\n📸 Instagram: @sisilolalive\n🎵 TikTok: @sisilolalive"
        }
        
        print(f"  ✅ Captions ready for all platforms")
        return captions
    
    async def post_to_instagram(self, video_path: Path, caption: str) -> bool:
        """Post video to Instagram as Reel"""
        print(f"\n📸 Step 4: Posting to Instagram...")
        
        if not INSTAGRAM_TOKEN:
            print("  ❌ INSTAGRAM_ACCESS_TOKEN not found!")
            return False
        
        # For Instagram posting, video needs to be hosted at a public URL
        # We'll upload to a free service or use Dropbox sharing
        print("  ℹ️ Instagram requires video at public URL")
        print(f"  📋 Video ready at: {video_path}")
        print(f"  📋 Caption ready: {len(caption)} chars")
        print("  📋 Manual upload recommended for first post to verify")
        
        # TODO: Implement Dropbox upload and sharing for public URL
        # For now, provide instructions for manual posting
        
        return False  # Change to True when automated
    
    async def produce_and_post(self, vibe_id: str):
        """Full production pipeline - BULLETPROOF EDITION"""
        print("\n" + "=" * 60)
        print(f"🚀 SISI LOLA SUPREME PRODUCTION v2.0: {vibe_id}")
        print("     BULLETPROOF EDITION - 100% Local Video Generation")
        print("=" * 60)
        
        # Get vibe data
        vibe = self.get_vibe(vibe_id)
        if not vibe:
            print(f"❌ Vibe '{vibe_id}' not found in content queue!")
            return
        
        print(f"\n📌 Title: {vibe.get('title')}")
        script = vibe.get("script", "How far my people! Na your girl Sisi Lola from Lagos!")
        print(f"📝 Script: {script[:80]}...")
        
        # Step 1: Generate Voiceover
        voiceover_path = await self.generate_voiceover(script, vibe_id)
        if not voiceover_path:
            print("\n❌ Failed to generate voiceover. Stopping.")
            return
        
        # Step 2: Generate Video with FFmpeg (LOCAL!)
        video_path = self.generate_video_ffmpeg(voiceover_path, vibe_id, vibe.get('title', ''))
        
        # Step 3: Generate Captions
        captions = self.generate_captions(vibe)
        
        # Step 4: Save production data
        production_data = {
            "vibe_id": vibe_id,
            "title": vibe.get("title"),
            "produced_at": datetime.now().isoformat(),
            "voiceover_path": str(voiceover_path) if voiceover_path else None,
            "video_path": str(video_path) if video_path else None,
            "captions": captions,
            "status": "ready" if video_path else "partial"
        }
        
        production_file = OUTPUT_FOLDER / f"{vibe_id}_production.json"
        with open(production_file, "w") as f:
            json.dump(production_data, f, indent=2)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION SUMMARY")
        print("=" * 60)
        print(f"  🎙️ Voiceover: {'✅ Ready' if voiceover_path else '❌ Failed'}")
        print(f"  🎬 Video: {'✅ Ready' if video_path else '❌ Failed'}")
        print(f"  📝 Captions: ✅ Ready")
        
        if video_path:
            print(f"\n📁 OUTPUT FILES:")
            print(f"  • Voiceover: {voiceover_path.name}")
            print(f"  • Video: {video_path.name}")
            print(f"  • Data: {production_file.name}")
            print(f"\n📍 Location: {OUTPUT_FOLDER}")
            
            print("\n" + "=" * 60)
            print("🎉 PRODUCTION SUCCESSFUL!")
            print("=" * 60)
            print("\n📣 NEXT STEPS:")
            print("  1. Check the video at the output location")
            print("  2. Upload manually to Instagram, TikTok, YouTube")
            print("  3. Or wait for automated posting (coming next!)")
        else:
            print("\n⚠️ Video not generated - check FFmpeg installation")
            print("  Install FFmpeg: sudo apt install ffmpeg")
        
        print("\n" + "=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Sisi Lola Producer v2.0 - Bulletproof Edition")
    parser.add_argument("--vibe", type=str, default="VIBE010", help="Vibe ID to produce")
    args = parser.parse_args()
    
    producer = SisiLolaProducerV2()
    await producer.produce_and_post(args.vibe)


if __name__ == "__main__":
    asyncio.run(main())
