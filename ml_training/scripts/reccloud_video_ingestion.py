#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - RECCLOUD MULTILINGUAL VIDEO INGESTION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
# Integrates RecCloud API for dual-transcript (EN+Yoruba, Pidgin+English, etc.)
# video processing, speaker identification, and multilingual training data extraction
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
import time
import hashlib
import requests
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RecCloudIngestion")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class LanguageCode(str, Enum):
    """Supported languages for Sisi Lola training."""
    ENGLISH = "en"
    YORUBA = "yo"
    PIDGIN = "np"  # Nigerian Pidgin
    HAUSA = "ha"
    IGBO = "ig"


class VideoTranscriptFormat(str, Enum):
    """Transcript extraction formats."""
    SINGLE_LANGUAGE = "single"       # One language per video
    DUAL_OVERLAY = "dual"            # Two languages side-by-side (EN+YO, NP+EN)
    MULTILINGUAL_TRACKS = "multi"    # Multiple distinct language sections


class TranscriptionBackend(str, Enum):
    """Available transcription backends."""
    RECCLOUD = "reccloud"    # RecCloud API (simple, pay-as-you-go)
    MODAL_WHISPER = "modal"  # Modal Whisper (batch/parallel, 300x cheaper)


@dataclass
class TranscriptSegment:
    """Single segment of transcribed speech."""
    start_time: float        # Milliseconds
    end_time: float
    speaker_id: str          # Unique speaker identifier
    speaker_name: Optional[str]  # Human-readable speaker name
    text: str
    language: str            # Language code (en, yo, np, etc.)
    confidence: float        # 0.0-1.0 transcription confidence
    is_translated: bool      # True if this is a translation
    original_language: Optional[str] = None  # If translated, original language


@dataclass
class VideoMetadata:
    """Video file metadata and processing info."""
    video_path: str
    video_url: Optional[str]  # RecCloud-hosted or S3 URL
    duration_seconds: float
    primary_language: str     # Primary language in video
    secondary_languages: List[str]  # Additional languages (translations)
    speakers: Dict[str, str]  # {speaker_id: speaker_name}
    upload_timestamp: str
    processing_status: str    # pending, transcribing, translating, complete, failed
    error_message: Optional[str] = None


@dataclass
class TrainingExample:
    """Single training example extracted from video transcript."""
    video_id: str
    segment_index: int
    speaker: str
    timestamp: str
    languages: List[str]
    text_original: str
    text_translated: Optional[str]
    language_original: str
    language_translated: Optional[str]
    topic: str                # Inferred or assigned
    duration_seconds: float
    confidence_score: float


# ═══════════════════════════════════════════════════════════════════════════════
# RECCLOUD API CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class RecCloudClient:
    """
    RecCloud API client for video transcription, translation, and processing.
    
    API Documentation: https://reccloud.com/video-api-doc
    
    IMPORTANT: RecCloud requires videos to be accessible via public HTTP URL.
    Local files must first be hosted (e.g., Dropbox public link, S3, etc.)
    """
    
    def __init__(self, api_key: str):
        """
        Initialize RecCloud client.
        
        Args:
            api_key: RecCloud API key (from environment or config)
        """
        self.api_key = api_key
        self.base_url = "https://techhk.aoscdn.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        })
    
    def _refresh_dropbox_token(self) -> Optional[str]:
        """
        Refresh Dropbox access token using refresh token.
        
        Returns:
            New access token or None if refresh fails
        """
        refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
        app_key = os.getenv("DROPBOX_APP_KEY")
        app_secret = os.getenv("DROPBOX_APP_SECRET")
        
        if not all([refresh_token, app_key, app_secret]):
            return None
        
        try:
            response = requests.post(
                "https://api.dropbox.com/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=(app_key, app_secret)
            )
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token")
                logger.info("Dropbox access token refreshed successfully")
                return new_token
            else:
                logger.warning(f"Token refresh failed: {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Token refresh error: {e}")
            return None
    
    def _get_dropbox_client(self):
        """
        Get authenticated Dropbox client using refresh token (auto-renews).
        
        Uses the refresh token which never expires, rather than access tokens
        which expire after 4 hours.

        Returns:
            Dropbox client or None
        """
        try:
            import dropbox
        except ImportError:
            logger.info("Dropbox SDK not installed: pip install dropbox")
            return None

        # Prefer refresh token (never expires) over access token (4hr expiry)
        app_key = os.getenv("DROPBOX_APP_KEY")
        refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
        
        if app_key and refresh_token:
            try:
                # This is the recommended approach - uses refresh token for auto-renewal
                dbx = dropbox.Dropbox(
                    app_key=app_key,
                    oauth2_refresh_token=refresh_token
                )
                # Test connection
                dbx.users_get_current_account()
                logger.info("Dropbox connected using refresh token (auto-renews)")
                return dbx
            except Exception as e:
                logger.warning(f"Dropbox refresh token auth failed: {e}")
        
        # Fallback to access token (short-lived)
        access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        if access_token:
            try:
                dbx = dropbox.Dropbox(access_token)
                dbx.users_get_current_account()
                logger.info("Dropbox connected using access token (may expire)")
                return dbx
            except dropbox.exceptions.AuthError:
                logger.warning("Dropbox access token expired")
            except Exception as e:
                logger.warning(f"Dropbox access token auth failed: {e}")
        
        logger.error("No valid Dropbox credentials. Set DROPBOX_APP_KEY and DROPBOX_REFRESH_TOKEN")
        return None

    def _get_dropbox_public_url(self, local_path: str) -> Optional[str]:
        """
        Convert Dropbox local path to a public shareable URL.
        
        Uses Dropbox API to create a temporary shared link.
        Falls back to manual URL construction for known Dropbox paths.
        
        Args:
            local_path: Local path to Dropbox file
        
        Returns:
            Public URL or None if not a Dropbox file
        """
        # Check if this is a Dropbox path
        dropbox_markers = ['Dropbox', 'dropbox']
        is_dropbox = any(marker in local_path for marker in dropbox_markers)
        
        if not is_dropbox:
            return None
        
        # Try to use Dropbox API if available
        try:
            import dropbox
            dbx = self._get_dropbox_client()
            if dbx:
                # Convert local path to Dropbox path
                # e.g., C:/Users/X/Dropbox/folder/file.mp4 -> /folder/file.mp4
                path_parts = local_path.replace("\\", "/").split("/")
                dropbox_idx = next((i for i, p in enumerate(path_parts) 
                                   if p.lower() == "dropbox"), -1)
                if dropbox_idx >= 0:
                    dropbox_path = "/" + "/".join(path_parts[dropbox_idx + 1:])
                    try:
                        shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
                        # Convert to direct download URL
                        url = shared_link.url.replace("?dl=0", "?dl=1")
                        logger.info(f"Created Dropbox shared link: {url[:50]}...")
                        return url
                    except dropbox.exceptions.ApiError as e:
                        if "shared_link_already_exists" in str(e):
                            links = dbx.sharing_list_shared_links(path=dropbox_path)
                            if links.links:
                                url = links.links[0].url.replace("?dl=0", "?dl=1")
                                return url
                        logger.warning(f"Dropbox API error: {e}")
        except ImportError:
            logger.info("Dropbox SDK not installed, using alternative method")
        except Exception as e:
            logger.warning(f"Dropbox link creation failed: {e}")
        
        return None
    
    def create_transcription_task(self, video_url: str, 
                                   language: str = "auto",
                                   speaker_recognition: bool = True) -> Dict:
        """
        Create a speech-to-text transcription task.
        
        Args:
            video_url: Public HTTP URL to video/audio file
            language: Language code or "auto" for auto-detect
            speaker_recognition: Enable speaker diarization
        
        Returns:
            {"task_id": str} for polling status
        """
        logger.info(f"Creating transcription task for: {video_url[:60]}...")
        
        payload = {
            "url": video_url,
            "type": 4,
            "content_type": 1,
            "speaker_recognition": 1 if speaker_recognition else 0
        }
        
        if language != "auto":
            payload["language"] = language
        
        response = self.session.post(
            f"{self.base_url}/tasks/audio/recognition",
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Task created: task_id={result.get('task_id')}")
        
        return result
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        Query transcription task status and results.
        
        Args:
            task_id: RecCloud task ID
        
        Returns:
            {
                "state": int,  # <0: Failed, 0: Queued, 1: Complete, 4: Processing
                "state_detail": str,
                "progress": int,  # 0-100
                "duration": int,  # seconds
                "source_language": str,
                "result": str  # Transcribed text (when complete)
            }
        """
        response = self.session.get(
            f"{self.base_url}/tasks/audio/recognition/{task_id}"
        )
        response.raise_for_status()
        
        return response.json()
    
    def wait_for_completion(self, task_id: str, 
                            timeout: int = 600,
                            poll_interval: int = 10) -> Dict:
        """
        Poll task until completion or timeout.
        
        Args:
            task_id: RecCloud task ID
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks
        
        Returns:
            Final task status with results
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            state = status.get("state", 0)
            
            if state == 1:  # Complete
                logger.info(f"Task {task_id} completed successfully")
                return status
            elif state < 0:  # Failed
                error_detail = status.get("state_detail", "Unknown error")
                logger.error(f"Task {task_id} failed: {error_detail}")
                raise Exception(f"Transcription failed: {error_detail}")
            else:
                progress = status.get("progress", 0)
                logger.info(f"Task {task_id}: {progress}% complete...")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Task {task_id} timed out after {timeout}s")
    
    def transcribe_from_url(self, video_url: str,
                            language: str = "auto",
                            speaker_recognition: bool = True,
                            timeout: int = 600) -> str:
        """
        Full transcription workflow: create task, wait, return result.
        
        Args:
            video_url: Public HTTP URL to video
            language: Target language
            speaker_recognition: Enable speaker ID
            timeout: Max wait time
        
        Returns:
            Transcribed text
        """
        # Create task
        task = self.create_transcription_task(
            video_url=video_url,
            language=language,
            speaker_recognition=speaker_recognition
        )
        task_id = task.get("task_id")
        
        if not task_id:
            raise ValueError("No task_id returned from RecCloud")
        
        # Wait for completion
        result = self.wait_for_completion(task_id, timeout=timeout)
        
        return result.get("result", "")
    
    def transcribe_local_file(self, local_path: str,
                               language: str = "auto",
                               speaker_recognition: bool = True) -> str:
        """
        Transcribe a local file by first getting its public URL.
        
        For Dropbox files, creates a shared link automatically.
        For other files, requires manual URL or alternative hosting.
        
        Args:
            local_path: Path to local video file
            language: Target language
            speaker_recognition: Enable speaker ID
        
        Returns:
            Transcribed text
        """
        # Try to get Dropbox public URL
        public_url = self._get_dropbox_public_url(local_path)
        
        if not public_url:
            raise ValueError(
                f"Cannot transcribe local file directly. "
                f"RecCloud requires a public HTTP URL. "
                f"Either:\n"
                f"1. Set DROPBOX_ACCESS_TOKEN to auto-create shared links\n"
                f"2. Upload file to S3/cloud storage and provide URL\n"
                f"3. Use local Whisper transcription (TRANSCRIPTION_BACKEND=local)"
            )
        
        return self.transcribe_from_url(
            video_url=public_url,
            language=language,
            speaker_recognition=speaker_recognition
        )
    
    def get_transcript(self, task_id: str) -> List[Dict]:
        """
        Get transcript segments from completed transcription.
        
        Args:
            task_id: Completed transcription task ID
        
        Returns:
            List of transcript segments
        """
        response = self.session.get(
            f"{self.base_url}/task/transcript/{task_id}"
        )
        response.raise_for_status()
        
        return response.json().get("segments", [])


# ═══════════════════════════════════════════════════════════════════════════════
# MULTILINGUAL TRANSCRIPT PARSER
# ═══════════════════════════════════════════════════════════════════════════════

class MultilingualTranscriptParser:
    """
    Parse dual-language and multilingual transcripts from RecCloud.
    Handles overlapping EN+YO, NP+EN, etc. transcripts intelligently.
    """
    
    def __init__(self):
        # Language detection patterns (diacritics-based)
        self.yoruba_chars = set("ẹọṣàáèéìíòóùúǹ")
        self.hausa_chars = set("ɓɗƙ")
        
        # Topic keywords for inference
        self.topic_keywords = {
            "storytelling": ["story", "once upon", "let me tell", "gist", "tale"],
            "coaching": ["advice", "should", "must", "help", "improve", "grow"],
            "culture": ["tradition", "yoruba", "igbo", "hausa", "nigeria", "african"],
            "entertainment": ["music", "dance", "party", "fun", "enjoy", "celebrate"],
            "business": ["money", "business", "work", "job", "career", "hustle"],
            "lifestyle": ["fashion", "beauty", "food", "health", "wellness"]
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect language based on character patterns.
        
        Returns language code: en, yo, np, ha, ig
        """
        text_lower = text.lower()
        
        # Check for Yoruba diacritics
        if any(c in text_lower for c in self.yoruba_chars):
            return "yo"
        
        # Check for Hausa characters
        if any(c in text_lower for c in self.hausa_chars):
            return "ha"
        
        # Check for Pidgin markers
        pidgin_markers = ["dey", "wetin", "wahala", "abi", "na", "wey", "abeg"]
        if sum(1 for m in pidgin_markers if m in text_lower) >= 2:
            return "np"
        
        # Default to English
        return "en"
    
    def infer_topic(self, text: str) -> str:
        """Infer topic from text content."""
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return topic
        
        return "general"
    
    def parse_dual_transcript(self, segments: List[Dict]) -> List[TranscriptSegment]:
        """
        Parse raw RecCloud segments into typed TranscriptSegment objects.
        
        Args:
            segments: Raw segments from RecCloud API
        
        Returns:
            List of TranscriptSegment objects
        """
        parsed = []
        
        for seg in segments:
            # Extract timing
            start_time = seg.get("start_time", seg.get("start", 0))
            end_time = seg.get("end_time", seg.get("end", 0))
            
            # Convert to milliseconds if needed
            if isinstance(start_time, (int, float)) and start_time < 1000:
                start_time *= 1000
                end_time *= 1000
            
            # Extract speaker
            speaker_id = seg.get("speaker_id", seg.get("speaker", "speaker_0"))
            speaker_name = seg.get("speaker_name", speaker_id)
            
            # Get text and detect language
            text = seg.get("text", "").strip()
            if not text:
                continue
            
            language = seg.get("language") or self.detect_language(text)
            confidence = seg.get("confidence", 0.9)
            is_translated = seg.get("is_translated", False)
            
            parsed.append(TranscriptSegment(
                start_time=start_time,
                end_time=end_time,
                speaker_id=speaker_id,
                speaker_name=speaker_name,
                text=text,
                language=language,
                confidence=confidence,
                is_translated=is_translated,
                original_language=seg.get("original_language")
            ))
        
        return parsed
    
    def align_paired_segments(
        self, 
        segments: List[TranscriptSegment]
    ) -> List[Tuple[TranscriptSegment, Optional[TranscriptSegment]]]:
        """
        Align segments by timestamp and speaker for dual-language pairing.
        
        Matches EN↔YO, EN↔NP, etc. by:
        1. Same speaker_id
        2. Overlapping timestamps (within 500ms tolerance)
        3. Different languages
        
        Returns:
            List of (primary_segment, optional_translation_segment) tuples
        """
        paired = []
        used_indices = set()
        tolerance_ms = 500
        
        for i, seg in enumerate(segments):
            if i in used_indices:
                continue
            
            # Find matching segment (same speaker, overlapping time, different language)
            match = None
            match_idx = None
            
            for j, other in enumerate(segments):
                if j in used_indices or j == i:
                    continue
                
                # Check speaker match
                if seg.speaker_id != other.speaker_id:
                    continue
                
                # Check language difference
                if seg.language == other.language:
                    continue
                
                # Check timestamp overlap
                time_overlap = (
                    abs(seg.start_time - other.start_time) <= tolerance_ms and
                    abs(seg.end_time - other.end_time) <= tolerance_ms
                )
                
                if time_overlap:
                    match = other
                    match_idx = j
                    break
            
            if match:
                # Determine which is original vs translation
                if seg.is_translated or (not match.is_translated and seg.language != "en"):
                    paired.append((match, seg))
                else:
                    paired.append((seg, match))
                used_indices.add(i)
                used_indices.add(match_idx)
            else:
                paired.append((seg, None))
                used_indices.add(i)
        
        return paired
    
    def extract_training_examples(
        self,
        video_id: str,
        segments: List[TranscriptSegment],
        format_type: VideoTranscriptFormat = VideoTranscriptFormat.DUAL_OVERLAY
    ) -> List[TrainingExample]:
        """
        Extract training examples from parsed segments.
        
        Args:
            video_id: Source video identifier
            segments: Parsed transcript segments
            format_type: How to process segments
        
        Returns:
            List of TrainingExample objects ready for training
        """
        examples = []
        
        if format_type == VideoTranscriptFormat.DUAL_OVERLAY:
            # Align segments for dual-language pairing
            paired = self.align_paired_segments(segments)
            
            for idx, (primary, translation) in enumerate(paired):
                languages = [primary.language]
                text_translated = None
                lang_translated = None
                
                if translation:
                    languages.append(translation.language)
                    text_translated = translation.text
                    lang_translated = translation.language
                
                duration = (primary.end_time - primary.start_time) / 1000
                timestamp = f"{primary.start_time/1000:.1f}-{primary.end_time/1000:.1f}s"
                
                example = TrainingExample(
                    video_id=video_id,
                    segment_index=idx,
                    speaker=primary.speaker_name or primary.speaker_id,
                    timestamp=timestamp,
                    languages=languages,
                    text_original=primary.text,
                    text_translated=text_translated,
                    language_original=primary.language,
                    language_translated=lang_translated,
                    topic=self.infer_topic(primary.text),
                    duration_seconds=duration,
                    confidence_score=primary.confidence
                )
                examples.append(example)
        
        else:
            # Single language or multi-track: each segment is its own example
            for idx, seg in enumerate(segments):
                duration = (seg.end_time - seg.start_time) / 1000
                timestamp = f"{seg.start_time/1000:.1f}-{seg.end_time/1000:.1f}s"
                
                example = TrainingExample(
                    video_id=video_id,
                    segment_index=idx,
                    speaker=seg.speaker_name or seg.speaker_id,
                    timestamp=timestamp,
                    languages=[seg.language],
                    text_original=seg.text,
                    text_translated=None,
                    language_original=seg.language,
                    language_translated=None,
                    topic=self.infer_topic(seg.text),
                    duration_seconds=duration,
                    confidence_score=seg.confidence
                )
                examples.append(example)
        
        logger.info(f"Extracted {len(examples)} training examples from video {video_id}")
        return examples


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO INGESTION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class LocalWhisperClient:
    """
    Local Whisper transcription using OpenAI Whisper or faster-whisper.
    Fallback when RecCloud URL hosting is not available.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize local Whisper client.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
    
    def _load_model(self):
        """Lazy load the Whisper model."""
        if self.model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model: {self.model_size}")
                self.model = whisper.load_model(self.model_size)
            except ImportError:
                raise ImportError(
                    "OpenAI Whisper not installed. "
                    "Install with: pip install openai-whisper"
                )
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        """
        Transcribe audio/video file locally.
        
        Args:
            audio_path: Path to audio/video file
            language: Language code or None for auto-detect
        
        Returns:
            Whisper result with segments
        """
        self._load_model()
        
        logger.info(f"Transcribing locally: {audio_path}")
        
        options = {"verbose": False}
        if language:
            options["language"] = language
        
        result = self.model.transcribe(audio_path, **options)
        
        logger.info(f"Transcription complete: {len(result.get('segments', []))} segments")
        return result
    
    def transcribe_to_segments(self, audio_path: str, 
                                language: str = None) -> List[Dict]:
        """
        Transcribe and return formatted segments.
        
        Returns:
            List of segment dictionaries compatible with parser
        """
        result = self.transcribe(audio_path, language)
        
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"] * 1000,  # Convert to ms
                "end": seg["end"] * 1000,
                "text": seg["text"].strip(),
                "speaker_id": "speaker_0",  # Whisper doesn't do speaker ID
                "language": result.get("language", language or "en"),
                "confidence": 0.9,  # Whisper doesn't provide confidence per segment
                "is_translated": False
            })
        
        return segments


class VideoIngestionOrchestrator:
    """
    Full pipeline: upload → transcribe → translate → extract training data.
    
    Supports multiple backends:
    - RecCloud API (requires public URL hosting)
    - Local Whisper (works with local files)
    """
    
    def __init__(
        self,
        reccloud_api_key: str = None,
        output_dir: str = "ml_training/datasets/video_training_data",
        backend: str = "auto"
    ):
        """
        Initialize orchestrator.
        
        Args:
            reccloud_api_key: RecCloud API key (optional if using local)
            output_dir: Output directory for training data
            backend: "reccloud", "local", or "auto"
        """
        self.backend = backend
        self.reccloud_key = reccloud_api_key
        
        # Initialize clients based on backend
        if reccloud_api_key and backend in ("reccloud", "auto"):
            self.reccloud_client = RecCloudClient(reccloud_api_key)
        else:
            self.reccloud_client = None
        
        self.local_client = None  # Lazy init
        
        self.parser = MultilingualTranscriptParser()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_whisper_client(self) -> LocalWhisperClient:
        """Lazy initialize local Whisper client."""
        if self.local_client is None:
            self.local_client = LocalWhisperClient(model_size="base")
        return self.local_client
    
    def _can_use_reccloud(self, video_path: str) -> bool:
        """Check if we can use RecCloud for this file."""
        if not self.reccloud_client:
            return False
        
        # Check if file is in Dropbox with API available
        if "dropbox" in video_path.lower():
            dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
            if dropbox_token:
                return True
        
        # Could add other URL hosting checks here (S3, etc.)
        return False
    
    def _transcribe_with_reccloud(self, video_path: str, 
                                   language: str) -> List[Dict]:
        """Transcribe using RecCloud API."""
        try:
            transcript_text = self.reccloud_client.transcribe_local_file(
                video_path, 
                language=language,
                speaker_recognition=True
            )
            
            # Parse the result text into segments
            # RecCloud returns plain text, need to create pseudo-segments
            segments = [{
                "start": 0,
                "end": 0,  # Will be updated
                "text": transcript_text,
                "speaker_id": "speaker_0",
                "language": language if language != "auto" else "en",
                "confidence": 0.95,
                "is_translated": False
            }]
            
            return segments
            
        except Exception as e:
            logger.error(f"RecCloud transcription failed: {e}")
            raise
    
    def _transcribe_with_whisper(self, video_path: str,
                                  language: str) -> List[Dict]:
        """Transcribe using local Whisper."""
        client = self._get_whisper_client()
        
        lang_code = None if language == "auto" else language
        return client.transcribe_to_segments(video_path, language=lang_code)
    
    def ingest_video(
        self,
        video_path: str,
        primary_language: str = "en",
        secondary_languages: List[str] = None,
        transcript_format: VideoTranscriptFormat = VideoTranscriptFormat.DUAL_OVERLAY
    ) -> List[TrainingExample]:
        """
        Full ingestion pipeline for a single video.
        
        Args:
            video_path: Path to video file
            primary_language: Primary transcription language
            secondary_languages: Languages to translate to (e.g., ["yo", "np"])
            transcript_format: How to process transcripts
        
        Returns:
            List of extracted TrainingExample objects
        """
        video_path = Path(video_path)
        video_name = video_path.stem
        video_id = f"vid_{hashlib.md5(video_name.encode()).hexdigest()[:8]}"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"INGESTING: {video_name}")
        logger.info(f"{'='*60}")
        
        try:
            # Determine transcription backend
            use_reccloud = (
                self.backend == "reccloud" or 
                (self.backend == "auto" and self._can_use_reccloud(str(video_path)))
            )
            
            if use_reccloud:
                logger.info("Using RecCloud API for transcription")
                raw_segments = self._transcribe_with_reccloud(
                    str(video_path), primary_language
                )
            else:
                logger.info("Using local Whisper for transcription")
                raw_segments = self._transcribe_with_whisper(
                    str(video_path), primary_language
                )
            
            # Note: Translation requires additional API calls
            # For local Whisper, we skip translation
            all_segments = raw_segments.copy()
            
            if secondary_languages and use_reccloud:
                logger.info(f"Translation requested for: {secondary_languages}")
                # Translation would require additional RecCloud API calls
                # This is a placeholder for future implementation
                logger.warning("Translation not yet implemented for RecCloud")
            
            # Parse and extract training examples
            parsed_segments = self.parser.parse_dual_transcript(all_segments)
            examples = self.parser.extract_training_examples(
                video_id, parsed_segments, transcript_format
            )
            
            # Save to JSONL
            output_file = self.output_dir / f"{video_name}_training.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for example in examples:
                    f.write(json.dumps(asdict(example), ensure_ascii=False) + '\n')
            
            logger.info(f"✅ Saved {len(examples)} examples to {output_file}")
            
            return examples
            
        except Exception as e:
            logger.error(f"❌ Ingestion failed for {video_name}: {e}")
            raise
    
    def batch_ingest_videos(
        self, 
        video_dir: str,
        **kwargs
    ) -> int:
        """
        Ingest all videos in a directory.
        
        Args:
            video_dir: Directory containing video files
            **kwargs: Additional arguments for ingest_video
        
        Returns:
            Total number of training examples extracted
        """
        video_dir = Path(video_dir)
        total_examples = 0
        
        # Find video files
        video_patterns = ["*.mp4", "*.mov", "*.avi", "*.mkv"]
        video_files = []
        for pattern in video_patterns:
            video_files.extend(video_dir.glob(pattern))
        
        logger.info(f"Found {len(video_files)} videos in {video_dir}")
        
        for video_file in video_files:
            try:
                examples = self.ingest_video(str(video_file), **kwargs)
                total_examples += len(examples)
            except Exception as e:
                logger.error(f"Failed to process {video_file}: {e}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH COMPLETE: {total_examples} total examples")
        logger.info(f"{'='*60}")
        
        return total_examples


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Load API key from environment
    api_key = os.getenv("RECCLOUD_API_KEY")
    if not api_key:
        logger.error("RECCLOUD_API_KEY not set in environment")
        exit(1)
    
    # Initialize orchestrator
    orchestrator = VideoIngestionOrchestrator(api_key)
    
    # Example: Ingest a video with dual EN+YO transcripts
    video_dir = os.getenv("VIDEO_SOURCE_DIR", "C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS")
    
    if Path(video_dir).exists():
        examples = orchestrator.batch_ingest_videos(
            video_dir,
            primary_language="en",
            secondary_languages=["yo", "np"],
            transcript_format=VideoTranscriptFormat.DUAL_OVERLAY
        )
        print(f"Extracted {examples} training examples")
    else:
        print(f"Video directory not found: {video_dir}")
