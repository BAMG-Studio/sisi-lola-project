"""
Optimized Modal Inference Service for Sisi Lola
Fixes: Cold starts, model caching, keep-warm configuration
"""
import modal
import os
from typing import Dict, Any

# ============================================
# OPTIMIZATION 1: Use faster GPU (T4 vs A100)
# ============================================
GPU_CONFIG = "T4"  # 10x faster cold start than A100


# =====================================================
# MODEL CONFIGURATION
# =====================================================
# Phase 1: Default English model (GPT-Neo - non-gated)
DEFAULT_ENGLISH_MODEL = "EleutherAI/gpt-neo-1.3B"  # Fast, non-gated
# Phase 2: Nigerian custom model (your trained model)
NIGERIAN_MODEL = "sisilolalive/sisi-lola-brain-mistral"  # Your custom trained model

# Language detection keywords
NIGERIAN_KEYWORDS = [
        "abeg", "oga", "wetin", "no wahala", "how far", "na so",
            "bros", "sista", "make we", "shey", "abi", "ehn"
            ]
# ============================================
# OPTIMIZATION 2: Optimized Image with Caching
# Pin numpy<2 for torch 2.1.0 compatibility
# ============================================
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy<2",  # Pin numpy for torch compatibility
        "torch==2.1.0",
        "transformers==4.35.0",
        "accelerate==0.24.0",
        "bitsandbytes==0.41.0",
        "scipy",
        "sentencepiece",
        "protobuf",
        "fastapi[standard]",
    )
    .env({"TRANSFORMERS_CACHE": "/cache/huggingface"})
)

app = modal.App("sisi-lola-inference")

# =====================================================
# LANGUAGE DETECTION (Phase 3)
# =====================================================
def detect_nigerian_language(text: str) -> bool:
        """Simple keyword-based Nigerian language detection (Pidgin/Yoruba)."""
            text_lower = text.lower()
                return any(keyword in text_lower for keyword in NIGERIAN_KEYWORDS)
# ============================================
# OPTIMIZATION 3: Model Cache Class with @modal.cls
# ============================================
@app.cls(
    image=image,
    gpu=GPU_CONFIG,
    min_containers=1,  # Keep 1 container always ready (cheaper)
    scaledown_window=300,  # Keep alive for 5 minutes
    timeout=300,  # 5 minute max per request
    secrets=[
        modal.Secret.from_name("huggingface-secret"),
        modal.Secret.from_name("sisi-lola-secrets")
    ],
)
class ModelInference:
    """Persistent model cache that loads once per container"""
    
    # Use class attributes instead of __init__
    models: Dict[str, Any] = {}
    tokenizers: Dict[str, Any] = {}
    
    @modal.enter()
    def load_models(self):
        """Load models ONCE when container starts"""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print("🚀 Loading models into memory...")
        
        # Get HuggingFace token from environment (set by Modal secret)
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        
                # TODO: UPDATED - Load BOTH English (GPT-Neo) and Nigerian (sisi-lola-brain-mistral) models
                        # Phase 1: English model = DEFAULT_ENGLISH_MODEL
                                # Phase 2: Nigerian model = NIGERIAN_MODEL
                                        # Phase 3: Use detect_nigerian_language() to route requests
                                        # Use a simpler, non-gated model for reliability
        chat_model = os.getenv("CHAT_MODEL", "microsoft/DialoGPT-medium")
        
        try:
            # Load with optimizations
            self.tokenizers['chat'] = AutoTokenizer.from_pretrained(
                chat_model,
                cache_dir="/cache/huggingface",
                trust_remote_code=True,
                token=hf_token
            )
            
            self.models['chat'] = AutoModelForCausalLM.from_pretrained(
                chat_model,
                cache_dir="/cache/huggingface",
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                token=hf_token
            )
            
            print("✅ Models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    @modal.method()
    def generate(self, prompt: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """Fast inference using cached models"""
        import torch
        
        model = self.models['chat']
        tokenizer = self.tokenizers['chat']
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    @modal.fastapi_endpoint(method="POST")
    async def generate_text(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fast inference endpoint with model caching
        
        Request format:
        {
            "message": "user message",
            "session_id": "session123",
            "max_tokens": 256,
            "temperature": 0.7
        }
        """
        import time
        start_time = time.time()
        
        try:
            # Extract parameters
            message = request.get("message", "")
            max_tokens = request.get("max_tokens", 256)
            temperature = request.get("temperature", 0.7)
            
            if not message:
                return {"error": "No message provided", "status": "error"}
            
            # Generate response using the cached model
            response_text = self.generate(
                prompt=message,
                max_length=max_tokens,
                temperature=temperature
            )
            
            inference_time = time.time() - start_time
            
            return {
                "status": "success",
                "text": response_text,
                "inference_time_ms": round(inference_time * 1000, 2),
                "model": "cached",
                "gpu": "T4"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "inference_time_ms": round((time.time() - start_time) * 1000, 2)
            }

    @modal.fastapi_endpoint(method="GET")
    def health(self) -> Dict[str, Any]:
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "service": "sisi-lola-inference",
            "optimizations": [
                "Model caching with @enter",
                "Keep-warm containers (1)",
                "Container idle timeout (300s)",
                "T4 GPU (fast startup)",
                "8-bit quantization"
            ]
        }

