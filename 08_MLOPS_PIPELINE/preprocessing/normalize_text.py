"""
Text normalization utilities for multilingual African datasets.
- Unicode NFC normalization (preserve Yoruba diacritics)
- Whitespace cleanup
- Basic punctuation spacing
- Optional lowercasing
"""
from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List


def normalize_text(text: str, lowercase: bool = False) -> str:
    t = text.strip()
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([,;:!?])", r"\1", t)
    if lowercase:
        t = t.lower()
    return t


def batch_normalize(lines: Iterable[str], lowercase: bool = False) -> List[str]:
    return [normalize_text(x, lowercase=lowercase) for x in lines]


if __name__ == "__main__":
    tests = [
        "  Ẹ  káàrọ̀   gbogbo   yín !  ",
        "Báwo   ni?  Èmi  ni  Sisi  Lola .",
    ]
    for t in tests:
        print(t, "=>", normalize_text(t))
