#!/usr/bin/env python3
"""
=============================================================================
🎙️ SISI LOLA VOICE SELECTOR & RVC TRAINER
=============================================================================
Finds the best voice samples and prepares them for Replicate RVC cloning.

Criteria for "engaging, storytelling, sexy" voice:
- Longer samples (more natural speech patterns)
- Consistent speaker (same voice throughout)
- Clear audio quality

Run: python -m sisi_lola_api.scripts.select_best_voices
=============================================================================
"""

import os
import wave
import shutil
import random
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_SAMPLES_ROOT = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_samples"
SELECTED_FOLDER = VOICE_SAMPLES_ROOT / "selected_best"
NIGERIAN_FEMALE = VOICE_SAMPLES_ROOT / "nigerian_english_female"

# Create selected folder
SELECTED_FOLDER.mkdir(parents=True, exist_ok=True)


def get_audio_duration(wav_path: Path) -> float:
    """Get duration of a WAV file in seconds"""
    try:
        with wave.open(str(wav_path), 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            return frames / float(rate)
    except:
        return 0


def analyze_speakers_fast(folder: Path) -> dict:
    """
    Analyze speakers by filename ONLY (Instant)
    Format: ngf_XXXXX_YYYYYYYYYYY.wav
    """
    speakers = defaultdict(list)
    files = list(folder.glob("*.wav"))
    
    print(f"   ⚡ Scanning {len(files)} files (Metadata mode)...")
    
    for wav_file in files:
        parts = wav_file.stem.split("_")
        if len(parts) >= 2:
            speaker_id = parts[1]
            speakers[speaker_id].append(wav_file)
            
    return speakers


def select_best_speaker_fast(speakers: dict) -> list:
    """
    Select best speaker based on file count, then verify duration for TOP candidates only.
    """
    # 1. Sort speakers by file count (descending)
    sorted_speakers = sorted(speakers.items(), key=lambda x: len(x[1]), reverse=True)
    
    top_candidates = []
    
    # 2. Only analyze the top 10 speakers deeply
    print("   🕵️ Analzying top 10 candidates deeply...")
    
    for speaker_id, file_paths in sorted_speakers[:10]:
        total_duration = 0
        valid_files = []
        
        # Check first 20 files for this speaker to estimate quality/length
        sample_size = min(len(file_paths), 20)
        
        for wav_path in file_paths[:sample_size]:
            try:
                # Only now do we open the file
                with wave.open(str(wav_path), 'rb') as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    duration = frames / float(rate)
                    total_duration += duration
                    
                    valid_files.append({
                        "path": wav_path,
                        "duration": duration,
                        "name": wav_path.name
                    })
            except:
                continue
        
        if valid_files:
            avg_duration = total_duration / len(valid_files)
            # Estimate total duration based on file count
            est_total_duration = avg_duration * len(file_paths)
            
            # Score: High file count + Good average length
            score = (len(file_paths) * 0.5) + (avg_duration * 20)
            
            top_candidates.append({
                "id": speaker_id,
                "samples": len(file_paths),
                "total_duration": round(est_total_duration, 1),
                "avg_duration": round(avg_duration, 2),
                "score": round(score, 2),
                # We need to process ALL files for the winner later, 
                # but for now store the raw paths
                "raw_files": file_paths 
            })
            
    # Sort by score
    top_candidates.sort(key=lambda x: x["score"], reverse=True)
    return top_candidates


def main():
    print("=" * 60)
    print("🎙️ SISI LOLA VOICE SELECTOR (TURBO MODE)")
    print("=" * 60)
    print("\n🎯 Looking for: Engaging, Storytelling, Sexy Nigerian Voice\n")
    
    # Analyze Nigerian English Female samples
    print("📊 Analyzing Nigerian English Female samples...")
    speakers = analyze_speakers_fast(NIGERIAN_FEMALE)
    
    print(f"   Found {len(speakers)} different speakers\n")
    
    # Get best speakers
    print("⭐ TOP 5 SPEAKERS (Best for Voice Cloning):")
    print("-" * 60)
    
    best_speakers = select_best_speaker_fast(speakers)[:5]
    
    for i, speaker in enumerate(best_speakers, 1):
        mins = speaker["total_duration"] / 60
        print(f"\n{i}. Speaker ID: {speaker['id']}")
        print(f"   📁 Samples: {speaker['samples']} files")
        print(f"   ⏱️ Est. Total: {mins:.1f} minutes")
        print(f"   📏 Avg length: {speaker['avg_duration']}s per clip")
        print(f"   ⭐ Score: {speaker['score']}")
    
    # Select top speaker
    if best_speakers:
        top_speaker = best_speakers[0]
        print("\n" + "=" * 60)
        print(f"🏆 SELECTED: Speaker {top_speaker['id']}")
        print("=" * 60)
        
        # Copy best samples to selected folder
        print(f"\n📦 Processing top 50 samples for selected_best/...")
        
        # Clear previous selections
        for f in SELECTED_FOLDER.glob("*.wav"):
            f.unlink()
        
        # Now we need to verify durations for ALL files of the winner to pick longest
        all_files_analyzed = []
        for fpath in top_speaker["raw_files"]:
             try:
                with wave.open(str(fpath), 'rb') as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    dur = frames / float(rate)
                    all_files_analyzed.append({"path": fpath, "name": fpath.name, "duration": dur})
             except:
                 pass
                 
        # Sort by duration
        sorted_samples = sorted(all_files_analyzed, key=lambda x: x["duration"], reverse=True)
        
        # Copy top 50 samples
        copied = 0
        total_copied_duration = 0
        for sample in sorted_samples[:50]:
            src = sample["path"]
            dst = SELECTED_FOLDER / sample["name"]
            shutil.copy2(src, dst)
            copied += 1
            total_copied_duration += sample["duration"]
        
        print(f"   ✅ Copied {copied} files")
        print(f"   ⏱️ Total duration: {total_copied_duration/60:.1f} minutes")
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 READY FOR REPLICATE RVC TRAINING!")
        print("=" * 60)
        print(f"""
📁 Selected samples: {SELECTED_FOLDER}
🎵 Files: {copied}
⏱️ Duration: {total_copied_duration/60:.1f} minutes

NEXT STEPS:
1. Review a few samples: Open folder and listen
2. Run the RVC training script:
   python -m sisi_lola_api.scripts.train_voice_rvc

OR manually upload to:
   https://replicate.com/zsxkib/realistic-voice-cloning
""")
        
        # Save speaker info
        info_file = SELECTED_FOLDER / "speaker_info.txt"
        with open(info_file, "w") as f:
            f.write(f"Speaker ID: {top_speaker['id']}\n")
            f.write(f"Total samples: {top_speaker['samples']}\n")
            f.write(f"Selected samples: {copied}\n")
            f.write(f"Total duration: {total_copied_duration/60:.1f} minutes\n")
            f.write(f"\nSource: Nigerian English Female (OpenSLR Dataset)\n")
        
        print(f"💾 Speaker info saved to: {info_file}")
        
    else:
        print("\n❌ No suitable speakers found!")
    
    print("\n" + "=" * 60)
    print("✅ SELECTION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
