"""Generate Talking Video with Wav2Lip - PRODUCTION"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("WAV2LIP TALKING VIDEO GENERATION")
print("=" * 70)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Paths
wav2lip_dir = PROJECT_ROOT / "wav2lip_workspace" / "Wav2Lip"
checkpoint = wav2lip_dir / "checkpoints" / "wav2lip_gan.pth"
face_image = PROJECT_ROOT / "01_AVATAR_DNA" / "sisi_lola_heygen_frame.jpg"
VOICE_DIR = PROJECT_ROOT / "04_AUDIO_CORE" / "voice_samples"
VOICE_FILENAME = "sisi_lola_yorunglish_female_LONG.wav"
audio_file = VOICE_DIR / VOICE_FILENAME
output_file = PROJECT_ROOT / "06_RENDER_OUTPUT" / "talking_videos" / "sisi_wav2lip_001.mp4"
FFMPEG_FALLBACK = Path(
    r"C:\Users\POK28\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
)


def require_asset(asset_path: Path, label: str) -> None:
    """Ensure the locked asset exists before generation."""
    if not asset_path.exists():
        print(f"[ERROR] {label} not found: {asset_path}")
        sys.exit(1)
    print(f"[LOCKED] {label}: {asset_path}")


print("\n[VALIDATION]")
require_asset(audio_file, "Voice source")
require_asset(face_image, "Avatar frame")
require_asset(checkpoint, "Wav2Lip checkpoint")

def ensure_ffmpeg() -> None:
    """Guarantee ffmpeg exists on PATH so Wav2Lip can mux audio/video."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"[LOCKED] ffmpeg binary: {ffmpeg_path}")
        return

    if FFMPEG_FALLBACK.exists():
        os.environ["PATH"] = str(FFMPEG_FALLBACK.parent) + os.pathsep + os.environ["PATH"]
        print(f"[LOCKED] ffmpeg binary: {FFMPEG_FALLBACK}")
        return

    print("[ERROR] FFmpeg not found. Install it or update FFMPEG_FALLBACK.")
    sys.exit(1)


ensure_ffmpeg()

# Create output dir
output_file.parent.mkdir(parents=True, exist_ok=True)

print(f"\nOutput: {output_file}")
print("\nGenerating talking video (this takes 2-3 minutes)...\n")

# Run Wav2Lip
cmd = [
    "py",
    "-3.10",
    str(wav2lip_dir / "inference.py"),
    "--checkpoint_path",
    str(checkpoint),
    "--face",
    str(face_image),
    "--audio",
    str(audio_file),
    "--outfile",
    str(output_file),
    "--fps",
    "25",
    "--pads",
    "0",
    "10",
    "0",
    "0",
    "--resize_factor",
    "2",
]

result = subprocess.run(cmd, cwd=str(wav2lip_dir), capture_output=True, text=True)

if result.returncode == 0:
    print("\n" + "=" * 70)
    print("SUCCESS! TALKING VIDEO CREATED")
    print("=" * 70)
    print(f"\nVideo: {output_file}")
    print("Duration: ~6.6 minutes")
    print("Features: Sisi Lola + Yoruba voice + LIP-SYNC")
    print("\nNext: Upload to YouTube")
else:
    print(f"\nError: {result.stderr}")
    sys.exit(1)
