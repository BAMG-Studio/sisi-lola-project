"""
SISI LOLA MULTIMODAL INPUT PROCESSOR
Handles URL, YouTube, file, and multimedia input processing.

Features:
- YouTube video transcript extraction
- Web page content fetching
- Audio file transcription
- Image description
- Document parsing
- Language pattern analysis from content
"""

import os
import re
import json
import asyncio
import tempfile
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib


class InputType(str, Enum):
    """Types of multimodal inputs"""
    TEXT = "text"
    YOUTUBE_URL = "youtube"
    WEB_URL = "web"
    AUDIO_FILE = "audio"
    IMAGE_FILE = "image"
    DOCUMENT = "document"
    VIDEO_FILE = "video"


@dataclass
class ProcessedInput:
    """Result of processing multimodal input"""
    input_type: InputType
    original_input: str
    extracted_text: str
    language_analysis: Dict = None
    metadata: Dict = None
    success: bool = True
    error: str = None
    processing_time_ms: float = 0


@dataclass
class LanguagePattern:
    """Detected language pattern from content"""
    language: str
    sample_text: str
    frequency: int
    expressions: List[str]


class MultimodalInputProcessor:
    """
    Process various input types for Sisi Lola training and interaction.
    
    Capabilities:
    - Extract transcripts from YouTube videos
    - Fetch and parse web content
    - Transcribe audio files
    - Analyze language patterns in content
    """
    
    # URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    # Nigerian language patterns for analysis
    NIGERIAN_LANGUAGE_PATTERNS = {
        'pidgin': {
            'markers': [
                r'\b(wetin|dey|na|wey|abi|sha|wahala|palava|pikin|sabi|shey|abeg)\b',
                r'\bhow (body|far|you dey)\b',
                r'\b(no be|e don|make I|e go|una|dem|sey|nawa|jeje|wahala)\b',
            ],
            'expressions': [
                "how body", "wetin dey", "na so", "e choke", "wahala dey",
                "no vex", "abeg", "e don be", "make we", "una don",
            ]
        },
        'yoruba': {
            'markers': [
                r'\b(bawo ni|se alaafia|e kaabo|omo|jeje|pele|daada|shebi)\b',
                r'\b(ehn|ko le|se o|o dabi|ọmọ|àbí|kí ni)\b',
            ],
            'expressions': [
                "bawo ni", "e kaabo", "pele o", "se alaafia", "daada",
                "omo", "shebi", "ko le", "e se", "mo ti",
            ]
        },
        'igbo': {
            'markers': [
                r'\b(kedu|ndewo|nnọọ|daalu|biko|nwanne|ọ dị mma)\b',
                r'\b(ka ọ dị|i mere|ọ na-go)\b',
            ],
            'expressions': [
                "kedu", "ndewo", "daalu", "biko", "nwanne",
                "o di mma", "ka o di", "i mere",
            ]
        },
        'hausa': {
            'markers': [
                r'\b(sannu|yaya|lafiya|ina|kai|ke|ba|ne|ce)\b',
                r'\b(da kyau|na gode|to mana|yauwa|kana|kina)\b',
            ],
            'expressions': [
                "sannu", "yaya", "lafiya", "na gode", "da kyau",
                "to mana", "yauwa", "ina so", "Allah ya",
            ]
        }
    }
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir or os.path.join(os.path.expanduser("~"), ".sisi_lola_cache", "multimodal"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize optional dependencies status
        self._youtube_available = None
        self._whisper_available = None
    
    async def process_input(self, input_data: str) -> ProcessedInput:
        """Process any input type and extract relevant information"""
        start_time = datetime.now()
        
        # Detect input type
        input_type = self._detect_input_type(input_data)
        
        result = ProcessedInput(
            input_type=input_type,
            original_input=input_data,
            extracted_text="",
            metadata={"detected_at": datetime.now().isoformat()}
        )
        
        try:
            if input_type == InputType.YOUTUBE_URL:
                result = await self._process_youtube(input_data, result)
            elif input_type == InputType.WEB_URL:
                result = await self._process_web_url(input_data, result)
            elif input_type == InputType.AUDIO_FILE:
                result = await self._process_audio(input_data, result)
            elif input_type == InputType.IMAGE_FILE:
                result = await self._process_image(input_data, result)
            elif input_type == InputType.DOCUMENT:
                result = await self._process_document(input_data, result)
            else:
                result.extracted_text = input_data
            
            # Analyze language patterns
            if result.extracted_text:
                result.language_analysis = self._analyze_language_patterns(result.extracted_text)
            
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error = str(e)
        
        result.processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def _detect_input_type(self, input_data: str) -> InputType:
        """Detect the type of input"""
        input_data = input_data.strip()
        
        # Check for YouTube URL
        for pattern in self.YOUTUBE_PATTERNS:
            if re.search(pattern, input_data):
                return InputType.YOUTUBE_URL
        
        # Check for general URL
        if re.match(r'https?://', input_data):
            return InputType.WEB_URL
        
        # Check for file paths
        if os.path.exists(input_data):
            ext = os.path.splitext(input_data)[1].lower()
            if ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                return InputType.AUDIO_FILE
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return InputType.IMAGE_FILE
            elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                return InputType.VIDEO_FILE
            elif ext in ['.pdf', '.docx', '.txt', '.md']:
                return InputType.DOCUMENT
        
        return InputType.TEXT
    
    async def _process_youtube(self, url: str, result: ProcessedInput) -> ProcessedInput:
        """Process YouTube video - extract transcript"""
        
        # Extract video ID
        video_id = None
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
            result.error = "Could not extract YouTube video ID"
            result.success = False
            return result
        
        result.metadata["video_id"] = video_id
        result.metadata["video_url"] = f"https://www.youtube.com/watch?v={video_id}"
        
        # Try to get transcript
        try:
            transcript = await self._get_youtube_transcript(video_id)
            if transcript:
                result.extracted_text = transcript
                result.metadata["source"] = "youtube_transcript"
                return result
        except Exception as e:
            print(f"Transcript extraction failed: {e}")
        
        # Fallback: Get video metadata
        try:
            metadata = await self._get_youtube_metadata(video_id)
            result.metadata.update(metadata)
            result.extracted_text = f"Video Title: {metadata.get('title', 'Unknown')}\n"
            result.extracted_text += f"Description: {metadata.get('description', 'No description')}"
            result.metadata["source"] = "youtube_metadata"
        except Exception as e:
            result.extracted_text = f"[YouTube video: {video_id}] - Unable to extract content automatically."
            result.metadata["source"] = "youtube_reference"
            result.metadata["note"] = "Manual review required for language patterns"
        
        return result
    
    async def _get_youtube_transcript(self, video_id: str) -> Optional[str]:
        """Get YouTube video transcript using youtube-transcript-api"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Prefer Nigerian/African English or Pidgin transcripts
            for lang_code in ['en', 'en-NG', 'en-GB', 'pcm']:
                try:
                    transcript = transcript_list.find_transcript([lang_code])
                    text = " ".join([entry['text'] for entry in transcript.fetch()])
                    return text
                except:
                    continue
            
            # Fallback to any available transcript
            for transcript in transcript_list:
                text = " ".join([entry['text'] for entry in transcript.fetch()])
                return text
                
        except ImportError:
            print("youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")
            return None
        except Exception as e:
            print(f"Transcript error: {e}")
            return None
    
    async def _get_youtube_metadata(self, video_id: str) -> Dict:
        """Get YouTube video metadata"""
        try:
            import httpx
            
            # Use oembed API (no API key required)
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "title": data.get("title", ""),
                        "author": data.get("author_name", ""),
                        "thumbnail": data.get("thumbnail_url", ""),
                    }
        except Exception as e:
            print(f"Metadata error: {e}")
        
        return {"title": "Unknown", "author": "Unknown"}
    
    async def _process_web_url(self, url: str, result: ProcessedInput) -> ProcessedInput:
        """Process web URL - extract main content"""
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=15, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator='\n')
                
                # Clean up
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                result.extracted_text = text[:5000]  # Limit to 5000 chars
                result.metadata["url"] = url
                result.metadata["title"] = soup.title.string if soup.title else "Unknown"
                
        except ImportError:
            result.extracted_text = f"[Web content from: {url}] - beautifulsoup4 not installed"
            result.metadata["note"] = "Install beautifulsoup4: pip install beautifulsoup4"
        except Exception as e:
            result.error = f"Failed to fetch URL: {str(e)}"
            result.success = False
        
        return result
    
    async def _process_audio(self, file_path: str, result: ProcessedInput) -> ProcessedInput:
        """Process audio file - transcribe"""
        try:
            import whisper
            
            model = whisper.load_model("base")
            transcription = model.transcribe(file_path)
            
            result.extracted_text = transcription["text"]
            result.metadata["language"] = transcription.get("language", "unknown")
            result.metadata["duration"] = transcription.get("duration", 0)
            
        except ImportError:
            result.extracted_text = f"[Audio file: {file_path}] - whisper not installed"
            result.metadata["note"] = "Install OpenAI Whisper: pip install openai-whisper"
        except Exception as e:
            result.error = f"Audio processing failed: {str(e)}"
            result.success = False
        
        return result
    
    async def _process_image(self, file_path: str, result: ProcessedInput) -> ProcessedInput:
        """Process image - extract text/description"""
        try:
            # Try OCR with pytesseract
            import pytesseract
            from PIL import Image
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            result.extracted_text = text.strip()
            result.metadata["width"] = image.width
            result.metadata["height"] = image.height
            
        except ImportError:
            result.extracted_text = f"[Image file: {file_path}]"
            result.metadata["note"] = "Install pytesseract for OCR: pip install pytesseract"
        except Exception as e:
            result.error = f"Image processing failed: {str(e)}"
            result.success = False
        
        return result
    
    async def _process_document(self, file_path: str, result: ProcessedInput) -> ProcessedInput:
        """Process document files"""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.txt' or ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    result.extracted_text = f.read()
            
            elif ext == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        result.extracted_text = text
                except ImportError:
                    result.extracted_text = f"[PDF file: {file_path}] - PyPDF2 not installed"
            
            elif ext == '.docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    result.extracted_text = "\n".join([p.text for p in doc.paragraphs])
                except ImportError:
                    result.extracted_text = f"[DOCX file: {file_path}] - python-docx not installed"
                    
        except Exception as e:
            result.error = f"Document processing failed: {str(e)}"
            result.success = False
        
        return result
    
    def _analyze_language_patterns(self, text: str) -> Dict:
        """Analyze text for Nigerian language patterns"""
        text_lower = text.lower()
        analysis = {
            "detected_languages": [],
            "language_breakdown": {},
            "expressions_found": {},
            "recommendations": [],
        }
        
        for lang, patterns in self.NIGERIAN_LANGUAGE_PATTERNS.items():
            markers_found = 0
            expressions_found = []
            
            # Check markers
            for marker in patterns['markers']:
                matches = re.findall(marker, text_lower)
                markers_found += len(matches)
            
            # Check expressions
            for expr in patterns['expressions']:
                if expr.lower() in text_lower:
                    expressions_found.append(expr)
            
            if markers_found > 0 or expressions_found:
                analysis["detected_languages"].append(lang)
                analysis["language_breakdown"][lang] = {
                    "marker_count": markers_found,
                    "expressions": expressions_found,
                    "confidence": min(1.0, (markers_found + len(expressions_found)) / 10)
                }
                analysis["expressions_found"][lang] = expressions_found
        
        # Generate recommendations
        if not analysis["detected_languages"]:
            analysis["recommendations"].append(
                "No Nigerian language patterns detected. Consider manual review."
            )
        else:
            primary_lang = max(
                analysis["language_breakdown"].items(),
                key=lambda x: x[1]["marker_count"]
            )[0]
            analysis["recommendations"].append(
                f"Primary language detected: {primary_lang}. Good for training data."
            )
            
            if len(analysis["detected_languages"]) > 1:
                analysis["recommendations"].append(
                    f"Code-switching detected between: {', '.join(analysis['detected_languages'])}"
                )
        
        return analysis
    
    def generate_training_samples_from_content(
        self,
        processed_input: ProcessedInput,
        sample_type: str = "language_learning"
    ) -> List[Dict]:
        """Generate training samples from processed content"""
        samples = []
        
        if not processed_input.extracted_text:
            return samples
        
        text = processed_input.extracted_text
        lang_analysis = processed_input.language_analysis or {}
        
        # Split into sentences/paragraphs
        sentences = re.split(r'[.!?]\s+', text)
        
        for lang, data in lang_analysis.get("language_breakdown", {}).items():
            for expr in data.get("expressions", []):
                # Find context around expression
                for sentence in sentences:
                    if expr.lower() in sentence.lower():
                        sample = {
                            "instruction": f"Use the {lang.upper()} expression '{expr}' naturally in conversation.",
                            "input": f"How would Sisi Lola use '{expr}'?",
                            "output": f"[{lang.upper()[:2]}] {sentence} [/{lang.upper()[:2]}]",
                            "metadata": {
                                "source": processed_input.input_type.value,
                                "language": lang,
                                "expression": expr,
                                "category": "language_learning"
                            }
                        }
                        samples.append(sample)
                        break  # One sample per expression
        
        return samples


# Singleton
_processor: Optional[MultimodalInputProcessor] = None

def get_multimodal_processor() -> MultimodalInputProcessor:
    """Get or create processor singleton"""
    global _processor
    if _processor is None:
        _processor = MultimodalInputProcessor()
    return _processor
