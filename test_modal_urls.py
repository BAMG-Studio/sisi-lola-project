"""
Modal URL Tester for Sisi Lola
Tests the inference endpoints to find the working one.
"""
import httpx
import asyncio
import sys

# All possible Modal endpoint URLs
MODAL_URLS = [
    "https://bamg-studio--sisi-lola-inference-generate.modal.run",
    "https://bamg-studio--sisi-lola-inference-modelinference-generate-text.modal.run",
    "https://bamg-studio--sisi-lola-modal-inference-model-generate.modal.run",
    "https://bamg-studio--sisi-lola-inference-modelinference-generate.modal.run",
]

async def test_url(url: str) -> dict:
    """Test a single Modal URL and return result."""
    print(f"🔍 Testing: {url[:60]}...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                url,
                json={
                    "message": "Hello Sisi! Quick test.",
                    "max_tokens": 30,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("text") or data.get("response") or str(data)
                return {
                    "url": url,
                    "status": "success",
                    "code": 200,
                    "response": text[:100] if text else "Empty response"
                }
            else:
                return {
                    "url": url,
                    "status": "error",
                    "code": response.status_code,
                    "response": response.text[:100]
                }
    except httpx.TimeoutException:
        return {"url": url, "status": "timeout", "code": 0, "response": "Request timed out (15s)"}
    except Exception as e:
        return {"url": url, "status": "exception", "code": 0, "response": str(e)[:100]}

async def main():
    print("=" * 60)
    print("🇳🇬 SISI LOLA - MODAL ENDPOINT TESTER")
    print("=" * 60)
    print()
    
    working_url = None
    results = []
    
    for url in MODAL_URLS:
        result = await test_url(url)
        results.append(result)
        
        if result["status"] == "success":
            print(f"   ✅ SUCCESS - HTTP {result['code']}")
            print(f"   📝 Response: {result['response']}")
            working_url = url
            break
        else:
            print(f"   ❌ FAILED - {result['status'].upper()} ({result['code']})")
            print(f"   📝 Details: {result['response']}")
        print()
    
    print("=" * 60)
    if working_url:
        print(f"✅ WORKING MODAL URL FOUND:")
        print(f"   {working_url}")
        print()
        print("📋 Add this to your .env file:")
        print(f'   MODAL_ENDPOINT_URL="{working_url}"')
    else:
        print("❌ NO WORKING MODAL URL FOUND")
        print()
        print("Possible causes:")
        print("  1. Modal service is not deployed")
        print("  2. Network/firewall issue")
        print("  3. Modal credits exhausted")
        print()
        print("To deploy Modal, run:")
        print("  modal deploy ml_training/modal_inference_optimized.py")
    print("=" * 60)
    
    return working_url

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
