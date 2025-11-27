import asyncio
import os
from dotenv import load_dotenv
from app.utils.perplexity import enhance_prompt_with_perplexity

load_dotenv()

async def main():
    print("Testing Perplexity API...")
    api_key = os.getenv("PERPLEXITY_API_KEY")
import asyncio
import os
from dotenv import load_dotenv
from app.utils.perplexity import enhance_prompt_with_perplexity

load_dotenv()

async def main():
    print("Testing Perplexity API via function...")
    try:
        prompt = await enhance_prompt_with_perplexity(
            scenario="Drinking coffee in a cafe",
            modality="image"
        )
        print(f"Success! Prompt:\n{prompt[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
