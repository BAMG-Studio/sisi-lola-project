#!/usr/bin/env python3
"""Download TinyLlama model for local training"""
from huggingface_hub import snapshot_download
import sys

print("Starting TinyLlama model download...")
print("This may take 5-10 minutes depending on your connection.")

try:
    path = snapshot_download(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        resume_download=True
    )
    print(f"Download complete! Model cached at: {path}")
except KeyboardInterrupt:
    print("\nDownload interrupted. Run again to resume.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
