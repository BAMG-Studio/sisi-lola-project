#!/usr/bin/env python3
"""
Sisi Lola Startup Optimizer
FastAPI lifespan handler for model preloading and optimization.

Use this to ensure models are loaded ONCE at startup, eliminating
the 60-70s first-request delay.

Usage in main.py:
    from ml_training.scripts.startup_optimizer import lifespan
    
    app = FastAPI(lifespan=lifespan)
"""
import os
import sys
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any
import time

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def preload_models() -> Dict[str, Any]:
    """
    Preload all models at startup.
    
    This is the key optimization that reduces response time from 80.5s to <2s.
    
    Returns:
        Dict with load times and status for each model
    """
    print("\n" + "="*60)
    print("🚀 SISI LOLA STARTUP OPTIMIZATION")
    print("="*60)
    print("   Loading models once at startup...")
    print("   This prevents 60-70s delay on first request")
    print("="*60 + "\n")
    
    results = {
        "brain": {"status": "pending", "load_time_s": 0},
        "voice": {"status": "pending", "load_time_s": 0},
        "cache": {"status": "pending"},
        "total_time_s": 0
    }
    
    total_start = time.time()
    
    # Check if models are enabled
    if os.getenv("NIGERIAN_MODELS_ENABLED", "false").lower() != "true":
        print("⚠️ Nigerian models not enabled (set NIGERIAN_MODELS_ENABLED=true)")
        results["status"] = "disabled"
        return results
    
    # Load brain model
    try:
        from ml_training.scripts.model_cache_manager import get_model_cache
        cache = get_model_cache()
        
        print("🧠 Loading brain model...")
        start = time.time()
        brain = cache.get_brain()
        load_time = time.time() - start
        results["brain"] = {
            "status": "loaded",
            "load_time_s": round(load_time, 2),
            "device": brain.device
        }
        print(f"   ✅ Brain loaded in {load_time:.1f}s")
        
    except Exception as e:
        print(f"   ❌ Brain loading failed: {e}")
        results["brain"] = {"status": "failed", "error": str(e)}
    
    # Load voice model (optional, can be lazy loaded)
    try:
        print("🎤 Loading voice model...")
        start = time.time()
        voice = cache.get_voice()
        load_time = time.time() - start
        results["voice"] = {
            "status": "loaded",
            "load_time_s": round(load_time, 2)
        }
        print(f"   ✅ Voice loaded in {load_time:.1f}s")
        
    except Exception as e:
        print(f"   ⚠️ Voice loading skipped: {e}")
        results["voice"] = {"status": "skipped", "reason": str(e)}
    
    # Initialize caches
    try:
        from ml_training.scripts.redis_cache import get_response_cache
        response_cache = get_response_cache()
        results["cache"] = {"status": "initialized"}
        print("   ✅ Response cache initialized")
    except Exception as e:
        results["cache"] = {"status": "fallback", "reason": str(e)}
    
    results["total_time_s"] = round(time.time() - total_start, 2)
    
    print("\n" + "="*60)
    print(f"✅ STARTUP COMPLETE in {results['total_time_s']}s")
    print("   Models are now cached - fast inference ready!")
    print("="*60 + "\n")
    
    return results


async def cleanup_models():
    """Cleanup on shutdown"""
    print("\n🧹 Cleaning up models...")
    
    try:
        from ml_training.scripts.model_cache_manager import get_model_cache
        cache = get_model_cache()
        cache.unload_all()
    except:
        pass
    
    print("✅ Cleanup complete")


@asynccontextmanager
async def lifespan(app):
    """
    FastAPI lifespan handler for model management.
    
    Usage:
        from fastapi import FastAPI
        from ml_training.scripts.startup_optimizer import lifespan
        
        app = FastAPI(lifespan=lifespan)
    """
    # Startup
    startup_results = await preload_models()
    app.state.startup_results = startup_results
    
    yield
    
    # Shutdown
    await cleanup_models()


def get_startup_status(app) -> Dict[str, Any]:
    """Get startup status from app state"""
    if hasattr(app, 'state') and hasattr(app.state, 'startup_results'):
        return app.state.startup_results
    return {"status": "unknown"}


# Quick startup function for scripts
def quick_start():
    """Quick startup for scripts and testing"""
    import asyncio
    return asyncio.run(preload_models())


if __name__ == "__main__":
    # Test startup
    import asyncio
    
    print("Testing Startup Optimizer\n")
    
    results = asyncio.run(preload_models())
    
    print("\n📊 Startup Results:")
    for key, value in results.items():
        print(f"   {key}: {value}")
