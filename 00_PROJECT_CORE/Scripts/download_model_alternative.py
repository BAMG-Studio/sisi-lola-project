"""Download from alternative source"""
import requests
from pathlib import Path
from tqdm import tqdm

checkpoint_file = Path("../../wav2lip_workspace/Wav2Lip/checkpoints/wav2lip_gan.pth")
checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

# Alternative: Download from GitHub release
url = "https://github.com/justinjohn0306/Wav2Lip/releases/download/models/wav2lip_gan.pth"

print(f"Downloading from GitHub release...")
print(f"URL: {url}")

response = requests.get(url, stream=True, allow_redirects=True)
total_size = int(response.headers.get('content-length', 0))

print(f"File size: {total_size/1024/1024:.1f}MB")

with open(checkpoint_file, 'wb') as f:
    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))

print(f"\nDownloaded to: {checkpoint_file}")
print(f"Size: {checkpoint_file.stat().st_size/1024/1024:.1f}MB")
