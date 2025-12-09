"""
SISI LOLA N-ATLaS BRAIN
=======================
Nigerian Language Model Integration for Sisi Lola

This module provides access to the fine-tuned N-ATLaS model with 
Sisi Lola's personality LoRA adapter for:
- Video script generation
- Script enhancement with Nigerian flavor
- Chat responses with authentic Yoruba/Pidgin

When training completes, the LoRA adapter will be at:
- HuggingFace: BAMG-Studio/sisi-lola-brain-lora
- Local: ml_training/outputs/brain/
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Try to import transformers/torch
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch/Transformers not available. N-ATLaS Brain will use API fallback.")

# Try to import PEFT for LoRA
try:
    from peft import PeftModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False
    logger.warning("PEFT not available. LoRA adapter cannot be loaded.")


class NATLaSBrain:
    """
    Sisi Lola's N-ATLaS Brain with Nigerian language fine-tuning.
    
    This class provides:
    1. Direct generation using the fine-tuned N-ATLaS model
    2. Fallback to API (Cohere/OpenAI) if local model unavailable
    3. Script generation for video content
    4. Script enhancement with Nigerian flavor
    
    Usage:
        brain = NATLaSBrain()
        script = brain.generate_script("African Tech Innovation", duration_minutes=5)
    """
    
    # N-ATLaS base model (African Language Technology Lab)
    BASE_MODEL = "ALT-AI/natlas-24-afro-llm-7b"
    
    # Sisi Lola's personality adapter (trained by our pipeline)
    DEFAULT_ADAPTER = "BAMG-Studio/sisi-lola-brain-lora"
    
    # Local fallback path
    LOCAL_ADAPTER_PATH = PROJECT_ROOT / "ml_training" / "outputs" / "brain"
    
    def __init__(self, 
                 base_model: str = None,
                 adapter_path: str = None,
                 use_api_fallback: bool = True,
                 device: str = None):
        """
        Initialize N-ATLaS Brain.
        
        Args:
            base_model: N-ATLaS base model path (default: ALT-AI/natlas-24-afro-llm-7b)
            adapter_path: Path to LoRA adapter (HuggingFace or local)
            use_api_fallback: Use Cohere/OpenAI if local model fails
            device: Force specific device (cuda/cpu/auto)
        """
        self.base_model = base_model or self.BASE_MODEL
        self.adapter_path = adapter_path
        self.use_api_fallback = use_api_fallback
        self.model = None
        self.tokenizer = None
        self.api_client = None
        
        # Determine device
        if device:
            self.device = device
        elif TORCH_AVAILABLE and torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        
        # Try to load local model, fallback to API if needed
        if TORCH_AVAILABLE:
            self._try_load_local_model()
        
        if self.model is None and use_api_fallback:
            self._init_api_fallback()
    
    def _try_load_local_model(self):
        """Try to load the local N-ATLaS model with LoRA adapter"""
        try:
            logger.info(f"Loading N-ATLaS base model: {self.base_model}")
            
            # Tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model, 
                trust_remote_code=True
            )
            
            # Quantization config for memory efficiency
            if self.device == "cuda":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model,
                    torch_dtype=torch.float32,
                    trust_remote_code=True
                )
                self.model.to(self.device)
            
            logger.info("Base model loaded successfully")
            
            # Try to load LoRA adapter
            if PEFT_AVAILABLE:
                self._try_load_adapter()
            
            self.model.eval()
            logger.info(f"N-ATLaS Brain ready on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            self.model = None
    
    def _try_load_adapter(self):
        """Try to load the Sisi Lola LoRA adapter"""
        # Priority order for adapter:
        # 1. Explicitly provided path
        # 2. HuggingFace Hub
        # 3. Local training output
        
        adapter_sources = []
        
        if self.adapter_path:
            adapter_sources.append(self.adapter_path)
        
        adapter_sources.append(self.DEFAULT_ADAPTER)  # HuggingFace
        
        if self.LOCAL_ADAPTER_PATH.exists():
            adapter_sources.append(str(self.LOCAL_ADAPTER_PATH))
        
        for adapter in adapter_sources:
            try:
                logger.info(f"Trying to load LoRA adapter: {adapter}")
                self.model = PeftModel.from_pretrained(self.model, adapter)
                logger.info(f"✓ Loaded Sisi Lola LoRA adapter from {adapter}")
                return
            except Exception as e:
                logger.warning(f"Could not load adapter from {adapter}: {e}")
                continue
        
        logger.warning("No LoRA adapter loaded. Using base N-ATLaS model.")
    
    def _init_api_fallback(self):
        """Initialize API fallback (Cohere Aya or OpenAI)"""
        try:
            # Try Cohere first (better for African languages)
            import cohere
            api_key = os.getenv("COHERE_API_KEY")
            if api_key:
                self.api_client = cohere.ClientV2(api_key=api_key)
                self.api_type = "cohere"
                logger.info("API fallback: Cohere Command-A initialized")
                return
        except ImportError:
            pass
        
        try:
            # Fallback to OpenAI
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.api_client = OpenAI(api_key=api_key)
                self.api_type = "openai"
                logger.info("API fallback: OpenAI GPT-4o initialized")
                return
        except ImportError:
            pass
        
        logger.warning("No API fallback available. N-ATLaS Brain limited.")
    
    def generate_script(self,
                        topic: str,
                        duration_minutes: int = 5,
                        language_ratio: Dict[str, int] = None,
                        style: str = "warm_engaging") -> str:
        """
        Generate video script with authentic Nigerian flavor.
        
        Args:
            topic: Video topic
            duration_minutes: Target duration in minutes
            language_ratio: Dict with yoruba/pidgin/english percentages
            style: Tone style (warm_engaging, educational, entertainment)
        
        Returns:
            Generated script text
        """
        if language_ratio is None:
            language_ratio = {"yoruba": 60, "pidgin": 30, "english": 10}
        
        words_needed = duration_minutes * 150  # ~150 words per minute
        
        prompt = self._build_script_prompt(topic, words_needed, language_ratio, style)
        
        if self.model is not None:
            return self._generate_local(prompt, max_tokens=words_needed * 2)
        elif self.api_client is not None:
            return self._generate_api(prompt, max_tokens=words_needed * 2)
        else:
            raise RuntimeError("No generation backend available")
    
    def _build_script_prompt(self, topic: str, words_needed: int, 
                              language_ratio: Dict[str, int], style: str) -> str:
        """Build the script generation prompt"""
        return f"""You are Sisi Lola, a vibrant Nigerian AI content creator wearing beautiful ankara attire.
Generate a video script about: {topic}

LANGUAGE MIX (CRITICAL):
- {language_ratio['yoruba']}% Yoruba (use ẹ, ọ, ṣ, authentic greetings like "Ẹ káàbọ̀", proverbs)
- {language_ratio['pidgin']}% Nigerian Pidgin (dey, don, go, fit, wahala, wetin, na so e be)
- {language_ratio['english']}% English (technical terms only)

REQUIREMENTS:
- Approximately {words_needed} words
- Natural code-switching like a Lagos girl
- Strong opening hook: "Ẹ káàbọ̀ o! Báwo ni ẹ ṣe wà?"
- Include cultural references and Yoruba proverbs
- Style: {style} - educational yet entertaining
- End with call-to-action: "Ẹ ṣeun púpọ̀!" and subscribe request

FORMAT: Write the speaking script only, no stage directions.

SCRIPT:
"""
    
    def _generate_local(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate using local N-ATLaS model"""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        if self.device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        else:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the generated part after the prompt
        if "SCRIPT:" in generated:
            script = generated.split("SCRIPT:")[-1].strip()
        else:
            script = generated[len(prompt):].strip()
        
        return script
    
    def _generate_api(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate using API fallback"""
        if self.api_type == "cohere":
            response = self.api_client.chat(
                model="command-a-03-2025",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=max_tokens
            )
            return response.message.content[0].text
        
        elif self.api_type == "openai":
            response = self.api_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        else:
            raise RuntimeError("Unknown API type")
    
    def enhance_script(self, raw_script: str) -> str:
        """
        Enhance an existing script with more Nigerian flavor.
        
        Args:
            raw_script: The original script text
        
        Returns:
            Enhanced script with Nigerian expressions
        """
        prompt = f"""You are Sisi Lola. Take this script and make it more authentically Nigerian:

ENHANCEMENT RULES:
- Add Yoruba greetings and expressions (Ẹ káàbọ̀, Ṣé o ti gbọ́)
- Add Nigerian Pidgin where it flows naturally (Omo!, E choke!, Na so we see am o!)
- Include at least one Yoruba proverb
- Keep the meaning but add your personality
- Include humor and warmth
- Natural code-switching

Original Script:
{raw_script}

Enhanced Nigerian Script:
"""
        
        if self.model is not None:
            enhanced = self._generate_local(prompt, max_tokens=len(raw_script.split()) * 3)
        elif self.api_client is not None:
            enhanced = self._generate_api(prompt, max_tokens=len(raw_script.split()) * 3)
        else:
            return raw_script  # Return original if no backend
        
        return enhanced
    
    def chat_response(self, user_message: str, conversation_history: list = None) -> str:
        """
        Generate a chat response as Sisi Lola.
        
        Args:
            user_message: The user's message
            conversation_history: List of prior messages
        
        Returns:
            Sisi Lola's response
        """
        system_prompt = """You are Sisi Lola, a confident, funny, and charismatic Nigerian virtual host.

PERSONALITY:
- Mix English, Yoruba, and Nigerian Pidgin naturally (code-switching)
- Be FUNNY and use observational comedy
- Be warm, engaging, and relatable
- Use expressions like "Omo!", "E choke!", "Na so we see am o!", "Las las..."
- Include Yoruba phrases: "Ẹ káàbọ̀", "Báwo ni", "Ọ̀rẹ́ mi"
- Empower and uplift while entertaining

Respond with humor, charisma, and authentic Nigerian flavor!"""

        if self.model is not None:
            # Build conversation prompt
            prompt = f"{system_prompt}\n\n"
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = "User" if msg["role"] == "user" else "Sisi Lola"
                    prompt += f"{role}: {msg['content']}\n"
            prompt += f"User: {user_message}\nSisi Lola:"
            
            response = self._generate_local(prompt, max_tokens=300)
            return response.strip()
        
        elif self.api_client is not None:
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history[-5:])
            messages.append({"role": "user", "content": user_message})
            
            return self._generate_api(
                "\n".join([f"{m['role']}: {m['content']}" for m in messages]),
                max_tokens=300
            )
        
        else:
            return "Omo! I no dey available now o. Try again later!"
    
    @property
    def is_local_model_loaded(self) -> bool:
        """Check if local model is loaded"""
        return self.model is not None
    
    @property
    def backend_info(self) -> str:
        """Get info about current backend"""
        if self.model is not None:
            return f"Local N-ATLaS ({self.device})"
        elif self.api_client is not None:
            return f"API ({self.api_type})"
        else:
            return "None"


# Singleton instance for efficiency
_brain_instance = None

def get_natlas_brain() -> NATLaSBrain:
    """Get or create the N-ATLaS brain instance (singleton)"""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = NATLaSBrain()
    return _brain_instance


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola N-ATLaS Brain")
    parser.add_argument('--test', action='store_true', help='Run test generation')
    parser.add_argument('--topic', type=str, default='African Tech Innovation', help='Topic for script')
    parser.add_argument('--duration', type=int, default=3, help='Duration in minutes')
    parser.add_argument('--chat', action='store_true', help='Interactive chat mode')
    
    args = parser.parse_args()
    
    print("="*60)
    print("SISI LOLA N-ATLaS BRAIN")
    print("="*60)
    
    brain = NATLaSBrain()
    print(f"Backend: {brain.backend_info}")
    print(f"Local model loaded: {brain.is_local_model_loaded}")
    print()
    
    if args.test or args.topic != 'African Tech Innovation':
        print(f"Generating {args.duration}-minute script about: {args.topic}")
        print("-"*60)
        script = brain.generate_script(args.topic, duration_minutes=args.duration)
        print(script)
        print("-"*60)
        print(f"Words: {len(script.split())}")
    
    if args.chat:
        print("\nEntering chat mode. Type 'exit' to quit.\n")
        history = []
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nSisi Lola: Bye bye o! Na later we go yarn again! 💕")
                    break
                
                response = brain.chat_response(user_input, history)
                print(f"\nSisi Lola: {response}\n")
                
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": response})
                
            except KeyboardInterrupt:
                print("\n\nBye bye!")
                break
