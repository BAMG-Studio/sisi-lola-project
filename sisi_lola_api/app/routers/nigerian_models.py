"""
Sisi Lola Nigerian Models Service
Provides brain (LLM) and voice (TTS) endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(prefix="/nigerian", tags=["nigerian-models"])

class ChatRequest(BaseModel):
    message: str
    generate_audio: bool = False
    language: str = "yo"

class ChatResponse(BaseModel):
    text: str
    audio_url: str = None

@router.get("/health")
async def health():
    """Check model health"""
    models_enabled = os.getenv("NIGERIAN_MODELS_ENABLED", "false").lower() == "true"
    brain_path = os.getenv("NIGERIAN_BRAIN_ADAPTER", "")
    voice_path = os.getenv("NIGERIAN_VOICE_CHECKPOINT", "")
    
    return {
        "status": "configured" if models_enabled else "disabled",
        "brain_path": brain_path,
        "voice_path": voice_path,
        "models_enabled": models_enabled
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Sisi Lola using Nigerian models"""
    if os.getenv("NIGERIAN_MODELS_ENABLED", "false").lower() != "true":
        raise HTTPException(status_code=503, detail="Nigerian models not enabled")
    
    # Placeholder response until models are trained
    response_text = f"Bawo ni! I received your message: '{request.message}'. Nigerian models are configured but training is pending. Run train_nigerian_models.bat to train me!"
    
    return ChatResponse(
        text=response_text,
        audio_url=None
    )

@router.post("/generate-text")
async def generate_text(message: str, max_length: int = 256):
    """Generate text response only"""
    if os.getenv("NIGERIAN_MODELS_ENABLED", "false").lower() != "true":
        raise HTTPException(status_code=503, detail="Nigerian models not enabled")
    
    return {"text": f"Text generation ready. Message: {message}. Train models first!"}

@router.post("/generate-speech")
async def generate_speech(text: str, language: str = "yo"):
    """Generate speech from text"""
    if os.getenv("NIGERIAN_MODELS_ENABLED", "false").lower() != "true":
        raise HTTPException(status_code=503, detail="Nigerian models not enabled")
    
    return {"audio_url": None, "message": "Voice generation ready. Train models first!"}
