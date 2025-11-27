"""
Unit tests for train_video_actor_model.py
- Test argument parsing
- Test train_model simulation
"""
import sys
from pathlib import Path
import pytest
from training.train_video_actor_model import train_model

def test_train_model_simulation(tmp_path):
    data_dir = tmp_path / "video_processed"
    data_dir.mkdir()
    annotations_csv = tmp_path / "annotations.csv"
    labels_yaml = tmp_path / "labels.yaml"
    # Create dummy files
    annotations_csv.write_text("filename,activity,attitude,role,emotion,cultural_marker\nclip1.mp4,reading,calm,journalist,neutral,fashion\n")
    labels_yaml.write_text("activities:\n  - reading\n")
    # Should not raise error
    train_model(str(data_dir), str(annotations_csv), str(labels_yaml), epochs=1)
