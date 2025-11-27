"""
Prepare TTS (XTTS) metadata from recorded clips.
Produces metadata.csv with columns: filename|text|speaker_id|language

This complements 00_PROJECT_CORE/Scripts/voice_training/prepare_training_data.py
by aggregating curated text and linking to recorded audio.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict


def write_tts_metadata(entries: List[Dict], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="|")
        w.writerow(["filename", "text", "speaker_id", "language"])  # header
        for e in entries:
            w.writerow([e["filename"], e["text"], e.get("speaker_id", "sisi_lola"), e.get("language", "en")])


if __name__ == "__main__":
    sample = [
        {"filename": "lola_0001.wav", "text": "Hello, I'm Sisi Lola.", "speaker_id": "sisi_lola", "language": "en"}
    ]
    write_tts_metadata(sample, Path("data/processed/yo/tts/metadata.csv"))
    print("Wrote sample TTS metadata")
