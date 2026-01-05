#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SISI LOLA - FULL VIDEO CONTENT PRODUCER
═══════════════════════════════════════════════════════════════════════════════
            Creates REAL 3-minute video content with voice and avatar
═══════════════════════════════════════════════════════════════════════════════

Pipeline:
1. Generate script (3 minutes of talking content)
2. Generate voice with ElevenLabs
3. Generate talking head video with HeyGen or D-ID
4. Post to Instagram as Reel

NO PLAY - THIS IS THE REAL THING!
"""

import os
import sys
import json
import time
import asyncio
import requests
import base64
from pathlib import Path
from datetime import datetime

# Load environment
from dotenv import load_dotenv

env_paths = [Path("sisi_lola_api/.env"), Path(".env")]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        print(f"✅ Loaded: {p}")
        break

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
# Use a PUBLIC HeyGen avatar instead of custom one
HEYGEN_AVATAR_ID = "Hada_Casual_Front_public"  # Free public avatar
DID_API_KEY = os.getenv("DID_API_KEY")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841478533567114")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

OUTPUT_DIR = Path("content_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA CHARACTER
# ═══════════════════════════════════════════════════════════════════════════════

SISI_LOLA_SCRIPT_3MIN = """
How you dey, my beautiful people! Welcome to another episode with your girl, Sisi Lola!

Today, I wan yarn with una about something wey dey very close to my heart - the New Africa we dey build together!

You know say, when I look around Nigeria today, I see so many young people wey dey innovate, wey dey create amazing things. From tech startups in Yaba, to fashion designers in Aba, to musicians wey dey take our Afrobeats to the whole world! E sweet me well well o!

But make I tell una small secret - the reason why Africa go definitely shine, na because of US. Na because of you wey dey watch this video right now. Na because you no gree give up, even when wahala full ground.

See ehn, I know say things no easy sometimes. Light dey take, fuel dey expensive, network dey misbehave. But my people, na these challenges dey make us strong! Na im make us creative! Na im make us find solution where other people see problem!

Look at Flutterwave, look at Paystack, look at all these Nigerian companies wey dey change the game globally. Dem no start with everything. Dem start with dream and determination!

So today, I wan challenge you. Yes, you wey dey watch me! What be that dream wey you don dey postpone? What be that business idea wey you dey fear to start? What be that skill wey you wan learn?

My dear, na today be the day! No more tomorrow, no more next week, no more next year. Start today, even if na small small. Baby steps still dey move person forward!

And remember say, community dey important. Link up with people wey get the same vision like you. Join WhatsApp groups, attend meetups, connect on LinkedIn. No man na island!

Before I go, make I give una my three golden rules for success:

Number one - Consistency dey key. Even when you no feel like am, show up!

Number two - Learn every single day. The world dey change fast, make sure say you dey change with am!

Number three - Never forget where you come from. Stay humble, stay grounded, stay Nigerian!

Alright my loves, na so we see am today o! Make sure say you follow me for more gist and inspiration. Share this video, comment wetin dey your mind, and remember say...

Sisi Lola love una scatter! Nigeria to the world! 

Bye bye now! Muah!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: GENERATE VOICE WITH ELEVENLABS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_voice_elevenlabs(script: str, output_path: Path) -> bool:
    """Generate Nigerian voice using ElevenLabs."""
    print("\n" + "═" * 70)
    print("🎤 STEP 1: GENERATING VOICE WITH ELEVENLABS")
    print("═" * 70)
    
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found!")
        return False
    
    print(f"📝 Script length: {len(script)} characters")
    print(f"⏱️  Estimated duration: ~3 minutes")
    
    # Use ElevenLabs API
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }
    
    try:
        print("🔄 Generating audio... (this may take 1-2 minutes)")
        response = requests.post(url, json=data, headers=headers, timeout=300)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            file_size = output_path.stat().st_size / 1024 / 1024  # MB
            print(f"✅ Voice generated!")
            print(f"📁 Saved to: {output_path}")
            print(f"📊 File size: {file_size:.2f} MB")
            return True
        else:
            print(f"❌ ElevenLabs error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: GENERATE VIDEO WITH HEYGEN
# ═══════════════════════════════════════════════════════════════════════════════

def generate_video_heygen(script: str) -> str:
    """Generate talking head video with HeyGen."""
    print("\n" + "═" * 70)
    print("🎬 STEP 2: GENERATING VIDEO WITH HEYGEN")
    print("═" * 70)
    
    if not HEYGEN_API_KEY:
        print("❌ HEYGEN_API_KEY not found!")
        return None
    
    print(f"🎭 Avatar ID: {HEYGEN_AVATAR_ID}")
    print(f"📝 Script length: {len(script)} characters")
    
    # Create video
    url = "https://api.heygen.com/v2/video/generate"
    
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
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
                "value": "#1a1a2e"  # Dark background
            }
        }],
        "dimension": {
            "width": 1080,
            "height": 1920  # 9:16 for Reels
        }
    }
    
    try:
        print("🔄 Creating video... (this may take 5-10 minutes)")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            video_id = result.get("data", {}).get("video_id")
            print(f"✅ Video generation started!")
            print(f"🆔 Video ID: {video_id}")
            
            # Poll for completion
            video_url = poll_heygen_status(video_id)
            return video_url
        else:
            print(f"❌ HeyGen error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def poll_heygen_status(video_id: str, max_wait: int = 600) -> str:
    """Poll HeyGen for video completion."""
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("data", {}).get("status")
                
                if status == "completed":
                    video_url = data.get("data", {}).get("video_url")
                    print(f"✅ Video ready!")
                    print(f"🔗 URL: {video_url[:80]}...")
                    return video_url
                elif status == "failed":
                    print(f"❌ Video generation failed")
                    error = data.get("data", {}).get("error")
                    if error:
                        print(f"   Error: {error}")
                    return None
                else:
                    elapsed = int(time.time() - start_time)
                    print(f"   ⏳ Status: {status} ({elapsed}s elapsed)")
                    time.sleep(15)
            else:
                print(f"   ⚠️ Poll error: {response.status_code}")
                time.sleep(10)
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            time.sleep(10)
    
    print("❌ Timeout waiting for video")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2B: FALLBACK - GENERATE VIDEO WITH D-ID
# ═══════════════════════════════════════════════════════════════════════════════

def generate_video_did(script: str) -> str:
    """Generate talking head video with D-ID as fallback."""
    print("\n" + "═" * 70)
    print("🎬 STEP 2B: GENERATING VIDEO WITH D-ID (FALLBACK)")
    print("═" * 70)
    
    if not DID_API_KEY:
        print("❌ DID_API_KEY not found!")
        return None
    
    # D-ID has character limits, split if needed
    max_chars = 500
    if len(script) > max_chars:
        print(f"⚠️  Script too long ({len(script)} chars), using first {max_chars}")
        script = script[:max_chars]
    
    # Create auth header
    if ":" in DID_API_KEY:
        auth_string = DID_API_KEY
    else:
        auth_string = f"{DID_API_KEY}:"
    
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    
    # Use D-ID presenter image
    source_url = "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg"
    
    url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Content-Type": "application/json"
    }
    
    data = {
        "script": {
            "type": "text",
            "input": script,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-NG-EzinneNeural"  # Nigerian voice
            }
        },
        "source_url": source_url,
        "config": {
            "fluent": True,
            "pad_audio": 0
        }
    }
    
    try:
        print("🔄 Creating video with D-ID...")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            result = response.json()
            talk_id = result.get("id")
            print(f"✅ D-ID video started! ID: {talk_id}")
            
            # Poll for completion
            video_url = poll_did_status(talk_id, auth_bytes)
            return video_url
        else:
            print(f"❌ D-ID error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def poll_did_status(talk_id: str, auth_bytes: str, max_wait: int = 180) -> str:
    """Poll D-ID for video completion."""
    url = f"https://api.d-id.com/talks/{talk_id}"
    headers = {"Authorization": f"Basic {auth_bytes}"}
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "done":
                    video_url = data.get("result_url")
                    print(f"✅ D-ID video ready!")
                    return video_url
                elif status == "error":
                    print(f"❌ D-ID error: {data.get('error')}")
                    return None
                else:
                    elapsed = int(time.time() - start_time)
                    print(f"   ⏳ D-ID status: {status} ({elapsed}s)")
                    time.sleep(5)
            else:
                time.sleep(5)
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            time.sleep(5)
    
    print("❌ D-ID timeout")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: POST TO INSTAGRAM AS REEL
# ═══════════════════════════════════════════════════════════════════════════════

def post_to_instagram_reel(video_url: str, caption: str) -> bool:
    """Post video to Instagram as Reel."""
    print("\n" + "═" * 70)
    print("📸 STEP 3: POSTING TO INSTAGRAM AS REEL")
    print("═" * 70)
    
    if not INSTAGRAM_TOKEN:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found!")
        return False
    
    print(f"🎬 Video URL: {video_url[:60]}...")
    print(f"📝 Caption: {caption[:50]}...")
    
    # Step 1: Create media container
    print("\n📍 Creating Reel container...")
    
    try:
        response = requests.post(
            f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media",
            params={
                "access_token": INSTAGRAM_TOKEN,
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            container_id = response.json().get("id")
            print(f"   ✅ Container created: {container_id}")
            
            # Wait for processing
            print("\n📍 Waiting for video processing...")
            for i in range(12):  # Wait up to 2 minutes
                time.sleep(10)
                print(f"   ⏳ Processing... ({(i+1)*10}s)")
                
                # Check status
                status_response = requests.get(
                    f"https://graph.facebook.com/v18.0/{container_id}",
                    params={
                        "access_token": INSTAGRAM_TOKEN,
                        "fields": "status_code"
                    }
                )
                
                if status_response.status_code == 200:
                    status = status_response.json().get("status_code")
                    if status == "FINISHED":
                        break
                    elif status == "ERROR":
                        print(f"   ❌ Processing error")
                        return False
            
            # Step 2: Publish
            print("\n📍 Publishing Reel...")
            publish_response = requests.post(
                f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish",
                params={
                    "access_token": INSTAGRAM_TOKEN,
                    "creation_id": container_id
                },
                timeout=60
            )
            
            if publish_response.status_code == 200:
                post_id = publish_response.json().get("id")
                print(f"\n🎉 REEL PUBLISHED!")
                print(f"📱 Post ID: {post_id}")
                print(f"🔗 Check @sisilolalive on Instagram!")
                return True
            else:
                error = publish_response.json().get("error", {})
                print(f"   ❌ Publish failed: {error.get('message', publish_response.text[:100])}")
                return False
        else:
            error = response.json().get("error", {})
            print(f"   ❌ Container failed: {error.get('message', response.text[:200])}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PRODUCTION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_production():
    """Run the full content production pipeline."""
    print("═" * 70)
    print("          SISI LOLA - 3 MINUTE VIDEO PRODUCTION")
    print("                    🇳🇬 NO PLAY O! 🇳🇬")
    print("═" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
    
    script = SISI_LOLA_SCRIPT_3MIN.strip()
    
    # Generate caption for Instagram
    ig_caption = """🇳🇬 The New Africa We Dey Build! 💚

How you dey, my beautiful people? Today I yarn about:
✨ Young Nigerian innovators changing the game
💪 Why our challenges make us stronger  
🚀 My 3 golden rules for success

Watch am full, share am, and remember say...
SISI LOLA LOVE UNA SCATTER! 

#SisiLola #NigeriaToTheWorld #NewAfrica #NaijaContent #AfricanCreator #Motivation #NigerianCreator #AfroVibes #Lagos #Afrobeats #NigerianTech

Follow for more gist! 💃"""
    
    results = {
        "voice": "built-in-heygen",
        "video_url": None,
        "instagram_posted": False
    }
    
    # SKIP STEP 1 - HeyGen has built-in Nigerian voice!
    print("\n⏭️  Skipping ElevenLabs - HeyGen has built-in Nigerian voice")
    
    # STEP 2: Generate Video with HeyGen (includes voice)
    print("\n🎬 Generating video avatar with built-in voice...")
    video_url = generate_video_heygen(script)
    
    # Fallback to D-ID if HeyGen fails
    if not video_url:
        print("\n⚠️  HeyGen failed, trying D-ID...")
        # Use shorter script for D-ID
        short_script = script[:500]
        video_url = generate_video_did(short_script)
    
    results["video_url"] = video_url
    
    # STEP 3: Post to Instagram
    if video_url:
        print("\n🎬 Video ready! Now posting to Instagram...")
        ig_success = post_to_instagram_reel(video_url, ig_caption)
        results["instagram_posted"] = ig_success
    else:
        print("\n❌ No video generated, cannot post to Instagram")
    
    # SUMMARY
    print("\n" + "═" * 70)
    print("                    PRODUCTION SUMMARY")
    print("═" * 70)
    print(f"🎤 Voice: {'✅ Generated' if results['voice'] else '❌ Failed'}")
    print(f"🎬 Video: {'✅ Generated' if results['video_url'] else '❌ Failed'}")
    print(f"📸 Instagram: {'✅ Posted' if results['instagram_posted'] else '❌ Not Posted'}")
    
    if results["video_url"]:
        print(f"\n🔗 Video URL: {results['video_url']}")
    
    if results["instagram_posted"]:
        print("\n🎉 SUCCESS! Check @sisilolalive on Instagram!")
    else:
        print("\n⚠️  Check logs above for issues")
    
    print("═" * 70)
    
    # Save results
    result_file = OUTPUT_DIR / f"production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📁 Results saved: {result_file}")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    results = run_production()
    
    if results["instagram_posted"]:
        print("\n✅ MISSION ACCOMPLISHED!")
        sys.exit(0)
    elif results["video_url"]:
        print("\n⚠️ Video generated but Instagram posting failed")
        sys.exit(1)
    else:
        print("\n❌ Production failed")
        sys.exit(2)
