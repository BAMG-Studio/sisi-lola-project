"""Upload README to voice-xtts repo"""
from huggingface_hub import HfApi

api = HfApi()

voice_readme = """---
license: apache-2.0
language:
  - en
  - yo
  - pcm
tags:
  - text-to-speech
  - xtts
  - voice-cloning
  - nigerian
  - sisi-lola
library_name: coqui-tts
pipeline_tag: text-to-speech
---

# Sisi Lola Voice Model (XTTS-v2 Embeddings)

Nigerian voice synthesis using XTTS-v2 speaker embeddings for authentic voice cloning.

## Model Details
- **Base TTS:** coqui/XTTS-v2
- **Voice Style:** Nigerian English with cultural authenticity
- **Format:** Speaker embeddings (.pth files)

## Voice Routing System

| Tag | Language | Primary Engine |
|-----|----------|----------------|
| [EN] | English | XTTS-v2 (this model) |
| [NP] | Pidgin | YarnGPT / XTTS |
| [YO] | Yoruba | VITS-Yoruba |
| [IG] | Igbo | YarnGPT |
| [HA] | Hausa | YarnGPT |

## Files
- speaker_embedding.pth - Main speaker embedding tensor
- gpt_cond_latent.pth - GPT conditioning latent
- config.json - Voice configuration

## Part of Sisi Lola Project
[GitHub](https://github.com/BAMG-Studio/sisi-lola-project)
"""

api.upload_file(
    path_or_fileobj=voice_readme.encode(),
    path_in_repo='README.md',
    repo_id='sisilolalive/sisi-lola-voice-xtts',
    repo_type='model',
    commit_message='Add model documentation',
)
print('✅ Uploaded voice README')
