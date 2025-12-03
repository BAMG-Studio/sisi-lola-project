#!/usr/bin/env python3
"""Test Nigerian models API integration"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing Nigerian Models API Integration\n")

# Test 1: Health check
print("[1/3] Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/nigerian/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
except Exception as e:
    print(f"Error: {e}\n")

# Test 2: Chat endpoint
print("[2/3] Testing chat endpoint...")
try:
    payload = {
        "message": "Bawo ni? Tell me about Lagos",
        "generate_audio": False,
        "language": "yo"
    }
    response = requests.post(f"{BASE_URL}/nigerian/chat", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
except Exception as e:
    print(f"Error: {e}\n")

# Test 3: Text generation
print("[3/3] Testing text generation...")
try:
    response = requests.post(
        f"{BASE_URL}/nigerian/generate-text",
        params={"message": "Wetin be your favorite food?"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
except Exception as e:
    print(f"Error: {e}\n")

print("=" * 60)
print("API Integration Test Complete")
print("=" * 60)
print("\nNote: Full functionality requires trained models.")
print("Run: train_nigerian_models.bat to train models.")
