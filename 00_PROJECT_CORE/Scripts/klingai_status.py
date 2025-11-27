"""Quick CLI helper to inspect KlingAI JWT readiness and API status."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_DIR = PROJECT_ROOT / "sisi_lola_api"
ENV_PATH = API_DIR / ".env"

# Ensure app modules can be imported when the script runs from 00_PROJECT_CORE/Scripts
sys.path.insert(0, str(API_DIR))

load_dotenv(ENV_PATH)

from app.utils.klingai import generate_klingai_token  # noqa: E402


def get_api_status() -> dict:
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # pragma: no cover - diagnostic helper
        return {"error": str(exc)}


def main() -> None:
    print("==> Sisi Lola | KlingAI Status Helper")

    try:
        token = generate_klingai_token()
        print("\nJWT (use this inside KlingAI verifier):")
        print(token)
    except Exception as exc:
        print(f"\nUnable to generate JWT: {exc}")
        token = None

    status = get_api_status()
    print("\nAPI Status (http://127.0.0.1:8000/):")
    print(json.dumps(status, indent=2))

    if token is None:
        print("\n⚠️  JWT generation failed. Confirm KLINGAI_ACCESS_KEY and KLINGAI_SECRET_KEY in .env")
    elif status.get("klingai_credentials_loaded") is False:
        print("\n⚠️  API is running without KlingAI credentials loaded. Restart the server after updating .env.")


if __name__ == "__main__":
    main()
