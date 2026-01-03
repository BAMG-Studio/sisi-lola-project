#!/usr/bin/env python3
"""
🇳🇬 YORUNGLISH/PIDGIN ENGLISH DOWNLOADER
Downloads Nigerian Pidgin English samples from Hugging Face
"""

import subprocess
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_SAMPLES_ROOT = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_samples"

# Create folders
PIDGIN_FEMALE = VOICE_SAMPLES_ROOT / "yorunglish_pidgin_female"
PIDGIN_MALE = VOICE_SAMPLES_ROOT / "yorunglish_pidgin_male"
PIDGIN_FEMALE.mkdir(parents=True, exist_ok=True)
PIDGIN_MALE.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("🇳🇬 YORUNGLISH/PIDGIN ENGLISH DOWNLOADER")
print("=" * 60)

# Install required packages
print("\n📦 Installing required packages...")
subprocess.run([sys.executable, "-m", "pip", "install", "datasets", "soundfile", "librosa", "scipy", "-q"])

print("\n📥 Downloading Nigerian Pidgin English dataset...")
print("   Source: Hugging Face (asr-nigerian-pidgin/nigerian-pidgin-1.0)")
print("   This may take a few minutes...\n")

try:
    from datasets import load_dataset, Audio
    import soundfile as sf
    import numpy as np
    
    # Load the dataset with audio decoding
    print("🔄 Loading dataset from Hugging Face...")
    dataset = load_dataset("asr-nigerian-pidgin/nigerian-pidgin-1.0", split="train")
    
    # Cast audio column to decode properly
    print("🔄 Decoding audio...")
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
    
    total = len(dataset)
    print(f"✅ Found {total} samples\n")
    
    # Save samples (limit to prevent huge download)
    max_samples = 500  # Can increase if needed
    saved_female = 0
    saved_male = 0
    
    print(f"📥 Downloading up to {max_samples} samples...")
    
    for i, sample in enumerate(dataset):
        if i >= max_samples:
            break
        
        audio = sample["audio"]
        text = sample.get("text", sample.get("sentence", ""))
        gender = sample.get("gender", "unknown")
        
        # Determine folder based on gender
        if gender.lower() in ["female", "f"]:
            output_dir = PIDGIN_FEMALE
            saved_female += 1
            prefix = "pidgin_f"
            count = saved_female
        elif gender.lower() in ["male", "m"]:
            output_dir = PIDGIN_MALE
            saved_male += 1
            prefix = "pidgin_m"
            count = saved_male
        else:
            # Default to female folder for unknown
            output_dir = PIDGIN_FEMALE
            saved_female += 1
            prefix = "pidgin_u"
            count = saved_female
        
        # Save audio
        audio_path = output_dir / f"{prefix}_{count:04d}.wav"
        sf.write(str(audio_path), audio["array"], audio["sampling_rate"])
        
        # Save transcription
        if text:
            txt_path = output_dir / f"{prefix}_{count:04d}.txt"
            with open(txt_path, "w") as f:
                f.write(text)
        
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{max_samples} (Female: {saved_female}, Male: {saved_male})")
    
    print(f"\n✅ DOWNLOAD COMPLETE!")
    print(f"   📁 Female samples: {saved_female} files → {PIDGIN_FEMALE}")
    print(f"   📁 Male samples: {saved_male} files → {PIDGIN_MALE}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Try: pip install datasets soundfile")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📝 MANUAL ALTERNATIVE:")
    print("   1. Go to: https://huggingface.co/datasets/asr-nigerian-pidgin/nigerian-pidgin-1.0")
    print("   2. Click 'Files and versions'")
    print("   3. Download the audio files manually")

print("\n" + "=" * 60)
print("🎯 NEXT: Select best samples and copy to 'selected_best' folder")
print("=" * 60)
