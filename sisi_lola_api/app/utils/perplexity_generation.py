"""Direct Perplexity media generation helpers (image/video).

These functions try Perplexity's native generation endpoints first and surface a
simple `media_url` so the routers can stay provider-agnostic. If the endpoints
change, override via PERPLEXITY_IMAGE_ENDPOINT / PERPLEXITY_VIDEO_ENDPOINT.
"""
from __future__ import annotations

import os
from typing import Dict, Optional

import httpx


PERPLEXITY_IMAGE_ENDPOINT = os.getenv("PERPLEXITY_IMAGE_ENDPOINT", "https://api.perplexity.ai/images/generations")
PERPLEXITY_VIDEO_ENDPOINT = os.getenv("PERPLEXITY_VIDEO_ENDPOINT", "https://api.perplexity.ai/videos/generations")


class PerplexityCredentialsError(ValueError):
    pass


def _get_api_key() -> str:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise PerplexityCredentialsError("PERPLEXITY_API_KEY is not set. Add it to .env to enable Perplexity-first generation.")
    return api_key


def _extract_media_url(payload: Dict) -> Optional[str]:
    """Normalize common Perplexity media response shapes to a single URL."""
    if not isinstance(payload, dict):
        return None
    for key in ("media_url", "url"):
        if key in payload and isinstance(payload[key], str):
            return payload[key]
    data = payload.get("data")
    if isinstance(data, list) and data:
        candidate = data[0]
        if isinstance(candidate, dict):
            for key in ("media_url", "url"):
                if key in candidate and isinstance(candidate[key], str):
                    return candidate[key]
    return None


async def generate_perplexity_image(prompt: str, aspect_ratio: str = "16:9", model: Optional[str] = None) -> Dict:
    """Generate an image via Perplexity's media endpoint, returning the raw payload plus normalized URL."""
    api_key = _get_api_key()
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "model": model or os.getenv("PERPLEXITY_IMAGE_MODEL", "sonar"),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(PERPLEXITY_IMAGE_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    media_url = _extract_media_url(data)
    if media_url:
        data["media_url"] = media_url
    return data


async def generate_perplexity_video(prompt: str, duration: int = 5, aspect_ratio: str = "16:9", model: Optional[str] = None) -> Dict:
    """Generate a video via Perplexity's media endpoint, returning the raw payload plus normalized URL."""
    api_key = _get_api_key()
    payload = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "model": model or os.getenv("PERPLEXITY_VIDEO_MODEL", "sonar"),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(PERPLEXITY_VIDEO_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    media_url = _extract_media_url(data)
    if media_url:
        data["media_url"] = media_url
    return data
