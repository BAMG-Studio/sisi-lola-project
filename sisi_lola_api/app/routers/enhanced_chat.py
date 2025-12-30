"""
SISI LOLA ENHANCED CHAT ROUTER
==============================
Fast inference endpoint that uses Gemini 3 Pro directly.
Previously proxied to Modal, now uses direct inference for reliability.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging
import os
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced-chat", tags=["enhanced-chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.8
    # Additional fields to handle frontend sending them
    mode: Optional[str] = "multimodal"
    language: Optional[str] = "mixed"
    include_audio_base64: Optional[bool] = False


class ChatResponse(BaseModel):
    text: str
    latency_ms: float
    source: str = "gemini"
    # Fields to match frontend expectations
    language_tags: List[str] = Field(default=["EN", "NP"])
    audio_base64: Optional[str] = None
    generation_time_ms: float = 0


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Enhanced chat endpoint using Gemini 3 Pro directly.
    Provides fast, reliable Sisi Lola responses.
    """
    logger.info(f"[⚡ ENHANCED] Received chat request: {request.message[:50]}...")
    start_time = datetime.now()
    
    try:
        # Import the google creative service for Nano Banana (fast Gemini)
        from sisi_lola_api.app.services.google_creative_service import get_google_creative_service
        
        google_creative = get_google_creative_service()
        
        # Use Nano Banana (Gemini 2.5 Flash) for fast responses
        response_text = await google_creative.generate_nano_engagement(
            text=request.message,
            image_b64=None
        )
        
        latency = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"[✅ ENHANCED] Success in {latency:.2f}s")
        
        return ChatResponse(
            text=response_text,
            latency_ms=latency * 1000,
            generation_time_ms=latency * 1000,
            source="gemini-direct",
            language_tags=["EN", "NP"]  # English + Nigerian Pidgin
        )
        
    except Exception as e:
        latency = (datetime.now() - start_time).total_seconds()
        logger.error(f"[❌ ENHANCED] Error after {latency:.2f}s: {str(e)}")
        
        # Fallback error response in Sisi Lola style
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Omo! Brain dey busy: {str(e)[:100]}"
        )


@router.get("/health")
async def health():
    """Health check for enhanced chat endpoint"""
    return {
        "status": "healthy", 
        "inference_mode": "gemini-direct",
        "model": "gemini-2.5-flash (Nano Banana)"
    }
