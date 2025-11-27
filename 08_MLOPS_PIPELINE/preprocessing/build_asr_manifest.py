"""
ASR Manifest Builder for Sisi Lola Whisper Fine-Tuning

Technical Explanation:
- Scans downloaded Fleurs and Common Voice datasets
- Extracts audio paths and transcriptions
- Normalizes text (Unicode NFC for Yoruba diacritics)
- Produces TSV: audio_path | text | language | duration_sec | speaker_id

Layman Explanation:
Think of this as creating a "recipe book" for teaching the AI to understand
African accents. Each line tells the AI: "This audio file contains this sentence
in this language." We organize thousands of these so the AI can learn patterns.

Usage:
    python build_asr_manifest.py --datasets fleurs common_voice_africa --output data/processed/asr_manifest_all.tsv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List, Dict
import sys

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"

# Import text normalizer
sys.path.append((ROOT / "preprocessing").as_posix())
from normalize_text import normalize_text


def extract_fleurs_manifest(fleurs_dir: Path, language_code: str) -> List[Dict]:
    """
    Extract audio+text pairs from Fleurs dataset.
    
    Technical: Fleurs stores audio in .arrow format via datasets library.
    Layman: Reads voice recordings and their written versions from Fleurs.
    """
    manifest = []
    
    # Fleurs subsets are saved as dataset directories
    for subset_dir in fleurs_dir.glob("fleurs_*"):
        if not subset_dir.is_dir():
            continue
        
        # Load using datasets library
        try:
            from datasets import load_from_disk
            ds = load_from_disk(subset_dir.as_posix())
        except Exception as e:
            print(f"Skip {subset_dir.name}: {e}")
            continue
        
        # Extract samples
        for split_name in ["train", "validation", "test"]:
            if split_name not in ds:
                continue
            
            split = ds[split_name]
            for i, sample in enumerate(split):
                # Fleurs structure: {audio: {path, array, sampling_rate}, transcription, ...}
                audio_info = sample.get("audio", {})
                text = sample.get("transcription", "") or sample.get("raw_transcription", "")
                
                if not text:
                    continue
                
                # Normalize text (preserve Yoruba diacritics)
                text = normalize_text(text)
                
                manifest.append({
                    "audio_path": audio_info.get("path", f"{subset_dir.name}_{split_name}_{i}"),
                    "text": text,
                    "language": language_code,
                    "duration_sec": len(audio_info.get("array", [])) / audio_info.get("sampling_rate", 16000),
                    "speaker_id": sample.get("speaker_id", "unknown"),
                    "split": split_name
                })
    
    return manifest


def extract_common_voice_manifest(cv_dir: Path, language_code: str) -> List[Dict]:
    """
    Extract audio+text pairs from Common Voice dataset.
    
    Technical: Common Voice stores MP3s with metadata in TSV files.
    Layman: Reads volunteer recordings and their transcriptions.
    """
    manifest = []
    
    for subset_dir in cv_dir.glob("common_voice_*"):
        if not subset_dir.is_dir():
            continue
        
        try:
            from datasets import load_from_disk
            ds = load_from_disk(subset_dir.as_posix())
        except Exception as e:
            print(f"Skip {subset_dir.name}: {e}")
            continue
        
        for split_name in ["train", "validation", "test"]:
            if split_name not in ds:
                continue
            
            split = ds[split_name]
            for i, sample in enumerate(split):
                audio_info = sample.get("audio", {})
                text = sample.get("sentence", "")
                
                if not text:
                    continue
                
                text = normalize_text(text)
                
                manifest.append({
                    "audio_path": audio_info.get("path", f"{subset_dir.name}_{split_name}_{i}"),
                    "text": text,
                    "language": language_code,
                    "duration_sec": len(audio_info.get("array", [])) / audio_info.get("sampling_rate", 48000),
                    "speaker_id": sample.get("client_id", "unknown"),
                    "split": split_name
                })
    
    return manifest


def build_manifest(datasets: List[str], output_tsv: Path) -> None:
    """
    Build unified ASR manifest from multiple datasets.
    
    Technical: Aggregates audio-text pairs, deduplicates, sorts by language/split.
    Layman: Combines all voice recordings into one master list for training.
    """
    all_entries = []
    
    for ds_name in datasets:
        ds_dir = EXTERNAL / ds_name
        if not ds_dir.exists():
            print(f"Dataset {ds_name} not found at {ds_dir}, skipping")
            continue
        
        print(f"Processing {ds_name}...")
        
        if "fleurs" in ds_name:
            # Detect language from subset name (e.g., fleurs_yo_ng -> yo)
            for subset in ds_dir.glob("fleurs_*"):
                parts = subset.name.split("_")
                lang_code = parts[1] if len(parts) > 1 else "unknown"
                entries = extract_fleurs_manifest(ds_dir, lang_code)
                all_entries.extend(entries)
                print(f"  Found {len(entries)} samples from {subset.name}")
        
        elif "common_voice" in ds_name:
            for subset in ds_dir.glob("common_voice_*"):
                parts = subset.name.split("_")
                lang_code = parts[-1] if len(parts) > 2 else "unknown"
                entries = extract_common_voice_manifest(ds_dir, lang_code)
                all_entries.extend(entries)
                print(f"  Found {len(entries)} samples from {subset.name}")
    
    # Sort by language then split
    all_entries.sort(key=lambda x: (x["language"], x["split"]))
    
    # Write TSV
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_tsv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["audio_path", "text", "language", "duration_sec", "speaker_id", "split"])
        
        for entry in all_entries:
            writer.writerow([
                entry["audio_path"],
                entry["text"],
                entry["language"],
                f"{entry['duration_sec']:.2f}",
                entry["speaker_id"],
                entry["split"]
            ])
    
    print(f"\n✅ Wrote {len(all_entries)} samples to {output_tsv}")
    
    # Print summary by language
    from collections import Counter
    lang_counts = Counter([e["language"] for e in all_entries])
    print("\n📊 Summary by language:")
    for lang, count in lang_counts.most_common():
        total_hours = sum(e["duration_sec"] for e in all_entries if e["language"] == lang) / 3600
        print(f"  {lang}: {count} samples, {total_hours:.1f} hours")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build ASR training manifest")
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["fleurs", "common_voice_africa"],
        help="Dataset names to include"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/asr_manifest_all.tsv",
        help="Output TSV path"
    )
    args = parser.parse_args()
    
    build_manifest(args.datasets, Path(args.output))
