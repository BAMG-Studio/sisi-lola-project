"""Accent-aware text rewriting for TTS.

Uses Perplexity to lightly localize text into a Nigerian (Yoruba-forward) cadence
while keeping meaning intact and TTS-friendly. Falls back to the original text
if the API is unavailable.
"""
from __future__ import annotations

import os
import httpx
from typing import List
from sisi_lola_api.app.config import SisiLolaDNA


async def rewrite_for_accent(text: str, accent: str = "nigerian-yoruba", languages: List[str] | None = None) -> str:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return text

    languages = languages or []
    accent_note = accent or "nigerian-yoruba"

    system_prompt = (
        f"You are a Nigerian Yoruba voice coach refining lines for {SisiLolaDNA.NAME}. "
        "Keep meaning intact, keep sentences concise, and make them flow naturally for TTS. "
        "Blend polished English with light Yoruba/Pidgin flavor (1–2 expressions max). "
        "Do not over-phoneticize. Avoid slang that could confuse speech synthesis. "
        "Maintain warmth, confidence, and Lagos energy."
    )

    user_content = (
        f"ACCENT: {accent_note}\n"
        f"LANGUAGES TO HINT: {', '.join(languages) if languages else 'English + Yoruba cadence'}\n"
        f"LINE:\n{text}\n"
        "Rewrite now for TTS with the requested accent. Return only the rewritten line."
    )

    payload = {
        "model": os.getenv("PERPLEXITY_AUDIO_MODEL", SisiLolaDNA.RESEARCH_MODEL),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.45
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            rewritten = data["choices"][0]["message"]["content"].strip()
            if rewritten.startswith('"') and rewritten.endswith('"'):
                rewritten = rewritten[1:-1]
            return rewritten
        except Exception as e:
            print(f"Perplexity accent rewrite failed: {e}")
            return text
