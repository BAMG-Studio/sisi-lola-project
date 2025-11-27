"""
Quick Test Script - Single Image DNA Validation
Run this for a fast DNA check before running the full suite.
"""

import requests
import json
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def quick_test():
    print("=" * 60)
    print("SISI LOLA - QUICK DNA TEST")
    print("=" * 60)
    
    # Test 1: Check API is running
    print("\n[1/4] Checking API connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        resp_json = response.json()
        status_msg = resp_json.get("system_status", resp_json)
        print(f"✅ API is online: {status_msg}")
    except Exception as e:
        print(f"❌ API is offline. Error: {str(e)}")
        print("\nStart the server with:")
        print("cd sisi_lola_api && ./venv/bin/python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Test 2: Generate a test image
    print("\n[2/4] Generating test image...")
    payload = {
        "scenario": "smiling confidently at the camera in a professional studio",
        "aspect_ratio": "1:1"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/images/generate", json=payload, timeout=120)
        result = response.json()
        
        print(f"✅ Image generation request sent")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Provider: {result.get('provider', 'unknown')}")
        print(f"   DNA Integrity: {result.get('dna_integrity', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        sys.exit(1)
    
    # Test 3: Validate DNA injection
    print("\n[3/4] Validating DNA injection...")
    injected_prompt = result.get("injected_prompt", "")
    
    dna_keywords = ["voluptuous", "yoruba", "mature", "hourglass", "luminous dark skin"]
    found_keywords = [kw for kw in dna_keywords if kw.lower() in injected_prompt.lower()]
    
    print(f"   Found DNA keywords: {len(found_keywords)}/{len(dna_keywords)}")
    for kw in found_keywords:
        print(f"   ✅ {kw}")
    
    missing = [kw for kw in dna_keywords if kw not in found_keywords]
    if missing:
        print(f"   ⚠️  Missing: {', '.join(missing)}")
    
    # Test 4: Check reference images
    print("\n[4/4] Checking reference images...")
    ref_images = result.get("reference_images", [])
    
    if len(ref_images) > 0:
        print(f"✅ {len(ref_images)} reference images detected")
        for img in ref_images:
            print(f"   - {img}")
    else:
        print(f"⚠️  No reference images found")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("TEST RESULT")
    print("=" * 60)
    
    passed = result.get("status") == "success" and len(found_keywords) >= 4 and len(ref_images) > 0

    if passed:
        print("✅ PASS - DNA integrity maintained!")
        print("\nNext steps:")
        print("1. Run the full validation suite: python dna_validation_test.py")
        print("2. Start batch asset generation: python batch_asset_generator.py")
    elif result.get("status") == "simulation":
        print("⚠️  SIMULATION MODE - Add KLINGAI_API_KEY to .env for real generation")
        sys.exit(2)
    else:
        print("❌ FAIL - DNA integrity issues detected")
        print("\nTroubleshooting:")
        print("1. Check that DNA reference images exist in assets/dna/")
        print("2. Verify VISUAL_PROMPT_CORE in app/config.py")
        print("3. Ensure KLINGAI_API_KEY is set in .env")
        sys.exit(1)
    
    print("=" * 60)
    
    # Save quick test result
    with open("quick_test_result.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "dna_keywords_found": found_keywords,
            "reference_images_count": len(ref_images)
        }, f, indent=2)
    
    print(f"\n📄 Full result saved to: quick_test_result.json")
    sys.exit(0)

if __name__ == "__main__":
    quick_test()
