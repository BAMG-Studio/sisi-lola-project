#!/usr/bin/env python3
"""
Fine-tune personality model with OpenAI
"""

import json
import os
import argparse
from datetime import datetime
import openai
from dotenv import load_dotenv

load_dotenv()

def prepare_training_data(dataset_path):
    """Prepare data for OpenAI fine-tuning"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    training_examples = []
    for example in data['training_examples']:
        training_examples.append({
            "messages": [
                {"role": "system", "content": "You are Sisi Lola - confident, funny, and charismatic Nigerian virtual host."},
                {"role": "user", "content": example['input']},
                {"role": "assistant", "content": example['output']}
            ]
        })
    
    # Save as JSONL
    output_path = 'ml_training/datasets/personality_training.jsonl'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(json.dumps(example) + '\n')
    
    return output_path

def finetune_model(training_file, intensity='moderate'):
    """Fine-tune OpenAI model"""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Upload training file
    with open(training_file, 'rb') as f:
        response = openai.File.create(file=f, purpose='fine-tune')
    
    file_id = response['id']
    
    # Set epochs based on intensity
    epochs = {'light': 3, 'moderate': 5, 'intensive': 10}
    n_epochs = epochs.get(intensity, 5)
    
    # Create fine-tuning job
    job = openai.FineTuningJob.create(
        training_file=file_id,
        model="gpt-3.5-turbo",
        hyperparameters={"n_epochs": n_epochs}
    )
    
    return job

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--intensity', default='moderate')
    args = parser.parse_args()
    
    print("🎯 Preparing personality training data...")
    training_file = prepare_training_data(args.dataset)
    
    print(f"🚀 Starting fine-tuning (intensity: {args.intensity})...")
    job = finetune_model(training_file, args.intensity)
    
    print(f"✅ Fine-tuning job created: {job['id']}")
    print(f"📊 Status: {job['status']}")
    
    # Log results
    log_path = 'ml_training/logs/personality_training.log'
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a') as f:
        f.write(f"\n{datetime.now().isoformat()} - Job: {job['id']} - Intensity: {args.intensity}\n")

if __name__ == "__main__":
    main()
