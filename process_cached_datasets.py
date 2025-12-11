#!/usr/bin/env python3
"""
Process cached FLEURS datasets (Hausa and Igbo)
Uses already-downloaded cache data
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

def process_language(lang_code, lang_name):
    """Process a single language from cached data."""
    print(f"\n{'='*60}")
    print(f"PROCESSING FLEURS {lang_name.upper()}")
    print("="*60)
    
    lang_dir = OUTPUT_DIR / f"fleurs_{lang_name}"
    female_dir = lang_dir / "female"
    male_dir = lang_dir / "male"
    
    # Check if already processed
    existing_female = len(list(female_dir.glob("*.wav"))) if female_dir.exists() else 0
    if existing_female >= 50:
        print(f"Already have {existing_female} female samples. Skipping.")
        return existing_female
    
    female_dir.mkdir(parents=True, exist_ok=True)
    male_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"Loading cached {lang_name} dataset...")
        ds = load_dataset(
            "google/fleurs",
            lang_code,
            split="train",
            trust_remote_code=True
        )
        
        ds = ds.cast_column("audio", Audio(sampling_rate=16000))
        
        print(f"Dataset size: {len(ds)} samples")
        
        count = 0
        female_count = 0
        max_samples = min(100, len(ds))
        
        for i in tqdm(range(max_samples), desc=f"Processing {lang_name}"):
            try:
                sample = ds[i]
                audio = sample.get("audio", {})
                
                if not audio:
                    continue
                
                audio_array = np.array(audio.get("array", []))
                sample_rate = audio.get("sampling_rate", 16000)
                
                if len(audio_array) == 0:
                    continue
                
                gender = sample.get("gender", 0)
                speaker_id = sample.get("speaker_id", i)
                
                if gender == 1:
                    female_count += 1
                    output_dir = female_dir
                    gender_label = "f"
                else:
                    output_dir = male_dir
                    gender_label = "m"
                
                filename = f"fleurs_{lang_name}_{count:04d}_{gender_label}_spk{speaker_id}.wav"
                filepath = output_dir / filename
                
                # Resample to 22050Hz
                import librosa
                audio_resampled = librosa.resample(
                    audio_array.astype(np.float32),
                    orig_sr=sample_rate,
                    target_sr=22050
                )
                
                sf.write(filepath, audio_resampled, 22050)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ {lang_name}: {count} samples (Female: {female_count})")
        return count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    print("="*60)
    print("   PROCESS CACHED FLEURS DATASETS")
    print("="*60)
    
    # Process Hausa (already cached)
    hausa_count = process_language("ha_ng", "hausa")
    
    # Try Igbo (may need to download)
    igbo_count = process_language("ig_ng", "igbo")
    
    print(f"\n{'='*60}")
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Hausa samples: {hausa_count}")
    print(f"Igbo samples: {igbo_count}")
    
    # Update speaker reference if we got new samples
    if hausa_count > 0 or igbo_count > 0:
        print("\nRun create_speaker_reference.py to update candidates!")

if __name__ == "__main__":
    main()
