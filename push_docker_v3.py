#!/usr/bin/env python3
"""Push Docker Space - Fix ZeroGPU config error"""
from huggingface_hub import HfApi
import os

TOKEN = os.getenv("HUGGINGFACE_TOKEN")
REPO = "sisilolalive/sisi-lola-demo"

api = HfApi(token=TOKEN)

# README using exact HF template format - NO ZeroGPU
README = """---
title: Sisi Lola AI
emoji: 👩🏾
colorFrom: green
colorTo: gray
sdk: docker
app_file: app.py
pinned: false
---

# Sisi Lola AI
Chat with Nigeria's virtual content creator!
"""

DOCKERFILE = """FROM python:3.10-slim

WORKDIR /app

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

RUN pip install --user --no-cache-dir gradio==4.19.2 huggingface_hub==0.20.3

COPY --chown=user app.py .

EXPOSE 7860

CMD ["python", "app.py"]
"""

APP = '''import gradio as gr

RESPONSES = {
    "hello": "How far! Wetin dey happen?",
    "hi": "Ehen! Na so. How you dey?",
    "jollof": "Ah! Nigerian jollof na the best, no cap!",
    "lagos": "Lagos! The city wey never sleep!",
    "music": "Afrobeats don take over the world!",
    "food": "Nigerian food na the sweetest!",
}

def respond(message, history):
    msg = message.lower()
    for key, response in RESPONSES.items():
        if key in msg:
            return response
    return "Wetin else you wan yarn? Ask about Lagos, jollof, or music!"

demo = gr.ChatInterface(
    fn=respond,
    title="Sisi Lola AI",
    description="Chat with Nigeria virtual content creator!",
    examples=["Hello!", "Tell me about Lagos", "What about jollof?"],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
'''

print("Pushing to HuggingFace Space...")

# Upload all files
for name, content in [("README.md", README), ("Dockerfile", DOCKERFILE), ("app.py", APP)]:
    api.upload_file(
        path_or_fileobj=content.encode(),
        path_in_repo=name,
        repo_id=REPO,
        repo_type="space",
        commit_message=f"Update {name} - Docker SDK no GPU"
    )
    print(f"✓ {name}")

print("\nDone! Check: https://huggingface.co/spaces/sisilolalive/sisi-lola-demo")
