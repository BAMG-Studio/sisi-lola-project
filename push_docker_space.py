#!/usr/bin/env python3
"""Push Docker-based Space to HuggingFace"""
from huggingface_hub import HfApi
import os

TOKEN = os.getenv("HUGGINGFACE_TOKEN")
REPO = "sisilolalive/sisi-lola-demo"

api = HfApi(token=TOKEN)

# Simple app that works
APP_PY = '''#!/usr/bin/env python3
import gradio as gr

def chat(message, history):
    responses = {
        "hello": "E kaabo! Welcome my friend! How you dey today?",
        "hi": "Hey! Na wa o, good to see you! Wetin dey happen?",
        "how are you": "I dey fine well well! The vibes dey sweet today.",
        "how you dey": "Ah! I dey kampe! Everything dey run smooth. You nko?",
        "jollof": "Ah! Jollof rice! Nigerian jollof sweet pass any other one o!",
        "food": "Nigerian food na the best! Jollof, Egusi, Pounded Yam, Suya...",
        "music": "Afrobeats don scatter everywhere! Burna Boy, Wizkid, Davido!",
        "lagos": "Lagos! The city wey never sleep! Eko for show!",
    }
    msg_lower = message.lower()
    for key, response in responses.items():
        if key in msg_lower:
            return response
    return f"E kaabo! You talk: {message}. I be Sisi Lola, your Nigerian AI!"

with gr.Blocks(title="Sisi Lola AI") as demo:
    gr.HTML("<h1 style='text-align:center'>Sisi Lola AI</h1>")
    gr.ChatInterface(fn=chat, examples=["How you dey?", "Tell me about jollof"])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
'''

DOCKERFILE = '''FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir gradio==4.19.2 huggingface_hub==0.20.3
COPY app.py .
EXPOSE 7860
CMD ["python", "app.py"]
'''

README = '''---
title: Sisi Lola AI
emoji: "\\U0001F469\\U0001F3FE"
colorFrom: green
colorTo: gray
sdk: docker
pinned: true
license: mit
short_description: Nigeria AI Content Creator
---

# Sisi Lola AI

Chat with Nigeria's virtual content creator!
'''

print("Uploading Dockerfile...")
api.upload_file(
    path_or_fileobj=DOCKERFILE.encode(),
    path_in_repo="Dockerfile",
    repo_id=REPO,
    repo_type="space"
)

print("Uploading app.py...")
api.upload_file(
    path_or_fileobj=APP_PY.encode(),
    path_in_repo="app.py",
    repo_id=REPO,
    repo_type="space"
)

print("Uploading README.md...")
api.upload_file(
    path_or_fileobj=README.encode(),
    path_in_repo="README.md",
    repo_id=REPO,
    repo_type="space",
    commit_message="Docker SDK with pinned versions"
)

print("DONE! Check: https://huggingface.co/spaces/sisilolalive/sisi-lola-demo")
