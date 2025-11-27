"""
TTS Metadata Aggregator for Sisi Lola XTTS Training

Technical Explanation:
- Aggregates recorded voice samples from multiple sources
- Matches audio files with transcription scripts
- Validates audio quality (duration, sample rate, no silence/clipping)
- Produces metadata.csv in XTTS format: filename|text|speaker_id|language

Layman Explanation:
This creates a "training manual" for cloning Sisi Lola's voice. Each line
tells the AI: "When you hear this audio file, this is what was said."
We check that recordings are good quality (not too quiet, no glitches).

Usage:
    python build_tts_metadata.py --voice-dir ../../04_AUDIO_CORE/01_Voice_Samples --output data/processed/tts_metadata.csv
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import List, Dict, Optional
import sys

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

sys.path.append((ROOT / "preprocessing").as_posix())
from normalize_text import normalize_text

# Optional audio validation
try:
    import librosa
    import soundfile as sf
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  librosa/soundfile not installed - skipping audio validation")


def extract_script_text(script_file: Path) -> str:
    """
    Extract clean script text from SCRIPT_*.txt files.
    
    Technical: Parses markdown-style scripts, extracts ## SCRIPT: section.
    Layman: Reads the written version of what the voice actor should say.
    """
    with open(script_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract script section
    if "## SCRIPT:" in content:
        script = content.split("## SCRIPT:")[1].split("---")[0]
        script = script.strip()
        # Remove extra whitespace
        script = re.sub(r"\s+", " ", script)
        return normalize_text(script)
    
    return ""


def validate_audio(audio_path: Path) -> Optional[Dict]:
    """
    Validate audio quality for TTS training.
    
    Technical: Checks duration (3-30s), RMS energy (no silence/clipping), sample rate.
    Layman: Makes sure the recording is clear and the right length.
    """
    if not AUDIO_AVAILABLE:
        return {"duration_sec": 0, "sample_rate": 0, "rms": 0, "valid": True}
    
    try:
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        duration = len(audio) / sr
        rms = np.sqrt(np.mean(audio**2))
        max_amp = np.max(np.abs(audio))
        
        # Quality checks
        valid = True
        issues = []
        
        if duration < 3.0:
            valid = False
            issues.append("too_short")
        if duration > 30.0:
            valid = False
            issues.append("too_long")
        if rms < 0.01:
            valid = False
            issues.append("too_quiet")
        if max_amp > 0.99:
            valid = False
            issues.append("clipping")
        
        return {
            "duration_sec": duration,
            "sample_rate": sr,
            "rms": rms,
            "max_amplitude": max_amp,
            "valid": valid,
            "issues": issues
        }
    except Exception as e:
        print(f"  ✗ Failed to validate {audio_path.name}: {e}")
        return None


def detect_language_from_filename(filename: str) -> str:
    """
    Detect language from filename patterns.
    
    Technical: Uses keyword matching (pidgin, yoruba, italian, etc.).
    Layman: Guesses the language from the file name.
    """
    name_lower = filename.lower()
    
    if "pidgin" in name_lower:
        return "pcm"
    elif "yoruba" in name_lower or "yo_" in name_lower:
        return "yo"
    elif "italian" in name_lower:
        return "it"
    elif "swahili" in name_lower:
        return "sw"
    elif "hausa" in name_lower:
        return "ha"
    elif "igbo" in name_lower or "ibo" in name_lower:
        return "ig"
    elif "french" in name_lower:
        return "fr"
    else:
        return "en"  # Default


def build_tts_metadata(
    voice_dir: Path,
    output_csv: Path,
    speaker_id: str = "sisi_lola",
    validate: bool = True
) -> None:
    """
    Build TTS metadata.csv from voice recordings directory.
    
    Technical: Scans for .wav/.mp3, matches with SCRIPT_*.txt, validates quality.
    Layman: Creates the master list linking recordings to their text scripts.
    """
    entries = []
    
    # Find all audio files
    audio_files = list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3"))
    
    if not audio_files:
        print(f"⚠️  No audio files found in {voice_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files in {voice_dir}")
    
    for audio_file in audio_files:
        # Find corresponding script
        base_name = audio_file.stem
        
        # Try to find matching script file
        script_file = voice_dir / f"SCRIPT_{base_name}.txt"
        if not script_file.exists():
            # Try without prefix
            script_file = voice_dir / f"{base_name}.txt"
        
        if script_file.exists():
            text = extract_script_text(script_file)
        else:
            print(f"  ⚠️  No script found for {audio_file.name}, skipping")
            continue
        
        if not text:
            print(f"  ⚠️  Empty script for {audio_file.name}, skipping")
            continue
        
        # Validate audio
        if validate:
            quality = validate_audio(audio_file)
            if quality and not quality["valid"]:
                print(f"  ✗ {audio_file.name}: quality issues: {quality['issues']}")
                continue
        
        # Detect language
        language = detect_language_from_filename(audio_file.name)
        
        entries.append({
            "filename": audio_file.name,
            "text": text,
            "speaker_id": speaker_id,
            "language": language
        })
        
        print(f"  ✓ {audio_file.name} [{language}]: {len(text)} chars")
    
    # Write metadata.csv
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(["filename", "text", "speaker_id", "language"])
        
        for entry in entries:
            writer.writerow([
                entry["filename"],
                entry["text"],
                entry["speaker_id"],
                entry["language"]
            ])
    
    print(f"\n✅ Wrote {len(entries)} entries to {output_csv}")
    
    # Summary
    from collections import Counter
    lang_counts = Counter([e["language"] for e in entries])
    print("\n📊 Summary by language:")
    for lang, count in lang_counts.most_common():
        print(f"  {lang}: {count} samples")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build TTS metadata")
    parser.add_argument(
        "--voice-dir",
        type=str,
        required=True,
        help="Directory containing voice recordings and scripts"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/tts_metadata.csv",
        help="Output metadata.csv path"
    )
    parser.add_argument(
        "--speaker-id",
        type=str,
        default="sisi_lola",
        help="Speaker identifier"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip audio quality validation"
    )
    args = parser.parse_args()
    
    build_tts_metadata(
        Path(args.voice_dir),
        Path(args.output),
        speaker_id=args.speaker_id,
        validate=not args.no_validate
    )
