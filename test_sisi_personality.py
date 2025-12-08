#!/usr/bin/env python3
"""
Quick test script for Sisi Lola's personality system
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_personality():
    """Test personality endpoint"""
    print("🎭 Testing Personality Configuration...")
    response = requests.get(f"{BASE_URL}/chat/personality")
    print(json.dumps(response.json(), indent=2))
    print()

def test_chat(message):
    """Test chat with personality"""
    print(f"💬 User: {message}")
    response = requests.post(
        f"{BASE_URL}/chat/chat",
        json={"message": message}
    )
    data = response.json()
    print(f"👑 Sisi: {data['response']}")
    print(f"   Humor: {data['humor_level']}/10 | Charisma: {data['charisma_level']}/10")
    print()

def main():
    print("🚀 SISI LOLA PERSONALITY TEST")
    print("=" * 60)
    print()
    
    # Test personality config
    test_personality()
    
    # Test various scenarios
    test_scenarios = [
        "Hey Sisi, how are you?",
        "I'm nervous about my job interview tomorrow",
        "What should I wear to a wedding?",
        "Tell me about Nigerian culture",
        "I'm feeling down today"
    ]
    
    for scenario in test_scenarios:
        test_chat(scenario)
    
    print("✅ Test complete! Sisi Lola is FUNNY and CHARISMATIC!")

if __name__ == "__main__":
    main()
