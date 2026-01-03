#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                         SISI LOLA API SERVER
═══════════════════════════════════════════════════════════════════════════════
                 Unified REST API for All System Operations
═══════════════════════════════════════════════════════════════════════════════

Endpoints:
- /api/v1/chat - Chat with Sisi Lola
- /api/v1/generate/voice - Generate voice
- /api/v1/generate/video - Generate video
- /api/v1/generate/image - Generate image
- /api/v1/training/trigger - Trigger training
- /api/v1/feedback - Submit feedback
- /api/v1/health - System health
- /api/v1/stats - System statistics
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator import SisiLolaOrchestrator, EventType, SystemEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    dialect: str = Field(default="pidgin", description="Preferred dialect")
    dialect_intensity: int = Field(default=70, ge=0, le=100)
    response_mode: str = Field(default="text", description="text, voice, or video")
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    session_id: str
    cost: float = 0.0


class GenerateVoiceRequest(BaseModel):
    """Voice generation request."""
    text: str = Field(..., description="Text to synthesize")
    voice_id: str = Field(default="sisi_lola_v1")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    emotion: str = Field(default="neutral")


class GenerateVideoRequest(BaseModel):
    """Video generation request."""
    audio_url: Optional[str] = None
    text: Optional[str] = None
    duration_seconds: int = Field(default=10, ge=1, le=60)
    aspect_ratio: str = Field(default="9:16")


class GenerateImageRequest(BaseModel):
    """Image generation request."""
    prompt: str = Field(..., description="Image prompt")
    style: str = Field(default="photorealistic")
    aspect_ratio: str = Field(default="1:1")
    seed: int = Field(default=45822, description="Seed for character consistency")


class TrainingTriggerRequest(BaseModel):
    """Training trigger request."""
    training_type: str = Field(..., description="voice, vision, or language")
    dataset_ids: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    """Feedback submission request."""
    prediction_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str = Field(default="rating")
    comment: Optional[str] = None
    is_nigerian: bool = Field(default=False)


class HealthResponse(BaseModel):
    """Health check response."""
    overall_status: str
    components: Dict[str, Any]
    daily_cost: float
    cost_limit: float


# ═══════════════════════════════════════════════════════════════════════════════
# Application Setup
# ═══════════════════════════════════════════════════════════════════════════════

# Global orchestrator instance
orchestrator: Optional[SisiLolaOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator
    
    # Startup
    logger.info("Starting Sisi Lola API Server...")
    orchestrator = SisiLolaOrchestrator()
    orchestrator.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sisi Lola API Server...")
    if orchestrator:
        orchestrator.stop()


app = FastAPI(
    title="Sisi Lola API",
    description="Nigerian AI Assistant API - Voice, Video, Image, and Chat",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# Health & Status Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    health = orchestrator.get_system_health()
    return HealthResponse(**health)


@app.get("/api/v1/stats")
async def get_statistics():
    """Get system statistics."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    return orchestrator.get_statistics()


@app.get("/api/v1/cost")
async def get_cost_status():
    """Get current cost status."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    return {
        "daily_cost": orchestrator.daily_cost,
        "cost_limit": orchestrator.cost_limit,
        "remaining": orchestrator.cost_limit - orchestrator.daily_cost,
        "utilization_percent": (orchestrator.daily_cost / orchestrator.cost_limit) * 100
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Chat Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with Sisi Lola.
    
    Supports text, voice, and video responses based on response_mode.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    try:
        # Generate text response
        result = await orchestrator.generate_content(
            modality='brain',
            prompt=request.message,
            dialect=request.dialect,
            dialect_intensity=request.dialect_intensity
        )
        
        if result['status'] != 'success':
            raise HTTPException(status_code=500, detail=result.get('error', 'Generation failed'))
        
        response_text = result['result'].get('text', '')
        audio_url = None
        video_url = None
        total_cost = result['result'].get('cost', 0)
        
        # Generate voice if requested
        if request.response_mode in ['voice', 'video']:
            voice_result = await orchestrator.generate_content(
                modality='voice',
                prompt=response_text
            )
            if voice_result['status'] == 'success':
                audio_url = voice_result['result'].get('audio_url')
                total_cost += voice_result['result'].get('cost', 0)
        
        # Generate video if requested
        if request.response_mode == 'video' and audio_url:
            video_result = await orchestrator.generate_content(
                modality='video',
                prompt=audio_url,
                duration=10
            )
            if video_result['status'] == 'success':
                video_url = video_result['result'].get('video_url')
                total_cost += video_result['result'].get('cost', 0)
        
        return ChatResponse(
            response=response_text,
            audio_url=audio_url,
            video_url=video_url,
            session_id=session_id,
            cost=total_cost
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Generation Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/generate/voice")
async def generate_voice(request: GenerateVoiceRequest):
    """Generate voice audio from text."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    result = await orchestrator.generate_content(
        modality='voice',
        prompt=request.text,
        voice_id=request.voice_id,
        speed=request.speed,
        emotion=request.emotion
    )
    
    if result['status'] != 'success':
        raise HTTPException(status_code=500, detail=result.get('error', 'Voice generation failed'))
    
    return result['result']


@app.post("/api/v1/generate/video")
async def generate_video(request: GenerateVideoRequest):
    """Generate video with Sisi Lola."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Need either audio_url or text
    if not request.audio_url and not request.text:
        raise HTTPException(status_code=400, detail="Either audio_url or text is required")
    
    # If text provided, generate audio first
    audio_url = request.audio_url
    if not audio_url and request.text:
        voice_result = await orchestrator.generate_content(
            modality='voice',
            prompt=request.text
        )
        if voice_result['status'] == 'success':
            audio_url = voice_result['result'].get('audio_url')
    
    result = await orchestrator.generate_content(
        modality='video',
        prompt=audio_url,
        duration=request.duration_seconds,
        aspect_ratio=request.aspect_ratio
    )
    
    if result['status'] != 'success':
        raise HTTPException(status_code=500, detail=result.get('error', 'Video generation failed'))
    
    return result['result']


@app.post("/api/v1/generate/image")
async def generate_image(request: GenerateImageRequest):
    """Generate image of Sisi Lola."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    result = await orchestrator.generate_content(
        modality='image',
        prompt=request.prompt,
        style=request.style,
        aspect_ratio=request.aspect_ratio,
        seed=request.seed  # Use consistent seed for character
    )
    
    if result['status'] != 'success':
        raise HTTPException(status_code=500, detail=result.get('error', 'Image generation failed'))
    
    return result['result']


# ═══════════════════════════════════════════════════════════════════════════════
# Training Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/training/trigger")
async def trigger_training(request: TrainingTriggerRequest, background_tasks: BackgroundTasks):
    """Trigger a training job on Modal."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Validate training type
    valid_types = ['voice', 'vision', 'language']
    if request.training_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid training_type. Must be one of: {valid_types}")
    
    result = await orchestrator.trigger_training(
        training_type=request.training_type,
        dataset_ids=request.dataset_ids,
        config=request.config
    )
    
    if result['status'] != 'success':
        raise HTTPException(status_code=500, detail=result.get('error', 'Training trigger failed'))
    
    return {
        "status": "triggered",
        "job_id": result.get('job_id'),
        "training_type": request.training_type
    }


@app.get("/api/v1/training/status/{job_id}")
async def get_training_status(job_id: str):
    """Get training job status."""
    # This would query Modal for job status
    return {
        "job_id": job_id,
        "status": "running",
        "progress": 45,
        "eta_minutes": 30
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Feedback Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a prediction."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Publish feedback event
    orchestrator.event_bus.publish(SystemEvent(
        event_type=EventType.FEEDBACK_RECEIVED,
        payload={
            'prediction_id': request.prediction_id,
            'rating': request.rating,
            'feedback_type': request.feedback_type,
            'comment': request.comment,
            'is_nigerian': request.is_nigerian
        },
        source='api'
    ))
    
    return {
        "status": "received",
        "prediction_id": request.prediction_id,
        "bonus_applied": request.is_nigerian  # Nigerian content gets bonus
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metadata Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/assets")
async def list_assets(
    asset_type: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    is_nigerian: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List assets from metadata store."""
    if not orchestrator or not orchestrator.metadata_store:
        raise HTTPException(status_code=503, detail="Metadata store not available")
    
    from metadata_system import AssetType, NigerianLanguage
    
    # Parse filters
    type_filter = AssetType(asset_type) if asset_type else None
    lang_filter = NigerianLanguage(language) if language else None
    
    assets = orchestrator.metadata_store.search_assets(
        asset_type=type_filter,
        language=lang_filter,
        is_nigerian=is_nigerian,
        limit=limit,
        offset=offset
    )
    
    return {
        "assets": [a.to_dict() for a in assets],
        "count": len(assets),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/v1/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Get asset details."""
    if not orchestrator or not orchestrator.metadata_store:
        raise HTTPException(status_code=503, detail="Metadata store not available")
    
    asset = orchestrator.metadata_store.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset.to_dict()


@app.get("/api/v1/assets/{asset_id}/lineage")
async def get_asset_lineage(asset_id: str):
    """Get asset lineage."""
    if not orchestrator or not orchestrator.lineage_tracker:
        raise HTTPException(status_code=503, detail="Lineage tracker not available")
    
    return orchestrator.lineage_tracker.impact_analysis(asset_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Run the API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola API Server")
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--reload', action='store_true')
    
    args = parser.parse_args()
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
