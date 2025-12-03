#!/usr/bin/env python3
"""
Cohere Fine-tuning Automation
Create and manage fine-tuned models for Sisi Lola
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import cohere

load_dotenv('sisi_lola_api/.env')

co = cohere.Client(os.getenv('COHERE_API_KEY'))

def prepare_training_data(conversations_file, output_file):
    """Convert conversations to Cohere format"""
    print(f"Preparing training data from: {conversations_file}")
    
    with open(conversations_file, 'r') as f:
        conversations = json.load(f)
    
    training_data = []
    for conv in conversations:
        training_data.append({
            "prompt": conv['user'],
            "completion": conv['assistant']
        })
    
    with open(output_file, 'w') as f:
        for item in training_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✓ Training data prepared: {output_file}")
    print(f"  Total examples: {len(training_data)}")
    return output_file

def upload_dataset(file_path, dataset_name="sisi_lola_conversations"):
    """Upload dataset to Cohere"""
    print(f"Uploading dataset: {file_path}")
    
    with open(file_path, 'rb') as f:
        dataset = co.datasets.create(
            name=dataset_name,
            data=f,
            type='chat-finetune-input'
        )
    
    dataset_id = dataset.id
    print(f"✓ Dataset uploaded: {dataset_id}")
    return dataset_id

def create_finetune(dataset_id, model_name="sisi-lola-v1"):
    """Create fine-tuning job"""
    print(f"Creating fine-tune job...")
    
    finetune = co.finetuning.create_finetuned_model(
        request={
            "name": model_name,
            "settings": {
                "base_model": {
                    "base_type": "BASE_TYPE_CHAT"
                },
                "dataset_id": dataset_id,
                "hyperparameters": {
                    "early_stopping_patience": 10,
                    "early_stopping_threshold": 0.001,
                    "train_batch_size": 16,
                    "train_epochs": 1,
                    "learning_rate": 0.01
                }
            }
        }
    )
    
    finetune_id = finetune.id
    print(f"✓ Fine-tune job created: {finetune_id}")
    return finetune_id

def monitor_finetune(finetune_id):
    """Monitor fine-tuning progress"""
    print("Monitoring fine-tune progress...")
    
    while True:
        finetune = co.finetuning.get_finetuned_model(finetune_id)
        status = finetune.status
        
        print(f"  Status: {status}")
        
        if status == 'STATUS_READY':
            print(f"✓ Fine-tuning complete!")
            return finetune_id
        elif status in ['STATUS_FAILED', 'STATUS_CANCELLED']:
            print(f"✗ Fine-tuning {status}")
            return None
        
        time.sleep(30)

def save_model_id(model_id):
    """Save fine-tuned model ID to .env"""
    env_file = Path('sisi_lola_api/.env')
    
    with open(env_file, 'a') as f:
        f.write(f"\n# Cohere Fine-tuned Model\n")
        f.write(f"COHERE_SISI_LOLA_MODEL={model_id}\n")
    
    print(f"✓ Model ID saved to .env")

def test_model(model_id, prompt="Tell me about yourself"):
    """Test fine-tuned model"""
    print(f"\nTesting model: {model_id}")
    print(f"Prompt: {prompt}")
    
    response = co.chat(
        model=model_id,
        message=prompt
    )
    
    answer = response.text
    print(f"\nResponse:\n{answer}")

def main():
    print("=" * 60)
    print("COHERE FINE-TUNING")
    print("=" * 60)
    
    if not os.getenv('COHERE_API_KEY'):
        print("Error: COHERE_API_KEY not found in .env")
        return 1
    
    # Check for training data
    conversations_file = Path('api_customization/datasets/sisi_lola_conversations.json')
    
    if not conversations_file.exists():
        print(f"Error: Training data not found: {conversations_file}")
        print("\nPlease create training data first.")
        return 1
    
    # Prepare training data
    training_file = Path('api_customization/datasets/cohere_training.jsonl')
    prepare_training_data(conversations_file, training_file)
    
    # Upload dataset
    dataset_id = upload_dataset(training_file)
    
    # Create fine-tune
    finetune_id = create_finetune(dataset_id)
    
    # Monitor progress
    model_id = monitor_finetune(finetune_id)
    
    if model_id:
        save_model_id(model_id)
        test_model(model_id)
        
        print("\n" + "=" * 60)
        print("FINE-TUNING COMPLETE!")
        print("=" * 60)
        print(f"Model ID: {model_id}")
        
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
