#!/usr/bin/env python3
"""
Test RecCloud API with a real Dropbox video.

This script:
1. Creates a public shareable Dropbox link for the video
2. Sends it to RecCloud API for transcription
3. Polls for completion and returns transcript
"""

import os
import sys
import time
import requests
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RecCloudTest")

# RecCloud API Configuration
RECCLOUD_API_KEY = os.getenv("RECCLOUD_API_KEY", "wxbgr07ikdtvgnws4")
RECCLOUD_BASE_URL = "https://techhk.aoscdn.com/api"

# Dropbox Configuration
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN", "")

# Video file path
VIDEO_PATH = "/SLS/SL TRAINING VIDEOS/FLAVOUR N'ABANIA_ MY MUSIC CAREER STARTED IN THE CHURCH _ EP115 PART 2 FT @officialflavour.mp4"


def create_dropbox_shared_link(dropbox_path: str) -> str:
    """Create a public shared link for a Dropbox file."""
    
    if not DROPBOX_ACCESS_TOKEN:
        logger.error("DROPBOX_ACCESS_TOKEN not set")
        logger.info("To get a token:")
        logger.info("1. Go to https://www.dropbox.com/developers/apps")
        logger.info("2. Create an app with 'Full Dropbox' access")
        logger.info("3. Generate an access token")
        logger.info("4. Set DROPBOX_ACCESS_TOKEN environment variable")
        return None
    
    try:
        import dropbox
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        
        # Try to create shared link
        try:
            result = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            url = result.url.replace("?dl=0", "?dl=1")
            logger.info(f"Created new shared link: {url}")
            return url
        except dropbox.exceptions.ApiError as e:
            # If link already exists, get it
            if "shared_link_already_exists" in str(e):
                links = dbx.sharing_list_shared_links(path=dropbox_path)
                if links.links:
                    url = links.links[0].url.replace("?dl=0", "?dl=1")
                    logger.info(f"Using existing shared link: {url}")
                    return url
            logger.error(f"Dropbox API error: {e}")
            return None
            
    except ImportError:
        logger.error("dropbox SDK not installed. Run: pip install dropbox")
        return None
    except Exception as e:
        logger.error(f"Failed to create Dropbox link: {e}")
        return None


def test_reccloud_api(video_url: str):
    """Test RecCloud API with a video URL."""
    
    logger.info(f"\n{'='*60}")
    logger.info("TESTING RECCLOUD API")
    logger.info(f"{'='*60}\n")
    
    logger.info(f"Video URL: {video_url[:80]}...")
    logger.info(f"API Key: {RECCLOUD_API_KEY[:8]}...")
    
    # Create transcription task
    logger.info("\n[1] Creating transcription task...")
    
    headers = {
        "X-API-KEY": RECCLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url,
        "type": 4,
        "content_type": 1,
        "speaker_recognition": 1
    }
    
    try:
        response = requests.post(
            f"{RECCLOUD_BASE_URL}/tasks/audio/recognition",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text[:500]}")
        
        if response.status_code != 200:
            logger.error(f"API error: {response.text}")
            return False
        
        result = response.json()
        task_id = result.get("task_id")
        
        if not task_id:
            logger.error("No task_id in response")
            return False
        
        logger.info(f"✅ Task created: {task_id}")
        
        # Poll for completion
        logger.info("\n[2] Polling for completion...")
        
        for attempt in range(30):  # Max 5 minutes
            time.sleep(10)
            
            status_response = requests.get(
                f"{RECCLOUD_BASE_URL}/tasks/audio/recognition/{task_id}",
                headers=headers,
                timeout=30
            )
            
            status = status_response.json()
            state = status.get("state", 0)
            progress = status.get("progress", 0)
            
            logger.info(f"  Attempt {attempt+1}: state={state}, progress={progress}%")
            
            if state == 1:  # Complete
                logger.info("\n[3] Transcription complete!")
                logger.info(f"Duration: {status.get('duration', 0)} seconds")
                logger.info(f"Language: {status.get('source_language', 'unknown')}")
                
                result_text = status.get("result", "")
                logger.info(f"\n{'='*40}")
                logger.info("TRANSCRIPT PREVIEW:")
                logger.info(f"{'='*40}")
                logger.info(result_text[:1000] + "..." if len(result_text) > 1000 else result_text)
                
                # Save full transcript
                output_path = Path("ml_training/datasets/video_training_data/test_transcript.txt")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result_text)
                logger.info(f"\n✅ Full transcript saved to: {output_path}")
                
                return True
            
            elif state < 0:  # Failed
                logger.error(f"Task failed: {status.get('state_detail', 'Unknown error')}")
                return False
        
        logger.error("Timeout waiting for completion")
        return False
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return False


def main():
    logger.info("\n" + "="*60)
    logger.info("SISI LOLA - RECCLOUD API TEST")
    logger.info("="*60)
    
    # Step 1: Create Dropbox shared link
    logger.info("\n[STEP 1] Creating Dropbox shared link...")
    video_url = create_dropbox_shared_link(VIDEO_PATH)
    
    if not video_url:
        logger.error("Failed to create Dropbox shared link")
        logger.info("\n" + "="*60)
        logger.info("ALTERNATIVE: Manual URL")
        logger.info("="*60)
        logger.info("You can manually create a shared link:")
        logger.info("1. Right-click the video in Dropbox")
        logger.info("2. Click 'Copy Link'")
        logger.info("3. Change ?dl=0 to ?dl=1 in the URL")
        logger.info("4. Run: MANUAL_VIDEO_URL='your_url' python3 test_reccloud_api.py")
        
        # Check for manual URL
        manual_url = os.getenv("MANUAL_VIDEO_URL")
        if manual_url:
            logger.info(f"\nUsing manual URL: {manual_url[:50]}...")
            video_url = manual_url
        else:
            return False
    
    # Step 2: Test RecCloud API
    logger.info("\n[STEP 2] Testing RecCloud API...")
    success = test_reccloud_api(video_url)
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("✅ RECCLOUD API TEST PASSED!")
        logger.info("="*60)
    else:
        logger.info("\n" + "="*60)
        logger.info("❌ RECCLOUD API TEST FAILED")
        logger.info("="*60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
