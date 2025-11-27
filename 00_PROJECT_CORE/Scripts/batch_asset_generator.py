"""CSV-driven batch generator outline for Sisi Lola assets."""
from __future__ import annotations

import csv
import json
import time
import base64
import os
import shutil
import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import httpx
from dotenv import load_dotenv

API_BASE_URL = "http://127.0.0.1:8000"
MANIFEST_PATH = Path(__file__).resolve().parents[2] / "00_PROJECT_CORE" / "PRODUCTION_MANIFEST.csv"
BATCH_ROOT = Path(__file__).resolve().parent / "batch_runs"
ASSETS_ROOT = Path(__file__).resolve().parents[2] / "assets" / "generated"
load_dotenv()  # load .env if present (root or current)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / "sisi_lola_api" / ".env")

DEFAULT_DELAY = float(os.getenv("BATCH_REQUEST_DELAY", 6.0))  # seconds between requests to respect rate limits
RETRY_BACKOFF = float(os.getenv("BATCH_RETRY_BACKOFF", 30.0))
MAX_RETRIES = int(os.getenv("BATCH_MAX_RETRIES", 3))


@dataclass
class AssetJob:
    asset_id: str
    modality: str  # image | video | audio
    scenario: str
    aspect_ratio: str = "16:9"
    duration: int = 5
    outfit_override: str | None = None


def load_manifest(path: Path = MANIFEST_PATH) -> List[AssetJob]:
    if not path.exists():
        raise FileNotFoundError(path)

    jobs: List[AssetJob] = []
    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            jobs.append(
                AssetJob(
                    asset_id=row.get("Asset Name") or f"asset-{idx}",
                    modality=(row.get("Asset Type") or "image").strip().lower(),
                    scenario=row.get("Description") or row.get("Scenario") or "",
                    aspect_ratio=row.get("Aspect Ratio", "16:9"),
                    duration=int(row.get("Duration", 5) or 5),
                    outfit_override=row.get("Outfit Override") or None,
                )
            )
    return jobs


def payload_for(job: AssetJob) -> dict:
    if job.modality == "audio":
        return {
            "text": job.scenario,
            "accent": "nigerian-yoruba",
            "languages": ["Yoruba", "English"],
            # "voice_id": ... # Optional, uses default
        }

    payload = {
        "scenario": job.scenario,
        "aspect_ratio": job.aspect_ratio,
    }
    if job.outfit_override:
        payload["outfit_override"] = job.outfit_override
    if job.modality == "video":
        payload["duration"] = job.duration
    return payload


def invoke_api(job: AssetJob) -> dict:
    if job.modality == "audio":
        endpoint = "/audio/speak"
    elif job.modality == "image":
        endpoint = "/images/generate"
    else:
        endpoint = "/videos/generate"

    url = f"{API_BASE_URL}{endpoint}"

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):  # initial try + retries
        with httpx.Client(timeout=240.0) as client:
            response = client.post(url, json=payload_for(job))
            try:
                data = response.json()
            except ValueError:
                data = {"status": "error", "message": response.text}

        data["http_status"] = response.status_code
        data["asset_id"] = job.asset_id
        data["modality"] = job.modality

        # Retry on 429 Too Many Requests for video/image
        if response.status_code == 429 and job.modality in ("video", "image") and attempt <= MAX_RETRIES:
            last_error = data
            sleep_for = RETRY_BACKOFF * attempt
            print(f"   [!] Rate limited (429) on attempt {attempt}. Backing off {sleep_for}s then retrying...")
            time.sleep(sleep_for)
            continue

        return data

    return last_error or data


def extract_url(result: dict) -> str | None:
    """Extracts the media URL from the provider response."""
    provider = result.get("provider")
    if provider == "OpenAI":
        try:
            return result["result"]["data"][0]["url"]
        except (KeyError, IndexError, TypeError):
            return None
    if provider and provider.lower() == "perplexity":
        # Perplexity helper normalizes to result["media_url"] when present
        try:
            return result["result"].get("media_url") or result["result"]["data"][0]["url"]
        except Exception:
            return None
    # Stub/local video fallback
    try:
        if "result" in result:
            inner = result["result"]
            if isinstance(inner, dict):
                if inner.get("local_path"):
                    return inner["local_path"]
                if inner.get("media_url"):
                    return inner["media_url"]
    except Exception:
        pass
    # TODO: Add KlingAI URL extraction logic here
    return None


def download_asset(url: str, dest_path: Path) -> bool:
    """Downloads the asset from the URL to the destination path."""
    # Local path copy support
    local_candidate = url.replace("file://", "")
    if Path(local_candidate).exists():
        try:
            dest_path.write_bytes(Path(local_candidate).read_bytes())
            parent = Path(local_candidate).parent
            if parent.name.startswith("stub_video_"):
                shutil.rmtree(parent, ignore_errors=True)
            return True
        except Exception as e:
            print(f"   [!] Failed to copy local media: {e}")
            return False

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            dest_path.write_bytes(resp.content)
        return True
    except Exception as e:
        print(f"   [!] Failed to download media: {e}")
        return False


def persist(job: AssetJob, result: dict, run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{job.asset_id}_{job.modality}.json"
    path = run_dir / filename
    path.write_text(json.dumps(result, indent=2))

    # Handle Audio (Base64)
    if job.modality == "audio" and "audio_base64" in result:
        media_filename = f"{job.asset_id}_{job.modality}.mp3"
        batch_media_path = run_dir / media_filename
        
        try:
            audio_bytes = base64.b64decode(result["audio_base64"])
            batch_media_path.write_bytes(audio_bytes)
            print(f"   Saved audio to {batch_media_path}")
            
            # Save to central assets library
            ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
            central_media_path = ASSETS_ROOT / media_filename
            central_media_path.write_bytes(audio_bytes)
            print(f"   Copied to library {central_media_path}")
            
            result["local_path"] = str(central_media_path)
            path.write_text(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"   [!] Failed to save audio: {e}")
            
        return path

    # Handle Image/Video (URL Download)
    url = extract_url(result)
    if url:
        ext = "png" if job.modality == "image" else "mp4"
        media_filename = f"{job.asset_id}_{job.modality}.{ext}"
        
        # 1. Save to batch run directory
        batch_media_path = run_dir / media_filename
        if download_asset(url, batch_media_path):
            print(f"   Saved media to {batch_media_path}")
            
            # 2. Save to central assets library
            ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
            central_media_path = ASSETS_ROOT / media_filename
            central_media_path.write_bytes(batch_media_path.read_bytes())
            print(f"   Copied to library {central_media_path}")
            
            # Update JSON with local path
            result["local_path"] = str(central_media_path)
            path.write_text(json.dumps(result, indent=2))

    return path


def run_batch(jobs: Iterable[AssetJob], delay: float = DEFAULT_DELAY, force: bool = False) -> None:
    jobs = list(jobs)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = BATCH_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []

    print(f"🚀 Starting batch run ({len(jobs)} jobs)")
    for idx, job in enumerate(jobs, start=1):
        # Check if asset already exists in library
        if job.modality == "image":
            ext = "png"
        elif job.modality == "audio":
            ext = "mp3"
        else:
            ext = "mp4"

        central_media_path = ASSETS_ROOT / f"{job.asset_id}_{job.modality}.{ext}"

        if central_media_path.exists() and not force:
            print(f"\n[{idx}] Skipping {job.asset_id} ({job.modality}) - Already exists at {central_media_path}")
            continue

        print(f"\n[{idx}] Generating {job.asset_id} ({job.modality})")
        result = invoke_api(job)
        save_path = persist(job, result, run_dir)
        summary.append(result)
        print(f"   HTTP {result.get('http_status')} -> saved {save_path}")
        time.sleep(delay)

    (run_dir / "_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nBatch complete. Summary stored under {run_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch generate Sisi Lola assets from manifest.")
    parser.add_argument("--modality", choices=["all", "image", "video", "audio"], default="all", help="Restrict to a single modality.")
    parser.add_argument("--ids", nargs="*", help="Specific asset IDs to process (space-separated).")
    parser.add_argument("--force", action="store_true", help="Force regeneration even if asset already exists.")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Override delay between requests.")
    args = parser.parse_args()

    all_jobs = load_manifest()
    if args.modality != "all":
        all_jobs = [j for j in all_jobs if j.modality == args.modality]
    if args.ids:
        wanted = set(args.ids)
        all_jobs = [j for j in all_jobs if j.asset_id in wanted]

    if not all_jobs:
        print("No matching jobs found.")
    else:
        run_batch(all_jobs, delay=args.delay, force=args.force)
