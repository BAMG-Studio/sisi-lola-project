"""
Voice Training Data Preprocessor
Integrates gender classification with voice training pipeline

This module:
1. Classifies unclassified voice samples by gender
2. Selects best female samples for Sisi Lola voice cloning
3. Prepares reference audio files for XTTS training
4. Generates quality metrics for training data
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Handle imports
try:
    import numpy as np
    import soundfile as sf
    import librosa
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "numpy", "soundfile", "librosa", "tqdm", "-q"])
    import numpy as np
    import soundfile as sf
    import librosa


class VoiceTrainingPreprocessor:
    """
    Preprocesses voice samples for XTTS training.
    Integrates gender classification and quality analysis.
    """
    
    def __init__(self, voice_samples_dir: Path):
        """
        Initialize preprocessor.
        
        Args:
            voice_samples_dir: Base directory containing voice samples
        """
        self.voice_samples_dir = Path(voice_samples_dir)
        self.output_dir = self.voice_samples_dir / "training_ready"
        self.output_dir.mkdir(exist_ok=True)
        
    def estimate_pitch(self, y: np.ndarray, sr: int) -> float:
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
            
            return float(np.median(pitches)) if len(pitches) > 5 else 0.0
        except:
            return 0.0
    
    def classify_gender(self, audio_path: Path) -> Tuple[str, float, Dict]:
        """
        Classify gender and extract quality metrics.
        
        Returns:
            (gender, confidence, metrics)
        """
        try:
            y, sr = librosa.load(audio_path, sr=22050, duration=30)
            
            if len(y) < sr * 0.5:
                return ("unknown", 0.0, {"error": "too_short"})
            
            # Pitch analysis
            pitch = self.estimate_pitch(y, sr)
            
            # Spectral centroid
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            
            # RMS energy
            rms = float(np.mean(librosa.feature.rms(y=y)))
            
            # Duration
            duration = len(y) / sr
            
            # Classify
            if pitch <= 0:
                gender, confidence = "unknown", 0.0
            elif pitch >= 200:
                gender, confidence = "female", 0.95
            elif pitch >= 180:
                gender, confidence = "female", 0.80
            elif pitch >= 165:
                gender, confidence = "female", 0.65
            elif pitch <= 120:
                gender, confidence = "male", 0.95
            elif pitch <= 140:
                gender, confidence = "male", 0.80
            elif pitch <= 160:
                gender, confidence = "male", 0.70
            else:
                gender, confidence = ("female", 0.55) if centroid > 2200 else ("male", 0.55)
            
            metrics = {
                "pitch": pitch,
                "spectral_centroid": centroid,
                "rms": rms,
                "duration": duration,
            }
            
            return gender, confidence, metrics
            
        except Exception as e:
            return ("unknown", 0.0, {"error": str(e)})
    
    def analyze_quality(self, audio_path: Path) -> Dict:
        """
        Analyze audio quality for training suitability.
        
        Returns quality metrics and training score.
        """
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Duration check (10-30 seconds ideal)
            duration = len(y) / sr
            if duration < 5:
                duration_score = 0.2
            elif 10 <= duration <= 30:
                duration_score = 1.0
            elif duration <= 60:
                duration_score = 0.8
            else:
                duration_score = 0.5
            
            # Silence ratio
            rms = librosa.feature.rms(y=y)[0]
            silence_threshold = np.percentile(rms, 10) * 2
            silence_ratio = np.sum(rms < silence_threshold) / len(rms)
            silence_score = max(0, 1 - silence_ratio * 2)
            
            # Volume consistency (lower std = more consistent)
            rms_std = np.std(rms) / (np.mean(rms) + 1e-10)
            consistency_score = max(0, 1 - rms_std)
            
            # Spectral clarity
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            clarity_score = min(1.0, np.mean(spectral_contrast) / 30)
            
            # Overall quality score
            quality_score = (
                duration_score * 0.3 +
                silence_score * 0.3 +
                consistency_score * 0.2 +
                clarity_score * 0.2
            )
            
            return {
                "duration": duration,
                "duration_score": duration_score,
                "silence_ratio": silence_ratio,
                "silence_score": silence_score,
                "consistency_score": consistency_score,
                "clarity_score": clarity_score,
                "quality_score": quality_score,
            }
            
        except Exception as e:
            return {"quality_score": 0.0, "error": str(e)}
    
    def collect_female_samples(self) -> List[Dict]:
        """
        Collect all female voice samples from various datasets.
        
        Returns list of sample info dicts with paths and metrics.
        """
        female_samples = []
        
        # Search patterns for female samples
        search_dirs = [
            self.voice_samples_dir / "fleurs_yoruba" / "female",
            self.voice_samples_dir / "nigerian_pidgin" / "female",
            self.voice_samples_dir / "fleurs_hausa" / "female",
            self.voice_samples_dir / "fleurs_igbo" / "female",
            self.voice_samples_dir / "speaker_reference_candidates",
        ]
        
        for dir_path in search_dirs:
            if not dir_path.exists():
                continue
                
            for wav_file in dir_path.glob("*.wav"):
                quality = self.analyze_quality(wav_file)
                
                female_samples.append({
                    "path": str(wav_file),
                    "filename": wav_file.name,
                    "source": dir_path.name,
                    "quality_score": quality.get("quality_score", 0),
                    "duration": quality.get("duration", 0),
                })
        
        # Sort by quality
        female_samples.sort(key=lambda x: x["quality_score"], reverse=True)
        
        return female_samples
    
    def prepare_training_data(self, 
                             target_gender: str = "female",
                             min_samples: int = 20,
                             max_samples: int = 50) -> Dict:
        """
        Prepare training data for XTTS voice training.
        
        Args:
            target_gender: Gender to select for voice cloning
            min_samples: Minimum samples needed
            max_samples: Maximum samples to include
            
        Returns:
            Training data manifest
        """
        print("=" * 60)
        print(f"   PREPARING VOICE TRAINING DATA ({target_gender.upper()})")
        print("=" * 60)
        
        if target_gender == "female":
            samples = self.collect_female_samples()
        else:
            # For male, would need similar collection logic
            samples = []
        
        print(f"\nFound {len(samples)} {target_gender} samples")
        
        if len(samples) < min_samples:
            print(f"⚠️ Warning: Only {len(samples)} samples, need {min_samples}")
        
        # Select top samples
        selected = samples[:max_samples]
        
        # Copy to training directory
        training_dir = self.output_dir / target_gender
        training_dir.mkdir(exist_ok=True)
        
        manifest = {
            "created_at": datetime.now().isoformat(),
            "target_gender": target_gender,
            "total_samples": len(selected),
            "samples": [],
        }
        
        print(f"\nPreparing {len(selected)} samples...")
        
        for i, sample in enumerate(selected):
            src = Path(sample["path"])
            dst = training_dir / f"{target_gender}_{i:04d}_{src.name}"
            
            if not dst.exists():
                shutil.copy2(src, dst)
            
            manifest["samples"].append({
                "file": dst.name,
                "source": sample["source"],
                "quality_score": sample["quality_score"],
                "duration": sample["duration"],
            })
        
        # Save manifest
        manifest_path = self.output_dir / f"{target_gender}_training_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Calculate total duration
        total_duration = sum(s["duration"] for s in manifest["samples"])
        
        print(f"\n✅ Training data prepared:")
        print(f"   Samples: {len(selected)}")
        print(f"   Total duration: {total_duration/60:.1f} minutes")
        print(f"   Location: {training_dir}")
        print(f"   Manifest: {manifest_path}")
        
        return manifest
    
    def select_speaker_reference(self, num_references: int = 3) -> List[Path]:
        """
        Select the best speaker reference files for XTTS cloning.
        
        Returns paths to top reference audio files.
        """
        samples = self.collect_female_samples()
        
        # Filter for ideal duration (10-30 seconds)
        ideal_samples = [s for s in samples if 10 <= s.get("duration", 0) <= 30]
        
        # If not enough ideal samples, use all
        if len(ideal_samples) < num_references:
            ideal_samples = samples
        
        # Sort by quality
        ideal_samples.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # Return top references
        references = []
        for s in ideal_samples[:num_references]:
            references.append(Path(s["path"]))
        
        return references


def prepare_for_modal_training(voice_samples_dir: Path) -> Dict:
    """
    Prepare voice data for Modal cloud training.
    
    This function is called before Modal training to ensure
    all voice samples are properly classified and organized.
    """
    preprocessor = VoiceTrainingPreprocessor(voice_samples_dir)
    
    # Prepare female voice training data
    manifest = preprocessor.prepare_training_data(
        target_gender="female",
        min_samples=20,
        max_samples=50
    )
    
    # Select best speaker references
    references = preprocessor.select_speaker_reference(num_references=3)
    
    result = {
        "manifest": manifest,
        "speaker_references": [str(r) for r in references],
        "training_dir": str(preprocessor.output_dir),
    }
    
    # Save result
    result_path = voice_samples_dir / "voice_training_preparation.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📋 Training preparation saved: {result_path}")
    
    return result


if __name__ == "__main__":
    # Get voice samples directory
    script_dir = Path(__file__).parent
    voice_samples_dir = script_dir / "data" / "voice_samples"
    
    if not voice_samples_dir.exists():
        print(f"Error: {voice_samples_dir} not found")
        sys.exit(1)
    
    # Prepare for training
    result = prepare_for_modal_training(voice_samples_dir)
    
    print("\n" + "=" * 60)
    print("VOICE TRAINING DATA READY")
    print("=" * 60)
    print(f"\nTotal samples: {result['manifest']['total_samples']}")
    print(f"Speaker references: {len(result['speaker_references'])}")
    print(f"\nTo start training, run:")
    print("  modal run modal_unified_training.py --stages voice")
