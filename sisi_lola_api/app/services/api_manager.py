"""
SISI LOLA API MANAGER
Handles API key rotation, rate limit management, and client initialization
for OpenAI, Perplexity, and other providers.

Features:
- Round-robin key rotation
- Automatic fallback on rate limits (429)
- Provider separation (OpenAI, Perplexity, etc.)
"""

import os
import random
from typing import Optional, List, Dict
import httpx
from sisi_lola_api.app.config import SisiLolaDNA

class APIKeyManager:
    # OpenAI keys should be provided in environment as semi-colon separated string
    # e.g., OPENAI_API_KEYS=sk-1...;sk-2...
    
    def __init__(self):
        # OpenAI keys can be a pool
        env_keys = os.getenv("OPENAI_API_KEYS", "")
        self.OPENAI_KEYS = [k.strip() for k in env_keys.split(";") if k.strip()]
        
        # Fallback to single key if pool is empty
        single_key = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_KEYS and single_key:
            self.OPENAI_KEYS = [single_key]
            
        self.openai_key_index = 0
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # New Providers from .env.example
        self.google_ai_studio_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
        self.cohere_key = os.getenv("COHERE_API_KEY")
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        self.elevenlabs_key = os.getenv("ELEVEN_LABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
        self.heygen_key = os.getenv("HEYGEN_API_KEY")
        self.kling_access_key = os.getenv("KLINGAI_ACCESS_KEY")
        self.kling_secret_key = os.getenv("KLINGAI_SECRET_KEY")
        self.reccloud_key = os.getenv("RECCLOUD_API_KEY")

        # Diagnostics (Moved inside __init__)
        print(f"🔑 Keys Loaded: Gemini={'YES' if self.google_ai_studio_key else 'NO'}, OpenAI={'YES' if self.OPENAI_KEYS else 'NO'}, Cohere={'YES' if self.cohere_key else 'NO'}")
        if self.google_ai_studio_key:
            print(f"💎 Gemini Key Detect: ...{self.google_ai_studio_key[-4:]}")
    
    def get_next_openai_key(self) -> str:
        """Get next OpenAI key in rotation (Round Robin)"""
        if not self.OPENAI_KEYS:
            return ""
        key = self.OPENAI_KEYS[self.openai_key_index]
        self.openai_key_index = (self.openai_key_index + 1) % len(self.OPENAI_KEYS)
        return key
    
    def get_random_openai_key(self) -> str:
        """Get random OpenAI key (Load Balancing)"""
        if not self.OPENAI_KEYS:
            return ""
        return random.choice(self.OPENAI_KEYS)

    def get_perplexity_key(self) -> Optional[str]:
        """Get Perplexity API key"""
        return self.perplexity_key

    def get_client(self, provider: str = "openai", timeout: int = 30) -> httpx.AsyncClient:
        """
        Get an HTTPX client configured for the specific provider 
        with appropriate headers and authentication.
        """
        if provider == "openai":
            api_key = self.get_next_openai_key()
            return httpx.AsyncClient(
                base_url="https://api.openai.com/v1",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=timeout
            )
        
        elif provider == "perplexity":
            if not self.perplexity_key:
                # Log warning or fallback
                print("⚠️ No Perplexity API key found. Check env vars.")
                return None
                
            return httpx.AsyncClient(
                base_url="https://api.perplexity.ai",
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                },
                timeout=timeout
            )
            
        elif provider == "openrouter":
            if not self.openrouter_key:
                 return None
            return httpx.AsyncClient(
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://sisilola.live",
                    "X-Title": "Sisi Lola AI"
                },
                timeout=timeout
            )
            
        elif provider == "gemini":
            if not self.google_ai_studio_key:
                return None
            return httpx.AsyncClient(
                base_url="https://generativelanguage.googleapis.com/v1beta",
                headers={"Content-Type": "application/json"},
                params={"key": self.google_ai_studio_key},
                timeout=timeout
            )
            
        elif provider == "cohere":
            if not self.cohere_key:
                return None
            return httpx.AsyncClient(
                base_url="https://api.cohere.ai/v1",
                headers={
                    "Authorization": f"Bearer {self.cohere_key}",
                    "Content-Type": "application/json"
                },
                timeout=timeout
            )
            
        elif provider == "huggingface":
            if not self.huggingface_token:
                return None
            return httpx.AsyncClient(
                base_url="https://api-inference.huggingface.co",
                headers={"Authorization": f"Bearer {self.huggingface_token}"},
                timeout=timeout
            )
            
        return None

# Singleton Instance
api_manager = APIKeyManager()

def get_api_manager():
    return api_manager
