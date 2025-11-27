"""Fallback: create a simple mp4 from a single image when video providers fail.
Adds a light Ken Burns (slow zoom) to avoid a static feel. Supports URLs or local file paths.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Tuple

import httpx
import imageio.v3 as iio
import numpy as np
from PIL import Image


def _download_image(url: str) -> bytes:
    path_candidate = Path(url.replace("file://", ""))
    if path_candidate.exists():
        return path_candidate.read_bytes()
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


def _fps_for_duration(duration: int) -> int:
    # Keep files small but smooth enough
    return 12 if duration > 3 else 8


def _ensure_three_channels(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:  # grayscale -> RGB
        return np.stack([frame] * 3, axis=-1)
    if frame.shape[2] == 4:  # RGBA -> RGB
        return frame[:, :, :3]
    return frame


def _scale_to_aspect(frame: np.ndarray, aspect_ratio: str) -> np.ndarray:
    # Lightweight center-crop/letterbox if needed
    h, w, _ = frame.shape
    target = aspect_ratio.strip()
    if ":" in target:
        x, y = target.split(":")
        try:
            target_ratio = float(x) / float(y)
        except Exception:
            return frame
    else:
        return frame

    current_ratio = w / h
    if abs(current_ratio - target_ratio) < 0.01:
        return frame

    if current_ratio > target_ratio:
        # too wide -> crop width
        new_w = int(h * target_ratio)
        offset = (w - new_w) // 2
        return frame[:, offset:offset + new_w, :]
    else:
        # too tall -> crop height
        new_h = int(w / target_ratio)
        offset = (h - new_h) // 2
        return frame[offset:offset + new_h, :, :]


def _apply_slow_zoom(base_image: Image.Image, total_frames: int) -> list[np.ndarray]:
    frames = []
    w, h = base_image.size
    scales = np.linspace(1.0, 1.05, total_frames)  # subtle zoom-in
    for s in scales:
        new_w, new_h = int(w * s), int(h * s)
        resized = base_image.resize((new_w, new_h), Image.LANCZOS)
        # center-crop back to original size
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        cropped = resized.crop((left, top, left + w, top + h))
        frames.append(np.array(cropped))
    return frames


def create_stub_video(image_url: str, duration: int = 5, aspect_ratio: str = "16:9") -> Tuple[str, str]:
    """
    Create a simple mp4 with a subtle zoom motion from the provided image.
    Returns (video_path, temp_dir) so caller can clean up temp_dir if desired.
    """
    img_bytes = _download_image(image_url)
    tmpdir = tempfile.mkdtemp(prefix="stub_video_")
    tmp_dir = Path(tmpdir)
    img_path = tmp_dir / "frame.png"
    img_path.write_bytes(img_bytes)

    frame = iio.imread(img_path)
    frame = _ensure_three_channels(frame)
    frame = _scale_to_aspect(frame, aspect_ratio)

    base_image = Image.fromarray(frame)
    fps = _fps_for_duration(duration)
    total_frames = max(1, int(fps * duration))
    frames = _apply_slow_zoom(base_image, total_frames)

    out_path = tmp_dir / "stub.mp4"
    iio.imwrite(out_path, frames, fps=fps, codec="libx264", quality=6)

    return str(out_path), tmpdir
