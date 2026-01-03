#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🚀 INFERENCE ROUTER - HuggingFace Inference Providers Routing
═══════════════════════════════════════════════════════════════════════════════
Route inference requests through HuggingFace Inference Providers for:
- Multi-provider support (Replicate, Together, Groq, etc.)
- Automatic failover
- Cost optimization with `:cheapest` suffix
- Speed optimization with `:fastest` suffix

This leverages HuggingFace Pro's Inference Providers feature.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Literal
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InferenceRouter")

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Optional imports
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("huggingface_hub not installed. Run: pip install huggingface_hub")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS AND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class RoutingStrategy(str, Enum):
    """Routing strategy for inference."""
    FASTEST = "fastest"
    CHEAPEST = "cheapest"
    SPECIFIC = "specific"
    FALLBACK = "fallback"


class Provider(str, Enum):
    """Supported inference providers."""
    REPLICATE = "replicate"
    TOGETHER = "together"
    GROQ = "groq"
    FIREWORKS = "fireworks"
    HUGGINGFACE = "huggingface"
    CEREBRAS = "cerebras"


@dataclass
class RouterConfig:
    """Inference router configuration."""
    
    # Default strategy
    default_strategy: RoutingStrategy = RoutingStrategy.FALLBACK
    
    # Provider priority for fallback
    provider_priority: List[str] = field(default_factory=lambda: [
        "replicate",
        "together",
        "groq",
        "huggingface",
    ])
    
    # Model mappings (Sisi Lola model → HF model ID or provider model)
    model_mappings: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "brain": {
            "huggingface": "sisilolalive/sisi-lola-brain-mistral",
            "together": "mistralai/Mistral-7B-Instruct-v0.3",
            "groq": "mixtral-8x7b-32768",
            "replicate": "bamg-studio/sisi-lola-brain",
        },
        "voice": {
            "replicate": "cjwbw/xtts-v2",
            "huggingface": "coqui/XTTS-v2",
        },
        "video": {
            "replicate": "zsxkib/omni-human",
        },
        "image": {
            "replicate": "stability-ai/sdxl",
            "together": "stabilityai/stable-diffusion-xl-base-1.0",
            "huggingface": "stabilityai/stable-diffusion-xl-base-1.0",
        }
    })
    
    # Timeout per provider (seconds)
    provider_timeouts: Dict[str, float] = field(default_factory=lambda: {
        "groq": 30,
        "together": 60,
        "replicate": 120,
        "huggingface": 90,
        "fireworks": 60,
    })
    
    # Max retries per request
    max_retries: int = 3
    
    # Enable request caching
    enable_cache: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# INFERENCE ROUTER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class InferenceRouter:
    """
    Route inference requests through HuggingFace Inference Providers.
    
    Features:
    - Multi-provider routing (Replicate, Together, Groq, etc.)
    - Automatic failover with priority ordering
    - Strategy-based routing (fastest, cheapest, specific)
    - Request caching
    - Metrics tracking
    """
    
    def __init__(
        self,
        hf_token: Optional[str] = None,
        config: Optional[RouterConfig] = None
    ):
        """
        Initialize the inference router.
        
        Args:
            hf_token: HuggingFace token (for Inference Providers)
            config: Router configuration
        """
        self.hf_token = hf_token or os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")
        self.config = config or RouterConfig()
        
        # Initialize HF Inference Client
        if HF_AVAILABLE and self.hf_token:
            self.client = InferenceClient(token=self.hf_token)
        else:
            self.client = None
        
        # Request cache
        self._cache: Dict[str, Any] = {}
        
        # Metrics
        self._metrics = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "provider_usage": {},
            "avg_latency": {}
        }
        
        logger.info(f"🚀 Inference Router initialized (HF client: {self.client is not None})")
    
    def route(
        self,
        model_type: str,
        prompt: str,
        strategy: Optional[RoutingStrategy] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route an inference request.
        
        Args:
            model_type: Type of model (brain, voice, video, image)
            prompt: Input prompt
            strategy: Routing strategy
            provider: Specific provider (for SPECIFIC strategy)
            **kwargs: Additional model parameters
            
        Returns:
            Inference result
        """
        strategy = strategy or self.config.default_strategy
        self._metrics["requests"] += 1
        
        # Check cache
        cache_key = self._get_cache_key(model_type, prompt, kwargs)
        if self.config.enable_cache and cache_key in self._cache:
            logger.info(f"📦 Cache hit for {model_type}")
            return self._cache[cache_key]
        
        # Route based on strategy
        if strategy == RoutingStrategy.SPECIFIC and provider:
            result = self._call_provider(model_type, prompt, provider, **kwargs)
        elif strategy == RoutingStrategy.FASTEST:
            result = self._call_fastest(model_type, prompt, **kwargs)
        elif strategy == RoutingStrategy.CHEAPEST:
            result = self._call_cheapest(model_type, prompt, **kwargs)
        else:  # FALLBACK
            result = self._call_with_fallback(model_type, prompt, **kwargs)
        
        # Cache result
        if self.config.enable_cache and result.get("success"):
            self._cache[cache_key] = result
        
        return result
    
    def _call_provider(
        self,
        model_type: str,
        prompt: str,
        provider: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Call a specific provider."""
        
        model_id = self._get_model_id(model_type, provider)
        if not model_id:
            return {
                "success": False,
                "error": f"No model mapping for {model_type} on {provider}"
            }
        
        logger.info(f"📡 Calling {provider} for {model_type}: {model_id}")
        
        try:
            start_time = datetime.now()
            
            if model_type == "brain":
                result = self._inference_text(model_id, prompt, provider, **kwargs)
            elif model_type == "voice":
                result = self._inference_voice(model_id, prompt, provider, **kwargs)
            elif model_type == "image":
                result = self._inference_image(model_id, prompt, provider, **kwargs)
            else:
                result = self._inference_text(model_id, prompt, provider, **kwargs)
            
            latency = (datetime.now() - start_time).total_seconds()
            self._update_metrics(provider, latency, True)
            
            return {
                "success": True,
                "provider": provider,
                "model": model_id,
                "result": result,
                "latency": latency
            }
            
        except Exception as e:
            self._update_metrics(provider, 0, False)
            logger.warning(f"❌ {provider} failed: {e}")
            return {
                "success": False,
                "provider": provider,
                "error": str(e)
            }
    
    def _call_with_fallback(
        self,
        model_type: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Call providers with fallback."""
        
        for provider in self.config.provider_priority:
            model_id = self._get_model_id(model_type, provider)
            if not model_id:
                continue
            
            result = self._call_provider(model_type, prompt, provider, **kwargs)
            if result.get("success"):
                return result
        
        self._metrics["failures"] += 1
        return {
            "success": False,
            "error": "All providers failed",
            "tried": [p for p in self.config.provider_priority if self._get_model_id(model_type, p)]
        }
    
    def _call_fastest(
        self,
        model_type: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call the fastest provider.
        
        Uses HuggingFace Inference Providers :fastest suffix.
        """
        model_mappings = self.config.model_mappings.get(model_type, {})
        hf_model = model_mappings.get("huggingface")
        
        if hf_model and self.client:
            # Use HF Inference Providers with :fastest suffix
            model_with_suffix = f"{hf_model}:fastest"
            logger.info(f"⚡ Using fastest provider for: {model_with_suffix}")
            
            try:
                if model_type == "brain":
                    result = self.client.text_generation(
                        prompt,
                        model=model_with_suffix,
                        **kwargs
                    )
                else:
                    result = self._call_with_fallback(model_type, prompt, **kwargs)
                    return result
                
                return {
                    "success": True,
                    "provider": "fastest",
                    "model": hf_model,
                    "result": result
                }
            except Exception as e:
                logger.warning(f"Fastest routing failed: {e}")
        
        # Fall back to normal fallback
        return self._call_with_fallback(model_type, prompt, **kwargs)
    
    def _call_cheapest(
        self,
        model_type: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call the cheapest provider.
        
        Uses HuggingFace Inference Providers :cheapest suffix.
        """
        model_mappings = self.config.model_mappings.get(model_type, {})
        hf_model = model_mappings.get("huggingface")
        
        if hf_model and self.client:
            model_with_suffix = f"{hf_model}:cheapest"
            logger.info(f"💰 Using cheapest provider for: {model_with_suffix}")
            
            try:
                if model_type == "brain":
                    result = self.client.text_generation(
                        prompt,
                        model=model_with_suffix,
                        **kwargs
                    )
                else:
                    result = self._call_with_fallback(model_type, prompt, **kwargs)
                    return result
                
                return {
                    "success": True,
                    "provider": "cheapest",
                    "model": hf_model,
                    "result": result
                }
            except Exception as e:
                logger.warning(f"Cheapest routing failed: {e}")
        
        return self._call_with_fallback(model_type, prompt, **kwargs)
    
    def _inference_text(
        self,
        model_id: str,
        prompt: str,
        provider: str,
        **kwargs
    ) -> str:
        """Text generation inference."""
        
        if provider == "huggingface" and self.client:
            return self.client.text_generation(
                prompt,
                model=model_id,
                max_new_tokens=kwargs.get("max_tokens", 512),
                temperature=kwargs.get("temperature", 0.7),
                **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
            )
        
        elif provider == "groq":
            return self._call_groq(model_id, prompt, **kwargs)
        
        elif provider == "together":
            return self._call_together(model_id, prompt, **kwargs)
        
        elif provider == "replicate":
            return self._call_replicate(model_id, prompt, **kwargs)
        
        else:
            raise ValueError(f"Unsupported provider for text: {provider}")
    
    def _inference_voice(
        self,
        model_id: str,
        prompt: str,
        provider: str,
        **kwargs
    ) -> bytes:
        """Voice synthesis inference."""
        
        if provider == "replicate":
            return self._call_replicate(model_id, prompt, task="tts", **kwargs)
        
        elif provider == "huggingface" and self.client:
            return self.client.text_to_speech(
                prompt,
                model=model_id
            )
        
        else:
            raise ValueError(f"Unsupported provider for voice: {provider}")
    
    def _inference_image(
        self,
        model_id: str,
        prompt: str,
        provider: str,
        **kwargs
    ) -> bytes:
        """Image generation inference."""
        
        if provider == "huggingface" and self.client:
            return self.client.text_to_image(
                prompt,
                model=model_id,
                **kwargs
            )
        
        elif provider == "replicate":
            return self._call_replicate(model_id, prompt, task="image", **kwargs)
        
        elif provider == "together":
            return self._call_together_image(model_id, prompt, **kwargs)
        
        else:
            raise ValueError(f"Unsupported provider for image: {provider}")
    
    def _call_groq(
        self,
        model_id: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Call Groq API."""
        
        groq_key = os.environ.get("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("GROQ_API_KEY not set")
        
        if HTTPX_AVAILABLE:
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 512),
                    "temperature": kwargs.get("temperature", 0.7)
                },
                timeout=self.config.provider_timeouts.get("groq", 30)
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        
        raise ValueError("httpx not available")
    
    def _call_together(
        self,
        model_id: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Call Together AI API."""
        
        together_key = os.environ.get("TOGETHER_API_KEY")
        if not together_key:
            raise ValueError("TOGETHER_API_KEY not set")
        
        if HTTPX_AVAILABLE:
            response = httpx.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {together_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 512),
                    "temperature": kwargs.get("temperature", 0.7)
                },
                timeout=self.config.provider_timeouts.get("together", 60)
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        
        raise ValueError("httpx not available")
    
    def _call_together_image(
        self,
        model_id: str,
        prompt: str,
        **kwargs
    ) -> bytes:
        """Call Together AI for image generation."""
        
        together_key = os.environ.get("TOGETHER_API_KEY")
        if not together_key:
            raise ValueError("TOGETHER_API_KEY not set")
        
        if HTTPX_AVAILABLE:
            response = httpx.post(
                "https://api.together.xyz/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {together_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "prompt": prompt,
                    "n": 1,
                    "size": kwargs.get("size", "1024x1024")
                },
                timeout=self.config.provider_timeouts.get("together", 60)
            )
            response.raise_for_status()
            
            # Get image URL and download
            image_url = response.json()["data"][0]["url"]
            image_response = httpx.get(image_url)
            return image_response.content
        
        raise ValueError("httpx not available")
    
    def _call_replicate(
        self,
        model_id: str,
        prompt: str,
        task: str = "text",
        **kwargs
    ) -> Any:
        """Call Replicate API."""
        
        try:
            import replicate
        except ImportError:
            raise ValueError("replicate not installed")
        
        if task == "text":
            output = replicate.run(
                model_id,
                input={"prompt": prompt, **kwargs}
            )
            return "".join(output) if hasattr(output, "__iter__") else str(output)
        
        elif task == "tts":
            output = replicate.run(
                model_id,
                input={"text": prompt, **kwargs}
            )
            return output
        
        elif task == "image":
            output = replicate.run(
                model_id,
                input={"prompt": prompt, **kwargs}
            )
            return output
        
        return output
    
    def _get_model_id(self, model_type: str, provider: str) -> Optional[str]:
        """Get model ID for a provider."""
        mappings = self.config.model_mappings.get(model_type, {})
        return mappings.get(provider)
    
    def _get_cache_key(
        self,
        model_type: str,
        prompt: str,
        kwargs: Dict[str, Any]
    ) -> str:
        """Generate cache key."""
        import hashlib
        content = f"{model_type}:{prompt}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _update_metrics(
        self,
        provider: str,
        latency: float,
        success: bool
    ) -> None:
        """Update metrics."""
        if success:
            self._metrics["successes"] += 1
        else:
            self._metrics["failures"] += 1
        
        # Provider usage
        if provider not in self._metrics["provider_usage"]:
            self._metrics["provider_usage"][provider] = 0
        self._metrics["provider_usage"][provider] += 1
        
        # Average latency
        if provider not in self._metrics["avg_latency"]:
            self._metrics["avg_latency"][provider] = []
        if latency > 0:
            self._metrics["avg_latency"][provider].append(latency)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get router metrics."""
        metrics = dict(self._metrics)
        
        # Calculate averages
        avg_latencies = {}
        for provider, latencies in metrics["avg_latency"].items():
            if latencies:
                avg_latencies[provider] = sum(latencies) / len(latencies)
        metrics["avg_latency"] = avg_latencies
        
        return metrics
    
    def clear_cache(self) -> int:
        """Clear the request cache."""
        count = len(self._cache)
        self._cache.clear()
        return count


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

class AsyncInferenceRouter(InferenceRouter):
    """Async version of the inference router."""
    
    async def route_async(
        self,
        model_type: str,
        prompt: str,
        strategy: Optional[RoutingStrategy] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Async route method."""
        # Run sync method in executor for now
        # TODO: Implement true async with aiohttp
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.route(model_type, prompt, strategy, provider, **kwargs)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def route_inference(
    model_type: str,
    prompt: str,
    strategy: str = "fallback",
    provider: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Route an inference request.
    
    Args:
        model_type: Type (brain, voice, image, video)
        prompt: Input prompt
        strategy: Routing strategy (fastest, cheapest, fallback, specific)
        provider: Specific provider for 'specific' strategy
        **kwargs: Model parameters
        
    Returns:
        Inference result
    """
    router = InferenceRouter()
    return router.route(
        model_type,
        prompt,
        RoutingStrategy(strategy) if strategy else None,
        provider,
        **kwargs
    )


def chat(prompt: str, **kwargs) -> str:
    """Quick chat function using brain model."""
    result = route_inference("brain", prompt, **kwargs)
    if result.get("success"):
        return result.get("result", "")
    return f"Error: {result.get('error', 'Unknown error')}"


def generate_voice(text: str, **kwargs) -> Any:
    """Generate voice from text."""
    result = route_inference("voice", text, **kwargs)
    if result.get("success"):
        return result.get("result")
    return None


def generate_image(prompt: str, **kwargs) -> Any:
    """Generate image from prompt."""
    result = route_inference("image", prompt, **kwargs)
    if result.get("success"):
        return result.get("result")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inference Router")
    parser.add_argument("action", choices=["route", "chat", "metrics"])
    parser.add_argument("--model-type", "-m", default="brain")
    parser.add_argument("--prompt", "-p")
    parser.add_argument("--strategy", "-s", default="fallback")
    parser.add_argument("--provider", help="Specific provider")
    
    args = parser.parse_args()
    
    router = InferenceRouter()
    
    if args.action == "route":
        if not args.prompt:
            print("Error: --prompt required")
            sys.exit(1)
        result = router.route(
            args.model_type,
            args.prompt,
            RoutingStrategy(args.strategy),
            args.provider
        )
        print(json.dumps(result, indent=2, default=str))
    
    elif args.action == "chat":
        prompt = args.prompt or input("Enter prompt: ")
        response = chat(prompt)
        print(f"\nResponse: {response}")
    
    elif args.action == "metrics":
        print(json.dumps(router.get_metrics(), indent=2))
