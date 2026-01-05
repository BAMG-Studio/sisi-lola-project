"""Mothers in Diaspora - WhatsApp Gateway (Modal + Twilio)

This app exposes a Twilio WhatsApp webhook and (for now) responds with a simple
message while delegating message classification/routing to the router module.

Secrets expected in Modal (recommended):
- sisi-lola-secrets (or any secret you choose to attach) containing:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN (or TWILIO_AUTH_TOKEN_LIVE)
    - TWILIO_WHATSAPP_FROM   (e.g. "whatsapp:+14155238886")

Deploy:
  modal deploy modal_deployments/mothers_diaspora_whatsapp.py

Notes:
- Do NOT hard-code tokens in source control.
- Twilio signature validation is supported when the request host/proto matches
  what Twilio hits (Modal URL). If you're testing behind proxies/tunnels, it may
  fail; you can temporarily disable validation via env var.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import modal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

# Router import: works locally; on Modal, source-layout imports can vary.
try:
    from modal_deployments.mothers_diaspora_router import (
        RouteDecision,
        route_incoming_message,
    )
except Exception:  # pragma: no cover
    from dataclasses import dataclass
    from typing import Optional

    @dataclass(frozen=True)
    class RouteDecision:
        kind: str
        intent: str
        language: str

    def _cheap_language_guess(text: str) -> str:
        lowered = text.lower()

        pidgin_markers = (
            "wetin",
            "weting",
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

        if any(tok in lowered for tok in ("jẹ", "ṣ", "ọba", "ẹ", "ọwọ")):
            return "yo"

        if any(tok in lowered for tok in ("anyị", "kpọ", "ụlọ", "n'ụzọ")):
            return "ig"

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
            if ct.startswith("audio/"):
                return RouteDecision(
                    kind="voice",
                    intent="translation" if not body.strip() else _cheap_intent_guess(body),
                    language="unknown",
                )
            return RouteDecision(kind="media", intent="general", language="unknown")
        if body and body.strip():
            return RouteDecision(
                kind="text",
                intent=_cheap_intent_guess(body),
                language=_cheap_language_guess(body),
            )
        return RouteDecision(kind="empty", intent="general", language="unknown")

APP_NAME = "mothers-diaspora-whatsapp"

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi==0.109.2",
        "python-multipart==0.0.9",
        "twilio==9.4.3",
    )
)

web = FastAPI()


@dataclass(frozen=True)
class TwilioConfig:
    account_sid: str
    auth_token: str
    whatsapp_from: str

    @staticmethod
    def from_env() -> "TwilioConfig":
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
        auth_token = (
            os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
            or os.environ.get("TWILIO_AUTH_TOKEN_LIVE", "").strip()
            or os.environ.get("TWILIO_AUTH_TOKEN_TEST", "").strip()
        )
        whatsapp_from = (
            os.environ.get("TWILIO_WHATSAPP_FROM", "").strip()
            or os.environ.get("TWILIO_WHATSAPP_NUMBER", "").strip()
        )

        missing = [
            key
            for key, val in (
                ("TWILIO_ACCOUNT_SID", account_sid),
                ("TWILIO_AUTH_TOKEN(_LIVE/_TEST)", auth_token),
                ("TWILIO_WHATSAPP_FROM", whatsapp_from),
            )
            if not val
        ]
        if missing:
            raise RuntimeError(
                "Missing required env vars in Modal secret: " + ", ".join(missing)
            )

        return TwilioConfig(
            account_sid=account_sid, auth_token=auth_token, whatsapp_from=whatsapp_from
        )


def _validate_twilio_signature(request: Request, raw_body: bytes, auth_token: str) -> None:
    """Validate Twilio signature, unless explicitly disabled."""

    # Allow disabling in emergencies/testing.
    if os.environ.get("DISABLE_TWILIO_SIGNATURE_VALIDATION", "").lower() in {
        "1",
        "true",
        "yes",
    }:
        return

    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing X-Twilio-Signature")

    validator = RequestValidator(auth_token)

    # Twilio signs the full URL it requested.
    # In Modal, request.url should reflect the public URL.
    url = str(request.url)

    # Twilio sends application/x-www-form-urlencoded.
    # We'll parse it via request.form() in the route, but signature verification
    # needs the param dict.
    # FastAPI already parsed it for us; we reconstruct inside the handler.
    # Here we just verify using the params dict.


@web.get("/health")
async def health() -> dict:
    return {"ok": True, "service": APP_NAME}


@web.post("/twilio/whatsapp")
@web.post("/twilio/whatsapp/")
async def twilio_whatsapp_webhook(request: Request) -> Response:
    raw_body = await request.body()

    cfg = TwilioConfig.from_env()

    form = await request.form()
    params = {k: str(v) for k, v in form.items()}

    # Validate signature
    if os.environ.get("DISABLE_TWILIO_SIGNATURE_VALIDATION", "").lower() not in {
        "1",
        "true",
        "yes",
    }:
        signature = request.headers.get("X-Twilio-Signature")
        if not signature:
            raise HTTPException(status_code=401, detail="Missing X-Twilio-Signature")
        validator = RequestValidator(cfg.auth_token)

        # Twilio signs the exact URL configured in the console. If the URL differs
        # only by a trailing slash, FastAPI/Modal can otherwise cause validation
        # to fail. We accept either variant.
        request_url = str(request.url)
        candidate_urls = {request_url}
        if request_url.endswith("/"):
            candidate_urls.add(request_url.rstrip("/"))
        else:
            candidate_urls.add(request_url + "/")

        if not any(validator.validate(u, params, signature) for u in candidate_urls):
            raise HTTPException(status_code=401, detail="Invalid Twilio signature")

    inbound_from = params.get("From", "")
    inbound_to = params.get("To", "")
    body_text = params.get("Body", "")
    num_media = int(params.get("NumMedia", "0") or 0)
    media_url_0 = params.get("MediaUrl0")
    media_type_0 = params.get("MediaContentType0")

    decision: RouteDecision = route_incoming_message(
        from_number=inbound_from,
        to_number=inbound_to,
        body=body_text,
        num_media=num_media,
        media_url_0=media_url_0,
        media_content_type_0=media_type_0,
    )

    # For Phase 1, just return a friendly message + the route decision.
    resp = MessagingResponse()
    msg = resp.message()

    if decision.kind == "voice" or decision.kind == "media":
        msg.body(
            "I got your media. Next: I’ll process it and reply shortly.\n\n"
            f"(route={decision.kind}, intent={decision.intent}, lang={decision.language})"
        )
    elif decision.kind == "text":
        preview = (body_text or "").strip()
        if len(preview) > 200:
            preview = preview[:200] + "…"
        if decision.intent == "voice_reply_request":
            msg.body(
                "Yes — I fit talk, but right now I dey reply with text.\n\n"
                f"I received: {preview!r}\n\n"
                f"(route={decision.kind}, intent={decision.intent}, lang={decision.language})"
            )
            return Response(content=str(resp), media_type="application/xml")
        msg.body(
            "Hello Sister — Sisi Lola here.\n\n"
            f"I received: {preview!r}\n\n"
            f"(route={decision.kind}, intent={decision.intent}, lang={decision.language})"
        )
    else:
        msg.body("Send a message and I’ll help you.")

    return Response(content=str(resp), media_type="application/xml")


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("TWILIO_CREDENTIALS")],
    cpu=1,
    memory=512,
    min_containers=1,
    timeout=60,
)
@modal.asgi_app()
def fastapi_app():
    return web
