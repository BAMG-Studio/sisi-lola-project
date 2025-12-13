#!/usr/bin/env python3
"""
Download Igbo FLEURS using batch mode with explicit download
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("    IGBO FLEURS DOWNLOADER (batch mode)")
    print("=" * 60)
    
    import soundfile as sf
    import numpy as np
    from datasets import load_dataset, Audio
    
    OUTPUT_DIR = Path(__file__).parent / "ml_training" / "data" / "voice_samples"
    lang_dir = OUTPUT_DIR / "fleurs_igbo"
    female_dir = lang_dir / "female"
    male_dir = lang_dir / "male"
    female_dir.mkdir(parents=True, exist_ok=True)
    male_dir.mkdir(parents=True, exist_ok=True)
    
    # Check existing
    existing_female = len(list(female_dir.glob("*.wav")))
    existing_male = len(list(male_dir.glob("*.wav")))
    total_existing = existing_female + existing_male
    
    print(f"Currently have: {existing_female} female, {existing_male} male = {total_existing} total")
    
    if total_existing >= 100:
        print("Already have enough samples!")
        return
    
    print("\nDownloading FLEURS Igbo dataset in batch mode...")
    print("This will download the full dataset to cache first (~2.4GB)...")
    print("Please wait...\n")
    
    try:
        # Use batch mode - downloads full dataset then processes
        ds = load_dataset(
            "google/fleurs",
            "ig_ng",
            split="train",
            trust_remote_code=True
        )
        
        # Cast audio
        ds = ds.cast_column("audio", Audio(sampling_rate=16000))
        
        print(f"Dataset loaded: {len(ds)} samples")
        
        count = 0
        female_count = 0
        max_samples = 100
        
        for i in range(min(max_samples, len(ds))):
            sample = ds[i]
            
            try:
                audio = sample.get("audio", {})
                if not audio:
                    continue
                
                audio_array = audio.get("array", None)
                sr = audio.get("sampling_rate", 16000)
                
                if audio_array is None or len(audio_array) == 0:
                    continue
                
                gender = sample.get("gender", 0)
                is_female = gender == 1
                
                text = sample.get("transcription", sample.get("sentence", ""))[:50].replace(" ", "_")
                text = "".join(c for c in text if c.isalnum() or c == "_")
                
                target_dir = female_dir if is_female else male_dir
                filename = f"igbo_{count:04d}_{text[:30]}.wav"
                filepath = target_dir / filename
                
                # Skip if file exists
                if filepath.exists():
                    count += 1
                    if is_female:
                        female_count += 1
                    continue
                
                audio_np = np.array(audio_array, dtype=np.float32)
                sf.write(str(filepath), audio_np, sr)
                
                count += 1
                if is_female:
                    female_count += 1
                
                if count % 10 == 0:
                    print(f"  Progress: {count}/{max_samples}")
                    
            except Exception as e:
                print(f"  Error on sample {i}: {e}")
                continue
        
        print(f"\n✅ Igbo: Downloaded {count} samples")
        print(f"   Female: {female_count}, Male: {count - female_count}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Final count
    print("\n" + "=" * 60)
    print("FINAL COUNT")
    print("=" * 60)
    final_female = len(list(female_dir.glob("*.wav")))
    final_male = len(list(male_dir.glob("*.wav")))
    print(f"Igbo: {final_female} female, {final_male} male = {final_female + final_male} total")

if __name__ == "__main__":
    main()
