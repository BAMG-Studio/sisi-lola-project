"""
Unit tests for prepare_video_dataset.py
- Test frame extraction
- Test audio extraction
- Test output directory creation
"""
import os
import tempfile
from pathlib import Path
import pytest
import shutil

from preprocessing.prepare_video_dataset import process_video

@pytest.fixture
def dummy_video(tmp_path):
    # Create a short dummy video using OpenCV
    import cv2
    height, width = 64, 64
    out_path = tmp_path / "dummy.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(out_path), fourcc, 25.0, (width, height))
    for i in range(25):
        frame = (255 * (i % 2) * np.ones((height, width, 3), dtype=np.uint8))
        out.write(frame)
    out.release()
    return out_path


def test_process_video_creates_frames_and_audio(tmp_path, dummy_video):
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    process_video(dummy_video, output_dir, frame_rate=5, duration=1)
    # Check frames
    frame_dir = output_dir / f"{dummy_video.stem}_frames"
    assert frame_dir.exists()
    frames = list(frame_dir.glob("*.jpg"))
    assert len(frames) > 0
    # Check audio
    audio_file = output_dir / f"{dummy_video.stem}.wav"
    assert audio_file.exists()


def test_process_video_handles_nonexistent_file(tmp_path):
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    fake_video = tmp_path / "fake.mp4"
    # Should not raise error
    try:
        process_video(fake_video, output_dir)
    except Exception:
        pytest.fail("process_video should handle nonexistent file gracefully")
