#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 SISI LOLA AUTHENTIC PRODUCER v4.0 - META MMS YORUBA EDITION
=============================================================================
REAL Nigerian Voice using Meta's MMS-TTS Yoruba Model!

Stack:
1. Meta MMS-TTS (Yoruba/Nigerian) → Authentic African voice
2. SadTalker (fixed) → Lip sync with resized image
3. FFmpeg → Final processing

Note: MMS-TTS speaks Yoruba natively. For Yorunglish (mixed English/Yoruba),
the voice will have authentic African tone and pronunciation.

Run: python -m sisi_lola_api.scripts.authentic_producer --vibe VIBE010
=============================================================================
"""

import asyncio
import argparse
import json
import os
import subprocess
import httpx
import time
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
from PIL import Image
import io

# Import SisiLolaDNA for centralized config
try:
    from sisi_lola_api.app.config import SisiLolaDNA
except ImportError:
    # Fallback if PYTHONPATH is not set correctly for the script
    class SisiLolaDNA:
        REPLICATE_MODELS = {
            "omnihuman": "tencentarc/omnihuman",
            "wav2lip": "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef"
        }
        VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5, "use_speaker_boost": True}

# Load environment
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DNA_FOLDER = PROJECT_ROOT / "sisi_lola_api" / "assets" / "dna"
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "authentic_videos"
CONTENT_QUEUE_PATH = PROJECT_ROOT / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# API Configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# Preferred DNA images
PREFERRED_DNA_IMAGES = [
    "Sisi Lola Live Show Hostess.png",
    "sisi lola 1.png",
    "sisi lola 2.png",
]

# ============================================================================
# AUTHENTIC YORUNGLISH SCRIPTS (3+ minutes of content)
# ============================================================================

AUTHENTIC_SCRIPTS = {
    "VIBE010": {
        "title": "New Africa Roll Call",
        "script": """
Ẹ kú àárọ̀ o! How far my beautiful people!

Na your girl Sisi Lola dey here again, coming to you straight from Lagos, Nigeria!

Today, I wan yarn una about wetin dey happen for our Africa. The new Africa wey dey rise!

From Lagos to Nairobi, from Accra to Johannesburg, young people dey change the game!

We no dey wait for anybody again. We dey build our own startups, we dey create our own content, we dey show the world say Africa na the future!

You know, when I look at our generation, my heart dey full. See the talent wey dey our continent! 

Musicians, artists, tech gurus, entrepreneurs - everybody dey hustle, everybody dey shine!

And you know wetin sweet pass? We dey do am our own way! No be copy copy - na original vibes!

So today, I dey give shoutout to every young African wey dey work hard. Whether you dey for Nigeria, Ghana, Kenya, South Africa, or anywhere for diaspora - you matter!

Ẹ ṣé o! Thank you for being part of this movement. Together, we go build the Africa wey we want to see.

Make sure you follow me for more gist. Share this video with your people dem.

Until next time, na your girl Sisi Lola. Stay blessed, stay African, stay winning!

Ó dàbọ̀!
        """,
        "duration_seconds": 180,
        "hashtags": ["SisiLola", "NewAfrica", "AfricanExcellence", "Lagos", "Naija", "AfroVibes", "YorubaPride"]
    },
    "VIBE011": {
        "title": "Lagos Hustle Chronicles",
        "script": """
Ẹ kú ilẹ̀ o! Good morning everybody!

Una don chop? Make sure say una belleful o, because today tori go long!

I wan gist una about this Lagos life. The hustle, the grind, the wins, and sometimes the wahala.

Lagos no be for the weak o! From morning when you wake up, na fight. Traffic go first test your patience.

But you know wetin make Lagos special? The people! Lagos people no dey give up!

I remember when I first come Lagos, e no easy at all. But I learn say this city go reward you if you no give up.

Every day, millions of people dey wake up, dey hustle, dey grind. And that energy, that spirit - e dey contagious!

So if you dey struggle for Lagos now, I want tell you say hold on. Your breakthrough dey come!

Every successful person wey you see for this Lagos, dem don see pepper before. But dem no quit!

So take heart, my people. Lagos go reward your hustle. Just make sure say you dey do the right thing.

Thank you for joining me today. Make una comment for down below, tell me your Lagos story.

Na your girl Sisi Lola. See una next time!

Ó dàbọ̀!
        """,
        "duration_seconds": 200,
        "hashtags": ["LagosHustle", "LagosBabe", "NaijaGirl", "SisiLola", "Lagos", "Hustle", "Motivation"]
    }
}


class AuthenticProducer:
    """
    Authentic Sisi Lola video producer using Meta MMS-TTS
    for REAL Nigerian/Yoruba voice!
    """
    
    def __init__(self):
        self.dna_images = self._get_dna_images()
        self.cloned_voice_id = self._get_cloned_voice_id()
        print(f"📸 Found {len(self.dna_images)} DNA images")
        if self.cloned_voice_id:
            print(f"🎙️ Using Cloned Voice ID: {self.cloned_voice_id}")
    
    def _get_cloned_voice_id(self) -> Optional[str]:
        """Load the voice ID generated by train_voice_elevenlabs.py"""
        voice_id_file = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_models" / "elevenlabs_voice_id.txt"
        if voice_id_file.exists():
            return voice_id_file.read_text().strip()
        return None
    
    def _get_dna_images(self) -> List[Path]:
        images = []
        if DNA_FOLDER.exists():
            for name in PREFERRED_DNA_IMAGES:
                path = DNA_FOLDER / name
                if path.exists():
                    images.append(path)
            
            if len(images) < 2:
                for img_path in DNA_FOLDER.glob("*.png"):
                    if img_path.stat().st_size > 500_000 and img_path not in images:
                        images.append(img_path)
                        if len(images) >= 3:
                            break
        return images
    
    def get_script(self, vibe_id: str) -> Optional[Dict]:
        """Get authentic script for a vibe"""
        return AUTHENTIC_SCRIPTS.get(vibe_id)
    
    def resize_image_for_sadtalker(self, image_path: Path, max_size: int = 512) -> bytes:
        """Resize image to prevent SadTalker 422 errors"""
        print(f"  📐 Resizing image for lip sync...")
        
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize while maintaining aspect ratio
        width, height = img.size
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        
        print(f"  ✅ Resized to {new_width}x{new_height}")
        return buffer.read()
    
    async def generate_voice_mms(self, text: str, vibe_id: str) -> Optional[Path]:
        """
        Generate voice - Try ElevenLabs first (works!), then Replicate XTTS
        """
        print(f"\n🎙️ Step 1: Generating voice...")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_voice.mp3"
        
        if output_path.exists():
            print(f"  ✅ Voice already exists: {output_path.name}")
            return output_path
        
        # Clean text - remove extra whitespace, limit length
        clean_text = " ".join(text.strip().split())[:1500]  # Limit to prevent timeout
        
        # Try ElevenLabs first (it WORKS!)
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        if elevenlabs_key:
            try:
                print(f"  🎙️ Using ElevenLabs...")
                # Use cloned voice if available, otherwise fallback to "Bella"
                voice_id = self.cloned_voice_id or "EXAVITQu4vr4xnSDxMaL"
                
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                        headers={
                            "xi-api-key": elevenlabs_key,
                            "Content-Type": "application/json"
                        },
                        json={
                            "text": clean_text,
                            "model_id": "eleven_multilingual_v2",
                            "voice_settings": {
                                "stability": 0.4,
                                "similarity_boost": 0.8,
                                "style": 0.7,
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
                        print(f"  ⚠️ ElevenLabs error: {response.status_code}")
            except Exception as e:
                print(f"  ⚠️ ElevenLabs failed: {str(e)}")
        
        # Fallback: Use Replicate Bark TTS (supports different styles)
        print(f"  🎙️ Trying Replicate Bark TTS...")
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",  # Bark
                        "input": {
                            "prompt": clean_text[:500],
                            "text_temp": 0.7,
                            "waveform_temp": 0.7,
                            "history_prompt": "v2/en_speaker_6"  # Female speaker
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    prediction = response.json()
                    prediction_id = prediction.get("id")
                    print(f"  ⏳ Voice generation started: {prediction_id}")
                    
                    audio_url = await self._poll_replicate(client, prediction_id)
                    
                    if audio_url:
                        audio_response = await client.get(audio_url)
                        wav_path = OUTPUT_FOLDER / f"{vibe_id}_voice.wav"
                        with open(wav_path, "wb") as f:
                            f.write(audio_response.content)
                        print(f"  ✅ Voice saved: {wav_path.name}")
                        return wav_path
                        
        except Exception as e:
            print(f"  ❌ Bark TTS failed: {str(e)}")
        
        print("  ❌ All voice generation methods failed!")
        return None
    
    async def _poll_replicate(self, client: httpx.AsyncClient, prediction_id: str, max_wait: int = 300) -> Optional[str]:
        """Poll Replicate API for completion"""
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
                        print(f"  ❌ Failed: {data.get('error')}")
                        return None
                    else:
                        print(f"  ⏳ Status: {status}...")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                print(f"  ⚠️ Poll error: {e}")
                await asyncio.sleep(3)
        
        return None
    
    async def create_talking_video_sadtalker(self, image_path: Path, audio_path: Path, vibe_id: str) -> Optional[Path]:
        """
        Create REALISTIC talking video using ByteDance OmniHuman
        - Supports audio-driven animation
        - Generates natural head movements and expressions
        - Professional-quality output
        """
        print(f"\n🎬 Step 2: Creating REALISTIC video (OmniHuman)...")
        print(f"  📸 Source: {image_path.name}")
        print(f"  🎙️ Audio: {audio_path.name}")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_talking.mp4"
        
        if output_path.exists():
            print(f"  ✅ Video already exists: {output_path.name}")
            return output_path
        
        try:
            # RESIZE IMAGE for optimal processing
            resized_image_bytes = self.resize_image_for_sadtalker(image_path, max_size=768)  # OmniHuman handles larger
            image_b64 = base64.b64encode(resized_image_bytes).decode()
            
            # Read audio
            with open(audio_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            
            # Determine audio format
            audio_ext = str(audio_path).split(".")[-1].lower()
            audio_mime = {"mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4"}.get(audio_ext, "audio/mpeg")
            
            async with httpx.AsyncClient(timeout=900) as client:  # Longer timeout for realistic generation
                # Use ByteDance OmniHuman - the BEST for realism
                print(f"  🚀 Sending to OmniHuman (Premium)...")
                
                # Use version from DNA or fallback
                model_version = SisiLolaDNA.REPLICATE_MODELS.get("omnihuman", "tencentarc/omnihuman")
                
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_version, # Using model slug directly often works or requires version ID
                        "input": {
                            "image": f"data:image/jpeg;base64,{image_b64}",
                            "audio": f"data:{audio_mime};base64,{audio_b64}"
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    prediction = response.json()
                    prediction_id = prediction.get("id")
                    print(f"  ⏳ Realistic generation started: {prediction_id}")
                    print(f"  ℹ️ This may take 2-5 minutes for high quality...")
                    
                    video_url = await self._poll_replicate(client, prediction_id, max_wait=600)
                    
                    if video_url:
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        
                        size_mb = output_path.stat().st_size / (1024 * 1024)
                        print(f"  ✅ REALISTIC video created: {output_path.name} ({size_mb:.1f} MB)")
                        return output_path
                elif response.status_code == 422:
                    # OmniHuman not available, try fallback
                    print(f"  ⚠️ OmniHuman not available, trying Wav2Lip fallback...")
                    return await self._fallback_wav2lip(image_b64, audio_b64, audio_mime, vibe_id)
                else:
                    error_text = response.text[:500]
                    print(f"  ❌ OmniHuman error: {response.status_code}")
                    print(f"  Details: {error_text}")
                    # Try fallback
                    return await self._fallback_wav2lip(image_b64, audio_b64, audio_mime, vibe_id)
                    
        except Exception as e:
            print(f"  ❌ Video generation failed: {str(e)}")
            return None
    
    async def _fallback_wav2lip(self, image_b64: str, audio_b64: str, audio_mime: str, vibe_id: str) -> Optional[Path]:
        """Fallback to Wav2Lip if OmniHuman fails"""
        print(f"  🔄 Trying Wav2Lip fallback...")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_talking.mp4"
        
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                # Use version from DNA or fallback
                model_version = SisiLolaDNA.REPLICATE_MODELS.get("wav2lip", "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef")
                
                # Check if it's a slug or version ID (if it has a colon, it's version)
                payload = {"input": {
                    "face": f"data:image/jpeg;base64,{image_b64}",
                    "audio": f"data:{audio_mime};base64,{audio_b64}",
                    "pads": "0 10 0 0",
                    "smooth": True,
                    "fps": 25
                }}
                
                if ":" in model_version:
                    payload["version"] = model_version.split(":")[-1]
                else:
                    payload["model"] = model_version

                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    prediction = response.json()
                    prediction_id = prediction.get("id")
                    print(f"  ⏳ Wav2Lip started: {prediction_id}")
                    
                    video_url = await self._poll_replicate(client, prediction_id)
                    
                    if video_url:
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        
                        size_mb = output_path.stat().st_size / (1024 * 1024)
                        print(f"  ✅ Fallback video: {output_path.name} ({size_mb:.1f} MB)")
                        return output_path
        except Exception as e:
            print(f"  ❌ Fallback failed: {str(e)}")
        
        return None
    
    def generate_captions(self, script_data: Dict) -> Dict[str, str]:
        """Generate platform-specific captions"""
        print(f"\n📝 Step 3: Generating captions...")
        
        hashtags = script_data.get("hashtags", ["SisiLola", "Naija"])
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        
        # Short version of script for caption
        script_preview = script_data.get("script", "")[:200].strip()
        
        captions = {
            "instagram": f"{script_preview}...\n\n{hashtag_str}\n\n💃 Follow @sisilolalive!",
            "tiktok": f"{script_preview}...\n\n{hashtag_str}",
            "youtube_title": script_data.get("title", "Sisi Lola"),
            "youtube_description": f"{script_data.get('script', '')}\n\n{hashtag_str}"
        }
        
        print(f"  ✅ Captions ready for all platforms")
        return captions
    
    async def produce(self, vibe_id: str):
        """Full authentic production pipeline"""
        print("\n" + "=" * 60)
        print(f"🇳🇬 SISI LOLA AUTHENTIC PRODUCER v4.0: {vibe_id}")
        print("     META MMS YORUBA + SADTALKER EDITION")
        print("=" * 60)
        
        # Get script
        script_data = self.get_script(vibe_id)
        if not script_data:
            print(f"❌ Script for '{vibe_id}' not found!")
            print(f"   Available: {list(AUTHENTIC_SCRIPTS.keys())}")
            return
        
        print(f"\n📌 Title: {script_data['title']}")
        print(f"📝 Script length: {len(script_data['script'])} chars")
        print(f"⏱️ Target duration: {script_data['duration_seconds']}s")
        
        # Get DNA image
        if not self.dna_images:
            print("❌ No DNA images found!")
            return
        
        source_image = self.dna_images[0]
        print(f"📸 Using: {source_image.name}")
        
        # Step 1: Generate Voice
        voice_path = await self.generate_voice_mms(script_data["script"], vibe_id)
        if not voice_path:
            print("\n❌ Voice generation failed!")
            return
        
        # Step 2: Create Talking Video
        video_path = await self.create_talking_video_sadtalker(source_image, voice_path, vibe_id)
        
        # Step 3: Captions
        captions = self.generate_captions(script_data)
        
        # Save production data
        production_data = {
            "vibe_id": vibe_id,
            "title": script_data["title"],
            "produced_at": datetime.now().isoformat(),
            "voice_path": str(voice_path) if voice_path else None,
            "video_path": str(video_path) if video_path else None,
            "captions": captions,
            "status": "success" if video_path else "partial",
            "method": "mms-tts-yoruba + sadtalker"
        }
        
        with open(OUTPUT_FOLDER / f"{vibe_id}_production.json", "w") as f:
            json.dump(production_data, f, indent=2, ensure_ascii=False)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION SUMMARY")
        print("=" * 60)
        print(f"  🎙️ Voice: {'✅ ' + voice_path.name if voice_path else '❌ Failed'}")
        print(f"  🎬 Video: {'✅ ' + video_path.name if video_path else '❌ Failed'}")
        print(f"  📝 Captions: ✅ Ready")
        
        if video_path:
            print(f"\n📍 Output: {OUTPUT_FOLDER}")
            print("\n🎉 AUTHENTIC PRODUCTION SUCCESSFUL!")
        
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Sisi Lola Authentic Producer v4.0")
    parser.add_argument("--vibe", type=str, default="VIBE010", help="Vibe ID")
    args = parser.parse_args()
    
    producer = AuthenticProducer()
    await producer.produce(args.vibe)


if __name__ == "__main__":
    # Check for PIL
    try:
        from PIL import Image
    except ImportError:
        print("Installing Pillow...")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"])
        from PIL import Image
    
    asyncio.run(main())
