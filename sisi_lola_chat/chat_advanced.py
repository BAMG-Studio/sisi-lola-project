"""
SISI LOLA ADVANCED CHAT v3.0
============================
Multi-modal, memory-enabled, content-aware chat interface.

Features:
- Multi-modal content ingestion (URLs, files, media)
- Intent classification (generative/technical/conversational)
- Content generation (short and long form)
- Session and long-term memory
- Feedback loops for continuous learning
- Voice output with Nigerian accent

Usage:
    python chat_advanced.py                    # Start interactive chat
    python chat_advanced.py --user myname      # With user ID for memory
    python chat_advanced.py --voice            # Enable voice output
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

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

from dotenv import load_dotenv
load_dotenv(project_root / "sisi_lola_api" / ".env")
load_dotenv(project_root / "00_PROJECT_CORE" / ".env")

# Import our modules
from intent_classifier import PromptIntentClassifier, IntentCategory, ClassifiedIntent
from multimodal_processor import MultiModalProcessor, ProcessedContent
from content_generator import ContentGenerator, ContentPlan
from memory_manager import MemoryManager

# Import enhanced prompts
try:
    from enhanced_prompts import get_enhanced_system_prompt, get_cohere_aya_prompt
except ImportError:
    def get_enhanced_system_prompt(*args): return "You are Sisi Lola, a Nigerian AI assistant."
    def get_cohere_aya_prompt(): return get_enhanced_system_prompt()

# Import voice engine
try:
    from voice_engines import VoiceEngineFactory, ElevenLabsVoice
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Import chat data logger for training
try:
    from chat_data_logger import ChatDataLogger
    DATA_LOGGER_AVAILABLE = True
except ImportError:
    DATA_LOGGER_AVAILABLE = False


def safe_print(text):
    """Print text safely on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


class SisiLolaAdvancedChat:
    """
    Advanced chat interface with all capabilities.
    
    This is the main interface that:
    1. Classifies user intent
    2. Processes any content (URLs, files)
    3. Routes to appropriate handler
    4. Maintains memory across sessions
    5. Generates content when requested
    6. Collects feedback for training
    """
    
    def __init__(self, 
                 user_id: str = "default",
                 model_type: str = "gpt4",
                 enable_voice: bool = False):
        """
        Initialize the advanced chat.
        
        Args:
            user_id: User identifier for memory personalization
            model_type: LLM to use (gpt4, aya, claude)
            enable_voice: Whether to enable voice output
        """
        self.user_id = user_id
        self.model_type = model_type
        self.enable_voice = enable_voice
        
        # Initialize components
        safe_print("[*] Initializing Sisi Lola Advanced Chat...")
        
        # Core LLM
        self.llm_client = self._init_llm(model_type)
        
        # Intent classifier
        self.classifier = PromptIntentClassifier()
        safe_print("[OK] Intent classifier ready")
        
        # Content processor
        self.processor = MultiModalProcessor()
        safe_print("[OK] Content processor ready")
        
        # Content generator
        self.generator = ContentGenerator(llm_client=self.llm_client)
        safe_print("[OK] Content generator ready")
        
        # Memory manager
        self.memory = MemoryManager(user_id=user_id)
        safe_print(f"[OK] Memory loaded for user: {user_id}")
        
        # Voice engine
        self.voice_engine = None
        if enable_voice and VOICE_AVAILABLE:
            self._init_voice()
        
        # Data logger for training
        self.data_logger = None
        if DATA_LOGGER_AVAILABLE:
            self.data_logger = ChatDataLogger()
            self.data_logger.start_conversation(model_type, "elevenlabs" if enable_voice else None)
            safe_print("[OK] Data logger ready")
        
        # Last message ID for rating
        self.last_message_id = None
        
        safe_print("[OK] All systems initialized!\n")
    
    def _init_llm(self, model_type: str):
        """Initialize LLM client"""
        if model_type == "gpt4":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found")
                client = OpenAI(api_key=api_key)
                safe_print("[OK] OpenAI GPT-4o ready")
                return client
            except Exception as e:
                safe_print(f"[!] OpenAI init failed: {e}")
                return None
        
        elif model_type == "aya":
            try:
                import cohere
                api_key = os.getenv("COHERE_API_KEY")
                if not api_key:
                    raise ValueError("COHERE_API_KEY not found")
                client = cohere.Client(api_key)
                safe_print("[OK] Cohere Aya ready")
                return client
            except Exception as e:
                safe_print(f"[!] Cohere init failed: {e}")
                return None
        
        return None
    
    def _init_voice(self):
        """Initialize voice engine"""
        try:
            self.voice_engine = VoiceEngineFactory.create("elevenlabs")
            if self.voice_engine:
                safe_print("[OK] Voice engine ready")
        except Exception as e:
            safe_print(f"[!] Voice init failed: {e}")
            self.voice_engine = None
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and generate response.
        
        This is the main entry point that:
        1. Classifies intent
        2. Processes any content
        3. Routes to appropriate handler
        4. Returns response
        """
        # Classify intent
        intent = self.classifier.classify(user_input)
        
        # Process any content URLs/files
        content_context = ""
        if intent.requires_content_input:
            content_context = self._process_content(intent)
        
        # Route based on intent
        if intent.category == IntentCategory.GENERATIVE:
            response = self._handle_generative(user_input, intent, content_context)
        elif intent.category == IntentCategory.TECHNICAL:
            response = self._handle_technical(user_input, intent, content_context)
        else:
            response = self._handle_conversational(user_input, intent, content_context)
        
        # Log for training
        if self.data_logger:
            self.data_logger.log_message(
                self.data_logger.conversation_id,
                "user", user_input
            )
            self.last_message_id = self.data_logger.log_message(
                self.data_logger.conversation_id,
                "assistant", response
            )
        
        # Add to memory
        self.memory.add_message("user", user_input, intent=intent.category.value)
        self.memory.add_message("assistant", response)
        
        return response
    
    def _process_content(self, intent: ClassifiedIntent) -> str:
        """Process URLs and files from the intent"""
        all_content = []
        
        # Process URLs
        for url in intent.content_urls:
            safe_print(f"[*] Processing URL: {url[:50]}...")
            content = self.processor.process(url)
            
            # Save to memory
            self.memory.add_content(
                content_id=content.content_id,
                title=content.title or "Untitled",
                content_type=content.content_type.value,
                source_url=url,
                summary=content.description,
                full_context=content.to_context_string(max_length=2000)
            )
            
            all_content.append(content.to_context_string(max_length=2000))
            safe_print(f"    ✓ Processed: {content.title or content.content_id}")
        
        # Process files
        for filepath in intent.file_paths:
            safe_print(f"[*] Processing file: {filepath}...")
            content = self.processor.process(filepath)
            
            self.memory.add_content(
                content_id=content.content_id,
                title=content.title or Path(filepath).name,
                content_type=content.content_type.value,
                full_context=content.to_context_string(max_length=2000)
            )
            
            all_content.append(content.to_context_string(max_length=2000))
            safe_print(f"    ✓ Processed: {content.title or content.content_id}")
        
        return "\n\n---\n\n".join(all_content)
    
    def _handle_generative(self, prompt: str, intent: ClassifiedIntent, 
                           content_context: str) -> str:
        """Handle generative content requests"""
        safe_print(f"[*] Generating {intent.generative_subtype.value if intent.generative_subtype else 'content'}...")
        
        topic = intent.topic or prompt
        
        # Determine what to generate based on subtype
        if intent.generative_subtype:
            subtype = intent.generative_subtype.value
        else:
            subtype = "reel"  # Default
        
        try:
            if subtype in ["reel", "snippet", "ad"]:
                # Short form content
                plan = self.generator.generate_reel(
                    topic=topic,
                    duration_seconds=60,
                    platform=intent.platform or "instagram",
                    style=intent.style or "casual",
                    source_context=content_context
                )
            elif subtype in ["episode", "documentary"]:
                # Medium form content
                plan = self.generator.generate_episode(
                    topic=topic,
                    duration_minutes=15,
                    platform=intent.platform or "youtube"
                )
            elif subtype in ["podcast", "interview"]:
                # Audio/long form
                plan = self.generator.generate_podcast(
                    topic=topic,
                    duration_minutes=30
                )
            elif subtype in ["live"]:
                # Live session
                plan = self.generator.generate_live_session(
                    topic=topic,
                    duration_minutes=60
                )
            else:
                # Default to reel
                plan = self.generator.generate_reel(
                    topic=topic,
                    duration_seconds=60
                )
            
            # Build response
            response = self._format_generation_response(plan)
            
        except Exception as e:
            response = f"Omo! I tried to generate that content but wahala happen: {e}\n\nMake I try again?"
        
        return response
    
    def _format_generation_response(self, plan: ContentPlan) -> str:
        """Format the generated content plan as a response"""
        lines = [
            f"✨ Oya! I don generate your {plan.content_type}! ✨",
            "",
            f"📌 **Title:** {plan.title}",
            f"⏱️ **Duration:** {plan.total_duration():.0f} seconds",
            f"📱 **Platform:** {plan.platform or 'General'}",
            "",
            "🎬 **Script Preview:**",
            f"```",
            plan.hook,
            "",
            "...",
            "",
            plan.call_to_action,
            "```",
            "",
            f"🏷️ **Hashtags:** {' '.join('#' + tag for tag in plan.hashtags[:8])}",
            "",
            f"💾 Plan saved to: `content_plans/{plan.plan_id}_{plan.content_type}_*.json`",
            "",
            "Wetin you wan do?",
            "- `/script` - View full script",
            "- `/export` - Export for video generation",
            "- `/modify` - Change something",
        ]
        
        return "\n".join(lines)
    
    def _handle_technical(self, prompt: str, intent: ClassifiedIntent,
                          content_context: str) -> str:
        """Handle technical questions"""
        # Build context with technical focus
        messages = self._build_messages(prompt, content_context, mode="technical")
        
        response = self._call_llm(messages)
        return response
    
    def _handle_conversational(self, prompt: str, intent: ClassifiedIntent,
                               content_context: str) -> str:
        """Handle conversational/discussion requests"""
        # Build context with conversational focus
        messages = self._build_messages(prompt, content_context, mode="conversational")
        
        response = self._call_llm(messages)
        return response
    
    def _build_messages(self, prompt: str, content_context: str = "",
                        mode: str = "conversational") -> List[Dict]:
        """Build message list for LLM"""
        # Get base context from memory
        messages = self.memory.get_context_for_llm(max_messages=15)
        
        # Enhance system prompt based on mode
        system_prompt = get_enhanced_system_prompt(self.model_type)
        
        if mode == "technical":
            system_prompt += "\n\nThe user is asking a technical question. Be helpful and precise."
        
        if content_context:
            system_prompt += f"\n\n=== CONTENT CONTEXT ===\n{content_context}"
        
        # Update system message
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = system_prompt
        else:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _call_llm(self, messages: List[Dict]) -> str:
        """Call the LLM and get response"""
        if self.model_type == "gpt4" and self.llm_client:
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.8,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Omo! Error calling GPT-4: {e}"
        
        elif self.model_type == "aya" and self.llm_client:
            try:
                # Convert to Cohere format
                chat_history = []
                for msg in messages[:-1]:
                    if msg["role"] != "system":
                        chat_history.append({
                            "role": "USER" if msg["role"] == "user" else "CHATBOT",
                            "message": msg["content"]
                        })
                
                preamble = messages[0]["content"] if messages[0]["role"] == "system" else ""
                
                response = self.llm_client.chat(
                    message=messages[-1]["content"],
                    chat_history=chat_history,
                    preamble=preamble,
                    model="command-r-plus"
                )
                return response.text
            except Exception as e:
                return f"Omo! Error calling Aya: {e}"
        
        return "I no fit respond now o. My brain no dey work!"
    
    def generate_voice(self, text: str) -> Optional[Path]:
        """Generate voice for the response"""
        if not self.voice_engine:
            return None
        
        try:
            return self.voice_engine.generate(text)
        except Exception as e:
            safe_print(f"[!] Voice generation failed: {e}")
            return None
    
    def rate_response(self, rating: int = None, voice_natural: bool = None):
        """Rate the last response for training"""
        if self.data_logger and self.last_message_id:
            self.data_logger.rate_response(
                self.last_message_id,
                response_rating=rating,
                voice_naturalness=5 if voice_natural else (1 if voice_natural is False else None)
            )
            safe_print(f"[OK] Rating recorded!")
    
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
                    if self._handle_command(user_input):
                        continue
                
                # Exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    safe_print("\nSisi Lola: Bye bye o! Na later we go yarn again! 💕\n")
                    if self.voice_engine:
                        audio = self.generate_voice("Bye bye o! Na later we go yarn again!")
                        if audio:
                            self._play_audio(audio)
                    self.memory.end_session()
                    break
                
                # Get response
                safe_print("\n[Sisi Lola is thinking...]")
                response = self.chat(user_input)
                safe_print(f"\nSisi Lola: {response}")
                
                # Generate voice if enabled
                if self.enable_voice and self.voice_engine:
                    safe_print("[*] Generating voice...")
                    audio = self.generate_voice(response)
                    if audio:
                        safe_print(f"    ♪ Playing audio...")
                        self._play_audio(audio)
                
            except KeyboardInterrupt:
                safe_print("\n\nBye bye! Session saved.")
                self.memory.end_session()
                break
            except Exception as e:
                safe_print(f"\n[X] Error: {e}")
    
    def _handle_command(self, command: str) -> bool:
        """Handle slash commands. Returns True if handled."""
        cmd = command.lower().strip()
        parts = cmd.split(maxsplit=1)
        cmd_name = parts[0]
        cmd_arg = parts[1] if len(parts) > 1 else ""
        
        if cmd_name == '/help':
            self._print_help()
        
        elif cmd_name == '/rate':
            try:
                rating = int(cmd_arg)
                if 1 <= rating <= 5:
                    self.rate_response(rating=rating)
                else:
                    safe_print("[!] Rating must be 1-5")
            except ValueError:
                safe_print("Usage: /rate 1-5")
        
        elif cmd_name == '/stats':
            self._print_stats()
        
        elif cmd_name == '/memory':
            safe_print(self.memory.session.get_summary())
        
        elif cmd_name == '/recall':
            if cmd_arg:
                results = self.memory.recall_content(cmd_arg)
                if results:
                    safe_print("Found in memory:")
                    for r in results:
                        safe_print(f"  - {r['title']} ({r['content_type']})")
                else:
                    safe_print("Nothing found in memory.")
            else:
                safe_print("Usage: /recall <query>")
        
        elif cmd_name == '/clear':
            self.memory.session.clear()
            safe_print("[OK] Session memory cleared!")
        
        elif cmd_name == '/export':
            if self.data_logger:
                path = self.data_logger.export_for_training()
                safe_print(f"[OK] Training data exported to {path}")
            else:
                safe_print("[!] Data logger not available")
        
        elif cmd_name == '/voice':
            if cmd_arg == 'on':
                if VOICE_AVAILABLE:
                    self._init_voice()
                    self.enable_voice = True
                else:
                    safe_print("[!] Voice not available")
            elif cmd_arg == 'off':
                self.voice_engine = None
                self.enable_voice = False
                safe_print("[OK] Voice disabled")
            else:
                status = "ON" if self.enable_voice else "OFF"
                safe_print(f"Voice: {status}")
        
        elif cmd_name == '/generate':
            # Quick generate command
            if cmd_arg:
                safe_print(f"\n[*] Generating content about: {cmd_arg}")
                response = self.chat(f"Create a reel about {cmd_arg}")
                safe_print(f"\n{response}")
            else:
                safe_print("Usage: /generate <topic>")
        
        elif cmd_name == '/process':
            # Process a URL
            if cmd_arg:
                content = self.processor.process(cmd_arg)
                safe_print(f"\nProcessed: {content.title or content.content_id}")
                safe_print(f"Type: {content.content_type.value}")
                if content.transcript:
                    safe_print(f"Transcript preview: {content.transcript[:200]}...")
            else:
                safe_print("Usage: /process <url or file path>")
        
        else:
            safe_print(f"[!] Unknown command: {cmd_name}. Type /help for commands.")
        
        return True
    
    def _print_welcome(self):
        """Print welcome message"""
        greeting = self.memory.get_relationship_greeting()
        
        safe_print("\n" + "=" * 65)
        safe_print("   *** SISI LOLA ADVANCED CHAT v3.0 ***")
        safe_print("=" * 65)
        safe_print(f"""
{greeting}

I be Sisi Lola - your AI bestie from Naija! 🇳🇬

This version dey do plenty:
  🎬 Generate content (reels, podcasts, episodes)
  🔗 Process URLs (YouTube, TikTok, websites)
  📁 Analyze files (videos, audio, documents)
  🧠 Remember our conversations
  🎤 Voice output available

Type /help to see all commands!
""")
        safe_print("-" * 65)
    
    def _print_help(self):
        """Print help message"""
        safe_print("""
📚 AVAILABLE COMMANDS:

CHAT:
  /help          - Show this help
  /clear         - Clear session memory
  /memory        - Show session summary
  /recall <query> - Search memory

CONTENT:
  /process <url> - Process a URL or file
  /generate <topic> - Quick generate content

FEEDBACK:
  /rate 1-5      - Rate last response
  /stats         - Show session stats
  /export        - Export training data

VOICE:
  /voice on/off  - Toggle voice output

EXAMPLES:
  "Create a 60-second reel about Lagos tech"
  "What do you think about this? https://youtube.com/..."
  "Generate a podcast episode about Afrobeats"
  "/process /path/to/video.mp4"
""")
    
    def _print_stats(self):
        """Print session statistics"""
        profile = self.memory.user_profile
        session = self.memory.session
        
        safe_print(f"""
📊 SESSION STATS:
   User: {profile.user_id}
   Relationship Level: {'⭐' * profile.relationship_level}{'☆' * (5 - profile.relationship_level)}
   Total Sessions: {profile.total_sessions}
   Total Messages: {profile.total_messages}
   
   Current Session:
   - Messages: {len(session.messages)}
   - Content Referenced: {len(session.active_content)}
   - Topics: {', '.join(session.topics_discussed[:5]) if session.topics_discussed else 'None'}
""")
    
    def _play_audio(self, audio_path: Path):
        """Play audio file"""
        try:
            if sys.platform == 'win32':
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)
            else:
                os.system(f"afplay {audio_path} 2>/dev/null || aplay {audio_path} 2>/dev/null")
        except Exception as e:
            safe_print(f"[!] Could not play audio: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sisi Lola Advanced Chat")
    parser.add_argument('--user', type=str, default='default', help='User ID for memory')
    parser.add_argument('--model', type=str, default='gpt4', choices=['gpt4', 'aya', 'claude'], help='LLM model')
    parser.add_argument('--voice', action='store_true', help='Enable voice output')
    
    args = parser.parse_args()
    
    chat = SisiLolaAdvancedChat(
        user_id=args.user,
        model_type=args.model,
        enable_voice=args.voice
    )
    
    chat.run_interactive()


if __name__ == "__main__":
    main()
