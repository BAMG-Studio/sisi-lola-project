#!/usr/bin/env python3
"""
Create Speaker Reference Candidates from Downloaded Voice Samples
Selects best female voice samples for Sisi Lola voice cloning
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# Install requirements
import subprocess
for pkg in ["soundfile", "librosa", "numpy"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import soundfile as sf
import numpy as np

# Paths
BASE_DIR = Path(__file__).parent
VOICE_SAMPLES_DIR = BASE_DIR / "ml_training" / "data" / "voice_samples"
REFERENCE_DIR = VOICE_SAMPLES_DIR / "speaker_reference_candidates"

def analyze_audio(filepath: Path) -> dict:
    """Analyze audio file for quality metrics."""
    try:
        data, sr = sf.read(filepath)
        
        # Handle mono/stereo
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        
        # Calculate metrics
        duration = len(data) / sr
        rms = np.sqrt(np.mean(data ** 2))
        peak = np.abs(data).max()
        
        # Silence detection (proportion below threshold)
        silence_threshold = 0.01
        silence_ratio = np.sum(np.abs(data) < silence_threshold) / len(data)
        
        # Dynamic range
        dynamic_range = peak / (rms + 1e-10)
        
        # Quality score (higher is better)
        # Prefer: 10-30 second duration, low silence, moderate dynamic range
        duration_score = 1.0 if 10 <= duration <= 30 else 0.5 if 5 <= duration <= 60 else 0.2
        silence_score = max(0, 1 - silence_ratio * 2)
        volume_score = min(1, rms * 10)  # Penalize very quiet audio
        
        quality_score = (duration_score * 0.4 + silence_score * 0.3 + volume_score * 0.3)
        
        return {
            "duration": duration,
            "sample_rate": sr,
            "rms": float(rms),
            "peak": float(peak),
            "silence_ratio": float(silence_ratio),
            "dynamic_range": float(dynamic_range),
            "quality_score": float(quality_score)
        }
    except Exception as e:
        return None

def find_female_samples():
    """Find all female voice samples."""
    samples = []
    
    for lang_dir in VOICE_SAMPLES_DIR.iterdir():
        if not lang_dir.is_dir():
            continue
        
        # Look in female subdirectory
        female_dir = lang_dir / "female"
        if female_dir.exists():
            for wav_file in female_dir.glob("*.wav"):
                analysis = analyze_audio(wav_file)
                if analysis:
                    samples.append({
                        "path": wav_file,
                        "language": lang_dir.name,
                        **analysis
                    })
    
    return samples

def create_speaker_reference():
    """Create speaker reference candidates."""
    print("=" * 60)
    print("   CREATING SPEAKER REFERENCE CANDIDATES")
    print("   For Sisi Lola Voice Cloning")
    print("=" * 60)
    
    # Create output directory
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all female samples
    print("\nScanning for female voice samples...")
    samples = find_female_samples()
    
    print(f"Found {len(samples)} female samples")
    
    if not samples:
        print("❌ No female samples found!")
        return
    
    # Sort by quality score
    samples.sort(key=lambda x: x["quality_score"], reverse=True)
    
    # Group by language
    by_language = {}
    for s in samples:
        lang = s["language"]
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(s)
    
    print("\nSamples by language:")
    for lang, lang_samples in by_language.items():
        print(f"  {lang}: {len(lang_samples)} samples")
    
    # Copy top candidates
    print("\nSelecting top 15 candidates...")
    selected = []
    
    for i, sample in enumerate(samples[:15]):
        src = sample["path"]
        dest_name = f"candidate_{i+1:02d}_{sample['language']}_{sample['duration']:.1f}s_q{sample['quality_score']:.2f}.wav"
        dest = REFERENCE_DIR / dest_name
        
        shutil.copy2(src, dest)
        selected.append({
            "rank": i + 1,
            "file": dest_name,
            "language": sample["language"],
            "duration": sample["duration"],
            "quality_score": sample["quality_score"],
            "sample_rate": sample["sample_rate"],
            "original": str(src)
        })
        print(f"  ✓ {dest_name}")
    
    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_female_samples": len(samples),
        "languages": list(by_language.keys()),
        "samples_per_language": {k: len(v) for k, v in by_language.items()},
        "selected_candidates": selected,
        "output_directory": str(REFERENCE_DIR)
    }
    
    report_path = REFERENCE_DIR / "selection_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Create README for candidates
    readme_content = """# Speaker Reference Candidates for Sisi Lola

## Selected Candidates

These voice samples have been selected as the best candidates for Sisi Lola's voice.

### Selection Criteria:
- Duration: 10-30 seconds (optimal for XTTS)
- Low silence ratio
- Good audio volume
- Clear speech

### How to Use:
1. Listen to each candidate
2. Select the best Nigerian female voice
3. Copy the selected file as `speaker_reference.wav`

### Files:
"""
    
    for s in selected:
        readme_content += f"\n- **{s['file']}**\n"
        readme_content += f"  - Language: {s['language']}\n"
        readme_content += f"  - Duration: {s['duration']:.1f}s\n"
        readme_content += f"  - Quality Score: {s['quality_score']:.2f}\n"
    
    readme_path = REFERENCE_DIR / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    print(f"\n✅ Created {len(selected)} speaker reference candidates")
    print(f"   Location: {REFERENCE_DIR}")
    print(f"\nNext steps:")
    print("1. Listen to the candidate files")
    print("2. Select the best female voice for Sisi Lola")
    print("3. Copy as 'speaker_reference.wav' for training")
    
    return report

def generate_training_summary():
    """Generate summary of voice samples for training."""
    print("\n" + "=" * 60)
    print("   VOICE SAMPLES TRAINING SUMMARY")
    print("=" * 60)
    
    total_samples = 0
    total_female = 0
    total_male = 0
    total_duration = 0
    
    for lang_dir in VOICE_SAMPLES_DIR.iterdir():
        if not lang_dir.is_dir() or lang_dir.name == "speaker_reference_candidates":
            continue
        
        female_count = 0
        male_count = 0
        lang_duration = 0
        
        for gender_dir in lang_dir.iterdir():
            if gender_dir.is_dir():
                for wav in gender_dir.glob("*.wav"):
                    try:
                        info = sf.info(wav)
                        lang_duration += info.duration
                        if gender_dir.name == "female":
                            female_count += 1
                        else:
                            male_count += 1
                    except:
                        pass
        
        if female_count + male_count > 0:
            print(f"\n{lang_dir.name}:")
            print(f"  Female: {female_count}")
            print(f"  Male: {male_count}")
            print(f"  Total Duration: {lang_duration/60:.1f} minutes")
            
            total_female += female_count
            total_male += male_count
            total_duration += lang_duration
    
    total_samples = total_female + total_male
    
    print(f"\n{'=' * 40}")
    print(f"TOTAL: {total_samples} samples")
    print(f"  Female: {total_female}")
    print(f"  Male: {total_male}")
    print(f"  Duration: {total_duration/60:.1f} minutes ({total_duration/3600:.2f} hours)")
    
    return {
        "total_samples": total_samples,
        "total_female": total_female,
        "total_male": total_male,
        "total_duration_seconds": total_duration
    }

if __name__ == "__main__":
    create_speaker_reference()
    generate_training_summary()
