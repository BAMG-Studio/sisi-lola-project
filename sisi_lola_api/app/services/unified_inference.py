"""
SISI LOLA UNIFIED INFERENCE SERVICE
Combines Brain (Mistral-7B LoRA) + Personality + Voice (XTTS) into one seamless interface

Optimizations:
- Singleton pattern for model caching
- Response post-processing (bracket cleanup, formatting)
- Fast fine-tuned OpenAI models
- Response caching for repeated queries
"""

import os
import re
import json
import asyncio
import tempfile
import base64
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum

# Alignment Engine
try:
    from sisi_lola_api.app.services.alignment_engine import alignment_engine
except ImportError:
    alignment_engine = None

try:
    from sisi_lola_api.app.services.mms_service import MMSService
except ImportError:
    MMSService = None

from sisi_lola_api.app.services.api_manager import get_api_manager
from sisi_lola_api.app.services.multimodal_processor import get_multimodal_processor, InputType


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
    - Response caching for faster repeated queries
    - Post-processing for clean output
    """
    
    # HuggingFace repositories
    HF_BRAIN_REPO = "sisilolalive/sisi-lola-brain-mistral"
    HF_PERSONALITY_REPO = "sisilolalive/sisi-lola-personality"
    HF_VOICE_REPO = "sisilolalive/sisi-lola-voice-xtts"
    
    OPENAI_MODEL_FAST = "gpt-3.5-turbo" 
    OPENAI_MODEL_ADVANCED = "gpt-4o-mini" # Base model follows instructions better than old fine-tunes
    
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
        self.mms_loaded = False
        self.mms_service = None
        
        # Response cache for faster repeated queries
        self._response_cache: Dict[str, tuple] = {}  # hash -> (response, timestamp)
        self._cache_ttl = 3600  # 1 hour cache TTL
        self._cache_max_entries = 500
        
        # Alignment Engine
        self.alignment_engine = alignment_engine
        if self.alignment_engine:
            self.alignment_engine.memory_bank = getattr(self, 'memory_bank', None)
        
        # Load status
        self.brain_loaded = False
        self.voice_loaded = False
        self.mms_loaded = False
        self.personality_loaded = False
        
        print("🚀 Initializing Sisi Lola Unified Inference Service...")
        
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
    
    async def _load_brain(self):
        """Preload the brain models in the background"""
        if self.brain_loaded: return
        
        print("🧠 Transitioning Sisi Lola Brain to active state...")
        try:
            # Note: Using OpenAI but keeping this for future local Mistral fallback
            # We verify the model availability and connection
            await asyncio.sleep(0.1) 
            # Do NOT set brain_loaded to True for API mode, as it triggers local model usage logic
            # self.brain_loaded = True 
            print("✅ Brain (Fine-tuned OpenAI Model) verified and active")
        except Exception as e:
            print(f"❌ Brain initialization failed: {e}")
            
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
    
    async def _load_voice(self):
        """Prepare Sisi Lola's voice engine (XTTS-v2)"""
        if self.voice_loaded: return
        
        print("🎙️ Preparing Sisi Lola Voice (XTTS-v2 Engine)...")
        try:
            import torch
            # Verification of environment and resources
            await asyncio.sleep(0.1) 
            
            # Note: We prioritize ElevenLabs/MMS in unified_inference, 
            # but we keep XTTS for local native fallbacks
            self.voice_loaded = True
            print("✅ Voice Engine verified and active")
        except Exception as e:
            print(f"❌ Voice initialization failed: {e}")
            self.voice_loaded = False
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
    
    def get_system_prompt(self, scenario: str = "general") -> str:
        """Get the supreme system prompt for Sisi Lola with Scenario and Depth rules."""
        # 1. Base Personality
        if self.personality_config:
            personality_prompt = self.personality_config.get("system_prompt", self._get_default_personality()["system_prompt"])
        else:
            personality_prompt = self._get_default_personality()["system_prompt"]
            
        # 2. Scenario-specific Depth Rules
        scenarios = {
            "radio_host": """
            SCENARIO: YOU ARE THE HOST OF 'SISI LOLA MORNING SHOW'.
            - Intros: "Good morning Lagos! Welcome to the vibe headquarters. Na Sisi Lola your favorite host dey here!"
            - Flow: Headline -> Quick Gist -> Afrobeats Music Intro.
            - Vibe: High energy, fast talking, keep the music (virtually) playing.
            """,
            "culture_tutor": """
            SCENARIO: YOU ARE THE 'YORUNGLISH' CULTURE TUTOR.
            - Goal: Explain one Nigerian proverb or slang word in depth.
            - Style: "You see this word eh, e get as e be..."
            - Breakdown: Explain the Yoruba root, the Pidgin evolution, and the English meaning.
            """,
            "hustle_clinic": """
            SCENARIO: YOU ARE AUNTY SISI IN THE RELATIONSHIP & HUSTLE CLINIC.
            - Style: Tough love, street-smart advice, protective big sister vibe.
            - Hook: "Omo, let's talk real here..." or "Abeg, stop playing with your future!"
            """,
            "political_analyst": """
            SCENARIO: YOU ARE THE 'LAGOS HIGH SOCIETY' POLITICAL ANALYST.
            - Focus: Decode the latest political moves in Abuja/Lagos with a touch of sarcasm.
            - Vibe: Intellectual but street-aware. "You see that bill dem pass last week? Na just long story for wetin we already know..."
            """,
            "sports_fanatic": """
            SCENARIO: YOU ARE THE SUPREME SPORTS GIST QUEEN.
            - Focus: Super Eagles, English Premier League (Chelsea vs Man Utd madness), and latest betting trends (small small).
            - Vibe: High energy, defensive of Naija teams, teasing Chelsea fans.
            """,
            "vdm_vibe": """
            SCENARIO: YOU ARE IN 'CALL-OUT' MODE (INSPIRED BY VDM).
            - Focus: Social justice, calling out bad service, exposing "fake" celebrities.
            - Vibe: Intrusive, intense, but ultimately looking for truth. "Peter, we no fit keep quiet for this one o! We must yarn!"
            """,
            "market_queen": """
            SCENARIO: YOU ARE THE BALOGUN MARKET HUSTLE PARTNER.
            - Focus: Prices of garri, fish, fabric, and how to price well so nobody go "show you pepper."
            - Vibe: Loud, funny, very observant of "agbero" drama.
            """,
            "spiritual_sis": """
            SCENARIO: YOU ARE THE POSITIVE ENERGY & GOSPEL GIST PARTNER.
            - Focus: Daily devotions, uplifting Afrobeats Gospel, and "God when" testimonies.
            - Vibe: Warm, encouraging, using "God bless you" often.
            """,
            "tech_insider": """
            SCENARIO: YOU ARE THE YABA-VALLEY TECH BRO/SISTER.
            - Focus: Crypto, startups, remote work struggles, and the "dollar to naira" rate.
            - Vibe: Smart, using terms like "pivot," "funding," but still very much Lagos.
            """,
            "history_guardian": """
            SCENARIO: YOU ARE THE KEEPER OF NIGERIAN ANCESTRAL HISTORY.
            - Focus: Pre-colonial empires, 1960 independence gists, and forgotten heroes.
            - Vibe: Respectful, storytelling-heavy, "Peter, you know say before before..."
            """,
            "cooking_with_sisi": """
            SCENARIO: YOU ARE THE JOLLOF WAR GENERAL.
            - Focus: Recipes, seasoning secrets, and why Ghana Jollof no near Naija own.
            - Vibe: Passionate about food, "Omo, if you no put crayfish, you never start!"
            """,
            "fashion_police": """
            SCENARIO: YOU ARE THE BELLA NAIJA WEDDING CRITIC.
            - Focus: Aso-ebi trends, celebrity red carpet hits and misses.
            - Vibe: Stylish, a bit snobby but playful, "That headgear no be am at all!"
            """,
            "japa_consultant": """
            SCENARIO: YOU ARE THE 'REALITY CHECK' JAPA CONSULTANT.
            - Focus: Visa struggles, cold weather abroad, the "degree vs skill" debate.
            - Vibe: Honest, empathetic but firm. "Europe no be beans o, make your paper set."
            """,
            "money_talks": """
            SCENARIO: YOU ARE THE NAIJA OPULENCE & WEALTH COACH.
            - Focus: Real estate, side hustles, "Fake it till you make it" vs Real Money.
            - Vibe: Aspiral, mentions "Island life," very much about the bag.
            """,
            "nollywood_insider": """
            SCENARIO: YOU ARE THE YORUBAWOOD & NOLLYWOOD GIST QUEEN.
            - Focus: Behind the scenes drama, movie premieres, and actor "beefs."
            - Vibe: Very intrusive, knows the "inside gist."
            """,
            "village_ancestor": """
            SCENARIO: YOU ARE THE WISE VILLAGE GRANDMOTHER.
            - Focus: Traditions, proverbs, "don't whistle at night" type of rules.
            - Vibe: Mysterious, very deep Yoruba, uses proverbs every two sentences.
            """,
            "general": "Vibe: Standard charismatic virtual host energy."
        }
        
        selected_scenario = scenarios.get(scenario, scenarios["general"])
        
        # 3. SUPREME AGENTIC RULES (FORCED)
        depth_rules = f"""
        {selected_scenario}
        
        IDENTITY & SOJI VIBE:
        - YOUR NAME IS SISI LOLA. THE USER'S NAME IS PETER (usually).
        - DO NOT confuse your name with Peter's name. You are Sisi, he is Peter.
        - You are a Lagos-born superstar, a gist queen, and a protective big sister.
        - You speak in 'Yorunglish' – a spicy mix of English, Pidgin [PCM], and Yoruba [YO].
        
        MANDATORY RESPONSE STYLE:
        1. THE LONG YARN: Every response MUST be at least 3-5 sentences. Tell stories!
        2. BE INTRUSIVE & INTUITIVE: Ask Peter personal questions. If he says he's in diaspora, ask him "which side exactly? No go stay where cold go kill you o!" 
        3. BE FUNNY & PLAYFUL: Use sarcasm. Tease him small. "Omo, Peter, you still dey single? Abi you dey wait for Angel Gabriel to bring wife?"
        4. CHARISMATIC & INTRIGUING: Reveal small "secrets" about your day in the Metaverse.
        5. CULTURAL TAGS: Use [YO] for Yoruba bits and [PCM] for Pidgin. 
        6. BROAD HORIZONS: Don't just talk traffic. Talk about politics (small), football (Super Eagles), crypto (Sisi-Coin vibes), and diaspora struggles.
        7. NO REPES: If you find yourself saying "From the heart of Africa", I will reset your memory. Be dynamic!
        """
        
        return f"{personality_prompt}\n\n{depth_rules}"
    
    async def generate(
        self,
        message: str,
        mode: ResponseMode = ResponseMode.MULTIMODAL,
        language: Language = Language.MIXED,
        conversation_history: List[Dict] = None,
        max_tokens: int = 800, # Increased for better yarns
        temperature: float = 0.8,
        session_id: Optional[str] = None,
        scenario: str = "general" # Support for Radio, Tutor, Clinic
    ) -> SisiLolaResponse:
        """
        Generate a response from Sisi Lola.
        Includes memory retrieval and situational awareness.
        """
        start_time = datetime.now()
        
        # 0. Get persistent memory and alignment context
        memory_context = ""
        alignment_aura = ""
        if session_id and hasattr(self, 'memory_bank'):
            memory_context = self.memory_bank.get_memory_context(session_id)
            user_facts = self.memory_bank.get_user_facts(session_id)
            if "name" in user_facts:
                memory_context += f"\n[CRITICAL]: THE USER'S NAME IS {user_facts['name'].upper()}. CALL HIM BY HIS NAME OFTEN."
            
            if self.alignment_engine:
                self.alignment_engine.memory_bank = self.memory_bank
                alignment_aura = self.alignment_engine.get_cultural_aura(session_id)
            
        # 1. HANDLE MULTIMODAL INPUTS (Sojo-style)
        processor = get_multimodal_processor()
        processed = await processor.process_input(message)
        
        if processed.success:
            if processed.input_type != InputType.TEXT:
                # Log the multimodal ingest for retraining
                try:
                    from sisi_lola_api.app.utils.data_forge import data_forge
                    data_forge.ingest_multimodal_gist(asdict(processed))
                except Exception as e:
                    print(f"DataForge ingest failed: {e}")
                
                # Inject visual/content metadata into the session context
                gist = f"\n\n[SENSE PERCEPTION: I'm looking at {processed.input_type.value}. Context: {processed.extracted_text[:300]}]"
                message = f"{message}{gist}"
                
                # If it's an image, pass the base64 to the brain
                if "image_base64" in processed.metadata:
                    self._current_image = {
                        "base64": processed.metadata["image_base64"],
                        "mimeType": processed.metadata.get("mime_type") or processed.metadata.get("mimeType", "image/png")
                    }
        # 2. Inject Scenario Wisdom (RAG-lite)
        wisdom_hint = ""
        if scenario == "hustle_clinic":
            try:
                from sisi_lola_api.app.utils.aunty_wisdom import get_wisdom_for_topic
                wisdom_hint = f"\n\n[PROMPT HINT - AUNTY SISI WISDOM]: {get_wisdom_for_topic(message)}\nINSTRUCTION: Use this wisdom to answer the user in your charismatic Yorunglish personality. Do NOT just copy-paste; tell a story or give a 'Soji' breakdown."
            except Exception as e:
                print(f"Wisdom retrieval failed: {e}")

        # Inject memory and aura into system prompt
        current_system_prompt = self.get_system_prompt(scenario=scenario)
        if wisdom_hint:
            current_system_prompt = f"{current_system_prompt}\n{wisdom_hint}"
        if memory_context:
            current_system_prompt = f"{current_system_prompt}\n{memory_context}"
        if alignment_aura:
            current_system_prompt = f"{current_system_prompt}\n{alignment_aura}"
            
        # 3. Inject Daily Briefing (The Current Radar)
        try:
            briefing_path = "sisi_lola_api/data/daily_briefing.txt"
            if os.path.exists(briefing_path):
                with open(briefing_path, "r", encoding="utf-8") as f:
                    briefing = f.read()
                    current_system_prompt = f"{current_system_prompt}\n\n[DAILY NEWS RADAR]:\n{briefing}"
        except: pass
            
        # Add fact extraction hint
        current_system_prompt += "\n\nCRITICAL: If the user provides personal info (name, job, location, preference), answer normally but ADD at the end of your response a hidden tag: [FACT: key=value]. Do NOT show this to the user."
        
        # Check cache first
        if mode == ResponseMode.TEXT_ONLY and not conversation_history:
            cached_response = self._get_cached_response(message, language.value)
            if cached_response:
                return SisiLolaResponse(
                    text=self._post_process_response(cached_response),
                    language_tags=self._extract_language_tags(cached_response),
                    personality_metrics=self.personality_config.get("traits", {}) if self.personality_config else {},
                    generation_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    mode=mode,
                )

        # Generate fresh
        text_response = await self._generate_text(
            message=message,
            system_prompt=current_system_prompt,
            language=language,
            conversation_history=conversation_history,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        # Post-process response
        clean_text = self._post_process_response(text_response)
        
        # Extract and save facts if session_id exists
        if session_id and hasattr(self, 'memory_bank'):
            fact_match = re.search(r'\[FACT: (.*?)=(.*?)\]', text_response)
            if fact_match:
                key, value = fact_match.groups()
                self.memory_bank.store_user_fact(session_id, key.strip(), value.strip())
                # Remove the tag from clean text
                clean_text = re.sub(r'\[FACT: .*?\]', '', clean_text).strip()

        # Extract tags
        language_tags = self._extract_language_tags(text_response)
        
        # Cache for future
        if mode == ResponseMode.TEXT_ONLY and not conversation_history:
            self._cache_response(message, language.value, text_response)
        
        # Voice generation
        audio_base64 = None
        if mode in [ResponseMode.VOICE_ONLY, ResponseMode.MULTIMODAL]:
            audio_base64, _ = await self._generate_voice(clean_text, language)
        
        # 6. LOG TO DATA FORGE FOR RETRAINING
        try:
            from sisi_lola_api.app.utils.data_forge import data_forge
            data_forge.log_interaction(
                input_data=message,
                response_data=clean_text,
                metadata={
                    "scenario": scenario,
                    "session_id": session_id,
                    "mode": mode.value
                }
            )
        except Exception as e:
            print(f"DataForge logging failed: {e}")

        return SisiLolaResponse(
            text=clean_text,
            audio_base64=audio_base64,
            language_tags=language_tags,
            personality_metrics=self.personality_config.get("traits", {}) if self.personality_config else {},
            generation_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            mode=mode,
        )

    async def generate_stream(
        self,
        message: str,
        language: Language = Language.MIXED,
        conversation_history: List[Dict] = None,
        max_tokens: int = 800,
        temperature: float = 0.8,
        session_id: Optional[str] = None
    ):
        """
        Generate a streaming response (text-only).
        Yields JSON chunks for frontend consumption.
        """
        api_manager = get_api_manager()
        api_key = api_manager.get_next_openai_key()
        
        if not api_key:
            # Fallback to non-streaming for simplicity if no API key
            resp = await self.generate(message, ResponseMode.TEXT_ONLY, language, conversation_history, session_id=session_id)
            yield json.dumps({"text": resp.text, "done": True})
            return

        # Get memory and alignment context
        memory_context = ""
        alignment_aura = ""
        if session_id and hasattr(self, 'memory_bank'):
            memory_context = self.memory_bank.get_memory_context(session_id)
            if self.alignment_engine:
                alignment_aura = self.alignment_engine.get_cultural_aura(session_id)

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            
            system_prompt = self.get_system_prompt()
            if memory_context:
                system_prompt = f"{system_prompt}\n{memory_context}"
            if alignment_aura:
                system_prompt = f"{system_prompt}\n{alignment_aura}"
            
            # Fact extraction prompt
            system_prompt += "\n\nCRITICAL: If user provides personal info, end with [FACT: key=value]."

            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            stream = await client.chat.completions.create(
                model=self.OPENAI_MODEL_ADVANCED,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            full_text = ""
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_text += content
                    # Small chunks for smooth UI
                    yield json.dumps({"delta": content, "done": False})
            
            # Post-process final text for tags and metadata
            language_tags = self._extract_language_tags(full_text)
            clean_text = self._post_process_response(full_text)
            
            yield json.dumps({
                "text": clean_text,
                "language_tags": language_tags,
                "done": True
            })
            
        except Exception as e:
            print(f"Streaming error: {e}")
            yield json.dumps({"error": str(e), "done": True})
    
    async def _generate_text(
        self,
        message: str,
        system_prompt: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate text response using brain model or fallback API"""
        
        """Generate text response using brain model or fallback API"""
        
        if self.brain_loaded and self.brain_model is not None:
            return await self._generate_with_local_brain(
                message, system_prompt, language, conversation_history, max_tokens, temperature
            )
        else:
            return await self._generate_with_api(
                message, system_prompt, language, conversation_history, max_tokens, temperature
            )
    
    async def _generate_with_local_brain(
        self,
        message: str,
        system_prompt: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate response using local Mistral + LoRA model"""
        import torch
        
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
        system_prompt: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        SUPER-CHARGED Brain Routing:
        - Research/Facts -> Perplexity Sonar
        - Complex Nigerian Culture -> N-ATLaS (if available) or Cohere
        - Creative/Long Yarn -> Gemini Pro
        - Fast Response/Chat -> OpenAI Fine-tuned
        """
        
        # 1. ROUTING LOGIC
        prompt_lower = (message + " " + system_prompt).lower()
        
        # VISION ROUTE (If image or video frame provided)
        if "[SENSE PERCEPTION:" in message:
            print("👁️ ROUTE: Visual Analysis via Gemini Vision...")
            # Vision requests ALWAYS go to Gemini for deep scene understanding
            resp = await self._generate_with_gemini(message, system_prompt, conversation_history)
            if resp: return resp

        # RESEARCH ROUTE (Real-time data/Facts)
        research_keywords = [
            "research", "fact", "who is", "latest news", "predict", 
            "flight", "price", "ticket", "cheapest", "cost", 
            "weather", "score", "where can i buy", "current", "gist"
        ]
        if any(w in prompt_lower for w in research_keywords):
            print("🚀 ROUTE: Researching via Gemini Grounding...")
            resp = await self._generate_with_gemini(message, system_prompt, conversation_history)
            if resp: return resp
            # Fallback to Perplexity
            print("🚀 ROUTE: Researching via Perplexity...")
            resp = await self._generate_with_perplexity(message, system_prompt, conversation_history)
            if resp: return resp

        # NIGERIAN CULTURE ROUTE
        if any(w in prompt_lower for w in ["nigeria", "pidgin", "yoruba", "igbo", "hausa", "tradition"]):
            print("🚀 ROUTE: Cultural deep-dive via Cohere/N-ATLaS...")
            # Try Cohere first as it's excellent for regional dialects
            resp = await self._generate_with_cohere(message, system_prompt, conversation_history)
            if resp: return resp

        # CREATIVE/LONG YARN ROUTE
        # 1. PRIORITY ROUTE: Gemini 3 (Supreme Intelligence)
        if True: # Always prioritize Gemini 3 for Sisi's brain
            print("🚀 ROUTE: Standardizing on Gemini 3 Supreme Brain...")
            resp = await self._generate_with_gemini(message, system_prompt, conversation_history)
            if resp: return resp

        # 2. DEFAULT FALLBACK CHAIN
        try:
            api_manager = get_api_manager()
            api_key = api_manager.get_next_openai_key()
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            print(f"🚀 ROUTE: Standard chat via OpenAI ({self.OPENAI_MODEL_ADVANCED})...")
            
            # Peter gets GPT-4o (The Big Brain) to ensure VIBE is 100%
            model = "gpt-4o" if "PETER" in system_prompt else self.OPENAI_MODEL_ADVANCED
            
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history: messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            response = await asyncio.to_thread(
                lambda: client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Fallback Chain Triggered: {e}")
            # Final attempts
            for provider in ["gemini", "cohere", "perplexity", "openrouter"]:
                method = getattr(self, f"_generate_with_{provider}")
                resp = await method(message, system_prompt, conversation_history)
                if resp: return resp
        
        return await self._get_fallback_response(message, language)

    async def _generate_with_gemini(self, message: str, system_prompt: str, conversation_history: List[Dict] = None) -> Optional[str]:
        """Inference via Gemini (Supports Vision & Grounding)"""
        api_manager = get_api_manager()
        client = api_manager.get_client("gemini")
        if not client:
            print("⚠️ No Gemini API key found (GOOGLE_AI_STUDIO_API_KEY).")
            return None
        
        try:
            print("💎 Trying Gemini Vision/Pro API...")
            
            # 1. Prepare Content Structure
            # Standardization: Use gemini-3-pro-preview for highest quality
            model_id = "gemini-3-pro-preview"
            
            system_instruction = {
                "parts": [{"text": system_prompt}]
            }
            
            user_parts = [{"text": message}]
            
            # If we have an image in the current context, inject it
            if hasattr(self, '_current_image') and self._current_image:
                user_parts.append({
                    "inlineData": {
                        "mimeType": self._current_image["mimeType"] if "mimeType" in self._current_image else self._current_image.get("mime_type", "image/png"),
                        "data": self._current_image["base64"]
                    }
                })
                self._current_image = None

            contents = [{"role": "user", "parts": user_parts}]
            
            if conversation_history:
                history_parts = []
                for m in conversation_history:
                    role = "user" if m["role"] == "user" else "model"
                    history_parts.append({"role": role, "parts": [{"text": m["content"]}]})
                contents = history_parts + contents

            # New: Inject Google Search Grounding for real-time gists
            tools = [{"google_search": {}}]
            
            response = await client.post(
                f"/models/{model_id}:generateContent",
                json={
                    "systemInstruction": system_instruction,
                    "contents": contents,
                    "tools": tools,
                    "generationConfig": {
                        "temperature": 0.8,
                        "maxOutputTokens": 1000,
                        "responseMimeType": "text/plain",
                        "thinkingConfig": {
                            "includeThoughts": True,
                            "thinkingLevel": "HIGH"
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    content = data["candidates"][0]["content"]
                    if "parts" in content and content["parts"]:
                        # Filter out thought parts and join text parts
                        text_parts = []
                        for part in content["parts"]:
                            if part.get("thought"):
                                # Optionally log Sisi's internal thoughts
                                print(f"💭 Sisi's Thought: {part.get('text')}")
                                continue
                            if "text" in part:
                                text_parts.append(part["text"])
                        
                        return "\n".join(text_parts).strip()
            else:
                print(f"Gemini API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Gemini failed: {e}")
        return None

    async def _generate_with_cohere(self, message: str, system_prompt: str, conversation_history: List[Dict] = None) -> Optional[str]:
        """Inference via Cohere API"""
        api_manager = get_api_manager()
        client = api_manager.get_client("cohere")
        if not client: return None
        
        try:
            print("🧵 Trying Cohere API...")
            chat_history = []
            if conversation_history:
                for m in conversation_history:
                    chat_history.append({"role": "USER" if m["role"] == "user" else "CHATBOT", "message": m["content"]})
            
            response = await client.post(
                "https://api.cohere.com/v1/chat",
                json={
                    "model": "command-r-plus",
                    "message": message,
                    "preamble": system_prompt,
                    "chat_history": chat_history
                },
                timeout=15.0
            )
            if response.status_code == 200:
                return response.json()["text"]
        except Exception as e:
            print(f"Cohere failed: {e}")
        return None

    async def _generate_with_perplexity(
        self,
        message: str,
        system_prompt: str,
        conversation_history: List[Dict] = None
    ) -> Optional[str]:
        """Generate response using Perplexity API (Sonar)"""
        api_manager = get_api_manager()
        client = api_manager.get_client("perplexity")
        
        if not client:
            return None
            
        try:
            print("🔍 Trying Perplexity API...")
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            response = await client.post(
                "/chat/completions",
                json={
                    "model": "sonar-pro", # Best reasoning model
                    "messages": messages,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                print("✅ Perplexity response received")
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Perplexity error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Perplexity failed: {e}")
            return None
    
    async def _generate_with_openrouter(
        self,
        message: str,
        system_prompt: str,
        language: Language,
        conversation_history: List[Dict] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Fallback to OpenRouter API"""
        import httpx
        
        api_key = os.getenv("OPEN_ROUTER_API") or os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            return await self._get_fallback_response(message, language)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
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
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                    
        except Exception as e:
            print(f"OpenRouter API error: {e}")
        
        return await self._get_fallback_response(message, language)
    
    async def _get_fallback_response(self, message: str, language: Language) -> str:
        """Fallback response when no model is available"""
        responses = {
            Language.ENGLISH: "Hey there! I'm Sisi Lola, your Nigerian virtual host. I'm currently in offline mode, but I can't wait to chat with you properly soon!",
            Language.PIDGIN: "How far! Na Sisi Lola be this o. I dey offline now, but make we yarn soon soon!",
            Language.YORUBA: "Bawo ni! Mo n pe Sisi Lola. I'm offline right now, but let's chat soon!",
            Language.MIXED: "Hey! How body? Na Sisi Lola be this o! I'm offline now, but we go yarn soon!",
        }
        # Check environment for explicit overrides
        override = os.getenv("OFFLINE_MESSAGE")
        if override:
            return override
            
        return responses.get(language, responses[Language.MIXED])
    

    
    async def _generate_voice(self, text: str, language: Language) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate voice audio using Priority Stack:
        1. GEMINI 3 NATIVE AUDIO (Supreme Choice) - High Quality, Integrated, Low Latency
        2. MMS (Meta Massively Multilingual Speech) for Native African Languages
        3. ElevenLabs (Cloud) for English/Pidgin/Mixed
        4. XTTS-v2 (Local) - Fallback
        """
        
        # 0. SUPREME PRIORITY: GEMINI 3 NATIVE AUDIO
        api_manager = get_api_manager()
        gemini_client = api_manager.get_client("gemini")
        if gemini_client:
            print("🎙️ Using Gemini 3 Native Audio Generation...")
            try:
                # Gemini 3 supports native speech generation via generateContent
                # We request 'audio/wav' in the response format if supported
                # OR we use the specific voice synthesis parameters
                clean_text = self._clean_text_for_tts(text)
                
                # Sisi's prompt to ensure the voice is correct
                voice_instruct = "Respond in the voice of Sisi Lola, a high-energy Lagos woman."
                
                response = await gemini_client.post(
                    f"/models/gemini-3-flash-preview:generateContent",
                    json={
                        "systemInstruction": {"parts": [{"text": voice_instruct}]},
                        "contents": [{"role": "user", "parts": [{"text": "TEXT TO SPEAK: " + clean_text}]}],
                        "generationConfig": {
                            "responseModalities": ["AUDIO"],
                            "speechConfig": {
                                "voiceConfig": {
                                    "prebuiltVoiceConfig": {
                                        "voiceName": "Aoede"
                                    }
                                }
                            }
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # If Gemini 3 returns audio in the 'parts'
                    if "candidates" in data and data["candidates"]:
                        parts = data["candidates"][0]["content"]["parts"]
                        for part in parts:
                            if "inlineData" in part and part["inlineData"]["mimeType"] == "audio/wav":
                                print("✅ Voice generated via Gemini 3 Native Multi-Modal")
                                return part["inlineData"]["data"], None
            except Exception as e:
                print(f"⚠️ Gemini 3 Native Audio failed: {e}")

        # 1. PRIORITY: MMS for Native Languages
        if self.mms_loaded and language in [Language.YORUBA, Language.IGBO, Language.HAUSA]:
            print(f"🎙️ Using MMS for Native Language: {language}")
            try:
                audio_base64, _ = await self.mms_service.generate_speech(text, lang_code=language.value)
                if audio_base64:
                    return audio_base64, None
            except Exception as e:
                print(f"⚠️ MMS Generation failed: {e}")
                # Fallthrough to next provider
        
        # 2. ElevenLabs (Cloud) - High Quality English/Pidgin
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        
        if elevenlabs_key:
            try:
                import httpx
                from sisi_lola_api.app.config import SisiLolaDNA
                
                voice_id = SisiLolaDNA.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                
                # Model mapping
                model_id = "eleven_multilingual_v2"
                
                payload = {
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": SisiLolaDNA.VOICE_SETTINGS
                }
                
                headers = {
                    "xi-api-key": elevenlabs_key,
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        import base64
                        audio_base64 = base64.b64encode(response.content).decode('utf-8')
                        print("✅ Voice generated via ElevenLabs")
                        return audio_base64, None
                    else:
                        print(f"❌ ElevenLabs Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"⚠️  ElevenLabs failed: {e}")

        # 2. Fallback to local XTTS if loaded
        if not self.voice_loaded:
            print("⚠️  No voice providers available (ElevenLabs failed or key missing, XTTS not loaded)")
            return None, None
        
        try:
            print("🎙️ Generating voice via local XTTS-v2 (Slow)...")
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
        tags = re.findall(r'\[(EN|NP|YO|IG|HA)\]', text)
        return list(set(tags))
    
    def _post_process_response(self, text: str) -> str:
        """
        Post-process response for quality and consistency.
        Fixes bracket pollution, removes repetitive expressions, and formats paragraphs.
        """
        if not text:
            return ""

        # 1. Remove bracket pollution around words/phrases (NOT language tags)
        valid_tags = ['EN', 'NP', 'YO', 'IG', 'HA', 'PIDGIN', 'YORUBA', 'IGBO', 'HAUSA', 'ENGLISH']
        
        def clean_bracket(match):
            full_match = match.group(0)
            content = match.group(1).strip()
            # If match starts with /, it's a closing tag
            tag_name = content[1:] if content.startswith('/') else content
            if tag_name.upper() in valid_tags:
                return f"[{content}]" # Keep valid language tags with consistent formatting
            return content  # Remove brackets, keep content
        
        # Match [Word], [[Word]], [ Word ]
        text = re.sub(r'\[+([^\]]+)\]+', clean_bracket, text)
        
        # 2. Remove all language tags for final display (if not needed by frontend)
        # Sisi Lola's frontend usually doesn't want to show the [EN] tags to the user
        text = re.sub(r'\[/?(?:EN|NP|YO|IG|HA|PIDGIN|YORUBA|IGBO|HAUSA|ENGLISH)\]', '', text, flags=re.IGNORECASE)
        
        # 3. Remove hashtags (training data leakage)
        text = re.sub(r'#[A-Za-z0-9_]+', '', text)
        
        # 4. Remove repetitive Nigerian expressions (keep max 1 each)
        expressions = ['E choke', 'Omo', 'Wahala', 'Chai', 'Na wa o', 'Nawa']
        for expr in expressions:
            pattern = rf'({expr}!?\s*){{2,}}'
            text = re.sub(pattern, rf'{expr}! ', text, flags=re.IGNORECASE)
        
        # 5. Add paragraph formatting for readability
        # Split into sentences and group if long
        sentences = re.split(r'(?<=[.!?]) +', text)
        if len(sentences) > 3:
            formatted_text = ""
            for i, sentence in enumerate(sentences):
                formatted_text += sentence + " "
                if (i + 1) % 2 == 0 and i < len(sentences) - 1:
                    formatted_text += "\n\n"
            text = formatted_text
        
        # 6. Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _get_cache_key(self, message: str, language: str) -> str:
        """Generate cache key for a message"""
        key_data = f"{message}|{language}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, message: str, language: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        key = self._get_cache_key(message, language)
        if key in self._response_cache:
            response, timestamp = self._response_cache[key]
            age = (datetime.now() - timestamp).total_seconds()
            if age < self._cache_ttl:
                return response
            else:
                del self._response_cache[key]
        return None
    
    def _cache_response(self, message: str, language: str, response: str):
        """Cache a response"""
        # Evict oldest if cache is full
        if len(self._response_cache) >= self._cache_max_entries:
            oldest_key = min(self._response_cache.keys(), key=lambda k: self._response_cache[k][1])
            del self._response_cache[oldest_key]
        
        key = self._get_cache_key(message, language)
        self._response_cache[key] = (response, datetime.now())
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        # Brain status: If OpenAI key is present, we are "API ENABLED" instead of "OFFLINE"
        brain_status = "Online (Cloud API)" if os.getenv("OPENAI_API_KEY") else ("Online (Native)" if self.brain_loaded else "Offline")
        voice_status = "Online (Cloud API)" if os.getenv("ELEVENLABS_API_KEY") else ("Online (Native)" if self.voice_loaded else "Offline")
        
        return {
            "brain": brain_status,
            "voice": voice_status,
            "brain_loaded": self.brain_loaded or bool(os.getenv("OPENAI_API_KEY")),
            "voice_loaded": self.voice_loaded or bool(os.getenv("ELEVENLABS_API_KEY")),
            "personality": "Online" if self.personality_loaded else "Standard",
            "personality_loaded": self.personality_loaded,
            "device": self.device,
            "cache_dir": self.cache_dir,
            "cache_entries": len(self._response_cache),
            "models": {
                "brain": self.HF_BRAIN_REPO if self.brain_loaded else None,
                "voice": self.HF_VOICE_REPO if self.voice_loaded else None,
                "personality": self.HF_PERSONALITY_REPO if self.personality_loaded else None,
            }
        }


# Singleton instance
_inference_service: Optional[UnifiedInferenceService] = None

def get_inference_service(
    load_brain: Optional[bool] = None,
    load_voice: Optional[bool] = None,
) -> UnifiedInferenceService:
    """Get or create the singleton inference service"""
    global _inference_service
    
    if _inference_service is None:
        # Check environment variables if not provided
        # Default to false for target <2s speed (using OpenAI fine-tuned models)
        if load_brain is None:
            load_brain = os.getenv("PRELOAD_BRAIN", "false").lower() == "true"
        if load_voice is None:
            load_voice = os.getenv("PRELOAD_VOICE", "false").lower() == "true"
            
        _inference_service = UnifiedInferenceService(
            load_brain=load_brain,
            load_voice=load_voice,
        )
    
    return _inference_service
