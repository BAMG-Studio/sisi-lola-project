#!/usr/bin/env python3
"""
Setup script for Nigerian models - downloads and validates all required models
"""
import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download, login
import torch

def check_gpu():
    """Check GPU availability"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f} GB)")
        return True
    else:
        print("⚠️  No GPU detected - training will be slow")
        return False

def login_huggingface():
    """Login to Hugging Face"""
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("❌ HUGGINGFACE_TOKEN not found in environment")
        print("   Set it with: export HUGGINGFACE_TOKEN=your_token")
        return False
    
    try:
        login(token=token)
        print("✅ Logged in to Hugging Face")
        return True
    except Exception as e:
        print(f"❌ HuggingFace login failed: {e}")
        return False

def download_natlas():
    """Download N-ATLaS model"""
    print("\n📥 Downloading N-ATLaS-8B...")
    try:
        model_path = snapshot_download(
            repo_id="NCAIR1/N-ATLaS-8B",
            cache_dir="models/natlas",
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        print(f"✅ N-ATLaS downloaded to: {model_path}")
        return True
    except Exception as e:
        print(f"❌ N-ATLaS download failed: {e}")
        return False

def download_xtts():
    """Download XTTS-v2 model"""
    print("\n📥 Downloading XTTS-v2...")
    try:
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        print("✅ XTTS-v2 downloaded")
        return True
    except Exception as e:
        print(f"❌ XTTS-v2 download failed: {e}")
        return False

def download_datasets():
    """Download training datasets"""
    print("\n📥 Downloading NaijaSenti dataset...")
    try:
        from datasets import load_dataset
        dataset = load_dataset("HausaNLP/NaijaSenti", split="train")
        print(f"✅ NaijaSenti downloaded ({len(dataset)} samples)")
        return True
    except Exception as e:
        print(f"⚠️  NaijaSenti download failed: {e}")
        print("   Will use local data only")
        return False

def validate_voice_samples():
    """Check voice samples"""
    voice_dir = Path("04_AUDIO_CORE/voice_samples")
    wav_files = list(voice_dir.glob("*.wav"))
    
    print(f"\n🎤 Voice samples: {len(wav_files)} found")
    
    if len(wav_files) < 5:
        print("⚠️  Need at least 5 voice samples for training")
        print(f"   Add more .wav files to {voice_dir}")
        return False
    
    print("✅ Sufficient voice samples")
    return True

def create_directories():
    """Create required directories"""
    dirs = [
        "ml_training/checkpoints/natlas_lora",
        "ml_training/checkpoints/xtts_sisi_lola",
        "ml_training/outputs",
        "ml_training/logs",
        "ml_training/datasets",
        "models/natlas",
        "models/xtts"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def main():
    print("=" * 60)
    print("🚀 SISI LOLA NIGERIAN MODELS SETUP")
    print("=" * 60)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    gpu_ok = check_gpu()
    hf_ok = login_huggingface()
    
    if not hf_ok:
        print("\n❌ Setup failed - HuggingFace login required")
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Download models
    natlas_ok = download_natlas()
    xtts_ok = download_xtts()
    
    # Download datasets
    dataset_ok = download_datasets()
    
    # Validate voice samples
    voice_ok = validate_voice_samples()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    print(f"GPU Available: {'✅' if gpu_ok else '⚠️ '}")
    print(f"HuggingFace Login: {'✅' if hf_ok else '❌'}")
    print(f"N-ATLaS Model: {'✅' if natlas_ok else '❌'}")
    print(f"XTTS-v2 Model: {'✅' if xtts_ok else '❌'}")
    print(f"NaijaSenti Dataset: {'✅' if dataset_ok else '⚠️ '}")
    print(f"Voice Samples: {'✅' if voice_ok else '⚠️ '}")
    
    if natlas_ok and xtts_ok and voice_ok:
        print("\n✅ Setup complete! Ready to train.")
        print("\nNext steps:")
        print("  1. Review config: ml_training/configs/nigerian_models_config.yaml")
        print("  2. Run training: python ml_training/scripts/unified_training_orchestrator.py")
    else:
        print("\n⚠️  Setup incomplete - resolve issues above before training")
        sys.exit(1)

if __name__ == "__main__":
    main()
