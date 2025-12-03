#!/usr/bin/env python3
"""Integrate Yoruba datasets from HuggingFace into training pipeline"""
import os
from datasets import load_dataset
from pathlib import Path
import json

os.environ['HUGGINGFACE_TOKEN'] = os.getenv('HUGGINGFACE_TOKEN', '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')

print("Integrating Yoruba Datasets\n")

output_dir = Path("ml_training/datasets/yoruba_extended")
output_dir.mkdir(parents=True, exist_ok=True)

# 1. Download yoruba-ljspeech
print("[1/3] Downloading yoruba-ljspeech...")
try:
    dataset1 = load_dataset("Abdullah804/yoruba-ljspeech", split="train")
    dataset1.save_to_disk(str(output_dir / "yoruba_ljspeech"))
    print(f"  Saved {len(dataset1)} samples\n")
except Exception as e:
    print(f"  Error: {e}\n")

# 2. Download yoruba_audio_translated
print("[2/3] Downloading yoruba_audio_translated...")
try:
    dataset2 = load_dataset("bytel0rd/yoruba_audio_translated", split="train")
    dataset2.save_to_disk(str(output_dir / "yoruba_audio_translated"))
    print(f"  Saved {len(dataset2)} samples\n")
except Exception as e:
    print(f"  Error: {e}\n")

# 3. Create manifest
print("[3/3] Creating training manifest...")
manifest = {
    "datasets": [
        {
            "name": "yoruba-ljspeech",
            "path": str(output_dir / "yoruba_ljspeech"),
            "type": "speech",
            "language": "yoruba"
        },
        {
            "name": "yoruba_audio_translated",
            "path": str(output_dir / "yoruba_audio_translated"),
            "type": "bilingual_speech",
            "language": "yoruba-english"
        }
    ],
    "total_samples": "TBD",
    "use_case": "XTTS voice training enhancement"
}

manifest_path = output_dir / "manifest.json"
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"  Manifest saved: {manifest_path}\n")
print("Integration complete!")
print(f"\nNext: Update train_nigerian_voice.py to use {output_dir}")
