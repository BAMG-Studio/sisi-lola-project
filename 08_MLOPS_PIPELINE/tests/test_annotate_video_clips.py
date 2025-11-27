"""
Unit tests for annotate_video_clips.py
- Test annotation structure
- Test CSV writing
"""
import tempfile
import csv
from pathlib import Path
from preprocessing.annotate_video_clips import LABELS, annotate_clip


def test_annotate_clip_structure(monkeypatch):
    # Simulate user input for annotation
    responses = iter(["dancing", "confident", "influencer", "happy", "greeting"])
    monkeypatch.setattr('builtins.input', lambda _: next(responses))
    dummy_path = Path("dummy.mp4")
    annotation = annotate_clip(dummy_path)
    assert annotation["filename"] == "dummy.mp4"
    for label in LABELS:
        assert label in annotation
        assert annotation[label] != ""


def test_csv_writing(tmp_path):
    # Simulate writing annotations to CSV
    csv_path = tmp_path / "annotations.csv"
    annotations = [
        {"filename": "clip1.mp4", "activity": "reading", "attitude": "calm", "role": "journalist", "emotion": "neutral", "cultural_marker": "fashion"},
        {"filename": "clip2.mp4", "activity": "dancing", "attitude": "energetic", "role": "influencer", "emotion": "happy", "cultural_marker": "greeting"}
    ]
    with open(csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["filename"] + LABELS)
        writer.writeheader()
        for ann in annotations:
            writer.writerow(ann)
    # Read back and check
    with open(csv_path, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["activity"] == "reading"
        assert rows[1]["attitude"] == "energetic"
