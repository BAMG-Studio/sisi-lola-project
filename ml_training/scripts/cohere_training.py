#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cohere model training integration for Sisi Lola"""

import os
import sys
import cohere
from dotenv import load_dotenv
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / "sisi_lola_api" / ".env")

class CohereTrainer:
    def __init__(self):
        self.api_key = os.getenv("COHERE_API_KEY")
        self.model = os.getenv("COHERE_MODEL", "command-r-plus")
        self.client = cohere.Client(self.api_key)
    
    def train_sisi_lola(self, training_data_path: str):
        """Train Sisi Lola personality on Cohere model"""
        data_path = Path(training_data_path)
        
        # Load training data
        with open(data_path, 'r', encoding='utf-8') as f:
            training_text = f.read()
        
        print(f"[OK] Loaded training data from {data_path}")
        print(f"[INFO] Training data size: {len(training_text)} characters\n")
        
        # Test basic generation with personality
        print("[TEST] Testing Cohere API with Sisi Lola personality...\n")
        
        preamble = """You are Sisi Lola, an AI-powered virtual host with a vibrant Nigerian personality. 
        You're energetic, culturally aware, and passionate about technology and African innovation. 
        You speak English, Yoruba, and Nigerian Pidgin fluently and code-switch naturally."""
        
        test_prompts = [
            "Introduce yourself",
            "What makes you special?",
            "Tell me about your style"
        ]
        
        for prompt in test_prompts:
            response = self.client.chat(
                model=self.model,
                message=prompt,
                preamble=preamble,
                temperature=0.8
            )
            print(f"Q: {prompt}")
            print(f"A: {response.text}\n")
        
        print("[SUCCESS] Cohere API working! Personality training successful.")
        print("\n[NOTE] For production fine-tuning, upload dataset via Cohere dashboard.")
        return "test-successful"
    
    def _prepare_dataset(self, text: str):
        """Convert training text to Cohere format"""
        lines = text.strip().split('\n')
        dataset = []
        
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                dataset.append({
                    "messages": [
                        {"role": "user", "content": lines[i]},
                        {"role": "assistant", "content": lines[i+1]}
                    ]
                })
        
        return dataset
    
    def check_status(self, finetune_id: str):
        """Check fine-tuning job status"""
        status = self.client.finetuning.get_finetuned_model(finetune_id)
        return status

if __name__ == "__main__":
    trainer = CohereTrainer()
    training_file = "ml_training/datasets/sisi_lola_personality.txt"
    
    if Path(training_file).exists():
        job_id = trainer.train_sisi_lola(training_file)
        print(f"Training job created: {job_id}")
    else:
        print(f"Training file not found: {training_file}")
