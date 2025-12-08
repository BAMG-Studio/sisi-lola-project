"""PRODUCTION PIPELINE - LOCKED SOURCES"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# LOCKED SOURCES - DO NOT CHANGE
VOICE_SOURCE = PROJECT_ROOT / "04_AUDIO_CORE" / "voice_samples" / "sisi_lola_yorunglish_female_LONG.wav"
AVATAR_FRAME = PROJECT_ROOT / "01_AVATAR_DNA" / "sisi_lola_heygen_frame.jpg"
WAV2LIP_DIR = PROJECT_ROOT / "wav2lip_workspace" / "Wav2Lip"
CHECKPOINT = WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"
OUTPUT_DIR = PROJECT_ROOT / "06_RENDER_OUTPUT" / "talking_videos"
FFMPEG_FALLBACK = Path(
    r"C:\Users\POK28\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
)


def require_asset(asset_path: Path, label: str) -> None:
    if not asset_path.exists():
        print(f"[ERROR] {label} missing: {asset_path}")
        sys.exit(1)
    print(f"[LOCKED] {label}: {asset_path}")


def ensure_ffmpeg() -> None:
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


print("=" * 70)
print("PRODUCTION PIPELINE - LOCKED SOURCES")
print("=" * 70)

print("\n[VALIDATION]")
require_asset(VOICE_SOURCE, "Voice source")
require_asset(AVATAR_FRAME, "Avatar frame")
require_asset(CHECKPOINT, "Wav2Lip checkpoint")
ensure_ffmpeg()

print("\n[GENERATION]")
output_file = OUTPUT_DIR / f"sisi_production_{int(time.time())}.mp4"
output_file.parent.mkdir(parents=True, exist_ok=True)

print(f"Output: {output_file}")
print("Generating (2-3 minutes)...\n")

cmd = [
    "py",
    "-3.10",
    str(WAV2LIP_DIR / "inference.py"),
    "--checkpoint_path",
    str(CHECKPOINT),
    "--face",
    str(AVATAR_FRAME),
    "--audio",
    str(VOICE_SOURCE),
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

result = subprocess.run(cmd, cwd=str(WAV2LIP_DIR), capture_output=True, text=True)

if result.returncode == 0:
    print("\n[OK] Video generated")
    print(f"Location: {output_file}")
else:
    print("\n[ERROR] Wav2Lip failed")
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
