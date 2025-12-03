import os
import sys
import random
from pathlib import Path
from moviepy import AudioFileClip, ImageClip

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

AUDIO_DIR = PROJECT_ROOT / "04_AUDIO_CORE" / "01_Voice_Samples"
IMAGE_DIR = PROJECT_ROOT / "01_AVATAR_DNA" / "01_Reference_Sheets"
OUTPUT_DIR = PROJECT_ROOT / "03_MEDIA_ASSETS" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_static_videos():
    print("🎬 Starting Static Video Generation...")
    
    audio_files = list(AUDIO_DIR.glob("*.wav"))
    image_files = list(IMAGE_DIR.glob("*.png"))
    
    if not audio_files:
        print("❌ No audio files found.")
        return
    if not image_files:
        print("❌ No image files found.")
        return
        
    print(f"Found {len(audio_files)} audio files and {len(image_files)} images.")
    
    for i, audio_path in enumerate(audio_files):
        try:
            # Pick a random image (or sequential)
            image_path = image_files[i % len(image_files)]
            
            output_filename = f"static_video_{audio_path.stem}.mp4"
            output_path = OUTPUT_DIR / output_filename
            
            if output_path.exists():
                print(f"⏩ Skipping (Exists): {output_filename}")
                continue
                
            print(f"Processing: {output_filename}")
            print(f"  Audio: {audio_path.name}")
            print(f"  Image: {image_path.name}")
            
            # Create clips
            audio_clip = AudioFileClip(str(audio_path))
            image_clip = ImageClip(str(image_path)).with_duration(audio_clip.duration)
            
            # Set FPS
            image_clip.fps = 24
            
            # Write file
            # Use 'libx264' for video and 'aac' for audio
            image_clip = image_clip.with_audio(audio_clip)
            image_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            
            print(f"✅ Created: {output_path}")
            
        except Exception as e:
            print(f"❌ Error creating video {i}: {e}")

    print("\n🏁 Static Video Generation Complete.")

if __name__ == "__main__":
    generate_static_videos()
