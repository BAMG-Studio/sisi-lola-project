#!/usr/bin/env python3
"""
Classify Hausa voice samples by gender using pitch analysis
"""

import sys
import numpy as np
import soundfile as sf
from pathlib import Path

# Pitch analysis functions (same as classify_pidgin_gender.py)
def estimate_pitch_simple(y: np.ndarray, sr: int) -> float:
    """Estimate fundamental frequency using autocorrelation."""
    try:
        frame_length = int(sr * 0.05)
        hop_length = int(sr * 0.025)
        pitches = []
        
        for i in range(0, len(y) - frame_length, hop_length):
            frame = y[i:i + frame_length]
            frame = frame * np.hanning(len(frame))
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr)//2:]
            
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
                if 50 < pitch < 500:
                    pitches.append(pitch)
        
        if len(pitches) > 5:
            return float(np.median(pitches))
        return 0.0
    except:
        return 0.0

def classify_gender(pitch: float) -> tuple:
    """Classify gender based on pitch."""
    if pitch <= 0:
        return ("unknown", 0.0)
    if pitch >= 180:
        return ("female", 0.85)
    elif pitch <= 140:
        return ("male", 0.85)
    else:
        return ("uncertain", 0.50)

def main():
    print("=" * 60)
    print("    HAUSA GENDER CLASSIFICATION")
    print("=" * 60)
    
    # Hausa directory - FLEURS already organized by gender
    hausa_dir = Path(__file__).parent / "ml_training" / "data" / "voice_samples" / "fleurs_hausa"
    female_dir = hausa_dir / "female"
    male_dir = hausa_dir / "male"
    
    # Count existing
    existing_female = len(list(female_dir.glob("*.wav")))
    existing_male = len(list(male_dir.glob("*.wav")))
    
    print(f"\nFLEURS Hausa samples (from metadata):")
    print(f"  Female: {existing_female}")
    print(f"  Male: {existing_male}")
    print(f"  Total: {existing_female + existing_male}")
    
    # Verify with pitch analysis on a sample
    print("\n--- Verifying with pitch analysis ---")
    
    # Check a few female samples
    female_files = list(female_dir.glob("*.wav"))[:5]
    male_files = list(male_dir.glob("*.wav"))[:5]
    
    female_pitches = []
    male_pitches = []
    
    for f in female_files:
        try:
            audio, sr = sf.read(str(f))
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            pitch = estimate_pitch_simple(audio, sr)
            if pitch > 0:
                gender, conf = classify_gender(pitch)
                female_pitches.append(pitch)
                print(f"  Female sample: {f.name[:40]}... -> {pitch:.1f} Hz ({gender})")
        except Exception as e:
            print(f"  Error: {e}")
    
    for f in male_files:
        try:
            audio, sr = sf.read(str(f))
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            pitch = estimate_pitch_simple(audio, sr)
            if pitch > 0:
                gender, conf = classify_gender(pitch)
                male_pitches.append(pitch)
                print(f"  Male sample: {f.name[:40]}... -> {pitch:.1f} Hz ({gender})")
        except Exception as e:
            print(f"  Error: {e}")
    
    if female_pitches:
        print(f"\nAverage female pitch: {sum(female_pitches)/len(female_pitches):.1f} Hz")
    if male_pitches:
        print(f"Average male pitch: {sum(male_pitches)/len(male_pitches):.1f} Hz")
    
    print("\n" + "=" * 60)
    print("HAUSA CLASSIFICATION COMPLETE")
    print("=" * 60)
    print(f"Total: {existing_female + existing_male} samples")
    print(f"Female: {existing_female}, Male: {existing_male}")
    print("\n(FLEURS metadata used for gender labels)")

if __name__ == "__main__":
    main()
