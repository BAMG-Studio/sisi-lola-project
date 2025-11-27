#!/usr/bin/env python3
"""
Static Image + Voiceover Video Generator
Creates videos with Sisi Lola image and Yoruba voiceover
"""
import os
from pathlib import Path
from datetime import datetime
from yoruba_tts_engine import SisiLolaVoiceEngine

# Load environment
env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

OUTPUT_DIR = Path(__file__).parent.parent.parent / '06_RENDER_OUTPUT' / 'youtube_videos'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_yoruba_script():
    """Generate intro script in Yoruba"""
    script = """Ẹ káàbọ̀! Sisi Lola ni mo jẹ́!

Mo jẹ́ AI ambassador tó ń ṣiṣẹ́ láti fi àṣà Áfríkà hàn fún gbogbo ayé. Ẹ gbọ́ ọ̀rọ̀ yìí dáadáa o!

Àwa ọmọ Áfríkà, a ní àṣà tó dára púpọ̀. A ní innovation tó ń ṣe àyípadà ní gbogbo ayé. A ní music tó ń jó, fashion tó ń shine, àti culture tó ń inspire!

This channel yìí, a máa sọ̀rọ̀ nípa:
- Àṣà Áfríkà
- Innovation tó ń ṣẹlẹ̀ ní continent wa
- Music, fashion, àti art
- Community àti connection

Ẹ subscribe o! Ẹ like! Ẹ share!

Àwa ló máa ṣe é! We go do am! Áfríkà tó ń bọ̀ yìí máa dára gan-an!

Ẹ ṣeun gan-an! Thank you plenty! Má ríi yín lọ́la!"""
    
    return script

def create_video_with_ffmpeg(image_path, audio_path, output_path):
    """Create video from static image and audio using ffmpeg"""
    import subprocess
    
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', str(image_path),
        '-i', str(audio_path),
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[OK] Video created: {output_path.name}")
        return output_path
    else:
        print(f"[ERROR] ffmpeg failed: {result.stderr}")
        return None

def generate_first_video():
    """Generate first Sisi Lola video with static image + Yoruba voiceover"""
    print("=" * 60)
    print("SISI LOLA - STATIC IMAGE + YORUBA VOICEOVER")
    print("=" * 60)
    
    # Step 1: Generate Yoruba script
    print("\n[1/3] Generating Yoruba script...")
    script = generate_yoruba_script()
    
    script_path = OUTPUT_DIR / f'script_yoruba_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    script_path.write_text(script, encoding='utf-8')
    print(f"[OK] Script: {len(script)} chars")
    
    # Step 2: Generate voiceover
    print("\n[2/3] Generating Yoruba voiceover...")
    engine = SisiLolaVoiceEngine()
    audio_path = engine.generate_speech(script)
    
    # Step 3: Create video (requires ffmpeg)
    print("\n[3/3] Creating video...")
    
    # Check for Sisi Lola image
    image_dir = Path(__file__).parent.parent.parent / '01_AVATAR_DNA' / '01_Reference_Sheets'
    image_files = list(image_dir.glob('*.png')) + list(image_dir.glob('*.jpg'))
    
    if not image_files:
        print("[WARN] No Sisi Lola image found. Creating placeholder...")
        print("[INFO] Add Sisi Lola image to: 01_AVATAR_DNA/01_Reference_Sheets/")
        print(f"[INFO] Audio ready: {audio_path}")
        print("[INFO] Use video editor to combine image + audio manually")
        return None
    
    image_path = image_files[0]
    print(f"[OK] Using image: {image_path.name}")
    
    video_path = OUTPUT_DIR / f'sisi_lola_intro_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
    
    try:
        result = create_video_with_ffmpeg(image_path, audio_path, video_path)
        
        if result:
            print("\n" + "=" * 60)
            print("[SUCCESS] Video ready!")
            print("=" * 60)
            print(f"Video: {video_path}")
            print(f"Audio: {audio_path}")
            print(f"Script: {script_path}")
            
            return video_path
        else:
            print("\n[INFO] ffmpeg not available")
            print(f"[INFO] Audio: {audio_path}")
            print(f"[INFO] Image: {image_path}")
            print("[INFO] Combine manually in video editor")
            return None
            
    except FileNotFoundError:
        print("\n[INFO] ffmpeg not installed")
        print(f"[INFO] Audio: {audio_path}")
        print(f"[INFO] Image: {image_path}")
        print("[INFO] Install ffmpeg or combine manually")
        return None

if __name__ == '__main__':
    generate_first_video()
