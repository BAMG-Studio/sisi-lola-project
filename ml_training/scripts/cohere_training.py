#!/usr/bin/env python3
"""Cohere model training integration for Sisi Lola"""

import os
import cohere
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

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
        
        # Create fine-tuning dataset
        dataset = self._prepare_dataset(training_text)
        
        # Upload dataset to Cohere
        dataset_response = self.client.datasets.create(
            name="sisi_lola_personality",
            data=dataset,
            dataset_type="chat-finetune-input"
        )
        
        print(f"Dataset uploaded: {dataset_response.id}")
        
        # Create fine-tune job
        finetune_response = self.client.finetuning.create_finetuned_model(
            request={
                "name": "sisi-lola-v1",
                "settings": {
                    "base_model": {
                        "base_type": self.model
                    },
                    "dataset_id": dataset_response.id,
                    "hyperparameters": {
                        "train_epochs": 3,
                        "learning_rate": 0.00001
                    }
                }
            }
        )
        
        print(f"Fine-tuning started: {finetune_response.id}")
        return finetune_response.id
    
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
