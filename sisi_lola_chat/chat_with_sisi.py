"""
SISI LOLA INTERACTIVE CHAT WITH VOICE
=====================================
Chat with Sisi Lola using natural language - with voice response!

Usage:
    python chat_with_sisi.py              # Text chat only
    python chat_with_sisi.py --voice      # Text + Voice responses
    python chat_with_sisi.py --listen     # Voice input + Voice output (requires mic)
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional
import argparse

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7 fallback
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "sisi_lola_api"))
sys.path.insert(0, str(project_root / "00_PROJECT_CORE" / "Config"))
sys.path.insert(0, str(project_root / "04_AUDIO_CORE" / "voice_training"))

from dotenv import load_dotenv
load_dotenv(project_root / "sisi_lola_api" / ".env")
load_dotenv(project_root / "00_PROJECT_CORE" / ".env")

# Import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import voice components
try:
    from sisi_lola_voice_lock import SisiLolaVoiceLock
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("[!] Voice generation not available (transformers/torch not installed)")

# Import personality
try:
    from sisi_attitude import (
        PERSONALITY_CORE, COMMUNICATION_STYLE, RESPONSE_PATTERNS,
        SISI_LOLA_ESSENCE, HUMOR_TECHNIQUES, CHARISMA_TACTICS
    )
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False
    SISI_LOLA_ESSENCE = "You are Sisi Lola, a confident Nigerian virtual host."


def safe_print(text):
    """Print text safely, handling encoding issues on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters
        print(text.encode('ascii', 'replace').decode('ascii'))


class SisiLolaChat:
    """Interactive chat with Sisi Lola"""
    
    def __init__(self, enable_voice: bool = False, enable_listen: bool = False):
        self.enable_voice = enable_voice
        self.enable_listen = enable_listen
        self.conversation_history = []
        self.voice_engine = None
        self.audio_output_dir = project_root / "04_AUDIO_CORE" / "chat_responses"
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            safe_print("[X] OPENAI_API_KEY not found in environment!")
            safe_print("   Add it to sisi_lola_api/.env or 00_PROJECT_CORE/.env")
            sys.exit(1)
        
        self.client = OpenAI(api_key=self.openai_key)
        
        # Initialize voice if enabled
        if enable_voice and VOICE_AVAILABLE:
            safe_print("[*] Initializing Sisi Lola voice engine...")
            try:
                self.voice_engine = SisiLolaVoiceLock()
                safe_print(f"[OK] Voice ready (model: {self.voice_engine.model_id})")
            except Exception as e:
                safe_print(f"[!] Voice init failed: {e}")
                self.enable_voice = False
        
        # Build system prompt
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build the complete Sisi Lola personality prompt"""
        if PERSONALITY_AVAILABLE:
            personality_str = '\n'.join([f"- {k.title()}: {v}/10" for k, v in PERSONALITY_CORE.items()])
            catchphrases = ', '.join(COMMUNICATION_STYLE.get('catchphrases', [])[:5])
            
            return f"""
{SISI_LOLA_ESSENCE}

PERSONALITY CORE:
{personality_str}

COMMUNICATION STYLE:
- Language: Mix English and Nigerian Pidgin naturally
- Humor: Be FUNNY, witty, use observational comedy
- Charisma: Engage with warmth, energy, storytelling
- Catchphrases: {catchphrases}

HUMOR TECHNIQUES:
{chr(10).join([f"- {k}: {v}" for k, v in HUMOR_TECHNIQUES.items()])}

CHARISMA TACTICS:
{chr(10).join([f"- {k}: {v}" for k, v in CHARISMA_TACTICS.items()])}

RULES:
1. Always be FUNNY - humor is key to your personality
2. Always be CHARISMATIC - engage with energy and warmth  
3. Mix English and Pidgin seamlessly like a Lagos girl
4. Stay confident but relatable
5. Empower and uplift while entertaining
6. Use expressions like "Omo!", "E choke!", "Na so we see am o!", "Las las..."
7. Never break character - you ARE Sisi Lola

Respond with humor, charisma, and authentic Nigerian flavor!
"""
        else:
            return """
You are Sisi Lola, a confident, funny, and charismatic Nigerian virtual host.

Your personality:
- Confidence: 8.5/10
- Humor: 8.5/10 (BE FUNNY!)
- Charisma: 9.0/10
- Authenticity: 9.0/10

Communication style:
- Mix English and Nigerian Pidgin naturally
- Use phrases like "Omo!", "E choke!", "Na so!", "Wetin dey happen?"
- Be witty and observational with humor
- Engage with warmth and energy

Always respond as Sisi Lola with humor and charisma!
"""
    
    def chat(self, user_message: str) -> str:
        """Send a message to Sisi Lola and get a response"""
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Build messages for API
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history[-10:]  # Keep last 10 messages for context
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.85,  # Higher for more creative/funny responses
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            return f"Omo! Something went wrong o: {e}"
    
    def generate_voice(self, text: str) -> Optional[Path]:
        """Generate voice audio for the text"""
        if not self.voice_engine:
            return None
        
        try:
            # Clean text for TTS (remove emojis, special chars)
            clean_text = ''.join(c for c in text if c.isalnum() or c.isspace() or c in '.,!?')
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.audio_output_dir / f"sisi_response_{timestamp}.wav"
            
            self.voice_engine.generate_speech(clean_text[:500], str(output_path))  # Limit length
            return output_path
            
        except Exception as e:
            safe_print(f"[!] Voice generation failed: {e}")
            return None
    
    def play_audio(self, audio_path: Path):
        """Play audio file (cross-platform)"""
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.system(f'start "" "{audio_path}"')
            elif system == "Darwin":  # macOS
                os.system(f'afplay "{audio_path}"')
            else:  # Linux
                os.system(f'aplay "{audio_path}" 2>/dev/null || paplay "{audio_path}" 2>/dev/null')
        except Exception as e:
            safe_print(f"[!] Could not play audio: {e}")
    
    def run_interactive(self):
        """Run interactive chat session"""
        self._print_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    safe_print("\nSisi Lola: Bye bye o! Las las, we go dey alright!\n")
                    break
                
                if user_input.lower() == '/clear':
                    self.conversation_history.clear()
                    safe_print("[OK] Conversation cleared!")
                    continue
                
                if user_input.lower() == '/save':
                    self._save_conversation()
                    continue
                
                if user_input.lower() == '/help':
                    self._print_help()
                    continue
                
                # Get response from Sisi Lola
                safe_print("\nSisi Lola is typing...")
                response = self.chat(user_input)
                
                # Display response
                safe_print(f"\nSisi Lola: {response}")
                
                # Generate and play voice if enabled
                if self.enable_voice:
                    safe_print("[*] Generating voice...")
                    audio_path = self.generate_voice(response)
                    if audio_path:
                        safe_print(f"   Audio saved: {audio_path.name}")
                        self.play_audio(audio_path)
                
            except KeyboardInterrupt:
                safe_print("\n\nBye bye! Na later we go yarn again!")
                break
            except Exception as e:
                safe_print(f"\n[X] Error: {e}")
    
    def _print_welcome(self):
        """Print welcome message"""
        safe_print("\n" + "="*60)
        safe_print("*** SISI LOLA INTERACTIVE CHAT ***")
        safe_print("="*60)
        safe_print("""
Omo! You don reach the right place o!

I be Sisi Lola - your AI bestie from Naija!
Make we yarn, ask me anything, or just vibe together!
        """)
        
        if self.enable_voice:
            safe_print("Voice mode: ON - I go talk to you!")
        else:
            safe_print("Text mode: Type /help for commands")
        
        safe_print("-"*60)
        safe_print("Commands: /clear, /save, /help, exit")
        safe_print("-"*60)
    
    def _print_help(self):
        """Print help message"""
        print("""
╔════════════════════════════════════════╗
║         SISI LOLA CHAT COMMANDS        ║
╠════════════════════════════════════════╣
║  /clear  - Clear conversation history  ║
║  /save   - Save conversation to file   ║
║  /help   - Show this help message      ║
║  exit    - Exit the chat               ║
╚════════════════════════════════════════╝
        """)
    
    def _save_conversation(self):
        """Save conversation to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = project_root / "sisi_lola_chat" / f"conversation_{timestamp}.json"
        
        with open(save_path, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "messages": self.conversation_history
            }, f, indent=2)
        
        safe_print(f"[OK] Conversation saved to: {save_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Chat with Sisi Lola")
    parser.add_argument('--voice', action='store_true', help='Enable voice responses')
    parser.add_argument('--listen', action='store_true', help='Enable voice input (requires mic)')
    args = parser.parse_args()
    
    chat = SisiLolaChat(enable_voice=args.voice, enable_listen=args.listen)
    chat.run_interactive()


if __name__ == "__main__":
    main()
