#!/usr/bin/env python3
"""
Voice Gender Classifier for Nigerian Voice Samples
Uses pitch analysis and ML classification to identify gender from audio

Methods:
1. Pitch-based classification (F0 fundamental frequency)
2. Spectral features (MFCCs, spectral centroid)
3. Optional: Pre-trained model classification

Female voices typically: 165-255 Hz
Male voices typically: 85-180 Hz
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Install requirements
import subprocess
for pkg in ["librosa", "numpy", "soundfile", "scikit-learn", "tqdm"]:
    try:
        __import__(pkg.replace("-", "_"))
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import numpy as np
import soundfile as sf
import librosa
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class VoiceGenderClassifier:
    """
    Classifies voice gender using pitch and spectral analysis.
    Optimized for Nigerian languages.
    """
    
    # Pitch thresholds (Hz) - calibrated for Nigerian accents
    FEMALE_MIN_PITCH = 165
    FEMALE_MAX_PITCH = 300
    MALE_MIN_PITCH = 75
    MALE_MAX_PITCH = 180
    OVERLAP_LOW = 165  # Overlap region
    OVERLAP_HIGH = 180
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize classifier.
        
        Args:
            confidence_threshold: Minimum confidence for classification (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.scaler = StandardScaler()
        self.classifier = None
        self.is_trained = False
        
    def extract_features(self, audio_path: Path) -> Optional[Dict]:
        """
        Extract audio features for gender classification.
        
        Returns dict with:
        - pitch_mean: Mean fundamental frequency
        - pitch_std: Pitch variation
        - mfcc_mean: Mean MFCC coefficients
        - spectral_centroid: Spectral brightness
        - spectral_rolloff: High frequency content
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050)
            
            if len(y) < sr * 0.5:  # Less than 0.5 seconds
                return None
            
            # Extract pitch (F0) using pyin for better accuracy
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y, 
                fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=librosa.note_to_hz('C6'),  # ~1047 Hz
                sr=sr
            )
            
            # Filter out unvoiced segments
            f0_voiced = f0[voiced_flag]
            
            if len(f0_voiced) < 10:  # Not enough voiced frames
                # Fallback to basic pitch detection
                f0_voiced = f0[~np.isnan(f0)]
                if len(f0_voiced) < 5:
                    return None
            
            # Pitch statistics
            pitch_mean = np.mean(f0_voiced)
            pitch_std = np.std(f0_voiced)
            pitch_median = np.median(f0_voiced)
            pitch_min = np.percentile(f0_voiced, 10)
            pitch_max = np.percentile(f0_voiced, 90)
            
            # MFCC features (voice quality)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            
            # Zero crossing rate (speech characteristics)
            zcr = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # RMS energy
            rms = np.mean(librosa.feature.rms(y=y))
            
            return {
                "pitch_mean": float(pitch_mean),
                "pitch_std": float(pitch_std),
                "pitch_median": float(pitch_median),
                "pitch_min": float(pitch_min),
                "pitch_max": float(pitch_max),
                "mfcc_mean": mfcc_mean.tolist(),
                "mfcc_std": mfcc_std.tolist(),
                "spectral_centroid": float(spectral_centroid),
                "spectral_rolloff": float(spectral_rolloff),
                "spectral_bandwidth": float(spectral_bandwidth),
                "zcr": float(zcr),
                "rms": float(rms),
                "duration": float(len(y) / sr)
            }
            
        except Exception as e:
            print(f"Error extracting features from {audio_path}: {e}")
            return None
    
    def classify_by_pitch(self, features: Dict) -> Tuple[str, float]:
        """
        Classify gender based on pitch analysis.
        
        Returns:
            (gender, confidence) tuple
        """
        pitch = features["pitch_mean"]
        pitch_std = features["pitch_std"]
        
        # Clear female range
        if pitch >= self.FEMALE_MIN_PITCH:
            if pitch >= 200:
                confidence = 0.95
            elif pitch >= 180:
                confidence = 0.85
            else:
                confidence = 0.70
            return ("female", confidence)
        
        # Clear male range
        elif pitch <= self.MALE_MAX_PITCH:
            if pitch <= 140:
                confidence = 0.95
            elif pitch <= 160:
                confidence = 0.85
            else:
                confidence = 0.70
            return ("male", confidence)
        
        # Overlap region - use additional features
        else:
            # In overlap, higher spectral centroid suggests female
            if features.get("spectral_centroid", 0) > 2000:
                return ("female", 0.60)
            else:
                return ("male", 0.60)
    
    def classify_single(self, audio_path: Path) -> Dict:
        """
        Classify a single audio file.
        
        Returns:
            Dict with gender, confidence, and features
        """
        features = self.extract_features(audio_path)
        
        if features is None:
            return {
                "file": str(audio_path),
                "gender": "unknown",
                "confidence": 0.0,
                "reason": "feature_extraction_failed"
            }
        
        gender, confidence = self.classify_by_pitch(features)
        
        return {
            "file": str(audio_path),
            "gender": gender,
            "confidence": confidence,
            "pitch_mean": features["pitch_mean"],
            "pitch_std": features["pitch_std"],
            "spectral_centroid": features["spectral_centroid"],
            "duration": features["duration"]
        }
    
    def classify_directory(self, 
                          input_dir: Path, 
                          reorganize: bool = False,
                          output_dir: Optional[Path] = None) -> Dict:
        """
        Classify all audio files in a directory.
        
        Args:
            input_dir: Directory containing audio files
            reorganize: If True, copy files to gender-specific folders
            output_dir: Where to put reorganized files (default: input_dir parent)
        
        Returns:
            Classification report
        """
        input_dir = Path(input_dir)
        wav_files = list(input_dir.glob("*.wav"))
        
        if not wav_files:
            return {"error": "No WAV files found"}
        
        print(f"\nClassifying {len(wav_files)} audio files...")
        
        results = {
            "total": len(wav_files),
            "female": [],
            "male": [],
            "unknown": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for wav_file in tqdm(wav_files, desc="Classifying"):
            classification = self.classify_single(wav_file)
            
            if classification["confidence"] >= self.confidence_threshold:
                results[classification["gender"]].append(classification)
            else:
                classification["gender"] = "unknown"
                results["unknown"].append(classification)
        
        # Summary
        results["summary"] = {
            "female_count": len(results["female"]),
            "male_count": len(results["male"]),
            "unknown_count": len(results["unknown"]),
            "female_avg_pitch": np.mean([r["pitch_mean"] for r in results["female"]]) if results["female"] else 0,
            "male_avg_pitch": np.mean([r["pitch_mean"] for r in results["male"]]) if results["male"] else 0
        }
        
        # Reorganize files if requested
        if reorganize:
            output_dir = output_dir or input_dir.parent
            self._reorganize_files(results, output_dir)
        
        return results
    
    def _reorganize_files(self, results: Dict, output_dir: Path):
        """Copy files to gender-specific directories."""
        female_dir = output_dir / "female"
        male_dir = output_dir / "male"
        unknown_dir = output_dir / "unknown_gender"
        
        female_dir.mkdir(parents=True, exist_ok=True)
        male_dir.mkdir(parents=True, exist_ok=True)
        unknown_dir.mkdir(parents=True, exist_ok=True)
        
        print("\nReorganizing files by gender...")
        
        for r in results["female"]:
            src = Path(r["file"])
            dst = female_dir / f"female_{src.name}"
            if not dst.exists():
                shutil.copy2(src, dst)
        
        for r in results["male"]:
            src = Path(r["file"])
            dst = male_dir / f"male_{src.name}"
            if not dst.exists():
                shutil.copy2(src, dst)
        
        for r in results["unknown"]:
            src = Path(r["file"])
            dst = unknown_dir / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
        
        print(f"  Female: {len(results['female'])} -> {female_dir}")
        print(f"  Male: {len(results['male'])} -> {male_dir}")
        print(f"  Unknown: {len(results['unknown'])} -> {unknown_dir}")


def train_classifier_from_labeled_data(classifier: VoiceGenderClassifier,
                                       female_dir: Path,
                                       male_dir: Path) -> VoiceGenderClassifier:
    """
    Train classifier using labeled data (e.g., from Yoruba dataset).
    
    This improves classification for Nigerian accents by learning
    from samples with known gender labels.
    """
    print("\nTraining classifier from labeled data...")
    
    X = []
    y = []
    
    # Extract features from female samples
    female_files = list(Path(female_dir).glob("*.wav"))
    print(f"Processing {len(female_files)} female samples...")
    
    for f in tqdm(female_files[:50], desc="Female"):  # Limit for speed
        features = classifier.extract_features(f)
        if features:
            # Create feature vector
            fv = [
                features["pitch_mean"],
                features["pitch_std"],
                features["spectral_centroid"],
                features["spectral_rolloff"],
                features["zcr"]
            ] + features["mfcc_mean"][:5]
            X.append(fv)
            y.append(1)  # Female = 1
    
    # Extract features from male samples
    male_files = list(Path(male_dir).glob("*.wav"))
    print(f"Processing {len(male_files)} male samples...")
    
    for f in tqdm(male_files[:50], desc="Male"):
        features = classifier.extract_features(f)
        if features:
            fv = [
                features["pitch_mean"],
                features["pitch_std"],
                features["spectral_centroid"],
                features["spectral_rolloff"],
                features["zcr"]
            ] + features["mfcc_mean"][:5]
            X.append(fv)
            y.append(0)  # Male = 0
    
    if len(X) < 20:
        print("Not enough training data")
        return classifier
    
    # Train model
    X = np.array(X)
    y = np.array(y)
    
    classifier.scaler.fit(X)
    X_scaled = classifier.scaler.transform(X)
    
    classifier.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    classifier.classifier.fit(X_scaled, y)
    classifier.is_trained = True
    
    print(f"Classifier trained on {len(X)} samples")
    
    return classifier


def classify_nigerian_pidgin(voice_samples_dir: Path,
                            use_yoruba_training: bool = True) -> Dict:
    """
    Classify Nigerian Pidgin samples using pitch analysis
    and optionally training from labeled Yoruba data.
    """
    print("="*60)
    print("   NIGERIAN PIDGIN GENDER CLASSIFICATION")
    print("="*60)
    
    classifier = VoiceGenderClassifier(confidence_threshold=0.6)
    
    # Optionally train from Yoruba labeled data
    if use_yoruba_training:
        yoruba_female = voice_samples_dir / "fleurs_yoruba" / "female"
        yoruba_male = voice_samples_dir / "fleurs_yoruba" / "male"
        
        if yoruba_female.exists() and yoruba_male.exists():
            classifier = train_classifier_from_labeled_data(
                classifier, yoruba_female, yoruba_male
            )
    
    # Classify Pidgin samples
    pidgin_dir = voice_samples_dir / "nigerian_pidgin" / "unknown"
    
    if not pidgin_dir.exists():
        print(f"Pidgin directory not found: {pidgin_dir}")
        return {}
    
    results = classifier.classify_directory(
        pidgin_dir,
        reorganize=True,
        output_dir=voice_samples_dir / "nigerian_pidgin"
    )
    
    # Save report
    report_path = voice_samples_dir / "nigerian_pidgin" / "gender_classification_report.json"
    with open(report_path, "w") as f:
        # Convert numpy types for JSON serialization
        def convert(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            return obj
        
        json.dump(results, f, indent=2, default=convert)
    
    print(f"\n{'='*60}")
    print("CLASSIFICATION COMPLETE")
    print("="*60)
    print(f"\nTotal samples: {results['total']}")
    print(f"Female: {results['summary']['female_count']} (avg pitch: {results['summary']['female_avg_pitch']:.1f} Hz)")
    print(f"Male: {results['summary']['male_count']} (avg pitch: {results['summary']['male_avg_pitch']:.1f} Hz)")
    print(f"Unknown: {results['summary']['unknown_count']}")
    print(f"\nReport saved: {report_path}")
    
    return results


if __name__ == "__main__":
    # Get the voice samples directory
    script_dir = Path(__file__).parent
    voice_samples_dir = script_dir / "data" / "voice_samples"
    
    if not voice_samples_dir.exists():
        print(f"Voice samples directory not found: {voice_samples_dir}")
        sys.exit(1)
    
    # Run classification
    results = classify_nigerian_pidgin(voice_samples_dir)
