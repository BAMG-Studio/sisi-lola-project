# =============================================================================
# SISI LOLA API - MAIN APPLICATION
# =============================================================================
# The Central Nervous System for the Sisi Lola Virtual Human
# Version: 2.1.0 (Supreme)
# Last Cleaned: 2025-12-29
# =============================================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the correct .env file FIRST
# The .env is in sisi_lola_api/.env (same level as this app folder)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"📂 Loading .env from: {env_path}")

# Verify API keys loaded
gemini_key = os.getenv("GEMINI_API_KEY", "")
openai_key = os.getenv("OPENAI_API_KEY", "")
cohere_key = os.getenv("COHERE_API_KEY", "")

print(f"🔑 Keys Loaded: Gemini={'YES' if gemini_key else 'NO'}, OpenAI={'YES' if openai_key else 'NO'}, Cohere={'YES' if cohere_key else 'NO'}")
if gemini_key:
    print(f"💎 Gemini Key Detect: ...{gemini_key[-4:]}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# =============================================================================
# ROUTER IMPORTS - All routers in one clean import block
# =============================================================================
from sisi_lola_api.app.routers import (
    dashboard_router,      # UI Pages: /, /dashboard, /demo
    vibe_router,           # Supreme Content: /api/v2/vibe/*
    social_router,         # Social Posting: /api/v2/social/*
    enhanced_chat,         # Modal Fast Chat: /api/v2/enhanced-chat/*
    auth_router,           # Auth: /api/v2/auth/*
    control_center_router, # Admin: /api/v2/control/*
    agent,                 # Agent Builder: /agent/*
    images,                # Image Gen: /images/*
    videos,                # Video Prod: /videos/*
    audio,                 # Audio/Voice: /audio/*
    auth,                  # Legacy Auth
    nigerian_models,       # Nigerian Models: /models/*
)

# Additional routers (loaded separately to avoid circular imports)
from sisi_lola_api.app.routers import vibes_router  # Content Queue: /api/v2/vibes/*

from sisi_lola_api.app.database import init_db
from sisi_lola_api.app.config import SisiLolaDNA
from sisi_lola_api.app.services import auth_store

print("🚀 Initializing Sisi Lola Unified Inference Service...")

# =============================================================================
# APPLICATION INSTANCE
# =============================================================================
app = FastAPI(
    title="Sisi Lola API",
    description="The Central Nervous System for the Sisi Lola Virtual Human with Role-Based Access Control.",
    version="2.1.0 (Supreme)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# STATIC FILES MOUNT
# =============================================================================
static_path = Path(__file__).resolve().parent / "static"
try:
    static_path.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
except Exception:
    print("⚠️ Static directory not available, skipping mount.")

# =============================================================================
# ROUTER REGISTRATION - Organized by priority
# =============================================================================

# 1. UI Pages (No prefix - serves HTML)
app.include_router(dashboard_router.router)  # Routes: /, /dashboard, /demo, /console, /vision

# 2. Core API Endpoints (v2)
app.include_router(vibe_router.router, prefix="/api/v2")          # /api/v2/vibe/*
app.include_router(vibes_router.router, prefix="/api/v2")         # /api/v2/vibes/* (Content Queue)
app.include_router(social_router.router, prefix="/api/v2")        # /api/v2/social/*
app.include_router(enhanced_chat.router, prefix="/api/v2")        # /api/v2/enhanced-chat/*
app.include_router(auth_router.router, prefix="/api/v2")          # /api/v2/auth/*
app.include_router(control_center_router.router, prefix="/api/v2") # /api/v2/control/*

# 3. Media Modules
app.include_router(agent.router, prefix="/agent", tags=["Agent Builder"])
app.include_router(images.router, prefix="/images", tags=["Image Generation"])
app.include_router(videos.router, prefix="/videos", tags=["Video Production"])
app.include_router(audio.router, prefix="/audio", tags=["Audio & Voice"])

# 4. Utility Routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(nigerian_models.router)

# =============================================================================
# HEALTH CHECK
# =============================================================================
@app.get("/api/health")
async def health_check():
    """System health check endpoint"""
    return {
        "system_status": "ONLINE",
        "entity": SisiLolaDNA.NAME,
        "version": "2.1.0",
        "endpoints": {
            "demo": "/demo",
            "dashboard": "/dashboard", 
            "chat_api": "/api/v2/vibe/demo-chat",
            "enhanced_chat": "/api/v2/enhanced-chat/chat"
        }
    }

# =============================================================================
# STARTUP EVENTS
# =============================================================================
@app.on_event("startup")
async def startup_init():
    """Initialize services on API startup"""
    print("🎭 Loading Sisi Lola personality...")
    auth_store.init_db()
    init_db()
    print("✅ Personality loaded from HuggingFace")

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
allowed_origins = [
    origin.strip() 
    for origin in os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",") 
    if origin.strip()
]
# Add Modal domain for production
allowed_origins.append("https://bamg-studio--sisi-lola-inference-supreme-api.modal.run")
allowed_origins.append("*")  # Allow all for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROOT ENDPOINT
# =============================================================================
@app.get("/")
async def root():
    """API root - redirects to demo or provides API info"""
    return {
        "name": SisiLolaDNA.NAME,
        "version": "2.1.0 (Supreme)",
        "status": "ONLINE",
        "ui": {
            "demo": "/demo",
            "dashboard": "/dashboard",
            "docs": "/docs"
        },
        "api": {
            "chat": "/api/v2/vibe/demo-chat",
            "enhanced_chat": "/api/v2/enhanced-chat/chat",
            "health": "/api/health"
        }
    }
