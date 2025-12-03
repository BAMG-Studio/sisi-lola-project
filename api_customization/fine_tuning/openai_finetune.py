#!/usr/bin/env python3
"""
OpenAI GPT Fine-tuning Automation
Create and manage fine-tuned models for Sisi Lola
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('sisi_lola_api/.env')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def prepare_training_data(conversations_file, output_file):
    """Convert conversations to JSONL format"""
    print(f"Preparing training data from: {conversations_file}")
    
    with open(conversations_file, 'r') as f:
        conversations = json.load(f)
    
    training_data = []
    for conv in conversations:
        training_data.append({
            "messages": [
                {"role": "system", "content": "You are Sisi Lola, an AI virtual host. You are friendly, engaging, and knowledgeable about entertainment and technology."},
                {"role": "user", "content": conv['user']},
                {"role": "assistant", "content": conv['assistant']}
            ]
        })
    
    with open(output_file, 'w') as f:
        for item in training_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✓ Training data prepared: {output_file}")
    print(f"  Total examples: {len(training_data)}")
    return output_file

def upload_training_file(file_path):
    """Upload training file to OpenAI"""
    print(f"Uploading training file: {file_path}")
    
    with open(file_path, 'rb') as f:
        response = client.files.create(
            file=f,
            purpose='fine-tune'
        )
    
    file_id = response.id
    print(f"✓ File uploaded: {file_id}")
    return file_id

def create_fine_tune_job(file_id, model="gpt-3.5-turbo", suffix="sisi-lola"):
    """Create fine-tuning job"""
    print(f"Creating fine-tune job...")
    
    response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=model,
        suffix=suffix
    )
    
    job_id = response.id
    print(f"✓ Fine-tune job created: {job_id}")
    return job_id

def monitor_fine_tune(job_id):
    """Monitor fine-tuning progress"""
    print("Monitoring fine-tune progress...")
    
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status
        
        print(f"  Status: {status}")
        
        if status == 'succeeded':
            model_id = job.fine_tuned_model
            print(f"✓ Fine-tuning complete!")
            print(f"  Model ID: {model_id}")
            return model_id
        elif status in ['failed', 'cancelled']:
            print(f"✗ Fine-tuning {status}")
            return None
        
        time.sleep(30)

def save_model_id(model_id):
    """Save fine-tuned model ID to .env"""
    env_file = Path('sisi_lola_api/.env')
    
    with open(env_file, 'a') as f:
        f.write(f"\n# OpenAI Fine-tuned Model\n")
        f.write(f"OPENAI_SISI_LOLA_MODEL={model_id}\n")
    
    print(f"✓ Model ID saved to .env")

def test_model(model_id, prompt="Tell me about yourself"):
    """Test fine-tuned model"""
    print(f"\nTesting model: {model_id}")
    print(f"Prompt: {prompt}")
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are Sisi Lola, an AI virtual host."},
            {"role": "user", "content": prompt}
        ]
    )
    
    answer = response.choices[0].message.content
    print(f"\nResponse:\n{answer}")

def main():
    print("=" * 60)
    print("OPENAI GPT FINE-TUNING")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in .env")
        return 1
    
    # Check for training data
    conversations_file = Path('api_customization/datasets/sisi_lola_conversations.json')
    
    if not conversations_file.exists():
        print(f"Error: Training data not found: {conversations_file}")
        print("\nPlease create training data first.")
        print("Format: [{\"user\": \"question\", \"assistant\": \"answer\"}, ...]")
        return 1
    
    # Prepare training data
    training_file = Path('api_customization/datasets/openai_training.jsonl')
    prepare_training_data(conversations_file, training_file)
    
    # Upload file
    file_id = upload_training_file(training_file)
    
    # Create fine-tune job
    job_id = create_fine_tune_job(file_id)
    
    # Monitor progress
    model_id = monitor_fine_tune(job_id)
    
    if model_id:
        save_model_id(model_id)
        test_model(model_id)
        
        print("\n" + "=" * 60)
        print("FINE-TUNING COMPLETE!")
        print("=" * 60)
        print(f"Model ID: {model_id}")
        print("Use this model in your API calls")
        
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
