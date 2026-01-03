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

# ============== PUBLIC DEMO ENDPOINT (No Auth) ==============

class DemoRequest(BaseModel):
    message: str
    scenario: Optional[str] = "general"
    session_id: Optional[str] = None
    image_base64: Optional[str] = None

@router.post("/demo-chat")
async def demo_chat(request: DemoRequest):
    """
    Public demo endpoint for the demo page.
    Logs conversations for training refinement.
    """
    from sisi_lola_api.app.services.conversation_logger import log_conversation
    import time as t
    
    start_time = t.time()
    response_text = None
    error_msg = None
    
    try:
        response_text = await google_creative.generate_nano_engagement(
            text=request.message,
            image_b64=request.image_base64
        )
        return {"response": response_text, "scenario": request.scenario}
    except Exception as e:
        error_msg = str(e)[:200]
        response_text = f"Omo! The Supreme Grid dey busy right now. Try again small. ({str(e)[:50]})"
        return {"response": response_text, "error": True}
    finally:
        # Log conversation for training data
        response_time = int((t.time() - start_time) * 1000)
        try:
            log_conversation(
                user_message=request.message,
                sisi_response=response_text or "",
                session_id=request.session_id,
                scenario=request.scenario,
                response_time_ms=response_time,
                model_used="gemini-2.5-flash",
                error=error_msg,
                platform="demo"
            )
        except Exception:
            pass  # Don't let logging errors break the response

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
async def nano_banana_engagement(
    prompt: str = Body(..., embed=True), 
    image_reference: Optional[str] = Body(None, embed=True),
    ctx=Depends(require_api_key)
):
    """Rapid multimodal engagement using Gemini 1.5 Flash (Nano Banana)"""
    start_time = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/vibe/engagement")
        
        response_text = await google_creative.generate_nano_engagement(
            text=prompt,
            image_b64=image_reference
        )
        
        auth_store.log_usage(ctx, "/vibe/engagement", "success", duration_ms=int((time.time() - start_time)*1000))
        return {"response": response_text, "model": "Gemini 1.5 Flash (Nano Banana)"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== SINGSTRESS (Priority 2) ==============

class SingstressRequest(BaseModel):
    lyrics: str
    mood: Optional[str] = "party"
    genre: Optional[str] = "Afrobeats"
    vocal_style: Optional[str] = "singing"  # singing, rapping, speaking
    duration: Optional[int] = 30

@router.post("/singstress")
async def create_singstress_track(request: SingstressRequest, ctx=Depends(require_api_key)):
    """
    Create an original song with Sisi's voice over AI-generated beats.
    
    This combines:
    - Lyria instrumental generation
    - ElevenLabs/XTTS vocal synthesis
    - FFmpeg audio mixing
    """
    from sisi_lola_api.app.services.singstress_service import get_singstress_service
    
    start_time = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/vibe/singstress")
        
        service = get_singstress_service()
        result = await service.create_singstress_track(
            lyrics=request.lyrics,
            mood=request.mood,
            genre=request.genre,
            vocal_style=request.vocal_style,
            duration=request.duration
        )
        
        if result["success"]:
            auth_store.log_usage(ctx, "/vibe/singstress", "success", duration_ms=int((time.time() - start_time)*1000))
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== LIVE ENGAGEMENT (Priority 3) ==============

class CommentBatch(BaseModel):
    comments: list  # List of {"id": str, "text": str, "username": str}
    platform: Optional[str] = "instagram"
    context: Optional[str] = None  # e.g., "This is a video about Jollof Rice"

@router.post("/engage-batch")
async def batch_engagement(request: CommentBatch, ctx=Depends(require_api_key)):
    """
    Process a batch of social media comments and generate Sisi's responses.
    
    This enables real-time engagement:
    1. Receive batch of comments from webhook/polling
    2. Generate personalized responses for each
    3. Return ready-to-post replies
    """
    import asyncio
    
    start_time = time.time()
    auth_store.enforce_rate_limit(ctx, "/vibe/engage-batch")
    
    # Build context prompt
    context_hint = f"You're replying to comments on {request.platform}. "
    if request.context:
        context_hint += f"The video is about: {request.context}. "
    context_hint += "Be brief (under 100 chars), witty, and engaging. Use emojis. Stay in Sisi Lola character."
    
    async def process_comment(comment: dict) -> dict:
        try:
            prompt = f"[Reply to @{comment.get('username', 'fan')}]: {comment.get('text', '')}"
            response = await google_creative.generate_nano_engagement(
                text=f"{context_hint}\n\nComment: {prompt}"
            )
            return {
                "comment_id": comment.get("id"),
                "username": comment.get("username"),
                "original": comment.get("text"),
                "reply": response[:150] if response else "💃",  # Instagram comment limit
                "success": True
            }
        except Exception as e:
            return {
                "comment_id": comment.get("id"),
                "success": False,
                "error": str(e)
            }
    
    # Process all comments concurrently
    results = await asyncio.gather(*[process_comment(c) for c in request.comments])
    
    auth_store.log_usage(
        ctx, "/vibe/engage-batch", "success", 
        duration_ms=int((time.time() - start_time)*1000),
        count=len(request.comments)
    )
    
    return {
        "processed": len(results),
        "replies": results,
        "platform": request.platform
    }
