"""
Sisi Lola Curated Samples Validator

Validates audio samples curated by the Voice Dataset Curator GPT
to ensure they meet Sisi Lola's training requirements.

Requirements:
- Audio format: WAV, 22050 Hz, mono
- Duration: 3-60 seconds (optimal: 10-30 seconds)
- Quality: Clean speech, minimal background noise
- Speaker: Female, matches Sisi Lola persona (28-40, Lagos accent)
"""

import librosa
import numpy as np
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# Constants - Sisi Lola Voice Standards
# =============================================================================

# Audio format requirements
REQUIRED_SAMPLE_RATE = 22050
REQUIRED_CHANNELS = 1
REQUIRED_FORMAT = "wav"

# Duration requirements
MIN_DURATION = 3.0  # seconds
MAX_DURATION = 60.0  # seconds
OPTIMAL_MIN_DURATION = 10.0  # seconds
OPTIMAL_MAX_DURATION = 30.0  # seconds

# Quality thresholds
MIN_SIGNAL_POWER = 0.001  # Minimum RMS power
MAX_SILENCE_RATIO = 0.40  # Maximum silence ratio
MIN_SNR_ESTIMATE = 10.0  # Minimum signal-to-noise ratio (dB)

# Sisi Lola persona matching
SISI_PERSONA = {
    "gender": "female",
    "age_range": "28-40",
    "accent": "nigerian",
    "dialects": ["lagos", "yoruba", "pidgin", "nigerian_english"],
    "energy": "high",
    "style": ["expressive", "playful", "dramatic"]
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ValidationResult:
    """Result of validating a single audio sample"""
    file_path: str
    valid: bool
    
    # Format checks
    sample_rate: int
    sample_rate_valid: bool
    channels: int
    channels_valid: bool
    format: str
    format_valid: bool
    
    # Duration checks
    duration: float
    duration_valid: bool
    duration_optimal: bool
    
    # Quality checks
    signal_power: float
    signal_power_valid: bool
    silence_ratio: float
    silence_ratio_valid: bool
    snr_estimate: float
    snr_valid: bool
    is_clean: bool
    
    # Persona matching
    persona_match_score: float
    sisi_compatible: bool
    
    # Recommendations
    issues: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BatchValidationReport:
    """Report for validating a batch of samples"""
    total_files: int
    valid_count: int
    invalid_count: int
    sisi_compatible_count: int
    
    # Aggregate stats
    total_duration_hours: float
    average_quality_score: float
    
    # By category
    format_issues: int
    duration_issues: int
    quality_issues: int
    
    # Results
    results: List[ValidationResult]
    
    # Summary
    summary: str
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "total_files": self.total_files,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "sisi_compatible_count": self.sisi_compatible_count,
            "total_duration_hours": self.total_duration_hours,
            "average_quality_score": self.average_quality_score,
            "format_issues": self.format_issues,
            "duration_issues": self.duration_issues,
            "quality_issues": self.quality_issues,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "results": [r.to_dict() for r in self.results]
        }


# =============================================================================
# Validation Functions
# =============================================================================

def estimate_snr(audio: np.ndarray, sr: int, noise_floor_percentile: float = 10) -> float:
    """
    Estimate Signal-to-Noise Ratio.
    
    Uses the percentile method to estimate noise floor.
    """
    try:
        # Compute frame-level RMS
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)  # 10ms hop
        
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Estimate noise floor as low percentile of RMS
        noise_floor = np.percentile(rms, noise_floor_percentile)
        
        # Signal level as high percentile
        signal_level = np.percentile(rms, 90)
        
        # Avoid division by zero
        if noise_floor < 1e-10:
            noise_floor = 1e-10
        
        # Calculate SNR in dB
        snr_db = 20 * np.log10(signal_level / noise_floor)
        
        return float(snr_db)
    except Exception as e:
        logger.warning(f"SNR estimation failed: {e}")
        return 0.0


def calculate_silence_ratio(audio: np.ndarray, sr: int, top_db: int = 25) -> float:
    """Calculate the ratio of silence in the audio"""
    try:
        non_silent_intervals = librosa.effects.split(audio, top_db=top_db)
        
        if len(non_silent_intervals) == 0:
            return 1.0  # All silence
        
        total_non_silent = sum(end - start for start, end in non_silent_intervals)
        silence_ratio = 1.0 - (total_non_silent / len(audio))
        
        return float(max(0.0, min(1.0, silence_ratio)))
    except Exception as e:
        logger.warning(f"Silence ratio calculation failed: {e}")
        return 0.5


def estimate_persona_match(
    audio: np.ndarray, 
    sr: int, 
    language: str = "unknown",
    metadata: Optional[Dict] = None
) -> float:
    """
    Estimate how well the audio matches Sisi Lola's persona.
    
    This is a heuristic based on available metadata and audio features.
    """
    score = 0.5  # Base score
    
    # Check metadata if available
    if metadata:
        # Gender check
        if metadata.get("speaker_gender", "").lower() == "female":
            score += 0.2
        
        # Language/dialect check
        lang = metadata.get("language", language).lower()
        dialect = metadata.get("dialect", "").lower()
        
        if lang in ["yoruba", "pidgin", "nigerian_pidgin", "nigerian_english", "hausa", "igbo"]:
            score += 0.15
        
        if dialect in ["lagos", "nigerian"]:
            score += 0.1
        
        # Age range check
        if metadata.get("speaker_age_range") in ["25-35", "28-40", "30-40"]:
            score += 0.05
    
    # Audio feature checks (pitch analysis for female voice)
    try:
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitches = pitches[magnitudes > np.median(magnitudes)]
        
        if len(pitches) > 0:
            median_pitch = np.median(pitches[pitches > 0])
            
            # Female voice typically 165-255 Hz
            if 150 < median_pitch < 300:
                score += 0.1
    except:
        pass
    
    return min(1.0, score)


def validate_sample(
    file_path: str,
    metadata: Optional[Dict] = None
) -> ValidationResult:
    """
    Validate a single audio sample against Sisi Lola requirements.
    """
    issues = []
    recommendations = []
    
    path = Path(file_path)
    
    # Check format
    file_format = path.suffix.lower().lstrip('.')
    format_valid = file_format == REQUIRED_FORMAT
    if not format_valid:
        issues.append(f"Wrong format: {file_format} (expected {REQUIRED_FORMAT})")
        recommendations.append(f"Convert to WAV format")
    
    # Load audio
    try:
        audio, sr = librosa.load(str(file_path), sr=None, mono=True)
    except Exception as e:
        return ValidationResult(
            file_path=str(file_path),
            valid=False,
            sample_rate=0,
            sample_rate_valid=False,
            channels=0,
            channels_valid=False,
            format=file_format,
            format_valid=format_valid,
            duration=0,
            duration_valid=False,
            duration_optimal=False,
            signal_power=0,
            signal_power_valid=False,
            silence_ratio=1.0,
            silence_ratio_valid=False,
            snr_estimate=0,
            snr_valid=False,
            is_clean=False,
            persona_match_score=0,
            sisi_compatible=False,
            issues=[f"Failed to load audio: {e}"],
            recommendations=["Check file integrity"]
        )
    
    # Sample rate check
    sample_rate_valid = sr == REQUIRED_SAMPLE_RATE
    if not sample_rate_valid:
        issues.append(f"Wrong sample rate: {sr}Hz (expected {REQUIRED_SAMPLE_RATE}Hz)")
        recommendations.append(f"Resample to {REQUIRED_SAMPLE_RATE}Hz")
    
    # Channels check (after loading with mono=True, this should be 1)
    channels = 1 if audio.ndim == 1 else audio.shape[0]
    channels_valid = channels == REQUIRED_CHANNELS
    
    # Duration check
    duration = len(audio) / sr
    duration_valid = MIN_DURATION <= duration <= MAX_DURATION
    duration_optimal = OPTIMAL_MIN_DURATION <= duration <= OPTIMAL_MAX_DURATION
    
    if duration < MIN_DURATION:
        issues.append(f"Too short: {duration:.1f}s (minimum {MIN_DURATION}s)")
        recommendations.append("Find longer samples or concatenate")
    elif duration > MAX_DURATION:
        issues.append(f"Too long: {duration:.1f}s (maximum {MAX_DURATION}s)")
        recommendations.append("Split into smaller segments")
    elif not duration_optimal:
        recommendations.append(f"Optimal duration is {OPTIMAL_MIN_DURATION}-{OPTIMAL_MAX_DURATION}s")
    
    # Signal power check
    signal_power = float(np.sqrt(np.mean(audio ** 2)))  # RMS
    signal_power_valid = signal_power >= MIN_SIGNAL_POWER
    if not signal_power_valid:
        issues.append(f"Audio too quiet: RMS={signal_power:.6f}")
        recommendations.append("Normalize audio volume")
    
    # Silence ratio check
    silence_ratio = calculate_silence_ratio(audio, sr)
    silence_ratio_valid = silence_ratio <= MAX_SILENCE_RATIO
    if not silence_ratio_valid:
        issues.append(f"Too much silence: {silence_ratio*100:.1f}%")
        recommendations.append("Trim silence from audio")
    
    # SNR estimate
    snr_estimate = estimate_snr(audio, sr)
    snr_valid = snr_estimate >= MIN_SNR_ESTIMATE
    if not snr_valid:
        issues.append(f"Low SNR: {snr_estimate:.1f}dB")
        recommendations.append("Apply noise reduction")
    
    # Overall quality
    is_clean = signal_power_valid and silence_ratio_valid and snr_valid
    
    # Persona match
    persona_match_score = estimate_persona_match(audio, sr, metadata=metadata)
    
    # Sisi Lola compatibility
    sisi_compatible = (
        format_valid and
        sample_rate_valid and
        duration_valid and
        is_clean and
        persona_match_score >= 0.5
    )
    
    # Overall validity
    valid = format_valid and sample_rate_valid and duration_valid and is_clean
    
    return ValidationResult(
        file_path=str(file_path),
        valid=valid,
        sample_rate=sr,
        sample_rate_valid=sample_rate_valid,
        channels=channels,
        channels_valid=channels_valid,
        format=file_format,
        format_valid=format_valid,
        duration=duration,
        duration_valid=duration_valid,
        duration_optimal=duration_optimal,
        signal_power=signal_power,
        signal_power_valid=signal_power_valid,
        silence_ratio=silence_ratio,
        silence_ratio_valid=silence_ratio_valid,
        snr_estimate=snr_estimate,
        snr_valid=snr_valid,
        is_clean=is_clean,
        persona_match_score=persona_match_score,
        sisi_compatible=sisi_compatible,
        issues=issues,
        recommendations=recommendations
    )


def validate_directory(
    audio_dir: str,
    manifest_path: Optional[str] = None,
    max_workers: int = 4
) -> BatchValidationReport:
    """
    Validate all audio files in a directory.
    """
    audio_path = Path(audio_dir)
    
    # Load manifest if provided for metadata
    metadata_map = {}
    if manifest_path and Path(manifest_path).exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            for sample in manifest.get("samples", []):
                audio_file = sample.get("audio_path")
                if audio_file:
                    metadata_map[audio_file] = sample
    
    # Find all audio files
    audio_files = list(audio_path.glob("**/*.wav"))
    audio_files.extend(audio_path.glob("**/*.flac"))
    audio_files.extend(audio_path.glob("**/*.mp3"))
    
    logger.info(f"Found {len(audio_files)} audio files to validate")
    
    # Validate in parallel
    results = []
    
    def validate_file(file_path):
        metadata = metadata_map.get(file_path.name, None)
        return validate_sample(str(file_path), metadata)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(validate_file, audio_files))
    
    # Aggregate results
    valid_count = sum(1 for r in results if r.valid)
    invalid_count = len(results) - valid_count
    sisi_compatible_count = sum(1 for r in results if r.sisi_compatible)
    
    total_duration = sum(r.duration for r in results)
    total_duration_hours = total_duration / 3600
    
    format_issues = sum(1 for r in results if not r.format_valid or not r.sample_rate_valid)
    duration_issues = sum(1 for r in results if not r.duration_valid)
    quality_issues = sum(1 for r in results if not r.is_clean)
    
    # Calculate average quality score
    quality_scores = []
    for r in results:
        score = 0.5
        if r.is_clean:
            score += 0.3
        if r.duration_optimal:
            score += 0.1
        score += r.persona_match_score * 0.1
        quality_scores.append(score)
    
    average_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Generate summary
    summary = f"""
Validation Summary:
- Total files: {len(results)}
- Valid: {valid_count} ({valid_count/len(results)*100:.1f}%)
- Invalid: {invalid_count}
- Sisi Lola Compatible: {sisi_compatible_count}
- Total Duration: {total_duration_hours:.2f} hours
- Average Quality Score: {average_quality_score:.2f}

Issues Breakdown:
- Format issues: {format_issues}
- Duration issues: {duration_issues}
- Quality issues: {quality_issues}
    """.strip()
    
    # Generate recommendations
    report_recommendations = []
    if format_issues > 0:
        report_recommendations.append(f"Convert {format_issues} files to 22050Hz WAV format")
    if duration_issues > 0:
        report_recommendations.append(f"Fix duration for {duration_issues} files (trim or split)")
    if quality_issues > 0:
        report_recommendations.append(f"Improve quality of {quality_issues} files (denoise, normalize)")
    if sisi_compatible_count < len(results) * 0.5:
        report_recommendations.append("Consider adding more female Nigerian voice samples")
    
    return BatchValidationReport(
        total_files=len(results),
        valid_count=valid_count,
        invalid_count=invalid_count,
        sisi_compatible_count=sisi_compatible_count,
        total_duration_hours=total_duration_hours,
        average_quality_score=average_quality_score,
        format_issues=format_issues,
        duration_issues=duration_issues,
        quality_issues=quality_issues,
        results=results,
        summary=summary,
        recommendations=report_recommendations
    )


def validate_manifest(manifest_path: str) -> BatchValidationReport:
    """
    Validate a curated manifest and its audio files.
    """
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Get base directory from manifest location
    base_dir = Path(manifest_path).parent
    
    # Validate each sample in manifest
    results = []
    
    for sample in manifest.get("samples", []):
        audio_path = sample.get("audio_path", "")
        
        # Try different path resolutions
        full_path = None
        if Path(audio_path).is_absolute() and Path(audio_path).exists():
            full_path = audio_path
        elif (base_dir / audio_path).exists():
            full_path = str(base_dir / audio_path)
        else:
            # Create a failed result for missing file
            results.append(ValidationResult(
                file_path=audio_path,
                valid=False,
                sample_rate=0,
                sample_rate_valid=False,
                channels=0,
                channels_valid=False,
                format="unknown",
                format_valid=False,
                duration=0,
                duration_valid=False,
                duration_optimal=False,
                signal_power=0,
                signal_power_valid=False,
                silence_ratio=1.0,
                silence_ratio_valid=False,
                snr_estimate=0,
                snr_valid=False,
                is_clean=False,
                persona_match_score=0,
                sisi_compatible=False,
                issues=["Audio file not found"],
                recommendations=["Check file path in manifest"]
            ))
            continue
        
        result = validate_sample(full_path, metadata=sample)
        results.append(result)
    
    # Aggregate (same as validate_directory)
    valid_count = sum(1 for r in results if r.valid)
    invalid_count = len(results) - valid_count
    sisi_compatible_count = sum(1 for r in results if r.sisi_compatible)
    
    total_duration = sum(r.duration for r in results)
    total_duration_hours = total_duration / 3600
    
    format_issues = sum(1 for r in results if not r.format_valid or not r.sample_rate_valid)
    duration_issues = sum(1 for r in results if not r.duration_valid)
    quality_issues = sum(1 for r in results if not r.is_clean)
    
    quality_scores = [(0.5 + 0.3 * r.is_clean + 0.1 * r.duration_optimal + 0.1 * r.persona_match_score) 
                      for r in results]
    average_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    summary = f"""
Manifest Validation: {manifest_path}
- Dataset: {manifest.get('name', 'Unknown')}
- Language: {manifest.get('language', 'Unknown')}
- Total samples: {len(results)}
- Valid: {valid_count}
- Sisi Lola Compatible: {sisi_compatible_count}
- Duration: {total_duration_hours:.2f} hours
    """.strip()
    
    return BatchValidationReport(
        total_files=len(results),
        valid_count=valid_count,
        invalid_count=invalid_count,
        sisi_compatible_count=sisi_compatible_count,
        total_duration_hours=total_duration_hours,
        average_quality_score=average_quality_score,
        format_issues=format_issues,
        duration_issues=duration_issues,
        quality_issues=quality_issues,
        results=results,
        summary=summary,
        recommendations=[]
    )


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate curated audio samples for Sisi Lola")
    parser.add_argument("input", help="Directory or manifest file to validate")
    parser.add_argument("-o", "--output", help="Output JSON report file")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(args.input)
    
    if input_path.is_dir():
        report = validate_directory(str(input_path), max_workers=args.workers)
    elif input_path.suffix == ".json":
        report = validate_manifest(str(input_path))
    else:
        print(f"Error: Input must be a directory or JSON manifest file")
        sys.exit(1)
    
    # Print summary
    print("\n" + "=" * 60)
    print(report.summary)
    print("=" * 60)
    
    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations:
            print(f"  • {rec}")
    
    # Save report if output specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nReport saved to: {args.output}")
    
    # Exit code based on validity
    sys.exit(0 if report.valid_count == report.total_files else 1)
