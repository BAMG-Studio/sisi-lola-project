#!/usr/bin/env python3
"""
Sisi Lola Transcription Status Checker
========================================
Checks status of RecCloud transcription jobs and downloads completed transcripts.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

RECCLOUD_API_KEY = os.getenv("RECCLOUD_API_KEY")
RECCLOUD_BASE_URL = "https://techhk.aoscdn.com/api"

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "ml_training" / "datasets" / "transcriptions"


def check_task_status(task_id: str) -> dict:
    """Check RecCloud task status."""
    headers = {
        "X-API-KEY": RECCLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Correct endpoint for audio recognition tasks
        response = requests.get(
            f"{RECCLOUD_BASE_URL}/tasks/audio/recognition/{task_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error checking task {task_id[:8]}...: {e}")
        return None


def get_transcript_result(task_id: str) -> dict:
    """Get the transcript result for a completed task."""
    headers = {
        "X-API-KEY": RECCLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{RECCLOUD_BASE_URL}/tasks/{task_id}/result",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error getting result for {task_id}: {e}")
        return None


def main():
    print("=" * 60)
    print("SISI LOLA TRANSCRIPTION STATUS CHECK")
    print("=" * 60)
    
    # Load job manifest
    manifest_path = OUTPUT_DIR / "transcription_jobs.json"
    if not manifest_path.exists():
        print("❌ No job manifest found. Run transcribe_videos.py first.")
        return
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    jobs = manifest.get("jobs", [])
    print(f"\n📋 Checking status of {len(jobs)} transcription jobs...\n")
    
    completed = 0
    processing = 0
    failed = 0
    
    updated_jobs = []
    
    for job in jobs:
        video = job.get("video", "unknown")
        task_id = job.get("task_id")
        
        if not task_id:
            print(f"⏩ {video}: No task_id")
            updated_jobs.append(job)
            continue
        
        status_response = check_task_status(task_id)
        
        if status_response:
            # Parse the response
            data = status_response.get("data", status_response)
            state = data.get("state", data.get("status", "unknown"))
            progress = data.get("progress", 0)
            
            # Map states
            if state in ["complete", "completed", "finished", 3]:
                status_str = "✅ COMPLETE"
                completed += 1
                job["transcription_status"] = "complete"
                
                # Try to get the result
                result = get_transcript_result(task_id)
                if result:
                    # Save transcript
                    transcript_path = OUTPUT_DIR / f"{video}_transcript.json"
                    with open(transcript_path, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"  📄 Saved transcript to: {transcript_path.name}")
                    job["transcript_file"] = str(transcript_path)
                    
            elif state in ["processing", "transcribing", 1, 2]:
                status_str = f"🔄 PROCESSING ({progress}%)"
                processing += 1
                job["transcription_status"] = "processing"
            elif state in ["failed", "error", -1]:
                status_str = "❌ FAILED"
                failed += 1
                job["transcription_status"] = "failed"
                job["error"] = data.get("error", "Unknown error")
            else:
                status_str = f"❓ UNKNOWN ({state})"
                job["transcription_status"] = str(state)
            
            print(f"  {video}: {status_str}")
        else:
            print(f"  {video}: ❓ Could not check status")
        
        updated_jobs.append(job)
    
    # Update manifest
    manifest["jobs"] = updated_jobs
    manifest["last_checked"] = datetime.now().isoformat()
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Complete: {completed}")
    print(f"🔄 Processing: {processing}")
    print(f"❌ Failed: {failed}")
    print(f"\n📁 Manifest updated: {manifest_path}")
    
    if processing > 0:
        print("\n⏳ Some jobs are still processing. Run this script again later.")
    
    if completed > 0:
        print(f"\n📄 {completed} transcripts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
