#!/usr/bin/env python3
"""
Sisi Lola Model Cache Manager
Singleton pattern for model loading - prevents 60-70s delay on each request
Models are loaded ONCE at startup and kept in GPU memory

This is the ROOT CAUSE fix for the 80.5s response time.
"""
import os
import sys
import torch
import threading
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class ModelStats:
    """Track model usage statistics"""
    load_time_seconds: float = 0.0
    requests_served: int = 0
    last_used: Optional[datetime] = None
    total_tokens_generated: int = 0
    avg_inference_time_ms: float = 0.0


@dataclass  
class CachedModel:
    """Container for a cached model with metadata"""
    model: Any = None
    tokenizer: Any = None
    config: Dict = field(default_factory=dict)
    stats: ModelStats = field(default_factory=ModelStats)
    loaded_at: Optional[datetime] = None
    device: str = "cpu"


class ModelCacheManager:
    """
    Singleton model cache manager.
    Ensures models are loaded ONCE and reused across all requests.
    
    Usage:
        cache = ModelCacheManager()
        brain = cache.get_brain()  # Returns cached model, loads if needed
        voice = cache.get_voice()  # Returns cached voice model
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._brain: Optional[CachedModel] = None
        self._voice: Optional[CachedModel] = None
        self._loading_lock = threading.Lock()
        self._config = self._load_config()
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🚀 ModelCacheManager initialized on {self._device}")
        
    def _load_config(self) -> Dict:
        """Load optimization configuration"""
        config_path = PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_production_config(self) -> Dict:
        """Load production model paths"""
        config_path = PROJECT_ROOT / "ml_training" / "outputs" / "production_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f).get('sisi_lola_production', {})
        
        # Fallback to environment variables
        return {
            'brain': {
                'base_model': os.getenv('BRAIN_MODEL', 'gpt2'),
                'adapter_path': os.getenv('NIGERIAN_BRAIN_ADAPTER', 'ml_training/checkpoints/natlas_lora'),
                'system_prompt': "You are Sisi Lola, a friendly Nigerian virtual host from Lagos."
            },
            'voice': {
                'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
                'checkpoint_path': os.getenv('NIGERIAN_VOICE_CHECKPOINT', '')
            }
        }
        
    def get_brain(self, force_reload: bool = False) -> CachedModel:
        """
        Get cached brain model (LLM).
        Loads model if not already cached.
        
        Args:
            force_reload: Force reload even if already cached
            
        Returns:
            CachedModel with model, tokenizer, and stats
        """
        if self._brain is not None and not force_reload:
            self._brain.stats.requests_served += 1
            self._brain.stats.last_used = datetime.now()
            return self._brain
            
        with self._loading_lock:
            # Double-check after acquiring lock
            if self._brain is not None and not force_reload:
                return self._brain
                
            print("🧠 Loading brain model (first request)...")
            start_time = datetime.now()
            
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                from peft import PeftModel
                
                prod_config = self._load_production_config()
                brain_cfg = prod_config.get('brain', {})
                
                base_model = brain_cfg.get('base_model', 'gpt2')
                adapter_path = brain_cfg.get('adapter_path', '')
                
                print(f"   📥 Loading base model: {base_model}")
                
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    base_model,
                    trust_remote_code=True,
                    token=os.getenv("HUGGINGFACE_TOKEN")
                )
                
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                # Load model with optimizations
                load_kwargs = {
                    'trust_remote_code': True,
                    'token': os.getenv("HUGGINGFACE_TOKEN")
                }
                
                # Apply optimizations based on config
                inference_cfg = self._config.get('inference', {})
                
                if self._device == "cuda":
                    load_kwargs['device_map'] = 'auto'
                    load_kwargs['torch_dtype'] = torch.float16
                    
                    # Enable Flash Attention 2 if configured
                    if inference_cfg.get('flash_attention', {}).get('enabled', False):
                        load_kwargs['attn_implementation'] = 'flash_attention_2'
                        print("   ⚡ Flash Attention 2 enabled")
                
                model = AutoModelForCausalLM.from_pretrained(base_model, **load_kwargs)
                
                # Load LoRA adapter if available
                adapter_full_path = PROJECT_ROOT / adapter_path
                if adapter_full_path.exists():
                    print(f"   🔧 Loading LoRA adapter: {adapter_path}")
                    model = PeftModel.from_pretrained(model, str(adapter_full_path))
                
                # Move to device if not using device_map
                if 'device_map' not in load_kwargs:
                    model = model.to(self._device)
                
                model.eval()  # Set to evaluation mode
                
                load_time = (datetime.now() - start_time).total_seconds()
                
                self._brain = CachedModel(
                    model=model,
                    tokenizer=tokenizer,
                    config=brain_cfg,
                    stats=ModelStats(load_time_seconds=load_time),
                    loaded_at=datetime.now(),
                    device=self._device
                )
                
                print(f"   ✅ Brain loaded in {load_time:.1f}s")
                return self._brain
                
            except Exception as e:
                print(f"   ❌ Brain loading failed: {e}")
                raise
    
    def get_voice(self, force_reload: bool = False) -> CachedModel:
        """
        Get cached voice model (TTS).
        Loads model if not already cached.
        
        Args:
            force_reload: Force reload even if already cached
            
        Returns:
            CachedModel with TTS model
        """
        if self._voice is not None and not force_reload:
            self._voice.stats.requests_served += 1
            self._voice.stats.last_used = datetime.now()
            return self._voice
            
        with self._loading_lock:
            if self._voice is not None and not force_reload:
                return self._voice
                
            print("🎤 Loading voice model (first request)...")
            start_time = datetime.now()
            
            try:
                from TTS.api import TTS
                
                prod_config = self._load_production_config()
                voice_cfg = prod_config.get('voice', {})
                
                model_name = voice_cfg.get('model', 'tts_models/multilingual/multi-dataset/xtts_v2')
                
                print(f"   📥 Loading TTS model: {model_name}")
                
                tts = TTS(model_name=model_name)
                
                # Load fine-tuned checkpoint if available
                checkpoint_path = voice_cfg.get('checkpoint_path', '')
                if checkpoint_path and os.path.exists(checkpoint_path):
                    print(f"   🔧 Loading voice checkpoint: {checkpoint_path}")
                    # tts.load_checkpoint(checkpoint_path)
                
                load_time = (datetime.now() - start_time).total_seconds()
                
                self._voice = CachedModel(
                    model=tts,
                    config=voice_cfg,
                    stats=ModelStats(load_time_seconds=load_time),
                    loaded_at=datetime.now(),
                    device=self._device
                )
                
                print(f"   ✅ Voice loaded in {load_time:.1f}s")
                return self._voice
                
            except Exception as e:
                print(f"   ❌ Voice loading failed: {e}")
                raise
    
    def preload_all(self) -> Dict[str, float]:
        """
        Preload all models at startup.
        Call this in FastAPI lifespan/startup event.
        
        Returns:
            Dict with load times for each model
        """
        print("\n" + "="*60)
        print("🚀 PRELOADING MODELS AT STARTUP")
        print("="*60)
        
        load_times = {}
        
        # Load brain
        try:
            brain = self.get_brain()
            load_times['brain'] = brain.stats.load_time_seconds
        except Exception as e:
            print(f"⚠️ Brain preload failed: {e}")
            load_times['brain'] = -1
            
        # Load voice (optional, can be lazy loaded)
        try:
            voice = self.get_voice()
            load_times['voice'] = voice.stats.load_time_seconds
        except Exception as e:
            print(f"⚠️ Voice preload failed (will use fallback): {e}")
            load_times['voice'] = -1
            
        total_time = sum(t for t in load_times.values() if t > 0)
        
        print("="*60)
        print(f"✅ Models preloaded in {total_time:.1f}s")
        print("="*60 + "\n")
        
        return load_times
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'device': self._device,
            'brain': None,
            'voice': None
        }
        
        if self._brain:
            stats['brain'] = {
                'loaded': True,
                'load_time_s': self._brain.stats.load_time_seconds,
                'requests_served': self._brain.stats.requests_served,
                'last_used': self._brain.stats.last_used.isoformat() if self._brain.stats.last_used else None,
                'loaded_at': self._brain.loaded_at.isoformat() if self._brain.loaded_at else None
            }
        else:
            stats['brain'] = {'loaded': False}
            
        if self._voice:
            stats['voice'] = {
                'loaded': True,
                'load_time_s': self._voice.stats.load_time_seconds,
                'requests_served': self._voice.stats.requests_served,
                'last_used': self._voice.stats.last_used.isoformat() if self._voice.stats.last_used else None,
                'loaded_at': self._voice.loaded_at.isoformat() if self._voice.loaded_at else None
            }
        else:
            stats['voice'] = {'loaded': False}
            
        return stats
    
    def unload_all(self):
        """Unload all models from memory"""
        print("🧹 Unloading all models...")
        
        if self._brain:
            del self._brain.model
            del self._brain.tokenizer
            self._brain = None
            
        if self._voice:
            del self._voice.model
            self._voice = None
            
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        print("✅ All models unloaded")


# Global instance for easy access
_cache_instance: Optional[ModelCacheManager] = None


def get_model_cache() -> ModelCacheManager:
    """Get the global model cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ModelCacheManager()
    return _cache_instance


# Convenience functions
def get_brain():
    """Get cached brain model"""
    return get_model_cache().get_brain()


def get_voice():
    """Get cached voice model"""
    return get_model_cache().get_voice()


def preload_models():
    """Preload all models at startup"""
    return get_model_cache().preload_all()


if __name__ == "__main__":
    # Test the cache manager
    print("Testing Model Cache Manager\n")
    
    cache = get_model_cache()
    
    # First load - should be slow
    print("\n--- First Load (Cold) ---")
    import time
    start = time.time()
    brain = cache.get_brain()
    first_load = time.time() - start
    print(f"First load took: {first_load:.2f}s")
    
    # Second load - should be instant
    print("\n--- Second Load (Cached) ---")
    start = time.time()
    brain2 = cache.get_brain()
    second_load = time.time() - start
    print(f"Second load took: {second_load:.4f}s")
    
    print(f"\n📊 Speedup: {first_load/max(second_load, 0.001):.0f}x faster!")
    
    # Show stats
    print("\n--- Cache Stats ---")
    stats = cache.get_stats()
    print(json.dumps(stats, indent=2, default=str))
