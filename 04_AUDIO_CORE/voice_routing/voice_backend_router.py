"""
SISI LOLA VOICE BACKEND ROUTER
==============================
Intelligent voice routing based on language tags from N-ATLaS/Mistral output.

Architecture:
    Brain Output (with language tags) → Router → Appropriate TTS Engine → Audio

Language Tag Routing:
    [EN] English     → XTTS-v2 (cloned voice) or ElevenLabs
    [NP] Pidgin      → NaijaTTS or YarnGPT or XTTS with Pidgin prosody
    [YO] Yoruba      → VITS-Yoruba or YarnGPT-Yoruba
    [IG] Igbo        → YarnGPT-Igbo
    [HA] Hausa       → YarnGPT-Hausa

The router reads voice_config.yaml and selects the best available engine
for each language segment, then stitches the audio together.

Usage:
    from voice_backend_router import VoiceRouter
    
    router = VoiceRouter()
    audio_path = router.synthesize(
        text="Hello! [NP] How you dey? [/NP] [YO] Ẹ kú àárọ̀! [/YO]",
        output_path="output.wav"
    )
"""

import os
import re
import yaml
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Literal
from dataclasses import dataclass
from abc import ABC, abstractmethod
import wave
import struct

# Try importing audio libraries
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


@dataclass
class TextSegment:
    """Represents a segment of text with language metadata"""
    text: str
    language: str  # "english", "yoruba", "pidgin", "igbo", "hausa"
    start_tag: str
    end_tag: str


@dataclass
class AudioSegmentResult:
    """Result from TTS synthesis"""
    audio_path: str
    duration_ms: float
    engine_used: str
    language: str


class TTSEngine(ABC):
    """Abstract base class for TTS engines"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def synthesize(self, text: str, output_path: str, language: str = "en") -> bool:
        pass


class XTTSEngine(TTSEngine):
    """Coqui XTTS-v2 engine for voice cloning"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = None
        self.speaker_wav = config.get("speaker_embedding")
        
    @property
    def name(self) -> str:
        return "xtts"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["english", "yoruba", "pidgin"]  # XTTS supports these with speaker reference
    
    def is_available(self) -> bool:
        try:
            from TTS.api import TTS
            return True
        except ImportError:
            return False
    
    def synthesize(self, text: str, output_path: str, language: str = "en") -> bool:
        if not self.is_available():
            return False
        
        try:
            from TTS.api import TTS
            
            if self.model is None:
                self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Map language to XTTS language code
            lang_map = {"english": "en", "yoruba": "en", "pidgin": "en"}  # XTTS uses "en" base
            xtts_lang = lang_map.get(language, "en")
            
            if self.speaker_wav and Path(self.speaker_wav).exists():
                self.model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=self.speaker_wav,
                    language=xtts_lang,
                )
            else:
                # Use default speaker
                self.model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=xtts_lang,
                )
            
            return True
        except Exception as e:
            print(f"XTTS synthesis error: {e}")
            return False


class EdgeTTSEngine(TTSEngine):
    """Microsoft Edge TTS (free, no API key required)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.voice_map = {
            "english": config.get("voice_id", "en-NG-EzinneNeural"),
            "yoruba": "en-NG-EzinneNeural",  # Nigerian English as fallback
            "pidgin": "en-NG-EzinneNeural",
            "igbo": "en-NG-EzinneNeural",
            "hausa": "en-NG-EzinneNeural",
        }
    
    @property
    def name(self) -> str:
        return "edge_tts"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["english", "yoruba", "pidgin", "igbo", "hausa"]
    
    def is_available(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False
    
    def synthesize(self, text: str, output_path: str, language: str = "english") -> bool:
        if not self.is_available():
            return False
        
        try:
            import edge_tts
            import asyncio
            
            voice = self.voice_map.get(language, "en-NG-EzinneNeural")
            
            async def _synthesize():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            asyncio.run(_synthesize())
            return True
        except Exception as e:
            print(f"EdgeTTS synthesis error: {e}")
            return False


class ElevenLabsEngine(TTSEngine):
    """ElevenLabs premium TTS"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.voice_id = config.get("voice_id", "EXAVITQu4vr4xnSDxMaL")
        self.model_id = config.get("model_id", "eleven_multilingual_v2")
    
    @property
    def name(self) -> str:
        return "elevenlabs"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["english", "yoruba", "pidgin"]
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def synthesize(self, text: str, output_path: str, language: str = "english") -> bool:
        if not self.is_available():
            return False
        
        try:
            import requests
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key,
            }
            data = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": self.config.get("voice_settings", {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                }),
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"ElevenLabs API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"ElevenLabs synthesis error: {e}")
            return False


class YarnGPTEngine(TTSEngine):
    """YarnGPT for Nigerian languages (Yoruba, Igbo, Hausa, Pidgin)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = None
    
    @property
    def name(self) -> str:
        return "yarngpt"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["yoruba", "igbo", "hausa", "pidgin"]
    
    def is_available(self) -> bool:
        # YarnGPT requires specific installation
        try:
            # Check if YarnGPT is installed
            import importlib.util
            return importlib.util.find_spec("yarngpt") is not None
        except:
            return False
    
    def synthesize(self, text: str, output_path: str, language: str = "yoruba") -> bool:
        if not self.is_available():
            return False
        
        try:
            # YarnGPT synthesis would go here
            # This is a placeholder for the actual implementation
            print(f"YarnGPT synthesis for {language}: {text[:50]}...")
            return False  # Not implemented yet
        except Exception as e:
            print(f"YarnGPT synthesis error: {e}")
            return False


class VITSYorubaEngine(TTSEngine):
    """VITS model trained on Yoruba (YorùLect/ÌròyìnSpeech)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = None
    
    @property
    def name(self) -> str:
        return "yoruba_vits"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["yoruba"]
    
    def is_available(self) -> bool:
        # Check if VITS Yoruba model is available
        checkpoint_path = self.config.get("checkpoint_path")
        if checkpoint_path:
            return Path(checkpoint_path).exists()
        return False
    
    def synthesize(self, text: str, output_path: str, language: str = "yoruba") -> bool:
        if not self.is_available():
            return False
        
        try:
            # VITS Yoruba synthesis would go here
            print(f"VITS Yoruba synthesis: {text[:50]}...")
            return False  # Not implemented yet
        except Exception as e:
            print(f"VITS Yoruba synthesis error: {e}")
            return False


class VoiceRouter:
    """
    Intelligent voice router that selects the best TTS engine
    based on language tags and availability.
    """
    
    # Language tag patterns
    LANGUAGE_PATTERNS = {
        "english": (r"\[EN\]", r"\[/EN\]"),
        "yoruba": (r"\[YO\]", r"\[/YO\]"),
        "pidgin": (r"\[NP\]", r"\[/NP\]"),
        "igbo": (r"\[IG\]", r"\[/IG\]"),
        "hausa": (r"\[HA\]", r"\[/HA\]"),
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the voice router with configuration"""
        if config_path is None:
            # Default config paths
            possible_paths = [
                Path(__file__).parent.parent / "sisi_lola_chat" / "voice_config.yaml",
                Path(__file__).parent / "voice_config.yaml",
                Path("voice_config.yaml"),
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break
        
        self.config = self._load_config(config_path)
        self.engines = self._initialize_engines()
        self.language_routing = self.config.get("voice_stack", {}).get("language_routing", {})
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load voice configuration from YAML"""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        
        # Return default config
        return {
            "voice_stack": {
                "language_routing": {
                    "english": ["xtts", "elevenlabs", "edge_tts"],
                    "yoruba": ["yoruba_vits", "yarngpt", "xtts", "edge_tts"],
                    "pidgin": ["yarngpt", "xtts", "edge_tts"],
                    "igbo": ["yarngpt", "edge_tts"],
                    "hausa": ["yarngpt", "edge_tts"],
                },
            },
            "xtts": {},
            "edge_tts": {"voice_id": "en-NG-EzinneNeural"},
            "elevenlabs": {},
        }
    
    def _initialize_engines(self) -> Dict[str, TTSEngine]:
        """Initialize all available TTS engines"""
        engines = {}
        
        # Initialize each engine with its config section
        engine_classes = {
            "xtts": XTTSEngine,
            "edge_tts": EdgeTTSEngine,
            "elevenlabs": ElevenLabsEngine,
            "yarngpt": YarnGPTEngine,
            "yoruba_vits": VITSYorubaEngine,
        }
        
        for engine_name, engine_class in engine_classes.items():
            engine_config = self.config.get(engine_name, {})
            engine = engine_class(engine_config)
            engines[engine_name] = engine
            
            # Log availability
            status = "✅" if engine.is_available() else "❌"
            print(f"{status} {engine_name}: {'Available' if engine.is_available() else 'Not available'}")
        
        return engines
    
    def parse_language_segments(self, text: str) -> List[TextSegment]:
        """
        Parse text with language tags into segments.
        
        Example:
            Input: "Hello! [NP] How you dey? [/NP]"
            Output: [
                TextSegment(text="Hello! ", language="english", ...),
                TextSegment(text="How you dey?", language="pidgin", ...),
            ]
        """
        segments = []
        remaining_text = text
        
        # Build regex pattern for all language tags
        all_patterns = []
        for lang, (start, end) in self.LANGUAGE_PATTERNS.items():
            all_patterns.append(f"({start})(.*?)({end})")
        
        combined_pattern = "|".join(all_patterns)
        
        # Find all tagged segments
        current_pos = 0
        for match in re.finditer(combined_pattern, text, re.DOTALL):
            # Add any untagged text before this match (treat as English)
            if match.start() > current_pos:
                untagged = text[current_pos:match.start()].strip()
                if untagged:
                    segments.append(TextSegment(
                        text=untagged,
                        language="english",
                        start_tag="",
                        end_tag="",
                    ))
            
            # Identify which language this match belongs to
            for lang, (start_pat, end_pat) in self.LANGUAGE_PATTERNS.items():
                lang_match = re.match(f"{start_pat}(.*?){end_pat}", match.group(), re.DOTALL)
                if lang_match:
                    content = lang_match.group(1).strip()
                    if content:
                        segments.append(TextSegment(
                            text=content,
                            language=lang,
                            start_tag=start_pat.replace("\\", ""),
                            end_tag=end_pat.replace("\\", ""),
                        ))
                    break
            
            current_pos = match.end()
        
        # Add any remaining untagged text
        if current_pos < len(text):
            remaining = text[current_pos:].strip()
            if remaining:
                segments.append(TextSegment(
                    text=remaining,
                    language="english",
                    start_tag="",
                    end_tag="",
                ))
        
        # If no segments found, treat entire text as English
        if not segments and text.strip():
            segments.append(TextSegment(
                text=text.strip(),
                language="english",
                start_tag="",
                end_tag="",
            ))
        
        return segments
    
    def select_engine(self, language: str) -> Optional[TTSEngine]:
        """Select the best available engine for a language"""
        routing = self.language_routing.get(language, ["edge_tts"])
        
        for engine_name in routing:
            engine = self.engines.get(engine_name)
            if engine and engine.is_available() and language in engine.supported_languages:
                return engine
        
        # Fallback to edge_tts
        edge = self.engines.get("edge_tts")
        if edge and edge.is_available():
            return edge
        
        return None
    
    def synthesize_segment(
        self,
        segment: TextSegment,
        output_dir: str,
        segment_index: int,
    ) -> Optional[AudioSegmentResult]:
        """Synthesize a single text segment"""
        engine = self.select_engine(segment.language)
        
        if not engine:
            print(f"⚠️ No engine available for {segment.language}")
            return None
        
        output_path = os.path.join(output_dir, f"segment_{segment_index:03d}.wav")
        
        print(f"🎤 [{engine.name}] {segment.language}: {segment.text[:50]}...")
        
        success = engine.synthesize(segment.text, output_path, segment.language)
        
        if success and os.path.exists(output_path):
            # Get duration
            duration_ms = self._get_audio_duration_ms(output_path)
            
            return AudioSegmentResult(
                audio_path=output_path,
                duration_ms=duration_ms,
                engine_used=engine.name,
                language=segment.language,
            )
        
        return None
    
    def _get_audio_duration_ms(self, audio_path: str) -> float:
        """Get audio duration in milliseconds"""
        try:
            with wave.open(audio_path, 'r') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                return (frames / rate) * 1000
        except:
            return 0.0
    
    def concatenate_audio(
        self,
        segment_results: List[AudioSegmentResult],
        output_path: str,
        gap_ms: int = 100,
    ) -> bool:
        """Concatenate audio segments into a single file"""
        if not segment_results:
            return False
        
        if HAS_PYDUB:
            try:
                combined = AudioSegment.empty()
                silence = AudioSegment.silent(duration=gap_ms)
                
                for i, result in enumerate(segment_results):
                    segment = AudioSegment.from_file(result.audio_path)
                    if i > 0:
                        combined += silence
                    combined += segment
                
                combined.export(output_path, format="wav")
                return True
            except Exception as e:
                print(f"Concatenation error: {e}")
                return False
        else:
            # Fallback: just copy the first segment
            import shutil
            if segment_results:
                shutil.copy(segment_results[0].audio_path, output_path)
                return True
            return False
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        gap_ms: int = 100,
    ) -> Optional[str]:
        """
        Main synthesis method: parse, route, synthesize, and concatenate.
        
        Args:
            text: Text with language tags (e.g., "[EN] Hello [/EN] [NP] How you dey? [/NP]")
            output_path: Path for the output audio file
            gap_ms: Gap between segments in milliseconds
            
        Returns:
            Path to the synthesized audio, or None on failure
        """
        print(f"\n🎙️ Voice Router: Synthesizing...")
        
        # Parse into segments
        segments = self.parse_language_segments(text)
        print(f"📊 Found {len(segments)} segment(s)")
        
        for seg in segments:
            print(f"   - [{seg.language}] {seg.text[:40]}...")
        
        # Create temp directory for segment files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Synthesize each segment
            segment_results = []
            for i, segment in enumerate(segments):
                result = self.synthesize_segment(segment, temp_dir, i)
                if result:
                    segment_results.append(result)
            
            if not segment_results:
                print("❌ No segments synthesized successfully")
                return None
            
            # Concatenate segments
            print(f"\n🔗 Concatenating {len(segment_results)} segment(s)...")
            success = self.concatenate_audio(segment_results, output_path, gap_ms)
            
            if success:
                print(f"✅ Audio saved to: {output_path}")
                return output_path
            else:
                print("❌ Concatenation failed")
                return None
    
    def get_status(self) -> Dict:
        """Get status of all engines"""
        return {
            name: {
                "available": engine.is_available(),
                "languages": engine.supported_languages,
            }
            for name, engine in self.engines.items()
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Voice Router")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--output", type=str, default="output.wav", help="Output audio path")
    parser.add_argument("--config", type=str, help="Path to voice_config.yaml")
    parser.add_argument("--status", action="store_true", help="Show engine status")
    
    args = parser.parse_args()
    
    router = VoiceRouter(args.config)
    
    if args.status:
        print("\n📊 Voice Router Status:")
        status = router.get_status()
        for engine, info in status.items():
            symbol = "✅" if info["available"] else "❌"
            print(f"  {symbol} {engine}: {info['languages']}")
    
    elif args.text:
        result = router.synthesize(args.text, args.output)
        if result:
            print(f"\n🎉 Success! Audio saved to: {result}")
        else:
            print("\n❌ Synthesis failed")
    
    else:
        # Demo
        demo_text = """
        Hello! Welcome to Sisi Lola.
        [NP] How you dey today? I hope say everything dey alright with you! [/NP]
        [YO] Ẹ kú àárọ̀! [/YO]
        Let me help you with whatever you need.
        """
        
        print("\n🎤 Demo: Synthesizing multi-language text...")
        result = router.synthesize(demo_text, "demo_output.wav")
