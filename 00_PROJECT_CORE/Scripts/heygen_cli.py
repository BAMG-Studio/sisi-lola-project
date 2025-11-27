"""CLI helper to hit the local /videos/generate endpoint and save the MP4."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_DIR = PROJECT_ROOT / "sisi_lola_api"
ENV_PATH = API_DIR / ".env"

# Make sure we can load env and keep PYTHONPATH happy if needed later
sys.path.insert(0, str(API_DIR))
load_dotenv(ENV_PATH)

DEFAULT_API_URL = "http://127.0.0.1:8000/videos/generate"
DEFAULT_OUT_DIR = PROJECT_ROOT / "03_MEDIA_ASSETS" / "CLI_HeyGen"


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "heygen_clip"


def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Support local path returned by stub flows
    if url.startswith("file://"):
        url = url.replace("file://", "")
    local_candidate = Path(url)
    if local_candidate.exists():
        dest.write_bytes(local_candidate.read_bytes())
        return dest

    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return dest


def run(
    scenario: str,
    script: Optional[str],
    aspect_ratio: str,
    avatar_id: Optional[str],
    voice_id: Optional[str],
    caption: bool,
    filename: Optional[str],
    output_dir: Path,
    api_url: str,
) -> None:
    payload = {
        "scenario": scenario,
        "aspect_ratio": aspect_ratio,
        "script": script or scenario,
        "avatar_id": avatar_id,
        "voice_id": voice_id,
        "caption": caption,
    }

    print(f"==> Requesting video from {api_url}")
    resp = requests.post(api_url, json=payload, timeout=240)
    try:
        data = resp.json()
    except Exception:
        data = {"status": "error", "message": resp.text}

    if resp.status_code >= 400:
        raise SystemExit(f"Request failed [{resp.status_code}]: {json.dumps(data, indent=2)}")

    status = data.get("status")
    if status != "success":
        raise SystemExit(f"Generation failed: {json.dumps(data, indent=2)}")

    result = data.get("result", {})
    media_url = result.get("media_url") or result.get("local_path")
    provider = data.get("provider", "unknown")
    if not media_url:
        raise SystemExit(f"No media_url returned. Full payload: {json.dumps(data, indent=2)}")

    name = filename or _slugify(scenario)
    dest = output_dir / f"{name}.mp4"
    saved = download_file(media_url, dest)
    print(f"[OK] Saved ({provider}) -> {saved}")

    meta_path = output_dir / f"{name}.json"
    meta_path.write_text(json.dumps(data, indent=2))
    print(f"[META] Metadata -> {meta_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="HeyGen video CLI (calls local /videos/generate).")
    parser.add_argument("--scenario", required=True, help="High-level scenario for DNA prompt.")
    parser.add_argument("--script", help="Explicit teleprompter script; defaults to scenario.")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (e.g., 16:9, 9:16).")
    parser.add_argument("--avatar-id", help="HeyGen avatar ID override.")
    parser.add_argument("--voice-id", help="HeyGen voice ID override.")
    parser.add_argument("--caption", action="store_true", help="Enable burned-in captions.")
    parser.add_argument("--filename", help="Output filename (without extension).")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Destination directory for MP4 + JSON.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API endpoint to call.")
    args = parser.parse_args()

    run(
        scenario=args.scenario,
        script=args.script,
        aspect_ratio=args.aspect_ratio,
        avatar_id=args.avatar_id,
        voice_id=args.voice_id,
        caption=args.caption,
        filename=args.filename,
        output_dir=args.out_dir,
        api_url=args.api_url,
    )


if __name__ == "__main__":
    main()
