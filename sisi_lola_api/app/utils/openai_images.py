"""Fallback utilities for generating images via OpenAI."""
from __future__ import annotations

import os
from typing import Dict

import httpx

OPENAI_IMAGE_ENDPOINT = "https://api.openai.com/v1/images/generations"
ASPECT_RATIO_TO_SIZE = {
    "1:1": "1024x1024",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
    "4:5": "1024x1792",  # Closest match for portrait
    "5:4": "1792x1024",  # Closest match for landscape
}


def _resolve_size(aspect_ratio: str) -> str:
    aspect_ratio = (aspect_ratio or "1:1").strip()
    return ASPECT_RATIO_TO_SIZE.get(aspect_ratio, "1024x1024")


def _get_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to .env to enable fallback generation.")
    return key


async def generate_openai_image(prompt: str, aspect_ratio: str = "1:1") -> Dict:
    """Generate an image via OpenAI's Images API."""
    api_key = _get_openai_key()
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": _resolve_size(aspect_ratio),
        "quality": "standard",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(OPENAI_IMAGE_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
