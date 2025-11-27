"""
Prepare ASR (Whisper) training manifests from processed datasets.
Produces a TSV with: audio_path\ttext\tlanguage
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict


def build_manifest(pairs: List[Dict], out_tsv: Path) -> None:
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["audio_path", "text", "language"])  # header
        for p in pairs:
            w.writerow([p["audio_path"], p["text"], p.get("language", "unknown")])


if __name__ == "__main__":
    # Example usage placeholder
    sample = [
        {"audio_path": "data/processed/yo/audio/y_0001.wav", "text": "Ẹ káàrọ̀", "language": "yo"}
    ]
    build_manifest(sample, Path("data/processed/yo/asr_manifest.tsv"))
    print("Wrote sample ASR manifest")
