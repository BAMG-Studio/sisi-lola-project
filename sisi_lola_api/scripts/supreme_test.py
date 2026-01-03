#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 SISI LOLA SUPREME MODULE TESTER
=============================================================================
Test ALL Sisi Lola modules before launch!
Run: python -m sisi_lola_api.scripts.supreme_test
=============================================================================
"""

import asyncio
import json
import httpx
import os
from datetime import datetime
from pathlib import Path

# Base URL
BASE_URL = "http://localhost:8000"

# Test Results
results = {
    "timestamp": datetime.now().isoformat(),
    "tests": [],
    "summary": {"passed": 0, "failed": 0}
}

def log_result(test_name: str, passed: bool, details: str = "", response_time_ms: float = 0):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name} ({response_time_ms:.0f}ms)")
    if details:
        print(f"   └─ {details[:100]}...")
    
    results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details,
        "response_time_ms": response_time_ms
    })
    
    if passed:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

async def test_health():
    """Test API health endpoint"""
    async with httpx.AsyncClient() as client:
        start = datetime.now()
        try:
            r = await client.get(f"{BASE_URL}/api/health", timeout=10)
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            if r.status_code == 200:
                data = r.json()
                log_result("API Health Check", True, f"Status: {data.get('system_status')}", elapsed)
                return True
            else:
                log_result("API Health Check", False, f"HTTP {r.status_code}", elapsed)
                return False
        except Exception as e:
            log_result("API Health Check", False, str(e), 0)
            return False

async def test_gemini_brain():
    """Test Gemini 3 Pro Supreme Brain"""
    async with httpx.AsyncClient() as client:
        start = datetime.now()
        try:
            r = await client.post(
                f"{BASE_URL}/api/v2/vibe/demo-chat",
                json={
                    "message": "How far na? Tell me something about Lagos in Pidgin!",
                    "session_id": "test_supreme_001"
                },
                timeout=30
            )
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            if r.status_code == 200:
                data = r.json()
                response = data.get("response", "")[:100]
                log_result("Gemini 3 Pro Brain", True, response, elapsed)
                return True
            else:
                log_result("Gemini 3 Pro Brain", False, f"HTTP {r.status_code}: {r.text[:100]}", elapsed)
                return False
        except Exception as e:
            log_result("Gemini 3 Pro Brain", False, str(e), 0)
            return False

async def test_modal_inference():
    """Test Modal Fast Inference"""
    async with httpx.AsyncClient() as client:
        start = datetime.now()
        try:
            r = await client.post(
                f"{BASE_URL}/api/v2/enhanced-chat/chat",
                json={
                    "message": "Wetin dey happen?",
                    "session_id": "test_modal_001"
                },
                timeout=30
            )
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            if r.status_code == 200:
                data = r.json()
                log_result("Modal Fast Inference", True, f"Source: {data.get('source', 'N/A')}", elapsed)
                return True
            else:
                log_result("Modal Fast Inference", False, f"HTTP {r.status_code}", elapsed)
                return False
        except Exception as e:
            log_result("Modal Fast Inference", False, str(e), 0)
            return False

async def test_social_tokens():
    """Test Social Media Token Status"""
    async with httpx.AsyncClient() as client:
        start = datetime.now()
        try:
            r = await client.get(f"{BASE_URL}/api/v2/social/tokens/status", timeout=10)
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            if r.status_code == 200:
                data = r.json()
                tokens = data.get("social_tokens", {})
                configured = sum(1 for t in tokens.values() if t.get("configured"))
                log_result("Social Token Status", True, f"{configured}/{len(tokens)} platforms configured", elapsed)
                return True
            else:
                log_result("Social Token Status", False, f"HTTP {r.status_code}", elapsed)
                return False
        except Exception as e:
            log_result("Social Token Status", False, str(e), 0)
            return False

async def test_vibes_list():
    """Test Vibes Content Queue"""
    async with httpx.AsyncClient() as client:
        start = datetime.now()
        try:
            r = await client.get(f"{BASE_URL}/api/v2/vibes/list", timeout=10)
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            if r.status_code == 200:
                data = r.json()
                total = data.get("total_vibes", 0)
                log_result("Vibes Content Queue", True, f"{total} vibes loaded", elapsed)
                return True
            else:
                log_result("Vibes Content Queue", False, f"HTTP {r.status_code}", elapsed)
                return False
        except Exception as e:
            log_result("Vibes Content Queue", False, str(e), 0)
            return False

async def test_engagement_batch():
    """Test Batch Engagement Reply Generation"""
    async with httpx.AsyncClient() as client:
        start = datetime.now()
        try:
            r = await client.post(
                f"{BASE_URL}/api/v2/vibe/engage-batch",
                json={
                    "comments": [
                        {"id": "1", "text": "Love this!", "username": "test_user"},
                        {"id": "2", "text": "Sisi Lola is amazing!", "username": "fan_nigeria"}
                    ],
                    "platform": "instagram"
                },
                timeout=60
            )
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            if r.status_code == 200:
                data = r.json()
                processed = data.get("processed", 0)
                log_result("Batch Engagement", True, f"Processed {processed} comments", elapsed)
                return True
            else:
                log_result("Batch Engagement", False, f"HTTP {r.status_code}", elapsed)
                return False
        except Exception as e:
            log_result("Batch Engagement", False, str(e), 0)
            return False

async def test_ui_pages():
    """Test UI Pages Load"""
    async with httpx.AsyncClient() as client:
        pages = ["/", "/demo", "/dashboard"]
        all_passed = True
        
        for page in pages:
            start = datetime.now()
            try:
                r = await client.get(f"{BASE_URL}{page}", timeout=10)
                elapsed = (datetime.now() - start).total_seconds() * 1000
                
                if r.status_code == 200:
                    log_result(f"UI Page: {page}", True, "HTML loaded", elapsed)
                else:
                    log_result(f"UI Page: {page}", False, f"HTTP {r.status_code}", elapsed)
                    all_passed = False
            except Exception as e:
                log_result(f"UI Page: {page}", False, str(e), 0)
                all_passed = False
        
        return all_passed

async def run_all_tests():
    """Run all supreme tests"""
    print("\n" + "=" * 60)
    print("🇳🇬 SISI LOLA SUPREME MODULE TESTER")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60 + "\n")
    
    # Run tests
    await test_health()
    await test_ui_pages()
    await test_gemini_brain()
    await test_modal_inference()
    await test_social_tokens()
    await test_vibes_list()
    await test_engagement_batch()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {results['summary']['passed']}")
    print(f"❌ Failed: {results['summary']['failed']}")
    
    total = results['summary']['passed'] + results['summary']['failed']
    rate = (results['summary']['passed'] / total * 100) if total > 0 else 0
    print(f"📈 Success Rate: {rate:.1f}%")
    print("=" * 60)
    
    # Save results
    results_path = Path(__file__).parent.parent.parent / "test_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {results_path}")
    
    if results['summary']['failed'] == 0:
        print("\n🎉 ALL SYSTEMS GO! Sisi Lola ready to LAUNCH! 🚀")
    else:
        print("\n⚠️ Some modules need attention before launch.")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_all_tests())
