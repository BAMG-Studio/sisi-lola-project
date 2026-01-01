#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 SISI LOLA SUPREME PRODUCER v5.0 - REPLICATE EDITION
=============================================================================
100% Replicate Pipeline for Voice & Video
NO External Dependencies (except local files)

Stack:
1. Voice: Replicate XTTS-v2 (Cloned from Authentic Samples)
2. Video: Replicate OmniHuman (ByteDance) - Audio-driven animation
3. Captions: Local Generation

Run: python -m sisi_lola_api.scripts.authentic_producer_v5 --vibe VIBE010
=============================================================================
"""

import asyncio
import argparse
import json
import os
import time
import base64
import httpx
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
from PIL import Image

# Load environment
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DNA_FOLDER = PROJECT_ROOT / "sisi_lola_api" / "assets" / "dna"
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "authentic_videos"
VOICE_MODELS_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_models"
REFERENCE_AUDIO_PATH = VOICE_MODELS_FOLDER / "sisi_lola_training_audio.wav"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# API Keys
REPLICATE_API_TOKEN = "r8_V7hyzBNwBGzhQax9O43wpb3CqInl5g22WaIhE"

# Preferred DNA images
PREFERRED_DNA_IMAGES = [
    "Sisi Lola Live Show Hostess.png",
    "sisi lola 1.png",
    "sisi lola 2.png",
]

# ============================================================================
# AUTHENTIC YORUNGLISH SCRIPTS
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


class SupremeProducer:
    """
    Sisi Lola Supreme Producer v5.0
    Replicate-only pipeline for authentic AI video production.
    """
    
    def __init__(self):
        self.dna_images = self._get_dna_images()
        print(f"📸 Found {len(self.dna_images)} DNA images")
        
        # Verify reference audio
        if REFERENCE_AUDIO_PATH.exists():
            print(f"🎙️ Found reference audio: {REFERENCE_AUDIO_PATH.name}")
        else:
            print(f"⚠️ Reference audio not found at: {REFERENCE_AUDIO_PATH}")
            print("   Please run 'select_best_voices.py' and 'train_voice_rvc.py' first!")
    
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
    
    def normalize_text_for_ai(self, text: str) -> str:
        """
        Fix pronunciation for AI models using phonetic respelling.
        """
        replacements = {
            "Lagos": "Lay-gos",
            "lagos": "Lay-gos",
            "Naija": "Nai-jah",
            "Sisi": "Cee-cee",
            "wahala": "wa-ha-la",
            "Una": "Oo-na",
            "una": "oo-na",
            "Abeg": "Ah-beg",
            "Oya": "Oh-ya"
        }
        
        for word, replacement in replacements.items():
            text = text.replace(word, replacement)
            
        return text

    def resize_image_for_model(self, image_path: Path, max_size: int = 1024) -> bytes:
        """Resize image to optimal dimensions for AI models"""
        print(f"  📐 Resizing image...")
        
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
        
        # Ensure dimensions are divisible by 2 (required by some video codecs)
        new_width = new_width - (new_width % 2)
        new_height = new_height - (new_height % 2)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        
        print(f"  ✅ Resized to {new_width}x{new_height}")
        return buffer.read()
    
    def file_to_base64(self, file_path: Path) -> str:
        """Convert file to base64 data URI"""
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        
        # Guess mime type
        ext = file_path.suffix.lower()
        if ext == ".wav":
            mime = "audio/wav"
        elif ext == ".mp3":
            mime = "audio/mpeg"
        elif ext in [".jpg", ".jpeg"]:
            mime = "image/jpeg"
        elif ext == ".png":
            mime = "image/png"
        else:
            mime = "application/octet-stream"
            
        return f"data:{mime};base64,{data}"
    
    async def generate_voice_elevenlabs(self, text: str, vibe_id: str) -> Optional[Path]:
        """
        Generate voice using ElevenLabs (Native Quality)
        """
        print(f"\n🎙️ Step 1: Generating voice (ElevenLabs - Native)...")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_voice_elevenlabs.wav"
        
        if output_path.exists():
            print(f"  ✅ Voice already exists: {output_path.name}")
            return output_path
            
        # 1. Normalize Pronunciation (Fix AI accents)
        clean_text = self.normalize_text_for_ai(text)
        print(f"  📝 Normalized Script: {clean_text[:50]}...")
        
        # Voice ID: "Sisi Lola (Authentic V5)"
        voice_id = "e3EHR2GS90EO276k1OCA" 
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json"
        }
        
        data = {
            "text": clean_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.35,  # Option B: High Expression
                "similarity_boost": 0.80,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                print(f"  🚀 Sending to ElevenLabs...")
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"  ✅ Voice saved: {output_path.name}")
                    return output_path
                else:
                    print(f"  ❌ ElevenLabs error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  ❌ Voice generation failed: {str(e)}")
            
        return None

    # ... (Unified Video Method) ...
    
    async def produce(self, vibe_id: str):
        """Full production pipeline"""
        print("\n" + "=" * 60)
        print(f"🇳🇬 SISI LOLA SUPREME PRODUCER v5.0: {vibe_id}")
        print("     REPLICATE ALL-IN-ONE EDITION")
        print("=" * 60)
        
        script_data = self.get_script(vibe_id)
        if not script_data:
            print(f"❌ Script '{vibe_id}' not found!")
            return
        
        print(f"\n📌 Title: {script_data['title']}")
        
        if not self.dna_images:
            print("❌ No DNA images found!")
            return
            
        source_image = self.dna_images[0]
        print(f"📸 Using: {source_image.name}")
        
        start_time = time.time()
        
        # 1. Voice
        # voice_path = await self.generate_voice_xtts(script_data["script"], vibe_id)
        voice_path = await self.generate_voice_elevenlabs(script_data["script"], vibe_id)
        
        if not voice_path:
            print("❌ Stopping production due to voice failure")
            return
            
        # 2. Video
        # Default to Wav2Lip for reliability, can switch back to OmniHuman later if unlocked
        video_path = await self.create_talking_video_wav2lip(source_image, voice_path, vibe_id)
        
        # 3. Captions
        captions = self.generate_captions(script_data)
        
        # Save Metadata
        if video_path:
            meta = {
                "vibe_id": vibe_id,
                "created_at": datetime.now().isoformat(),
                "video_path": str(video_path),
                "voice_path": str(voice_path),
                "captions": captions,
                "engine": "ElevenLabs + Wav2Lip"
            }
    
    async def create_talking_video_omnihuman(self, image_path: Path, audio_path: Path, vibe_id: str) -> Optional[Path]:
        """
        Create REALISTIC talking video using OmniHuman (Camenduru Version)
        """
        print(f"\n🎬 Step 2: Creating REALISTIC video (OmniHuman)...")
        print(f"  📸 Source: {image_path.name}")
        print(f"  🎙️ Audio: {audio_path.name}")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_talking_omni.mp4"
        if output_path.exists():
            return output_path
        
        try:
            # Resize image (OmniHuman likes 512x512 or 768x768)
            resized_bytes = self.resize_image_for_model(image_path, max_size=768)
            image_b64 = "data:image/jpeg;base64," + base64.b64encode(resized_bytes).decode('utf-8')
            audio_b64 = self.file_to_base64(audio_path)
            
            async with httpx.AsyncClient(timeout=900) as client:
                print(f"  🚀 Sending to OmniHuman (Camenduru)...")
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        # camenduru/omni-human
                        "version": "5313a37b3f9dc4d409d6c810c2834f8287383796d195cd4520937a0c1071d05d",
                        "input": {
                            "image": image_b64,
                            "audio": audio_b64
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    prediction_id = response.json().get("id")
                    print(f"  ⏳ OmniHuman Generation started: {prediction_id}")
                    print(f"  ℹ️ This takes 3-5 minutes...")
                    
                    video_url = await self._poll_replicate(client, prediction_id, max_wait=1200)
                    
                    if video_url:
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        print(f"  ✅ OMNIHUMAN VIDEO CREATED: {output_path.name}")
                        return output_path
                else:
                    print(f"  ❌ Replicate error: {response.status_code}")
                    print(f"  ⚠️ Falling back to Wav2Lip...")
                    
        except Exception as e:
            print(f"  ❌ Generation failed: {str(e)}")
            print(f"  ⚠️ Falling back to Wav2Lip...")
            
        # Fallback to Wav2Lip if OmniHuman fails
        return await self.create_talking_video_wav2lip(image_path, audio_path, vibe_id)

    async def create_talking_video_wav2lip(self, image_path: Path, audio_path: Path, vibe_id: str) -> Optional[Path]:
        """
        Create talking video using Wav2Lip (Reliable & Public)
        """
        print(f"\n🎬 Step 2b: Fallback Video (Wav2Lip)...")
        print(f"  📸 Source: {image_path.name}")
        
        output_path = OUTPUT_FOLDER / f"{vibe_id}_talking_wav2lip.mp4"
        if output_path.exists():
            return output_path
        
        try:
            # Wav2Lip likes 512x512
            resized_bytes = self.resize_image_for_model(image_path, max_size=512)
            image_b64 = "data:image/jpeg;base64," + base64.b64encode(resized_bytes).decode('utf-8')
            audio_b64 = self.file_to_base64(audio_path)
            
            async with httpx.AsyncClient(timeout=600) as client:
                print(f"  🚀 Sending to Wav2Lip...")
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {REPLICATE_API_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        # devxpy/cog-wav2lip
                        "version": "8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
                        "input": {
                            "face": image_b64,
                            "audio": audio_b64,
                            "pads": "0 10 0 0",
                            "smooth": True
                        }
                    }
                )
                
                if response.status_code in [200, 201]:
                    prediction_id = response.json().get("id")
                    print(f"  ⏳ Wav2Lip Generation started: {prediction_id}")
                    
                    video_url = await self._poll_replicate(client, prediction_id)
                    
                    if video_url:
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        print(f"  ✅ WAV2LIP VIDEO CREATED: {output_path.name}")
                        return output_path
                else:
                    print(f"  ❌ Replicate error: {response.text}")

        except Exception as e:
            print(f"  ❌ Wav2Lip failed: {str(e)}")
            
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
                        # Some models return list, select first item
                        if isinstance(output, list) and output:
                            return output[0]
                        return output
                    elif status == "failed":
                        print(f"  ❌ Failed: {data.get('error')}")
                        return None
                    elif status == "canceled":
                        print(f"  ❌ Canceled")
                        return None
                    else:
                        print(f"  ⏳ Status: {status}...")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                print(f"  ⚠️ Poll error: {e}")
                await asyncio.sleep(5)
        
        print("  ❌ Timeout waiting for prediction")
        return None
    
    def generate_captions(self, script_data: Dict) -> Dict[str, str]:
        """Generate platform-specific captions"""
        print(f"\n📝 Step 3: Generating captions...")
        
        hashtags = script_data.get("hashtags", ["SisiLola", "Naija"])
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        
        script_preview = script_data.get("script", "")[:200].strip()
        
        captions = {
            "instagram": f"{script_preview}...\n\n{hashtag_str}\n\n💃 Follow @sisilolalive!",
            "tiktok": f"{script_preview}...\n\n{hashtag_str}",
            "youtube_title": script_data.get("title", "Sisi Lola"),
            "youtube_description": f"{script_data.get('script', '')}\n\n{hashtag_str}"
        }
        
        print(f"  ✅ Captions ready")
        return captions
    
    async def produce(self, vibe_id: str):
        """Full production pipeline"""
        print("\n" + "=" * 60)
        print(f"🇳🇬 SISI LOLA SUPREME PRODUCER v5.0: {vibe_id}")
        print("     REPLICATE ALL-IN-ONE EDITION")
        print("=" * 60)
        
        script_data = self.get_script(vibe_id)
        if not script_data:
            print(f"❌ Script '{vibe_id}' not found!")
            return
        
        print(f"\n📌 Title: {script_data['title']}")
        
        if not self.dna_images:
            print("❌ No DNA images found!")
            return
            
        source_image = self.dna_images[0]
        print(f"📸 Using: {source_image.name}")
        
        start_time = time.time()
        
        # 1. Voice
        # voice_path = await self.generate_voice_xtts(script_data["script"], vibe_id)
        voice_path = await self.generate_voice_elevenlabs(script_data["script"], vibe_id)
        
        if not voice_path:
            print("❌ Stopping production due to voice failure")
            return
            
        # 2. Video
        # Default to Wav2Lip for reliability now
        video_path = await self.create_talking_video_wav2lip(source_image, voice_path, vibe_id)
        
        # 3. Captions
        captions = self.generate_captions(script_data)
        
        # Save Metadata
        if video_path:
            meta = {
                "vibe_id": vibe_id,
                "created_at": datetime.now().isoformat(),
                "video_path": str(video_path),
                "voice_path": str(voice_path),
                "captions": captions,
                "engine": "ElevenLabs + Wav2Lip"
            }
            with open(OUTPUT_FOLDER / f"{vibe_id}_meta.json", "w") as f:
                json.dump(meta, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 SUPREME PRODUCTION SUMMARY")
        print("=" * 60)
        print(f"  ⏱️ Total Time: {(time.time() - start_time)/60:.1f} minutes")
        print(f"  🎙️ Voice: {voice_path.name}")
        print(f"  🎬 Video: {'✅ ' + video_path.name if video_path else '❌ Failed'}")
        
        if video_path:
            print(f"\n🎉 DONE! Video is ready in: {OUTPUT_FOLDER}")
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vibe", type=str, default="VIBE010", help="Vibe ID")
    args = parser.parse_args()
    
    producer = SupremeProducer()
    await producer.produce(args.vibe)


if __name__ == "__main__":
    asyncio.run(main())
