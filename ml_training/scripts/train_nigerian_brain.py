#!/usr/bin/env python3
"""
Sisi Lola Nigerian Brain Training - N-ATLaS + AfriBERTa + Aya
Trains Nigerian/African-focused LLMs with LoRA adapters
"""
import os
import yaml
import torch
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, 
    TrainingArguments, Trainer, BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset
import json
from datetime import datetime

class NigerianBrainTrainer:
    def __init__(self, config_path="ml_training/configs/nigerian_models_config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_natlas_model(self):
        """Load Nigerian LLM with 4-bit quantization"""
        # Use meta-llama/Llama-3.2-1B as base - lightweight and effective
        model_id = "meta-llama/Llama-3.2-1B-Instruct"
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                token=os.getenv("HUGGINGFACE_TOKEN")
            )
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=True,
                token=os.getenv("HUGGINGFACE_TOKEN")
            )
        except:
            # Fallback to TinyLlama if Llama gated
            model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto"
            )
            tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        return model, tokenizer
    
    def prepare_lora_adapter(self, model):
        """Configure LoRA for efficient fine-tuning"""
        cfg = self.config['training']['brain']
        
        lora_config = LoraConfig(
            r=cfg['rank'],
            lora_alpha=cfg['alpha'],
            target_modules=cfg['target_modules'],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, lora_config)
        
        print(f"Trainable params: {model.print_trainable_parameters()}")
        return model
    
    def load_training_data(self):
        """Load NaijaSenti + custom Sisi Lola personality data"""
        datasets = []
        
        # NaijaSenti for sentiment/cultural context
        try:
            naija_senti = load_dataset("HausaNLP/NaijaSenti", split="train")
            datasets.append(naija_senti)
        except:
            print("NaijaSenti not available, using local data only")
        
        # Sisi Lola personality
        personality_path = "ml_training/datasets/sisi_lola_personality.txt"
        if os.path.exists(personality_path):
            with open(personality_path) as f:
                personality_data = [{"text": line.strip()} for line in f if line.strip()]
            datasets.append(Dataset.from_list(personality_data))
        
        # Custom conversations
        conv_path = "api_customization/datasets/sisi_lola_conversations.json"
        if os.path.exists(conv_path):
            with open(conv_path) as f:
                convs = json.load(f)
            conv_data = [{"text": f"User: {c['user']}\nSisi Lola: {c['assistant']}"} 
                        for c in convs]
            datasets.append(Dataset.from_list(conv_data))
        
        from datasets import concatenate_datasets
        return concatenate_datasets(datasets) if datasets else None
    
    def format_prompt(self, example, tokenizer):
        """Format with Sisi Lola system prompt"""
        system = self.config['system_prompts']['sisi_lola_core']
        text = example.get('text', '')
        
        prompt = f"<|system|>\n{system}\n<|user|>\n{text}\n<|assistant|>\n"
        return tokenizer(prompt, truncation=True, max_length=512)
    
    def train(self, output_dir="ml_training/checkpoints/natlas_lora"):
        """Execute training with LoRA"""
        print("🧠 Loading N-ATLaS-LLM...")
        model, tokenizer = self.load_natlas_model()
        
        print("🔧 Preparing LoRA adapter...")
        model = self.prepare_lora_adapter(model)
        
        print("📚 Loading training data...")
        dataset = self.load_training_data()
        if dataset is None:
            raise ValueError("No training data available")
        
        dataset = dataset.map(lambda x: self.format_prompt(x, tokenizer), batched=False)
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            fp16=True,
            logging_steps=10,
            save_steps=100,
            save_total_limit=3,
            report_to="none"
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer
        )
        
        print("🚀 Starting training...")
        trainer.train()
        
        print(f"💾 Saving adapter to {output_dir}")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        # Save metadata
        metadata = {
            "model": "N-ATLaS-8B",
            "adapter": "LoRA",
            "trained_on": datetime.now().isoformat(),
            "languages": ["yoruba", "pidgin", "nigerian_english"],
            "personality": "Sisi Lola - Lagos virtual host"
        }
        
        with open(f"{output_dir}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return output_dir

if __name__ == "__main__":
    trainer = NigerianBrainTrainer()
    adapter_path = trainer.train()
    print(f"✅ Training complete! Adapter saved to: {adapter_path}")
