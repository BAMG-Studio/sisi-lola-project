"""Generate Talking Sisi Lola Video with Wav2Lip - PRODUCTION READY"""
import subprocess
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Paths
VOICE_SAMPLE = "../../04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
AVATAR_IMAGE = "../../01_AVATAR_DNA/01_Reference_Sheets/SisiLola_Reference_Sheet_v01.png"
WAV2LIP_DIR = "../../wav2lip_workspace/Wav2Lip"
OUTPUT_DIR = "../../06_RENDER_OUTPUT/talking_videos"

def generate_talking_video(face_image, audio_file, output_file):
    """Generate talking video using Wav2Lip"""
    
    # Verify files exist
    if not os.path.exists(face_image):
        raise FileNotFoundError(f"Face image not found: {face_image}")
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    
    # Create output directory
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Wav2Lip command
    checkpoint = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip_gan.pth")
    
    cmd = [
        sys.executable,
        os.path.join(WAV2LIP_DIR, "inference.py"),
        "--checkpoint_path", checkpoint,
        "--face", face_image,
        "--audio", audio_file,
        "--outfile", output_file,
        "--fps", "25",
        "--pads", "0", "10", "0", "0",  # Top, bottom, left, right padding
        "--resize_factor", "1"
    ]
    
    print(f"  Running Wav2Lip...")
    print(f"  Face: {face_image}")
    print(f"  Audio: {audio_file}")
    print(f"  Output: {output_file}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WAV2LIP_DIR)
    
    if result.returncode != 0:
        print(f"✗ Wav2Lip failed:")
        print(result.stderr)
        raise RuntimeError("Wav2Lip generation failed")
    
    print(f"✓ Talking video generated: {output_file}")
    return output_file

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATE TALKING SISI LOLA VIDEO")
    print("=" * 70)
    
    # Check if Wav2Lip is set up
    if not os.path.exists(WAV2LIP_DIR):
        print("\n✗ Wav2Lip not found. Run setup_wav2lip.py first:")
        print("  python setup_wav2lip.py")
        sys.exit(1)
    
    # Generate video
    print("\n[1/2] Generating talking video with Wav2Lip...")
    output_file = os.path.join(OUTPUT_DIR, "sisi_lola_talking_001.mp4")
    
    try:
        video_path = generate_talking_video(AVATAR_IMAGE, VOICE_SAMPLE, output_file)
        
        print("\n[2/2] ✓ COMPLETE")
        print(f"\nTalking video created: {video_path}")
        print("\nNext: Upload to YouTube with upload script")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Wav2Lip is installed: python setup_wav2lip.py")
        print("2. Check GPU availability: nvidia-smi")
        print("3. Verify file paths exist")
        sys.exit(1)
