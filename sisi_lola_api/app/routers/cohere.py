"""Cohere API endpoints for Sisi Lola"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.cohere_service import CohereService

router = APIRouter(prefix="/cohere", tags=["cohere"])
cohere_service = CohereService()


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    temperature: Optional[float] = 0.8


class ChatResponse(BaseModel):
    text: str
    generation_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Sisi Lola personality"""
    try:
        result = cohere_service.chat_with_personality(
            message=request.message,
            temperature=request.temperature
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate(request: ChatRequest):
    """Generate text response"""
    try:
        response = cohere_service.generate_multilingual(
            prompt=request.message,
            language=request.language,
            temperature=request.temperature
        )
        return {"text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
