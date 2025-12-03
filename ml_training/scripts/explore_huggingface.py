#!/usr/bin/env python3
"""Explore HuggingFace Hub for Sisi Lola-relevant datasets and models"""
import os
from huggingface_hub import HfApi, login
import json

login(token=os.getenv('HUGGINGFACE_TOKEN'))
api = HfApi()

print("Exploring HuggingFace Hub for Sisi Lola Project\n")

# Search criteria
searches = {
    "African Languages": {
        "models": ["african", "yoruba", "igbo", "hausa", "swahili", "pidgin"],
        "datasets": ["african", "yoruba", "nigerian", "naija", "afro"]
    },
    "Voice/TTS": {
        "models": ["tts", "voice", "speech", "xtts"],
        "datasets": ["speech", "audio", "voice", "tts"]
    },
    "Virtual Influencer": {
        "models": ["avatar", "character", "persona", "influencer"],
        "datasets": ["conversation", "dialogue", "chat", "social"]
    }
}

results = {}

for category, queries in searches.items():
    print(f"\n{'='*60}")
    print(f"Category: {category}")
    print('='*60)
    
    results[category] = {"models": [], "datasets": []}
    
    # Search models
    print(f"\n[Models]")
    for query in queries["models"][:2]:  # Limit to 2 queries per category
        try:
            models = api.list_models(search=query, limit=5, sort="downloads", direction=-1)
            for model in models:
                info = {
                    "id": model.modelId,
                    "downloads": model.downloads or 0,
                    "likes": model.likes or 0,
                    "tags": model.tags[:5] if model.tags else []
                }
                results[category]["models"].append(info)
                print(f"  - {model.modelId} (↓{info['downloads']:,})")
        except:
            pass
    
    # Search datasets
    print(f"\n[Datasets]")
    for query in queries["datasets"][:2]:
        try:
            datasets = api.list_datasets(search=query, limit=5, sort="downloads", direction=-1)
            for dataset in datasets:
                info = {
                    "id": dataset.id,
                    "downloads": dataset.downloads or 0,
                    "likes": dataset.likes or 0,
                    "tags": dataset.tags[:5] if dataset.tags else []
                }
                results[category]["datasets"].append(info)
                print(f"  - {dataset.id} (↓{info['downloads']:,})")
        except:
            pass

# Save results
output_file = "ml_training/outputs/huggingface_discovery.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to: {output_file}")
