"""
Audio Processing Recipes for African Language Voice Datasets
For Sisi Lola Voice Dataset Curator

These recipes are used to process datasets sourced by the Voice Dataset Curator GPT
to prepare them for XTTS-v2 training in the Sisi Lola pipeline.
"""

import librosa
import soundfile as sf
from pathlib import Path
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sisi Lola Voice Training Standards
SISI_LOLA_SAMPLE_RATE = 22050  # XTTS-v2 standard
SISI_LOLA_BIT_DEPTH = 16
SISI_LOLA_CHANNELS = 1  # Mono
MIN_DURATION_SEC = 3
MAX_DURATION_SEC = 60
OPTIMAL_DURATION_SEC = (10, 30)  # Sweet spot for voice cloning


@dataclass
class AudioQualityReport:
    """Quality assessment report for an audio sample"""
    file_path: str
    duration: float
    sample_rate: int
    channels: int
    silence_ratio: float
    signal_power: float
    is_clean: bool
    is_optimal_duration: bool
    sisi_lola_compatible: bool
    recommendations: List[str]


# =============================================================================
# Recipe 1: Format Conversion
# =============================================================================

def flac_to_wav_22k(input_path: str, output_path: str) -> str:
    """
    Convert FLAC to WAV at 22050 Hz for XTTS-v2 voice cloning.
    
    Args:
        input_path: Path to input FLAC file
        output_path: Path for output WAV file
        
    Returns:
        Path to output file
    """
    audio, sr = librosa.load(input_path, sr=None)
    if sr != SISI_LOLA_SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SISI_LOLA_SAMPLE_RATE)
    sf.write(output_path, audio, SISI_LOLA_SAMPLE_RATE, subtype='PCM_16')
    logger.info(f"Converted {input_path} → {output_path} (22050 Hz WAV)")
    return output_path


def mp3_to_wav_22k(input_path: str, output_path: str) -> str:
    """Convert MP3 to WAV at 22050 Hz"""
    audio, sr = librosa.load(input_path, sr=None)
    if sr != SISI_LOLA_SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SISI_LOLA_SAMPLE_RATE)
    sf.write(output_path, audio, SISI_LOLA_SAMPLE_RATE, subtype='PCM_16')
    logger.info(f"Converted {input_path} → {output_path} (22050 Hz WAV)")
    return output_path


def convert_any_to_sisi_format(input_path: str, output_dir: str) -> str:
    """
    Convert any audio format to Sisi Lola standard format.
    
    Standard: WAV, 22050 Hz, 16-bit, Mono
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{input_path.stem}.wav"
    
    # Load audio at original sample rate
    audio, sr = librosa.load(str(input_path), sr=None, mono=True)
    
    # Resample if needed
    if sr != SISI_LOLA_SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SISI_LOLA_SAMPLE_RATE)
    
    # Normalize volume
    audio = librosa.util.normalize(audio)
    
    # Save as WAV
    sf.write(str(output_path), audio, SISI_LOLA_SAMPLE_RATE, subtype='PCM_16')
    
    return str(output_path)


# =============================================================================
# Recipe 2: Batch Processing
# =============================================================================

def batch_convert_bibletts(input_dir: str, output_dir: str, target_sr: int = 22050) -> List[str]:
    """
    Batch convert BibleTTS FLAC files (48kHz) to Sisi Lola format.
    
    BibleTTS files are high-quality studio recordings at 48kHz.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    converted_files = []
    
    for flac_file in input_path.glob("**/*.flac"):
        audio, sr = librosa.load(str(flac_file), sr=48000)
        audio_resampled = librosa.resample(audio, orig_sr=48000, target_sr=target_sr)
        audio_normalized = librosa.util.normalize(audio_resampled)
        
        out_file = output_path / flac_file.with_suffix('.wav').name
        sf.write(str(out_file), audio_normalized, target_sr, subtype='PCM_16')
        converted_files.append(str(out_file))
        logger.info(f"Processed: {flac_file.name}")
    
    return converted_files


def batch_convert_directory(
    input_dir: str, 
    output_dir: str, 
    extensions: List[str] = ['.wav', '.flac', '.mp3', '.ogg']
) -> List[str]:
    """Batch convert all audio files in a directory to Sisi Lola format"""
    input_path = Path(input_dir)
    converted_files = []
    
    for ext in extensions:
        for audio_file in input_path.glob(f"**/*{ext}"):
            try:
                out_file = convert_any_to_sisi_format(str(audio_file), output_dir)
                converted_files.append(out_file)
            except Exception as e:
                logger.error(f"Failed to convert {audio_file}: {e}")
    
    return converted_files


# =============================================================================
# Recipe 3: Duration Filtering
# =============================================================================

def filter_by_duration(
    audio_dir: str, 
    min_sec: float = MIN_DURATION_SEC, 
    max_sec: float = MAX_DURATION_SEC
) -> Tuple[List[str], List[str]]:
    """
    Filter audio files by duration range.
    
    Returns:
        Tuple of (valid_files, rejected_files)
    """
    valid_files = []
    rejected_files = []
    
    for audio_file in Path(audio_dir).glob("**/*.wav"):
        try:
            duration = librosa.get_duration(path=str(audio_file))
            if min_sec <= duration <= max_sec:
                valid_files.append(str(audio_file))
            else:
                rejected_files.append(str(audio_file))
        except Exception as e:
            logger.error(f"Error processing {audio_file}: {e}")
            rejected_files.append(str(audio_file))
    
    logger.info(f"Duration filter: {len(valid_files)} valid, {len(rejected_files)} rejected")
    return valid_files, rejected_files


def get_optimal_duration_samples(audio_dir: str) -> List[str]:
    """Get samples in the optimal duration range (10-30s) for voice cloning"""
    valid, _ = filter_by_duration(
        audio_dir, 
        min_sec=OPTIMAL_DURATION_SEC[0], 
        max_sec=OPTIMAL_DURATION_SEC[1]
    )
    return valid


# =============================================================================
# Recipe 4: HuggingFace Dataset Export
# =============================================================================

def hf_to_wav(
    dataset_name: str, 
    language_subset: str, 
    output_dir: str, 
    target_sr: int = SISI_LOLA_SAMPLE_RATE,
    max_samples: Optional[int] = None
) -> Dict:
    """
    Load HuggingFace dataset and export audio to WAV files with transcripts.
    
    Args:
        dataset_name: HuggingFace dataset ID
        language_subset: Language subset/split
        output_dir: Output directory
        target_sr: Target sample rate
        max_samples: Maximum samples to process (None for all)
    
    Returns:
        Dict with manifest of exported files
    """
    from datasets import load_dataset
    
    dataset = load_dataset(dataset_name, language_subset, split="train")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "dataset": dataset_name,
        "language": language_subset,
        "sample_rate": target_sr,
        "files": []
    }
    
    samples_to_process = len(dataset) if max_samples is None else min(max_samples, len(dataset))
    
    for i, sample in enumerate(dataset):
        if i >= samples_to_process:
            break
            
        audio_array = np.array(sample['audio']['array'], dtype=np.float32)
        sample_rate = sample['audio']['sampling_rate']
        
        # Resample if needed
        if sample_rate != target_sr:
            audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=target_sr)
        
        # Normalize
        audio_array = librosa.util.normalize(audio_array)
        
        # Generate filenames
        audio_file = output_path / f"{language_subset}_{i:05d}.wav"
        transcript_file = output_path / f"{language_subset}_{i:05d}.txt"
        
        # Save audio
        sf.write(str(audio_file), audio_array, target_sr, subtype='PCM_16')
        
        # Save transcript if available
        text = sample.get('text', sample.get('sentence', sample.get('transcription', '')))
        if text:
            transcript_file.write_text(text, encoding='utf-8')
        
        # Add to manifest
        manifest["files"].append({
            "audio": str(audio_file.name),
            "transcript": str(transcript_file.name) if text else None,
            "text": text,
            "duration": len(audio_array) / target_sr
        })
        
        if (i + 1) % 100 == 0:
            logger.info(f"Exported {i + 1}/{samples_to_process} files...")
    
    # Save manifest
    manifest_file = output_path / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported {len(manifest['files'])} samples to {output_dir}")
    return manifest


# =============================================================================
# Recipe 5: Quality Assessment
# =============================================================================

def quality_check(audio_file: str, silence_threshold: float = 0.01) -> AudioQualityReport:
    """
    Comprehensive quality check for an audio sample.
    
    Returns AudioQualityReport with Sisi Lola compatibility assessment.
    """
    audio, sr = librosa.load(audio_file, sr=None)
    
    # Duration
    duration = len(audio) / sr
    is_optimal = OPTIMAL_DURATION_SEC[0] <= duration <= OPTIMAL_DURATION_SEC[1]
    
    # Silence analysis
    non_silent_intervals = librosa.effects.split(audio, top_db=20)
    total_non_silent = sum([end - start for start, end in non_silent_intervals])
    silence_ratio = 1 - (total_non_silent / len(audio)) if len(audio) > 0 else 1
    
    # Signal power (rough SNR indicator)
    signal_power = float(np.mean(audio ** 2))
    
    # Channel count
    channels = 1 if audio.ndim == 1 else audio.shape[0]
    
    # Determine if clean
    is_clean = silence_ratio < 0.3 and signal_power > silence_threshold
    
    # Build recommendations
    recommendations = []
    
    if sr != SISI_LOLA_SAMPLE_RATE:
        recommendations.append(f"Resample from {sr}Hz to {SISI_LOLA_SAMPLE_RATE}Hz")
    
    if channels > 1:
        recommendations.append("Convert to mono")
    
    if silence_ratio > 0.3:
        recommendations.append("Remove excessive silence (trim/split)")
    
    if duration < MIN_DURATION_SEC:
        recommendations.append(f"Duration too short ({duration:.1f}s < {MIN_DURATION_SEC}s)")
    elif duration > MAX_DURATION_SEC:
        recommendations.append(f"Duration too long ({duration:.1f}s > {MAX_DURATION_SEC}s)")
    
    if signal_power < silence_threshold:
        recommendations.append("Audio level too low - normalize")
    
    # Sisi Lola compatibility
    sisi_compatible = (
        sr == SISI_LOLA_SAMPLE_RATE and
        channels == 1 and
        MIN_DURATION_SEC <= duration <= MAX_DURATION_SEC and
        is_clean
    )
    
    return AudioQualityReport(
        file_path=audio_file,
        duration=duration,
        sample_rate=sr,
        channels=channels,
        silence_ratio=silence_ratio,
        signal_power=signal_power,
        is_clean=is_clean,
        is_optimal_duration=is_optimal,
        sisi_lola_compatible=sisi_compatible,
        recommendations=recommendations
    )


def batch_quality_check(audio_dir: str) -> Dict:
    """
    Run quality checks on all audio files in a directory.
    
    Returns summary report.
    """
    reports = []
    
    for audio_file in Path(audio_dir).glob("**/*.wav"):
        try:
            report = quality_check(str(audio_file))
            reports.append(report)
        except Exception as e:
            logger.error(f"Quality check failed for {audio_file}: {e}")
    
    # Summary
    total = len(reports)
    compatible = sum(1 for r in reports if r.sisi_lola_compatible)
    optimal_duration = sum(1 for r in reports if r.is_optimal_duration)
    clean = sum(1 for r in reports if r.is_clean)
    
    summary = {
        "total_files": total,
        "sisi_lola_compatible": compatible,
        "compatibility_rate": compatible / total if total > 0 else 0,
        "optimal_duration_count": optimal_duration,
        "clean_audio_count": clean,
        "reports": [
            {
                "file": r.file_path,
                "duration": r.duration,
                "sample_rate": r.sample_rate,
                "compatible": r.sisi_lola_compatible,
                "recommendations": r.recommendations
            }
            for r in reports
        ]
    }
    
    return summary


# =============================================================================
# Recipe 6: NaijaVoices Specific Loader
# =============================================================================

def download_naijavoices_language(
    language: str = "igbo", 
    batch: int = 0, 
    cache_dir: str = "./data"
) -> Dict:
    """
    Download specific NaijaVoices language batch.
    
    Languages: igbo, hausa, yoruba
    """
    from datasets import load_dataset
    
    subset_name = f"{language}-batch-{batch}"
    
    try:
        dataset = load_dataset(
            "naijavoices/naijavoices-dataset",
            subset_name,
            cache_dir=cache_dir
        )
        
        logger.info(f"Downloaded {language} batch {batch}: {len(dataset['train'])} samples")
        
        return {
            "dataset": dataset,
            "language": language,
            "batch": batch,
            "sample_count": len(dataset['train'])
        }
    except Exception as e:
        logger.error(f"Failed to download NaijaVoices {language} batch {batch}: {e}")
        return {"error": str(e)}


# =============================================================================
# Recipe 7: Silence Removal & Trimming
# =============================================================================

def trim_silence(audio_file: str, output_file: str, top_db: int = 20) -> str:
    """Remove leading and trailing silence from audio"""
    audio, sr = librosa.load(audio_file, sr=None)
    
    # Trim silence
    audio_trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
    
    sf.write(output_file, audio_trimmed, sr, subtype='PCM_16')
    
    original_duration = len(audio) / sr
    trimmed_duration = len(audio_trimmed) / sr
    
    logger.info(f"Trimmed {audio_file}: {original_duration:.1f}s → {trimmed_duration:.1f}s")
    
    return output_file


def split_on_silence(
    audio_file: str, 
    output_dir: str, 
    min_duration: float = 5.0,
    top_db: int = 25
) -> List[str]:
    """
    Split audio on silence into separate chunks.
    
    Useful for processing long recordings into voice cloning samples.
    """
    audio, sr = librosa.load(audio_file, sr=None)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find non-silent intervals
    intervals = librosa.effects.split(audio, top_db=top_db)
    
    output_files = []
    stem = Path(audio_file).stem
    
    for i, (start, end) in enumerate(intervals):
        chunk = audio[start:end]
        duration = len(chunk) / sr
        
        if duration >= min_duration:
            out_file = output_path / f"{stem}_chunk_{i:03d}.wav"
            sf.write(str(out_file), chunk, sr, subtype='PCM_16')
            output_files.append(str(out_file))
    
    logger.info(f"Split {audio_file} into {len(output_files)} chunks")
    return output_files


# =============================================================================
# Recipe 8: Create Training Manifest
# =============================================================================

def create_sisi_lola_manifest(
    audio_dir: str,
    output_file: str,
    language: str = "yoruba",
    dialect: str = "lagos",
    speaker_name: str = "sisi_lola"
) -> Dict:
    """
    Create a training manifest in Sisi Lola format.
    
    Compatible with train_nigerian_voice.py
    """
    audio_path = Path(audio_dir)
    
    manifest = {
        "name": f"{speaker_name}_{language}_{dialect}",
        "language": language,
        "dialect": dialect,
        "speaker": speaker_name,
        "source": "curator",
        "created": str(Path(output_file).stat().st_mtime if Path(output_file).exists() else "new"),
        "audio_format": {
            "sample_rate": SISI_LOLA_SAMPLE_RATE,
            "channels": 1,
            "format": "wav"
        },
        "samples": []
    }
    
    for wav_file in sorted(audio_path.glob("*.wav")):
        txt_file = wav_file.with_suffix('.txt')
        
        # Get duration
        try:
            duration = librosa.get_duration(path=str(wav_file))
        except:
            continue
        
        # Get transcript
        transcript = ""
        if txt_file.exists():
            transcript = txt_file.read_text(encoding='utf-8').strip()
        
        # Quality check
        report = quality_check(str(wav_file))
        
        manifest["samples"].append({
            "audio_path": str(wav_file.name),
            "text": transcript,
            "duration": duration,
            "quality_score": 1.0 if report.sisi_lola_compatible else 0.5,
            "is_clean": report.is_clean,
            "language": language,
            "dialect": dialect
        })
    
    # Save manifest
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created manifest with {len(manifest['samples'])} samples: {output_file}")
    return manifest


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Audio Processing Recipes")
    parser.add_argument("recipe", choices=[
        "convert", "batch_convert", "filter_duration", 
        "hf_export", "quality_check", "create_manifest"
    ])
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output file or directory")
    parser.add_argument("--language", "-l", default="yoruba", help="Language code")
    
    args = parser.parse_args()
    
    if args.recipe == "convert":
        convert_any_to_sisi_format(args.input, args.output)
    elif args.recipe == "batch_convert":
        batch_convert_directory(args.input, args.output)
    elif args.recipe == "filter_duration":
        valid, rejected = filter_by_duration(args.input)
        print(f"Valid: {len(valid)}, Rejected: {len(rejected)}")
    elif args.recipe == "quality_check":
        summary = batch_quality_check(args.input)
        print(json.dumps(summary, indent=2))
    elif args.recipe == "create_manifest":
        create_sisi_lola_manifest(args.input, args.output, language=args.language)
