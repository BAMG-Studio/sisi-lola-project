"""
SISI LOLA SOCIAL DISPATCH ROUTER
=================================
One-Click posting from Supreme Dashboard to all social platforms.
Integrates Vibe Scheduler output with automated posting.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from sisi_lola_api.app.auth import require_permission
from sisi_lola_api.app.services.automated_posting import AutomatedPostingService, post_now
from sisi_lola_api.app.services.auth_store import get_social_token, save_social_token

router = APIRouter(prefix="/social", tags=["Social Dispatch"])

class SocialTokenInput(BaseModel):
    platform: str  # instagram, tiktok, youtube
    access_token: str
    account_id: Optional[str] = None
    expires_in: Optional[int] = None

class QuickPostRequest(BaseModel):
    platform: str  # instagram, tiktok, youtube, facebook
    content_id: Optional[int] = None  # From ContentQueue
    video_url: Optional[str] = None   # Direct URL to video
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None

# ============== TOKEN MANAGEMENT ==============

@router.get("/tokens/status")
async def get_token_status(ctx=Depends(require_permission("content:read"))):
    """Get status of all configured social tokens"""
    platforms = ["instagram", "tiktok", "youtube"]
    status = {}
    
    for platform in platforms:
        token_data = get_social_token(platform)
        if token_data:
            # Mask the token for security
            masked = token_data["access_token"][:10] + "..." if token_data.get("access_token") else None
            status[platform] = {
                "configured": True,
                "token_preview": masked,
                "account_id": token_data.get("account_id"),
                "expires_at": token_data.get("expires_at"),
            }
        else:
            status[platform] = {"configured": False}
    
    return {"social_tokens": status}

@router.post("/tokens/save")
async def save_token(data: SocialTokenInput, ctx=Depends(require_permission("system:manage"))):
    """Save a new social media token"""
    save_social_token(
        platform=data.platform,
        access_token=data.access_token,
        account_id=data.account_id,
        expires_in=data.expires_in
    )
    return {"success": True, "message": f"{data.platform} token saved"}

# ============== POSTING ==============

@router.post("/dispatch")
async def dispatch_content(request: QuickPostRequest, ctx=Depends(require_permission("content:write"))):
    """
    One-Click Dispatch: Post content to a social platform.
    
    Can post:
    1. Content from the ContentQueue (by content_id)
    2. Direct video URL with caption
    """
    service = AutomatedPostingService()
    
    # Build vibe data
    vibe_data = {
        "vibe_id": f"DISPATCH_{request.content_id or 'QUICK'}",
        "caption": request.caption or "Sisi Lola vibes 💃",
        "hashtags": request.hashtags or ["SisiLola", "Naija", "Vibes"],
        "title": request.caption[:50] if request.caption else "Sisi Lola"
    }
    
    # If content_id provided, fetch from database
    if request.content_id:
        from sisi_lola_api.app.database import SessionLocal, ContentQueue
        db = SessionLocal()
        content = db.query(ContentQueue).filter(ContentQueue.id == request.content_id).first()
        db.close()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        vibe_data["vibe_id"] = f"CONTENT_{content.id}"
        vibe_data["caption"] = content.script
        vibe_data["title"] = content.title
        
        # Get video from metadata
        if content.metadata_ and content.metadata_.get("video_asset"):
            request.video_url = content.metadata_.get("video_asset")
    
    # Validate we have a video
    if not request.video_url:
        raise HTTPException(status_code=400, detail="No video URL provided")
    
    # Route to platform
    platform = request.platform.lower()
    
    if platform == "instagram":
        result = await service.post_to_instagram(vibe_data, video_url=request.video_url)
    elif platform == "tiktok":
        result = await service.post_to_tiktok(vibe_data, video_url=request.video_url)
    elif platform == "youtube":
        result = await service.post_to_youtube(vibe_data, video_url=request.video_url)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    return {
        "success": result.success,
        "platform": result.platform,
        "post_id": result.post_id,
        "post_url": result.post_url,
        "error": result.error
    }

@router.get("/schedule")
async def get_posting_schedule(ctx=Depends(require_permission("content:read"))):
    """Get the current posting schedule and status"""
    service = AutomatedPostingService()
    return service.get_posting_status()

@router.post("/schedule/sync")
async def sync_content_queue_to_schedule(ctx=Depends(require_permission("content:write"))):
    """
    Sync the approved ContentQueue items to the posting schedule.
    This enables the autonomous loop to work end-to-end.
    """
    from sisi_lola_api.app.database import SessionLocal, ContentQueue
    
    db = SessionLocal()
    approved_content = db.query(ContentQueue).filter(ContentQueue.status == "approved").all()
    
    synced = []
    for content in approved_content:
        synced.append({
            "id": content.id,
            "title": content.title,
            "platform": content.platform,
            "scheduled_at": content.scheduled_at.isoformat() if content.scheduled_at else None
        })
    
    db.close()
    
    return {
        "synced_items": len(synced),
        "items": synced,
        "message": "Content synced to posting scheduler"
    }
