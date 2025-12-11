#!/usr/bin/env python3
"""
Quick Voice Dataset Downloader for Sisi Lola
Downloads smaller targeted samples for voice training
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add virtual environment to path
venv_path = Path(__file__).parent / ".venv" / "Lib" / "site-packages"
if venv_path.exists():
    sys.path.insert(0, str(venv_path))

def install_requirements():
    """Install required packages."""
    import subprocess
    packages = ["datasets", "soundfile", "librosa", "tqdm", "huggingface_hub"]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

install_requirements()

import soundfile as sf
import numpy as np
from tqdm import tqdm
from datasets import load_dataset
from huggingface_hub import hf_hub_download

# Output directory
OUTPUT_DIR = Path(__file__).parent / "ml_training" / "data" / "voice_samples"

def ensure_directory(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def download_common_voice_nigerian():
    """
    Download Nigerian English samples from Common Voice.
    These are high-quality, validated voice samples.
    """
    print("\n" + "=" * 60)
    print("DOWNLOADING COMMON VOICE NIGERIAN ENGLISH")
    print("=" * 60)
    
    output_dir = ensure_directory(OUTPUT_DIR / "common_voice_ng")
    
    try:
        # Load a small subset of Common Voice
        print("Loading dataset (this may take a moment)...")
        ds = load_dataset(
            "mozilla-foundation/common_voice_16_1",
            "en",  # English
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        
        # Filter for Nigerian accents if available
        count = 0
        female_count = 0
        max_samples = 50
        
        print(f"Downloading up to {max_samples} samples...")
        
        for sample in tqdm(ds, total=max_samples):
            if count >= max_samples:
                break
                
            try:
                audio = sample.get("audio", {})
                if not audio:
                    continue
                    
                audio_array = audio.get("array")
                sample_rate = audio.get("sampling_rate", 48000)
                
                if audio_array is None:
                    continue
                
                # Get metadata
                gender = sample.get("gender", "unknown")
                client_id = sample.get("client_id", f"speaker_{count}")[:8]
                
                # Prioritize female voices
                if gender == "female":
                    female_count += 1
                    subdir = "female"
                elif gender == "male":
                    subdir = "male"
                else:
                    subdir = "unknown"
                
                # Save audio
                speaker_dir = ensure_directory(output_dir / subdir)
                filename = f"cv_ng_{count:04d}_{client_id}.wav"
                filepath = speaker_dir / filename
                
                # Resample to 22050Hz if needed
                if sample_rate != 22050:
                    import librosa
                    audio_array = librosa.resample(
                        np.array(audio_array), 
                        orig_sr=sample_rate, 
                        target_sr=22050
                    )
                    sample_rate = 22050
                
                sf.write(filepath, audio_array, sample_rate)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ Downloaded {count} Common Voice samples")
        print(f"   Female voices: {female_count}")
        return count
        
    except Exception as e:
        print(f"❌ Error downloading Common Voice: {e}")
        return 0

def download_fleurs_yoruba():
    """
    Download FLEURS Yoruba dataset.
    Google's high-quality multilingual speech dataset.
    """
    print("\n" + "=" * 60)
    print("DOWNLOADING FLEURS YORUBA")
    print("=" * 60)
    
    output_dir = ensure_directory(OUTPUT_DIR / "fleurs_yoruba")
    
    try:
        print("Loading FLEURS Yoruba dataset...")
        ds = load_dataset(
            "google/fleurs",
            "yo_ng",  # Yoruba (Nigeria)
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        
        count = 0
        female_count = 0
        max_samples = 100
        
        print(f"Downloading up to {max_samples} Yoruba samples...")
        
        for sample in tqdm(ds, total=max_samples):
            if count >= max_samples:
                break
                
            try:
                audio = sample.get("audio", {})
                if not audio:
                    continue
                    
                audio_array = audio.get("array")
                sample_rate = audio.get("sampling_rate", 16000)
                
                if audio_array is None:
                    continue
                
                # Get metadata
                gender = sample.get("gender", 0)  # 0=male, 1=female in FLEURS
                speaker_id = sample.get("speaker_id", count)
                
                # Determine gender subdirectory
                if gender == 1:
                    female_count += 1
                    subdir = "female"
                elif gender == 0:
                    subdir = "male"
                else:
                    subdir = "unknown"
                
                # Save audio
                speaker_dir = ensure_directory(output_dir / subdir)
                filename = f"fleurs_yo_{count:04d}_spk{speaker_id}.wav"
                filepath = speaker_dir / filename
                
                # Resample to 22050Hz
                import librosa
                audio_array = librosa.resample(
                    np.array(audio_array), 
                    orig_sr=sample_rate, 
                    target_sr=22050
                )
                
                sf.write(filepath, audio_array, 22050)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ Downloaded {count} FLEURS Yoruba samples")
        print(f"   Female voices: {female_count}")
        return count
        
    except Exception as e:
        print(f"❌ Error downloading FLEURS Yoruba: {e}")
        return 0

def download_fleurs_hausa():
    """
    Download FLEURS Hausa dataset.
    """
    print("\n" + "=" * 60)
    print("DOWNLOADING FLEURS HAUSA")
    print("=" * 60)
    
    output_dir = ensure_directory(OUTPUT_DIR / "fleurs_hausa")
    
    try:
        print("Loading FLEURS Hausa dataset...")
        ds = load_dataset(
            "google/fleurs",
            "ha_ng",  # Hausa (Nigeria)
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        
        count = 0
        female_count = 0
        max_samples = 100
        
        print(f"Downloading up to {max_samples} Hausa samples...")
        
        for sample in tqdm(ds, total=max_samples):
            if count >= max_samples:
                break
                
            try:
                audio = sample.get("audio", {})
                if not audio:
                    continue
                    
                audio_array = audio.get("array")
                sample_rate = audio.get("sampling_rate", 16000)
                
                if audio_array is None:
                    continue
                
                gender = sample.get("gender", 0)
                speaker_id = sample.get("speaker_id", count)
                
                if gender == 1:
                    female_count += 1
                    subdir = "female"
                elif gender == 0:
                    subdir = "male"
                else:
                    subdir = "unknown"
                
                speaker_dir = ensure_directory(output_dir / subdir)
                filename = f"fleurs_ha_{count:04d}_spk{speaker_id}.wav"
                filepath = speaker_dir / filename
                
                import librosa
                audio_array = librosa.resample(
                    np.array(audio_array), 
                    orig_sr=sample_rate, 
                    target_sr=22050
                )
                
                sf.write(filepath, audio_array, 22050)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ Downloaded {count} FLEURS Hausa samples")
        print(f"   Female voices: {female_count}")
        return count
        
    except Exception as e:
        print(f"❌ Error downloading FLEURS Hausa: {e}")
        return 0

def download_fleurs_igbo():
    """
    Download FLEURS Igbo dataset.
    """
    print("\n" + "=" * 60)
    print("DOWNLOADING FLEURS IGBO")
    print("=" * 60)
    
    output_dir = ensure_directory(OUTPUT_DIR / "fleurs_igbo")
    
    try:
        print("Loading FLEURS Igbo dataset...")
        ds = load_dataset(
            "google/fleurs",
            "ig_ng",  # Igbo (Nigeria)
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        
        count = 0
        female_count = 0
        max_samples = 100
        
        print(f"Downloading up to {max_samples} Igbo samples...")
        
        for sample in tqdm(ds, total=max_samples):
            if count >= max_samples:
                break
                
            try:
                audio = sample.get("audio", {})
                if not audio:
                    continue
                    
                audio_array = audio.get("array")
                sample_rate = audio.get("sampling_rate", 16000)
                
                if audio_array is None:
                    continue
                
                gender = sample.get("gender", 0)
                speaker_id = sample.get("speaker_id", count)
                
                if gender == 1:
                    female_count += 1
                    subdir = "female"
                elif gender == 0:
                    subdir = "male"
                else:
                    subdir = "unknown"
                
                speaker_dir = ensure_directory(output_dir / subdir)
                filename = f"fleurs_ig_{count:04d}_spk{speaker_id}.wav"
                filepath = speaker_dir / filename
                
                import librosa
                audio_array = librosa.resample(
                    np.array(audio_array), 
                    orig_sr=sample_rate, 
                    target_sr=22050
                )
                
                sf.write(filepath, audio_array, 22050)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ Downloaded {count} FLEURS Igbo samples")
        print(f"   Female voices: {female_count}")
        return count
        
    except Exception as e:
        print(f"❌ Error downloading FLEURS Igbo: {e}")
        return 0

def download_african_accented_english():
    """
    Download African-accented English from available datasets.
    """
    print("\n" + "=" * 60)
    print("DOWNLOADING AFRICAN ACCENTED ENGLISH")
    print("=" * 60)
    
    output_dir = ensure_directory(OUTPUT_DIR / "african_english")
    
    try:
        # Try to get L2-ARCTIC or similar datasets
        print("Loading African-accented English dataset...")
        
        # Using Librispeech as fallback with diverse speakers
        ds = load_dataset(
            "openslr/librispeech_asr",
            "clean",
            split="train.clean.100",
            streaming=True,
            trust_remote_code=True
        )
        
        count = 0
        max_samples = 30
        
        print(f"Downloading up to {max_samples} English samples...")
        
        for sample in tqdm(ds, total=max_samples):
            if count >= max_samples:
                break
                
            try:
                audio = sample.get("audio", {})
                if not audio:
                    continue
                    
                audio_array = audio.get("array")
                sample_rate = audio.get("sampling_rate", 16000)
                
                if audio_array is None:
                    continue
                
                speaker_id = sample.get("speaker_id", count)
                
                speaker_dir = ensure_directory(output_dir / "samples")
                filename = f"libri_{count:04d}_spk{speaker_id}.wav"
                filepath = speaker_dir / filename
                
                import librosa
                audio_array = librosa.resample(
                    np.array(audio_array), 
                    orig_sr=sample_rate, 
                    target_sr=22050
                )
                
                sf.write(filepath, audio_array, 22050)
                count += 1
                
            except Exception as e:
                continue
        
        print(f"\n✅ Downloaded {count} English samples")
        return count
        
    except Exception as e:
        print(f"❌ Error downloading African English: {e}")
        return 0

def create_speaker_reference_candidates():
    """
    Create speaker reference candidates from downloaded female voices.
    """
    print("\n" + "=" * 60)
    print("CREATING SPEAKER REFERENCE CANDIDATES")
    print("=" * 60)
    
    reference_dir = ensure_directory(OUTPUT_DIR / "speaker_reference_candidates")
    
    # Collect all female voice samples
    female_samples = []
    
    for lang_dir in OUTPUT_DIR.iterdir():
        if lang_dir.is_dir() and lang_dir.name != "speaker_reference_candidates":
            female_dir = lang_dir / "female"
            if female_dir.exists():
                for wav_file in female_dir.glob("*.wav"):
                    try:
                        info = sf.info(wav_file)
                        duration = info.duration
                        # Ideal duration for speaker reference: 10-60 seconds
                        if 5 <= duration <= 120:
                            female_samples.append({
                                "path": wav_file,
                                "duration": duration,
                                "language": lang_dir.name
                            })
                    except Exception:
                        continue
    
    print(f"Found {len(female_samples)} female voice samples")
    
    # Sort by duration (prefer 10-30 second samples)
    female_samples.sort(key=lambda x: abs(x["duration"] - 20))
    
    # Copy top candidates
    import shutil
    for i, sample in enumerate(female_samples[:10]):
        dest = reference_dir / f"candidate_{i+1}_{sample['language']}_{sample['duration']:.1f}s.wav"
        shutil.copy2(sample["path"], dest)
        print(f"  Copied: {dest.name}")
    
    print(f"\n✅ Created {min(10, len(female_samples))} speaker reference candidates")
    print(f"   Location: {reference_dir}")

def generate_summary_report():
    """Generate a summary report of downloaded samples."""
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY REPORT")
    print("=" * 60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "datasets": {},
        "total_samples": 0,
        "total_female": 0,
        "total_male": 0
    }
    
    for lang_dir in OUTPUT_DIR.iterdir():
        if lang_dir.is_dir():
            lang_stats = {"female": 0, "male": 0, "unknown": 0, "total": 0}
            
            for gender_dir in lang_dir.iterdir():
                if gender_dir.is_dir():
                    count = len(list(gender_dir.glob("*.wav")))
                    gender = gender_dir.name
                    if gender in lang_stats:
                        lang_stats[gender] = count
                    lang_stats["total"] += count
            
            if lang_stats["total"] > 0:
                report["datasets"][lang_dir.name] = lang_stats
                report["total_samples"] += lang_stats["total"]
                report["total_female"] += lang_stats.get("female", 0)
                report["total_male"] += lang_stats.get("male", 0)
    
    # Print summary
    for dataset, stats in report["datasets"].items():
        print(f"\n{dataset}:")
        print(f"  Total: {stats['total']}")
        print(f"  Female: {stats.get('female', 0)}")
        print(f"  Male: {stats.get('male', 0)}")
    
    print(f"\n{'=' * 40}")
    print(f"GRAND TOTAL: {report['total_samples']} samples")
    print(f"Total Female: {report['total_female']}")
    print(f"Total Male: {report['total_male']}")
    
    # Save report
    report_path = OUTPUT_DIR / "download_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {report_path}")
    
    return report

def main():
    """Main function to download all voice datasets."""
    print("=" * 60)
    print("       SISI LOLA QUICK VOICE DOWNLOADER")
    print("       Nigerian Languages Voice Dataset")
    print("=" * 60)
    print(f"\nOutput Directory: {OUTPUT_DIR}")
    
    ensure_directory(OUTPUT_DIR)
    
    # Download all datasets
    total = 0
    
    # 1. FLEURS Yoruba (best quality Nigerian language dataset)
    total += download_fleurs_yoruba()
    
    # 2. FLEURS Hausa
    total += download_fleurs_hausa()
    
    # 3. FLEURS Igbo
    total += download_fleurs_igbo()
    
    # 4. Common Voice Nigerian English (if available)
    total += download_common_voice_nigerian()
    
    # 5. African-accented English
    total += download_african_accented_english()
    
    # Create speaker reference candidates
    create_speaker_reference_candidates()
    
    # Generate summary report
    generate_summary_report()
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"\nTotal samples downloaded: {total}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Review speaker reference candidates in:")
    print(f"   {OUTPUT_DIR / 'speaker_reference_candidates'}")
    print("2. Select the best female voice for Sisi Lola")
    print("3. Copy selected file as 'speaker_reference.wav'")
    
if __name__ == "__main__":
    main()
