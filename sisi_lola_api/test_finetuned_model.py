#!/usr/bin/env python3
"""
Test Sisi Lola Fine-Tuned Model Integration

Quick test to verify the fine-tuned model works with the API.
"""

import os
import sys

# Add the API path
sys.path.insert(0, '/mnt/c/Users/POK28/Dropbox/Sisi_Lola/sisi_lola_api')

from dotenv import load_dotenv
load_dotenv('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/sisi_lola_api/.env')

from openai import OpenAI
from sisi_lola_api.app.config import SisiLolaDNA

def test_model():
    print("=" * 60)
    print("🌍 SISI LOLA - FINE-TUNED MODEL TEST")
    print("=" * 60)
    
    # Check config
    print(f"\n📋 Config Check:")
    print(f"   Fine-tuned Model: {SisiLolaDNA.CHAT_MODEL_FINETUNED}")
    print(f"   Fallback Model: {SisiLolaDNA.CHAT_MODEL_FALLBACK}")
    print(f"   Default Model: {SisiLolaDNA.CHAT_MODEL}")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OPENAI_API_KEY not found in .env")
        return False
    print(f"   API Key: {api_key[:20]}...")
    
    # Test fine-tuned model
    print(f"\n🧪 Testing Fine-Tuned Model...")
    client = OpenAI(api_key=api_key)
    
    test_prompts = [
        "Say hello to your audience",
        "Tell me about jollof rice",
        "What does 'e kaabo' mean?",
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt}")
        try:
            response = client.chat.completions.create(
                model=SisiLolaDNA.CHAT_MODEL_FINETUNED,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            print(f"🤖 Response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_model()
    sys.exit(0 if success else 1)
