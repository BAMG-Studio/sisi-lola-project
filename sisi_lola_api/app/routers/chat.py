# app/routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import SisiLolaDNA
import os
from openai import AsyncOpenAI

router = APIRouter()

# Initialize OpenAI Client (Ensure OPENAI_API_KEY is in your .env file)
# client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    user_input: str

@router.post("/speak")
async def chat_with_sisi(message: ChatMessage):
    """
    Chat with Sisi Lola. Uses her system persona via ChatGPT API.
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        # 1. Construct the conversation history with the DNA Persona
        messages = [
            {"role": "system", "content": SisiLolaDNA.SYSTEM_PERSONA},
            {"role": "user", "content": message.user_input}
        ]

        # 2. Call ChatGPT API (GPT-4o is recommended for personality)
        # If no API key is set, this will fail, so we wrap in try/except or use mock for now if needed.
        if not client.api_key:
             return {
                "speaker": "Sisi Lola",
                "response": "[SYSTEM: OpenAI API Key missing. Please add it to .env file] Ah, darling, I seem to have lost my voice connection!",
                "tone": "Error"
            }

        response = await client.chat.completions.create(
            model=SisiLolaDNA.CHAT_MODEL,  # Using best model from config
            messages=messages,
            temperature=0.7,  # Slightly creative for personality
            max_tokens=200,
            presence_penalty=0.3,  # Encourage diverse responses
            frequency_penalty=0.3  # Reduce repetition
        )

        sisi_reply = response.choices[0].message.content

        return {
            "speaker": "Sisi Lola",
            "response": sisi_reply,
            "tone": "Dynamic" # In a real app, we could ask GPT to analyze the tone too
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))