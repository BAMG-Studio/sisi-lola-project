"""
SISI LOLA ENHANCED INFERENCE SERVICE
Upgraded inference with training data collection, enhanced prompts, and multimodal support.

Integrates:
- EnhancedPromptEngine for better responses
- TrainingDataCollector for retraining data
- MultimodalInputProcessor for URL/file ingestion
- Language consistency post-processing
"""

import os
import json
import asyncio
import tempfile
import base64
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# HuggingFace
from huggingface_hub import hf_hub_download, snapshot_download

# Local services
from .prompt_engine import (
    EnhancedPromptEngine, 
    get_prompt_engine, 
    PromptMode, 
    LanguageStyle
)
from .training_data_collector import (
    TrainingDataCollector,
    get_training_collector,
    ConversationQuality
)
from .multimodal_processor import (
    MultimodalInputProcessor,
    get_multimodal_processor,
    InputType
)
from .personality_modes import (
    PersonalityModesEngine,
    get_personality_modes,
    PrimaryLanguage,
    LanguageMode,
    MoodPreset
)
from .training_reinforcement import (
    TrainingReinforcementEngine,
    get_training_engine,
    TrainingFocus
)

try:
    from .mms_service import mms_service
except ImportError:
    mms_service = None


class ResponseMode(str, Enum):
    TEXT_ONLY = "text"
    VOICE_ONLY = "voice"
    MULTIMODAL = "multimodal"
    
class Language(str, Enum):
    ENGLISH = "en"
    PIDGIN = "pcm"
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"
    YORUNGLISH = "yoen"
    MIXED = "mixed"


@dataclass
class SisiLolaResponse:
    """Enhanced response from Sisi Lola"""
    text: str
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    language_tags: List[str] = None
    personality_metrics: Dict[str, float] = None
    generation_time_ms: float = 0
    mode: ResponseMode = ResponseMode.TEXT_ONLY
    prompt_mode: str = "standard"
    training_data_logged: bool = False
    quality_score: float = 0.0
    multimodal_analysis: Dict = None


class EnhancedInferenceService:
    """
    Enhanced inference service with:
    - Better prompts for coherent responses
    - Training data collection
    - Multimodal input processing
    - Language consistency
    - Special command handling (/BAMG-STUDIO, /REPORT)
    """
    
    HF_BRAIN_REPO = "sisilolalive/sisi-lola-brain-mistral"
    HF_PERSONALITY_REPO = "sisilolalive/sisi-lola-personality"
    HF_VOICE_REPO = "sisilolalive/sisi-lola-voice-xtts"
    
    def __init__(
        self,
        load_brain: bool = True,
        load_voice: bool = False,  # Default off for faster startup
        device: str = "auto",
        cache_dir: str = None,
        collect_training_data: bool = True
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
        
        # Enhanced components
        self.prompt_engine = get_prompt_engine()
        self.training_collector = get_training_collector() if collect_training_data else None
        self.multimodal_processor = get_multimodal_processor()
        self.personality_modes = get_personality_modes()
        self.training_engine = get_training_engine()
        
        # Session tracking
        self.active_sessions: Dict[str, Dict] = {}
        
        # Initialize
        self._load_personality()
        if load_brain:
            self._load_brain()
        if load_voice:
            self._load_voice()
    
    def _load_personality(self):
        """Load enhanced personality configuration"""
        print("🎭 Loading Sisi Lola personality...")
        
        try:
            config_path = hf_hub_download(
                repo_id=self.HF_PERSONALITY_REPO,
                filename="personality_config.json",
                cache_dir=self.cache_dir
            )
            with open(config_path, 'r') as f:
                self.personality_config = json.load(f)
            
            # Merge with enhanced prompt engine
            self.personality_config["enhanced_prompt"] = True
            self.personality_loaded = True
            print("✅ Personality loaded from HuggingFace")
        except Exception as e:
            print(f"⚠️  Using default personality: {e}")
            self.personality_config = self._get_default_personality()
            self.personality_loaded = True
    
    def _get_default_personality(self) -> Dict:
        """Enhanced default personality"""
        return {
            "name": "Sisi Lola",
            "traits": {
                "confidence": 9.0,
                "humor": 8.5,
                "charisma": 9.0,
                "warmth": 8.0,
                "authenticity": 9.0,
                "wisdom": 8.0,
            },
            "languages": ["english", "yoruba", "pidgin", "igbo", "hausa", "yorunglish"],
            "default_style": "yorunglish",
            "enhanced_prompt": True,
        }
    
    def _load_brain(self):
        """Load Mistral-7B with LoRA adapters"""
        print("🧠 Loading Sisi Lola brain (Mistral-7B + LoRA)...")
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            from peft import PeftModel
            
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            if self.device == "cuda":
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                print(f"📊 GPU Memory: {gpu_memory:.1f} GB")
                
                if gpu_memory < 16:
                    print("⚠️  Using 4-bit quantization for memory efficiency")
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
            
            print(f"📥 Loading LoRA adapters from {self.HF_BRAIN_REPO}")
            try:
                self.brain_model = PeftModel.from_pretrained(
                    self.brain_model,
                    self.HF_BRAIN_REPO,
                    cache_dir=self.cache_dir
                )
                print("✅ LoRA adapters loaded!")
            except Exception as lora_error:
                print(f"⚠️  LoRA adapters not loaded: {lora_error}")
                print("   Using base Mistral model")
            
            self.brain_loaded = True
            print("✅ Brain loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load brain: {e}")
            print("   Will use API-based inference as fallback")
            self.brain_loaded = False
    
    def _load_voice(self):
        """Load XTTS-v2 voice model"""
        print("🎙️ Loading Sisi Lola voice (XTTS-v2)...")
        
        try:
            from TTS.api import TTS
            
            print(f"📥 Downloading voice model from {self.HF_VOICE_REPO}")
            voice_dir = snapshot_download(
                repo_id=self.HF_VOICE_REPO,
                cache_dir=self.cache_dir,
                allow_patterns=["*.pth", "*.json", "*.wav", "config.json"]
            )
            
            self.voice_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            speaker_wav = os.path.join(voice_dir, "speaker_reference.wav")
            self.speaker_reference = speaker_wav if os.path.exists(speaker_wav) else None
            
            self.voice_loaded = True
            print("✅ Voice loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Voice not loaded: {e}")
            self.voice_loaded = False
    
    def update_session_personality(
        self,
        session_id: str,
        primary_language: PrimaryLanguage = None,
        language_mode: LanguageMode = None,
        mood: MoodPreset = None,
        user_name: str = None
    ) -> bool:
        """Update personality settings for an existing session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Update settings if provided
        if primary_language is not None:
            session["primary_language"] = primary_language
        if language_mode is not None:
            session["language_mode"] = language_mode
        if mood is not None:
            session["mood"] = mood
        if user_name is not None:
            session["user_name"] = user_name
        
        # Rebuild personality prompt
        session["personality_prompt"] = self.personality_modes.build_personality_prompt(
            language=session.get("primary_language", PrimaryLanguage.YORUNGLISH),
            mode=session.get("language_mode", LanguageMode.HEAVY),
            mood=session.get("mood", MoodPreset.DEFAULT),
            user_name=session.get("user_name")
        )
        
        return True
    
    def get_session_greeting(self, session_id: str) -> str:
        """Get a contextual greeting for the session"""
        if session_id not in self.active_sessions:
            return self.personality_modes.get_random_greeting(
                PrimaryLanguage.YORUNGLISH,
                LanguageMode.HEAVY,
                None
            )
        
        session = self.active_sessions[session_id]
        return self.personality_modes.get_random_greeting(
            session.get("primary_language", PrimaryLanguage.YORUNGLISH),
            session.get("language_mode", LanguageMode.HEAVY),
            session.get("user_name")
        )
    
    def get_training_dashboard(self) -> Dict:
        """Get training reinforcement dashboard data"""
        return self.training_engine.get_training_dashboard()

    def start_session(
        self,
        session_id: str = None,
        user_id: str = "anonymous",
        primary_language: PrimaryLanguage = PrimaryLanguage.YORUNGLISH,
        language_mode: LanguageMode = LanguageMode.HEAVY,
        mood: MoodPreset = MoodPreset.DEFAULT,
        user_name: str = None
    ) -> str:
        """Start a conversation session with training data collection and personality modes"""
        import uuid
        session_id = session_id or str(uuid.uuid4())[:8]
        
        # Get personality prompt
        personality_prompt = self.personality_modes.build_personality_prompt(
            language=primary_language,
            mode=language_mode,
            mood=mood,
            user_name=user_name
        )
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "user_name": user_name,
            "started_at": datetime.now().isoformat(),
            "conversation_history": [],
            "prompt_mode": PromptMode.STANDARD,
            "language_style": LanguageStyle.YORUNGLISH,
            "is_developer": False,
            # New personality mode settings
            "primary_language": primary_language,
            "language_mode": language_mode,
            "mood": mood,
            "personality_prompt": personality_prompt,
        }
        
        if self.training_collector:
            self.training_collector.start_session(session_id, user_id)
        
        return session_id
    
    async def generate(
        self,
        message: str,
        session_id: str = None,
        mode: ResponseMode = ResponseMode.MULTIMODAL,
        language: Language = Language.MIXED,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> SisiLolaResponse:
        """
        Generate enhanced response with training data collection.
        """
        start_time = datetime.now()
        
        # Ensure session exists
        if session_id not in self.active_sessions:
            session_id = self.start_session(session_id)
        
        session = self.active_sessions[session_id]
        
        # Step 1: Detect special commands
        command_info = self.prompt_engine.detect_special_commands(message)
        if command_info["has_command"]:
            session["prompt_mode"] = command_info["mode"]
            if command_info["mode"] == PromptMode.DEVELOPER:
                session["is_developer"] = True
            message = command_info["remaining_message"]
        
        # Step 2: Process multimodal input (URLs, files)
        multimodal_analysis = None
        processed_message = message
        
        urls = re.findall(r'https?://\S+', message)
        if urls:
            for url in urls:
                processed = await self.multimodal_processor.process_input(url)
                if processed.success and processed.extracted_text:
                    multimodal_analysis = {
                        "type": processed.input_type.value,
                        "url": url,
                        "language_analysis": processed.language_analysis,
                        "extracted_preview": processed.extracted_text[:500] + "..." if len(processed.extracted_text) > 500 else processed.extracted_text
                    }
                    # Augment message with extracted content
                    processed_message += f"\n\n[Extracted from {url}]:\n{processed.extracted_text[:1000]}"
        
        # Step 3: Build enhanced prompt with personality mode
        messages, effective_mode = self.prompt_engine.format_conversation_for_model(
            message=processed_message,
            conversation_history=session["conversation_history"],
            mode=session["prompt_mode"],
            language_style=self._language_to_style(language),
        )
        
        # Step 3b: Inject personality mode prompt into system message
        personality_prompt = session.get("personality_prompt", "")
        if personality_prompt and messages and messages[0]["role"] == "system":
            messages[0]["content"] = messages[0]["content"] + "\n\n" + personality_prompt
        
        # Step 4: Log user turn for training
        if self.training_collector:
            self.training_collector.add_turn(
                session_id=session_id,
                role="user",
                content=message,
                metadata={"multimodal": multimodal_analysis is not None}
            )
        
        # Step 5: Generate text response
        text_response = await self._generate_text(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            mode=effective_mode,
        )
        
        # Step 6: Post-process for quality
        text_response = self.prompt_engine.post_process_response(text_response, effective_mode)
        
        # Step 7: Generate voice if requested
        audio_base64 = None
        if mode in [ResponseMode.VOICE_ONLY, ResponseMode.MULTIMODAL] and self.voice_loaded:
            audio_base64, _ = await self._generate_voice(text_response, language)
        
        # Step 8: Calculate metrics
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        language_tags = self._extract_language_tags(text_response)
        quality_score = self._calculate_quality_score(text_response)
        
        # Step 9: Log assistant turn for training
        training_logged = False
        if self.training_collector:
            self.training_collector.add_turn(
                session_id=session_id,
                role="assistant",
                content=text_response,
                response_time_ms=generation_time,
                metadata={
                    "mode": effective_mode.value,
                    "quality_score": quality_score,
                    "languages": language_tags,
                }
            )
            training_logged = True
        
        # Step 10: Update conversation history
        session["conversation_history"].append({"role": "user", "content": message})
        session["conversation_history"].append({"role": "assistant", "content": text_response})
        
        # Keep history manageable
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]
        
        return SisiLolaResponse(
            text=text_response,
            audio_base64=audio_base64,
            language_tags=language_tags,
            personality_metrics=self.personality_config.get("traits", {}),
            generation_time_ms=generation_time,
            mode=mode,
            prompt_mode=effective_mode.value,
            training_data_logged=training_logged,
            quality_score=quality_score,
            multimodal_analysis=multimodal_analysis,
        )
    
    async def _generate_text(
        self,
        messages: List[Dict],
        max_tokens: int,
        temperature: float,
        mode: PromptMode,
    ) -> str:
        """Generate text using Modal (preferred), local model, or API"""
        
        # 1. Try Modal Inference (Fastest)
        use_modal = os.getenv("USE_MODAL", "true").lower() == "true"
        if use_modal:
            # Build full prompt for Modal to preserve context/instructions
            system_prompt = messages[0]["content"] if messages[0]["role"] == "system" else ""
            conversation = []
            for msg in messages[1:]:
                role = "User" if msg["role"] == "user" else "Sisi Lola"
                conversation.append(f"{role}: {msg['content']}")
            
            full_prompt = f"{system_prompt}\n\n" + "\n".join(conversation)
            
            modal_response = await self._generate_with_modal(full_prompt, max_tokens, temperature)
            if modal_response:
                return modal_response

        # 2. Fallback to local brain
        if self.brain_loaded:
            return await self._generate_with_local_brain(messages, max_tokens, temperature)
        
        # 3. Fallback to direct API
        return await self._generate_with_api(messages, max_tokens, temperature)

    async def _generate_with_modal(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Call optimized Modal endpoint"""
        import httpx
        from sisi_lola_api.app.config import MODAL_INFERENCE_URL
        
        # Ensure we use the best URL (prioritize ModelInference endpoint if config or env says so)
        modal_url = os.getenv("MODAL_ENDPOINT_URL", MODAL_INFERENCE_URL)
        
        # Check if we need to append method name (if we are calling ModelInference directly)
        if "modelinference-generate-text" not in modal_url and "-generate" not in modal_url:
             # If it's the base app URL, we might need a suffix, but usually MODAL_INFERENCE_URL is complete
             pass

        print(f"[⚡ MODAL] Calling inference: {modal_url[:50]}...")
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    modal_url,
                    json={
                        "message": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                
                latency = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("text") or data.get("response")
                    if response_text:
                        print(f"[✅ MODAL] Success in {latency:.2f}s")
                        return response_text
                
                print(f"[❌ MODAL] Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[❌ MODAL] Request failed: {e}")
            
        return None
    
    async def _generate_with_local_brain(
        self,
        messages: List[Dict],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate with local Mistral + LoRA"""
        import torch
        
        # Format messages for Mistral
        system_prompt = messages[0]["content"] if messages[0]["role"] == "system" else ""
        
        conversation = []
        for msg in messages[1:]:
            if msg["role"] == "user":
                conversation.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                conversation.append(f"Sisi Lola: {msg['content']}")
        
        full_prompt = f"<s>[INST] {system_prompt}\n\n{chr(10).join(conversation)} [/INST]"
        
        inputs = self.brain_tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096
        )
        
        if self.device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.brain_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.15,  # Reduce repetition
                pad_token_id=self.brain_tokenizer.eos_token_id,
            )
        
        response = self.brain_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
        
        return response
    
    async def _generate_with_api(
        self,
        messages: List[Dict],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Fallback to API-based generation"""
        
        try:
            from sisi_lola_api.app.services.api_manager import get_api_manager
            api_manager = get_api_manager()
            
            # 1. Try OpenAI with rotation
            api_key = api_manager.get_next_openai_key()
            
            if api_key:
                try:
                    import httpx
                    api_url = "https://api.openai.com/v1/chat/completions"
                    # Use standard gpt-4o or config model
                    model = "gpt-4o" 
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            api_url,
                            headers={"Authorization": f"Bearer {api_key}"},
                            json={
                                "model": model,
                                "messages": messages,
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                            },
                            timeout=60
                        )
                        if response.status_code == 200:
                            return response.json()["choices"][0]["message"]["content"]
                        else:
                            print(f"OpenAI error {response.status_code}: {response.text}")
                except Exception as e:
                    print(f"OpenAI attempt failed: {e}")

            # 2. Try OpenRouter (Fallback)
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {openrouter_key}",
                            "HTTP-Referer": "https://sisilola.live",
                            "X-Title": "Sisi Lola AI",
                        },
                        json={
                            "model": "mistralai/mistral-7b-instruct",
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                        timeout=60
                    )
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
            
            return self._get_offline_response()
            
        except Exception as e:
            print(f"API error: {e}")
            return self._get_offline_response()
    
    def _get_offline_response(self) -> str:
        """Fallback when no model available"""
        return """[NP] How body? Na Sisi Lola be this o! [/NP] 💃

[EN] I'm currently in offline mode, but I can't wait to chat properly soon! [/EN]

[YO] E má worry, we go connect back soon! [/YO] ✨"""
    
    async def _generate_voice(self, text: str, language: Language) -> tuple:
        """Generate voice audio using MMS (native) or XTTS (legacy)"""
        # 1. Try MMS Native Voice (Fast and Authentic for YO/HA/IG)
        if mms_service:
            # Check if language is supported by MMS
            mms_lang_map = {
                Language.YORUBA: "yo",
                Language.HAUSA: "ha",
                Language.IGBO: "ig"
            }
            mms_code = mms_lang_map.get(language)
            if mms_code:
                print(f"[🔊 MMS] Generating native {language.name} audio...")
                audio_base64, _ = await mms_service.generate_speech(text, mms_code)
                if audio_base64:
                    return audio_base64, None

        # 2. Fallback to legacy XTTS voice
        if not self.voice_loaded:
            return None, None
        
        try:
            # Clean text for TTS
            clean_text = re.sub(r'\[/?(?:EN|NP|YO|IG|HA)\]', '', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            clean_text = re.sub(r'[💃✨🇳🇬🎵💼💬🌍❤️🎭]', '', clean_text)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name
            
            tts_lang = "en"  # Most Nigerian languages use English phonetics
            
            if self.speaker_reference:
                self.voice_model.tts_to_file(
                    text=clean_text[:500],  # Limit length
                    file_path=output_path,
                    speaker_wav=self.speaker_reference,
                    language=tts_lang,
                )
            else:
                self.voice_model.tts_to_file(
                    text=clean_text[:500],
                    file_path=output_path,
                    language=tts_lang,
                )
            
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            os.remove(output_path)
            
            return audio_base64, None
            
        except Exception as e:
            print(f"Voice generation error: {e}")
            return None, None
    
    def _language_to_style(self, language: Language) -> LanguageStyle:
        """Convert Language enum to LanguageStyle"""
        mapping = {
            Language.ENGLISH: LanguageStyle.PURE_ENGLISH,
            Language.PIDGIN: LanguageStyle.PURE_PIDGIN,
            Language.YORUBA: LanguageStyle.PURE_YORUBA,
            Language.YORUNGLISH: LanguageStyle.YORUNGLISH,
            Language.MIXED: LanguageStyle.MIXED_NIGERIAN,
        }
        return mapping.get(language, LanguageStyle.YORUNGLISH)
    
    def _extract_language_tags(self, text: str) -> List[str]:
        """Extract language tags from response"""
        tags = re.findall(r'\[(EN|NP|YO|IG|HA)\]', text)
        return list(set(tags))
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calculate response quality score"""
        score = 0.5
        
        # Length check
        word_count = len(text.split())
        if 20 < word_count < 300:
            score += 0.15
        elif word_count < 10 or word_count > 500:
            score -= 0.2
        
        # Has language tags
        if re.search(r'\[(?:EN|NP|YO|IG|HA)\]', text):
            score += 0.1
        
        # Multiple languages (code-switching)
        tags = self._extract_language_tags(text)
        if len(tags) >= 2:
            score += 0.1
        
        # Repetition check
        words = text.lower().split()
        if len(words) > 15:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:
                score -= 0.25
        
        # Has personality (Nigerian expressions)
        nigerian_markers = ['omo', 'wahala', 'pikin', 'wetin', 'how body', 'e choke']
        if any(marker in text.lower() for marker in nigerian_markers):
            score += 0.1
        
        return max(0, min(1, score))
    
    def get_training_report(self, session_id: str = None) -> Dict:
        """Get training data report"""
        if not self.training_collector:
            return {"error": "Training data collection not enabled"}
        
        return self.training_collector.generate_report(session_id)
    
    def export_training_data(
        self,
        format: str = "jsonl",
        min_quality: str = "good"
    ) -> str:
        """Export collected training data"""
        if not self.training_collector:
            return "Training data collection not enabled"
        
        return self.training_collector.export_for_finetuning(
            format=format,
            min_quality=min_quality
        )
    
    def end_session(self, session_id: str) -> Dict:
        """End a session and save training data"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        if self.training_collector:
            return self.training_collector.end_session(session_id)
        
        return {"session_id": session_id, "ended": True}
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "brain_loaded": self.brain_loaded,
            "voice_loaded": self.voice_loaded,
            "personality_loaded": self.personality_loaded,
            "device": self.device,
            "training_collection_active": self.training_collector is not None,
            "active_sessions": len(self.active_sessions),
            "models": {
                "brain": self.HF_BRAIN_REPO if self.brain_loaded else None,
                "voice": self.HF_VOICE_REPO if self.voice_loaded else None,
                "personality": self.HF_PERSONALITY_REPO if self.personality_loaded else None,
            },
            "enhanced_features": {
                "prompt_engine": True,
                "training_collector": self.training_collector is not None,
                "multimodal_processor": True,
            }
        }


# Singleton
_enhanced_service: Optional[EnhancedInferenceService] = None

def get_enhanced_inference_service(
    load_brain: bool = True,
    load_voice: bool = False,
) -> EnhancedInferenceService:
    """Get or create enhanced inference service"""
    global _enhanced_service
    
    if _enhanced_service is None:
        _enhanced_service = EnhancedInferenceService(
            load_brain=load_brain,
            load_voice=load_voice,
        )
    
    return _enhanced_service
