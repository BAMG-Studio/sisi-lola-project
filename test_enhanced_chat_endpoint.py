import requests
import time

# Test the enhanced chat endpoint
print("Testing Enhanced Chat Endpoint with Modal Integration\n" + "="*60)

test_messages = [
    "Hello, how are you?",
    "Tell me about Nigerian culture",
    "What's your favorite food?"
]

for i, message in enumerate(test_messages, 1):
    print(f"\n[Test {i}] Message: '{message}'")
    print("-" * 60)
    
    start = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/enhanced-chat/chat",
            json={"message": message},
            timeout=30
        )
        
        latency = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success (Total: {latency:.2f}s, API: {data.get('latency', 0):.2f}s)")
            print(f"Response: {data.get('text', '')[:150]}...")
            print(f"Source: {data.get('source', 'unknown')}")
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    time.sleep(0.5)

print("\n" + "="*60)
print("Enhanced Chat Endpoint Test Complete!")
