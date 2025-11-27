"""
Code-switch detection wrapper using existing Sisi Lola utilities.

Loads text lines, detects language segments, and produces a segmented
CSV suitable for ASR/TTS preprocessing.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import List

# Add project root to import the language detector
ROOT = Path(__file__).resolve().parents[2]
SISI_API = ROOT / "sisi_lola_api"
sys.path.append(SISI_API.as_posix())

from app.utils.language_detector import SisiLolaLanguageDetector


def segment_file(input_txt: Path, output_csv: Path) -> None:
    det = SisiLolaLanguageDetector()
    with open(input_txt, "r", encoding="utf-8") as f_in, \
         open(output_csv, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["segment_text", "language", "confidence", "line_idx"]) 
        for i, line in enumerate(f_in):
            line = line.strip()
            if not line:
                continue
            segs = det.detect_code_switching(line)
            for seg in segs:
                writer.writerow([seg.text, seg.language, seg.confidence, i])


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Segment text file by code-switching")
    p.add_argument("input_txt", type=str)
    p.add_argument("output_csv", type=str)
    args = p.parse_args()
    segment_file(Path(args.input_txt), Path(args.output_csv))
