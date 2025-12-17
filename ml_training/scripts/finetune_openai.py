#!/usr/bin/env python3
"""
Sisi Lola - OpenAI Fine-Tuning Script

This script fine-tunes an OpenAI model (GPT-3.5-turbo or GPT-4) with Sisi Lola's personality.

Prerequisites:
1. OpenAI API key (get from https://platform.openai.com/api-keys)
2. Training data in OpenAI chat format (JSONL)
3. At least 10 training examples (recommended: 50-100+)

Usage:
    python finetune_openai.py --action create --data sisi_lola_openai.jsonl
    python finetune_openai.py --action status --job-id ftjob-xxx
    python finetune_openai.py --action list
    python finetune_openai.py --action test --model ft:gpt-3.5-turbo:xxx

Environment:
    OPENAI_API_KEY: Your OpenAI API key

Costs (approximate):
    - GPT-3.5-turbo fine-tuning: $0.008 per 1K tokens
    - GPT-4 fine-tuning: ~$0.03 per 1K tokens (limited availability)
"""

import os
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI library not installed. Run: pip install openai")
    exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/.env')

# Configuration
TRAINING_DATA_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/training_data')
JOBS_FILE = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/openai_finetune_jobs.json')

# OpenAI fine-tuning settings
FINETUNE_CONFIG = {
    "base_model": "gpt-3.5-turbo",  # Options: gpt-3.5-turbo, gpt-4-0613 (limited)
    "hyperparameters": {
        "n_epochs": 3,                    # Number of training epochs (1-10)
        "batch_size": "auto",             # Batch size (auto, or 1-256)
        "learning_rate_multiplier": 1.0,  # Learning rate multiplier (0.1-2.0)
    },
    "suffix": "sisi-lola"  # Suffix for the fine-tuned model name
}


def get_openai_client():
    """Initialize OpenAI client."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "❌ OPENAI_API_KEY not found in environment.\n"
            "Set it with: export OPENAI_API_KEY='your-key-here'\n"
            "Or add to .env file: OPENAI_API_KEY=your-key-here"
        )
    return OpenAI(api_key=api_key)


def validate_training_data(filepath: Path) -> dict:
    """Validate training data format for OpenAI."""
    print(f"\n📋 Validating training data: {filepath.name}")
    
    if not filepath.exists():
        raise FileNotFoundError(f"Training file not found: {filepath}")
    
    examples = []
    errors = []
    total_tokens = 0
    
    # Rough token estimation (4 chars per token)
    def estimate_tokens(text):
        return len(text) // 4
    
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
                roles = [m.get('role', '') for m in messages]
                if 'user' not in roles:
                    errors.append(f"Line {i}: Missing 'user' role")
                if 'assistant' not in roles:
                    errors.append(f"Line {i}: Missing 'assistant' role")
                
                # Estimate tokens
                for msg in messages:
                    total_tokens += estimate_tokens(msg.get('content', ''))
                
                examples.append(example)
                
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: Invalid JSON - {e}")
    
    # Cost estimation
    training_cost = (total_tokens / 1000) * 0.008  # GPT-3.5 training cost
    
    stats = {
        "total_examples": len(examples),
        "estimated_tokens": total_tokens,
        "estimated_cost": f"${training_cost:.2f}",
        "errors": errors[:10],
        "has_errors": len(errors) > 0,
        "valid": len(examples) >= 10  # OpenAI minimum
    }
    
    print(f"   ✅ Valid examples: {len(examples)}")
    print(f"   📊 Estimated tokens: {total_tokens:,}")
    print(f"   💰 Estimated training cost: ${training_cost:.2f}")
    
    if errors:
        print(f"   ⚠️  Errors found: {len(errors)}")
        for err in errors[:5]:
            print(f"      - {err}")
    
    if len(examples) < 10:
        print(f"   ⚠️  Warning: OpenAI requires at least 10 examples (found {len(examples)})")
    
    return stats


def upload_file(client, filepath: Path) -> str:
    """Upload training file to OpenAI."""
    print(f"\n📤 Uploading training file: {filepath.name}")
    
    with open(filepath, 'rb') as f:
        response = client.files.create(
            file=f,
            purpose='fine-tune'
        )
    
    file_id = response.id
    print(f"   File ID: {file_id}")
    print(f"   ✅ File uploaded successfully")
    
    return file_id


def create_finetune_job(client, file_id: str) -> dict:
    """Create a fine-tuning job."""
    print(f"\n🚀 Creating fine-tuning job")
    print(f"   Base model: {FINETUNE_CONFIG['base_model']}")
    print(f"   Suffix: {FINETUNE_CONFIG['suffix']}")
    
    hyperparams = {}
    if FINETUNE_CONFIG['hyperparameters']['n_epochs'] != 'auto':
        hyperparams['n_epochs'] = FINETUNE_CONFIG['hyperparameters']['n_epochs']
    if FINETUNE_CONFIG['hyperparameters']['learning_rate_multiplier'] != 'auto':
        hyperparams['learning_rate_multiplier'] = FINETUNE_CONFIG['hyperparameters']['learning_rate_multiplier']
    
    response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=FINETUNE_CONFIG['base_model'],
        suffix=FINETUNE_CONFIG['suffix'],
        hyperparameters=hyperparams if hyperparams else None
    )
    
    job_info = {
        "job_id": response.id,
        "status": response.status,
        "model": response.model,
        "created_at": datetime.now().isoformat(),
        "file_id": file_id,
        "fine_tuned_model": response.fine_tuned_model
    }
    
    print(f"   ✅ Job created: {job_info['job_id']}")
    print(f"   Status: {job_info['status']}")
    
    # Save job info
    save_job_info(job_info)
    
    return job_info


def get_job_status(client, job_id: str) -> dict:
    """Get status of a fine-tuning job."""
    print(f"\n📊 Checking job status: {job_id}")
    
    response = client.fine_tuning.jobs.retrieve(job_id)
    
    status = {
        "job_id": job_id,
        "status": response.status,
        "model": response.model,
        "fine_tuned_model": response.fine_tuned_model,
        "trained_tokens": response.trained_tokens,
        "error": response.error
    }
    
    print(f"   Status: {status['status']}")
    
    if status['status'] == 'succeeded':
        print(f"   ✅ Training complete!")
        print(f"   Fine-tuned model: {status['fine_tuned_model']}")
        print(f"   Tokens trained: {status['trained_tokens']:,}")
    elif status['status'] == 'failed':
        print(f"   ❌ Training failed")
        if status['error']:
            print(f"   Error: {status['error']}")
    elif status['status'] == 'running':
        print(f"   ⏳ Training in progress...")
        if status['trained_tokens']:
            print(f"   Tokens trained so far: {status['trained_tokens']:,}")
    else:
        print(f"   Current status: {status['status']}")
    
    # Get recent events
    events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id, limit=5)
    if events.data:
        print("\n   Recent events:")
        for event in events.data[:5]:
            print(f"   - {event.message}")
    
    return status


def list_finetune_jobs(client) -> list:
    """List all fine-tuning jobs."""
    print("\n📋 Listing fine-tuning jobs...")
    
    response = client.fine_tuning.jobs.list(limit=10)
    
    jobs = []
    for job in response.data:
        job_info = {
            "id": job.id,
            "status": job.status,
            "model": job.model,
            "fine_tuned_model": job.fine_tuned_model,
            "created_at": str(job.created_at)
        }
        jobs.append(job_info)
        
        print(f"\n   Job: {job_info['id']}")
        print(f"   Status: {job_info['status']}")
        print(f"   Base model: {job_info['model']}")
        if job_info['fine_tuned_model']:
            print(f"   Fine-tuned: {job_info['fine_tuned_model']}")
    
    if not jobs:
        print("   No fine-tuning jobs found.")
    
    return jobs


def test_model(client, model_id: str, prompt: str = None):
    """Test the fine-tuned model."""
    if prompt is None:
        prompt = "Greet me in your special way and tell me about African culture."
    
    print(f"\n🧪 Testing model: {model_id}")
    print(f"   Prompt: {prompt}")
    print("\n" + "-" * 50)
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    reply = response.choices[0].message.content
    
    print(f"\n🤖 Sisi Lola says:\n")
    print(reply)
    print("\n" + "-" * 50)
    
    # Show usage
    print(f"\n📊 Usage: {response.usage.total_tokens} tokens")
    
    return reply


def cancel_job(client, job_id: str):
    """Cancel a fine-tuning job."""
    print(f"\n🛑 Cancelling job: {job_id}")
    
    response = client.fine_tuning.jobs.cancel(job_id)
    print(f"   Status: {response.status}")


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
        description="Sisi Lola OpenAI Fine-Tuning Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate training data (check format and estimate cost)
  python finetune_openai.py --action validate --data sisi_lola_openai.jsonl

  # Create a new fine-tuning job
  python finetune_openai.py --action create --data sisi_lola_openai.jsonl

  # Check job status
  python finetune_openai.py --action status --job-id ftjob-xxx

  # List all jobs
  python finetune_openai.py --action list

  # Test a fine-tuned model
  python finetune_openai.py --action test --model ft:gpt-3.5-turbo:org:sisi-lola:xxx

  # Cancel a job
  python finetune_openai.py --action cancel --job-id ftjob-xxx
        """
    )
    
    parser.add_argument('--action', required=True,
                       choices=['create', 'status', 'list', 'test', 'validate', 'cancel'],
                       help='Action to perform')
    parser.add_argument('--data', help='Training data file (JSONL)')
    parser.add_argument('--job-id', help='Fine-tuning job ID')
    parser.add_argument('--model', help='Fine-tuned model ID for testing')
    parser.add_argument('--prompt', help='Test prompt', default=None)
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌍 SISI LOLA - OPENAI FINE-TUNING MANAGER")
    print("=" * 60)
    
    try:
        client = get_openai_client()
        print("✅ OpenAI client initialized")
        
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
            
            # Confirm cost
            print(f"\n⚠️  Estimated cost: {stats['estimated_cost']}")
            confirm = input("   Proceed with fine-tuning? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("   Cancelled.")
                return
            
            # Upload and create job
            file_id = upload_file(client, filepath)
            job = create_finetune_job(client, file_id)
            
            print(f"\n✅ Fine-tuning job created!")
            print(f"   Job ID: {job['job_id']}")
            print(f"\n   Check status with:")
            print(f"   python finetune_openai.py --action status --job-id {job['job_id']}")
        
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
        
        elif args.action == 'cancel':
            if not args.job_id:
                raise ValueError("--job-id required for cancel action")
            cancel_job(client, args.job_id)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
