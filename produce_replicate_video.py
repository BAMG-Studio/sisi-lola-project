#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SISI LOLA - REPLICATE VIDEO PRODUCER
═══════════════════════════════════════════════════════════════════════════════
        Creates video content using Replicate models ONLY (all working)
═══════════════════════════════════════════════════════════════════════════════

Pipeline:
1. Generate image with SDXL (Sisi Lola character)
2. Generate voice with MusicGen/Bark (text-to-speech)
3. Create talking video with Wav2Lip
4. Post to Instagram as Reel

REPLICATE ONLY - NO HeyGen, NO D-ID!
"""

import os
import sys
import json
import time
import requests
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

import replicate

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841478533567114")

OUTPUT_DIR = Path("content_output")
OUTPUT_DIR.mkdir(exist_ok=True)

SISI_LOLA_SEED = 45822

# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA SHORT SCRIPT (30 seconds for testing)
# ═══════════════════════════════════════════════════════════════════════════════

SISI_LOLA_SCRIPT_SHORT = """
How you dey, my beautiful people! Welcome to Sisi Lola live!

Today I wan tell you say, the New Africa wey we dey build, na our future!

See ehn, no matter the wahala, no matter the challenge, we go always rise!

Nigeria to the world! Sisi Lola love una scatter!
"""

SISI_LOLA_SCRIPT_FULL = """
How you dey, my beautiful people! Welcome to another episode with your girl, Sisi Lola!

Today, I wan yarn with una about something wey dey very close to my heart - the New Africa we dey build together!

You know say, when I look around Nigeria today, I see so many young people wey dey innovate. From tech startups in Yaba, to fashion designers in Aba, to musicians wey dey take our Afrobeats to the whole world!

But make I tell una small secret - the reason why Africa go definitely shine, na because of US. Na because of you wey dey watch this video right now.

So today, I wan challenge you. What be that dream wey you don dey postpone? Start today!

Remember my three golden rules: Consistency, Learning, and Never forget where you come from!

Sisi Lola love una scatter! Nigeria to the world!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: GENERATE IMAGE WITH SDXL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_image() -> str:
    """Generate Sisi Lola character image."""
    print("\n" + "═" * 70)
    print("🎨 STEP 1: GENERATING SISI LOLA IMAGE (SDXL)")
    print("═" * 70)
    
    prompt = """Beautiful young Nigerian woman, professional content creator,
    natural afro hair, warm smile, colorful African print outfit,
    professional studio lighting, clean background, portrait photo,
    confident pose, high quality, photorealistic, 4k"""
    
    try:
        print("🔄 Generating image...")
        output = replicate.run(
            "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
            input={
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted, text, watermark",
                "width": 768,
                "height": 768,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "seed": SISI_LOLA_SEED
            }
        )
        
        image_url = str(list(output)[0])
        print(f"✅ Image generated!")
        print(f"🔗 URL: {image_url[:60]}...")
        return image_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: GENERATE VOICE WITH BARK/PARLER
# ═══════════════════════════════════════════════════════════════════════════════

def generate_voice(text: str) -> str:
    """Generate voice using Kokoro TTS (working model)."""
    print("\n" + "═" * 70)
    print("🎤 STEP 2: GENERATING VOICE (KOKORO-TTS)")
    print("═" * 70)
    
    print(f"📝 Script: {text[:100]}...")
    
    try:
        print("🔄 Generating voice with Kokoro...")
        
        # Use Kokoro TTS (confirmed working)
        output = replicate.run(
            "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13",
            input={
                "text": text,
                "voice": "af_bella"  # Female voice
            }
        )
        
        audio_url = str(output)
        print(f"✅ Voice generated!")
        print(f"🔗 URL: {audio_url[:60]}...")
        return audio_url
        
    except Exception as e:
        print(f"❌ Kokoro TTS failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: CREATE TALKING VIDEO WITH WAV2LIP
# ═══════════════════════════════════════════════════════════════════════════════

def create_talking_video(image_url: str, audio_url: str) -> str:
    """Create talking head video using Wav2Lip."""
    print("\n" + "═" * 70)
    print("🎬 STEP 3: CREATING TALKING VIDEO (WAV2LIP)")
    print("═" * 70)
    
    print(f"🖼️ Image: {image_url[:50]}...")
    print(f"🔊 Audio: {audio_url[:50]}...")
    
    try:
        print("🔄 Creating lipsync video... (this may take 1-2 minutes)")
        
        output = replicate.run(
            "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
            input={
                "face": image_url,
                "audio": audio_url,
                "pads": "0 10 0 0",
                "smooth": True,
                "fps": 25,
                "resize_factor": 1
            }
        )
        
        video_url = str(output)
        print(f"✅ Video created!")
        print(f"🔗 URL: {video_url[:60]}...")
        return video_url
        
    except Exception as e:
        print(f"❌ Wav2Lip error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: POST TO INSTAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def post_to_instagram(video_url: str) -> bool:
    """Post video to Instagram as Reel."""
    print("\n" + "═" * 70)
    print("📸 STEP 4: POSTING TO INSTAGRAM")
    print("═" * 70)
    
    if not INSTAGRAM_TOKEN:
        print("❌ Instagram token not found!")
        return False
    
    caption = """🇳🇬 The New Africa We Dey Build! 💚

How you dey, my beautiful people? 

Today I wan tell you say - no matter the wahala, we go ALWAYS rise! 

✨ Nigeria to the world!
💪 We are the future!

#SisiLola #NigeriaToTheWorld #NewAfrica #NaijaContent #AfricanCreator #Motivation

Follow for more gist! 💃"""
    
    print(f"📝 Caption: {caption[:50]}...")
    
    try:
        # Step 1: Create container
        print("\n📍 Creating Reel container...")
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
        
        if response.status_code != 200:
            error = response.json().get("error", {})
            print(f"❌ Container failed: {error.get('message', response.text[:200])}")
            return False
        
        container_id = response.json().get("id")
        print(f"   ✅ Container: {container_id}")
        
        # Wait for processing
        print("\n📍 Waiting for video processing...")
        for i in range(18):  # Up to 3 minutes
            time.sleep(10)
            print(f"   ⏳ Processing... ({(i+1)*10}s)")
            
            status_resp = requests.get(
                f"https://graph.facebook.com/v18.0/{container_id}",
                params={
                    "access_token": INSTAGRAM_TOKEN,
                    "fields": "status_code"
                }
            )
            
            if status_resp.status_code == 200:
                status = status_resp.json().get("status_code")
                if status == "FINISHED":
                    print("   ✅ Processing complete!")
                    break
                elif status == "ERROR":
                    print("   ❌ Processing error!")
                    return False
        
        # Step 2: Publish
        print("\n📍 Publishing Reel...")
        pub_resp = requests.post(
            f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            params={
                "access_token": INSTAGRAM_TOKEN,
                "creation_id": container_id
            },
            timeout=60
        )
        
        if pub_resp.status_code == 200:
            post_id = pub_resp.json().get("id")
            print(f"\n🎉 REEL PUBLISHED! ID: {post_id}")
            print("📱 Check @sisilolalive on Instagram!")
            return True
        else:
            error = pub_resp.json().get("error", {})
            print(f"❌ Publish failed: {error.get('message', pub_resp.text[:100])}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run_production(use_short_script=True):
    """Run the full Replicate-based production pipeline."""
    print("═" * 70)
    print("       SISI LOLA - REPLICATE VIDEO PRODUCTION")
    print("              🇳🇬 NO PLAY O! 🇳🇬")
    print("═" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
    
    script = SISI_LOLA_SCRIPT_SHORT.strip() if use_short_script else SISI_LOLA_SCRIPT_FULL.strip()
    print(f"\n📝 Script length: {len(script)} chars")
    
    results = {
        "image_url": None,
        "audio_url": None,
        "video_url": None,
        "instagram_posted": False
    }
    
    # Step 1: Generate Image
    image_url = generate_image()
    results["image_url"] = image_url
    
    if not image_url:
        print("\n❌ Failed to generate image. Stopping.")
        return results
    
    # Step 2: Generate Voice
    audio_url = generate_voice(script)
    results["audio_url"] = audio_url
    
    if not audio_url:
        print("\n❌ Failed to generate voice. Stopping.")
        return results
    
    # Step 3: Create Talking Video
    video_url = create_talking_video(image_url, audio_url)
    results["video_url"] = video_url
    
    if not video_url:
        print("\n❌ Failed to create video. Stopping.")
        return results
    
    # Step 4: Post to Instagram
    ig_success = post_to_instagram(video_url)
    results["instagram_posted"] = ig_success
    
    # Summary
    print("\n" + "═" * 70)
    print("                    PRODUCTION SUMMARY")
    print("═" * 70)
    print(f"🎨 Image: {'✅' if results['image_url'] else '❌'}")
    print(f"🎤 Voice: {'✅' if results['audio_url'] else '❌'}")
    print(f"🎬 Video: {'✅' if results['video_url'] else '❌'}")
    print(f"📸 Instagram: {'✅' if results['instagram_posted'] else '❌'}")
    
    if results["video_url"]:
        print(f"\n🔗 Video: {results['video_url']}")
    
    if results["instagram_posted"]:
        print("\n🎉 SUCCESS! Check @sisilolalive!")
    
    print("═" * 70)
    
    # Save results
    result_file = OUTPUT_DIR / f"replicate_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, "w") as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    # Use short script for testing (30 seconds)
    use_full = "--full" in sys.argv
    results = run_production(use_short_script=not use_full)
    
    if results["instagram_posted"]:
        sys.exit(0)
    elif results["video_url"]:
        print("\n⚠️ Video created but Instagram failed")
        sys.exit(1)
    else:
        sys.exit(2)
