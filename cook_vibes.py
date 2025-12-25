"""
SISI LOLA VIDEO COOKER
=======================
Combines Sisi Lola's voiceovers (.mp3) with a static avatar image
to create social-media-ready videos (.mp4).
"""

import os
import subprocess
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
PRODUCED_DIR = PROJECT_ROOT / "03_MEDIA_ASSETS" / "produced_vibes"
AVATAR_IMAGE = PROJECT_ROOT / "01_AVATAR_DNA" / "sisi lola 3.png"
OUTPUT_DIR = PRODUCED_DIR

def cook_video(audio_path: Path, output_path: Path):
    """Uses ffmpeg to create a static image video"""
    if not audio_path.exists():
        print(f"❌ Audio not found: {audio_path}")
        return False
        
    if not AVATAR_IMAGE.exists():
        print(f"❌ Avatar image not found: {AVATAR_IMAGE}")
        return False

    print(f"🍳 Cooking: {audio_path.name} -> {output_path.name}...")
    
    # FFmpeg command:
    # -loop 1: Loop the image
    # -i image: Input image
    # -i audio: Input audio
    # -c:v libx264: Video codec
    # -tune stillimage: Optimize for static image
    # -c:a aac: Audio codec
    # -b:a 192k: Audio bitrate
    # -pix_fmt yuv420p: Pixel format for compatibility
    # -shortest: Finish when audio ends
    # -vf scale: Scale to 1080x1920 (Vertical)
    
    # FFmpeg command optimized for Reels compatibility
    # -r 30: fixed framerate
    # -g 60: GOP size for smooth streaming
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "30", "-i", str(AVATAR_IMAGE), # Loop image for at least 30s
        "-i", str(audio_path),
        "-filter_complex", "[0:v]scale=1920:3413,zoompan=z='min(zoom+0.0005,1.2)':d=1:s=1080x1920:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',format=yuv420p[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-profile:v", "main", "-level:v", "4.0",
        "-r", "30", "-g", "60", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Ready! {output_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Error: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("❌ FFmpeg not found! Please install ffmpeg on your system.")
        return False

def main():
    print("\n" + "="*50)
    print("SISI LOLA: COOKING VIDEOS FOR SOCIAL MEDIA")
    print("="*50 + "\n")
    
    # Find all terbaru (latest) mp3 files
    mp3_files = list(PRODUCED_DIR.glob("VIBE*_20251225.mp3"))
    if not mp3_files:
        # Fallback to any VIBE mp3
        mp3_files = list(PRODUCED_DIR.glob("VIBE*.mp3"))
        
    if not mp3_files:
        print("❌ No produced audio files found!")
        return

    for audio_path in mp3_files:
        # Get the vibe_id (e.g., VIBE001)
        vibe_id = audio_path.name.split('_')[0]
        output_path = PRODUCED_DIR / f"{vibe_id}.mp4"
        
        cook_video(audio_path, output_path)

    print("\n" + "="*50)
    print("Cooking Complete! Now you can run fire_immediate_posts.py")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
