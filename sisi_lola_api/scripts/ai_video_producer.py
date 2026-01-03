#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 SISI LOLA AI VIDEO PRODUCER v3.0 - REPLICATE EDITION
=============================================================================
REAL AI-Generated Videos - Makes Sisi Lola MOVE and TALK!

Stack:
1. Replicate API → Stable Video Diffusion (image-to-video)
2. Replicate API → SadTalker (lip sync)
3. ElevenLabs → Voice generation
4. FFmpeg → Final processing

Requirements:
- REPLICATE_API_TOKEN (sign up at replicate.com - ~$0.10 per video)
- ELEVENLABS_API_KEY (already configured)

Run: python -m sisi_lola_api.scripts.ai_video_producer --vibe VIBE010
=============================================================================
"""

import asyncio
import argparse
import json
import os
import subprocess
import random
import httpx
import time
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
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "ai_videos"
CONTENT_QUEUE_PATH = PROJECT_ROOT / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"

# Ensure output folder exists
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# API Keys
# HARDCODED to bypass .env loading issues
REPLICATE_API_TOKEN = "r8_V7hyzBNwBGzhQax9O43wpb3CqInl5g22WaIhE"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

# Sisi Lola Voice
SISI_LOLA_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Best DNA images for video (manually curated)
PREFERRED_DNA_IMAGES = [
    "Sisi Lola Live Show Hostess.png",
    "sisi lola 1.png",
    "sisi lola 2.png",
    "sisi lola 3.png",
    "sisi_lola_4.png",
]


class AIVideoProducer:
    """
    TRUE AI Video Producer using Replicate models.
    Generates REAL moving, talking videos of Sisi Lola!
    """
    
    def __init__(self):
        self.vibes_data = self._load_vibes()
        self.dna_images = self._get_best_dna_images()
        print(f"📸 Found {len(self.dna_images)} high-quality DNA images")
        
    def _load_vibes(self) -> Dict:
        if CONTENT_QUEUE_PATH.exists():
            with open(CONTENT_QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"batch": "december_2025", "vibes": []}
    
    def _get_best_dna_images(self) -> List[Path]:
        """Get best DNA images for video generation"""
        images = []
        if DNA_FOLDER.exists():
            # First try preferred images
            for name in PREFERRED_DNA_IMAGES:
                path = DNA_FOLDER / name
                if path.exists():
                    images.append(path)
            
            # If not enough, get other large PNG files
            if len(images) < 3:
                for img_path in DNA_FOLDER.glob("*.png"):
                    if img_path.stat().st_size > 500_000 and img_path not in images:
                        images.append(img_path)
                        if len(images) >= 5:
                            break
        
        return images
    
    def get_vibe(self, vibe_id: str) -> Optional[Dict]:
        for vibe in self.vibes_data.get("vibes", []):
            if vibe.get("vibe_id") == vibe_id:
                return vibe
        return None
    
    async def generate_voiceover(self, text: str, vibe_id: str) -> Optional[Path]:
        """Generate voiceover with ElevenLabs"""
        print(f"\n🎙️ Step 1: Generating voiceover...")
        
        if not ELEVENLABS_API_KEY:
            print("  ❌ ELEVENLABS_API_KEY not found!")
            return None
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_voice.mp3"
        
        if output_path.exists():
            print(f"  ✅ Voice already exists: {output_path.name}")
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
                    print(f"  ✅ Voice saved: {output_path.name}")
                    return output_path
                else:
                    print(f"  ❌ ElevenLabs error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ Voice generation failed: {str(e)}")
            return None
    
    async def image_to_video_replicate(self, image_path: Path, vibe_id: str) -> Optional[Path]:
        """
        Convert DNA image to moving video using Replicate's Stable Video Diffusion.
        This makes Sisi Lola MOVE!
        """
        print(f"\n🎬 Step 2: Generating AI video (Image → Motion)...")
        
        if not REPLICATE_API_TOKEN:
            print("  ❌ REPLICATE_API_TOKEN not found!")
            print("  📝 Sign up at replicate.com and add token to .env")
            return None
        
        print(f"  📸 Source image: {image_path.name}")
        
        try:
            import base64
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            image_uri = f"data:image/png;base64,{image_data}"
            
            async with httpx.AsyncClient(timeout=300) as client:
                # Start prediction
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",  # Stable Video Diffusion
                        "input": {
                            "input_image": image_uri,
                            "video_length": "14_frames_with_svd",
                            "sizing_strategy": "maintain_aspect_ratio",
                            "frames_per_second": 6,
                            "motion_bucket_id": 127,
                            "cond_aug": 0.02
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    prediction = response.json()
                    prediction_id = prediction.get("id")
                    print(f"  ⏳ AI generation started: {prediction_id}")
                    
                    # Poll for completion
                    video_url = await self._poll_replicate(client, prediction_id)
                    
                    if video_url:
                        # Download the video
                        output_path = OUTPUT_FOLDER / f"{vibe_id}_motion.mp4"
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        
                        size_mb = output_path.stat().st_size / (1024 * 1024)
                        print(f"  ✅ Motion video created: {output_path.name} ({size_mb:.1f} MB)")
                        return output_path
                else:
                    print(f"  ❌ Replicate error: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ AI video generation failed: {str(e)}")
            return None
    
    async def _poll_replicate(self, client: httpx.AsyncClient, prediction_id: str, max_wait: int = 300) -> Optional[str]:
        """Poll Replicate API for prediction completion"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status == "succeeded":
                        output = data.get("output")
                        if isinstance(output, list) and output:
                            return output[0]
                        return output
                    elif status == "failed":
                        print(f"  ❌ Prediction failed: {data.get('error')}")
                        return None
                    else:
                        print(f"  ⏳ Status: {status}...")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                print(f"  ⚠️ Poll error: {e}")
                await asyncio.sleep(3)
        
        print("  ❌ Prediction timed out")
        return None
    
    async def add_lip_sync_sadtalker(self, video_path: Path, audio_path: Path, vibe_id: str) -> Optional[Path]:
        """
        Add lip sync using SadTalker via Replicate.
        Makes Sisi Lola TALK!
        """
        print(f"\n🗣️ Step 3: Adding lip sync (SadTalker)...")
        
        if not REPLICATE_API_TOKEN:
            print("  ⏭️ Skipping lip sync - no Replicate token")
            return video_path
        
        # For lip sync, we need the source image, not video
        # SadTalker takes image + audio → talking video
        
        source_image = self.dna_images[0] if self.dna_images else None
        if not source_image:
            print("  ⏭️ No source image for lip sync")
            return video_path
        
        try:
            import base64
            
            # Encode image
            with open(source_image, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Encode audio
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "cde35f3c91e8f5da8a959e7c7f3b44e6426cf8ae814d1f1b08e2309e2acee0e1",  # SadTalker
                        "input": {
                            "source_image": f"data:image/png;base64,{image_data}",
                            "driven_audio": f"data:audio/mp3;base64,{audio_data}",
                            "still": False,
                            "preprocess": "crop",
                            "expression_scale": 1.0
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    prediction = response.json()
                    prediction_id = prediction.get("id")
                    print(f"  ⏳ Lip sync started: {prediction_id}")
                    
                    video_url = await self._poll_replicate(client, prediction_id)
                    
                    if video_url:
                        output_path = OUTPUT_FOLDER / f"{vibe_id}_talking.mp4"
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        
                        size_mb = output_path.stat().st_size / (1024 * 1024)
                        print(f"  ✅ Talking video created: {output_path.name} ({size_mb:.1f} MB)")
                        return output_path
                else:
                    print(f"  ⚠️ SadTalker error: {response.status_code}")
                    return video_path
                    
        except Exception as e:
            print(f"  ⚠️ Lip sync failed: {str(e)}")
            return video_path
    
    def combine_video_audio_ffmpeg(self, video_path: Path, audio_path: Path, vibe_id: str) -> Optional[Path]:
        """Combine video with audio using FFmpeg"""
        print(f"\n🎬 Step 4: Combining video + audio (FFmpeg)...")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_final.mp4"
        
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ Final video: {output_path.name} ({size_mb:.1f} MB)")
                return output_path
            else:
                print(f"  ⚠️ FFmpeg combine failed")
                return video_path
                
        except Exception as e:
            print(f"  ⚠️ Combine failed: {str(e)}")
            return video_path
    
    def generate_captions(self, vibe: Dict) -> Dict[str, str]:
        """Generate platform-specific captions"""
        print(f"\n📝 Step 5: Generating captions...")
        
        base_caption = vibe.get("script", "")
        hashtags = vibe.get("hashtags", ["SisiLola", "Naija", "AI", "AfroAI"])
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags[:10]])
        
        captions = {
            "instagram": f"{base_caption}\n\n{hashtag_str}\n\n💃 @sisilolalive",
            "tiktok": f"{base_caption}\n\n{hashtag_str}",
            "youtube_title": vibe.get("title", "Sisi Lola AI"),
        }
        
        print(f"  ✅ Captions ready")
        return captions
    
    async def produce(self, vibe_id: str):
        """Full AI video production pipeline"""
        print("\n" + "=" * 60)
        print(f"🚀 SISI LOLA AI VIDEO PRODUCER v3.0: {vibe_id}")
        print("     REPLICATE EDITION - Real AI-Generated Videos")
        print("=" * 60)
        
        # Check requirements
        if not REPLICATE_API_TOKEN:
            print("\n⚠️ REPLICATE_API_TOKEN not configured!")
            print("=" * 60)
            print("📝 TO GET STARTED:")
            print("1. Go to https://replicate.com")
            print("2. Sign up (free account)")
            print("3. Go to Account Settings → API Tokens")
            print("4. Create a token")
            print("5. Add to your .env file:")
            print("   REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxx")
            print("=" * 60)
            print("\n💰 COST: ~$0.10-0.20 per video")
            print("   Well worth it for REAL AI videos!")
            return
        
        # Get vibe data
        vibe = self.get_vibe(vibe_id)
        if not vibe:
            print(f"❌ Vibe '{vibe_id}' not found!")
            return
        
        print(f"\n📌 Title: {vibe.get('title')}")
        script = vibe.get("script", "How far my people! Na Sisi Lola!")
        print(f"📝 Script: {script[:60]}...")
        
        # Step 1: Generate Voice
        voice_path = await self.generate_voiceover(script, vibe_id)
        if not voice_path:
            return
        
        # Step 2: Image to Video (Stable Video Diffusion)
        source_image = self.dna_images[0] if self.dna_images else None
        if not source_image:
            print("❌ No DNA images found!")
            return
        
        motion_video = await self.image_to_video_replicate(source_image, vibe_id)
        
        # Step 3: Add Lip Sync (SadTalker)
        if motion_video:
            talking_video = await self.add_lip_sync_sadtalker(motion_video, voice_path, vibe_id)
        else:
            # Fallback: Direct lip sync on image
            talking_video = await self.add_lip_sync_sadtalker(source_image, voice_path, vibe_id)
        
        # Step 4: Combine if needed
        final_video = talking_video
        if talking_video and not str(talking_video).endswith("_talking.mp4"):
            final_video = self.combine_video_audio_ffmpeg(talking_video, voice_path, vibe_id)
        
        # Step 5: Captions
        captions = self.generate_captions(vibe)
        
        # Save production data
        production_data = {
            "vibe_id": vibe_id,
            "produced_at": datetime.now().isoformat(),
            "voice_path": str(voice_path),
            "video_path": str(final_video) if final_video else None,
            "captions": captions,
            "status": "success" if final_video else "partial",
            "method": "replicate-ai"
        }
        
        with open(OUTPUT_FOLDER / f"{vibe_id}_production.json", "w") as f:
            json.dump(production_data, f, indent=2)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION SUMMARY")
        print("=" * 60)
        print(f"  🎙️ Voice: ✅ {voice_path.name}")
        print(f"  🎬 Video: {'✅ ' + final_video.name if final_video else '❌ Failed'}")
        print(f"  📝 Captions: ✅ Ready")
        
        if final_video:
            print(f"\n📍 Output: {OUTPUT_FOLDER}")
            print("\n🎉 AI VIDEO PRODUCTION SUCCESSFUL!")
        
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Sisi Lola AI Video Producer v3.0")
    parser.add_argument("--vibe", type=str, default="VIBE010", help="Vibe ID to produce")
    args = parser.parse_args()
    
    producer = AIVideoProducer()
    await producer.produce(args.vibe)


if __name__ == "__main__":
    asyncio.run(main())
