from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import SisiLolaDNA
from app.services.personality_engine import personality_engine
import openai
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: dict = None

class ChatResponse(BaseModel):
    response: str
    personality_applied: bool
    humor_level: float
    charisma_level: float

@router.post("/chat", response_model=ChatResponse)
async def chat_with_sisi(request: ChatRequest):
    """
    Chat with Sisi Lola - now with humor and charisma!
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    openai.api_key = openai_key
    
    try:
        # Get enhanced system prompt with personality
        system_prompt = personality_engine.get_system_prompt()
        
        # Create chat completion with personality
        response = openai.ChatCompletion.create(
            model=SisiLolaDNA.CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.8,  # Higher for more creative/funny responses
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Add personality flair
        enhanced_response = personality_engine.add_personality_flair(ai_response)
        
        return ChatResponse(
            response=enhanced_response,
            personality_applied=True,
            humor_level=personality_engine.personality['humor'],
            charisma_level=personality_engine.personality['charisma']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/personality")
async def get_personality_info():
    """Get current personality configuration"""
    return {
        "personality_core": personality_engine.personality,
        "communication_style": personality_engine.style,
        "response_patterns": personality_engine.patterns,
        "status": "Sisi Lola is FUNNY and CHARISMATIC!"
    }
