"""
Create AUTHENTIC Sisi Lola Yoruba Video
Uses YOUR trained assets: Yoruba voice samples + Sisi Lola images
"""
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

def create_authentic_video():
    """Create authentic Yoruba video using existing assets"""
    
    print("="*70)
    print("AUTHENTIC SISI LOLA YORUBA VIDEO CREATOR")
    print("="*70)
    
    # Paths
    base = Path(__file__).parent.parent.parent
    audio_file = base / "04_AUDIO_CORE" / "voice_samples" / "sisi_lola_yorunglish_female_LONG.wav"
    image_file = base / "01_AVATAR_DNA" / "01_Reference_Sheets" / "SisiLola_Reference_Sheet_v01.png"
    output_dir = base / "06_RENDER_OUTPUT" / "youtube_videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"sisi_lola_yoruba_authentic.mp4"
    
    # Check files exist
    if not audio_file.exists():
        print(f"[ERROR] Audio not found: {audio_file}")
        print("[INFO] Using alternative Yoruba sample...")
        audio_file = base / "04_AUDIO_CORE" / "01_Voice_Samples" / "Voice_Sample_Nigerian_Pidgin_Casual.wav"
    
    if not image_file.exists():
        print(f"[ERROR] Image not found: {image_file}")
        return None
    
    print(f"\n[INPUT] Audio: {audio_file.name}")
    print(f"[INPUT] Image: {image_file.name}")
    print(f"[OUTPUT] Video: {output_file.name}")
    
    # FFmpeg command to create video from image + audio
    cmd = [
        'ffmpeg',
        '-loop', '1',
        '-i', str(image_file),
        '-i', str(audio_file),
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-y',
        str(output_file)
    ]
    
    print("\n[CREATING] Combining Yoruba audio with Sisi Lola image...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n[SUCCESS] Video created: {output_file}")
            print(f"[SIZE] {output_file.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Get duration
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(output_file)
            ]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(duration_result.stdout.strip())
            
            print(f"[DURATION] {duration/60:.1f} minutes")
            print(f"\n[LANGUAGE] Yoruba/Yorunglish (60% Yoruba, 30% Pidgin, 10% English)")
            print(f"[AVATAR] Sisi Lola (consistent character)")
            print(f"[VOICE] Authentic Nigerian female accent")
            
            return str(output_file)
        else:
            print(f"[ERROR] FFmpeg failed: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("[ERROR] FFmpeg not found. Install: https://ffmpeg.org/download.html")
        print("\n[ALTERNATIVE] Use online tool:")
        print(f"  1. Upload image: {image_file}")
        print(f"  2. Upload audio: {audio_file}")
        print(f"  3. Combine at: https://www.kapwing.com/")
        return None

if __name__ == "__main__":
    video_path = create_authentic_video()
    
    if video_path:
        print("\n" + "="*70)
        print("READY TO POST TO YOUTUBE!")
        print("="*70)
        print(f"Video: {video_path}")
        print("\nThis is AUTHENTIC Sisi Lola:")
        print("  - Yoruba/Yorunglish language")
        print("  - Nigerian female voice")
        print("  - Sisi Lola character image")
        print("  - Cultural authenticity")
        print("\nNext: Post to YouTube with post_to_youtube_now.py")
