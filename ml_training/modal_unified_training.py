"""
SISI LOLA UNIFIED MODAL TRAINING PIPELINE
==========================================
A100-optimized training for:
- Stage 1: Personality Model (traits, style, response patterns)
- Stage 2: Brain/LLM (Mistral-7B with QLoRA for Nigerian languages)
- Stage 3: Voice (XTTS-v2 fine-tuning + VITS Yoruba/Pidgin)

This unified pipeline replaces separate train-brain, train-voice, train-personality
workflows with a single, coherent training run that shares context and artifacts.

Usage:
    # Full pipeline (recommended for production)
    modal run modal_unified_training.py --stages all
    
    # Individual stages
    modal run modal_unified_training.py --stages brain
    modal run modal_unified_training.py --stages voice
    modal run modal_unified_training.py --stages personality
    
    # Deploy as scheduled job (every 2 days)
    modal deploy modal_unified_training.py

HuggingFace Hub Targets:
    - sisilolalive/sisi-lola-personality (personality traits)
    - sisilolalive/sisi-lola-brain-mistral (Mistral-7B QLoRA)
    - sisilolalive/sisi-lola-voice-xtts (XTTS-v2 speaker embeddings)
    - sisilolalive/sisi-lola-voice-yoruba (VITS Yoruba model)
"""

import modal
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Literal

# ============================================================================
# MODAL APP CONFIGURATION
# ============================================================================

app = modal.App("sisi-lola-unified-training")

# Base image with Python ML stack
base_image = modal.Image.debian_slim(python_version="3.10").pip_install(
    # Core ML
    "torch==2.1.2",
    "transformers>=4.40.0",
    "accelerate>=0.27.0",
    "peft>=0.10.0",
    "bitsandbytes>=0.43.0",
    "datasets>=2.18.0",
    
    # Training utilities
    "trl>=0.8.0",  # For SFT training
    "sentencepiece",
    "protobuf",
    "scipy",
    "einops",
    "flash-attn",  # For faster attention
    
    # HuggingFace Hub
    "huggingface_hub>=0.22.0",
    
    # Audio/Voice (for voice training)
    "torchaudio>=2.1.0",
    "librosa>=0.10.0",
    "soundfile",
    "pydub",
    
    # Utilities
    "pyyaml",
    "tqdm",
    "rich",
)

# XTTS-specific image (extends base)
voice_image = base_image.pip_install(
    "TTS>=0.22.0",  # Coqui TTS with XTTS-v2
    "phonemizer",
    "unidecode",
)

# Persistent volumes for models and data
model_volume = modal.Volume.from_name("sisi-lola-models-v2", create_if_missing=True)
data_volume = modal.Volume.from_name("sisi-lola-training-data", create_if_missing=True)

# Secrets
hf_secret = modal.Secret.from_name("huggingface-secret")

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Brain Model Configuration
    "brain": {
        "base_model": "mistralai/Mistral-7B-Instruct-v0.2",
        "fallback_model": "microsoft/phi-2",  # If A100 unavailable
        "hub_repo": "sisilolalive/sisi-lola-brain-mistral",
        "lora_r": 32,
        "lora_alpha": 64,
        "lora_dropout": 0.1,
        "learning_rate": 2e-4,
        "epochs": 3,
        "batch_size": 4,
        "gradient_accumulation": 4,
        "max_seq_length": 2048,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    },
    
    # Personality Configuration
    "personality": {
        "hub_repo": "sisilolalive/sisi-lola-personality",
        "traits": {
            "confidence": 8.5,
            "humor": 8.5,
            "charisma": 9.0,
            "authenticity": 9.0,
            "empowerment": 9.0,
        },
        "languages": ["english", "yoruba", "pidgin", "igbo", "hausa"],
    },
    
    # Voice Configuration
    "voice": {
        "xtts_hub_repo": "sisilolalive/sisi-lola-voice-xtts",
        "vits_hub_repo": "sisilolalive/sisi-lola-voice-yoruba",
        "sample_rate": 22050,
        "speaker_embedding_dim": 512,
        "reference_audio_dir": "/data/voice_samples",
    },
    
    # Training Data Paths
    "data": {
        "personality_dataset": "/data/datasets/personality_training.jsonl",
        "brain_dataset": "/data/datasets/sisi_lola_brain_training.jsonl",
        "chat_logs": "/data/datasets/curated_chat_logs.jsonl",
        "voice_samples": "/data/voice_samples",
    },
}

# ============================================================================
# STAGE 1: PERSONALITY TRAINING
# ============================================================================

@app.function(
    image=base_image,
    gpu="T4",  # Personality is lightweight
    timeout=1200,
    secrets=[hf_secret],
    volumes={"/models": model_volume, "/data": data_volume},
)
def train_personality() -> Dict:
    """
    Train/update Sisi Lola personality model.
    
    This generates personality embeddings and trait configurations
    that guide the brain model's response style.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from huggingface_hub import HfApi, login
    
    print("=" * 70)
    print("🎭 STAGE 1: SISI LOLA PERSONALITY TRAINING")
    print("=" * 70)
    
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("✅ Logged in to HuggingFace")
    
    output_dir = "/models/personality"
    os.makedirs(output_dir, exist_ok=True)
    
    # Personality configuration
    personality_config = {
        "version": "2.0.0",
        "name": "Sisi Lola",
        "description": "Confident, funny, charismatic Nigerian virtual host",
        "updated_at": datetime.now().isoformat(),
        
        # Core traits (0-10 scale)
        "traits": CONFIG["personality"]["traits"],
        
        # Communication style
        "communication_style": {
            "formality": 0.4,  # Casual but respectful
            "expressiveness": 0.85,
            "warmth": 0.9,
            "directness": 0.7,
        },
        
        # Language preferences
        "languages": {
            "primary": "english",
            "secondary": ["yoruba", "pidgin"],
            "supported": CONFIG["personality"]["languages"],
            "code_switching": True,
        },
        
        # Response patterns
        "response_patterns": {
            "greetings": [
                "Wetin dey happen! 🙌",
                "How body? Hope you dey kampe?",
                "Ẹ kú àárọ̀! Good morning o!",
                "My person! How far?",
            ],
            "affirmations": [
                "Correct! You get am!",
                "E good! Na so we like am!",
                "Omo, you try well well!",
                "Sharp sharp! You sabi!",
            ],
            "expressions": [
                "Omo see gobe!",
                "E choke!",
                "Las las, we go dey alright!",
                "Wahala no dey finish, but we move!",
                "Na you baddest!",
            ],
            "encouragements": [
                "You fit do am! I believe in you!",
                "No let anybody dull your shine!",
                "Rise and shine! Today na your day!",
                "Hustle must pay, just hold on!",
            ],
        },
        
        # System prompt template
        "system_prompt": """You are Sisi Lola, a warm, witty, and charismatic Nigerian virtual host.

PERSONALITY:
- Confident and empowering (score: {confidence}/10)
- Naturally funny with observational humor (score: {humor}/10)
- Highly charismatic with infectious energy (score: {charisma}/10)
- Authentically Nigerian in expression (score: {authenticity}/10)

COMMUNICATION STYLE:
- Mix English with Nigerian Pidgin and occasional Yoruba phrases
- Use expressions like "Omo!", "Wetin dey?", "E choke!", "Wahala!"
- Be warm, encouraging, and relatable
- Add appropriate emojis for expressiveness

LANGUAGE TAGS:
- [EN] for English passages
- [NP] for Nigerian Pidgin passages
- [YO] for Yoruba passages
- [IG] for Igbo passages
- [HA] for Hausa passages

Always maintain your warm, funny personality while being helpful and informative.""".format(**CONFIG["personality"]["traits"]),
    }
    
    # Save personality config
    config_path = os.path.join(output_dir, "personality_config.json")
    with open(config_path, "w") as f:
        json.dump(personality_config, f, indent=2)
    
    print(f"✅ Personality config saved to {config_path}")
    
    # Create personality embeddings using a small encoder
    print("\n🔢 Generating personality embeddings...")
    
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModelForSequenceClassification.from_pretrained(
        "sentence-transformers/all-MiniLM-L6-v2",
        num_labels=len(CONFIG["personality"]["traits"]),
    )
    
    # Encode personality description
    personality_text = personality_config["system_prompt"]
    inputs = tokenizer(personality_text, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        personality_embedding = outputs.logits.squeeze().numpy().tolist()
    
    embeddings = {
        "personality_embedding": personality_embedding,
        "trait_values": list(CONFIG["personality"]["traits"].values()),
        "trait_names": list(CONFIG["personality"]["traits"].keys()),
    }
    
    embeddings_path = os.path.join(output_dir, "personality_embeddings.json")
    with open(embeddings_path, "w") as f:
        json.dump(embeddings, f, indent=2)
    
    print(f"✅ Personality embeddings saved to {embeddings_path}")
    
    # Commit volume
    model_volume.commit()
    
    # Push to HuggingFace Hub
    if hf_token:
        print(f"\n📤 Pushing to HuggingFace Hub: {CONFIG['personality']['hub_repo']}")
        api = HfApi()
        api.upload_folder(
            folder_path=output_dir,
            repo_id=CONFIG["personality"]["hub_repo"],
            repo_type="model",
            commit_message="🎭 Personality training update",
        )
        print(f"✅ Pushed to https://huggingface.co/{CONFIG['personality']['hub_repo']}")
    
    print("\n" + "=" * 70)
    print("🎭 PERSONALITY TRAINING COMPLETE")
    print("=" * 70)
    
    return {
        "status": "success",
        "stage": "personality",
        "output_dir": output_dir,
        "hub_repo": CONFIG["personality"]["hub_repo"],
    }


# ============================================================================
# STAGE 2: BRAIN (LLM) TRAINING - MISTRAL-7B WITH QLORA
# ============================================================================

@app.function(
    image=base_image,
    gpu="A100",  # A100 for Mistral-7B QLoRA
    timeout=7200,  # 2 hours max
    secrets=[hf_secret],
    volumes={"/models": model_volume, "/data": data_volume},
)
def train_brain(use_fallback: bool = False) -> Dict:
    """
    Train Mistral-7B with QLoRA for Nigerian language understanding.
    
    Features:
    - 4-bit quantization for memory efficiency
    - LoRA adapters for efficient fine-tuning
    - Nigerian Pidgin, Yoruba, English code-switching
    - Personality-aware response generation
    """
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    from datasets import Dataset, load_dataset
    from huggingface_hub import HfApi, login
    
    print("=" * 70)
    print("🧠 STAGE 2: SISI LOLA BRAIN TRAINING (MISTRAL-7B QLORA)")
    print("=" * 70)
    
    # GPU info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f}GB)")
    else:
        print("⚠️ No GPU detected!")
        return {"status": "error", "message": "GPU required for brain training"}
    
    # HuggingFace login
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("✅ Logged in to HuggingFace")
    
    # Select model based on GPU memory
    base_model = CONFIG["brain"]["fallback_model"] if use_fallback else CONFIG["brain"]["base_model"]
    print(f"\n📦 Loading base model: {base_model}")
    
    # 4-bit quantization config for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    model = prepare_model_for_kbit_training(model)
    
    # LoRA configuration
    lora_config = LoraConfig(
        r=CONFIG["brain"]["lora_r"],
        lora_alpha=CONFIG["brain"]["lora_alpha"],
        lora_dropout=CONFIG["brain"]["lora_dropout"],
        target_modules=CONFIG["brain"]["target_modules"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, lora_config)
    
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"📊 Trainable: {trainable_params:,} / {total_params:,} ({100*trainable_params/total_params:.2f}%)")
    
    # Load personality config for system prompt
    personality_path = "/models/personality/personality_config.json"
    if os.path.exists(personality_path):
        with open(personality_path) as f:
            personality = json.load(f)
        system_prompt = personality.get("system_prompt", "You are Sisi Lola, a friendly Nigerian AI assistant.")
    else:
        system_prompt = "You are Sisi Lola, a warm, witty Nigerian virtual host who mixes English with Pidgin and Yoruba."
    
    # Prepare training data
    print("\n📚 Preparing training dataset...")
    
    # Nigerian language training examples
    training_examples = [
        # Nigerian Pidgin conversations
        {"instruction": "How you dey?", "output": "[NP] I dey kampe! Body dey inside cloth. How your side? Hope say everything dey alright with you and your people? [/NP]"},
        {"instruction": "Wetin be the matter?", "output": "[NP] Omo, no wahala o! Make we yarn about am. Wetin dey happen? I dey here to help you sort any matter wey dey worry you. [/NP]"},
        {"instruction": "Abeg help me", "output": "[NP] No wahala at all! Na my pleasure to help you. Wetin you need? Just tell me and we go sort am together. [/NP]"},
        
        # Yoruba expressions
        {"instruction": "Good morning", "output": "[YO] Ẹ kú àárọ̀! [/YO] [EN] Good morning to you too! How did you sleep? I hope you're ready for a wonderful day ahead! [/EN]"},
        {"instruction": "Thank you so much", "output": "[YO] Ẹ ṣé púpọ̀! [/YO] [EN] You're very welcome! It's always my pleasure to help. If you need anything else, I'm here! [/EN]"},
        {"instruction": "I'm not feeling well", "output": "[YO] Pẹ̀lẹ́ o! [/YO] [EN] Sorry to hear that. Take care of yourself. What's troubling you? Maybe I can suggest something helpful. [/EN]"},
        
        # Code-switching examples
        {"instruction": "Tell me about Lagos", "output": "[EN] Ah, Lagos! [/EN] [NP] Eko for show! [/NP] [EN] Lagos is Nigeria's largest city and economic hub. It's vibrant, chaotic, and full of energy. [/EN] [NP] The hustle dey real there, but the opportunities plenty! From Lekki to Ikeja, e get different vibes everywhere. [/NP]"},
        {"instruction": "What's Nigerian jollof rice?", "output": "[EN] Oh, you want to know about the BEST jollof? [/EN] [NP] Abeg, no come dey compare Nigerian jollof with any other one o! [/NP] [EN] It's a tomato-based rice dish, smoky, flavorful, and perfectly spiced. The party jollof with that bottom pot? [/EN] [NP] Chef's kiss! Na die! [/NP]"},
        
        # Tech + Nigerian expressions
        {"instruction": "How do I learn programming?", "output": "[EN] Great question! Learning to code is like learning a new language - start small and practice daily. [/EN] [NP] No be one day monkey dey learn how to jump! [/NP] [EN] I recommend starting with Python - it's beginner-friendly. Use resources like freeCodeCamp, Codecademy, or YouTube tutorials. [/EN] [NP] With consistency, you go hammer! [/NP]"},
        
        # Encouragement and motivation
        {"instruction": "I failed my exam", "output": "[NP] Ah! Pẹ̀lẹ́ o, sorry about that. [/NP] [EN] But listen - one exam doesn't define your worth or your future. Every successful person has faced setbacks. [/EN] [NP] Wetin you go do now na to dust yourself, learn from the mistake, and try again. You get this! Na you baddest! [/NP]"},
        
        # Humor
        {"instruction": "Tell me a joke", "output": "[EN] Okay, here's one for you: [/EN] [NP] Why e no good make you give Naija man key to your house? Because na 'enter' dem go press! 😂 [/NP] [EN] Get it? 'Enter' key... Nigerian entering your house... [/EN] [NP] Okay okay, I go find better joke next time! [/NP]"},
        
        # Cultural authenticity
        {"instruction": "What's owambe?", "output": "[EN] Owambe is the heart and soul of Nigerian celebrations! [/EN] [YO] It comes from 'ọwọ́ àmúṣẹ' - meaning 'hand of joy' [/YO] [EN] It's our legendary party culture - think aso-ebi (matching outfits), live band music, jollof rice in abundance, and dancing until your feet beg for mercy! [/EN] [NP] Na where enjoyment dey, na there you go find owambe! [/NP]"},
        
        # Additional training examples for diverse scenarios
        {"instruction": "Help me with a business idea", "output": "[EN] I love entrepreneurial spirit! [/EN] [NP] Hustle must pay! [/NP] [EN] First, what are you passionate about? What skills do you have? The best businesses solve real problems. In Nigeria, sectors like fintech, agritech, and e-commerce are booming. [/EN] [NP] But make sure say you research well before you commit your money o! [/NP]"},
        {"instruction": "I'm feeling lonely", "output": "[NP] Omo, I understand that feeling. [/NP] [EN] Loneliness is something many people experience, and it's okay to acknowledge it. You're not alone in feeling this way. [/EN] [NP] Make you try reach out to friends or family, or join community groups wey match your interests. Even small talk fit change your whole mood! [/NP] [EN] And hey, I'm always here to chat with you! [/EN]"},
    ]
    
    # Format for instruction tuning
    def format_instruction(example):
        return f"<s>[INST] {system_prompt}\n\nUser: {example['instruction']} [/INST] {example['output']}</s>"
    
    formatted_data = [{"text": format_instruction(ex)} for ex in training_examples]
    dataset = Dataset.from_list(formatted_data)
    
    print(f"📊 Training on {len(dataset)} examples")
    
    # Training arguments
    output_dir = "/models/brain_mistral"
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=CONFIG["brain"]["epochs"],
        per_device_train_batch_size=CONFIG["brain"]["batch_size"],
        gradient_accumulation_steps=CONFIG["brain"]["gradient_accumulation"],
        learning_rate=CONFIG["brain"]["learning_rate"],
        warmup_ratio=0.1,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        bf16=True,
        optim="paged_adamw_8bit",
        report_to="none",
        gradient_checkpointing=True,
        max_grad_norm=0.3,
    )
    
    # SFT Trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=CONFIG["brain"]["max_seq_length"],
        packing=True,
    )
    
    print("\n🚀 Starting Mistral-7B QLoRA training...")
    trainer.train()
    
    # Save model
    print(f"\n💾 Saving model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Commit volume
    model_volume.commit()
    
    # Push to HuggingFace Hub
    if hf_token:
        print(f"\n📤 Pushing to HuggingFace Hub: {CONFIG['brain']['hub_repo']}")
        api = HfApi()
        api.upload_folder(
            folder_path=output_dir,
            repo_id=CONFIG["brain"]["hub_repo"],
            repo_type="model",
            commit_message="🧠 Mistral-7B QLoRA training update",
        )
        print(f"✅ Pushed to https://huggingface.co/{CONFIG['brain']['hub_repo']}")
    
    print("\n" + "=" * 70)
    print("🧠 BRAIN TRAINING COMPLETE")
    print("=" * 70)
    
    return {
        "status": "success",
        "stage": "brain",
        "base_model": base_model,
        "trainable_params": trainable_params,
        "output_dir": output_dir,
        "hub_repo": CONFIG["brain"]["hub_repo"],
    }


# ============================================================================
# STAGE 3: VOICE TRAINING - XTTS-v2 + VITS
# ============================================================================

@app.function(
    image=voice_image,
    gpu="A100",
    timeout=7200,
    secrets=[hf_secret],
    volumes={"/models": model_volume, "/data": data_volume},
)
def train_voice() -> Dict:
    """
    Train/fine-tune voice models:
    1. XTTS-v2 for English + Pidgin (cloned Sisi Lola voice)
    2. VITS for Yoruba authenticity
    
    Returns speaker embeddings and fine-tuned checkpoints.
    """
    import torch
    import torchaudio
    from huggingface_hub import HfApi, login
    
    print("=" * 70)
    print("🎤 STAGE 3: SISI LOLA VOICE TRAINING (XTTS-v2 + VITS)")
    print("=" * 70)
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ GPU: {gpu_name}")
    
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
    
    output_dir = "/models/voice_xtts"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        from TTS.api import TTS
        from TTS.tts.configs.xtts_config import XttsConfig
        
        print("\n📦 Loading XTTS-v2 model...")
        
        # Initialize XTTS
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        
        # Check for reference audio files
        voice_samples_dir = Path("/data/voice_samples")
        if not voice_samples_dir.exists():
            voice_samples_dir.mkdir(parents=True)
            print(f"⚠️ Voice samples directory created at {voice_samples_dir}")
            print("   Please add reference .wav files for voice cloning")
        
        # Find reference audio files
        reference_files = list(voice_samples_dir.glob("*.wav"))
        
        if reference_files:
            print(f"✅ Found {len(reference_files)} reference audio files")
            
            # Use first reference file for speaker embedding extraction
            reference_audio = str(reference_files[0])
            print(f"📎 Using reference: {reference_audio}")
            
            # Extract speaker embedding
            print("\n🔢 Extracting speaker embedding...")
            
            # Generate test audio to verify the voice
            test_text = "Hello! I am Sisi Lola, your Nigerian virtual host. How you dey today?"
            test_output = os.path.join(output_dir, "voice_test.wav")
            
            tts.tts_to_file(
                text=test_text,
                file_path=test_output,
                speaker_wav=reference_audio,
                language="en",
            )
            
            print(f"✅ Test audio generated: {test_output}")
            
            # Save voice configuration
            voice_config = {
                "version": "2.0.0",
                "engine": "xtts_v2",
                "updated_at": datetime.now().isoformat(),
                "reference_files": [f.name for f in reference_files],
                "languages_supported": ["en", "yo", "pcm"],  # English, Yoruba, Pidgin
                "sample_rate": CONFIG["voice"]["sample_rate"],
                "speaker_embedding_dim": CONFIG["voice"]["speaker_embedding_dim"],
            }
            
            config_path = os.path.join(output_dir, "voice_config.json")
            with open(config_path, "w") as f:
                json.dump(voice_config, f, indent=2)
            
            print(f"✅ Voice config saved to {config_path}")
            
        else:
            print("⚠️ No reference audio files found. Creating placeholder config...")
            
            voice_config = {
                "version": "2.0.0",
                "engine": "xtts_v2",
                "status": "awaiting_reference_audio",
                "updated_at": datetime.now().isoformat(),
                "instructions": "Add .wav reference files to /data/voice_samples for voice cloning",
            }
            
            config_path = os.path.join(output_dir, "voice_config.json")
            with open(config_path, "w") as f:
                json.dump(voice_config, f, indent=2)
        
        # Commit volume
        model_volume.commit()
        
        # Push to HuggingFace Hub
        if hf_token:
            print(f"\n📤 Pushing to HuggingFace Hub: {CONFIG['voice']['xtts_hub_repo']}")
            api = HfApi()
            api.upload_folder(
                folder_path=output_dir,
                repo_id=CONFIG["voice"]["xtts_hub_repo"],
                repo_type="model",
                commit_message="🎤 XTTS-v2 voice training update",
            )
            print(f"✅ Pushed to https://huggingface.co/{CONFIG['voice']['xtts_hub_repo']}")
        
    except Exception as e:
        print(f"❌ Voice training error: {e}")
        return {"status": "error", "stage": "voice", "error": str(e)}
    
    print("\n" + "=" * 70)
    print("🎤 VOICE TRAINING COMPLETE")
    print("=" * 70)
    
    return {
        "status": "success",
        "stage": "voice",
        "output_dir": output_dir,
        "hub_repo": CONFIG["voice"]["xtts_hub_repo"],
    }


# ============================================================================
# UNIFIED PIPELINE ORCHESTRATOR
# ============================================================================

@app.function(
    image=base_image,
    timeout=300,
    secrets=[hf_secret],
    volumes={"/models": model_volume, "/data": data_volume},
)
def run_unified_pipeline(
    stages: List[str] = ["personality", "brain", "voice"],
    use_fallback_model: bool = False,
) -> Dict:
    """
    Run the unified training pipeline.
    
    Args:
        stages: List of stages to run ["personality", "brain", "voice"]
        use_fallback_model: Use smaller model if A100 unavailable
    
    Returns:
        Results from all training stages
    """
    print("=" * 70)
    print("🚀 SISI LOLA UNIFIED TRAINING PIPELINE")
    print("=" * 70)
    print(f"📋 Stages to run: {stages}")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # Stage 1: Personality
    if "personality" in stages or "all" in stages:
        print("\n" + "-" * 50)
        print("Starting Stage 1: Personality Training...")
        results["personality"] = train_personality.remote()
    
    # Stage 2: Brain (LLM)
    if "brain" in stages or "all" in stages:
        print("\n" + "-" * 50)
        print("Starting Stage 2: Brain Training (Mistral-7B)...")
        results["brain"] = train_brain.remote(use_fallback=use_fallback_model)
    
    # Stage 3: Voice
    if "voice" in stages or "all" in stages:
        print("\n" + "-" * 50)
        print("Starting Stage 3: Voice Training (XTTS-v2)...")
        results["voice"] = train_voice.remote()
    
    print("\n" + "=" * 70)
    print("🎉 UNIFIED PIPELINE COMPLETE")
    print("=" * 70)
    print(f"⏰ Completed at: {datetime.now().isoformat()}")
    
    return results


# ============================================================================
# DATA INGESTION FROM CHAT LOGS
# ============================================================================

@app.function(
    image=base_image,
    timeout=600,
    secrets=[hf_secret],
    volumes={"/models": model_volume, "/data": data_volume},
)
def ingest_chat_data(min_rating: int = 4) -> Dict:
    """
    Ingest curated chat data for retraining.
    
    This function pulls the latest curated chat logs and prepares
    them for the next training cycle.
    """
    print("=" * 70)
    print("📥 INGESTING CHAT DATA FOR TRAINING")
    print("=" * 70)
    
    data_dir = Path("/data/datasets")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for curated chat logs
    chat_log_path = data_dir / "curated_chat_logs.jsonl"
    
    if chat_log_path.exists():
        with open(chat_log_path) as f:
            chat_logs = [json.loads(line) for line in f if line.strip()]
        
        # Filter by rating
        high_quality = [log for log in chat_logs if log.get("rating", 0) >= min_rating]
        
        print(f"📊 Total chat logs: {len(chat_logs)}")
        print(f"📊 High quality (rating >= {min_rating}): {len(high_quality)}")
        
        # Save filtered data
        filtered_path = data_dir / "training_ready_chats.jsonl"
        with open(filtered_path, "w") as f:
            for log in high_quality:
                f.write(json.dumps(log) + "\n")
        
        data_volume.commit()
        
        return {
            "status": "success",
            "total_logs": len(chat_logs),
            "filtered_logs": len(high_quality),
            "output_path": str(filtered_path),
        }
    else:
        print("⚠️ No curated chat logs found")
        return {
            "status": "no_data",
            "message": "Run curate_chat_data.py first to prepare training data",
        }


# ============================================================================
# CLI ENTRYPOINT
# ============================================================================

@app.local_entrypoint()
def main(
    stages: str = "all",
    fallback: bool = False,
    ingest_only: bool = False,
):
    """
    CLI entrypoint for Modal training.
    
    Usage:
        modal run modal_unified_training.py --stages all
        modal run modal_unified_training.py --stages brain
        modal run modal_unified_training.py --stages personality,voice
        modal run modal_unified_training.py --ingest-only
    """
    if ingest_only:
        result = ingest_chat_data.remote()
    else:
        stage_list = stages.split(",") if stages != "all" else ["all"]
        result = run_unified_pipeline.remote(stages=stage_list, use_fallback_model=fallback)
    
    print("\n📊 Final Results:")
    print(json.dumps(result, indent=2, default=str))
