#!/usr/bin/env python3
"""
Train native Nigerian languages (Yoruba, Pidgin) for Sisi Lola
"""

import json
import os
import argparse
from datetime import datetime

def train_native_languages(dataset_path):
    """Train on native language datasets"""
    
    print("🌍 Training native Nigerian languages...")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract training samples
    yoruba_samples = data['languages']['yoruba']['samples']
    pidgin_samples = data['languages']['pidgin']['samples']
    mixed_samples = data['languages']['mixed_code_switching']['samples']
    
    print(f"✅ Yoruba samples: {len(yoruba_samples)}")
    print(f"✅ Pidgin samples: {len(pidgin_samples)}")
    print(f"✅ Mixed code-switching: {len(mixed_samples)}")
    
    # Prepare training data
    training_data = []
    
    # Yoruba
    for sample in yoruba_samples:
        training_data.append({
            "language": "yoruba",
            "native": sample['yoruba'],
            "english": sample['english'],
            "context": sample['context'],
            "personality": sample['personality']
        })
    
    # Pidgin
    for sample in pidgin_samples:
        training_data.append({
            "language": "pidgin",
            "native": sample['pidgin'],
            "english": sample['english'],
            "context": sample['context'],
            "personality": sample['personality']
        })
    
    # Mixed
    for sample in mixed_samples:
        training_data.append({
            "language": "mixed",
            "text": sample['text'],
            "translation": sample['translation'],
            "context": sample['context'],
            "personality": sample['personality']
        })
    
    # Save processed training data
    output_path = 'ml_training/datasets/native_languages_processed.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Processed {len(training_data)} native language samples")
    print(f"📁 Saved to: {output_path}")
    
    # Log training
    log_path = 'ml_training/logs/native_languages_training.log'
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{datetime.now().isoformat()} - Trained {len(training_data)} samples\n")
        f.write(f"  Yoruba: {len(yoruba_samples)}\n")
        f.write(f"  Pidgin: {len(pidgin_samples)}\n")
        f.write(f"  Mixed: {len(mixed_samples)}\n")
    
    return training_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()
    
    train_native_languages(args.dataset)
    print("✅ Native language training complete!")

if __name__ == "__main__":
    main()
