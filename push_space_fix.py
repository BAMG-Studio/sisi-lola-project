#!/usr/bin/env python3
"""Quick push fix for HuggingFace Space"""
from huggingface_hub import HfApi
import os

# Use the active token from environment
api = HfApi(token=os.getenv("HUGGINGFACE_TOKEN"))

print("Pushing fixed Space with gradio 4.19.2...")
api.upload_folder(
    folder_path='huggingface_space',
    repo_id='sisilolalive/sisi-lola-demo',
    repo_type='space',
    commit_message='Fix: gradio 4.19.2 + huggingface_hub 0.20.3 for HfFolder compatibility'
)
print("✅ Done! Space updated.")
print("Check: https://huggingface.co/spaces/sisilolalive/sisi-lola-demo")
