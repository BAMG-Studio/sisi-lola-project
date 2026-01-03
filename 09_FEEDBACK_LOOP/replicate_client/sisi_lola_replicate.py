#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - UNIFIED REPLICATE CLIENT (Brain, Eyes, Voice, Heart)
═══════════════════════════════════════════════════════════════════════════════
Complete Replicate integration with state-of-the-art models for all modalities.

MODALITIES:
🧠 BRAIN (Text/Chat) - Language models, RAG, reasoning
👁️ EYES (Vision) - Image generation, video, scene understanding
🗣️ VOICE (Audio) - TTS, voice cloning, speech recognition
💜 HEART (Personality) - Sentiment, cultural nuance, Nigerian authenticity

STATE-OF-THE-ART MODELS (2026):
- Video: ByteDance Omni-Human (NOT wav2lip!)
- Voice: MiniMax Speech-02-HD, XTTS-v2, RVC
- Image: SeeDream-3, Flux, Ideogram
- LLM: Qwen, Llama, Command-R

Ready-to-deploy examples included!
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import base64
import hashlib
import asyncio
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Literal
from dataclasses import dataclass, field
from enum import Enum
import httpx
from abc import ABC, abstractmethod

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReplicateClient")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class ModelRegistry:
    """
    Central registry of state-of-the-art Replicate models.
    Updated for 2026 best practices.
    """
    
    # 🎬 VIDEO MODELS (State-of-the-art - NO wav2lip!)
    VIDEO = {
        "omni_human": {
            "id": "bytedance/omni-human",
            "description": "Audio-driven realistic talking videos",
            "input_types": ["image", "audio"],
            "output_type": "video",
            "quality": "production",
            "cost_per_sec": 0.05
        },
        "stable_video": {
            "id": "stability-ai/stable-video-diffusion",
            "description": "Image-to-video with subtle motion",
            "input_types": ["image"],
            "output_type": "video",
            "quality": "high",
            "cost_per_sec": 0.03
        },
        "minimax_video": {
            "id": "minimax/video-01-live2d",
            "description": "Anime/2D style video generation",
            "input_types": ["image", "audio"],
            "output_type": "video",
            "quality": "high",
            "cost_per_sec": 0.04
        },
        "kling": {
            "id": "fofr/kling",
            "description": "High-quality video generation",
            "input_types": ["text", "image"],
            "output_type": "video",
            "quality": "production",
            "cost_per_sec": 0.06
        }
    }
    
    # 🗣️ VOICE MODELS
    VOICE = {
        "minimax_speech": {
            "id": "minimax/speech-02-hd",
            "description": "High-quality voiceovers with emotion",
            "input_types": ["text"],
            "output_type": "audio",
            "quality": "production",
            "cost_per_1k_chars": 0.015
        },
        "xtts_v2": {
            "id": "lucataco/xtts-v2",
            "description": "Multilingual voice cloning",
            "input_types": ["text", "audio_reference"],
            "output_type": "audio",
            "quality": "high",
            "cost_per_1k_chars": 0.01
        },
        "rvc": {
            "id": "zsxkib/realistic-voice-cloning",
            "description": "Realistic voice cloning from samples",
            "input_types": ["audio", "audio_reference"],
            "output_type": "audio",
            "quality": "high"
        },
        "tortoise": {
            "id": "afiaka87/tortoise-tts",
            "description": "Slow but very high quality TTS",
            "input_types": ["text"],
            "output_type": "audio",
            "quality": "highest",
            "cost_per_1k_chars": 0.02
        },
        "whisper": {
            "id": "openai/whisper",
            "description": "Speech recognition",
            "input_types": ["audio"],
            "output_type": "text",
            "quality": "production"
        }
    }
    
    # 🖼️ IMAGE MODELS
    IMAGE = {
        "seedream_3": {
            "id": "bytedance/seedream-3",
            "description": "Highest quality image generation",
            "input_types": ["text"],
            "output_type": "image",
            "quality": "highest"
        },
        "flux_schnell": {
            "id": "black-forest-labs/flux-schnell",
            "description": "Fast image generation (<2 seconds)",
            "input_types": ["text"],
            "output_type": "image",
            "quality": "fast"
        },
        "flux_pro": {
            "id": "black-forest-labs/flux-1.1-pro",
            "description": "Professional image generation",
            "input_types": ["text"],
            "output_type": "image",
            "quality": "production"
        },
        "sdxl": {
            "id": "stability-ai/sdxl",
            "description": "Customizable with LoRA",
            "input_types": ["text"],
            "output_type": "image",
            "quality": "high"
        },
        "ideogram": {
            "id": "ideogram-ai/ideogram-v3-turbo",
            "description": "Images with text/logos",
            "input_types": ["text"],
            "output_type": "image",
            "quality": "high"
        },
        "recraft_svg": {
            "id": "recraft-ai/recraft-v3-svg",
            "description": "Vector graphics and icons",
            "input_types": ["text"],
            "output_type": "svg",
            "quality": "high"
        }
    }
    
    # 🧠 LLM MODELS
    LLM = {
        "qwen": {
            "id": "qwen/qwen-2.5-coder-32b-instruct",
            "description": "Coding and instruction following",
            "quality": "production"
        },
        "llama": {
            "id": "meta/llama-3.1-405b-instruct",
            "description": "Large language model",
            "quality": "highest"
        },
        "command_r": {
            "id": "cohere/command-r-plus",
            "description": "RAG optimized",
            "quality": "production"
        }
    }
    
    # 📄 DOCUMENT MODELS
    DOCUMENT = {
        "moondream": {
            "id": "vikhyat/moondream2",
            "description": "Vision-language understanding",
            "input_types": ["image"],
            "output_type": "text"
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class Modality(str, Enum):
    """Sisi Lola modalities."""
    BRAIN = "brain"   # Text/Chat
    EYES = "eyes"     # Vision
    VOICE = "voice"   # Audio
    HEART = "heart"   # Personality/Sentiment
    VIDEO = "video"   # Video generation


@dataclass
class PredictionResult:
    """Result from a Replicate prediction."""
    id: str
    status: str
    output: Any
    metrics: Dict[str, Any]
    model: str
    modality: Modality
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == "succeeded" and self.error is None
    
    @property
    def latency_ms(self) -> float:
        if self.metrics and "predict_time" in self.metrics:
            return self.metrics["predict_time"] * 1000
        return 0


@dataclass  
class SisiLolaConfig:
    """Configuration for Sisi Lola Replicate client."""
    api_token: str
    webhook_url: Optional[str] = None
    
    # Character consistency
    character_seed: int = 45822
    
    # Voice settings
    default_voice_id: str = "e3EHR2GS90EO276k1OCA"  # Nigerian accent
    
    # Quality preferences
    prefer_quality_over_speed: bool = True
    
    # Caching
    enable_cache: bool = True
    cache_dir: Path = field(default_factory=lambda: Path("cache/replicate"))


# ═══════════════════════════════════════════════════════════════════════════════
# BASE REPLICATE CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class ReplicateClient:
    """
    Base Replicate API client with async support and caching.
    """
    
    API_BASE = "https://api.replicate.com/v1"
    
    def __init__(self, config: SisiLolaConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Token {config.api_token}",
            "Content-Type": "application/json"
        }
        
        if config.enable_cache:
            config.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, model: str, input_data: Dict) -> str:
        """Generate cache key from model and input."""
        content = f"{model}:{json.dumps(input_data, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if result is cached."""
        if not self.config.enable_cache:
            return None
        
        cache_file = self.config.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            logger.info(f"💾 Cache HIT: {cache_key[:8]}")
            with open(cache_file) as f:
                return json.load(f)
        return None
    
    def _save_cache(self, cache_key: str, data: Dict):
        """Save result to cache."""
        if not self.config.enable_cache:
            return
        
        cache_file = self.config.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)
    
    async def run(self, model: str, input_data: Dict, 
                  wait: bool = True, timeout: float = 300) -> PredictionResult:
        """
        Run a prediction on Replicate.
        
        Args:
            model: Model identifier (e.g., "bytedance/omni-human")
            input_data: Model input parameters
            wait: Wait for completion
            timeout: Timeout in seconds
            
        Returns:
            PredictionResult
        """
        # Check cache first
        cache_key = self._get_cache_key(model, input_data)
        cached = self._check_cache(cache_key)
        if cached:
            return PredictionResult(**cached)
        
        async with httpx.AsyncClient() as client:
            # Create prediction
            response = await client.post(
                f"{self.API_BASE}/predictions",
                headers=self.headers,
                json={
                    "version": model,
                    "input": input_data,
                    "webhook": self.config.webhook_url
                },
                timeout=30.0
            )
            response.raise_for_status()
            prediction = response.json()
            
            prediction_id = prediction["id"]
            logger.info(f"🚀 Prediction started: {prediction_id}")
            
            if not wait:
                return PredictionResult(
                    id=prediction_id,
                    status="starting",
                    output=None,
                    metrics={},
                    model=model,
                    modality=Modality.BRAIN,
                    created_at=prediction.get("created_at", "")
                )
            
            # Poll for completion
            start_time = time.time()
            while time.time() - start_time < timeout:
                response = await client.get(
                    f"{self.API_BASE}/predictions/{prediction_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                prediction = response.json()
                
                status = prediction["status"]
                
                if status == "succeeded":
                    result = PredictionResult(
                        id=prediction_id,
                        status="succeeded",
                        output=prediction.get("output"),
                        metrics=prediction.get("metrics", {}),
                        model=model,
                        modality=Modality.BRAIN,
                        created_at=prediction.get("created_at", ""),
                        completed_at=prediction.get("completed_at")
                    )
                    self._save_cache(cache_key, result.__dict__)
                    logger.info(f"✅ Prediction complete: {prediction_id}")
                    return result
                
                elif status == "failed":
                    return PredictionResult(
                        id=prediction_id,
                        status="failed",
                        output=None,
                        metrics={},
                        model=model,
                        modality=Modality.BRAIN,
                        created_at=prediction.get("created_at", ""),
                        error=prediction.get("error")
                    )
                
                await asyncio.sleep(2)
            
            raise TimeoutError(f"Prediction {prediction_id} timed out after {timeout}s")
    
    async def run_sync(self, model: str, input_data: Dict) -> PredictionResult:
        """Synchronous wrapper for run()."""
        return await self.run(model, input_data, wait=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA BRAIN (Text/Chat)
# ═══════════════════════════════════════════════════════════════════════════════

class SisiLolaBrain:
    """
    🧠 Sisi Lola's Brain - Language understanding and generation.
    
    Features:
    - Nigerian Pidgin understanding
    - Cultural context awareness
    - RAG-ready responses
    - Personality consistency
    """
    
    PERSONALITY_PROMPT = """You are Sisi Lola, a vibrant Nigerian AI assistant with:
- Deep knowledge of Nigerian culture, languages (Yoruba, Hausa, Igbo, Pidgin)
- Warm, friendly, and sometimes playful personality
- Professional expertise in various domains
- Cultural sensitivity and authenticity

Respond naturally, mixing English with Nigerian Pidgin when appropriate.
Use expressions like "How far?", "No wahala", "Oya let's go!" naturally."""
    
    def __init__(self, client: ReplicateClient):
        self.client = client
    
    async def think(self, prompt: str, 
                    system_prompt: Optional[str] = None,
                    context: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using Sisi Lola's personality.
        
        Args:
            prompt: User input
            system_prompt: Override personality prompt
            context: Previous conversation context
            
        Returns:
            Generated response
        """
        system = system_prompt or self.PERSONALITY_PROMPT
        
        # Build messages
        messages = [{"role": "system", "content": system}]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": prompt})
        
        # Use Qwen for fast, high-quality responses
        result = await self.client.run(
            ModelRegistry.LLM["qwen"]["id"],
            {
                "prompt": prompt,
                "system_prompt": system,
                "max_tokens": 1024,
                "temperature": 0.7
            }
        )
        
        if result.success:
            return result.output
        else:
            logger.error(f"Brain error: {result.error}")
            return "Abeg, something no work well. Make we try again?"
    
    async def understand(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for intent, sentiment, and entities.
        """
        analysis_prompt = f"""Analyze this text and return JSON:
Text: "{text}"

Return:
{{
    "intent": "question|statement|command|greeting|farewell",
    "sentiment": "positive|negative|neutral",
    "language": "english|pidgin|yoruba|hausa|igbo|mixed",
    "entities": ["list", "of", "entities"],
    "nigerian_context": true/false
}}"""
        
        result = await self.client.run(
            ModelRegistry.LLM["qwen"]["id"],
            {
                "prompt": analysis_prompt,
                "max_tokens": 256,
                "temperature": 0.1
            }
        )
        
        if result.success:
            try:
                return json.loads(result.output)
            except:
                return {"raw": result.output}
        
        return {"error": result.error}


# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA EYES (Vision)
# ═══════════════════════════════════════════════════════════════════════════════

class SisiLolaEyes:
    """
    👁️ Sisi Lola's Eyes - Image generation and understanding.
    
    Features:
    - Character-consistent image generation (SEED 45822)
    - Nigerian/African aesthetic awareness
    - Multiple quality tiers
    - Logo and text generation
    """
    
    DNA_PROMPT = """Beautiful Nigerian woman, Sisi Lola character,
professional appearance, warm expression, African elegance,
Lagos luxury aesthetic, character seed 45822"""
    
    def __init__(self, client: ReplicateClient, config: SisiLolaConfig):
        self.client = client
        self.config = config
    
    async def generate_image(self, prompt: str,
                              style: str = "professional",
                              quality: str = "high",
                              aspect_ratio: str = "1:1",
                              include_character: bool = False) -> str:
        """
        Generate an image.
        
        Args:
            prompt: Image description
            style: "professional", "casual", "cultural", "artistic"
            quality: "fast", "high", "highest"
            aspect_ratio: "1:1", "16:9", "9:16"
            include_character: Include Sisi Lola character
            
        Returns:
            URL of generated image
        """
        # Add character prompt if needed
        if include_character:
            prompt = f"{self.DNA_PROMPT}, {prompt}"
        
        # Select model based on quality
        if quality == "fast":
            model = ModelRegistry.IMAGE["flux_schnell"]["id"]
        elif quality == "highest":
            model = ModelRegistry.IMAGE["seedream_3"]["id"]
        else:
            model = ModelRegistry.IMAGE["flux_pro"]["id"]
        
        input_data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "seed": self.config.character_seed if include_character else None
        }
        
        result = await self.client.run(model, input_data)
        
        if result.success:
            # Return first image URL
            if isinstance(result.output, list):
                return result.output[0]
            return result.output
        else:
            logger.error(f"Eyes error: {result.error}")
            return None
    
    async def generate_logo(self, text: str, style: str = "modern") -> str:
        """Generate logo or text-based image."""
        prompt = f"Logo design, text '{text}', {style} style, clean, professional"
        
        result = await self.client.run(
            ModelRegistry.IMAGE["ideogram"]["id"],
            {
                "prompt": prompt,
                "aspect_ratio": "1:1"
            }
        )
        
        if result.success:
            return result.output[0] if isinstance(result.output, list) else result.output
        return None
    
    async def understand_image(self, image_url: str, question: str = "Describe this image") -> str:
        """Analyze and understand an image."""
        result = await self.client.run(
            ModelRegistry.DOCUMENT["moondream"]["id"],
            {
                "image": image_url,
                "prompt": question
            }
        )
        
        if result.success:
            return result.output
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA VOICE (Audio)
# ═══════════════════════════════════════════════════════════════════════════════

class SisiLolaVoice:
    """
    🗣️ Sisi Lola's Voice - Speech synthesis and recognition.
    
    Features:
    - Nigerian accent authenticity
    - Voice cloning capability
    - Emotional expression
    - Multilingual support (Yoruba, Hausa, Igbo, Pidgin)
    """
    
    # Nigerian pronunciation mappings
    NAIJA_PRONUNCIATIONS = {
        "Lagos": "Lay-gos",
        "Naija": "Nai-jah",
        "Sisi": "Cee-cee",
        "wahala": "wa-ha-la",
        "Abuja": "Ah-boo-jah",
        "Oya": "Oh-ya",
        "abeg": "ah-beg",
        "wetin": "way-teen"
    }
    
    def __init__(self, client: ReplicateClient, config: SisiLolaConfig):
        self.client = client
        self.config = config
    
    def normalize_for_pronunciation(self, text: str) -> str:
        """Adjust text for proper Nigerian pronunciation."""
        for word, pronunciation in self.NAIJA_PRONUNCIATIONS.items():
            text = text.replace(word, pronunciation)
        return text
    
    async def speak(self, text: str,
                    voice_id: Optional[str] = None,
                    emotion: str = "neutral",
                    speed: float = 1.0) -> str:
        """
        Convert text to speech with Nigerian accent.
        
        Args:
            text: Text to speak
            voice_id: Override voice
            emotion: "neutral", "happy", "serious", "excited"
            speed: Speech rate (0.5 to 2.0)
            
        Returns:
            URL of generated audio
        """
        normalized_text = self.normalize_for_pronunciation(text)
        
        result = await self.client.run(
            ModelRegistry.VOICE["minimax_speech"]["id"],
            {
                "text": normalized_text,
                "voice_id": voice_id or self.config.default_voice_id,
                "speed": speed
            }
        )
        
        if result.success:
            return result.output
        
        logger.error(f"Voice error: {result.error}")
        return None
    
    async def clone_voice(self, reference_audio_url: str,
                          text: str) -> str:
        """
        Clone a voice from reference audio.
        
        Args:
            reference_audio_url: URL to reference audio (6+ seconds)
            text: Text to speak in cloned voice
            
        Returns:
            URL of generated audio
        """
        result = await self.client.run(
            ModelRegistry.VOICE["xtts_v2"]["id"],
            {
                "text": text,
                "speaker_wav": reference_audio_url,
                "language": "en"
            }
        )
        
        if result.success:
            return result.output
        return None
    
    async def transcribe(self, audio_url: str,
                         language: str = "auto") -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_url: URL to audio file
            language: Language code or "auto"
            
        Returns:
            Transcribed text
        """
        result = await self.client.run(
            ModelRegistry.VOICE["whisper"]["id"],
            {
                "audio": audio_url,
                "language": language if language != "auto" else None
            }
        )
        
        if result.success:
            if isinstance(result.output, dict):
                return result.output.get("transcription", result.output.get("text", ""))
            return result.output
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA VIDEO (State-of-the-Art - NO WAV2LIP!)
# ═══════════════════════════════════════════════════════════════════════════════

class SisiLolaVideo:
    """
    🎬 Sisi Lola's Video - State-of-the-art video generation.
    
    Uses ByteDance Omni-Human and other production-quality models.
    NO wav2lip - that's outdated and low quality!
    
    Features:
    - Audio-driven realistic talking videos
    - Character-consistent generation
    - High-quality lip sync and expressions
    - Nigerian presenter style
    """
    
    def __init__(self, client: ReplicateClient, config: SisiLolaConfig):
        self.client = client
        self.config = config
    
    async def create_talking_video(self,
                                    image_url: str,
                                    audio_url: str,
                                    duration: Optional[float] = None) -> str:
        """
        Create talking video from image and audio using Omni-Human.
        
        This is STATE-OF-THE-ART - NOT wav2lip!
        
        Args:
            image_url: URL to portrait image
            audio_url: URL to driving audio
            duration: Optional duration limit
            
        Returns:
            URL of generated video
        """
        logger.info("🎬 Creating talking video with Omni-Human (state-of-the-art)")
        
        result = await self.client.run(
            ModelRegistry.VIDEO["omni_human"]["id"],
            {
                "image": image_url,
                "audio": audio_url,
                "resolution": "720p"
            },
            timeout=600  # Video generation takes time
        )
        
        if result.success:
            logger.info("✅ Talking video generated successfully")
            return result.output
        
        logger.error(f"Video error: {result.error}")
        return None
    
    async def create_motion_video(self, image_url: str,
                                   motion_type: str = "subtle") -> str:
        """
        Create motion video from static image.
        
        Args:
            image_url: URL to source image
            motion_type: "subtle", "dynamic", "zoom"
            
        Returns:
            URL of generated video
        """
        result = await self.client.run(
            ModelRegistry.VIDEO["stable_video"]["id"],
            {
                "input_image": image_url,
                "motion_bucket_id": 40 if motion_type == "subtle" else 80,
                "fps": 24
            },
            timeout=300
        )
        
        if result.success:
            return result.output
        return None
    
    async def create_video_from_text(self, prompt: str,
                                      image_url: Optional[str] = None,
                                      duration: int = 5) -> str:
        """
        Create video from text prompt.
        
        Args:
            prompt: Video description
            image_url: Optional starting frame
            duration: Video duration in seconds
            
        Returns:
            URL of generated video
        """
        input_data = {
            "prompt": prompt,
            "duration": duration
        }
        
        if image_url:
            input_data["image"] = image_url
        
        result = await self.client.run(
            ModelRegistry.VIDEO["kling"]["id"],
            input_data,
            timeout=600
        )
        
        if result.success:
            return result.output
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA HEART (Personality & Culture)
# ═══════════════════════════════════════════════════════════════════════════════

class SisiLolaHeart:
    """
    💜 Sisi Lola's Heart - Personality, sentiment, and cultural nuance.
    
    Features:
    - Nigerian cultural understanding
    - Sentiment analysis with Nigerian context
    - Code-switching awareness
    - Pidgin/local language detection
    """
    
    # Nigerian cultural markers
    NIGERIAN_MARKERS = {
        "greetings": ["how far", "how body", "e kaaro", "sannu"],
        "affirmations": ["no wahala", "na so", "ehen", "o dabo"],
        "expressions": ["wahala", "gbedu", "japa", "oga", "sabi"]
    }
    
    def __init__(self, brain: SisiLolaBrain):
        self.brain = brain
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment with Nigerian cultural context.
        """
        analysis = await self.brain.understand(text)
        
        # Enhance with Nigerian markers
        text_lower = text.lower()
        
        markers_found = []
        for category, markers in self.NIGERIAN_MARKERS.items():
            for marker in markers:
                if marker in text_lower:
                    markers_found.append({"category": category, "marker": marker})
        
        analysis["nigerian_markers"] = markers_found
        analysis["cultural_score"] = len(markers_found) / 10.0
        
        return analysis
    
    async def adapt_response(self, response: str, 
                              formality: str = "casual",
                              language_mix: float = 0.3) -> str:
        """
        Adapt response for Nigerian cultural context.
        
        Args:
            response: Original response
            formality: "formal", "casual", "pidgin"
            language_mix: How much Pidgin to include (0.0 to 1.0)
            
        Returns:
            Culturally adapted response
        """
        adaptation_prompt = f"""Adapt this response for a Nigerian audience:

Original: "{response}"

Style: {formality}
Pidgin level: {int(language_mix * 100)}%

Rules:
- Keep the meaning intact
- Add appropriate Nigerian expressions
- {'Use formal English' if formality == 'formal' else 'Mix in Pidgin naturally'}
- Sound authentic and warm

Return only the adapted text."""
        
        return await self.brain.think(adaptation_prompt)


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED SISI LOLA CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class SisiLolaReplicate:
    """
    🇳🇬 Complete Sisi Lola Replicate Client
    
    Unified access to all modalities:
    - brain: Text/Chat
    - eyes: Vision/Images
    - voice: Audio/Speech
    - video: Video generation
    - heart: Personality/Culture
    
    Usage:
        sisi = SisiLolaReplicate(api_token="...")
        
        # Generate image
        image = await sisi.eyes.generate_image("Nigerian cityscape")
        
        # Create voice
        audio = await sisi.voice.speak("How far, my people!")
        
        # Create talking video (state-of-the-art!)
        video = await sisi.video.create_talking_video(image, audio)
    """
    
    def __init__(self, api_token: Optional[str] = None,
                 webhook_url: Optional[str] = None):
        """
        Initialize Sisi Lola Replicate client.
        
        Args:
            api_token: Replicate API token (or REPLICATE_API_TOKEN env var)
            webhook_url: Optional webhook URL for async predictions
        """
        token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not token:
            raise ValueError("Replicate API token required")
        
        self.config = SisiLolaConfig(
            api_token=token,
            webhook_url=webhook_url
        )
        
        self._client = ReplicateClient(self.config)
        
        # Initialize modalities
        self.brain = SisiLolaBrain(self._client)
        self.eyes = SisiLolaEyes(self._client, self.config)
        self.voice = SisiLolaVoice(self._client, self.config)
        self.video = SisiLolaVideo(self._client, self.config)
        self.heart = SisiLolaHeart(self.brain)
        
        logger.info("🇳🇬 Sisi Lola Replicate Client initialized")
        logger.info("   Modalities: brain, eyes, voice, video, heart")
    
    async def produce_content(self,
                               text: str,
                               modality: str = "all",
                               vibe: str = "default") -> Dict[str, Any]:
        """
        Produce complete content package.
        
        Args:
            text: Content script/prompt
            modality: "all", "image", "audio", "video"
            vibe: Content style/mood
            
        Returns:
            Dictionary with all generated assets
        """
        results = {
            "text": text,
            "vibe": vibe,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate image
        if modality in ["all", "image", "video"]:
            image_url = await self.eyes.generate_image(
                f"Nigerian presenter, {vibe} style, professional broadcast quality",
                include_character=True
            )
            results["image_url"] = image_url
        
        # Generate audio
        if modality in ["all", "audio", "video"]:
            audio_url = await self.voice.speak(text)
            results["audio_url"] = audio_url
        
        # Generate video (state-of-the-art!)
        if modality in ["all", "video"]:
            if results.get("image_url") and results.get("audio_url"):
                video_url = await self.video.create_talking_video(
                    results["image_url"],
                    results["audio_url"]
                )
                results["video_url"] = video_url
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# READY-TO-DEPLOY EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

async def example_text_to_video():
    """
    Example: Complete text-to-video pipeline.
    
    This creates a talking video from just text input!
    """
    sisi = SisiLolaReplicate()
    
    script = "How far, my people! Welcome to Sisi Lola TV. Today we dey talk about tech!"
    
    result = await sisi.produce_content(
        text=script,
        modality="video",
        vibe="tech_review"
    )
    
    print(f"✅ Video generated: {result['video_url']}")
    return result


async def example_voice_cloning():
    """
    Example: Clone a Nigerian voice from samples.
    """
    sisi = SisiLolaReplicate()
    
    # Reference audio (6+ seconds of target voice)
    reference_url = "https://example.com/nigerian_voice_sample.wav"
    
    cloned_audio = await sisi.voice.clone_voice(
        reference_audio_url=reference_url,
        text="This is Sisi Lola speaking with my unique Nigerian accent!"
    )
    
    print(f"✅ Cloned voice: {cloned_audio}")
    return cloned_audio


async def example_image_generation():
    """
    Example: Generate character-consistent images.
    """
    sisi = SisiLolaReplicate()
    
    # Generate with Sisi Lola character (SEED 45822)
    image = await sisi.eyes.generate_image(
        prompt="hosting a tech show in Lagos studio",
        style="professional",
        quality="highest",
        include_character=True
    )
    
    print(f"✅ Image generated: {image}")
    return image


async def example_cultural_chat():
    """
    Example: Chat with Nigerian cultural awareness.
    """
    sisi = SisiLolaReplicate()
    
    # User message with Pidgin
    user_message = "Oga, how far? Wetin dey happen for Lagos today?"
    
    # Analyze sentiment and cultural markers
    analysis = await sisi.heart.analyze_sentiment(user_message)
    print(f"Cultural analysis: {analysis}")
    
    # Generate culturally-appropriate response
    response = await sisi.brain.think(user_message)
    
    # Adapt for casual Nigerian context
    adapted = await sisi.heart.adapt_response(response, formality="casual")
    
    print(f"Response: {adapted}")
    return adapted


async def example_tutorial_video():
    """
    Example: Create a tutorial video.
    """
    sisi = SisiLolaReplicate()
    
    tutorial_script = """
    E kaabo! Welcome to this tutorial on how to use Python for data analysis.
    First, make sure you don install Python on your computer.
    No wahala, I go show you step by step how to do am.
    """
    
    result = await sisi.produce_content(
        text=tutorial_script,
        modality="video",
        vibe="educational"
    )
    
    print(f"✅ Tutorial video: {result['video_url']}")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Replicate Client")
    parser.add_argument("--action", choices=["video", "voice", "image", "chat"],
                        required=True, help="Action to perform")
    parser.add_argument("--text", type=str, help="Text input")
    parser.add_argument("--image", type=str, help="Image URL")
    parser.add_argument("--audio", type=str, help="Audio URL")
    
    args = parser.parse_args()
    
    async def run():
        sisi = SisiLolaReplicate()
        
        if args.action == "video":
            result = await sisi.produce_content(
                text=args.text or "Hello from Sisi Lola!",
                modality="video"
            )
            print(json.dumps(result, indent=2))
        
        elif args.action == "voice":
            audio = await sisi.voice.speak(args.text or "How far, my people!")
            print(f"Audio: {audio}")
        
        elif args.action == "image":
            image = await sisi.eyes.generate_image(
                args.text or "Nigerian tech presenter",
                include_character=True
            )
            print(f"Image: {image}")
        
        elif args.action == "chat":
            response = await sisi.brain.think(args.text or "How far?")
            print(f"Response: {response}")
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
