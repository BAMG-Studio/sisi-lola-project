
import asyncio
import os
import sys

# Setup path
sys.path.append(os.getcwd())

from sisi_lola_api.app.services.api_manager import get_api_manager
from sisi_lola_api.app.services.unified_inference import get_inference_service, ResponseMode, Language

async def test_api_manager():
    print("--- Testing API Manager ---")
    manager = get_api_manager()
    key1 = manager.get_next_openai_key()
    print(f"Key 1: {key1[:10]}...")
    key2 = manager.get_next_openai_key()
    print(f"Key 2: {key2[:10]}...")
    
    client = manager.get_client("openai")
    print(f"Client headers: {client.headers.get('Authorization')[:15]}...")

async def test_inference():
    print("\n--- Testing Unified Inference ---")
    service = get_inference_service(load_brain=True, load_voice=False)
    
    print("Generating response...")
    response = await service.generate(
        message="Hello Sisi Lola! How are you?",
        mode=ResponseMode.TEXT_ONLY,
        language=Language.MIXED
    )
    
    print("\n--- Response ---")
    print(f"Text: {response.text}")
    print(f"Tags: {response.language_tags}")
    print(f"Mode: {response.mode}")
    print(f"Generation Time: {response.generation_time_ms}ms")

if __name__ == "__main__":
    asyncio.run(test_api_manager())
    asyncio.run(test_inference())
