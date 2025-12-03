#!/usr/bin/env python3
"""
Integrate trained Nigerian models with Sisi Lola API
"""
import os
import sys
import json
import shutil
from pathlib import Path

def check_trained_models():
    """Verify trained models exist"""
    brain_path = "ml_training/checkpoints/natlas_lora"
    voice_path = "ml_training/checkpoints/xtts_sisi_lola"
    
    brain_exists = Path(brain_path).exists()
    voice_exists = Path(voice_path).exists()
    
    print("📋 Checking trained models...")
    print(f"  Brain (N-ATLaS): {'✅' if brain_exists else '❌'} {brain_path}")
    print(f"  Voice (XTTS): {'✅' if voice_exists else '❌'} {voice_path}")
    
    if not (brain_exists or voice_exists):
        print("\n❌ No trained models found. Run training first:")
        print("   python ml_training/scripts/unified_training_orchestrator.py")
        return False
    
    return True

def create_api_service():
    """Create FastAPI service for Nigerian models"""
    service_code = '''"""
Sisi Lola Nigerian Models Service
Provides brain (LLM) and voice (TTS) endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
sys.path.append("ml_training/scripts")
from inference_nigerian import SisiLolaInference

router = APIRouter(prefix="/nigerian", tags=["nigerian-models"])

# Initialize inference engine
sisi = None

class ChatRequest(BaseModel):
    message: str
    generate_audio: bool = False
    language: str = "yo"

class ChatResponse(BaseModel):
    text: str
    audio_url: str = None

@router.on_event("startup")
async def load_models():
    """Load models on startup"""
    global sisi
    try:
        sisi = SisiLolaInference()
        print("✅ Nigerian models loaded")
    except Exception as e:
        print(f"⚠️  Failed to load models: {e}")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Sisi Lola using Nigerian models"""
    if sisi is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        result = sisi.chat(
            request.message,
            generate_audio=request.generate_audio,
            language=request.language
        )
        
        return ChatResponse(
            text=result["text"],
            audio_url=result.get("audio")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-text")
async def generate_text(message: str, max_length: int = 256):
    """Generate text response only"""
    if sisi is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        response = sisi.generate_text(message, max_length=max_length)
        return {"text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-speech")
async def generate_speech(text: str, language: str = "yo"):
    """Generate speech from text"""
    if sisi is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        from datetime import datetime
        output_path = f"ml_training/outputs/speech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_path = sisi.generate_speech(text, output_path, language)
        return {"audio_url": audio_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    """Check model health"""
    return {
        "status": "healthy" if sisi else "not_loaded",
        "brain": "loaded" if sisi and sisi.brain else "not_loaded",
        "voice": "loaded" if sisi and sisi.voice else "not_loaded"
    }
'''
    
    service_path = "sisi_lola_api/app/routers/nigerian_models.py"
    os.makedirs(os.path.dirname(service_path), exist_ok=True)
    
    with open(service_path, 'w') as f:
        f.write(service_code)
    
    print(f"✅ Created API service: {service_path}")
    return service_path

def update_main_api():
    """Update main.py to include Nigerian models router"""
    main_path = "sisi_lola_api/app/main.py"
    
    if not os.path.exists(main_path):
        print(f"⚠️  {main_path} not found, skipping API update")
        return
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Check if already integrated
    if "nigerian_models" in content:
        print("✅ API already includes Nigerian models router")
        return
    
    # Add import and router
    import_line = "from app.routers import nigerian_models\n"
    router_line = "app.include_router(nigerian_models.router)\n"
    
    # Find where to insert
    if "from app.routers import" in content:
        # Add after existing router imports
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "from app.routers import" in line and "nigerian_models" not in line:
                lines.insert(i + 1, import_line.strip())
                break
        content = '\n'.join(lines)
    
    if "app.include_router" in content:
        # Add after existing router includes
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "app.include_router" in line:
                lines.insert(i + 1, router_line.strip())
                break
        content = '\n'.join(lines)
    
    with open(main_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {main_path} with Nigerian models router")

def create_env_updates():
    """Generate environment variable updates"""
    env_updates = """
# Nigerian Models Configuration
NIGERIAN_BRAIN_MODEL=NCAIR1/N-ATLaS-8B
NIGERIAN_BRAIN_ADAPTER=ml_training/checkpoints/natlas_lora
NIGERIAN_VOICE_MODEL=XTTS-v2
NIGERIAN_VOICE_CHECKPOINT=ml_training/checkpoints/xtts_sisi_lola
NIGERIAN_MODELS_ENABLED=true
"""
    
    print("\n📝 Add these to your .env file:")
    print(env_updates)
    
    # Optionally append to .env
    env_path = "sisi_lola_api/.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            current_env = f.read()
        
        if "NIGERIAN_MODELS_ENABLED" not in current_env:
            with open(env_path, 'a') as f:
                f.write(env_updates)
            print(f"✅ Updated {env_path}")
        else:
            print(f"✅ {env_path} already has Nigerian models config")

def create_test_script():
    """Create test script for API integration"""
    test_code = '''#!/usr/bin/env python3
"""Test Nigerian models API integration"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/nigerian/health")
    print(f"Health: {response.json()}")
    return response.status_code == 200

def test_chat():
    """Test chat endpoint"""
    payload = {
        "message": "Bawo ni? Tell me about Lagos",
        "generate_audio": False,
        "language": "yo"
    }
    response = requests.post(f"{BASE_URL}/nigerian/chat", json=payload)
    print(f"Chat response: {response.json()}")
    return response.status_code == 200

def test_text_generation():
    """Test text generation"""
    response = requests.post(
        f"{BASE_URL}/nigerian/generate-text",
        params={"message": "Wetin be your favorite food?"}
    )
    print(f"Text: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    print("🧪 Testing Nigerian Models API Integration\\n")
    
    tests = [
        ("Health Check", test_health),
        ("Chat", test_chat),
        ("Text Generation", test_text_generation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            status = "✅" if result else "❌"
            results.append((name, result))
            print(f"{status} {name}\\n")
        except Exception as e:
            print(f"❌ {name}: {e}\\n")
            results.append((name, False))
    
    print("\\n" + "="*50)
    print("Test Summary:")
    for name, result in results:
        print(f"  {'✅' if result else '❌'} {name}")
'''
    
    test_path = "ml_training/scripts/test_api_integration.py"
    with open(test_path, 'w') as f:
        f.write(test_code)
    
    print(f"✅ Created test script: {test_path}")
    return test_path

def main():
    print("=" * 60)
    print("🔗 INTEGRATING NIGERIAN MODELS WITH API")
    print("=" * 60)
    
    # Check models
    if not check_trained_models():
        sys.exit(1)
    
    print("\n📦 Creating API integration...")
    
    # Create service
    service_path = create_api_service()
    
    # Update main API
    update_main_api()
    
    # Create env updates
    create_env_updates()
    
    # Create test script
    test_path = create_test_script()
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Restart API server:")
    print("     cd sisi_lola_api && uvicorn app.main:app --reload")
    print("\n  2. Test integration:")
    print(f"     python {test_path}")
    print("\n  3. Try endpoints:")
    print("     POST http://localhost:8000/nigerian/chat")
    print("     POST http://localhost:8000/nigerian/generate-text")
    print("     POST http://localhost:8000/nigerian/generate-speech")
    print("     GET  http://localhost:8000/nigerian/health")

if __name__ == "__main__":
    main()
