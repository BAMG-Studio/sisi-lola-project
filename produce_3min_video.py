#!/usr/bin/env python3
# Use: sisi-lola-brain-mistral (Mistral-7B LoRA)
# Fallback: mistralai/Mistral-7B-Instruct-v0.3 via HF Inference API
"""
═══════════════════════════════════════════════════════════════════════════════
              SISI LOLA 3-MINUTE VIDEO PRODUCTION
═══════════════════════════════════════════════════════════════════════════════
Creates a full 3-minute video with:
1. Kokoro TTS voice generation
2. SDXL image generation  
3. FFmpeg video creation (image + audio)
4. Ready for Instagram posting
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import requests
import subprocess
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path("C:/Users/POK28/Dropbox/Sisi_Lola")
OUTPUT_DIR = PROJECT_ROOT / "pipeline_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load env
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "sisi_lola_api" / ".env")

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

import replicate

# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA 3-MINUTE SCRIPT
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT = """
How you dey, my beautiful people! Welcome back to another episode with your girl, Sisi Lola!

Today, we dey talk about something wey dey touch all of us. Nigeria, our beloved country. 
You know say, no matter where we dey for this world, that green white green blood dey flow for our veins.

Make I tell you something. When I see Nigerians dey shine for abroad, my heart dey swell with pride o!
From Wizkid to Burna Boy, from Ngozi Okonjo-Iweala to Chimamanda, we dey show the world say na we get am!

But you know wetin dey sweet me pass? Na the everyday Nigerian hustle. 
That mama wey dey sell akara for morning, that okada man wey dey navigate Lagos traffic,
that student wey dey read with candle light because NEPA no gree. Una be the real MVPs!

Now, make we yarn about tech. Nigeria don become Silicon Savannah! 
Paystack, Flutterwave, Andela - all these companies wey dey change the game.
Young Nigerians dey code, dey innovate, dey create solutions for Africa problems.

And food? Omo, no be play o! Jollof rice na our national treasure.
No Ghana, no Senegal, nobody fit come close to Nigerian jollof. I said what I said!
Add small dodo, some fried plantain, maybe chicken or fish - that na heaven for plate!

But make I keep am real with una. We still get work to do.
Light dey fail, fuel dey scarce, things no easy. But you know wetin?
That Nigerian spirit, that never-give-up attitude, that's what makes us special.

So whether you dey Lagos, dey Abuja, dey Port Harcourt, or even dey japa abroad,
remember say you carry Nigeria for your chest. Represent am well!

Before I go, make I tell una say I love una die! 
Drop comment, tell me where you dey, what you love about Naija.
Share this video, follow for more vibes, and remember - Sisi Lola dey always dey for una!

Na we dey, na we go always dey! Until next time, stay blessed, stay winning!
Bye bye my people! Muah!
"""

def generate_voice():
    """Generate voice using Kokoro TTS."""
    print("\n🎤 STEP 1: Generating Voice (Kokoro TTS)...")
    print(f"   Script length: {len(SCRIPT)} characters")
    
    try:
        output = replicate.run(
            "jaaari/kokoro-82m:dfdf537ba482b029e0a761699e6f55e9162cfd159270bfe0e44857caa5f275a6",
            input={
                "text": SCRIPT,
                "speed": 1.0,
                "voice": "af_bella"
            }
        )
        
        audio_url = str(output)
        print(f"   ✅ Voice generated!")
        print(f"   URL: {audio_url[:80]}...")
        
        # Download
        audio_path = OUTPUT_DIR / "sisi_lola_voice.wav"
        print(f"   📥 Downloading to {audio_path.name}...")
        
        response = requests.get(audio_url, timeout=120)
        response.raise_for_status()
        
        with open(audio_path, "wb") as f:
            f.write(response.content)
        
        file_size = audio_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Audio saved! Size: {file_size:.2f} MB")
        
        return audio_path
        
    except Exception as e:
        print(f"   ❌ Voice generation failed: {e}")
        return None


def generate_image():
    """Generate image using SDXL."""
    print("\n🎨 STEP 2: Generating Image (SDXL)...")
    
    prompt = """Beautiful confident Nigerian woman content creator named Sisi Lola, 
    professional studio setting with ring light, 
    colorful traditional African fashion ankara dress with green and white Nigerian flag patterns, 
    warm genuine smile, speaking directly to camera, 
    Lagos cityscape visible through modern window behind her,
    natural curly afro hair styled beautifully,
    high quality portrait, 4k, cinematic lighting, social media influencer aesthetic"""
    
    try:
        output = replicate.run(
            "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
            input={
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted, multiple people, text, watermark, ugly, deformed",
                "width": 1080,
                "height": 1920,
                "num_outputs": 1,
                "guidance_scale": 7.5
            }
        )
        
        image_url = str(list(output)[0])
        print(f"   ✅ Image generated!")
        print(f"   URL: {image_url[:80]}...")
        
        # Download
        image_path = OUTPUT_DIR / "sisi_lola_image.png"
        print(f"   📥 Downloading to {image_path.name}...")
        
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        with open(image_path, "wb") as f:
            f.write(response.content)
        
        file_size = image_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Image saved! Size: {file_size:.2f} MB")
        
        return image_path
        
    except Exception as e:
        print(f"   ❌ Image generation failed: {e}")
        return None


def create_video(audio_path: Path, image_path: Path):
    """Create video from image + audio using ffmpeg."""
    print("\n🎬 STEP 3: Creating Video (FFmpeg)...")
    
    video_path = OUTPUT_DIR / "sisi_lola_video.mp4"
    
    # Get audio duration
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
        ], capture_output=True, text=True, timeout=30)
        duration = float(result.stdout.strip())
        print(f"   Audio duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    except:
        duration = 180  # Default 3 minutes
        print(f"   Using default duration: {duration}s")
    
    # Create video with Ken Burns effect (slow zoom)
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
        "-vf", f"scale=1080:1920,zoompan=z='min(zoom+0.0005,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*30)}:s=1080x1920:fps=30",
        "-shortest",
        "-t", str(duration),
        str(video_path)
    ]
    
    print(f"   🔧 Running FFmpeg...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and video_path.exists():
            file_size = video_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Video created! Size: {file_size:.2f} MB")
            return video_path
        else:
            print(f"   ❌ FFmpeg error: {result.stderr[:500]}")
            
            # Fallback: simpler command
            print("   🔄 Trying simpler video creation...")
            cmd_simple = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-pix_fmt", "yuv420p",
                "-shortest",
                str(video_path)
            ]
            result = subprocess.run(cmd_simple, capture_output=True, text=True, timeout=300)
            
            if video_path.exists():
                file_size = video_path.stat().st_size / (1024 * 1024)
                print(f"   ✅ Video created (simple)! Size: {file_size:.2f} MB")
                return video_path
            
            return None
            
    except subprocess.TimeoutExpired:
        print("   ❌ FFmpeg timed out")
        return None
    except Exception as e:
        print(f"   ❌ Video creation failed: {e}")
        return None


def main():
    """Main production pipeline."""
    print("═" * 70)
    print("         SISI LOLA 3-MINUTE VIDEO PRODUCTION")
    print("═" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
    
    # Step 1: Voice
    audio_path = generate_voice()
    if not audio_path:
        print("\n❌ FAILED: Could not generate voice")
        return None
    
    # Step 2: Image
    image_path = generate_image()
    if not image_path:
        print("\n❌ FAILED: Could not generate image")
        return None
    
    # Step 3: Video
    video_path = create_video(audio_path, image_path)
    
    # Summary
    print("\n" + "═" * 70)
    print("                    PRODUCTION SUMMARY")
    print("═" * 70)
    print(f"✅ Voice: {audio_path}")
    print(f"✅ Image: {image_path}")
    print(f"{'✅' if video_path else '❌'} Video: {video_path or 'FAILED'}")
    print("═" * 70)
    
    if video_path:
        print("\n🎉 SUCCESS! Video ready for Instagram!")
        print(f"📁 File: {video_path}")
        print("\n📱 To post to Instagram, run:")
        print("   python test_instagram_posting.py")
    
    return video_path


if __name__ == "__main__":
    main()
