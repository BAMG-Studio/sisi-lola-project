"""
Audio Quality Analysis for Voice Training Data

Technical Explanation:
- Validates audio files for training suitability
- Checks: sample rate, bit depth, duration, noise levels, clipping
- Generates histograms and statistical reports

Layman Explanation:
This checks if voice recordings are "clean enough" to train AI on:
- Not too loud (no distortion)
- Not too quiet (no background noise drowning voice)
- Right length (not too short, not too long)
- Good clarity (proper microphone quality)

Usage:
    python audio_quality_report.py --voice-dir ../04_AUDIO_CORE/01_Voice_Samples --output reports/audio_quality.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

try:
    import librosa
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False


def analyze_audio_file(audio_path: Path) -> Dict | None:
    """
    Analyze single audio file for quality metrics.
    
    Technical: Extracts sample rate, duration, RMS energy, max amplitude, zero-crossing rate.
    Layman: Checks if audio is loud enough, clear enough, and not distorted.
    """
    if not AUDIO_LIBS_AVAILABLE:
        return None
    
    try:
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        
        # Basic stats
        duration = len(y) / sr
        rms = librosa.feature.rms(y=y)[0].mean()
        max_amp = np.max(np.abs(y))
        zcr = librosa.feature.zero_crossing_rate(y)[0].mean()
        
        # Detect issues
        issues = []
        if duration < 3.0:
            issues.append("too_short")
        elif duration > 30.0:
            issues.append("too_long")
        
        if rms < 0.01:
            issues.append("too_quiet")
        elif rms > 0.95:
            issues.append("too_loud")
        
        if max_amp >= 0.99:
            issues.append("clipping")
        
        # Estimate SNR (very rough approximation)
        # Lower 10% energy vs upper 90%
        sorted_abs = np.sort(np.abs(y))
        noise_floor = np.mean(sorted_abs[:len(sorted_abs)//10])
        signal_level = np.mean(sorted_abs[9*len(sorted_abs)//10:])
        snr_estimate = 20 * np.log10(signal_level / (noise_floor + 1e-8))
        
        if snr_estimate < 10:
            issues.append("low_snr")
        
        return {
            "sample_rate": sr,
            "duration_sec": round(duration, 2),
            "rms_energy": round(float(rms), 4),
            "max_amplitude": round(float(max_amp), 4),
            "zero_crossing_rate": round(float(zcr), 4),
            "snr_estimate_db": round(float(snr_estimate), 1),
            "issues": issues,
            "status": "good" if not issues else "warning"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def analyze_audio_dataset(voice_dir: Path, file_extensions: List[str] = None) -> Dict:
    """
    Analyze all audio files in directory.
    
    Technical: Scans directory, processes each file, aggregates statistics.
    Layman: Checks all voice recordings in a folder and creates summary.
    """
    if file_extensions is None:
        file_extensions = [".wav", ".mp3", ".flac", ".ogg"]
    
    if not AUDIO_LIBS_AVAILABLE:
        return {
            "error": "librosa/soundfile not installed. Run: pip install librosa soundfile",
            "analyzed_files": 0
        }
    
    audio_files = []
    for ext in file_extensions:
        audio_files.extend(voice_dir.rglob(f"*{ext}"))
    
    print(f"Found {len(audio_files)} audio files in {voice_dir}")
    
    results = {
        "total_files": len(audio_files),
        "analyzed_files": 0,
        "good_files": 0,
        "warning_files": 0,
        "error_files": 0,
        "total_duration_hours": 0.0,
        "sample_rate_distribution": defaultdict(int),
        "duration_bins": defaultdict(int),  # <3s, 3-10s, 10-30s, >30s
        "rms_distribution": [],
        "issues_summary": defaultdict(int),
        "file_details": {}
    }
    
    for audio_path in audio_files:
        print(f"Analyzing {audio_path.name}...", end="\r")
        
        metrics = analyze_audio_file(audio_path)
        if metrics is None:
            continue
        
        results["analyzed_files"] += 1
        results["file_details"][str(audio_path)] = metrics
        
        if metrics.get("error"):
            results["error_files"] += 1
            continue
        
        # Aggregate stats
        if metrics["status"] == "good":
            results["good_files"] += 1
        else:
            results["warning_files"] += 1
        
        results["total_duration_hours"] += metrics["duration_sec"] / 3600
        results["sample_rate_distribution"][metrics["sample_rate"]] += 1
        results["rms_distribution"].append(metrics["rms_energy"])
        
        # Duration bins
        dur = metrics["duration_sec"]
        if dur < 3:
            results["duration_bins"]["<3s"] += 1
        elif dur < 10:
            results["duration_bins"]["3-10s"] += 1
        elif dur < 30:
            results["duration_bins"]["10-30s"] += 1
        else:
            results["duration_bins"][">30s"] += 1
        
        # Issues
        for issue in metrics["issues"]:
            results["issues_summary"][issue] += 1
    
    # Convert defaultdicts to regular dicts
    results["sample_rate_distribution"] = dict(results["sample_rate_distribution"])
    results["duration_bins"] = dict(results["duration_bins"])
    results["issues_summary"] = dict(results["issues_summary"])
    
    # Calculate RMS statistics
    if results["rms_distribution"]:
        rms_arr = np.array(results["rms_distribution"])
        results["rms_stats"] = {
            "mean": round(float(np.mean(rms_arr)), 4),
            "median": round(float(np.median(rms_arr)), 4),
            "std": round(float(np.std(rms_arr)), 4),
            "min": round(float(np.min(rms_arr)), 4),
            "max": round(float(np.max(rms_arr)), 4)
        }
        del results["rms_distribution"]  # Remove raw values to save space
    
    return results


def generate_recommendations(report: Dict) -> List[str]:
    """
    Generate recommendations based on audio quality analysis.
    
    Technical: Rule-based heuristics for common audio issues.
    Layman: Tells you how to fix bad recordings.
    """
    recommendations = []
    
    total = report.get("analyzed_files", 0)
    good = report.get("good_files", 0)
    issues = report.get("issues_summary", {})
    
    if total == 0:
        recommendations.append("⚠️  No audio files analyzed. Check directory path.")
        return recommendations
    
    good_ratio = good / total
    if good_ratio < 0.7:
        recommendations.append(
            f"⚠️  Only {good_ratio*100:.0f}% of files are good quality. "
            f"Aim for 90%+ before training."
        )
    
    # Specific issues
    if issues.get("too_quiet", 0) > total * 0.1:
        recommendations.append(
            f"🔇 {issues['too_quiet']} files are too quiet. "
            f"Re-record with mic closer or increase gain."
        )
    
    if issues.get("clipping", 0) > 0:
        recommendations.append(
            f"🔴 {issues['clipping']} files have clipping (distortion). "
            f"Reduce input gain and re-record."
        )
    
    if issues.get("low_snr", 0) > total * 0.2:
        recommendations.append(
            f"📢 {issues['low_snr']} files have low signal-to-noise ratio. "
            f"Record in quieter room or use better microphone."
        )
    
    if issues.get("too_short", 0) > 0:
        recommendations.append(
            f"⏱️  {issues['too_short']} files are <3 seconds. "
            f"XTTS needs 3-30s samples. Trim or re-record."
        )
    
    # Sample rate consistency
    sr_dist = report.get("sample_rate_distribution", {})
    if len(sr_dist) > 1:
        most_common_sr = max(sr_dist, key=sr_dist.get)
        recommendations.append(
            f"🎚️  Mixed sample rates detected. Standardize to {most_common_sr} Hz "
            f"for consistent training."
        )
    
    if not recommendations:
        recommendations.append("✅ Audio quality looks excellent! Ready for voice cloning.")
    
    return recommendations


def generate_report(voice_dir: Path, output_json: Path) -> None:
    """
    Generate comprehensive audio quality report.
    
    Technical: Aggregates all metrics, writes JSON report.
    Layman: Creates a full assessment of voice recording quality.
    """
    print(f"Analyzing audio files in {voice_dir}...")
    
    report = analyze_audio_dataset(voice_dir)
    report["recommendations"] = generate_recommendations(report)
    
    # Save report (exclude file_details if too large)
    if len(report.get("file_details", {})) > 100:
        print("⚠️  Many files detected. Saving summary only (not individual file details).")
        report["file_details_note"] = "Details excluded (>100 files). Rerun with smaller dataset for full details."
        del report["file_details"]
    
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Report saved to {output_json}")
    
    # Print summary
    print("\n" + "="*60)
    print("🎤 AUDIO QUALITY REPORT")
    print("="*60)
    
    print(f"\n📊 Overview:")
    print(f"  Total files: {report.get('total_files', 0)}")
    print(f"  Analyzed: {report.get('analyzed_files', 0)}")
    print(f"  Good quality: {report.get('good_files', 0)} ({report.get('good_files', 0)/max(report.get('analyzed_files', 1), 1)*100:.0f}%)")
    print(f"  With warnings: {report.get('warning_files', 0)}")
    print(f"  Errors: {report.get('error_files', 0)}")
    print(f"  Total duration: {report.get('total_duration_hours', 0):.2f} hours")
    
    if "rms_stats" in report:
        print(f"\n🔊 RMS Energy Stats:")
        print(f"  Mean: {report['rms_stats']['mean']}")
        print(f"  Median: {report['rms_stats']['median']}")
        print(f"  Range: {report['rms_stats']['min']} - {report['rms_stats']['max']}")
    
    if "duration_bins" in report:
        print(f"\n⏱️  Duration Distribution:")
        for bin_label, count in report["duration_bins"].items():
            print(f"  {bin_label:8} {count:>4} files")
    
    if "issues_summary" in report and report["issues_summary"]:
        print(f"\n⚠️  Issues Found:")
        for issue, count in report["issues_summary"].items():
            print(f"  {issue:15} {count:>4} files")
    
    print("\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze audio quality for voice training")
    parser.add_argument(
        "--voice-dir",
        type=str,
        required=True,
        help="Directory containing voice recordings"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/reports/audio_quality.json",
        help="Output JSON report path"
    )
    args = parser.parse_args()
    
    generate_report(Path(args.voice_dir), Path(args.output))
