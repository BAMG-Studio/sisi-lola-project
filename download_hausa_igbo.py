#!/usr/bin/env python3
"""
Direct downloader for Hausa and Igbo FLEURS datasets
Uses smaller batches with timeout handling and retry logic
"""

import os
import sys
import time
from pathlib import Path

def main():
    print("=" * 60)
    print("    HAUSA & IGBO DOWNLOADER (with retry)")
    print("=" * 60)
    
    import soundfile as sf
    import numpy as np
    from tqdm import tqdm
    from datasets import load_dataset, Audio
    
    OUTPUT_DIR = Path(__file__).parent / "ml_training" / "data" / "voice_samples"
    
    languages = [
        {"name": "hausa", "code": "ha_ng", "label": "Hausa"},
        {"name": "igbo", "code": "ig_ng", "label": "Igbo"},
    ]
    
    max_retries = 5
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"DOWNLOADING FLEURS {lang['label'].upper()}")
        print("=" * 60)
        
        lang_dir = OUTPUT_DIR / f"fleurs_{lang['name']}"
        female_dir = lang_dir / "female"
        male_dir = lang_dir / "male"
        female_dir.mkdir(parents=True, exist_ok=True)
        male_dir.mkdir(parents=True, exist_ok=True)
        
        for retry in range(max_retries):
            # Check current progress
            existing_female = len(list(female_dir.glob("*.wav")))
            existing_male = len(list(male_dir.glob("*.wav")))
            total_existing = existing_female + existing_male
            
            if total_existing >= 100:
                print(f"Already has {existing_female} female, {existing_male} male ({total_existing} total) - done!")
                break
            
            print(f"\nAttempt {retry + 1}/{max_retries}: Have {total_existing} samples, need {100 - total_existing} more...")
            
            try:
                # Try streaming mode
                ds = load_dataset(
                    "google/fleurs",
                    lang['code'],
                    split="train",
                    streaming=True,
                    trust_remote_code=True
                )
                
                count = total_existing
                female_count = existing_female
                max_samples = 100
                
                for i, sample in enumerate(ds):
                    if count >= max_samples:
                        break
                    
                    # Skip already downloaded
                    if i < total_existing:
                        continue
                    
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
                        filename = f"{lang['name']}_{count:04d}_{text[:30]}.wav"
                        filepath = target_dir / filename
                        
                        audio_np = np.array(audio_array, dtype=np.float32)
                        sf.write(str(filepath), audio_np, sr)
                        
                        count += 1
                        if is_female:
                            female_count += 1
                        
                        # Progress every 10 samples
                        if count % 10 == 0:
                            print(f"  Progress: {count}/{max_samples} samples")
                        
                    except Exception as e:
                        print(f"  Error on sample {i}: {e}")
                        continue
                
                print(f"✅ Downloaded {count} samples total")
                if count >= max_samples:
                    break
                    
            except Exception as e:
                print(f"Error on attempt {retry + 1}: {e}")
                print("Waiting 5 seconds before retry...")
                time.sleep(5)
                continue
    
    # Final summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    
    for lang in languages:
        lang_dir = OUTPUT_DIR / f"fleurs_{lang['name']}"
        female_count = len(list((lang_dir / "female").glob("*.wav")))
        male_count = len(list((lang_dir / "male").glob("*.wav")))
        print(f"{lang['label']}: {female_count} female, {male_count} male = {female_count + male_count} total")

if __name__ == "__main__":
    main()
