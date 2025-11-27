#!/usr/bin/env python3
"""Test Cohere integration for Sisi Lola"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "sisi_lola_api"))

from dotenv import load_dotenv
from app.services.cohere_service import CohereService

load_dotenv("sisi_lola_api/.env")


def test_basic_generation():
    """Test basic text generation"""
    print("🧪 Testing basic generation...")
    
    service = CohereService()
    response = service.generate_response(
        "Introduce yourself as Sisi Lola",
        temperature=0.8
    )
    
    print(f"✅ Response: {response}\n")


def test_multilingual():
    """Test multilingual capabilities"""
    print("🧪 Testing multilingual generation...")
    
    service = CohereService()
    
    # English
    en_response = service.generate_multilingual(
        "What's your favorite thing about technology?",
        language="en"
    )
    print(f"🇬🇧 English: {en_response}\n")
    
    # Yoruba
    yo_response = service.generate_multilingual(
        "Tell me about yourself",
        language="yo"
    )
    print(f"🇳🇬 Yoruba: {yo_response}\n")


def test_personality_chat():
    """Test personality-driven chat"""
    print("🧪 Testing personality chat...")
    
    service = CohereService()
    
    messages = [
        "Hi Sisi Lola! What do you do?",
        "What makes you different from other AI assistants?",
        "Can you speak Yoruba?"
    ]
    
    conversation_history = []
    
    for msg in messages:
        print(f"👤 User: {msg}")
        
        result = service.chat_with_personality(
            msg,
            conversation_history=conversation_history
        )
        
        print(f"🤖 Sisi Lola: {result['text']}\n")
        
        # Update conversation history
        conversation_history.append({
            "role": "USER",
            "message": msg
        })
        conversation_history.append({
            "role": "CHATBOT",
            "message": result['text']
        })


def test_embeddings():
    """Test text embeddings"""
    print("🧪 Testing embeddings...")
    
    service = CohereService()
    
    texts = [
        "Sisi Lola is a virtual AI host",
        "Technology and African culture",
        "Multilingual content creation"
    ]
    
    embeddings = service.embed_text(texts)
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   Dimension: {len(embeddings[0])}\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("COHERE INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")
    
    # Check API key
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key or api_key == "your_cohere_key_here":
        print("❌ COHERE_API_KEY not configured in .env")
        return
    
    print(f"✅ API Key configured: {api_key[:10]}...\n")
    
    try:
        test_basic_generation()
        test_multilingual()
        test_personality_chat()
        test_embeddings()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
