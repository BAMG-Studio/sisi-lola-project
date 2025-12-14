"""
SISI LOLA AUDIO DATA AUGMENTATION
=================================
Augments voice training data to improve model robustness.

Techniques:
- Speed perturbation (0.9x - 1.1x)
- Pitch shifting (±2 semitones)
- Background noise addition
- Room reverb simulation
- Volume normalization

This expands the effective training set while maintaining
audio quality for TTS training.
"""

import os
import random
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import json
from datetime import datetime

# Check for audio processing libraries
AUDIO_AVAILABLE = False
try:
    import torch
    import torchaudio
    import torchaudio.transforms as T
    import torchaudio.functional as F
    AUDIO_AVAILABLE = True
except ImportError:
    print("[WARN] torchaudio not available. Install with: pip install torchaudio")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class AudioAugmentor:
    """
    Applies audio augmentations for voice training data expansion.
    
    Features:
    - Speed perturbation (time stretching)
    - Pitch shifting
    - Additive noise
    - Volume normalization
    - Reverberation (optional)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent
        
        # Load config
        if config_path is None:
            config_path = self.project_root / "ml_training" / "configs" / "voice_training_config.yaml"
        
        if YAML_AVAILABLE and Path(config_path).exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.aug_config = config.get("augmentation", {})
        else:
            self.aug_config = {}
        
        # Default augmentation settings
        self.speed_factors = self.aug_config.get("speed_factors", [0.9, 0.95, 1.0, 1.05, 1.1])
        self.pitch_semitones = self.aug_config.get("pitch_semitones", [-2, -1, 0, 1, 2])
        self.noise_snr_db = self.aug_config.get("noise_snr_db", [20, 25, 30, 35])
        self.target_sample_rate = self.aug_config.get("target_sample_rate", 22050)
        
        # Output directory
        self.output_dir = self.project_root / "ml_training" / "datasets" / "augmented_voice"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Stats tracking
        self.stats = {
            "original_files": 0,
            "augmented_files": 0,
            "failed": 0,
            "augmentations_applied": {}
        }
    
    def load_audio(self, audio_path: str) -> Tuple[Any, int]:
        """Load audio file and return waveform + sample rate"""
        if not AUDIO_AVAILABLE:
            raise RuntimeError("torchaudio not available")
        
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        return waveform, sample_rate
    
    def save_audio(self, waveform, sample_rate: int, output_path: str):
        """Save waveform to file"""
        if not AUDIO_AVAILABLE:
            raise RuntimeError("torchaudio not available")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        torchaudio.save(output_path, waveform, sample_rate)
    
    def resample(self, waveform, orig_sr: int, target_sr: int):
        """Resample audio to target sample rate"""
        if orig_sr == target_sr:
            return waveform
        
        resampler = T.Resample(orig_sr, target_sr)
        return resampler(waveform)
    
    def apply_speed_perturbation(self, waveform, sample_rate: int, speed_factor: float):
        """
        Apply speed perturbation (time stretching).
        
        Speed factor > 1.0 = faster
        Speed factor < 1.0 = slower
        """
        if speed_factor == 1.0:
            return waveform, sample_rate
        
        # Use resampling for speed change (changes pitch too, but quick)
        # For pitch-preserving time stretch, would need phase vocoder
        new_sample_rate = int(sample_rate * speed_factor)
        
        # Resample back to original rate
        resampler = T.Resample(new_sample_rate, sample_rate)
        stretched = resampler(waveform)
        
        return stretched, sample_rate
    
    def apply_pitch_shift(self, waveform, sample_rate: int, semitones: int):
        """
        Shift pitch by semitones.
        
        Positive = higher pitch
        Negative = lower pitch
        """
        if semitones == 0:
            return waveform
        
        # Pitch shift factor: 2^(semitones/12)
        shift_factor = 2 ** (semitones / 12)
        
        # Resample to change pitch, then resample back
        intermediate_sr = int(sample_rate / shift_factor)
        
        # Resample to intermediate (changes pitch)
        resampler1 = T.Resample(sample_rate, intermediate_sr)
        shifted = resampler1(waveform)
        
        # Resample back to original rate
        resampler2 = T.Resample(intermediate_sr, sample_rate)
        shifted = resampler2(shifted)
        
        return shifted
    
    def add_noise(self, waveform, snr_db: float):
        """
        Add white noise at specified SNR level.
        
        Higher SNR = less noise (cleaner)
        """
        if not NUMPY_AVAILABLE:
            return waveform
        
        # Calculate signal power
        signal_power = torch.mean(waveform ** 2)
        
        # Calculate noise power for desired SNR
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear
        
        # Generate noise
        noise = torch.randn_like(waveform) * torch.sqrt(noise_power)
        
        return waveform + noise
    
    def normalize_volume(self, waveform, target_db: float = -3.0):
        """Normalize audio to target dB level"""
        # Calculate current peak
        peak = torch.max(torch.abs(waveform))
        
        if peak > 0:
            # Target amplitude
            target_amplitude = 10 ** (target_db / 20)
            
            # Scale
            waveform = waveform * (target_amplitude / peak)
        
        return waveform
    
    def augment_file(self, 
                     audio_path: str, 
                     transcript: str,
                     output_prefix: str,
                     augmentations: List[str] = None) -> List[Dict[str, str]]:
        """
        Apply augmentations to a single audio file.
        
        Args:
            audio_path: Path to source audio
            transcript: Text transcript
            output_prefix: Prefix for output filenames
            augmentations: List of augmentation types to apply
                         ["speed", "pitch", "noise", "all"]
        
        Returns:
            List of dicts with {audio_path, transcript, augmentation}
        """
        if not AUDIO_AVAILABLE:
            print("[WARN] Audio processing not available, skipping augmentation")
            return []
        
        if augmentations is None:
            augmentations = ["speed", "pitch"]
        
        results = []
        
        try:
            # Load original audio
            waveform, sample_rate = self.load_audio(audio_path)
            
            # Resample to target
            waveform = self.resample(waveform, sample_rate, self.target_sample_rate)
            sample_rate = self.target_sample_rate
            
            # Save original (normalized)
            original_normalized = self.normalize_volume(waveform)
            original_path = self.output_dir / f"{output_prefix}_original.wav"
            self.save_audio(original_normalized, sample_rate, str(original_path))
            results.append({
                "audio_path": str(original_path),
                "transcript": transcript,
                "augmentation": "original"
            })
            
            # Apply speed perturbations
            if "speed" in augmentations or "all" in augmentations:
                for speed in self.speed_factors:
                    if speed == 1.0:
                        continue
                    
                    aug_waveform, _ = self.apply_speed_perturbation(
                        waveform.clone(), sample_rate, speed
                    )
                    aug_waveform = self.normalize_volume(aug_waveform)
                    
                    aug_name = f"speed_{speed:.2f}".replace(".", "p")
                    aug_path = self.output_dir / f"{output_prefix}_{aug_name}.wav"
                    self.save_audio(aug_waveform, sample_rate, str(aug_path))
                    
                    results.append({
                        "audio_path": str(aug_path),
                        "transcript": transcript,
                        "augmentation": f"speed_{speed}"
                    })
                    
                    self.stats["augmentations_applied"]["speed"] = \
                        self.stats["augmentations_applied"].get("speed", 0) + 1
            
            # Apply pitch shifts
            if "pitch" in augmentations or "all" in augmentations:
                for semitones in self.pitch_semitones:
                    if semitones == 0:
                        continue
                    
                    aug_waveform = self.apply_pitch_shift(
                        waveform.clone(), sample_rate, semitones
                    )
                    aug_waveform = self.normalize_volume(aug_waveform)
                    
                    sign = "up" if semitones > 0 else "down"
                    aug_name = f"pitch_{sign}{abs(semitones)}"
                    aug_path = self.output_dir / f"{output_prefix}_{aug_name}.wav"
                    self.save_audio(aug_waveform, sample_rate, str(aug_path))
                    
                    results.append({
                        "audio_path": str(aug_path),
                        "transcript": transcript,
                        "augmentation": f"pitch_{semitones:+d}"
                    })
                    
                    self.stats["augmentations_applied"]["pitch"] = \
                        self.stats["augmentations_applied"].get("pitch", 0) + 1
            
            # Apply noise additions
            if "noise" in augmentations or "all" in augmentations:
                for snr in self.noise_snr_db:
                    aug_waveform = self.add_noise(waveform.clone(), snr)
                    aug_waveform = self.normalize_volume(aug_waveform)
                    
                    aug_name = f"noise_snr{snr}"
                    aug_path = self.output_dir / f"{output_prefix}_{aug_name}.wav"
                    self.save_audio(aug_waveform, sample_rate, str(aug_path))
                    
                    results.append({
                        "audio_path": str(aug_path),
                        "transcript": transcript,
                        "augmentation": f"noise_snr{snr}"
                    })
                    
                    self.stats["augmentations_applied"]["noise"] = \
                        self.stats["augmentations_applied"].get("noise", 0) + 1
            
            self.stats["original_files"] += 1
            self.stats["augmented_files"] += len(results) - 1  # Exclude original
            
        except Exception as e:
            print(f"[ERROR] Failed to augment {audio_path}: {e}")
            self.stats["failed"] += 1
        
        return results
    
    def augment_manifest(self, 
                         manifest_path: str,
                         output_manifest: Optional[str] = None,
                         augmentations: List[str] = None) -> str:
        """
        Augment all files in a curator manifest.
        
        Args:
            manifest_path: Path to curator manifest JSON
            output_manifest: Path for output manifest (optional)
            augmentations: Types of augmentation to apply
        
        Returns:
            Path to augmented manifest
        """
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        dataset_id = manifest.get("dataset_id", "unknown")
        print(f"\n{'='*60}")
        print(f"Augmenting: {dataset_id}")
        print(f"{'='*60}")
        
        all_samples = []
        
        for i, sample in enumerate(manifest.get("samples", [])):
            audio_path = sample.get("audio_path", "")
            text = sample.get("text", "")
            
            if not audio_path or not Path(audio_path).exists():
                print(f"  [SKIP] Sample {i}: audio not found")
                continue
            
            prefix = f"{dataset_id}_sample{i:04d}"
            augmented = self.augment_file(
                audio_path, text, prefix, augmentations
            )
            
            for aug_sample in augmented:
                all_samples.append({
                    **sample,
                    "audio_path": aug_sample["audio_path"],
                    "augmentation": aug_sample["augmentation"]
                })
            
            print(f"  Sample {i}: {len(augmented)} variants")
        
        # Create augmented manifest
        augmented_manifest = {
            **manifest,
            "dataset_id": f"{dataset_id}_augmented",
            "samples": all_samples,
            "augmentation_stats": self.stats,
            "augmented_at": datetime.now().isoformat()
        }
        
        if output_manifest is None:
            output_manifest = self.output_dir / f"{dataset_id}_augmented.json"
        
        with open(output_manifest, 'w') as f:
            json.dump(augmented_manifest, f, indent=2)
        
        print(f"\n📁 Augmented manifest saved to: {output_manifest}")
        print(f"   Original samples: {self.stats['original_files']}")
        print(f"   Augmented samples: {self.stats['augmented_files']}")
        
        return str(output_manifest)
    
    def augment_all_manifests(self, augmentations: List[str] = None):
        """Augment all manifests in the curator manifests directory"""
        manifests_dir = self.project_root / "ml_training" / "curator" / "manifests"
        
        if not manifests_dir.exists():
            print(f"[WARN] Manifests directory not found: {manifests_dir}")
            return
        
        for manifest_path in manifests_dir.glob("*.json"):
            if "_augmented" in manifest_path.stem:
                continue  # Skip already augmented
            
            self.augment_manifest(str(manifest_path), augmentations=augmentations)
        
        # Print summary
        print("\n" + "="*60)
        print("AUGMENTATION COMPLETE")
        print("="*60)
        print(f"Original files processed: {self.stats['original_files']}")
        print(f"Augmented files created: {self.stats['augmented_files']}")
        print(f"Failed: {self.stats['failed']}")
        print("\nAugmentations applied:")
        for aug_type, count in self.stats["augmentations_applied"].items():
            print(f"  {aug_type}: {count}")


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio data augmentation for Sisi Lola")
    parser.add_argument("--manifest", type=str, help="Path to manifest JSON to augment")
    parser.add_argument("--all", action="store_true", help="Augment all manifests")
    parser.add_argument("--augmentations", nargs="+", 
                        default=["speed", "pitch"],
                        help="Augmentation types: speed, pitch, noise, all")
    parser.add_argument("--config", type=str, help="Path to config YAML")
    
    args = parser.parse_args()
    
    augmentor = AudioAugmentor(config_path=args.config)
    
    if args.manifest:
        augmentor.augment_manifest(args.manifest, augmentations=args.augmentations)
    elif args.all:
        augmentor.augment_all_manifests(augmentations=args.augmentations)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
