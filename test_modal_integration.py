import asyncio
import sys
import time
from datetime import datetime
import requests

# Test Modal endpoint integration
def test_modal_endpoint():
    """Test the Modal inference endpoint directly"""
    print("\n" + "="*60)
    print("MODAL ENDPOINT INTEGRATION TEST")
    print("="*60)
    
    # Modal endpoint URL (update with your actual endpoint)
    modal_url = "https://bamg-studio--sisi-lola-modal-inference-model-generate.modal.run"
    
    test_prompts = [
        "Hello, how are you today?",
        "Tell me about yourself",
        "What's your favorite color?",
        "Can you help me with something?",
        "What do you think about AI?"
    ]
    
    results = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Test {i}/5] Prompt: '{prompt}'")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                modal_url,
                json={
                    "message": prompt,
                    "max_tokens": 256,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("text", "")
                print(f"✓ Success (Latency: {latency:.2f}s)")
                print(f"Response: {response_text}")
                
                results.append({
                    "test": i,
                    "prompt": prompt,
                    "response": response_text,
                    "latency": latency,
                    "status": "success"
                })
            else:
                print(f"✗ Failed: HTTP {response.status_code}")
                print(f"Error: {response.text}")
                results.append({
                    "test": i,
                    "prompt": prompt,
                    "error": response.text,
                    "latency": latency,
                    "status": "failed"
                })
                
        except Exception as e:
            end_time = time.time()
            latency = end_time - start_time
            print(f"✗ Exception: {str(e)}")
            results.append({
                "test": i,
                "prompt": prompt,
                "error": str(e),
                "latency": latency,
                "status": "error"
            })
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r["status"] == "success")
    total = len(results)
    avg_latency = sum(r["latency"] for r in results if r["status"] == "success") / successful if successful > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {(successful/total)*100:.1f}%")
    print(f"Average Latency: {avg_latency:.2f}s")
    print("="*60)
    
    return results

if __name__ == "__main__":
    test_modal_endpoint()
