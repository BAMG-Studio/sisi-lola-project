#!/usr/bin/env python3
"""
=============================================================================
🎙️ VOICE SAMPLE ANALYZER & SELECTOR
=============================================================================
Analyzes downloaded voice samples and helps select the best ones for cloning.

Run: python -m sisi_lola_api.scripts.analyze_voice_samples
=============================================================================
"""

import os
import wave
import json
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_SAMPLES_ROOT = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_samples"
SELECTED_BEST = VOICE_SAMPLES_ROOT / "selected_best"


def get_audio_info(wav_path: Path) -> dict:
    """Get basic info about a WAV file"""
    try:
        with wave.open(str(wav_path), 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate)
            channels = wav.getnchannels()
            return {
                "path": str(wav_path),
                "name": wav_path.name,
                "duration_seconds": round(duration, 2),
                "sample_rate": rate,
                "channels": channels,
                "size_kb": round(wav_path.stat().st_size / 1024, 1)
            }
    except Exception as e:
        return {"path": str(wav_path), "error": str(e)}


def analyze_folder(folder_path: Path) -> dict:
    """Analyze all WAV files in a folder"""
    wav_files = list(folder_path.glob("*.wav"))
    
    if not wav_files:
        return {
            "folder": folder_path.name,
            "count": 0,
            "total_duration_minutes": 0,
            "samples": []
        }
    
    samples = []
    total_duration = 0
    
    for wav_file in wav_files[:100]:  # Sample first 100 for analysis
        info = get_audio_info(wav_file)
        if "duration_seconds" in info:
            total_duration += info["duration_seconds"]
            samples.append(info)
    
    # Extrapolate for full folder
    if len(wav_files) > 100:
        avg_duration = total_duration / len(samples) if samples else 0
        estimated_total = avg_duration * len(wav_files)
    else:
        estimated_total = total_duration
    
    return {
        "folder": folder_path.name,
        "count": len(wav_files),
        "analyzed": len(samples),
        "total_duration_minutes": round(estimated_total / 60, 1),
        "avg_duration_seconds": round(total_duration / len(samples), 2) if samples else 0,
        "samples": samples[:10]  # Keep first 10 for reference
    }


def analyze_all_voice_samples():
    """Analyze all voice sample folders"""
    print("=" * 60)
    print("🎙️ VOICE SAMPLE ANALYZER")
    print("=" * 60)
    
    results = {}
    total_files = 0
    total_minutes = 0
    
    # Priority folders for Sisi Lola
    priority_folders = [
        "nigerian_english_female",
        "yoruba_female",
        "yorunglish_pidgin_female",
    ]
    
    print("\n📊 ANALYZING VOICE SAMPLES...\n")
    
    for folder in VOICE_SAMPLES_ROOT.iterdir():
        if folder.is_dir() and folder.name not in ["selected_best", "__pycache__"]:
            print(f"  Analyzing: {folder.name}...")
            analysis = analyze_folder(folder)
            results[folder.name] = analysis
            total_files += analysis["count"]
            total_minutes += analysis["total_duration_minutes"]
            
            is_priority = "⭐" if folder.name in priority_folders else "  "
            print(f"    {is_priority} {analysis['count']} files, ~{analysis['total_duration_minutes']} min")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"\n📁 Total folders analyzed: {len(results)}")
    print(f"🎵 Total audio files: {total_files}")
    print(f"⏱️ Total estimated duration: {round(total_minutes, 1)} minutes ({round(total_minutes/60, 1)} hours)")
    
    # Priority recommendations
    print("\n" + "=" * 60)
    print("⭐ RECOMMENDED FOR SISI LOLA VOICE")
    print("=" * 60)
    
    for folder_name in priority_folders:
        if folder_name in results:
            r = results[folder_name]
            print(f"\n📁 {folder_name}")
            print(f"   Files: {r['count']}")
            print(f"   Duration: ~{r['total_duration_minutes']} minutes")
            if r.get('avg_duration_seconds'):
                print(f"   Avg per file: {r['avg_duration_seconds']} seconds")
    
    # Voice cloning requirements
    print("\n" + "=" * 60)
    print("📋 VOICE CLONING REQUIREMENTS")
    print("=" * 60)
    print("""
For ElevenLabs Voice Cloning:
  - Minimum: 1 minute of audio
  - Recommended: 3-5 minutes
  - Requirements: 
    * Single speaker
    * Clear audio (no background noise)
    * Natural speaking voice
    * Consistent quality

For Replicate RVC (zsxkib/realistic-voice-cloning):
  - Minimum: 10-15 samples (30 seconds each)
  - Recommended: 50+ samples
  - Training time: ~5-10 minutes
""")
    
    # Save results
    results_file = VOICE_SAMPLES_ROOT / "analysis_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {results_file}")
    
    # Next steps
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    print("""
1. Listen to samples from nigerian_english_female/
   - Find a speaker you like (warm, friendly, clear)
   
2. Select 20-50 good samples from that speaker
   - Copy to selected_best/ folder
   
3. Run voice cloning:
   - ElevenLabs: https://elevenlabs.io/voice-lab
   - Replicate RVC: zsxkib/realistic-voice-cloning

4. Test the cloned voice with Yorunglish script!
""")
    
    print("=" * 60)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    analyze_all_voice_samples()
