#!/usr/bin/env python3
"""
Simple Voice Gender Classifier using Pitch Analysis
Fast and robust classification for Nigerian Pidgin samples
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Install requirements
import subprocess
for pkg in ["librosa", "numpy", "soundfile", "tqdm"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import numpy as np
import soundfile as sf
import librosa
from tqdm import tqdm


def estimate_pitch_simple(y: np.ndarray, sr: int) -> float:
    """
    Estimate fundamental frequency using autocorrelation.
    Fast and robust method.
    """
    try:
        # Use autocorrelation for pitch estimation
        # More robust than pyin for varied audio quality
        
        # Compute autocorrelation
        frame_length = int(sr * 0.05)  # 50ms frames
        hop_length = int(sr * 0.025)   # 25ms hop
        
        pitches = []
        
        for i in range(0, len(y) - frame_length, hop_length):
            frame = y[i:i + frame_length]
            
            # Apply window
            frame = frame * np.hanning(len(frame))
            
            # Autocorrelation
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr)//2:]
            
            # Find first peak after the initial drop
            # Minimum lag corresponds to ~500Hz (sr/500), max to ~50Hz (sr/50)
            min_lag = int(sr / 500)
            max_lag = int(sr / 50)
            
            if max_lag > len(corr):
                continue
            
            search_region = corr[min_lag:max_lag]
            if len(search_region) == 0:
                continue
                
            peak_idx = np.argmax(search_region) + min_lag
            
            if peak_idx > 0:
                pitch = sr / peak_idx
                if 50 < pitch < 500:  # Valid speech range
                    pitches.append(pitch)
        
        if len(pitches) > 5:
            # Use median for robustness
            return float(np.median(pitches))
        else:
            return 0.0
            
    except Exception as e:
        return 0.0


def classify_gender_by_pitch(pitch: float, spectral_centroid: float = 0) -> tuple:
    """
    Classify gender based on pitch.
    
    Female typical range: 165-255 Hz
    Male typical range: 85-180 Hz
    
    Returns: (gender, confidence)
    """
    if pitch <= 0:
        return ("unknown", 0.0)
    
    # Clear female range
    if pitch >= 200:
        return ("female", 0.95)
    elif pitch >= 180:
        return ("female", 0.80)
    elif pitch >= 165:
        return ("female", 0.65)
    
    # Clear male range  
    elif pitch <= 120:
        return ("male", 0.95)
    elif pitch <= 140:
        return ("male", 0.80)
    elif pitch <= 160:
        return ("male", 0.70)
    
    # Overlap region (160-165 Hz) - use spectral centroid
    else:
        if spectral_centroid > 2200:
            return ("female", 0.55)
        else:
            return ("male", 0.55)


def get_spectral_centroid(y: np.ndarray, sr: int) -> float:
    """Calculate spectral centroid (brightness indicator)."""
    try:
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        return float(np.mean(centroid))
    except:
        return 0.0


def classify_pidgin_samples():
    """Classify Nigerian Pidgin samples by gender."""
    
    print("="*60)
    print("   NIGERIAN PIDGIN GENDER CLASSIFICATION")
    print("   Using Fast Pitch Analysis")
    print("="*60)
    
    # Paths
    base_dir = Path(__file__).parent
    voice_dir = base_dir / "ml_training" / "data" / "voice_samples"
    pidgin_dir = voice_dir / "nigerian_pidgin"
    unknown_dir = pidgin_dir / "unknown"
    
    if not unknown_dir.exists():
        print(f"Error: {unknown_dir} not found")
        return
    
    # Output directories
    female_dir = pidgin_dir / "female"
    male_dir = pidgin_dir / "male"
    low_confidence_dir = pidgin_dir / "low_confidence"
    
    female_dir.mkdir(exist_ok=True)
    male_dir.mkdir(exist_ok=True)
    low_confidence_dir.mkdir(exist_ok=True)
    
    # Get all WAV files
    wav_files = list(unknown_dir.glob("*.wav"))
    print(f"\nClassifying {len(wav_files)} samples...")
    
    results = {
        "female": [],
        "male": [],
        "unknown": [],
        "low_confidence": []
    }
    
    for wav_file in tqdm(wav_files, desc="Classifying"):
        try:
            # Load audio
            y, sr = librosa.load(wav_file, sr=22050, duration=30)
            
            if len(y) < sr * 0.5:
                results["unknown"].append({
                    "file": wav_file.name,
                    "reason": "too_short"
                })
                continue
            
            # Estimate pitch
            pitch = estimate_pitch_simple(y, sr)
            
            # Get spectral centroid for edge cases
            centroid = get_spectral_centroid(y, sr)
            
            # Classify
            gender, confidence = classify_gender_by_pitch(pitch, centroid)
            
            result = {
                "file": wav_file.name,
                "pitch": pitch,
                "spectral_centroid": centroid,
                "gender": gender,
                "confidence": confidence
            }
            
            # Organize by confidence
            if confidence >= 0.65:
                results[gender].append(result)
                
                # Copy file to gender folder
                if gender == "female":
                    dst = female_dir / f"female_{wav_file.name}"
                else:
                    dst = male_dir / f"male_{wav_file.name}"
                
                if not dst.exists():
                    shutil.copy2(wav_file, dst)
            else:
                results["low_confidence"].append(result)
                dst = low_confidence_dir / wav_file.name
                if not dst.exists():
                    shutil.copy2(wav_file, dst)
                
        except Exception as e:
            results["unknown"].append({
                "file": wav_file.name,
                "error": str(e)
            })
    
    # Calculate statistics
    female_pitches = [r["pitch"] for r in results["female"] if r["pitch"] > 0]
    male_pitches = [r["pitch"] for r in results["male"] if r["pitch"] > 0]
    
    summary = {
        "total": len(wav_files),
        "female_count": len(results["female"]),
        "male_count": len(results["male"]),
        "low_confidence_count": len(results["low_confidence"]),
        "unknown_count": len(results["unknown"]),
        "female_avg_pitch": np.mean(female_pitches) if female_pitches else 0,
        "male_avg_pitch": np.mean(male_pitches) if male_pitches else 0
    }
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "female": results["female"],
        "male": results["male"],
        "low_confidence": results["low_confidence"],
        "unknown": results["unknown"]
    }
    
    report_path = pidgin_dir / "gender_classification_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)
    
    # Print summary
    print(f"\n{'='*60}")
    print("CLASSIFICATION COMPLETE")
    print("="*60)
    print(f"\nTotal: {summary['total']}")
    print(f"Female: {summary['female_count']} (avg pitch: {summary['female_avg_pitch']:.1f} Hz)")
    print(f"Male: {summary['male_count']} (avg pitch: {summary['male_avg_pitch']:.1f} Hz)")
    print(f"Low confidence: {summary['low_confidence_count']}")
    print(f"Unknown: {summary['unknown_count']}")
    print(f"\nReport: {report_path}")
    print(f"\nFiles organized into:")
    print(f"  Female: {female_dir}")
    print(f"  Male: {male_dir}")
    print(f"  Low confidence: {low_confidence_dir}")
    
    return summary


if __name__ == "__main__":
    classify_pidgin_samples()
