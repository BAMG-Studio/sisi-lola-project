#!/usr/bin/env python3
"""
Robust Voice Dataset Downloader for Sisi Lola
Uses batch download mode for reliability
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

def main():
    print("=" * 60)
    print("    SISI LOLA VOICE DATASET DOWNLOADER")
    print("    Nigerian Languages: Yoruba, Hausa, Igbo")
    print("=" * 60)
    
    # Install requirements
    import subprocess
    packages = ["datasets", "soundfile", "librosa", "tqdm", "huggingface_hub"]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
    
    import soundfile as sf
    import numpy as np
    from tqdm import tqdm
    from datasets import load_dataset, Audio
    
    # Output directory
    OUTPUT_DIR = Path(__file__).parent / "ml_training" / "data" / "voice_samples"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\nOutput Directory: {OUTPUT_DIR}")
    
    # Configuration for each language
    languages = [
        {"name": "yoruba", "code": "yo_ng", "label": "Yoruba"},
        {"name": "hausa", "code": "ha_ng", "label": "Hausa"},
        {"name": "igbo", "code": "ig_ng", "label": "Igbo"},
    ]
    
    total_downloaded = 0
    total_female = 0
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        print(f"DOWNLOADING FLEURS {lang['label'].upper()}")
        print("=" * 60)
        
        lang_dir = OUTPUT_DIR / f"fleurs_{lang['name']}"
        female_dir = lang_dir / "female"
        male_dir = lang_dir / "male"
        female_dir.mkdir(parents=True, exist_ok=True)
        male_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Loading FLEURS {lang['label']} dataset (batch mode)...")
            
            # Load in batch mode (not streaming) - more reliable
            ds = load_dataset(
                "google/fleurs",
                lang['code'],
                split="train",
                trust_remote_code=True
            )
            
            # Cast audio to proper format
            ds = ds.cast_column("audio", Audio(sampling_rate=16000))
            
            print(f"Dataset size: {len(ds)} samples")
            
            count = 0
            female_count = 0
            max_samples = min(100, len(ds))
            
            print(f"Processing {max_samples} samples...")
            
            for i in tqdm(range(max_samples)):
                try:
                    sample = ds[i]
                    audio = sample.get("audio", {})
                    
                    if not audio:
                        continue
                    
                    audio_array = np.array(audio.get("array", []))
                    sample_rate = audio.get("sampling_rate", 16000)
                    
                    if len(audio_array) == 0:
                        continue
                    
                    # Get metadata
                    gender = sample.get("gender", 0)  # 0=male, 1=female
                    speaker_id = sample.get("speaker_id", i)
                    
                    # Determine output directory
                    if gender == 1:
                        female_count += 1
                        output_subdir = female_dir
                        gender_label = "f"
                    else:
                        output_subdir = male_dir
                        gender_label = "m"
                    
                    # Create filename
                    filename = f"fleurs_{lang['name']}_{count:04d}_{gender_label}_spk{speaker_id}.wav"
                    filepath = output_subdir / filename
                    
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
            
            print(f"\n✅ {lang['label']}: Downloaded {count} samples")
            print(f"   Female: {female_count}, Male: {count - female_count}")
            
            total_downloaded += count
            total_female += female_count
            
        except Exception as e:
            print(f"❌ Error downloading {lang['label']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create speaker reference candidates
    print(f"\n{'=' * 60}")
    print("CREATING SPEAKER REFERENCE CANDIDATES")
    print("=" * 60)
    
    ref_dir = OUTPUT_DIR / "speaker_reference_candidates"
    ref_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect female samples
    female_samples = []
    for lang_dir in OUTPUT_DIR.iterdir():
        if lang_dir.is_dir() and "fleurs" in lang_dir.name:
            female_path = lang_dir / "female"
            if female_path.exists():
                for wav in female_path.glob("*.wav"):
                    try:
                        info = sf.info(wav)
                        if 3 <= info.duration <= 30:
                            female_samples.append({
                                "path": wav,
                                "duration": info.duration,
                                "lang": lang_dir.name
                            })
                    except:
                        continue
    
    print(f"Found {len(female_samples)} female samples")
    
    # Sort by ideal duration (10-15 seconds is best)
    female_samples.sort(key=lambda x: abs(x["duration"] - 12))
    
    # Copy top 10 candidates
    import shutil
    for i, sample in enumerate(female_samples[:10]):
        dest = ref_dir / f"candidate_{i+1}_{sample['lang']}_{sample['duration']:.1f}s.wav"
        shutil.copy2(sample["path"], dest)
        print(f"  Created: {dest.name}")
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": total_downloaded,
        "total_female": total_female,
        "output_directory": str(OUTPUT_DIR)
    }
    
    with open(OUTPUT_DIR / "download_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"\nTotal samples: {total_downloaded}")
    print(f"Female samples: {total_female}")
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"\nSpeaker reference candidates: {ref_dir}")
    print("\nNext steps:")
    print("1. Review candidates and select best female voice")
    print("2. Copy as 'speaker_reference.wav' for XTTS training")

if __name__ == "__main__":
    main()
