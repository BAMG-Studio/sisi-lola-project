#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SISI LOLA INSTAGRAM AUTO-POSTING TEST
═══════════════════════════════════════════════════════════════════════════════
                    Verify Instagram Graph API Connection
═══════════════════════════════════════════════════════════════════════════════

Tests:
1. Verify Instagram Business Account connection
2. Test image posting to Instagram
3. Validate token permissions
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Load environment from multiple locations
from dotenv import load_dotenv

# Try loading from multiple .env locations
env_paths = [
    Path("sisi_lola_api/.env"),
    Path(".env"),
    Path("00_PROJECT_CORE/.env"),
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded env from: {env_path}")
        break

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841478533567114")
GRAPH_API_VERSION = "v18.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def check_token():
    """Check if the Instagram token is valid."""
    print("\n" + "═" * 70)
    print("              INSTAGRAM CREDENTIALS CHECK")
    print("═" * 70)
    
    if not INSTAGRAM_TOKEN:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in environment!")
        return False
    
    print(f"✅ Token found: {INSTAGRAM_TOKEN[:20]}...")
    print(f"✅ Account ID: {INSTAGRAM_ACCOUNT_ID}")
    
    # Verify token with debug endpoint
    print("\n📍 Checking token validity...")
    try:
        response = requests.get(
            f"{GRAPH_API_BASE}/debug_token",
            params={
                "input_token": INSTAGRAM_TOKEN,
                "access_token": INSTAGRAM_TOKEN
            }
        )
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_valid = data.get("is_valid", False)
            expires_at = data.get("expires_at", 0)
            scopes = data.get("scopes", [])
            
            if is_valid:
                print(f"   ✅ Token is VALID")
                if expires_at > 0:
                    from datetime import datetime
                    exp_date = datetime.fromtimestamp(expires_at)
                    print(f"   📅 Expires: {exp_date}")
                else:
                    print("   📅 Expires: Never (Long-lived token)")
                print(f"   🔑 Scopes: {', '.join(scopes[:5])}...")
                return True
            else:
                print(f"   ❌ Token is INVALID")
                return False
        else:
            print(f"   ⚠️  Could not verify: {response.status_code}")
            # Try alternate check
            return check_account()
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_account():
    """Check Instagram Business Account details."""
    print("\n📍 Checking Instagram Business Account...")
    
    try:
        response = requests.get(
            f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}",
            params={
                "access_token": INSTAGRAM_TOKEN,
                "fields": "id,username,name,profile_picture_url,followers_count,media_count,biography"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Account Found!")
            print(f"   📛 Username: @{data.get('username', 'N/A')}")
            print(f"   📊 Followers: {data.get('followers_count', 'N/A')}")
            print(f"   📸 Media Count: {data.get('media_count', 'N/A')}")
            print(f"   📝 Bio: {data.get('biography', 'N/A')[:50]}...")
            return True
        else:
            error = response.json().get("error", {})
            print(f"   ❌ Error: {error.get('message', response.text[:100])}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_photo_post(image_url: str = None, caption: str = None):
    """Test posting a photo to Instagram."""
    print("\n" + "═" * 70)
    print("              TEST PHOTO POST")
    print("═" * 70)
    
    # Default test image from the pipeline
    if not image_url:
        image_url = "https://replicate.delivery/xezq/3gerNNEkGvVqY6HcWvYjPHBPH2S2FeIgR3cQRdwXnf89w4zrA/out-0.png"
    
    if not caption:
        caption = """🇳🇬 Testing Sisi Lola Auto-Posting! 🚀

How you dey, my people? This na test post from our AI system o!
We dey build something amazing for Nigeria and Africa! 

#SisiLola #NigeriaAI #AfricanTech #NaijaContent #AIContentCreator

💚🤍💚"""
    
    print(f"📸 Image URL: {image_url[:60]}...")
    print(f"📝 Caption: {caption[:50]}...")
    
    # Step 1: Create media container
    print("\n📍 Step 1: Creating media container...")
    try:
        response = requests.post(
            f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/media",
            params={
                "access_token": INSTAGRAM_TOKEN,
                "image_url": image_url,
                "caption": caption
            }
        )
        
        if response.status_code == 200:
            container_id = response.json().get("id")
            print(f"   ✅ Container created: {container_id}")
            
            # Step 2: Publish the media
            print("\n📍 Step 2: Publishing to Instagram...")
            
            # Wait a moment for processing
            import time
            print("   ⏳ Waiting for media processing (5 seconds)...")
            time.sleep(5)
            
            publish_response = requests.post(
                f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
                params={
                    "access_token": INSTAGRAM_TOKEN,
                    "creation_id": container_id
                }
            )
            
            if publish_response.status_code == 200:
                post_id = publish_response.json().get("id")
                print(f"   ✅ POST PUBLISHED! ID: {post_id}")
                print(f"\n🎉 SUCCESS! Check @sisilolalive on Instagram!")
                return True
            else:
                error = publish_response.json().get("error", {})
                print(f"   ❌ Publish failed: {error.get('message', publish_response.text[:100])}")
                return False
        else:
            error = response.json().get("error", {})
            error_msg = error.get("message", response.text[:200])
            print(f"   ❌ Container creation failed: {error_msg}")
            
            # Check for specific errors
            if "URL not responding" in error_msg or "media could not be fetched" in error_msg:
                print("\n   💡 TIP: The image URL might have expired.")
                print("   💡 Replicate URLs are temporary. Generate a new image or use permanent URL.")
            
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def run_full_test():
    """Run all Instagram tests."""
    print("═" * 70)
    print("         SISI LOLA INSTAGRAM AUTO-POSTING TEST")
    print("═" * 70)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Check token
    results["token_valid"] = check_token()
    
    # Test 2: Check account
    results["account_connected"] = check_account()
    
    # Test 3: Post test (only if account check passed)
    if results["account_connected"]:
        print("\n" + "═" * 70)
        print("⚠️  READY TO POST TEST IMAGE")
        print("═" * 70)
        print("This will post a test image to @sisilolalive")
        print("To skip, press Ctrl+C within 5 seconds...")
        
        try:
            import time
            for i in range(5, 0, -1):
                print(f"   Posting in {i}...")
                time.sleep(1)
            
            results["post_success"] = test_photo_post()
        except KeyboardInterrupt:
            print("\n   ⏭️  Post test skipped by user")
            results["post_success"] = "skipped"
    else:
        print("\n⏭️  Skipping post test - account not connected")
        results["post_success"] = False
    
    # Summary
    print("\n" + "═" * 70)
    print("                      SUMMARY")
    print("═" * 70)
    print(f"✅ Token Valid: {'YES' if results['token_valid'] else 'NO'}")
    print(f"✅ Account Connected: {'YES' if results['account_connected'] else 'NO'}")
    print(f"✅ Post Test: {'SUCCESS' if results['post_success'] == True else 'SKIPPED' if results['post_success'] == 'skipped' else 'FAILED'}")
    
    if results["token_valid"] and results["account_connected"]:
        print("\n🎉 Instagram integration is READY for auto-posting!")
    else:
        print("\n⚠️  Some issues need to be resolved:")
        if not results["token_valid"]:
            print("   - Token needs to be refreshed")
        if not results["account_connected"]:
            print("   - Account connection needs to be fixed")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Check for --skip-post flag
    skip_post = "--skip-post" in sys.argv or "--no-post" in sys.argv
    
    if skip_post:
        print("⏭️  Running in check-only mode (no posting)")
        check_token()
        check_account()
    else:
        run_full_test()
