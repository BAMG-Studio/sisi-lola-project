"""
SISI LOLA VIBE ROUTER
======================
API endpoints for vibe content production and management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/vibes", tags=["Vibes"])


class VibeProductionRequest(BaseModel):
    vibe_id: str


class BatchProductionRequest(BaseModel):
    vibe_ids: Optional[List[str]] = None


class VibeResponse(BaseModel):
    success: bool
    vibe_id: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    audio_path: Optional[str] = None
    script: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    error: Optional[str] = None


@router.get("/list")
async def list_vibes():
    """
    List all available vibes from the current batch.
    """
    from sisi_lola_api.app.services.vibe_production import VibeProductionService
    
    service = VibeProductionService()
    vibes = service.vibes_data.get("vibes", [])
    
    return {
        "batch_id": service.vibes_data.get("batch_id"),
        "batch_name": service.vibes_data.get("batch_name"),
        "total_vibes": len(vibes),
        "vibes": [
            {
                "vibe_id": v["vibe_id"],
                "title": v["title"],
                "duration_seconds": v["duration_seconds"],
                "platforms": v["platforms"],
                "scheduled_date": v["scheduled_date"],
                "viral_potential": v.get("viral_potential", "unknown"),
                "status": v.get("status", "pending")
            }
            for v in vibes
        ]
    }


@router.get("/next")
async def get_next_scheduled():
    """
    Get the next scheduled vibe for posting.
    """
    from sisi_lola_api.app.services.vibe_production import VibeProductionService
    
    service = VibeProductionService()
    next_vibe = service.get_next_scheduled_vibe()
    
    if next_vibe:
        return {
            "has_upcoming": True,
            "scheduled": next_vibe["scheduled"].isoformat(),
            "platform": next_vibe["platform"],
            "vibe": {
                "vibe_id": next_vibe["vibe"]["vibe_id"],
                "title": next_vibe["vibe"]["title"],
                "caption": next_vibe["vibe"]["caption"],
                "hashtags": next_vibe["vibe"]["hashtags"]
            }
        }
    
    return {"has_upcoming": False, "message": "No upcoming vibes scheduled"}


@router.get("/{vibe_id}")
async def get_vibe(vibe_id: str):
    """
    Get full details of a specific vibe.
    """
    from sisi_lola_api.app.services.vibe_production import VibeProductionService
    
    service = VibeProductionService()
    vibe = service.get_vibe(vibe_id)
    
    if not vibe:
        raise HTTPException(status_code=404, detail=f"Vibe {vibe_id} not found")
    
    return vibe


@router.post("/produce", response_model=VibeResponse)
async def produce_vibe(request: VibeProductionRequest):
    """
    Produce a single vibe (generate voice audio + assets).
    Requires ELEVENLABS_API_KEY in environment.
    """
    from sisi_lola_api.app.services.vibe_production import produce_vibe_for_api
    
    result = await produce_vibe_for_api(request.vibe_id)
    return VibeResponse(**result)


@router.post("/produce/batch")
async def produce_batch(request: BatchProductionRequest, background_tasks: BackgroundTasks):
    """
    Produce multiple vibes in batch (background task).
    If vibe_ids is None, produces all vibes.
    """
    from sisi_lola_api.app.services.vibe_production import VibeProductionService
    
    service = VibeProductionService()
    
    # Get vibe IDs to produce
    if request.vibe_ids:
        vibe_ids = request.vibe_ids
    else:
        vibe_ids = [v["vibe_id"] for v in service.vibes_data.get("vibes", [])]
    
    # Queue background production
    async def run_batch():
        await service.produce_batch(vibe_ids)
    
    background_tasks.add_task(lambda: __import__('asyncio').run(run_batch()))
    
    return {
        "status": "queued",
        "vibes_to_produce": len(vibe_ids),
        "vibe_ids": vibe_ids,
        "message": "Batch production started in background. Check /vibes/status for progress."
    }


@router.get("/calendar/week/{week_number}")
async def get_week_calendar(week_number: int):
    """
    Get the deployment calendar for a specific week (1, 2, or 3).
    """
    from sisi_lola_api.app.services.vibe_production import VibeProductionService
    
    service = VibeProductionService()
    calendar = service.get_deployment_calendar()
    
    week_key = f"week_{week_number}"
    if week_key not in calendar:
        raise HTTPException(status_code=404, detail=f"Week {week_number} not found in calendar")
    
    week_data = calendar[week_key]
    
    # Enrich with vibe details
    enriched = []
    for date_str, vibe_info in week_data.items():
        vibe = service.get_vibe(vibe_info["vibe_id"])
        enriched.append({
            "date": date_str,
            "time_wat": vibe_info.get("time_wat", "00:00"),
            "primary_platform": vibe_info.get("primary_platform"),
            "vibe_id": vibe_info["vibe_id"],
            "title": vibe.get("title") if vibe else "Unknown",
            "duration_seconds": vibe.get("duration_seconds") if vibe else 0
        })
    
    return {
        "week": week_number,
        "schedule": enriched
    }


@router.get("/metrics/targets")
async def get_success_metrics():
    """
    Get the target success metrics for the vibe campaign.
    """
    from sisi_lola_api.app.services.vibe_production import VibeProductionService
    
    service = VibeProductionService()
    
    return {
        "success_metrics": service.vibes_data.get("success_metrics", {}),
        "production_specs": service.vibes_data.get("production_specs", {}),
        "voice_config": service.vibes_data.get("voice_config", {})
    }
