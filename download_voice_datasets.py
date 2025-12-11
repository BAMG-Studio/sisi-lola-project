#!/usr/bin/env python3
"""
NIGERIAN VOICE DATASET DOWNLOADER & PROCESSOR
==============================================
Downloads and processes voice datasets from:
1. NaijaVoices Dataset (Yoruba, Hausa, Igbo)
2. Nigerian Pidgin ASR Dataset

Focuses on FEMALE voices for Sisi Lola character training.

Usage:
    python download_voice_datasets.py --all
    python download_voice_datasets.py --language yoruba
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import random

# Install dependencies if needed
try:
    import librosa
    import soundfile as sf
    import numpy as np
    from tqdm import tqdm
    from datasets import load_dataset
    from huggingface_hub import hf_hub_download
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                          "librosa", "soundfile", "numpy", "tqdm", "datasets", "huggingface_hub"])
    import librosa
    import soundfile as sf
    import numpy as np
    from tqdm import tqdm
    from datasets import load_dataset
    from huggingface_hub import hf_hub_download


# Configuration
BASE_DIR = Path(__file__).parent / "ml_training" / "data" / "voice_samples"
MIN_DURATION = 1.0
MAX_DURATION = 30.0
TARGET_SR = 22050


@dataclass
class AudioSample:
    """Audio sample metadata"""
    id: str
    path: str
    language: str
    gender: str
    duration: float
    sample_rate: int
    text: str
    source: str
    speaker_id: Optional[str] = None
    quality_score: Optional[float] = None


def resample_audio(input_path: str, output_path: str, target_sr: int = 22050) -> bool:
    """Resample audio to target sample rate"""
    try:
        y, sr = librosa.load(input_path, sr=None)
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        y = librosa.util.normalize(y)
        sf.write(output_path, y, target_sr)
        return True
    except Exception as e:
        print(f"Error resampling: {e}")
        return False


def get_audio_info(path: str) -> Tuple[float, int]:
    """Get audio duration and sample rate"""
    try:
        info = sf.info(path)
        return info.duration, info.samplerate
    except:
        return 0.0, 0


def compute_quality_score(audio_path: str) -> float:
    """Compute quality score (0-1)"""
    try:
        y, sr = librosa.load(audio_path, sr=22050)
        rms = librosa.feature.rms(y=y)[0]
        silence_ratio = np.sum(rms < 0.01) / len(rms)
        return 1.0 - min(silence_ratio, 1.0)
    except:
        return 0.5


class NaijaVoicesDownloader:
    """Download NaijaVoices dataset (Yoruba, Hausa, Igbo)"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.repo_id = "naijavoices/naijavoices-dataset"
        self.samples: List[AudioSample] = []
        
        # Config map for each language
        self.config_map = {
            "yoruba": ["yoruba-batch-0", "yoruba-batch-1", "yoruba-batch-2"],
            "hausa": ["hausa-batch-0", "hausa-batch-1", "hausa-batch-2"],
            "igbo": ["igbo-batch-0", "igbo-batch-1", "igbo-batch-2"],
        }
    
    def download(self, languages: List[str] = None, female_only: bool = True,
                 max_samples_per_language: int = 200) -> List[AudioSample]:
        """Download samples from NaijaVoices"""
        print(f"\n{'='*60}")
        print("DOWNLOADING NAIJAVOICES DATASET")
        print(f"{'='*60}")
        
        if languages is None:
            languages = ["yoruba", "hausa", "igbo"]
        
        for lang in languages:
            if lang not in self.config_map:
                print(f"Language {lang} not available")
                continue
            
            sample_count = 0
            print(f"\nDownloading {lang.upper()}...")
            
            for config_name in self.config_map[lang]:
                if sample_count >= max_samples_per_language:
                    break
                
                print(f"  Loading {config_name}...")
                
                try:
                    dataset = load_dataset(self.repo_id, config_name, trust_remote_code=True)
                except Exception as e:
                    print(f"  Could not load {config_name}: {e}")
                    continue
                
                for split_name in dataset.keys():
                    if sample_count >= max_samples_per_language:
                        break
                    
                    split_data = dataset[split_name]
                    columns = split_data.column_names
                    
                    # Find audio column
                    audio_col = next((c for c in columns if 'audio' in c.lower()), None)
                    text_col = next((c for c in columns if 'text' in c.lower() or 'sentence' in c.lower()), None)
                    gender_col = next((c for c in columns if 'gender' in c.lower()), None)
                    
                    if not audio_col:
                        continue
                    
                    for idx, item in enumerate(tqdm(split_data, desc=f"  {config_name}/{split_name}")):
                        if sample_count >= max_samples_per_language:
                            break
                        
                        # Get gender
                        gender = "unknown"
                        if gender_col and gender_col in item:
                            g = str(item[gender_col]).lower()
                            if g in ["f", "female"]:
                                gender = "female"
                            elif g in ["m", "male"]:
                                gender = "male"
                        
                        # Filter for female only
                        if female_only and gender == "male":
                            continue
                        
                        # Get audio
                        audio_data = item.get(audio_col)
                        if audio_data is None:
                            continue
                        
                        try:
                            # Create output directory
                            output_subdir = self.output_dir / "raw" / lang / gender
                            output_subdir.mkdir(parents=True, exist_ok=True)
                            
                            sample_id = f"naijavoices_{lang}_{config_name}_{idx:06d}"
                            output_path = output_subdir / f"{sample_id}.wav"
                            
                            # Save audio
                            if isinstance(audio_data, dict) and "array" in audio_data:
                                array = np.array(audio_data["array"])
                                sr = audio_data.get("sampling_rate", 16000)
                                sf.write(str(output_path), array, sr)
                            elif isinstance(audio_data, dict) and "path" in audio_data:
                                if os.path.exists(audio_data["path"]):
                                    shutil.copy(audio_data["path"], output_path)
                                else:
                                    continue
                            else:
                                continue
                            
                            # Check duration
                            duration, sr = get_audio_info(str(output_path))
                            if duration < MIN_DURATION or duration > MAX_DURATION:
                                output_path.unlink()
                                continue
                            
                            # Get text
                            text = ""
                            if text_col and text_col in item:
                                text = str(item[text_col])
                            
                            # Create sample record
                            sample = AudioSample(
                                id=sample_id,
                                path=str(output_path),
                                language=lang,
                                gender=gender,
                                duration=duration,
                                sample_rate=sr,
                                text=text,
                                source="naijavoices",
                            )
                            
                            self.samples.append(sample)
                            sample_count += 1
                            
                        except Exception as e:
                            continue
            
            print(f"  Downloaded {sample_count} {lang} samples")
        
        return self.samples


class NigerianPidginDownloader:
    """Download Nigerian Pidgin ASR dataset"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.repo_id = "asr-nigerian-pidgin/nigerian-pidgin-1.0"
        self.samples: List[AudioSample] = []
    
    def download(self, female_only: bool = True, max_samples: int = 200) -> List[AudioSample]:
        """Download Pidgin samples"""
        print(f"\n{'='*60}")
        print("DOWNLOADING NIGERIAN PIDGIN DATASET")
        print(f"{'='*60}")
        
        sample_count = 0
        
        try:
            dataset = load_dataset(self.repo_id, trust_remote_code=True)
            
            for split_name in dataset.keys():
                if sample_count >= max_samples:
                    break
                
                split_data = dataset[split_name]
                columns = split_data.column_names
                print(f"  Split: {split_name}, Columns: {columns}")
                
                audio_col = next((c for c in columns if 'audio' in c.lower()), None)
                text_col = next((c for c in columns if 'text' in c.lower() or 'sentence' in c.lower()), None)
                
                if not audio_col:
                    continue
                
                for idx, item in enumerate(tqdm(split_data, desc=f"  {split_name}")):
                    if sample_count >= max_samples:
                        break
                    
                    audio_data = item.get(audio_col)
                    if audio_data is None:
                        continue
                    
                    try:
                        output_subdir = self.output_dir / "raw" / "pidgin" / "unknown"
                        output_subdir.mkdir(parents=True, exist_ok=True)
                        
                        sample_id = f"pidgin_{split_name}_{idx:06d}"
                        output_path = output_subdir / f"{sample_id}.wav"
                        
                        if isinstance(audio_data, dict) and "array" in audio_data:
                            array = np.array(audio_data["array"])
                            sr = audio_data.get("sampling_rate", 16000)
                            sf.write(str(output_path), array, sr)
                        elif isinstance(audio_data, dict) and "path" in audio_data:
                            if os.path.exists(audio_data["path"]):
                                shutil.copy(audio_data["path"], output_path)
                            else:
                                continue
                        else:
                            continue
                        
                        duration, sr = get_audio_info(str(output_path))
                        if duration < MIN_DURATION or duration > MAX_DURATION:
                            output_path.unlink()
                            continue
                        
                        text = ""
                        if text_col and text_col in item:
                            text = str(item[text_col])
                        
                        sample = AudioSample(
                            id=sample_id,
                            path=str(output_path),
                            language="pidgin",
                            gender="unknown",
                            duration=duration,
                            sample_rate=sr,
                            text=text,
                            source="nigerian_pidgin",
                        )
                        
                        self.samples.append(sample)
                        sample_count += 1
                        
                    except Exception as e:
                        continue
            
            print(f"  Downloaded {sample_count} pidgin samples")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        return self.samples


class VoiceDatasetProcessor:
    """Process and organize voice samples"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.raw_dir = base_dir / "raw"
        self.processed_dir = base_dir / "processed"
        self.metadata_dir = base_dir / "metadata"
        self.female_dir = base_dir / "female"
        
        for d in [self.processed_dir, self.metadata_dir, self.female_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.all_samples: List[AudioSample] = []
    
    def add_samples(self, samples: List[AudioSample]):
        """Add samples to processor"""
        self.all_samples.extend(samples)
    
    def process_all(self, target_sr: int = 22050) -> Dict:
        """Process all samples"""
        print(f"\n{'='*60}")
        print(f"PROCESSING {len(self.all_samples)} SAMPLES")
        print(f"{'='*60}")
        
        stats = {
            "total": 0,
            "female": 0,
            "by_language": {},
            "total_duration": 0,
        }
        
        processed_samples = []
        
        for sample in tqdm(self.all_samples, desc="Processing"):
            try:
                # Compute quality
                quality = compute_quality_score(sample.path)
                sample.quality_score = quality
                
                if quality < 0.2:
                    continue
                
                # Create output dirs
                (self.processed_dir / sample.language).mkdir(parents=True, exist_ok=True)
                (self.female_dir / sample.language).mkdir(parents=True, exist_ok=True)
                
                # Resample
                output_filename = f"{sample.id}_{target_sr}hz.wav"
                processed_path = self.processed_dir / sample.language / output_filename
                
                if resample_audio(sample.path, str(processed_path), target_sr):
                    sample.path = str(processed_path)
                    sample.sample_rate = target_sr
                    
                    # Copy to female dir if female/unknown
                    if sample.gender in ["female", "unknown"]:
                        female_path = self.female_dir / sample.language / output_filename
                        shutil.copy(processed_path, female_path)
                        stats["female"] += 1
                    
                    processed_samples.append(sample)
                    stats["total"] += 1
                    stats["total_duration"] += sample.duration
                    
                    if sample.language not in stats["by_language"]:
                        stats["by_language"][sample.language] = {"count": 0, "duration": 0}
                    stats["by_language"][sample.language]["count"] += 1
                    stats["by_language"][sample.language]["duration"] += sample.duration
                    
            except Exception as e:
                continue
        
        self.all_samples = processed_samples
        self._save_metadata()
        
        return stats
    
    def _save_metadata(self):
        """Save metadata to JSON"""
        manifest = {
            "created": datetime.now().isoformat(),
            "total_samples": len(self.all_samples),
            "samples": [asdict(s) for s in self.all_samples],
        }
        
        with open(self.metadata_dir / "speaker_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Training splits
        random.shuffle(self.all_samples)
        n = len(self.all_samples)
        train_end = int(0.8 * n)
        val_end = int(0.9 * n)
        
        splits = {
            "train": [s.id for s in self.all_samples[:train_end]],
            "validation": [s.id for s in self.all_samples[train_end:val_end]],
            "test": [s.id for s in self.all_samples[val_end:]],
        }
        
        with open(self.metadata_dir / "training_splits.json", "w") as f:
            json.dump(splits, f, indent=2)
        
        print(f"Metadata saved to {self.metadata_dir}")
    
    def create_speaker_reference(self, duration: float = 60.0) -> str:
        """Create combined speaker reference for XTTS"""
        print(f"\nCreating speaker reference...")
        
        # Get best female samples
        samples = [s for s in self.all_samples if s.gender in ["female", "unknown"]]
        samples.sort(key=lambda x: x.quality_score or 0, reverse=True)
        
        # Select up to target duration
        selected = []
        total_dur = 0
        for s in samples:
            if total_dur >= duration:
                break
            if s.duration >= 2.0:
                selected.append(s)
                total_dur += s.duration
        
        if not selected:
            print("No suitable samples found")
            return None
        
        print(f"  Selected {len(selected)} samples ({total_dur:.1f}s)")
        
        # Combine audio
        combined = []
        silence = np.zeros(int(0.3 * TARGET_SR))
        
        for sample in selected:
            try:
                y, _ = librosa.load(sample.path, sr=TARGET_SR)
                combined.append(y)
                combined.append(silence)
            except:
                continue
        
        if combined:
            combined_audio = np.concatenate(combined)
            combined_audio = librosa.util.normalize(combined_audio)
            
            output_path = self.base_dir / "speaker_reference.wav"
            sf.write(str(output_path), combined_audio, TARGET_SR)
            
            print(f"Speaker reference saved: {output_path}")
            print(f"   Duration: {len(combined_audio)/TARGET_SR:.1f}s")
            
            return str(output_path)
        
        return None


def main():
    parser = argparse.ArgumentParser(description="Download Nigerian voice datasets")
    parser.add_argument("--all", action="store_true", help="Download all datasets")
    parser.add_argument("--naijavoices", action="store_true", help="Download NaijaVoices")
    parser.add_argument("--pidgin", action="store_true", help="Download Pidgin dataset")
    parser.add_argument("--max-samples", type=int, default=200, help="Max samples per language")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    
    args = parser.parse_args()
    
    # Set output directory
    output_dir = Path(args.output_dir) if args.output_dir else BASE_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"""
==============================================================
          SISI LOLA VOICE DATASET DOWNLOADER
          Nigerian Languages: Yoruba, Hausa, Igbo, Pidgin
==============================================================

Output Directory: {output_dir}
Max Samples per Language: {args.max_samples}
""")
    
    processor = VoiceDatasetProcessor(output_dir)
    
    # Download datasets
    if args.all or args.naijavoices:
        downloader = NaijaVoicesDownloader(output_dir)
        samples = downloader.download(max_samples_per_language=args.max_samples)
        processor.add_samples(samples)
    
    if args.all or args.pidgin:
        downloader = NigerianPidginDownloader(output_dir)
        samples = downloader.download(max_samples=args.max_samples)
        processor.add_samples(samples)
    
    if not (args.all or args.naijavoices or args.pidgin):
        print("No datasets selected. Use --all or --naijavoices/--pidgin")
        return
    
    # Process samples
    if processor.all_samples:
        stats = processor.process_all(target_sr=TARGET_SR)
        processor.create_speaker_reference(duration=60.0)
        
        print(f"""
==============================================================
                    DOWNLOAD COMPLETE
==============================================================

STATISTICS:
   Total Samples: {stats['total']}
   Female/Unknown: {stats['female']}
   Total Duration: {stats['total_duration']/60:.1f} minutes

BY LANGUAGE:""")
        
        for lang, lang_stats in stats.get("by_language", {}).items():
            print(f"   {lang.upper()}: {lang_stats['count']} samples ({lang_stats['duration']/60:.1f} min)")
        
        print(f"""
OUTPUT STRUCTURE:
   {output_dir}/
   ├── raw/           (Original downloads)
   ├── processed/     (Resampled to 22050Hz)
   ├── female/        (Female voice samples)
   ├── metadata/      (JSON manifests)
   └── speaker_reference.wav

Ready for XTTS training!
""")


if __name__ == "__main__":
    main()
