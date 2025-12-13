# app/main.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables before importing any modules that depend on them
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import agent, images, videos, audio, auth, nigerian_models, cohere, chat
from app.routers import unified_chat
from app.routers import enhanced_chat
from app.routers import curator
from app.services.instagram_bot import router as instagram_router
from app.config import SisiLolaDNA
from app.services import auth_store

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

# Include the modular routers
app.include_router(agent.router, prefix="/agent", tags=["Agent Builder"])
app.include_router(chat.router, prefix="/chat", tags=["Chat & Persona"])
app.include_router(images.router, prefix="/images", tags=["Image Generation"])
app.include_router(videos.router, prefix="/videos", tags=["Video Production"])
app.include_router(audio.router, prefix="/audio", tags=["Audio & Voice"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(nigerian_models.router)
app.include_router(cohere.router)

# NEW: Unified multimodal chat
app.include_router(unified_chat.router)

# NEW: Enhanced chat with training data collection
app.include_router(enhanced_chat.router)

# NEW: Instagram bot webhook
app.include_router(instagram_router)

# NEW: Voice Dataset Curator for African language datasets
app.include_router(curator.router)

# Mount static files for web demo
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_init():
    auth_store.init_db()
    print("🚀 Sisi Lola API started!")
    print("📖 API Docs: http://localhost:8000/docs")
    print("💃 Web Demo: http://localhost:8000/demo")

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


@app.get("/demo", include_in_schema=False)
async def serve_demo():
    """Serve the interactive web demo"""
    static_file = Path(__file__).parent.parent / "static" / "index.html"
    if static_file.exists():
        return FileResponse(str(static_file))
    return {"error": "Demo not found", "hint": "Run from sisi_lola_api directory"}


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
