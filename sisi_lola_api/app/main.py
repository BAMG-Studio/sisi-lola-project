# app/main.py
import os
from dotenv import load_dotenv

# Load environment variables before importing any modules that depend on them
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import agent, images, videos, audio, auth, nigerian_models, cohere, chat
# from app.routers import chat
from app.config import SisiLolaDNA
from app.services import auth_store

app = FastAPI(
    title="Sisi Lola OS API",
    description="The Central Nervous System for the Sisi Lola Virtual Human.",
    version="1.0.0"
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


@app.on_event("startup")
async def startup_init():
    auth_store.init_db()

# CORS for frontend integration
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    access_key = os.getenv("KLINGAI_ACCESS_KEY")
    secret_key = os.getenv("KLINGAI_SECRET_KEY")
    return {
        "system_status": "ONLINE",
        "entity": SisiLolaDNA.NAME,
        "dna_version": "2.0 (Breathtaking/Voluptuous)",
        "klingai_credentials_loaded": bool(access_key and secret_key),
        "openai_key_loaded": bool(os.getenv("OPENAI_API_KEY"))
    }
