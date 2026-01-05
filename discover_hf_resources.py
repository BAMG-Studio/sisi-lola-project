#!/usr/bin/env python3
"""Quick HuggingFace discovery for Sisi Lola"""
import os
os.environ['HUGGINGFACE_TOKEN'] = os.getenv('HUGGINGFACE_TOKEN', '')

from huggingface_hub import HfApi, login
import json

login(token=os.getenv('HUGGINGFACE_TOKEN'))
api = HfApi()

print("Discovering HuggingFace Resources for Sisi Lola\n")

discoveries = {}

# 1. African Language Models
print("[1/4] African Language Models...")
try:
    models = list(api.list_models(search="african", limit=3, sort="downloads", direction=-1))
    discoveries['african_models'] = [{"id": m.modelId, "downloads": m.downloads} for m in models]
    for m in models:
        print(f"  - {m.modelId}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Nigerian/Yoruba Datasets
print("\n[2/4] Nigerian/Yoruba Datasets...")
try:
    datasets = list(api.list_datasets(search="yoruba", limit=3, sort="downloads", direction=-1))
    discoveries['yoruba_datasets'] = [{"id": d.id, "downloads": d.downloads} for d in datasets]
    for d in datasets:
        print(f"  - {d.id}")
except Exception as e:
    print(f"  Error: {e}")

# 3. TTS/Voice Models
print("\n[3/4] TTS/Voice Models...")
try:
    models = list(api.list_models(search="tts", limit=3, sort="downloads", direction=-1))
    discoveries['tts_models'] = [{"id": m.modelId, "downloads": m.downloads} for m in models]
    for m in models:
        print(f"  - {m.modelId}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Conversation Datasets
print("\n[4/4] Conversation Datasets...")
try:
    datasets = list(api.list_datasets(search="conversation", limit=3, sort="downloads", direction=-1))
    discoveries['conversation_datasets'] = [{"id": d.id, "downloads": d.downloads} for d in datasets]
    for d in datasets:
        print(f"  - {d.id}")
except Exception as e:
    print(f"  Error: {e}")

# Save
output = "ml_training/outputs/hf_discoveries.json"
os.makedirs(os.path.dirname(output), exist_ok=True)
with open(output, 'w') as f:
    json.dump(discoveries, f, indent=2)

print(f"\n\nSaved to: {output}")
print(f"Found {sum(len(v) for v in discoveries.values())} resources")
