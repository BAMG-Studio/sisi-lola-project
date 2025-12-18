import requests
import time
import json
from datetime import datetime

# Test prompts for Sisi Lola chat
test_prompts = [
    "Hello Sisi Lola, how are you doing today?",
    "Tell me about yourself and what makes you special",
    "What's your favorite thing about Nigerian culture?",
    "Can you help me learn some Yoruba phrases?",
    "What do you think about technology and AI?",
    "Tell me a story about Lagos",
    "What advice would you give to someone visiting Nigeria?",
    "How do you stay positive and motivated?",
    "What are your thoughts on African innovation?",
    "Can you recommend some Nigerian music?"
]

print("\n" + "="*70)
print("SISI LOLA CHAT - 10 RESPONSE TEST")
print("="*70)
print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

# Modal endpoint URL
modal_url = "https://bamg-studio--sisi-lola-modal-inference-model-generate.modal.run"

results = []
total_start_time = time.time()

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n[Test {i}/10]")
    print(f"Prompt: '{prompt}'")
    print("-" * 70)
    
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
            print(f"\u2713 Success (Latency: {latency:.2f}s)")
            print(f"Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
            
            results.append({
                "test": i,
                "prompt": prompt,
                "response": response_text,
                "latency": latency,
                "status": "success"
            })
        else:
            print(f"\u2717 Failed: HTTP {response.status_code}")
            print(f"Error: {response.text[:200]}")
            results.append({
                "test": i,
                "prompt": prompt,
                "error": response.text,
                "status_code": response.status_code,
                "latency": latency,
                "status": "failed"
            })
            
    except Exception as e:
        end_time = time.time()
        latency = end_time - start_time
        print(f"\u2717 Exception: {str(e)}")
        results.append({
            "test": i,
            "prompt": prompt,
            "error": str(e),
            "latency": latency,
            "status": "error"
        })
    
    # Small delay between requests
    if i < len(test_prompts):
        time.sleep(1)

total_end_time = time.time()
total_duration = total_end_time - total_start_time

# Print summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

successful = sum(1 for r in results if r["status"] == "success")
failed = sum(1 for r in results if r["status"] in ["failed", "error"])
total = len(results)
avg_latency = sum(r["latency"] for r in results if r["status"] == "success") / successful if successful > 0 else 0

print(f"Total Tests: {total}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Success Rate: {(successful/total)*100:.1f}%")
print(f"Average Latency: {avg_latency:.2f}s")
print(f"Total Duration: {total_duration:.2f}s")
print("="*70)

# Save results to file
with open('test_results_sisi_lola_chat.json', 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total)*100:.1f}%",
            "avg_latency": f"{avg_latency:.2f}s",
            "total_duration": f"{total_duration:.2f}s"
        },
        "results": results
    }, f, indent=2)

print(f"\nResults saved to: test_results_sisi_lola_chat.json")
