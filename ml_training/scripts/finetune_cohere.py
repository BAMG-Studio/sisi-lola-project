#!/usr/bin/env python3
"""
Sisi Lola - Cohere Fine-Tuning Script

This script fine-tunes a Cohere Command model with Sisi Lola's personality.
It uses the Cohere API to create and manage fine-tuning jobs.

Prerequisites:
1. Cohere API key (get from https://dashboard.cohere.com/api-keys)
2. Training data in Cohere chat format (JSONL)
3. At least 32 training examples (recommended: 100+)

Usage:
    python finetune_cohere.py --action create --data sisi_lola_cohere_full.jsonl
    python finetune_cohere.py --action status --job-id <job_id>
    python finetune_cohere.py --action list
    python finetune_cohere.py --action test --model <fine-tuned-model-id>

Environment:
    COHERE_API_KEY: Your Cohere API key
"""

import os
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

try:
    import cohere
except ImportError:
    print("❌ Cohere library not installed. Run: pip install cohere")
    exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/.env')

# Configuration
TRAINING_DATA_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/training_data')
JOBS_FILE = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/cohere_finetune_jobs.json')

# Cohere fine-tuning settings
FINETUNE_CONFIG = {
    "base_model": "command-r",  # Options: command-r, command-r-plus, command-light
    "hyperparameters": {
        "train_epochs": 3,           # Number of training epochs (1-10)
        "learning_rate": 0.01,       # Learning rate (0.001 - 0.1)
        "train_batch_size": 16,      # Batch size (8-64)
    },
    "model_prefix": "sisi-lola"      # Prefix for the fine-tuned model name
}


def get_cohere_client():
    """Initialize Cohere client."""
    api_key = os.getenv('COHERE_API_KEY')
    if not api_key:
        raise ValueError(
            "❌ COHERE_API_KEY not found in environment.\n"
            "Set it with: export COHERE_API_KEY='your-key-here'\n"
            "Or add to .env file: COHERE_API_KEY=your-key-here"
        )
    return cohere.ClientV2(api_key=api_key)


def validate_training_data(filepath: Path) -> dict:
    """Validate training data format for Cohere."""
    print(f"\n📋 Validating training data: {filepath.name}")
    
    if not filepath.exists():
        raise FileNotFoundError(f"Training file not found: {filepath}")
    
    examples = []
    errors = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                example = json.loads(line.strip())
                
                # Validate structure
                if 'messages' not in example:
                    errors.append(f"Line {i}: Missing 'messages' key")
                    continue
                
                messages = example['messages']
                if not isinstance(messages, list):
                    errors.append(f"Line {i}: 'messages' must be a list")
                    continue
                
                # Validate roles
                roles = [m.get('role', '').lower() for m in messages]
                if 'user' not in roles:
                    errors.append(f"Line {i}: Missing 'User' role")
                if 'chatbot' not in roles:
                    errors.append(f"Line {i}: Missing 'Chatbot' role")
                
                examples.append(example)
                
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: Invalid JSON - {e}")
    
    stats = {
        "total_examples": len(examples),
        "errors": errors[:10],  # Show first 10 errors
        "has_errors": len(errors) > 0,
        "valid": len(examples) >= 32  # Cohere minimum
    }
    
    print(f"   ✅ Valid examples: {len(examples)}")
    if errors:
        print(f"   ⚠️  Errors found: {len(errors)}")
        for err in errors[:5]:
            print(f"      - {err}")
    
    if len(examples) < 32:
        print(f"   ⚠️  Warning: Cohere recommends at least 32 examples (found {len(examples)})")
    
    return stats


def upload_dataset(client, filepath: Path) -> str:
    """Upload training dataset to Cohere."""
    print(f"\n📤 Uploading dataset: {filepath.name}")
    
    # Create dataset
    dataset = client.datasets.create(
        name=f"sisi-lola-training-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        type="chat-finetune-input",
        data=open(filepath, 'rb')
    )
    
    dataset_id = dataset.id
    print(f"   Dataset ID: {dataset_id}")
    
    # Wait for processing
    print("   Waiting for dataset processing...")
    for _ in range(60):  # Max 5 minutes wait
        status = client.datasets.get(dataset_id)
        # Handle both old and new API response formats
        val_status = getattr(status, 'validation_status', None) or getattr(status, 'status', None)
        if val_status in ["validated", "ready", "complete"]:
            print("   ✅ Dataset validated successfully")
            break
        elif val_status in ["failed", "error"]:
            val_error = getattr(status, 'validation_error', None) or getattr(status, 'error', 'Unknown error')
            raise ValueError(f"Dataset validation failed: {val_error}")
        time.sleep(5)
    else:
        print("   ⚠️ Timeout waiting for validation, proceeding anyway...")
    
    return dataset_id


def create_finetune_job(client, dataset_id: str, name: str = None) -> dict:
    """Create a fine-tuning job."""
    if name is None:
        name = f"{FINETUNE_CONFIG['model_prefix']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"\n🚀 Creating fine-tuning job: {name}")
    print(f"   Base model: {FINETUNE_CONFIG['base_model']}")
    print(f"   Hyperparameters: {FINETUNE_CONFIG['hyperparameters']}")
    
    job = client.finetuning.create_finetuned_model(
        request={
            "name": name,
            "settings": {
                "base_model": {
                    "base_type": FINETUNE_CONFIG['base_model']
                },
                "dataset_id": dataset_id,
                "hyperparameters": FINETUNE_CONFIG['hyperparameters']
            }
        }
    )
    
    job_info = {
        "job_id": job.finetuned_model.id,
        "name": name,
        "status": job.finetuned_model.status,
        "created_at": datetime.now().isoformat(),
        "base_model": FINETUNE_CONFIG['base_model'],
        "dataset_id": dataset_id
    }
    
    print(f"   ✅ Job created: {job_info['job_id']}")
    
    # Save job info
    save_job_info(job_info)
    
    return job_info


def get_job_status(client, job_id: str) -> dict:
    """Get status of a fine-tuning job."""
    print(f"\n📊 Checking job status: {job_id}")
    
    job = client.finetuning.get_finetuned_model(job_id)
    
    status = {
        "job_id": job_id,
        "name": job.finetuned_model.name,
        "status": job.finetuned_model.status,
        "base_model": FINETUNE_CONFIG['base_model']
    }
    
    print(f"   Name: {status['name']}")
    print(f"   Status: {status['status']}")
    
    if status['status'] == 'READY':
        print(f"   ✅ Model is ready to use!")
        print(f"   Model ID: {job_id}")
    elif status['status'] == 'FAILED':
        print(f"   ❌ Fine-tuning failed")
    else:
        print(f"   ⏳ Still processing...")
    
    return status


def list_finetune_jobs(client) -> list:
    """List all fine-tuning jobs."""
    print("\n📋 Listing fine-tuned models...")
    
    models = client.finetuning.list_finetuned_models()
    
    jobs = []
    for model in models.finetuned_models:
        job = {
            "id": model.id,
            "name": model.name,
            "status": model.status,
            "created_at": str(model.created_at) if hasattr(model, 'created_at') else "N/A"
        }
        jobs.append(job)
        print(f"\n   Model: {job['name']}")
        print(f"   ID: {job['id']}")
        print(f"   Status: {job['status']}")
    
    if not jobs:
        print("   No fine-tuned models found.")
    
    return jobs


def test_model(client, model_id: str, prompt: str = None):
    """Test the fine-tuned model."""
    if prompt is None:
        prompt = "Greet me in your special way and tell me about African culture."
    
    print(f"\n🧪 Testing model: {model_id}")
    print(f"   Prompt: {prompt}")
    print("\n" + "-" * 50)
    
    response = client.chat(
        model=model_id,
        message=prompt
    )
    
    print(f"\n🤖 Sisi Lola says:\n")
    print(response.text)
    print("\n" + "-" * 50)
    
    return response.text


def save_job_info(job_info: dict):
    """Save job info to local file."""
    jobs = []
    if JOBS_FILE.exists():
        with open(JOBS_FILE, 'r') as f:
            jobs = json.load(f)
    
    jobs.append(job_info)
    
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Sisi Lola Cohere Fine-Tuning Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new fine-tuning job
  python finetune_cohere.py --action create --data sisi_lola_cohere_full.jsonl

  # Check job status
  python finetune_cohere.py --action status --job-id abc123

  # List all jobs
  python finetune_cohere.py --action list

  # Test a fine-tuned model
  python finetune_cohere.py --action test --model sisi-lola-xyz --prompt "Hello!"

  # Validate training data only
  python finetune_cohere.py --action validate --data sisi_lola_cohere.jsonl
        """
    )
    
    parser.add_argument('--action', required=True,
                       choices=['create', 'status', 'list', 'test', 'validate'],
                       help='Action to perform')
    parser.add_argument('--data', help='Training data file (JSONL)')
    parser.add_argument('--job-id', help='Fine-tuning job ID')
    parser.add_argument('--model', help='Fine-tuned model ID for testing')
    parser.add_argument('--prompt', help='Test prompt', default=None)
    parser.add_argument('--name', help='Custom name for fine-tuned model')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌍 SISI LOLA - COHERE FINE-TUNING MANAGER")
    print("=" * 60)
    
    try:
        client = get_cohere_client()
        print("✅ Cohere client initialized")
        
        if args.action == 'validate':
            if not args.data:
                raise ValueError("--data required for validate action")
            filepath = TRAINING_DATA_DIR / args.data
            validate_training_data(filepath)
        
        elif args.action == 'create':
            if not args.data:
                raise ValueError("--data required for create action")
            
            filepath = TRAINING_DATA_DIR / args.data
            
            # Validate first
            stats = validate_training_data(filepath)
            if not stats['valid']:
                print("\n❌ Training data validation failed. Fix errors and try again.")
                return
            
            # Upload and create job
            dataset_id = upload_dataset(client, filepath)
            job = create_finetune_job(client, dataset_id, args.name)
            
            print(f"\n✅ Fine-tuning job created!")
            print(f"   Job ID: {job['job_id']}")
            print(f"\n   Check status with:")
            print(f"   python finetune_cohere.py --action status --job-id {job['job_id']}")
        
        elif args.action == 'status':
            if not args.job_id:
                raise ValueError("--job-id required for status action")
            get_job_status(client, args.job_id)
        
        elif args.action == 'list':
            list_finetune_jobs(client)
        
        elif args.action == 'test':
            if not args.model:
                raise ValueError("--model required for test action")
            test_model(client, args.model, args.prompt)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
