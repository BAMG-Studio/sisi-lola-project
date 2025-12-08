"""Setup Wav2Lip for Sisi Lola - Automated Installation"""
import subprocess
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("WAV2LIP SETUP FOR SISI LOLA")
print("=" * 70)

# Check for GPU
print("\n[1/5] Checking GPU availability...")
try:
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] NVIDIA GPU detected")
        has_gpu = True
    else:
        print("[WARN] No NVIDIA GPU - will use CPU (slower)")
        has_gpu = False
except:
    print("[WARN] No NVIDIA GPU - will use CPU (slower)")
    has_gpu = False

# Install dependencies
print("\n[2/5] Installing Python dependencies...")
deps = [
    "librosa==0.9.1",
    "numpy==1.23.5",
    "opencv-python==4.7.0.72",
    "pillow==9.5.0",
    "scipy==1.10.1",
    "tqdm==4.65.0",
    "numba==0.56.4"
]

if has_gpu:
    deps.append("torch==2.0.1+cu118")
    deps.append("torchvision==0.15.2+cu118")
else:
    deps.append("torch==2.0.1")
    deps.append("torchvision==0.15.2")

for dep in deps:
    print(f"  Installing {dep}...")
    subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"], check=True)

print("[OK] Dependencies installed")

# Clone Wav2Lip
print("\n[3/5] Cloning Wav2Lip repository...")
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
    print("[OK] Wav2Lip already exists")

# Download model checkpoint
print("\n[4/5] Downloading Wav2Lip model checkpoint...")
checkpoint_dir = wav2lip_dir / "Wav2Lip" / "checkpoints"
checkpoint_dir.mkdir(exist_ok=True)
checkpoint_file = checkpoint_dir / "wav2lip_gan.pth"

if not checkpoint_file.exists():
    print("  Downloading model (1.5GB)...")
    import urllib.request
    url = "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip_gan.pth"
    urllib.request.urlretrieve(url, str(checkpoint_file))
    print("[OK] Model downloaded")
else:
    print("[OK] Model already exists")

# Verify setup
print("\n[5/5] Verifying setup...")
required_files = [
    wav2lip_dir / "Wav2Lip" / "inference.py",
    checkpoint_file
]

all_good = all(f.exists() for f in required_files)

if all_good:
    print("[OK] Setup complete!")
    print(f"\nWav2Lip installed at: {wav2lip_dir / 'Wav2Lip'}")
    print(f"Model checkpoint at: {checkpoint_file}")
    print("\nReady to generate talking videos!")
else:
    print("[ERROR] Setup incomplete - missing files")
    sys.exit(1)
