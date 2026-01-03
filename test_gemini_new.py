
import os
import asyncio
from google import genai
from google.genai import types

async def test_gemini():
    api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    if not api_key:
        print("No API key found")
        return
        
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents="Say hello in Nigerian Pidgin",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="LOW"),
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
