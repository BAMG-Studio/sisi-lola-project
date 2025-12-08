"""Setup Wav2Lip with Python 3.10 - Production Ready"""
import subprocess
import sys
import os
from pathlib import Path

print("=" * 70)
print("WAV2LIP SETUP - PYTHON 3.10")
print("=" * 70)

# Use Python 3.10
PY310 = "py -3.10"

# Install dependencies
print("\n[1/4] Installing dependencies...")
deps = [
    "librosa==0.9.1",
    "numpy==1.23.5",
    "opencv-python",
    "pillow",
    "scipy",
    "tqdm",
    "numba",
    "torch==2.0.1",
    "torchvision==0.15.2"
]

for dep in deps:
    print(f"  Installing {dep}...")
    subprocess.run(f"{PY310} -m pip install {dep} -q", shell=True, check=True)

print("[OK] Dependencies installed")

# Clone Wav2Lip
print("\n[2/4] Cloning Wav2Lip...")
wav2lip_dir = Path("../../wav2lip_workspace")
wav2lip_dir.mkdir(exist_ok=True)

if not (wav2lip_dir / "Wav2Lip").exists():
    subprocess.run([
        "git", "clone",
        "https://github.com/Rudrabha/Wav2Lip.git",
        str(wav2lip_dir / "Wav2Lip")
    ], check=True)
    print("[OK] Wav2Lip cloned")
else:
    print("[OK] Wav2Lip exists")

# Download model
print("\n[3/4] Downloading model checkpoint (1.5GB)...")
checkpoint_dir = wav2lip_dir / "Wav2Lip" / "checkpoints"
checkpoint_dir.mkdir(exist_ok=True)
checkpoint_file = checkpoint_dir / "wav2lip_gan.pth"

if not checkpoint_file.exists():
    print("  Installing gdown...")
    subprocess.run(f"{PY310} -m pip install gdown -q", shell=True, check=True)
    print("  Downloading model (1.5GB)...")
    subprocess.run([
        "py", "-3.10", "-m", "gdown",
        "https://drive.google.com/uc?id=1fQtBSYEyuai9MjBOF8j7zZ0DYFHj0gfC",
        "-O", str(checkpoint_file)
    ], check=True)
    print("[OK] Model downloaded")
else:
    print("[OK] Model exists")

# Verify
print("\n[4/4] Verifying setup...")
if checkpoint_file.exists():
    print("[OK] Setup complete!")
    print(f"\nWav2Lip: {wav2lip_dir / 'Wav2Lip'}")
    print(f"Model: {checkpoint_file}")
    print("\nReady for production!")
else:
    print("[ERROR] Setup failed")
    sys.exit(1)
