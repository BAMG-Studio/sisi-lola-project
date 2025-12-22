from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from sisi_lola_api.app.config import SisiLolaDNA
from sisi_lola_api.app.services.personality_engine import personality_engine
from openai import OpenAI
import os

router = APIRouter()

# Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")
    return OpenAI(api_key=api_key)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    context: dict = None
    conversation_history: Optional[List[ChatMessage]] = None
    use_finetuned: bool = Field(default=True, description="Use fine-tuned Sisi Lola model")

class ChatResponse(BaseModel):
    response: str
    personality_applied: bool
    humor_level: float
    charisma_level: float
    model_used: str = ""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_sisi(request: ChatRequest):
    """
    Chat with Sisi Lola - Fine-tuned Nigerian AI Ambassador!
    
    Uses the custom fine-tuned model trained on authentic Sisi Lola content
    with Nigerian Pidgin English, cultural knowledge, and personality.
    
    Set use_finetuned=False to use GPT-4o fallback for complex reasoning.
    """
    try:
        client = get_openai_client()
        
        # Select model based on request
        model = SisiLolaDNA.CHAT_MODEL_FINETUNED if request.use_finetuned else SisiLolaDNA.CHAT_MODEL_FALLBACK
        
        # Get enhanced system prompt with personality
        system_prompt = personality_engine.get_system_prompt()
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if request.conversation_history:
            for msg in request.conversation_history:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Create chat completion with fine-tuned model
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.8,  # Higher for more creative/funny responses
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Add personality flair (lighter touch for fine-tuned model)
        if request.use_finetuned:
            # Fine-tuned model already has personality baked in
            enhanced_response = ai_response
        else:
            enhanced_response = personality_engine.add_personality_flair(ai_response)
        
        return ChatResponse(
            response=enhanced_response,
            personality_applied=True,
            humor_level=personality_engine.personality['humor'],
            charisma_level=personality_engine.personality['charisma'],
            model_used=model
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
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
