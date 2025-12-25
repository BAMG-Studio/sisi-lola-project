"""
SISI LOLA MODAL STUB - FULL VERSION
====================================
Cloud inference engine with full ML capabilities:
- Coqui TTS (XTTS-v2) for voice
- Mistral-7B / Llama-3 local inference support
- Unified Inference Service integration
"""

import os
from typing import Dict, Any, Optional
import modal
from modal import App, Image, Secret, Volume

# Define the Modal App
app = App("sisi-lola-inference")

# Define shared volumes for model caching
model_volume = Volume.from_name("sisi-lola-models", create_if_missing=True)

# FULL ML IMAGE - This will take time to build the first time!
sisi_image = (
    Image.debian_slim(python_version="3.10")  # TTS requires 3.10
    .apt_install("libsndfile1", "ffmpeg", "git")
    .pip_install(
        "fastapi",
        "torch",
        "torchaudio",
        "transformers",
        "scipy",
        "numpy",
        "python-dotenv",
        "huggingface_hub",
        "TTS",  # Coqui TTS
        "openai",
        "httpx"
    )
    .add_local_dir(
        local_path=os.path.join(os.path.dirname(__file__), "../../../"),
        remote_path="/root/sisi_lola_project",
        ignore=[
            "**/venv", 
            "**/.git", 
            "**/__pycache__", 
            "**/*.pyc", 
            "**/.env", 
            "**/*.mp3", 
            "**/*.wav", 
            "**/models",
            "wav2lip_workspace" # Specifically ignore this large workspace for cloud inference
        ]
    )
    .env({
        "HUGGINGFACE_HUB_CACHE": "/cache/huggingface",
        "TTS_HOME": "/cache/tts",
        "PYTHONPATH": "/root/sisi_lola_project"
    })
)


@app.cls(
    image=sisi_image,
    gpu="T4",
    timeout=600,
    cpu=4,
    memory=16384,
    volumes={"/cache": model_volume},
    secrets=[Secret.from_name("sisi-lola-secrets")]
)
class SisiLolaEngine:
    """
    The core engine running in the cloud.
    Handles high-performance text and voice generation.
    """
    
    def __enter__(self):
        """Initialize the engine when the container starts"""
        print("🚀 SISI LOLA ENGINE: Powering up in the cloud...")
        
        # Import inside __enter__ to avoid build-time issues
        from sisi_lola_api.app.services.unified_inference import UnifiedInferenceService
        
        self.service = UnifiedInferenceService()
        print("✅ SISI LOLA ENGINE: Service initialized.")

    @modal.method()
    async def generate_response(self, message: str, session_id: str = "default"):
        """Generate response with integrated voice"""
        print(f"🧠 SISI LOLA ENGINE: Thinking about: {message[:50]}...")
        
        # This will call the unified service which handles model routing
        result = await self.service.process_chat(message, session_id)
        
        return result

    @modal.method()
    async def generate_voice(self, text: str, voice_id: Optional[str] = None):
        """Standalone voice generation"""
        print(f"🎙️ SISI LOLA ENGINE: Speaking: {text[:50]}...")
        
        # Integration with TTS
        from sisi_lola_api.app.services.audio_service import AudioService
        voice_service = AudioService()
        
        audio_path = await voice_service.synthesize(text, voice_id)
        
        # Read file to bytes
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                return f.read()
        return None


@app.function(image=sisi_image)
@modal.fastapi_endpoint(method="POST")
async def generate(item: Dict[str, Any]):
    """
    Web endpoint to trigger the engine.
    Input: {"message": "Hello", "session_id": "123"}
    """
    engine = SisiLolaEngine()
    return await engine.generate_response.remote.aio(
        item.get("message"), 
        item.get("session_id", "default")
    )


@app.function(image=sisi_image)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sisi-lola-full-engine",
        "gpu": "active",
        "version": "2.0.0-full"
    }
