"""Download Wav2Lip Model - Multiple Methods"""
import os
import sys
import subprocess
from pathlib import Path
import requests

checkpoint_file = Path("../../wav2lip_workspace/Wav2Lip/checkpoints/wav2lip_gan.pth")
checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

print("Downloading Wav2Lip model (1.5GB)...")
print("This may take 5-10 minutes...")

# Method 1: Direct HTTP download from HuggingFace mirror
urls = [
    "https://huggingface.co/spaces/Rudrabha/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth",
    "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth",
]

for i, url in enumerate([urls[0]], 1):
    try:
        print(f"\nAttempt {i}: Downloading from {url[:50]}...")
        response = requests.get(url, stream=True, timeout=30)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(checkpoint_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}% ({downloaded/1024/1024:.1f}MB/{total_size/1024/1024:.1f}MB)", end='')
            
            print(f"\n\nSUCCESS! Model downloaded to: {checkpoint_file}")
            print(f"File size: {checkpoint_file.stat().st_size / 1024 / 1024:.1f}MB")
            sys.exit(0)
    except Exception as e:
        print(f"\nFailed: {e}")
        continue

# Method 2: wget
print("\n\nTrying wget...")
try:
    subprocess.run([
        "wget",
        "https://huggingface.co/spaces/Rudrabha/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth",
        "-O", str(checkpoint_file)
    ], check=True)
    print("SUCCESS with wget!")
    sys.exit(0)
except:
    pass

# Method 3: curl
print("\n\nTrying curl...")
try:
    subprocess.run([
        "curl", "-L",
        "https://huggingface.co/spaces/Rudrabha/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth",
        "-o", str(checkpoint_file)
    ], check=True)
    print("SUCCESS with curl!")
    sys.exit(0)
except:
    pass

print("\n\nAll download methods failed.")
print("Please download manually from:")
print("https://huggingface.co/spaces/Rudrabha/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth")
