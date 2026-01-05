#!/usr/bin/env python3
"""Push a fully working Docker Space to HuggingFace"""
from huggingface_hub import HfApi
import os

TOKEN = os.getenv("HUGGINGFACE_TOKEN")
REPO = "sisilolalive/sisi-lola-demo"

api = HfApi(token=TOKEN)

# Dockerfile with explicit version control
DOCKERFILE = """FROM python:3.10-slim

WORKDIR /app

# Create user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Install exact versions to avoid HfFolder error
RUN pip install --user --no-cache-dir \\
    gradio==4.19.2 \\
    huggingface_hub==0.20.3

# Verify installation
RUN python -c "from huggingface_hub import HfFolder; print('HfFolder import works!')"

COPY --chown=user app.py .

EXPOSE 7860

CMD ["python", "app.py"]
"""

# Simple app that definitely works
APP = '''import gradio as gr

# Nigerian Pidgin AI responses
RESPONSES = {
    "hello": "How far! Wetin dey happen?",
    "hi": "Ehen! Na so. How you dey?",
    "jollof": "Ah! You don touch my heart. Nigerian jollof na the best, no cap! Ghana own no reach am at all!",
    "lagos": "Lagos! The city wey never sleep. Traffic go kill person, but the vibes dey mad!",
    "music": "Afrobeats don take over the world! From Burna Boy to Wizkid, na we dey run things!",
    "food": "Omo! Nigerian food na the sweetest. Egusi, amala, suya... my belle dey rumble now!",
    "money": "E be like say money dey find me! Hustle go pay one day, trust the process.",
}

def respond(message, history):
    msg = message.lower()
    for key, response in RESPONSES.items():
        if key in msg:
            return response
    return "Ah, I hear you! Wetin else you wan yarn? Ask me about Lagos, jollof, music, or anything naija!"

demo = gr.ChatInterface(
    fn=respond,
    title="🇳🇬 Sisi Lola AI",
    description="Chat with Nigeria\\'s virtual content creator! Ask about Lagos, jollof, music, and more.",
    examples=["Hello!", "Tell me about Lagos", "What about jollof rice?"],
    theme="soft"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
'''

README = """---
title: Sisi Lola AI
emoji: "\\U0001F469\\U0001F3FE"
colorFrom: green
colorTo: gray
sdk: docker
app_file: app.py
pinned: true
license: mit
short_description: Nigeria AI Content Creator
---

# Sisi Lola AI 🇳🇬
Chat with Nigeria's virtual content creator!
"""

print("=" * 50)
print("PUSHING DOCKER SPACE TO HUGGINGFACE")
print("=" * 50)

print("\\n1. Uploading Dockerfile...")
api.upload_file(
    path_or_fileobj=DOCKERFILE.encode(),
    path_in_repo="Dockerfile",
    repo_id=REPO,
    repo_type="space",
    commit_message="Fix Dockerfile with explicit version pins"
)
print("   ✓ Dockerfile uploaded")

print("\\n2. Uploading app.py...")
api.upload_file(
    path_or_fileobj=APP.encode(),
    path_in_repo="app.py",
    repo_id=REPO,
    repo_type="space",
    commit_message="Update app.py"
)
print("   ✓ app.py uploaded")

print("\\n3. Uploading README.md...")
api.upload_file(
    path_or_fileobj=README.encode(),
    path_in_repo="README.md",
    repo_id=REPO,
    repo_type="space",
    commit_message="Update README - Docker SDK"
)
print("   ✓ README.md uploaded")

print("\\n" + "=" * 50)
print("DONE! Wait 2-3 minutes for rebuild.")
print("Check: https://huggingface.co/spaces/sisilolalive/sisi-lola-demo")
print("=" * 50)
