# app/main.py
import os
from dotenv import load_dotenv

# Load environment variables before importing any modules that depend on them
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sisi_lola_api.app.routers import (
    agent, images, videos, audio, auth, nigerian_models, 
    auth_router, control_center_router, vibe_router, dashboard_router
)
from sisi_lola_api.app.database import init_db
# from sisi_lola_api.app.routers import chat
from sisi_lola_api.app.config import SisiLolaDNA
from sisi_lola_api.app.services import auth_store
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(
    title="Sisi Lola Control Center API",
    description="The Central Nervous System for the Sisi Lola Virtual Human with Role-Based Access Control.",
    version="2.1.0 (Supreme)"
)

# Static files for UI
static_path = Path(__file__).resolve().parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include UI Router
app.include_router(dashboard_router.router)

# Include the modular routers
app.include_router(vibe_router.router, prefix="/api/v2")
app.include_router(agent.router, prefix="/agent", tags=["Agent Builder"])
# app.include_router(chat.router, prefix="/chat", tags=["Chat & Persona"])
app.include_router(images.router, prefix="/images", tags=["Image Generation"])
app.include_router(videos.router, prefix="/videos", tags=["Video Production"])
app.include_router(audio.router, prefix="/audio", tags=["Audio & Voice"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(nigerian_models.router)

# Control Center routes with RBAC
app.include_router(auth_router.router, prefix="/api/v2")
app.include_router(control_center_router.router, prefix="/api/v2")

@app.get("/api/health")
async def health_check():
    return {
        "system_status": "ONLINE",
        "entity": SisiLolaDNA.NAME,
        "version": "2.1.0"
    }


@app.on_event("startup")
async def startup_init():
    auth_store.init_db()
    init_db()

# CORS for frontend integration
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
