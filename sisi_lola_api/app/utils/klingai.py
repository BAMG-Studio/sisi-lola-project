"""Utilities for generating KlingAI JWT tokens and headers."""
import os
import time
from typing import Dict

import jwt

KLINGAI_API_DOMAIN = os.getenv("KLINGAI_API_DOMAIN", "https://api-singapore.klingai.com")
KLINGAI_IMAGE_ENDPOINT = f"{KLINGAI_API_DOMAIN}/v1/images/generations"
KLINGAI_VIDEO_ENDPOINT = f"{KLINGAI_API_DOMAIN}/v1/videos/text2video"


def _get_credentials() -> tuple[str, str]:
    access_key = os.getenv("KLINGAI_ACCESS_KEY")
    secret_key = os.getenv("KLINGAI_SECRET_KEY")

    if not access_key or not secret_key:
        raise ValueError("KlingAI credentials missing. Set KLINGAI_ACCESS_KEY and KLINGAI_SECRET_KEY in .env")

    return access_key, secret_key


def generate_klingai_token(expiry_seconds: int = 1800) -> str:
    """Generate a short-lived JWT token required by KlingAI."""
    access_key, secret_key = _get_credentials()
    now = int(time.time())

    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": access_key,
        "exp": now + expiry_seconds,
        "nbf": now - 5,
    }

    token = jwt.encode(payload, secret_key, headers=headers, algorithm="HS256")
    # PyJWT may return bytes in older versions, normalize to string
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def build_klingai_headers() -> Dict[str, str]:
    """Return the Authorization + content headers for KlingAI requests."""
    token = generate_klingai_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
