"""Lightweight HeyGen client helpers for avatar video generation."""
from __future__ import annotations

import asyncio
import os
import time
from typing import Dict, Optional

import httpx

HEYGEN_API_BASE = os.getenv("HEYGEN_API_BASE", "https://api.heygen.com")
_API_KEY = os.getenv("HEYGEN_API_KEY")
DEFAULT_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID")
DEFAULT_VOICE_ID = os.getenv("HEYGEN_VOICE_ID")
STATUS_ENDPOINT = os.getenv("HEYGEN_STATUS_ENDPOINT", f"{HEYGEN_API_BASE}/v1/video_status.get")
DEFAULT_TEST_MODE = os.getenv("HEYGEN_TEST_MODE", "true").lower() in ("1", "true", "yes", "on")
DEFAULT_WIDTH = int(os.getenv("HEYGEN_WIDTH", "1280"))
DEFAULT_HEIGHT = int(os.getenv("HEYGEN_HEIGHT", "720"))


def _headers() -> Dict[str, str]:
    if not _API_KEY:
        raise ValueError("HEYGEN_API_KEY is not set. Add it to .env to enable HeyGen video generation.")
    return {"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"}


async def _fetch_fallback_voice_id() -> str:
    """Pick the first available voice as a fallback when no valid voice_id is supplied."""
    endpoint = f"{HEYGEN_API_BASE}/v2/voices"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(endpoint, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
    voices = (data.get("data") or {}).get("voices") or []
    if not voices:
        raise RuntimeError("No HeyGen voices available; set HEYGEN_VOICE_ID to a valid voice.")
    return voices[0]["voice_id"]


def _dimension_for_ratio(aspect_ratio: str) -> Dict[str, int]:
    """
    Derive a safe width/height pair that respects the requested aspect ratio
    while staying within plan-friendly dimensions (defaults to 1280px on the long edge).
    """
    try:
        w_ratio, h_ratio = aspect_ratio.split(":")
        w_ratio = float(w_ratio)
        h_ratio = float(h_ratio)
    except Exception:
        w_ratio, h_ratio = 16.0, 9.0

    long_edge = max(DEFAULT_WIDTH, DEFAULT_HEIGHT)
    if w_ratio >= h_ratio:
        width = long_edge
        height = int(long_edge * h_ratio / w_ratio)
    else:
        height = long_edge
        width = int(long_edge * w_ratio / h_ratio)

    return {"width": int(width), "height": int(height)}


async def start_heygen_video(
    script: str,
    aspect_ratio: str = "16:9",
    avatar_id: Optional[str] = None,
    voice_id: Optional[str] = None,
    caption: bool = False,
) -> Dict:
    """
    Kick off a HeyGen video generation job.

    Returns the raw response payload which should include a video_id.
    """
    avatar = avatar_id or DEFAULT_AVATAR_ID
    voice = voice_id or DEFAULT_VOICE_ID
    if not avatar:
        raise ValueError("HEYGEN_AVATAR_ID is missing. Provide avatar_id in the request or set HEYGEN_AVATAR_ID.")

    # If voice is missing or clearly a placeholder/comment, fall back to the first available voice
    if not voice or voice.strip().startswith("#"):
        voice = await _fetch_fallback_voice_id()

    payload = {
        "video_inputs": [
            {
                "avatar_id": avatar,
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice,
                },
            }
        ],
        "dimension": _dimension_for_ratio(aspect_ratio),
        "caption": caption,
        "test": DEFAULT_TEST_MODE,
    }

    endpoint = f"{HEYGEN_API_BASE}/v2/video/generate"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(endpoint, json=payload, headers=_headers())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        body = exc.response.text
        raise RuntimeError(f"HeyGen request failed [{exc.response.status_code}]: {body}") from exc


async def poll_heygen_video(
    video_id: str,
    poll_interval: float = 5.0,
    timeout_seconds: int = 480,
) -> Dict:
    """
    Poll HeyGen for a video job status until completion or failure.
    """
    endpoint = STATUS_ENDPOINT
    start = time.time()

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            response = await client.get(endpoint, params={"video_id": video_id}, headers=_headers())
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", {})
            status = data.get("status")
            if status is None and "state" in data:
                status = data.get("state")

            if status in {"completed", "ready"}:
                return payload
            if status in {"processing", "pending", "in_progress", "generating"}:
                pass
            if status in {"failed", "error"}:
                raise RuntimeError(f"HeyGen job failed: {data}")
            if isinstance(data.get("error"), str) and data["error"]:
                raise RuntimeError(f"HeyGen job error: {data['error']}")

            if time.time() - start > timeout_seconds:
                raise TimeoutError(f"HeyGen job timed out after {timeout_seconds}s (last status: {status})")

            await asyncio.sleep(poll_interval)
