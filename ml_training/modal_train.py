"""
Modal.com Cloud GPU Training for Sisi Lola Nigerian AI

This script runs the brain training on Modal's cloud infrastructure with GPU support.
Free tier includes $30 credits (~60 training runs on T4 GPU).

Usage:
    # Test locally first (no GPU)
    modal run modal_train.py::train_brain --local
    
    # Run on Modal cloud with GPU
    modal run modal_train.py::train_brain
    
    # Deploy as scheduled job
    modal deploy modal_train.py
"""

import modal
import os
from pathlib import Path

# Create Modal app
app = modal.App("sisi-lola-training")

# Define the Docker image with all dependencies
training_image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "torch==2.5.1",
    "transformers>=4.36.0",
    "peft>=0.7.0",
    "datasets>=2.15.0",
    "accelerate>=0.25.0",
    "bitsandbytes>=0.41.0",
    "huggingface_hub>=0.19.0",
    "scipy",
    "sentencepiece",
    "protobuf",
)

# Volume to persist trained models
model_volume = modal.Volume.from_name("sisi-lola-models", create_if_missing=True)

# Secret for HuggingFace token
hf_secret = modal.Secret.from_name("huggingface-secret")


@app.function(
    image=training_image,
    gpu="T4",  # Free tier compatible, 16GB VRAM
    timeout=1800,  # 30 minutes max
    secrets=[hf_secret],
    volumes={"/models": model_volume},
)
def train_brain(
    base_model: str = "gpt2",
    push_to_hub: bool = True,
    hub_repo: str = "sisilolalive/sisi-lola-brain",
):
    """Train the Sisi Lola brain adapter on Modal GPU"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import Dataset
    from huggingface_hub import HfApi, login
    
    print("=" * 60)
    print("🧠 SISI LOLA BRAIN TRAINING ON MODAL")
    print("=" * 60)
    
    # Check GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f}GB)")
    else:
        print("⚠️ No GPU detected, training on CPU")
    
    # Login to HuggingFace
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("✅ Logged in to HuggingFace")
    
    # Load model and tokenizer
    print(f"\n📦 Loading base model: {base_model}")
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    
    # Determine LoRA target modules based on architecture
    model_name_lower = base_model.lower()
    if "gpt2" in model_name_lower or "gpt-2" in model_name_lower:
        target_modules = ["c_attn", "c_proj"]
    else:  # LLaMA, Mistral, etc.
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
    
    print(f"🎯 LoRA target modules: {target_modules}")
    
    # Configure LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=target_modules,
    )
    
    model = get_peft_model(model, lora_config)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 Trainable parameters: {trainable_params:,}")
    
    # Nigerian personality training data
    training_texts = [
        # Lagos street slang and expressions
        "Wetin dey happen? Make we yarn about this matter small small.",
        "Omo, this thing sweet die! Lagos no dey carry last.",
        "E be like say you no sabi the way things dey run for here.",
        "Abeg, no vex. We go sort this matter out sharp sharp.",
        "The thing wey you dey find, e dey your front. Open your eyes well.",
        
        # Warm Nigerian hospitality
        "Welcome welcome! You are most welcome. Come, sit down, let me serve you something.",
        "How body? Hope say you dey kampe? Your family nko?",
        "Ah ah! Long time no see! Where you been hiding yourself?",
        "No worry yourself, everything go dey alright. Na so life be.",
        "You try well well. I appreciate your effort plenty plenty.",
        
        # Yoruba-influenced expressions
        "Ah, ẹ kú àárọ̀! Good morning, my dear. How did you sleep?",
        "Ó dára! That is good. You have done well.",
        "Pẹ̀lẹ́ o, sorry about that. May God comfort you.",
        "E jọ̀ọ́, please help me with this small thing.",
        
        # Tech-savvy Nigerian expressions
        "Gbedu plenty for this new AI thing wey I discover.",
        "Your tech skills sharp well well! You sabi this thing die.",
        "Make we deploy this code sharp sharp, deadline dey near.",
        "The algorithm dey work correct. No wahala at all.",
        
        # Encouragement and motivation
        "You get am! I believe in you plenty. Go show them pepper!",
        "No let anybody tell you wetin you no fit do. You be champion!",
        "Rise and shine! Today na your day to shine bright like diamond.",
        "Even if e hard, no give up. The hustle must pay one day.",
        
        # Food and culture references
        "Make I put extra pepper for your jollof? Na the way we like am.",
        "Suya with cold drink, under moonlight. Na enjoyment be that!",
        "Mama put food sweet well well. Nothing compare to home cooking.",
        
        # Sisi Lola personality - warm, witty, helpful
        "As your digital sister from Lagos, I go always dey here for you.",
        "No wahala, make we solve this problem together. Two heads better.",
        "Chai! You don work hard today. Make you rest small now.",
        "I understand say the matter hard, but we go find way.",
        "You fit ask me anything. I no go judge you at all.",
    ]
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=256,
            padding="max_length",
        )
    
    dataset = Dataset.from_dict({"text": training_texts})
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Add labels for causal LM
    def add_labels(examples):
        examples["labels"] = examples["input_ids"].copy()
        return examples
    
    tokenized_dataset = tokenized_dataset.map(add_labels, batched=True)
    
    # Training arguments
    output_dir = "/models/natlas_lora"
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=2,
        learning_rate=3e-4,
        warmup_steps=50,
        logging_steps=10,
        save_steps=100,
        fp16=torch.cuda.is_available(),
        report_to="none",
        remove_unused_columns=False,
    )
    
    # Train
    print("\n🚀 Starting training...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )
    
    trainer.train()
    
    # Save model
    print(f"\n💾 Saving model to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Commit volume changes
    model_volume.commit()
    
    # Push to HuggingFace Hub
    if push_to_hub and hf_token:
        print(f"\n📤 Pushing to HuggingFace Hub: {hub_repo}")
        api = HfApi()
        api.upload_folder(
            folder_path=output_dir,
            repo_id=hub_repo,
            repo_type="model",
            commit_message="🧠 Modal cloud training update",
        )
        print(f"✅ Pushed to https://huggingface.co/{hub_repo}")
    
    print("\n" + "=" * 60)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 60)
    
    return {
        "status": "success",
        "base_model": base_model,
        "trainable_params": trainable_params,
        "output_dir": output_dir,
        "hub_repo": hub_repo if push_to_hub else None,
    }


@app.function(
    image=training_image,
    timeout=300,
    secrets=[hf_secret],
    volumes={"/models": model_volume},
)
def create_voice_profile(push_to_hub: bool = True, hub_repo: str = "sisilolalive/sisi-lola-voice"):
    """Create/update voice profile (no GPU needed for EdgeTTS)"""
    import json
    from huggingface_hub import HfApi, login
    
    print("=" * 60)
    print("🎤 SISI LOLA VOICE PROFILE CREATION")
    print("=" * 60)
    
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
    
    output_dir = "/models/xtts_sisi_lola"
    os.makedirs(output_dir, exist_ok=True)
    
    # Voice profile configuration
    voice_profile = {
        "name": "Sisi Lola",
        "description": "Warm, friendly Nigerian AI assistant voice",
        "tts_engine": "edge_tts",
        "voice_id": "en-NG-EzinneNeural",
        "language": "en-NG",
        "speaking_rate": "+5%",
        "pitch": "+2Hz",
        "personality_traits": {
            "warmth": 0.9,
            "energy": 0.75,
            "formality": 0.4,
            "humor": 0.7,
        },
        "speech_patterns": {
            "greetings": ["Wetin dey!", "How body?", "Ẹ kú àárọ̀!"],
            "affirmations": ["Correct!", "E good!", "Na so!"],
            "expressions": ["Omo!", "Chai!", "Wahala!"],
        },
    }
    
    profile_path = os.path.join(output_dir, "voice_profile.json")
    with open(profile_path, "w") as f:
        json.dump(voice_profile, f, indent=2)
    
    print(f"✅ Voice profile saved to {profile_path}")
    
    # Commit volume
    model_volume.commit()
    
    if push_to_hub and hf_token:
        print(f"\n📤 Pushing to HuggingFace Hub: {hub_repo}")
        api = HfApi()
        api.upload_folder(
            folder_path=output_dir,
            repo_id=hub_repo,
            repo_type="model",
            commit_message="🎤 Modal voice profile update",
        )
        print(f"✅ Pushed to https://huggingface.co/{hub_repo}")
    
    return {"status": "success", "profile": voice_profile}


@app.function(
    image=training_image,
    gpu="T4",
    timeout=2400,  # 40 minutes for full pipeline
    secrets=[hf_secret],
    volumes={"/models": model_volume},
)
def train_full_pipeline(base_model: str = "gpt2"):
    """Run complete training pipeline: brain + voice"""
    print("=" * 60)
    print("🚀 SISI LOLA FULL TRAINING PIPELINE")
    print("=" * 60)
    
    # Train brain
    brain_result = train_brain.local(base_model=base_model, push_to_hub=True)
    
    # Create voice profile
    voice_result = create_voice_profile.local(push_to_hub=True)
    
    return {
        "brain": brain_result,
        "voice": voice_result,
    }


@app.local_entrypoint()
def main(
    model: str = "gpt2",
    full_pipeline: bool = False,
):
    """CLI entrypoint for Modal training"""
    if full_pipeline:
        result = train_full_pipeline.remote(base_model=model)
    else:
        result = train_brain.remote(base_model=model)
    
    print("\n📊 Training Result:")
    print(result)
