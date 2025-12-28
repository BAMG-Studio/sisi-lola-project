# app/main.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables before importing any modules that depend on them
load_dotenv()

import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Routers
from sisi_lola_api.app.routers import enhanced_chat
from sisi_lola_api.app.routers import unified_chat
from sisi_lola_api.app.services.instagram_bot import router as instagram_router

# V2 Control Center Routers
from sisi_lola_api.app.routers import auth_router, control_center_router
from sisi_lola_api.app.routers import agent, images, videos, audio, auth, nigerian_models
from sisi_lola_api.app.database import init_db
from fastapi.templating import Jinja2Templates

from sisi_lola_api.app.config import SisiLolaDNA
from sisi_lola_api.app.services import auth_store

app = FastAPI(
    title="Sisi Lola OS API",
    description="""
# 🇳🇬 Sisi Lola - Nigerian AI Virtual Host

The Central Nervous System for the Sisi Lola Virtual Human.

## Features

### 🧠 Brain (Mistral-7B + LoRA)
- Fine-tuned on Nigerian languages and culture
- Supports English, Pidgin, Yoruba, Igbo, Hausa

### 💃 Personality Engine
- Confident, funny, charismatic Nigerian host
- Code-switching between languages
- Cultural authenticity

### 🎙️ Voice (XTTS-v2)
- Nigerian-accented voice synthesis
- Multiple language support
- Emotional expression

## Quick Start

1. **Chat Endpoint**: `POST /unified/chat`
2. **Voice Generation**: `POST /unified/voice`
3. **WebSocket**: `WS /unified/ws/chat`

## Web Demo

Visit the [interactive demo](/demo) to chat with Sisi Lola!
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==========================================
# ROUTER CONFIGURATION
# ==========================================

# 1. Core Chat & Intelligence (High Priority)
app.include_router(unified_chat.router)
app.include_router(enhanced_chat.router)

# 2. Control Center & Auth (V2 Infrastructure)
app.include_router(auth_router.router, prefix="/api/v2")
app.include_router(control_center_router.router, prefix="/api/v2")

# 3. Agent & Media Modules
app.include_router(agent.router, prefix="/agent", tags=["Agent Builder"])
app.include_router(images.router, prefix="/images", tags=["Image Generation"])
app.include_router(videos.router, prefix="/videos", tags=["Video Production"])
app.include_router(audio.router, prefix="/audio", tags=["Audio & Voice"])
app.include_router(nigerian_models.router)

# 4. Social & Integrations
app.include_router(instagram_router)

# 5. Content Vibes Production (New Africa Campaign)
from sisi_lola_api.app.routers import vibes_router
app.include_router(vibes_router.router)

# NEW: Unified multimodal chat
app.include_router(unified_chat.router)

# NEW: Enhanced chat with training data collection
app.include_router(enhanced_chat.router)

# NEW: Instagram bot webhook
app.include_router(instagram_router)

# NEW: Voice Dataset Curator for African language datasets
#app.include_router(curator.router)

# Mount static files for web demo
# Search for static dir relative to this file to be robust
current_dir = Path(__file__).parent.parent
static_dir = current_dir / "static"

# Fallback check if mounted incorrectly
if not static_dir.exists():
    # Try one level up if we're in a subdirectory of app
    static_dir = Path(__file__).parent.parent.parent / "sisi_lola_api" / "static"

if static_dir.exists():
    print(f"📁 Mounting static files from: {static_dir}")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    print(f"⚠️  Static directory not found at {static_dir}")

# Setup Dashboard Templates
templates = Jinja2Templates(directory="sisi_lola_api/app/templates")


@app.on_event("startup")
async def startup_init():
    """Initialize services on API startup"""
    # 1. Initialize Database
    print("💽 Initializing Sisi Lola Database...")
    auth_store.init_db()
    init_db()
    
    # 2. Preload Inference Services (Async)
    # Trigger loading in background to not block startup
    print("🚀 Preloading AI Models...")
    from sisi_lola_api.app.services.unified_inference import get_inference_service
    get_inference_service()  # Triggers init in constructor
    
    print("✨ Sisi Lola V2 is READY! 💃")
    auth_store.init_db()
    
    print("=" * 60)
    print("🚀 SISI LOLA API STARTING...")
    print("=" * 60)
    
    # Preload inference service for faster first response
    preload_models = os.getenv("PRELOAD_MODELS", "true").lower() == "true"
    
    if preload_models:
        print("\n📦 Preloading inference service...")
        try:
            from sisi_lola_api.app.services.unified_inference import get_inference_service
            # Load with voice disabled for faster startup (can be enabled per-request)
            service = get_inference_service(load_brain=False, load_voice=False)
            
            # Background preload MMS for Native Authenticity
            from sisi_lola_api.app.services.mms_service import mms_service
            import asyncio
            # We don't await this to avoid blocking startup, but it starts the download
            asyncio.create_task(asyncio.to_thread(mms_service.preload_common_models))
            
            print("✅ Inference service ready (using fine-tuned OpenAI models)")
        except Exception as e:
            print(f"⚠️  Inference preload skipped: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 SISI LOLA API READY!")
    print("=" * 60)
    print("📖 API Docs: http://localhost:8000/docs")
    print("💃 Web Demo: http://localhost:8000/demo")
    print("🗣️ Chat API: POST /unified/chat")
    print("\n🎯 OPTIMIZATIONS ACTIVE:")
    print("   • Fine-tuned OpenAI models (2-5s response)")
    print("   • Response caching for repeated queries")
    print("   • Bracket pollution cleanup")
    print("   • Paragraph formatting")
    print("=" * 60)

# CORS for frontend integration
allowed_origins = [
    origin.strip() 
    for origin in os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",") 
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard(request: Request):
    """Serve the Sisi Lola Command Center Dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/dashboard/status")
async def dashboard_status():
    """Get system health for the dashboard"""
    from .services.auth_store import get_social_token
    
    ig = get_social_token("instagram")
    tk = get_social_token("tiktok")
    yt = get_social_token("youtube")
    
    return {
        "auth": {
            "instagram": "ACTIVE" if ig else "MISSING",
            "tiktok": "ACTIVE" if tk else "MISSING",
            "youtube": "ACTIVE" if yt else "MISSING"
        },
        "gpu_nodes": "ONLINE (Modal)",
        "gist_radar": "IDLE"
    }


@app.post("/api/dashboard/gist-hunt")
async def trigger_gist_hunt(request: Request):
    """Trigger the Daily Gist Hunter manually with scope"""
    data = await request.json()
    scope = data.get("scope", "nigeria") # nigeria, africa, global
    
    from .services.gist_hunter import GistHunter
    hunter = GistHunter()
    briefing = await hunter.sync_radar_v2(scope)
    
    return {"success": True, "scope": scope, "message": f"Radar synced for {scope}"}


@app.post("/api/dashboard/render-video")
async def dashboard_render_video(request: Request):
    """Trigger a video render on Modal Wizard"""
    data = await request.json()
    prompt = data.get("prompt")
    model = data.get("model", "kling")
    
    # In a real scenario, this would call production_stub.py on Modal
    # For now, we simulate the request to the wizard
    return {
        "status": "QUEUED",
        "wizard": "Modal-SisiLolaProducer",
        "job_id": "vid_" + os.urandom(4).hex(),
        "estimated_time": "120s"
    }


@app.get("/api/dashboard/export-data")
async def export_training_data():
    """Package the logged interactions for GitHub Actions"""
    from .utils.data_forge import data_forge
    path = data_forge.prepare_github_action_export()
    
    # Read first 10 for preview
    preview = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 10: break
                preview.append(json.loads(line))
                
    return {
        "file": path,
        "entry_count": len(preview), # Mocking total for now
        "preview": preview
    }


@app.get("/demo", include_in_schema=False)
async def serve_demo(request: Request):
    """Serve the interactive public web demo"""
    return templates.TemplateResponse("demo.html", {"request": request})


@app.get("/")
async def root():
    access_key = os.getenv("KLINGAI_ACCESS_KEY")
    secret_key = os.getenv("KLINGAI_SECRET_KEY")
    return {
        "system_status": "ONLINE",
        "entity": SisiLolaDNA.NAME,
        "dna_version": "2.0 (Breathtaking/Voluptuous)",
        "demo_url": "/demo",
        "api_docs": "/docs",
        "endpoints": {
            "chat_v1": "/unified/chat",
            "chat_v2": "/v2/chat",  # Enhanced with training data
            "voice": "/unified/voice",
            "personality": "/unified/personality",
            "health": "/unified/health",
            "websocket": "/unified/ws/chat",
            "training_report": "/v2/training/report",
            "training_export": "/v2/training/export",
            "curator": "/curator",  # Voice Dataset Curator
            "curator_ingest": "/curator/ingest",
            "curator_coverage": "/curator/coverage",
        },
        "special_commands": {
            "/BAMG-STUDIO": "Developer mode for extensive responses",
            "/REPORT": "Generate training data report",
        },
        "models": {
            "brain": "sisilolalive/sisi-lola-brain-mistral",
            "voice": "sisilolalive/sisi-lola-voice-xtts",
            "personality": "sisilolalive/sisi-lola-personality"
        },
        "klingai_credentials_loaded": bool(access_key and secret_key),
        "openai_key_loaded": bool(os.getenv("OPENAI_API_KEY"))
    }
