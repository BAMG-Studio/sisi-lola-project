"""Mothers in Diaspora - Router

Small, CPU-only routing layer.

Phase 1 goal: deterministically classify inbound WhatsApp messages into a few
buckets so the webhook can hand off work to the right downstream service later.

This module is intentionally dependency-light so it can be imported anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RouteDecision:
    kind: str  # "text" | "voice" | "media" | "empty"
    intent: str  # e.g. "legal_query" | "translation" | "support" | "general"
    language: str  # best-effort: "en" | "yo" | "ig" | "ha" | "pcm" | "unknown"


def _cheap_language_guess(text: str) -> str:
    # Minimal heuristic (Phase 1). Replace with fastText/CLD3/Whisper later.
    lowered = text.lower()

    # Nigerian Pidgin / common markers
    pidgin_markers = (
        "wetin",
        "weting",  # common misspelling
        "abi",
        "abeg",
        "na so",
        "wahala",
        "dey",
        "una",
        "naija",
        "wey",
        "no be",
        "sha",
        "sabi",
        "jare",
    )
    if any(tok in lowered for tok in pidgin_markers):
        return "pcm"

    # Yoruba markers (very rough)
    if any(tok in lowered for tok in ("jẹ", "ṣ", "ọba", "ẹ", "ọwọ")):
        return "yo"

    # Igbo markers (very rough)
    if any(tok in lowered for tok in ("anyị", "kpọ", "ụlọ", "n'ụzọ")):
        return "ig"

    # Hausa markers (very rough)
    if any(tok in lowered for tok in ("ina", "yaya", "haka", "na gode")):
        return "ha"

    return "en" if lowered.strip() else "unknown"


def _cheap_intent_guess(text: str) -> str:
    lowered = text.lower().strip()
    if not lowered:
        return "general"

    voice_request_markers = (
        "voice note",
        "voicenote",
        "send voice",
        "send audio",
        "can you talk",
        "can u talk",
        "you fit talk",
        "fit talk",
        "can you speak",
        "talk to me",
        "speak to me",
        "call me",
    )
    if any(m in lowered for m in voice_request_markers):
        return "voice_reply_request"

    legal_markers = (
        "visa",
        "uscis",
        "green card",
        "i-130",
        "i-485",
        "asylum",
        "work permit",
        "ead",
        "rfe",
        "immigration",
    )
    if any(m in lowered for m in legal_markers):
        return "legal_query"

    support_markers = (
        "lonely",
        "homesick",
        "tired",
        "depressed",
        "overwhelmed",
        "stressed",
        "help me",
    )
    if any(m in lowered for m in support_markers):
        return "emotional_support"

    translation_markers = ("translate", "meaning", "what does", "say this in")
    if any(m in lowered for m in translation_markers):
        return "translation"

    return "general"


def route_incoming_message(
    *,
    from_number: str,
    to_number: str,
    body: str,
    num_media: int,
    media_url_0: Optional[str],
    media_content_type_0: Optional[str],
) -> RouteDecision:
    if num_media and media_url_0:
        ct = (media_content_type_0 or "").lower()
        # Twilio voice notes arrive as audio/* (often audio/ogg)
        if ct.startswith("audio/"):
            return RouteDecision(
                kind="voice",
                intent="translation" if not body.strip() else _cheap_intent_guess(body),
                language="unknown",
            )
        return RouteDecision(kind="media", intent="general", language="unknown")

    if body and body.strip():
        lang = _cheap_language_guess(body)
        intent = _cheap_intent_guess(body)
        return RouteDecision(kind="text", intent=intent, language=lang)

    return RouteDecision(kind="empty", intent="general", language="unknown")
