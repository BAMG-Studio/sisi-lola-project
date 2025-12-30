#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 SISI LOLA SUPREME CONTENT PRODUCER
=============================================================================
Full content production pipeline:
1. Generate voiceover with ElevenLabs
2. Create talking head video with HeyGen/D-ID
3. Generate platform-specific captions
4. Post to ALL platforms (Instagram, YouTube, TikTok)

Run: python -m sisi_lola_api.scripts.produce_and_post --vibe VIBE010
=============================================================================
"""

import asyncio
import argparse
import json
import os
import base64
import httpx
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DNA_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "dna"
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "produced_vibes"
CONTENT_QUEUE_PATH = PROJECT_ROOT / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"

# Ensure output folder exists
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# API Keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID", "046a63da7b20403c8c6bb51dbda12f65")
DID_API_KEY = os.getenv("DID_API_KEY")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Sisi Lola Voice Configuration
SISI_LOLA_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice (Rachel)
# TODO: Replace with custom Sisi Lola cloned voice when available


class SisiLolaProducer:
    """Supreme content production engine"""
    
    def __init__(self):
        self.vibes_data = self._load_vibes()
        self.production_log = []
        
    def _load_vibes(self) -> Dict:
        """Load vibes from content queue"""
        if CONTENT_QUEUE_PATH.exists():
            with open(CONTENT_QUEUE_PATH, "r") as f:
                return json.load(f)
        return {"batch": "december_2025", "vibes": []}
    
    def get_vibe(self, vibe_id: str) -> Optional[Dict]:
        """Get a specific vibe by ID"""
        for vibe in self.vibes_data.get("vibes", []):
            if vibe.get("vibe_id") == vibe_id:
                return vibe
        return None
    
    async def generate_voiceover(self, text: str, vibe_id: str) -> Optional[Path]:
        """Generate voiceover with ElevenLabs"""
        print(f"\n🎙️ Generating voiceover with ElevenLabs...")
        
        if not ELEVENLABS_API_KEY:
            print("  ❌ ELEVENLABS_API_KEY not found!")
            return None
        
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
                    output_path = OUTPUT_FOLDER / f"{vibe_id}_voiceover.mp3"
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"  ✅ Voiceover saved: {output_path}")
                    return output_path
                else:
                    print(f"  ❌ ElevenLabs error: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ Voiceover generation failed: {str(e)}")
            return None
    
    async def generate_talking_video_heygen(self, script: str, vibe_id: str) -> Optional[str]:
        """Generate talking head video with HeyGen"""
        print(f"\n🎬 Generating video with HeyGen...")
        
        if not HEYGEN_API_KEY:
            print("  ❌ HEYGEN_API_KEY not found!")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                # Create video generation request
                response = await client.post(
                    "https://api.heygen.com/v2/video/generate",
                    headers={
                        "X-Api-Key": HEYGEN_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "video_inputs": [{
                            "character": {
                                "type": "avatar",
                                "avatar_id": HEYGEN_AVATAR_ID,
                                "avatar_style": "normal"
                            },
                            "voice": {
                                "type": "text",
                                "input_text": script,
                                "voice_id": "en-NG-EzinneNeural"  # Nigerian English voice
                            },
                            "background": {
                                "type": "color",
                                "value": "#1a1a2e"  # Dark purple background
                            }
                        }],
                        "dimension": {
                            "width": 1080,
                            "height": 1920  # 9:16 for TikTok/Reels
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    video_id = data.get("data", {}).get("video_id")
                    print(f"  ⏳ Video generation started: {video_id}")
                    
                    # Poll for completion
                    video_url = await self._poll_heygen_status(client, video_id)
                    if video_url:
                        print(f"  ✅ Video ready: {video_url}")
                        return video_url
                else:
                    print(f"  ❌ HeyGen error: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ Video generation failed: {str(e)}")
            return None
    
    async def _poll_heygen_status(self, client: httpx.AsyncClient, video_id: str, max_wait: int = 300) -> Optional[str]:
        """Poll HeyGen for video completion"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = await client.get(
                    f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                    headers={"X-Api-Key": HEYGEN_API_KEY}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("data", {}).get("status")
                    
                    if status == "completed":
                        return data.get("data", {}).get("video_url")
                    elif status == "failed":
                        print(f"  ❌ Video generation failed")
                        return None
                    else:
                        print(f"  ⏳ Status: {status}...")
                        await asyncio.sleep(10)
                        
            except Exception as e:
                print(f"  ⚠️ Poll error: {e}")
                await asyncio.sleep(5)
        
        print("  ❌ Video generation timed out")
        return None
    
    async def generate_talking_video_did(self, script: str, vibe_id: str) -> Optional[str]:
        """Generate talking head video with D-ID as fallback"""
        print(f"\n🎬 Generating video with D-ID (fallback)...")
        
        if not DID_API_KEY:
            print("  ❌ DID_API_KEY not found!")
            return None
        
        # Get DNA image
        dna_image_path = DNA_FOLDER / "sisi_lola_official_dna_v1.png"
        
        # If no local DNA image, use a placeholder URL
        source_url = "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg"
        
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    "https://api.d-id.com/talks",
                    auth=(DID_API_KEY.split(":")[0], DID_API_KEY.split(":")[1] if ":" in DID_API_KEY else ""),
                    json={
                        "script": {
                            "type": "text",
                            "input": script,
                            "provider": {
                                "type": "microsoft",
                                "voice_id": "en-NG-EzinneNeural"
                            }
                        },
                        "source_url": source_url,
                        "config": {
                            "fluent": True,
                            "pad_audio": 0
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    talk_id = data.get("id")
                    print(f"  ⏳ D-ID video started: {talk_id}")
                    
                    # Poll for completion
                    video_url = await self._poll_did_status(client, talk_id)
                    if video_url:
                        print(f"  ✅ Video ready: {video_url}")
                        return video_url
                else:
                    print(f"  ❌ D-ID error: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ D-ID generation failed: {str(e)}")
            return None
    
    async def _poll_did_status(self, client: httpx.AsyncClient, talk_id: str, max_wait: int = 120) -> Optional[str]:
        """Poll D-ID for video completion"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = await client.get(
                    f"https://api.d-id.com/talks/{talk_id}",
                    auth=(DID_API_KEY.split(":")[0], DID_API_KEY.split(":")[1] if ":" in DID_API_KEY else "")
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status == "done":
                        return data.get("result_url")
                    elif status == "error":
                        print(f"  ❌ D-ID error: {data.get('error', {}).get('description')}")
                        return None
                    else:
                        print(f"  ⏳ D-ID status: {status}...")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                print(f"  ⚠️ Poll error: {e}")
                await asyncio.sleep(3)
        
        print("  ❌ D-ID timed out")
        return None
    
    def generate_captions(self, vibe: Dict) -> Dict[str, str]:
        """Generate platform-specific captions"""
        print(f"\n📝 Generating captions for all platforms...")
        
        base_caption = vibe.get("captions", {}).get("instagram", vibe.get("script", ""))
        hashtags = vibe.get("hashtags", ["SisiLola", "Naija", "Vibes"])
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        
        captions = {
            "instagram": f"{base_caption}\n\n{hashtag_str}\n\n💃 Follow @sisilolalive for more vibes!",
            "tiktok": f"{base_caption}\n\n{hashtag_str}",
            "youtube": f"{vibe.get('title', 'Sisi Lola')}\n\n{base_caption}\n\n{hashtag_str}\n\n🔔 Subscribe for more!",
            "youtube_title": vibe.get("title", "Sisi Lola Vibes"),
            "youtube_description": f"{base_caption}\n\n{hashtag_str}\n\nFollow Sisi Lola:\n📸 Instagram: @sisilolalive\n🎵 TikTok: @sisilolalive\n🌐 Website: https://sisilola.io"
        }
        
        for platform, caption in captions.items():
            print(f"  ✅ {platform}: {len(caption)} chars")
        
        return captions
    
    async def post_to_instagram(self, video_url: str, caption: str) -> bool:
        """Post Reel to Instagram"""
        print(f"\n📸 Posting to Instagram...")
        
        if not INSTAGRAM_TOKEN:
            print("  ❌ INSTAGRAM_ACCESS_TOKEN not found!")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                # Step 1: Create media container
                ig_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841478533567114")
                
                container_response = await client.post(
                    f"https://graph.facebook.com/v18.0/{ig_account_id}/media",
                    params={
                        "access_token": INSTAGRAM_TOKEN,
                        "media_type": "REELS",
                        "video_url": video_url,
                        "caption": caption,
                        "share_to_feed": True
                    }
                )
                
                if container_response.status_code == 200:
                    container_id = container_response.json().get("id")
                    print(f"  ⏳ Container created: {container_id}")
                    
                    # Wait for processing
                    await asyncio.sleep(30)
                    
                    # Step 2: Publish
                    publish_response = await client.post(
                        f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish",
                        params={
                            "access_token": INSTAGRAM_TOKEN,
                            "creation_id": container_id
                        }
                    )
                    
                    if publish_response.status_code == 200:
                        post_id = publish_response.json().get("id")
                        print(f"  ✅ Instagram posted! ID: {post_id}")
                        return True
                    else:
                        print(f"  ❌ Publish failed: {publish_response.text[:200]}")
                        return False
                else:
                    print(f"  ❌ Container failed: {container_response.text[:200]}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Instagram posting failed: {str(e)}")
            return False
    
    async def post_to_tiktok(self, video_url: str, caption: str) -> bool:
        """Post to TikTok - requires OAuth token"""
        print(f"\n🎵 Posting to TikTok...")
        
        tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        if not tiktok_token or tiktok_token == "PLACEHOLDER_UPDATE_AFTER_OAUTH":
            print("  ⏭️ TikTok skipped - OAuth token not configured")
            return False
        
        # TikTok posting requires video upload, not URL
        print("  ℹ️ TikTok requires video file upload - manual posting recommended for now")
        return False
    
    async def post_to_youtube(self, video_url: str, title: str, description: str) -> bool:
        """Post Short to YouTube"""
        print(f"\n📺 Posting to YouTube...")
        
        # YouTube requires OAuth with upload scope
        # For now, log the content for manual upload
        print("  ℹ️ YouTube Shorts requires OAuth flow for uploads")
        print(f"  📋 Ready for manual upload:")
        print(f"     Title: {title}")
        print(f"     Video: {video_url}")
        return False
    
    async def produce_and_post(self, vibe_id: str):
        """Full production pipeline for a vibe"""
        print("\n" + "=" * 60)
        print(f"🚀 SISI LOLA SUPREME PRODUCTION: {vibe_id}")
        print("=" * 60)
        
        # Get vibe data
        vibe = self.get_vibe(vibe_id)
        if not vibe:
            print(f"❌ Vibe '{vibe_id}' not found in content queue!")
            return
        
        print(f"📌 Title: {vibe.get('title')}")
        print(f"📝 Script: {vibe.get('script', '')[:100]}...")
        
        script = vibe.get("script", "How far my people! Na your girl Sisi Lola from Lagos!")
        
        # Step 1: Generate Voiceover
        voiceover_path = await self.generate_voiceover(script, vibe_id)
        
        # Step 2: Generate Video (try HeyGen first, then D-ID)
        video_url = await self.generate_talking_video_heygen(script, vibe_id)
        if not video_url:
            video_url = await self.generate_talking_video_did(script, vibe_id)
        
        # Step 3: Generate Captions
        captions = self.generate_captions(vibe)
        
        # Save production data
        production_data = {
            "vibe_id": vibe_id,
            "produced_at": datetime.now().isoformat(),
            "voiceover_path": str(voiceover_path) if voiceover_path else None,
            "video_url": video_url,
            "captions": captions,
            "status": "ready_to_post" if video_url else "partial"
        }
        
        production_file = OUTPUT_FOLDER / f"{vibe_id}_production.json"
        with open(production_file, "w") as f:
            json.dump(production_data, f, indent=2)
        print(f"\n💾 Production data saved: {production_file}")
        
        # Step 4: Post to all platforms
        if video_url:
            print("\n" + "=" * 60)
            print("📣 POSTING TO ALL PLATFORMS")
            print("=" * 60)
            
            # Instagram
            ig_result = await self.post_to_instagram(video_url, captions["instagram"])
            
            # TikTok
            tt_result = await self.post_to_tiktok(video_url, captions["tiktok"])
            
            # YouTube
            yt_result = await self.post_to_youtube(
                video_url, 
                captions["youtube_title"], 
                captions["youtube_description"]
            )
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 POSTING SUMMARY")
            print("=" * 60)
            print(f"  Instagram: {'✅ Posted' if ig_result else '❌ Failed/Manual'}")
            print(f"  TikTok: {'✅ Posted' if tt_result else '⏭️ Needs OAuth'}")
            print(f"  YouTube: {'✅ Posted' if yt_result else '⏭️ Manual Upload'}")
            
            # Save final status
            production_data["posted"] = {
                "instagram": ig_result,
                "tiktok": tt_result,
                "youtube": yt_result,
                "posted_at": datetime.now().isoformat()
            }
            with open(production_file, "w") as f:
                json.dump(production_data, f, indent=2)
        else:
            print("\n⚠️ No video generated - cannot post")
        
        print("\n" + "=" * 60)
        print("🎉 PRODUCTION COMPLETE!")
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Sisi Lola Content Producer")
    parser.add_argument("--vibe", type=str, default="VIBE010", help="Vibe ID to produce")
    args = parser.parse_args()
    
    producer = SisiLolaProducer()
    await producer.produce_and_post(args.vibe)


if __name__ == "__main__":
    asyncio.run(main())
