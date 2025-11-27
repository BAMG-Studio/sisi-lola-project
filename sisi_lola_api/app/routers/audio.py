import base64
import os
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx
from app.config import SisiLolaDNA
from app.dependencies.auth import require_api_key
from app.services import auth_store
from app.utils.voice_accent import rewrite_for_accent

router = APIRouter()

class AudioRequest(BaseModel):
    text: str
    voice_id: str = None  # Optional: Override default voice
    accent: str | None = "nigerian-yoruba"
    languages: list[str] | None = None

@router.get("/")
async def audio_status():
    return {"status": "Audio Module Online", "provider": "ElevenLabs", "voice_id": SisiLolaDNA.VOICE_ID}

@router.post("/speak")
async def generate_speech(request: AudioRequest, ctx=Depends(require_api_key)):
    """
    Generate speech using ElevenLabs with Sisi Lola's voice DNA.
    """
    try:
        auth_store.enforce_rate_limit(ctx, "/audio/speak")
    except Exception as limit_err:
        raise HTTPException(status_code=429, detail=str(limit_err))

    started = time.time()
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not elevenlabs_key:
        payload = {
            "status": "simulation",
            "text": request.text,
            "voice_id": SisiLolaDNA.VOICE_ID,
            "message": "Add ELEVENLABS_API_KEY to .env to generate real audio"
        }
        auth_store.log_usage(ctx, "/audio/speak", "simulation", duration_ms=int((time.time() - started) * 1000))
        return payload
    
    voice_id = request.voice_id if request.voice_id else SisiLolaDNA.VOICE_ID

    # Lightly localize the text for Nigerian/Yoruba cadence using Perplexity
    localized_text = await rewrite_for_accent(
        text=request.text,
        accent=request.accent or "nigerian-yoruba",
        languages=request.languages or []
    )
    
    try:
        # ElevenLabs Text-to-Speech endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        payload = {
            "text": localized_text,
            "model_id": "eleven_multilingual_v2",  # Best model for accents
            "voice_settings": SisiLolaDNA.VOICE_SETTINGS
        }
        
        headers = {
            "xi-api-key": elevenlabs_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Return audio as base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
        payload = {
            "status": "success",
            "text": request.text,
            "voice_id": voice_id,
            "audio_base64": audio_base64,
            "provider": "ElevenLabs",
            "input_text": request.text,
            "localized_text": localized_text,
            "accent": request.accent or "nigerian-yoruba"
        }
        auth_store.log_usage(ctx, "/audio/speak", "success", duration_ms=int((time.time() - started) * 1000))
        return payload
        
    except Exception as e:
        auth_store.log_usage(ctx, "/audio/speak", "error", duration_ms=int((time.time() - started) * 1000), error=str(e))
        raise HTTPException(status_code=500, detail=f"ElevenLabs speech generation failed: {str(e)}")
