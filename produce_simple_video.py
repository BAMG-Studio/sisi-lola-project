#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SISI LOLA - SIMPLE VIDEO PRODUCER
═══════════════════════════════════════════════════════════════════════════════
        Creates video with image + audio (no complex lipsync)
═══════════════════════════════════════════════════════════════════════════════

Pipeline:
1. Generate image with SDXL
2. Generate voice with Kokoro TTS  
3. Combine image + audio = video (with zoom effect)
4. Post to Instagram as Reel

SIMPLE BUT EFFECTIVE!
"""

import os
import sys
import json
import time
import requests
import subprocess
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
# SISI LOLA SCRIPT
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_30SEC = """
How you dey, my beautiful people! Welcome to Sisi Lola live!
Today I wan tell you say, the New Africa wey we dey build, na our future!
No matter the wahala, no matter the challenge, we go always rise!
Nigeria to the world! Sisi Lola love una scatter!
"""

SCRIPT_3MIN = """
How you dey, my beautiful people! Welcome to another episode with your girl, Sisi Lola!

Today, I wan yarn with una about something wey dey very close to my heart - the New Africa we dey build together!

You know say, when I look around Nigeria today, I see so many young people wey dey innovate. From tech startups in Yaba, to fashion designers in Aba, to musicians wey dey take our Afrobeats to the whole world!

But make I tell una small secret - the reason why Africa go definitely shine, na because of US. Na because of you wey dey watch this video right now.

See ehn, I know say things no easy sometimes. Light dey take, fuel dey expensive, network dey misbehave. But my people, na these challenges dey make us strong!

So today, I wan challenge you. What be that dream wey you don dey postpone? Start today, even if na small small!

Remember my three golden rules: Consistency, Learning, and Never forget where you come from!

Alright my loves, make sure say you follow me for more gist and inspiration.

Sisi Lola love una scatter! Nigeria to the world! Bye bye now!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: GENERATE IMAGE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_image() -> str:
    """Generate Sisi Lola character image."""
    print("\n" + "═" * 70)
    print("🎨 STEP 1: GENERATING SISI LOLA IMAGE")
    print("═" * 70)
    
    prompt = """Beautiful young Nigerian woman, professional content creator,
    natural afro hair, warm genuine smile, colorful African print blouse,
    professional studio lighting, solid dark purple background, 
    portrait photo, confident pose, looking at camera, high quality, 4k"""
    
    try:
        print("🔄 Generating image...")
        output = replicate.run(
            "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
            input={
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted, text, watermark, deformed",
                "width": 1024,
                "height": 1024,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "seed": SISI_LOLA_SEED
            }
        )
        
        image_url = str(list(output)[0])
        print(f"✅ Image generated!")
        print(f"🔗 {image_url[:70]}...")
        return image_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: GENERATE VOICE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_voice(text: str) -> str:
    """Generate voice using Kokoro TTS."""
    print("\n" + "═" * 70)
    print("🎤 STEP 2: GENERATING VOICE")
    print("═" * 70)
    
    print(f"📝 Script length: {len(text)} chars")
    
    try:
        print("🔄 Generating voice with Kokoro TTS...")
        
        output = replicate.run(
            "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13",
            input={
                "text": text,
                "voice": "af_bella"
            }
        )
        
        audio_url = str(output)
        print(f"✅ Voice generated!")
        print(f"🔗 {audio_url[:70]}...")
        return audio_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: CREATE VIDEO (Image + Audio)
# ═══════════════════════════════════════════════════════════════════════════════

def download_file(url: str, output_path: Path) -> bool:
    """Download file from URL."""
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"   Download error: {e}")
    return False


def create_video(image_url: str, audio_url: str) -> str:
    """Create video from image and audio using ffmpeg."""
    print("\n" + "═" * 70)
    print("🎬 STEP 3: CREATING VIDEO (FFMPEG)")
    print("═" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Download image
    image_path = OUTPUT_DIR / f"image_{timestamp}.png"
    print(f"📥 Downloading image...")
    if not download_file(image_url, image_path):
        print("❌ Failed to download image")
        return None
    print(f"   ✅ Image saved: {image_path}")
    
    # Download audio
    audio_path = OUTPUT_DIR / f"audio_{timestamp}.wav"
    print(f"📥 Downloading audio...")
    if not download_file(audio_url, audio_path):
        print("❌ Failed to download audio")
        return None
    print(f"   ✅ Audio saved: {audio_path}")
    
    # Create video with ffmpeg
    video_path = OUTPUT_DIR / f"sisi_lola_{timestamp}.mp4"
    
    print(f"🔄 Creating video with ffmpeg...")
    
    # FFmpeg command: image + audio with Ken Burns zoom effect
    # -t gets duration from audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(zoom+0.0005,1.3)':d=1:s=1080x1920",
        "-shortest",
        "-movflags", "+faststart",
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and video_path.exists():
            size_mb = video_path.stat().st_size / 1024 / 1024
            print(f"✅ Video created!")
            print(f"📁 Path: {video_path}")
            print(f"📊 Size: {size_mb:.2f} MB")
            return str(video_path)
        else:
            print(f"❌ FFmpeg error: {result.stderr[:300]}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timeout")
        return None
    except FileNotFoundError:
        print("❌ FFmpeg not found! Please install ffmpeg.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: UPLOAD VIDEO & POST TO INSTAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def upload_to_storage(video_path: str) -> str:
    """Upload video to a publicly accessible URL.
    
    For Instagram, we need a public URL. Options:
    1. Upload to Dropbox and get shared link
    2. Upload to S3/GCS
    3. Use a temporary hosting service
    """
    print("\n📤 Uploading video for Instagram...")
    
    # For now, we'll use the local file path
    # In production, this would upload to cloud storage
    
    # Try using tmpfiles.org (temporary file hosting)
    try:
        with open(video_path, 'rb') as f:
            response = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files={'file': f},
                timeout=120
            )
            
        if response.status_code == 200:
            data = response.json()
            # Convert tmpfiles URL to direct download
            url = data.get('data', {}).get('url', '')
            # tmpfiles.org returns URL like https://tmpfiles.org/123/file.mp4
            # Need to convert to https://tmpfiles.org/dl/123/file.mp4
            if 'tmpfiles.org/' in url:
                url = url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
            print(f"✅ Uploaded: {url}")
            return url
    except Exception as e:
        print(f"❌ Upload failed: {e}")
    
    return None


def post_to_instagram(video_url: str) -> bool:
    """Post video to Instagram as Reel."""
    print("\n" + "═" * 70)
    print("📸 STEP 4: POSTING TO INSTAGRAM")
    print("═" * 70)
    
    if not INSTAGRAM_TOKEN:
        print("❌ Instagram token not found!")
        return False
    
    if not video_url:
        print("❌ No video URL provided!")
        return False
    
    caption = """🇳🇬 The New Africa We Dey Build! 💚

How you dey, my beautiful people? 

Today I wan tell you say - no matter the wahala, we go ALWAYS rise! 

✨ Nigeria to the world!
💪 We are the future!

#SisiLola #NigeriaToTheWorld #NewAfrica #NaijaContent #AfricanCreator #Motivation #NigerianCreator

Follow for more gist! 💃"""
    
    print(f"🔗 Video URL: {video_url[:50]}...")
    
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
        for i in range(24):  # Up to 4 minutes
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

def run_production(use_3min=False):
    """Run the production pipeline."""
    print("═" * 70)
    print("        SISI LOLA - SIMPLE VIDEO PRODUCTION")
    print("              🇳🇬 NO PLAY O! 🇳🇬")
    print("═" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
    
    script = SCRIPT_3MIN.strip() if use_3min else SCRIPT_30SEC.strip()
    print(f"\n📝 Using {'3-minute' if use_3min else '30-second'} script ({len(script)} chars)")
    
    results = {
        "image_url": None,
        "audio_url": None,
        "video_path": None,
        "video_url": None,
        "instagram_posted": False
    }
    
    # Step 1: Generate Image
    image_url = generate_image()
    results["image_url"] = image_url
    if not image_url:
        print("\n❌ Failed at image generation")
        return results
    
    # Step 2: Generate Voice
    audio_url = generate_voice(script)
    results["audio_url"] = audio_url
    if not audio_url:
        print("\n❌ Failed at voice generation")
        return results
    
    # Step 3: Create Video
    video_path = create_video(image_url, audio_url)
    results["video_path"] = video_path
    if not video_path:
        print("\n❌ Failed at video creation")
        return results
    
    # Step 4: Upload and Post
    video_url = upload_to_storage(video_path)
    results["video_url"] = video_url
    
    if video_url:
        ig_success = post_to_instagram(video_url)
        results["instagram_posted"] = ig_success
    else:
        print("\n⚠️ Could not upload video - skipping Instagram")
    
    # Summary
    print("\n" + "═" * 70)
    print("                    PRODUCTION SUMMARY")
    print("═" * 70)
    print(f"🎨 Image: {'✅' if results['image_url'] else '❌'}")
    print(f"🎤 Voice: {'✅' if results['audio_url'] else '❌'}")
    print(f"🎬 Video: {'✅' if results['video_path'] else '❌'}")
    print(f"📤 Upload: {'✅' if results['video_url'] else '❌'}")
    print(f"📸 Instagram: {'✅' if results['instagram_posted'] else '❌'}")
    
    if results["video_path"]:
        print(f"\n📁 Local video: {results['video_path']}")
    if results["video_url"]:
        print(f"🔗 Video URL: {results['video_url']}")
    
    print("═" * 70)
    
    # Save results
    result_file = OUTPUT_DIR / f"production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, "w") as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    use_3min = "--3min" in sys.argv or "--full" in sys.argv
    results = run_production(use_3min=use_3min)
    
    if results["instagram_posted"]:
        print("\n✅ SUCCESS!")
        sys.exit(0)
    elif results["video_path"]:
        print("\n⚠️ Video created locally but Instagram posting failed")
        sys.exit(1)
    else:
        sys.exit(2)
