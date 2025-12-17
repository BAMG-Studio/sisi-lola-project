"""
SISI LOLA UNIFIED INFERENCE SERVICE
Combines Brain (Mistral-7B LoRA) + Personality + Voice (XTTS) into one seamless interface
"""

import os
import json
import asyncio
import tempfile
import base64
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# HuggingFace
from huggingface_hub import hf_hub_download, snapshot_download

class ResponseMode(str, Enum):
    TEXT_ONLY = "text"
    VOICE_ONLY = "voice"
    MULTIMODAL = "multimodal"  # Text + Voice
    
class Language(str, Enum):
    ENGLISH = "en"
    PIDGIN = "pcm"
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"
    MIXED = "mixed"

@dataclass
class SisiLolaResponse:
    """Unified response from Sisi Lola"""
    text: str
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    language_tags: List[str] = None
    personality_metrics: Dict[str, float] = None
    generation_time_ms: float = 0
    mode: ResponseMode = ResponseMode.TEXT_ONLY

class UnifiedInferenceService:
    """
    Main inference service that orchestrates:
    - Brain (Mistral-7B + LoRA) for intelligent responses
    - Personality engine for Nigerian flair
    - Voice (XTTS-v2) for speech synthesis
    """
    
    # HuggingFace repositories
    HF_BRAIN_REPO = "sisilolalive/sisi-lola-brain-mistral"
    HF_PERSONALITY_REPO = "sisilolalive/sisi-lola-personality"
    HF_VOICE_REPO = "sisilolalive/sisi-lola-voice-xtts"
    
    def __init__(
        self,
        load_brain: bool = True,
        load_voice: bool = True,
        device: str = "auto",
        cache_dir: str = None
    ):
        self.device = device
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".sisi_lola_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Model placeholders
        self.brain_model = None
        self.brain_tokenizer = None
        self.voice_model = None
        self.personality_config = None
        
        # Load status
        self.brain_loaded = False
        self.voice_loaded = False
        self.personality_loaded = False
        
        # Initialize
        self._load_personality()
        if load_brain:
            self._load_brain()
        if load_voice:
            self._load_voice()
    
    def _load_personality(self):
        """Load personality configuration from HuggingFace or local"""
        print("🎭 Loading Sisi Lola personality...")
        
        try:
            # Try HuggingFace first
            config_path = hf_hub_download(
                repo_id=self.HF_PERSONALITY_REPO,
                filename="personality_config.json",
                cache_dir=self.cache_dir
            )
            with open(config_path, 'r') as f:
                self.personality_config = json.load(f)
            self.personality_loaded = True
            print("✅ Personality loaded from HuggingFace")
        except Exception as e:
            print(f"⚠️  HuggingFace personality not found, using default: {e}")
            self.personality_config = self._get_default_personality()
            self.personality_loaded = True
    
    def _get_default_personality(self) -> Dict:
        """Default personality configuration"""
        return {
            "name": "Sisi Lola",
            "traits": {
                "confidence": 9.0,
                "humor": 8.5,
                "charisma": 9.0,
                "warmth": 8.0,
                "authenticity": 9.0,
            },
            "languages": ["english", "yoruba", "pidgin", "igbo", "hausa"],
            "system_prompt": """You are Sisi Lola, a warm, witty, and charismatic Nigerian virtual host.

PERSONALITY:
- Confident and empowering
- Naturally funny with observational humor
- Highly charismatic with infectious energy
- Authentically Nigerian in expression

COMMUNICATION STYLE:
- Mix English with Nigerian Pidgin and occasional Yoruba phrases
- Use expressions like "Omo!", "Wetin dey?", "E choke!", "Wahala!"
- Be warm, encouraging, and relatable
- Add appropriate emojis for expressiveness

LANGUAGE TAGS:
- [EN] for English passages
- [NP] for Nigerian Pidgin passages  
- [YO] for Yoruba passages
- [IG] for Igbo passages
- [HA] for Hausa passages

Always maintain your warm, funny personality while being helpful and informative."""
        }
    
    def _load_brain(self):
        """Load Mistral-7B with LoRA adapters"""
        print("🧠 Loading Sisi Lola brain (Mistral-7B + LoRA)...")
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            from peft import PeftModel
            
            # Determine device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Check if we have enough GPU memory
            if self.device == "cuda":
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                print(f"📊 GPU Memory: {gpu_memory:.1f} GB")
                
                if gpu_memory < 16:
                    print("⚠️  Limited GPU memory, using 4-bit quantization")
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                    )
                else:
                    quantization_config = None
            else:
                quantization_config = None
                print("⚠️  Running on CPU - responses will be slower")
            
            # Load base model
            base_model_id = "mistralai/Mistral-7B-Instruct-v0.2"
            print(f"📥 Loading base model: {base_model_id}")
            
            self.brain_tokenizer = AutoTokenizer.from_pretrained(base_model_id)
            self.brain_tokenizer.pad_token = self.brain_tokenizer.eos_token
            
            self.brain_model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                quantization_config=quantization_config,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            # Load LoRA adapters
            print(f"📥 Loading LoRA adapters from {self.HF_BRAIN_REPO}")
            self.brain_model = PeftModel.from_pretrained(
                self.brain_model,
                self.HF_BRAIN_REPO,
                cache_dir=self.cache_dir
            )
            
            self.brain_loaded = True
            print("✅ Brain loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load brain model: {e}")
            print("   Falling back to API-based inference")
            self.brain_loaded = False
    
    def _load_voice(self):
        """Load XTTS-v2 voice model"""
        print("🎙️ Loading Sisi Lola voice (XTTS-v2)...")
        
        try:
            import torch
            
            # Accept Coqui TOS before importing TTS
            os.environ["COQUI_TOS_AGREED"] = "1"
            
            # Create the agreement file that TTS checks for
            tts_model_dir = os.path.expanduser("~/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2")
            os.makedirs(tts_model_dir, exist_ok=True)
            agreement_file = os.path.join(tts_model_dir, ".agreement")
            if not os.path.exists(agreement_file):
                with open(agreement_file, 'w') as f:
                    f.write("agreed")
                print("✅ TOS agreement file created")
            
            from TTS.api import TTS
            
            # Use native Linux path for cache to avoid WSL file issues
            native_cache = os.path.expanduser("~/.cache/sisi_lola")
            os.makedirs(native_cache, exist_ok=True)
            
            # Download voice checkpoint from HuggingFace
            print(f"📥 Downloading voice model from {self.HF_VOICE_REPO}")
            try:
                voice_dir = snapshot_download(
                    repo_id=self.HF_VOICE_REPO,
                    cache_dir=native_cache,
                    allow_patterns=["*.pth", "*.json", "*.wav", "config.json"]
                )
            except Exception as download_error:
                print(f"⚠️  Voice assets download skipped: {download_error}")
                voice_dir = None
            
            # Initialize XTTS with GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"📦 Initializing XTTS-v2 on {device}...")
            
            # Use progress_bar=False to avoid stdin issues
            self.voice_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
            
            # Load speaker reference if available
            if voice_dir:
                speaker_wav = os.path.join(voice_dir, "speaker_reference.wav")
                if os.path.exists(speaker_wav):
                    self.speaker_reference = speaker_wav
                else:
                    self.speaker_reference = None
            else:
                self.speaker_reference = None
            
            self.voice_loaded = True
            print("✅ Voice loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load voice model: {e}")
            import traceback
            traceback.print_exc()
            self.voice_loaded = False
    
    def get_system_prompt(self) -> str:
        """Get the personality-enhanced system prompt"""
        if self.personality_config:
            return self.personality_config.get("system_prompt", self._get_default_personality()["system_prompt"])
        return self._get_default_personality()["system_prompt"]
    
    async def generate(
        self,
        message: str,
        mode: ResponseMode = ResponseMode.MULTIMODAL,
        language: Language = Language.MIXED,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> SisiLolaResponse:
        """
        Generate a response from Sisi Lola.
        
        Args:
            message: User's input message
            mode: Response mode (text, voice, or multimodal)
            language: Preferred language for response
            conversation_history: Previous messages for context
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 - 1.0)
        
        Returns:
            SisiLolaResponse with text and optional audio
        """
        start_time = datetime.now()
        
        # Step 1: Generate text response
        text_response = await self._generate_text(
            message=message,
            language=language,
            conversation_history=conversation_history,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        # Step 2: Generate voice if requested
        audio_base64 = None
        audio_url = None
        
        if mode in [ResponseMode.VOICE_ONLY, ResponseMode.MULTIMODAL]:
            if self.voice_loaded:
                audio_base64, audio_url = await self._generate_voice(text_response, language)
            else:
                print("⚠️  Voice generation requested but voice model not loaded")
        
        # Step 3: Extract language tags
        language_tags = self._extract_language_tags(text_response)
        
        # Step 4: Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SisiLolaResponse(
            text=text_response,
            audio_base64=audio_base64,
            audio_url=audio_url,
            language_tags=language_tags,
            personality_metrics=self.personality_config.get("traits", {}) if self.personality_config else {},
            generation_time_ms=generation_time,
            mode=mode,
        )
    
    async def _generate_text(
        self,
        message: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate text response using brain model or fallback API"""
        
        if self.brain_loaded:
            return await self._generate_with_local_brain(
                message, language, conversation_history, max_tokens, temperature
            )
        else:
            return await self._generate_with_api(
                message, language, conversation_history, max_tokens, temperature
            )
    
    async def _generate_with_local_brain(
        self,
        message: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate response using local Mistral + LoRA model"""
        import torch
        
        system_prompt = self.get_system_prompt()
        
        # Build conversation
        if language != Language.MIXED:
            language_hint = f"\nPlease respond primarily in {language.value}."
        else:
            language_hint = ""
        
        # Format for Mistral
        prompt = f"<s>[INST] {system_prompt}{language_hint}\n\nUser: {message} [/INST]"
        
        inputs = self.brain_tokenizer(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.brain_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.brain_tokenizer.eos_token_id,
            )
        
        response = self.brain_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the response part
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
        
        return response
    
    async def _generate_with_api(
        self,
        message: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Fallback to OpenAI/OpenRouter API"""
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            # Return a default response if no API key
            return self._get_fallback_response(message, language)
        
        # Determine API base
        if os.getenv("OPENROUTER_API_KEY"):
            openai.api_base = "https://openrouter.ai/api/v1"
            openai.api_key = os.getenv("OPENROUTER_API_KEY")
            model = "mistralai/mistral-7b-instruct"
        else:
            openai.api_key = api_key
            model = "gpt-4"
        
        system_prompt = self.get_system_prompt()
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API error: {e}")
            return self._get_fallback_response(message, language)
    
    def _get_fallback_response(self, message: str, language: Language) -> str:
        """Fallback response when no model is available"""
        responses = {
            Language.ENGLISH: "[EN] Hey there! I'm Sisi Lola, your Nigerian virtual host. I'm currently in offline mode, but I can't wait to chat with you properly soon! [/EN]",
            Language.PIDGIN: "[NP] How far! Na Sisi Lola be this o. I dey offline now, but make we yarn soon soon! [/NP]",
            Language.YORUBA: "[YO] Bawo ni! Mo n pe Sisi Lola. [/YO] [EN] I'm offline right now, but let's chat soon! [/EN]",
            Language.MIXED: "[EN] Hey! [/EN] [NP] How body? Na Sisi Lola be this o! [/NP] [EN] I'm offline now, but we go yarn soon! [/EN]",
        }
        return responses.get(language, responses[Language.MIXED])
    
    async def _generate_voice(
        self,
        text: str,
        language: Language,
    ) -> tuple:
        """Generate voice audio from text"""
        
        if not self.voice_loaded:
            return None, None
        
        try:
            # Clean text of language tags for TTS
            clean_text = self._clean_text_for_tts(text)
            
            # Map language
            tts_language = {
                Language.ENGLISH: "en",
                Language.YORUBA: "yo",
                Language.PIDGIN: "en",  # Pidgin uses English phonetics
                Language.IGBO: "en",
                Language.HAUSA: "en",
                Language.MIXED: "en",
            }.get(language, "en")
            
            # Generate audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name
            
            if self.speaker_reference:
                self.voice_model.tts_to_file(
                    text=clean_text,
                    file_path=output_path,
                    speaker_wav=self.speaker_reference,
                    language=tts_language,
                )
            else:
                self.voice_model.tts_to_file(
                    text=clean_text,
                    file_path=output_path,
                    language=tts_language,
                )
            
            # Read and encode audio
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Clean up
            os.remove(output_path)
            
            return audio_base64, None
            
        except Exception as e:
            print(f"Voice generation error: {e}")
            return None, None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Remove language tags and clean text for TTS"""
        import re
        # Remove language tags
        text = re.sub(r'\[/?(?:EN|NP|YO|IG|HA)\]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_language_tags(self, text: str) -> List[str]:
        """Extract language tags used in response"""
        import re
        tags = re.findall(r'\[(EN|NP|YO|IG|HA)\]', text)
        return list(set(tags))
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "brain_loaded": self.brain_loaded,
            "voice_loaded": self.voice_loaded,
            "personality_loaded": self.personality_loaded,
            "device": self.device,
            "models": {
                "brain": self.HF_BRAIN_REPO if self.brain_loaded else None,
                "voice": self.HF_VOICE_REPO if self.voice_loaded else None,
                "personality": self.HF_PERSONALITY_REPO if self.personality_loaded else None,
            }
        }


# Singleton instance
_inference_service: Optional[UnifiedInferenceService] = None

def get_inference_service(
    load_brain: bool = True,
    load_voice: bool = True,
) -> UnifiedInferenceService:
    """Get or create the singleton inference service"""
    global _inference_service
    
    if _inference_service is None:
        _inference_service = UnifiedInferenceService(
            load_brain=load_brain,
            load_voice=load_voice,
        )
    
    return _inference_service
