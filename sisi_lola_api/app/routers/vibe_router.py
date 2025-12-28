"""
SISI LOLA SUPREME VIBE ROUTER
==============================
High-tier content generation endpoints using Google's Supreme AI assets:
- Veo 3.1: Short Vibe Videos
- Lyria: Vibe Music
- Imagen 4: Photorealistic Snapshots
- Nano Banana: Rapid Multimodal Engagement
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time

from sisi_lola_api.app.dependencies.auth import require_api_key
from sisi_lola_api.app.services.google_creative_service import get_google_creative_service
from sisi_lola_api.app.services import auth_store

router = APIRouter(prefix="/vibe", tags=["Supreme Vibe Generation"])
google_creative = get_google_creative_service()

class VibeRequest(BaseModel):
    prompt: str
    scenario: Optional[str] = "Lagos Lifestyle"
    duration: Optional[int] = 8
    image_reference: Optional[str] = None # Base64

@router.get("/status")
async def vibe_status():
    """Check the status of Supreme Google AI assets"""
    return {
        "status": "Supreme Vibe Module Operational",
        "assets": {
            "video": "Veo 3.1",
            "music": "Lyria RealTime",
            "image": "Imagen 4",
            "fast_chat": "Nano Banana (Gemini 2.5 Flash)"
        }
    }

@router.post("/video")
async def generate_vibe_video(request: VibeRequest, ctx=Depends(require_api_key)):
    """Generate 8-second cinematic shorts with native audio using Veo 3.1"""
    start_time = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/vibe/video")
        
        result = await google_creative.generate_vibe_video(
            prompt=request.prompt, 
            reference_image_b64=request.image_reference
        )
        
        if result["success"]:
            auth_store.log_usage(ctx, "/vibe/video", "success", duration_ms=int((time.time() - start_time)*1000))
            return result
        else:
            auth_store.log_usage(ctx, "/vibe/video", "error", error=result.get("error"))
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music")
async def generate_vibe_music(request: VibeRequest, ctx=Depends(require_api_key)):
    """Create unique Afrobeats-inspired music vibes using Lyria"""
    start_time = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/vibe/music")
        
        result = await google_creative.generate_vibe_music(
            mood_prompt=request.prompt,
            duration=request.duration or 15
        )
        
        if result["success"]:
            auth_store.log_usage(ctx, "/vibe/music", "success", duration_ms=int((time.time() - start_time)*1000))
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/snapshot")
async def generate_vibe_snapshot(scene: str = Body(..., embed=True), ctx=Depends(require_api_key)):
    """Generate high-fidelity photorealistic branding assets using Imagen 4"""
    start_time = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/vibe/snapshot")
        
        result = await google_creative.generate_supreme_snapshot(scene=scene)
        
        if result["success"]:
            auth_store.log_usage(ctx, "/vibe/snapshot", "success", duration_ms=int((time.time() - start_time)*1000))
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/engagement")
async def nano_banana_engagement(message: str = Body(..., embed=True), ctx=Depends(require_api_key)):
    """Rapid multimodal engagement using Gemini 2.5 Flash (Nano Banana)"""
    start_time = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/vibe/engagement")
        
        response_text = await google_creative.generate_nano_engagement(text=message)
        
        auth_store.log_usage(ctx, "/vibe/engagement", "success", duration_ms=int((time.time() - start_time)*1000))
        return {"response": response_text, "model": "Gemini 2.5 Flash (Nano Banana)"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
