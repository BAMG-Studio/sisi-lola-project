#!/usr/bin/env python3
"""
Download and process Nigerian Pidgin voice dataset
Uses the asr-nigerian-pidgin/nigerian-pidgin-1.0 dataset
"""

import os
import sys
import subprocess

# Install requirements
for pkg in ["datasets", "soundfile", "librosa", "numpy", "tqdm"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

from pathlib import Path
import soundfile as sf
import numpy as np
from tqdm import tqdm
from datasets import load_dataset, Audio

OUTPUT_DIR = Path(__file__).parent / "ml_training" / "data" / "voice_samples"

def download_nigerian_pidgin():
    """Download and process Nigerian Pidgin dataset."""
    print("="*60)
    print("   DOWNLOADING NIGERIAN PIDGIN VOICE DATASET")
    print("="*60)
    
    pidgin_dir = OUTPUT_DIR / "nigerian_pidgin"
    female_dir = pidgin_dir / "female"
    male_dir = pidgin_dir / "male"
    unknown_dir = pidgin_dir / "unknown"
    
    female_dir.mkdir(parents=True, exist_ok=True)
    male_dir.mkdir(parents=True, exist_ok=True)
    unknown_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("\nLoading Nigerian Pidgin dataset...")
        print("Source: asr-nigerian-pidgin/nigerian-pidgin-1.0")
        
        # Load the dataset
        ds = load_dataset(
            "asr-nigerian-pidgin/nigerian-pidgin-1.0",
            split="train",
            trust_remote_code=True
        )
        
        print(f"Dataset loaded: {len(ds)} samples")
        
        # Cast audio to standard format
        ds = ds.cast_column("audio", Audio(sampling_rate=16000))
        
        count = 0
        female_count = 0
        male_count = 0
        max_samples = min(150, len(ds))
        
        print(f"\nProcessing {max_samples} samples...")
        
        for i in tqdm(range(max_samples), desc="Processing Pidgin"):
            try:
                sample = ds[i]
                audio = sample.get("audio", {})
                
                if not audio:
                    continue
                
                audio_array = np.array(audio.get("array", []))
                sample_rate = audio.get("sampling_rate", 16000)
                
                if len(audio_array) == 0:
                    continue
                
                # Check for gender field (may not exist in this dataset)
                gender = sample.get("gender", None)
                speaker_id = sample.get("speaker_id", sample.get("client_id", i))
                
                # Determine output directory
                if gender == "female" or gender == 1:
                    output_dir = female_dir
                    gender_label = "f"
                    female_count += 1
                elif gender == "male" or gender == 0:
                    output_dir = male_dir
                    gender_label = "m"
                    male_count += 1
                else:
                    output_dir = unknown_dir
                    gender_label = "u"
                
                # Create filename
                filename = f"pidgin_{count:04d}_{gender_label}_spk{speaker_id}.wav"
                filepath = output_dir / filename
                
                # Resample to 22050Hz for XTTS
                import librosa
                audio_resampled = librosa.resample(
                    audio_array.astype(np.float32),
                    orig_sr=sample_rate,
                    target_sr=22050
                )
                
                # Save as WAV
                sf.write(filepath, audio_resampled, 22050)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ Nigerian Pidgin: {count} samples processed")
        print(f"   Female: {female_count}")
        print(f"   Male: {male_count}")
        print(f"   Unknown gender: {count - female_count - male_count}")
        print(f"\nOutput: {pidgin_dir}")
        
        return count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    print("="*60)
    print("   SISI LOLA - NIGERIAN PIDGIN VOICE DOWNLOADER")
    print("="*60)
    print(f"\nOutput Directory: {OUTPUT_DIR}")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download and process
    count = download_nigerian_pidgin()
    
    if count > 0:
        print("\n" + "="*60)
        print("DOWNLOAD COMPLETE!")
        print("="*60)
        print(f"\nTotal samples: {count}")
        print("\nTo update speaker reference candidates, run:")
        print("  python create_speaker_reference.py")

if __name__ == "__main__":
    main()
