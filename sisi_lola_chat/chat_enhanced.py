"""
SISI LOLA ENHANCED CHAT v2.0
============================
Multi-model, multi-voice interactive chat with Sisi Lola

Features:
- Multiple LLM backends: GPT-4o, Cohere Aya, Claude
- Multiple Voice engines: ElevenLabs (female), Coqui XTTS (male), Facebook MMS
- Enhanced Pidgin/Yoruba prompts
- Voice and model toggling

Usage:
    python chat_enhanced.py                          # Default: GPT-4o + ElevenLabs
    python chat_enhanced.py --voice elevenlabs       # Female Nigerian voice
    python chat_enhanced.py --voice coqui            # Male Nigerian voice  
    python chat_enhanced.py --model aya              # Use Cohere Aya
    python chat_enhanced.py --model gpt4             # Use GPT-4o (default)
    python chat_enhanced.py --list-voices            # List available ElevenLabs voices
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "sisi_lola_api"))
sys.path.insert(0, str(project_root / "00_PROJECT_CORE" / "Config"))
sys.path.insert(0, str(project_root / "04_AUDIO_CORE" / "voice_training"))

from dotenv import load_dotenv
load_dotenv(project_root / "sisi_lola_api" / ".env")
load_dotenv(project_root / "00_PROJECT_CORE" / ".env")

# Import our modules
from enhanced_prompts import (
    get_enhanced_system_prompt,
    get_conversation_examples,
    get_cohere_aya_prompt
)

from voice_engines import (
    VoiceEngineFactory,
    ElevenLabsVoice,
    CoquiXTTSVoice,
    FacebookMMSVoice
)


def safe_print(text):
    """Print text safely on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


class LLMBackend:
    """Multi-model LLM backend"""
    
    def __init__(self, model_type: Literal["gpt4", "aya", "claude"] = "gpt4"):
        self.model_type = model_type
        self.client = None
        self.model_name = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client"""
        
        if self.model_type == "gpt4":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found")
                self.client = OpenAI(api_key=api_key)
                self.model_name = "gpt-4o"
                safe_print(f"[OK] OpenAI GPT-4o initialized")
            except Exception as e:
                safe_print(f"[X] Failed to initialize GPT-4o: {e}")
                raise
        
        elif self.model_type == "aya":
            try:
                import cohere
                api_key = os.getenv("COHERE_API_KEY")
                if not api_key:
                    raise ValueError("COHERE_API_KEY not found")
                self.client = cohere.ClientV2(api_key=api_key)
                self.model_name = "command-a-03-2025"  # Latest Cohere model with Aya multilingual
                safe_print(f"[OK] Cohere Command-A initialized")
            except ImportError:
                safe_print("[!] Cohere not installed. Run: pip install cohere")
                raise
            except Exception as e:
                safe_print(f"[X] Failed to initialize Cohere: {e}")
                raise
        
        elif self.model_type == "claude":
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found")
                self.client = Anthropic(api_key=api_key)
                self.model_name = "claude-3-5-sonnet-20241022"
                safe_print(f"[OK] Claude 3.5 Sonnet initialized")
            except ImportError:
                safe_print("[!] Anthropic not installed. Run: pip install anthropic")
                raise
            except Exception as e:
                safe_print(f"[X] Failed to initialize Claude: {e}")
                raise
    
    def chat(self, messages: list, system_prompt: str) -> str:
        """Send messages and get response"""
        
        if self.model_type == "gpt4":
            return self._chat_openai(messages, system_prompt)
        elif self.model_type == "aya":
            return self._chat_cohere(messages, system_prompt)
        elif self.model_type == "claude":
            return self._chat_claude(messages, system_prompt)
    
    def _chat_openai(self, messages: list, system_prompt: str) -> str:
        """Chat using OpenAI"""
        try:
            full_messages = [{"role": "system", "content": system_prompt}]
            
            # Add few-shot examples for better output
            examples = get_conversation_examples()
            full_messages.extend(examples)
            
            # Add conversation history
            full_messages.extend(messages[-10:])
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=full_messages,
                temperature=0.85,
                max_tokens=600,
                presence_penalty=0.3,  # Encourage variety
                frequency_penalty=0.2   # Reduce repetition
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Omo! OpenAI wahala: {e}"
    
    def _chat_cohere(self, messages: list, system_prompt: str) -> str:
        """Chat using Cohere Command-A (with Aya multilingual)"""
        try:
            # Convert messages to Cohere V2 format
            cohere_messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in messages:
                role = "user" if msg["role"] == "user" else "assistant"
                cohere_messages.append({"role": role, "content": msg["content"]})
            
            response = self.client.chat(
                model=self.model_name,
                messages=cohere_messages,
                temperature=0.85,
                max_tokens=600
            )
            
            return response.message.content[0].text
            
        except Exception as e:
            return f"Omo! Cohere wahala: {e}"
    
    def _chat_claude(self, messages: list, system_prompt: str) -> str:
        """Chat using Claude"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=600,
                system=system_prompt,
                messages=messages[-10:]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Omo! Claude wahala: {e}"


class SisiLolaEnhancedChat:
    """Enhanced Sisi Lola Chat with multi-model and multi-voice support"""
    
    def __init__(
        self,
        model: Literal["gpt4", "aya", "claude"] = "gpt4",
        voice: Literal["elevenlabs", "coqui", "mms", "none"] = "none",
        voice_gender: Literal["female", "male"] = "female"
    ):
        self.model_type = model
        self.voice_type = voice
        self.voice_gender = voice_gender
        self.conversation_history = []
        self.voice_engine = None
        
        # Paths
        self.audio_output_dir = project_root / "04_AUDIO_CORE" / "chat_responses"
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM
        safe_print(f"\n[*] Initializing Sisi Lola Enhanced Chat...")
        safe_print(f"    Model: {model.upper()}")
        safe_print(f"    Voice: {voice if voice != 'none' else 'OFF'}")
        
        self.llm = LLMBackend(model_type=model)
        
        # Initialize voice engine
        if voice != "none":
            self._init_voice(voice)
        
        # Get appropriate system prompt
        if model == "aya":
            self.system_prompt = get_cohere_aya_prompt()
        else:
            self.system_prompt = get_enhanced_system_prompt(model)
        
        safe_print("[OK] Ready to chat!\n")
    
    def _init_voice(self, voice_type: str):
        """Initialize voice engine"""
        try:
            if voice_type == "elevenlabs":
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if not api_key:
                    safe_print("[!] ELEVENLABS_API_KEY not found - voice disabled")
                    return
                self.voice_engine = ElevenLabsVoice(api_key=api_key)
                safe_print(f"[OK] ElevenLabs voice ready ({self.voice_engine.voice_type})")
                
            elif voice_type == "coqui":
                speaker_wav = self._find_voice_sample()
                self.voice_engine = CoquiXTTSVoice(speaker_wav=speaker_wav)
                # Check if model actually loaded
                if self.voice_engine.model is None:
                    safe_print("[!] Coqui XTTS failed to load - voice disabled")
                    safe_print("    Run: pip install TTS")
                    self.voice_engine = None
                    return
                safe_print(f"[OK] Coqui XTTS voice ready ({self.voice_engine.voice_type})")
                
            elif voice_type == "mms":
                self.voice_engine = FacebookMMSVoice()
                if self.voice_engine.model is None:
                    safe_print("[!] Facebook MMS failed to load - voice disabled")
                    self.voice_engine = None
                    return
                safe_print(f"[OK] Facebook MMS voice ready ({self.voice_engine.voice_type})")
                
        except Exception as e:
            safe_print(f"[!] Voice initialization failed: {e}")
            self.voice_engine = None
    
    def _find_voice_sample(self) -> Optional[str]:
        """Find a voice sample for cloning"""
        # Look for voice samples in the training directory
        samples_dir = project_root / "04_AUDIO_CORE" / "voice_samples"
        if samples_dir.exists():
            wav_files = list(samples_dir.glob("*.wav"))
            if wav_files:
                return str(wav_files[0])
        return None
    
    def chat(self, user_message: str) -> str:
        """Send message and get response"""
        
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response from LLM
        response = self.llm.chat(self.conversation_history, self.system_prompt)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def generate_voice(self, text: str) -> Optional[Path]:
        """Generate voice for text"""
        if not self.voice_engine:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = "mp3" if isinstance(self.voice_engine, ElevenLabsVoice) else "wav"
            output_path = self.audio_output_dir / f"sisi_response_{timestamp}.{ext}"
            
            result = self.voice_engine.generate_speech(text, str(output_path))
            return Path(result) if result else None
            
        except Exception as e:
            safe_print(f"[!] Voice generation failed: {e}")
            return None
    
    def play_audio(self, audio_path: Path):
        """Play audio file"""
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.system(f'start "" "{audio_path}"')
            elif system == "Darwin":
                os.system(f'afplay "{audio_path}"')
            else:
                os.system(f'aplay "{audio_path}" 2>/dev/null || paplay "{audio_path}" 2>/dev/null')
        except Exception as e:
            safe_print(f"[!] Could not play audio: {e}")
    
    def switch_model(self, new_model: str):
        """Switch to a different model"""
        safe_print(f"\n[*] Switching to {new_model.upper()}...")
        try:
            self.llm = LLMBackend(model_type=new_model)
            self.model_type = new_model
            
            if new_model == "aya":
                self.system_prompt = get_cohere_aya_prompt()
            else:
                self.system_prompt = get_enhanced_system_prompt(new_model)
            
            safe_print(f"[OK] Now using {new_model.upper()}")
        except Exception as e:
            safe_print(f"[X] Failed to switch: {e}")
    
    def switch_voice(self, new_voice: str):
        """Switch to a different voice engine"""
        safe_print(f"\n[*] Switching voice to {new_voice}...")
        try:
            self._init_voice(new_voice)
            self.voice_type = new_voice
        except Exception as e:
            safe_print(f"[X] Failed to switch voice: {e}")
    
    def run_interactive(self):
        """Run interactive chat session"""
        self._print_welcome()
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    safe_print("\nSisi Lola: Bye bye o! Las las, we go dey alright! Na later we go yarn again! 💕\n")
                    if self.voice_engine:
                        self.generate_voice("Bye bye o! Na later we go yarn again!")
                    break
                
                # Get response
                safe_print("\nSisi Lola is typing...")
                response = self.chat(user_input)
                safe_print(f"\nSisi Lola: {response}")
                
                # Generate voice if enabled
                if self.voice_engine:
                    safe_print("[*] Generating voice...")
                    audio_path = self.generate_voice(response)
                    if audio_path:
                        safe_print(f"    Audio: {audio_path.name}")
                        self.play_audio(audio_path)
                
            except KeyboardInterrupt:
                safe_print("\n\nBye bye! Na later we go yarn again!")
                break
            except Exception as e:
                safe_print(f"\n[X] Error: {e}")
    
    def _handle_command(self, command: str):
        """Handle slash commands"""
        cmd = command.lower().strip()
        
        if cmd == '/help':
            self._print_help()
        elif cmd == '/clear':
            self.conversation_history.clear()
            safe_print("[OK] Conversation cleared!")
        elif cmd == '/save':
            self._save_conversation()
        elif cmd == '/model':
            safe_print(f"Current model: {self.model_type.upper()}")
            safe_print("Available: gpt4, aya, claude")
        elif cmd.startswith('/model '):
            new_model = cmd.split(' ', 1)[1].strip()
            if new_model in ['gpt4', 'aya', 'claude']:
                self.switch_model(new_model)
            else:
                safe_print(f"[!] Unknown model: {new_model}. Use: gpt4, aya, claude")
        elif cmd == '/voice':
            voice_status = self.voice_type if self.voice_engine else "OFF"
            safe_print(f"Current voice: {voice_status}")
            safe_print("Available: elevenlabs, coqui, mms, off")
        elif cmd.startswith('/voice '):
            new_voice = cmd.split(' ', 1)[1].strip()
            if new_voice == 'off':
                self.voice_engine = None
                self.voice_type = 'none'
                safe_print("[OK] Voice disabled")
            elif new_voice in ['elevenlabs', 'coqui', 'mms']:
                self.switch_voice(new_voice)
            else:
                safe_print(f"[!] Unknown voice: {new_voice}. Use: elevenlabs, coqui, mms, off")
        elif cmd == '/status':
            self._print_status()
        else:
            safe_print(f"[!] Unknown command: {cmd}. Type /help for commands.")
    
    def _print_welcome(self):
        """Print welcome message"""
        safe_print("\n" + "="*65)
        safe_print("   *** SISI LOLA ENHANCED CHAT v2.0 ***")
        safe_print("="*65)
        safe_print("""
Omo! You don reach the right place o!

I be Sisi Lola - your AI bestie from Naija!
Make we yarn, ask me anything, or just vibe together!
        """)
        self._print_status()
        safe_print("-"*65)
        safe_print("Commands: /help, /model, /voice, /clear, /save, exit")
        safe_print("-"*65)
    
    def _print_status(self):
        """Print current configuration"""
        voice_status = f"{self.voice_type} ({self.voice_engine.voice_type})" if self.voice_engine else "OFF"
        safe_print(f"  Model: {self.model_type.upper()} | Voice: {voice_status}")
    
    def _print_help(self):
        """Print help message"""
        safe_print("""
╔═══════════════════════════════════════════════════════════════╗
║              SISI LOLA ENHANCED CHAT COMMANDS                 ║
╠═══════════════════════════════════════════════════════════════╣
║  /help           - Show this help message                     ║
║  /clear          - Clear conversation history                 ║
║  /save           - Save conversation to file                  ║
║  /status         - Show current model and voice settings      ║
║                                                               ║
║  MODEL COMMANDS:                                              ║
║  /model          - Show current model                         ║
║  /model gpt4     - Switch to GPT-4o                           ║
║  /model aya      - Switch to Cohere Aya (better Pidgin!)      ║
║  /model claude   - Switch to Claude 3.5                       ║
║                                                               ║
║  VOICE COMMANDS:                                              ║
║  /voice          - Show current voice engine                  ║
║  /voice elevenlabs - ElevenLabs (female, premium)             ║
║  /voice coqui    - Coqui XTTS (male, free)                    ║
║  /voice mms      - Facebook MMS (Yoruba, basic)               ║
║  /voice off      - Disable voice                              ║
║                                                               ║
║  exit/quit/bye   - Exit the chat                              ║
╚═══════════════════════════════════════════════════════════════╝
        """)
    
    def _save_conversation(self):
        """Save conversation to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = project_root / "sisi_lola_chat" / f"conversation_{timestamp}.json"
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "model": self.model_type,
                "voice": self.voice_type,
                "messages": self.conversation_history
            }, f, indent=2, ensure_ascii=False)
        
        safe_print(f"[OK] Saved to: {save_path.name}")


def list_elevenlabs_voices():
    """List available ElevenLabs voices"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        safe_print("[X] ELEVENLABS_API_KEY not found")
        return
    
    try:
        engine = ElevenLabsVoice(api_key=api_key)
        voices = engine.list_voices()
        
        safe_print("\n=== Available ElevenLabs Voices ===\n")
        for voice in voices:
            labels = voice.get('labels', {})
            accent = labels.get('accent', 'N/A')
            gender = labels.get('gender', 'N/A')
            safe_print(f"  {voice['name']}")
            safe_print(f"    ID: {voice['voice_id']}")
            safe_print(f"    Gender: {gender} | Accent: {accent}")
            safe_print()
            
    except Exception as e:
        safe_print(f"[X] Error listing voices: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Sisi Lola Enhanced Chat - Multi-model, Multi-voice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chat_enhanced.py                      # Default: GPT-4o, no voice
  python chat_enhanced.py --voice elevenlabs   # GPT-4o + ElevenLabs female voice
  python chat_enhanced.py --model aya          # Cohere Aya (better Pidgin!)
  python chat_enhanced.py --model aya --voice coqui  # Aya + Coqui male voice
  python chat_enhanced.py --list-voices        # List ElevenLabs voices
        """
    )
    
    parser.add_argument(
        '--model', '-m',
        choices=['gpt4', 'aya', 'claude'],
        default='gpt4',
        help='LLM model to use (default: gpt4)'
    )
    parser.add_argument(
        '--voice', '-v',
        choices=['elevenlabs', 'coqui', 'mms', 'none'],
        default='none',
        help='Voice engine to use (default: none)'
    )
    parser.add_argument(
        '--list-voices',
        action='store_true',
        help='List available ElevenLabs voices and exit'
    )
    
    args = parser.parse_args()
    
    if args.list_voices:
        list_elevenlabs_voices()
        return
    
    # Create and run chat
    chat = SisiLolaEnhancedChat(
        model=args.model,
        voice=args.voice
    )
    chat.run_interactive()


if __name__ == "__main__":
    main()
