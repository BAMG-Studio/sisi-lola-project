#!/usr/bin/env python3
"""Fix HuggingFace Space configuration"""
from huggingface_hub import HfApi
import os

TOKEN = os.getenv("HUGGINGFACE_TOKEN")
REPO = "sisilolalive/sisi-lola-demo"

api = HfApi(token=TOKEN)

README = """---
title: Sisi Lola AI
emoji: "\U0001F469\U0001F3FE"
colorFrom: green
colorTo: gray
sdk: docker
app_file: app.py
pinned: true
license: mit
short_description: Nigeria AI Content Creator
---

# Sisi Lola AI
Chat with Nigeria's virtual content creator!
"""

print("Fixing README (removing ZeroGPU)...")
api.upload_file(
    path_or_fileobj=README.encode(),
    path_in_repo="README.md",
    repo_id=REPO,
    repo_type="space",
    commit_message="Fix: Remove ZeroGPU for Docker SDK"
)
print("Done! Check: https://huggingface.co/spaces/sisilolalive/sisi-lola-demo")
