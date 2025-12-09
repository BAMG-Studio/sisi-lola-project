"""
SISI LOLA MULTI-MODAL CONTENT PROCESSOR
========================================
Handles ingestion and processing of all content types:
- URLs (YouTube, Instagram, TikTok, Facebook, Websites)
- Media files (video, audio, images)
- Documents (txt, pdf, html, json)
- Live streams and sessions

The processor extracts, transcribes, and structures content
for Sisi Lola to understand, discuss, and generate from.
"""

import os
import re
import json
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Union, Literal, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import mimetypes

# Optional imports with graceful fallback
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import PyPDF2
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class ContentType(Enum):
    """Types of content that can be processed"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    WEBPAGE = "webpage"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"
    LIVE_STREAM = "live_stream"


class SourcePlatform(Enum):
    """Supported source platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    WEBSITE = "website"
    LOCAL_FILE = "local_file"
    DIRECT_INPUT = "direct_input"


@dataclass
class MediaMetadata:
    """Metadata extracted from media"""
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    channels: Optional[int] = None  # For audio
    sample_rate: Optional[int] = None  # For audio


@dataclass
class ProcessedContent:
    """
    Unified structure for all processed content.
    This is what Sisi Lola works with regardless of source.
    """
    # Core identification
    content_id: str
    content_type: ContentType
    source_platform: SourcePlatform
    source_url: Optional[str] = None
    local_path: Optional[str] = None
    
    # Extracted content
    title: Optional[str] = None
    description: Optional[str] = None
    transcript: Optional[str] = None  # For video/audio
    text_content: Optional[str] = None  # For documents/webpages
    
    # Visual content
    thumbnail_path: Optional[str] = None
    key_frames: List[str] = field(default_factory=list)
    image_descriptions: List[str] = field(default_factory=list)  # AI-generated descriptions
    
    # Metadata
    metadata: MediaMetadata = field(default_factory=MediaMetadata)
    creator: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    
    # Processing info
    processed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_notes: List[str] = field(default_factory=list)
    
    # For multi-turn conversation
    topics_extracted: List[str] = field(default_factory=list)
    entities_mentioned: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    language: Optional[str] = None
    
    def to_context_string(self, max_length: int = 4000) -> str:
        """Convert to a string suitable for LLM context"""
        parts = []
        
        if self.title:
            parts.append(f"**Title:** {self.title}")
        
        if self.creator:
            parts.append(f"**Creator:** {self.creator}")
        
        if self.description:
            desc = self.description[:500] + "..." if len(self.description) > 500 else self.description
            parts.append(f"**Description:** {desc}")
        
        if self.transcript:
            # Truncate transcript if needed
            trans = self.transcript
            if len(trans) > max_length - 500:
                trans = trans[:max_length-500] + "...[transcript truncated]"
            parts.append(f"**Transcript:**\n{trans}")
        
        if self.text_content and not self.transcript:
            text = self.text_content
            if len(text) > max_length - 500:
                text = text[:max_length-500] + "...[content truncated]"
            parts.append(f"**Content:**\n{text}")
        
        if self.topics_extracted:
            parts.append(f"**Topics:** {', '.join(self.topics_extracted)}")
        
        if self.image_descriptions:
            parts.append(f"**Visual Content:** {'; '.join(self.image_descriptions[:3])}")
        
        return "\n\n".join(parts)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return asdict(self)


class ContentExtractor(ABC):
    """Base class for content extractors"""
    
    @abstractmethod
    def can_handle(self, source: str) -> bool:
        """Check if this extractor can handle the source"""
        pass
    
    @abstractmethod
    def extract(self, source: str) -> ProcessedContent:
        """Extract content from source"""
        pass


class URLExtractor(ContentExtractor):
    """Extract content from URLs (YouTube, TikTok, Instagram, etc.)"""
    
    YOUTUBE_PATTERN = r'(youtube\.com|youtu\.be)'
    INSTAGRAM_PATTERN = r'instagram\.com'
    TIKTOK_PATTERN = r'tiktok\.com'
    FACEBOOK_PATTERN = r'facebook\.com|fb\.watch'
    TWITTER_PATTERN = r'(twitter\.com|x\.com)'
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "sisi_lola_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def can_handle(self, source: str) -> bool:
        """Check if source is a URL we can handle"""
        return source.startswith(('http://', 'https://'))
    
    def _detect_platform(self, url: str) -> SourcePlatform:
        """Detect which platform the URL is from"""
        if re.search(self.YOUTUBE_PATTERN, url):
            return SourcePlatform.YOUTUBE
        elif re.search(self.INSTAGRAM_PATTERN, url):
            return SourcePlatform.INSTAGRAM
        elif re.search(self.TIKTOK_PATTERN, url):
            return SourcePlatform.TIKTOK
        elif re.search(self.FACEBOOK_PATTERN, url):
            return SourcePlatform.FACEBOOK
        elif re.search(self.TWITTER_PATTERN, url):
            return SourcePlatform.TWITTER
        else:
            return SourcePlatform.WEBSITE
    
    def _generate_content_id(self, url: str) -> str:
        """Generate unique content ID from URL"""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def extract(self, url: str) -> ProcessedContent:
        """Extract content from URL"""
        platform = self._detect_platform(url)
        content_id = self._generate_content_id(url)
        
        if platform in [SourcePlatform.YOUTUBE, SourcePlatform.TIKTOK, 
                       SourcePlatform.INSTAGRAM, SourcePlatform.FACEBOOK]:
            return self._extract_video_content(url, platform, content_id)
        else:
            return self._extract_webpage(url, content_id)
    
    def _extract_video_content(self, url: str, platform: SourcePlatform, 
                               content_id: str) -> ProcessedContent:
        """Extract video content using yt-dlp"""
        if not YTDLP_AVAILABLE:
            return ProcessedContent(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                source_platform=platform,
                source_url=url,
                processing_notes=["yt-dlp not installed. Install with: pip install yt-dlp"]
            )
        
        try:
            # Configure yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB'],
                'outtmpl': str(self.cache_dir / f'{content_id}.%(ext)s'),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info without downloading
                info = ydl.extract_info(url, download=False)
                
                # Get available subtitles/captions
                transcript = None
                if 'subtitles' in info and info['subtitles']:
                    # Download subtitles
                    ydl_opts['skip_download'] = True
                    transcript = self._extract_subtitles(info)
                elif 'automatic_captions' in info and info['automatic_captions']:
                    transcript = self._extract_subtitles(info, auto=True)
                
                # Build metadata
                metadata = MediaMetadata(
                    duration_seconds=info.get('duration'),
                    width=info.get('width'),
                    height=info.get('height'),
                    fps=info.get('fps'),
                )
                
                return ProcessedContent(
                    content_id=content_id,
                    content_type=ContentType.VIDEO,
                    source_platform=platform,
                    source_url=url,
                    title=info.get('title'),
                    description=info.get('description'),
                    transcript=transcript,
                    thumbnail_path=info.get('thumbnail'),
                    metadata=metadata,
                    creator=info.get('uploader') or info.get('channel'),
                    upload_date=info.get('upload_date'),
                    view_count=info.get('view_count'),
                    like_count=info.get('like_count'),
                    comment_count=info.get('comment_count'),
                    language=info.get('language'),
                )
        
        except Exception as e:
            return ProcessedContent(
                content_id=content_id,
                content_type=ContentType.VIDEO,
                source_platform=platform,
                source_url=url,
                processing_notes=[f"Error extracting video: {str(e)}"]
            )
    
    def _extract_subtitles(self, info: Dict, auto: bool = False) -> Optional[str]:
        """Extract subtitles from video info"""
        try:
            subs_key = 'automatic_captions' if auto else 'subtitles'
            subs = info.get(subs_key, {})
            
            # Prefer English
            for lang in ['en', 'en-US', 'en-GB']:
                if lang in subs:
                    # Get the first format (usually vtt or json3)
                    for fmt in subs[lang]:
                        if fmt.get('ext') in ['vtt', 'json3', 'srv1']:
                            # Would need to download and parse
                            # For now, return None and use Whisper later
                            return None
            return None
        except Exception:
            return None
    
    def _extract_webpage(self, url: str, content_id: str) -> ProcessedContent:
        """Extract content from a generic webpage"""
        if not HTTPX_AVAILABLE:
            return ProcessedContent(
                content_id=content_id,
                content_type=ContentType.WEBPAGE,
                source_platform=SourcePlatform.WEBSITE,
                source_url=url,
                processing_notes=["httpx not installed. Install with: pip install httpx"]
            )
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()
                html = response.text
            
            if BS4_AVAILABLE:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = soup.title.string if soup.title else None
                
                # Extract main content (try common article containers)
                content_selectors = ['article', 'main', '.content', '.post', '#content']
                text_content = ""
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        text_content = element.get_text(separator='\n', strip=True)
                        break
                
                if not text_content:
                    # Fall back to body
                    body = soup.find('body')
                    if body:
                        # Remove script and style elements
                        for tag in body(['script', 'style', 'nav', 'header', 'footer']):
                            tag.decompose()
                        text_content = body.get_text(separator='\n', strip=True)
                
                # Extract metadata
                description = None
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content')
                
                return ProcessedContent(
                    content_id=content_id,
                    content_type=ContentType.WEBPAGE,
                    source_platform=SourcePlatform.WEBSITE,
                    source_url=url,
                    title=title,
                    description=description,
                    text_content=text_content[:10000],  # Limit text
                )
            else:
                # Basic extraction without BeautifulSoup
                return ProcessedContent(
                    content_id=content_id,
                    content_type=ContentType.WEBPAGE,
                    source_platform=SourcePlatform.WEBSITE,
                    source_url=url,
                    text_content=html[:5000],
                    processing_notes=["BeautifulSoup not available - raw HTML returned"]
                )
        
        except Exception as e:
            return ProcessedContent(
                content_id=content_id,
                content_type=ContentType.WEBPAGE,
                source_platform=SourcePlatform.WEBSITE,
                source_url=url,
                processing_notes=[f"Error extracting webpage: {str(e)}"]
            )


class FileExtractor(ContentExtractor):
    """Extract content from local files"""
    
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    DOC_EXTENSIONS = {'.txt', '.pdf', '.html', '.htm', '.json', '.md', '.csv'}
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "sisi_lola_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def can_handle(self, source: str) -> bool:
        """Check if source is a local file path"""
        path = Path(source)
        return path.exists() and path.is_file()
    
    def _get_content_type(self, path: Path) -> ContentType:
        """Determine content type from file extension"""
        ext = path.suffix.lower()
        if ext in self.VIDEO_EXTENSIONS:
            return ContentType.VIDEO
        elif ext in self.AUDIO_EXTENSIONS:
            return ContentType.AUDIO
        elif ext in self.IMAGE_EXTENSIONS:
            return ContentType.IMAGE
        elif ext in self.DOC_EXTENSIONS:
            return ContentType.DOCUMENT
        else:
            return ContentType.TEXT
    
    def extract(self, source: str) -> ProcessedContent:
        """Extract content from local file"""
        path = Path(source)
        content_type = self._get_content_type(path)
        content_id = hashlib.md5(str(path).encode()).hexdigest()[:12]
        
        if content_type == ContentType.VIDEO:
            return self._extract_video(path, content_id)
        elif content_type == ContentType.AUDIO:
            return self._extract_audio(path, content_id)
        elif content_type == ContentType.IMAGE:
            return self._extract_image(path, content_id)
        elif content_type == ContentType.DOCUMENT:
            return self._extract_document(path, content_id)
        else:
            return self._extract_text(path, content_id)
    
    def _extract_video(self, path: Path, content_id: str) -> ProcessedContent:
        """Extract video content with transcription"""
        content = ProcessedContent(
            content_id=content_id,
            content_type=ContentType.VIDEO,
            source_platform=SourcePlatform.LOCAL_FILE,
            local_path=str(path),
            title=path.stem,
        )
        
        # Transcribe using Whisper if available
        if WHISPER_AVAILABLE:
            try:
                model = whisper.load_model("base")
                result = model.transcribe(str(path))
                content.transcript = result["text"]
                content.language = result.get("language")
            except Exception as e:
                content.processing_notes.append(f"Whisper transcription failed: {e}")
        else:
            content.processing_notes.append("Whisper not installed. Install with: pip install openai-whisper")
        
        return content
    
    def _extract_audio(self, path: Path, content_id: str) -> ProcessedContent:
        """Extract audio content with transcription"""
        content = ProcessedContent(
            content_id=content_id,
            content_type=ContentType.AUDIO,
            source_platform=SourcePlatform.LOCAL_FILE,
            local_path=str(path),
            title=path.stem,
        )
        
        # Transcribe using Whisper
        if WHISPER_AVAILABLE:
            try:
                model = whisper.load_model("base")
                result = model.transcribe(str(path))
                content.transcript = result["text"]
                content.language = result.get("language")
            except Exception as e:
                content.processing_notes.append(f"Whisper transcription failed: {e}")
        
        return content
    
    def _extract_image(self, path: Path, content_id: str) -> ProcessedContent:
        """Extract image content with description"""
        content = ProcessedContent(
            content_id=content_id,
            content_type=ContentType.IMAGE,
            source_platform=SourcePlatform.LOCAL_FILE,
            local_path=str(path),
            title=path.stem,
        )
        
        if PIL_AVAILABLE:
            try:
                with Image.open(path) as img:
                    content.metadata.width = img.width
                    content.metadata.height = img.height
            except Exception as e:
                content.processing_notes.append(f"Image processing failed: {e}")
        
        return content
    
    def _extract_document(self, path: Path, content_id: str) -> ProcessedContent:
        """Extract document content"""
        content = ProcessedContent(
            content_id=content_id,
            content_type=ContentType.DOCUMENT,
            source_platform=SourcePlatform.LOCAL_FILE,
            local_path=str(path),
            title=path.stem,
        )
        
        ext = path.suffix.lower()
        
        try:
            if ext == '.pdf' and PYPDF_AVAILABLE:
                with open(path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages[:20]:  # Limit pages
                        text += page.extract_text() + "\n"
                    content.text_content = text
            elif ext in ['.html', '.htm']:
                html = path.read_text(encoding='utf-8', errors='ignore')
                if BS4_AVAILABLE:
                    soup = BeautifulSoup(html, 'html.parser')
                    content.text_content = soup.get_text(separator='\n', strip=True)
                else:
                    content.text_content = html
            elif ext == '.json':
                data = json.loads(path.read_text(encoding='utf-8'))
                content.text_content = json.dumps(data, indent=2)
            else:
                content.text_content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            content.processing_notes.append(f"Document extraction failed: {e}")
        
        return content
    
    def _extract_text(self, path: Path, content_id: str) -> ProcessedContent:
        """Extract plain text content"""
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except:
            text = None
        
        return ProcessedContent(
            content_id=content_id,
            content_type=ContentType.TEXT,
            source_platform=SourcePlatform.LOCAL_FILE,
            local_path=str(path),
            title=path.stem,
            text_content=text,
        )


class MultiModalProcessor:
    """
    Main processor that orchestrates all content extraction and processing.
    
    Usage:
        processor = MultiModalProcessor()
        
        # Process a YouTube video
        content = processor.process("https://youtube.com/watch?v=xyz")
        
        # Process a local file
        content = processor.process("/path/to/video.mp4")
        
        # Get context for LLM
        context = content.to_context_string()
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "sisi_lola_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize extractors
        self.extractors: List[ContentExtractor] = [
            URLExtractor(self.cache_dir),
            FileExtractor(self.cache_dir),
        ]
        
        # Content cache
        self.content_cache: Dict[str, ProcessedContent] = {}
    
    def process(self, source: str) -> ProcessedContent:
        """
        Process any content source and return structured content.
        
        Args:
            source: URL, file path, or raw text
            
        Returns:
            ProcessedContent object with extracted information
        """
        # Check cache first
        cache_key = hashlib.md5(source.encode()).hexdigest()[:12]
        if cache_key in self.content_cache:
            return self.content_cache[cache_key]
        
        # Find appropriate extractor
        for extractor in self.extractors:
            if extractor.can_handle(source):
                content = extractor.extract(source)
                self.content_cache[cache_key] = content
                return content
        
        # Treat as raw text input
        content = ProcessedContent(
            content_id=cache_key,
            content_type=ContentType.TEXT,
            source_platform=SourcePlatform.DIRECT_INPUT,
            text_content=source,
        )
        self.content_cache[cache_key] = content
        return content
    
    def process_multiple(self, sources: List[str]) -> List[ProcessedContent]:
        """Process multiple sources"""
        return [self.process(source) for source in sources]
    
    def clear_cache(self):
        """Clear the content cache"""
        self.content_cache.clear()
    
    def get_combined_context(self, sources: List[str], max_length: int = 8000) -> str:
        """Get combined context from multiple sources for LLM"""
        contents = self.process_multiple(sources)
        
        parts = []
        remaining = max_length
        
        for i, content in enumerate(contents):
            header = f"=== Source {i+1}: {content.title or content.source_url or 'Direct Input'} ==="
            ctx = content.to_context_string(max_length=remaining // len(contents))
            
            part = f"{header}\n{ctx}"
            parts.append(part)
            remaining -= len(part)
        
        return "\n\n".join(parts)


# Convenience functions
def process_content(source: str) -> ProcessedContent:
    """Quick function to process any content"""
    processor = MultiModalProcessor()
    return processor.process(source)


def get_context_for_chat(source: str, max_length: int = 4000) -> str:
    """Get content context ready for chat"""
    content = process_content(source)
    return content.to_context_string(max_length)


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("SISI LOLA MULTI-MODAL PROCESSOR")
    print("=" * 60)
    
    processor = MultiModalProcessor()
    
    # Test with a sample URL (if yt-dlp is available)
    test_url = "https://www.example.com"
    print(f"\nTesting with: {test_url}")
    
    content = processor.process(test_url)
    print(f"Content ID: {content.content_id}")
    print(f"Type: {content.content_type}")
    print(f"Platform: {content.source_platform}")
    
    if content.processing_notes:
        print(f"Notes: {content.processing_notes}")
    
    print("\n--- Context for LLM ---")
    print(content.to_context_string()[:500])
