#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - WHISPER VIDEO INGESTION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
# Uses OpenAI Whisper (via transformers) for local video transcription
# Supports multilingual transcription and training data extraction
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
import subprocess
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import torch
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhisperIngestion")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class LanguageCode(str, Enum):
    """Supported languages for Sisi Lola training."""
    ENGLISH = "en"
    YORUBA = "yo"
    PIDGIN = "pcm"  # Nigerian Pidgin ISO code
    HAUSA = "ha"
    IGBO = "ig"


@dataclass
class TranscriptSegment:
    """Single segment of transcribed speech."""
    start_time: float
    end_time: float
    text: str
    language: str
    confidence: float = 0.9


@dataclass 
class TrainingExample:
    """Single training example extracted from video transcript."""
    video_id: str
    segment_type: str  # "teaching", "conversation", "qa"
    text: str
    languages: List[str]
    speaker: str
    topic: str
    timestamp: float
    duration: float


# ═══════════════════════════════════════════════════════════════════════════════
# WHISPER TRANSCRIBER
# ═══════════════════════════════════════════════════════════════════════════════

class WhisperTranscriber:
    """
    Local Whisper transcription using transformers pipeline.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
    
    def load_model(self):
        """Load Whisper model lazily."""
        if self.model is not None:
            return
        
        logger.info(f"Loading Whisper {self.model_size} model...")
        
        try:
            from transformers import pipeline
            
            model_id = f"openai/whisper-{self.model_size}"
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model_id,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            logger.info(f"✓ Whisper {self.model_size} loaded on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file using FFmpeg.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        video_path = Path(video_path)
        
        # Create temp audio file
        audio_path = tempfile.mktemp(suffix=".wav")
        
        logger.info(f"Extracting audio from: {video_path.name}")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM format
            "-ar", "16000",  # 16kHz sample rate (Whisper requires this)
            "-ac", "1",  # Mono
            audio_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"Failed to extract audio: {result.stderr}")
        
        logger.info(f"✓ Audio extracted: {audio_path}")
        return audio_path
    
    def transcribe(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Target language code
            
        Returns:
            Transcription result with timestamps
        """
        self.load_model()
        
        logger.info(f"Transcribing audio ({language})...")
        
        # Use chunked transcription for long files
        result = self.pipe(
            audio_path,
            return_timestamps=True,
            generate_kwargs={
                "language": language,
                "task": "transcribe"
            }
        )
        
        return result
    
    def transcribe_video(self, video_path: str, language: str = "en") -> List[TranscriptSegment]:
        """
        Transcribe video file end-to-end.
        
        Args:
            video_path: Path to video file
            language: Target language code
            
        Returns:
            List of transcript segments
        """
        # Extract audio
        audio_path = self.extract_audio(video_path)
        
        try:
            # Transcribe
            result = self.transcribe(audio_path, language)
            
            # Parse segments
            segments = []
            
            if "chunks" in result:
                for chunk in result["chunks"]:
                    segment = TranscriptSegment(
                        start_time=chunk["timestamp"][0] or 0.0,
                        end_time=chunk["timestamp"][1] or 0.0,
                        text=chunk["text"].strip(),
                        language=language
                    )
                    segments.append(segment)
            else:
                # Single segment for short audio
                segments.append(TranscriptSegment(
                    start_time=0.0,
                    end_time=0.0,
                    text=result["text"].strip(),
                    language=language
                ))
            
            logger.info(f"✓ Transcribed {len(segments)} segments")
            return segments
            
        finally:
            # Cleanup temp audio
            if os.path.exists(audio_path):
                os.remove(audio_path)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING DATA EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════════

class TrainingDataExtractor:
    """
    Converts transcript segments into training examples for LLM fine-tuning.
    """
    
    # Topic keywords for classification
    TOPIC_KEYWORDS = {
        "fashion": ["style", "wear", "dress", "outfit", "ankara", "clothes", "fashion"],
        "culture": ["nigeria", "naija", "yoruba", "igbo", "hausa", "tradition", "culture"],
        "motivation": ["inspire", "motivate", "believe", "dream", "success", "confidence"],
        "relationships": ["love", "relationship", "marriage", "partner", "dating"],
        "lifestyle": ["life", "living", "home", "food", "jollof", "party", "owambe"],
        "music": ["music", "song", "sing", "artist", "album", "studio", "church"],
        "business": ["business", "money", "work", "career", "hustle", "entrepreneur"]
    }
    
    def __init__(self):
        self.examples = []
    
    def classify_topic(self, text: str) -> str:
        """Classify text into a topic category."""
        text_lower = text.lower()
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return topic
        
        return "general"
    
    def detect_pidgin(self, text: str) -> bool:
        """Detect if text contains Nigerian Pidgin."""
        pidgin_markers = [
            "dey", "na", "abi", "wahala", "wetin", "dem", "una",
            "abeg", "omo", "sha", "shey", "sef", "gist", "yarn"
        ]
        text_lower = text.lower()
        return any(marker in text_lower.split() for marker in pidgin_markers)
    
    def segment_to_examples(
        self, 
        segment: TranscriptSegment, 
        video_id: str,
        segment_index: int
    ) -> List[TrainingExample]:
        """
        Convert a transcript segment into training examples.
        
        Creates multiple examples if the segment is long enough.
        """
        text = segment.text.strip()
        
        # Skip very short segments
        if len(text) < 20:
            return []
        
        # Detect languages
        languages = [segment.language]
        if self.detect_pidgin(text):
            languages.append("np")
        
        # Classify topic
        topic = self.classify_topic(text)
        
        # Create example
        example = TrainingExample(
            video_id=video_id,
            segment_type="teaching",
            text=text,
            languages=languages,
            speaker="Sisi Lola",
            topic=topic,
            timestamp=segment.start_time,
            duration=segment.end_time - segment.start_time if segment.end_time else 0
        )
        
        return [example]
    
    def extract_from_segments(
        self,
        segments: List[TranscriptSegment],
        video_id: str
    ) -> List[TrainingExample]:
        """Extract all training examples from transcript segments."""
        examples = []
        
        for i, segment in enumerate(segments):
            segment_examples = self.segment_to_examples(segment, video_id, i)
            examples.extend(segment_examples)
        
        logger.info(f"✓ Extracted {len(examples)} training examples")
        return examples


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO INGESTION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class VideoIngestionOrchestrator:
    """
    Main orchestrator for video → training data pipeline.
    """
    
    def __init__(
        self,
        output_dir: str = "ml_training/datasets/video_training_data",
        model_size: str = "base"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.transcriber = WhisperTranscriber(model_size=model_size)
        self.extractor = TrainingDataExtractor()
    
    def ingest_video(
        self,
        video_path: str,
        primary_language: str = "en"
    ) -> List[TrainingExample]:
        """
        Ingest a single video and extract training examples.
        
        Args:
            video_path: Path to video file
            primary_language: Primary language in video
            
        Returns:
            List of training examples
        """
        video_path = Path(video_path)
        video_id = video_path.stem
        
        logger.info(f"\n{'='*60}")
        logger.info(f"INGESTING: {video_id}")
        logger.info(f"{'='*60}")
        
        # Transcribe video
        segments = self.transcriber.transcribe_video(str(video_path), primary_language)
        
        # Extract training examples
        examples = self.extractor.extract_from_segments(segments, video_id)
        
        # Save to JSONL
        output_file = self.output_dir / f"{video_id}.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for ex in examples:
                f.write(json.dumps(asdict(ex), ensure_ascii=False) + '\n')
        
        logger.info(f"✓ Saved to: {output_file}")
        
        return examples
    
    def ingest_batch(
        self,
        video_dir: str,
        primary_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Ingest all videos in a directory.
        
        Args:
            video_dir: Directory containing video files
            primary_language: Primary language in videos
            
        Returns:
            Summary report
        """
        video_dir = Path(video_dir)
        
        # Find all video files
        video_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        video_files = []
        for ext in video_extensions:
            video_files.extend(video_dir.glob(f"*{ext}"))
        
        video_files = sorted(set(video_files))
        
        if not video_files:
            logger.warning(f"No video files found in {video_dir}")
            return {"error": "No videos found"}
        
        logger.info(f"\n╔{'═'*58}╗")
        logger.info(f"║  SISI LOLA - BATCH VIDEO INGESTION                       ║")
        logger.info(f"║  Found {len(video_files):3d} video files                               ║")
        logger.info(f"╚{'═'*58}╝\n")
        
        # Process videos
        all_examples = []
        processed = 0
        failed = 0
        
        for video_file in tqdm(video_files, desc="Processing videos"):
            try:
                examples = self.ingest_video(str(video_file), primary_language)
                all_examples.extend(examples)
                processed += 1
            except Exception as e:
                logger.error(f"Failed to process {video_file.name}: {e}")
                failed += 1
        
        # Save combined manifest
        manifest = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "total_examples": len(all_examples),
            "videos_processed": processed,
            "videos_failed": failed,
            "languages": {},
            "topics": {}
        }
        
        # Count statistics
        for ex in all_examples:
            for lang in ex.languages:
                manifest["languages"][lang] = manifest["languages"].get(lang, 0) + 1
            manifest["topics"][ex.topic] = manifest["topics"].get(ex.topic, 0) + 1
        
        manifest_path = self.output_dir / "ingestion_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Summary
        logger.info(f"\n╔{'═'*58}╗")
        logger.info(f"║  BATCH INGESTION COMPLETE                                ║")
        logger.info(f"╚{'═'*58}╝\n")
        logger.info(f"Videos processed: {processed}")
        logger.info(f"Videos failed:    {failed}")
        logger.info(f"Total examples:   {len(all_examples)}")
        logger.info(f"Languages: {manifest['languages']}")
        logger.info(f"Topics: {manifest['topics']}")
        
        return manifest


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Whisper Video Ingestion for Sisi Lola")
    parser.add_argument("mode", choices=["single", "batch"], help="Processing mode")
    parser.add_argument("path", help="Video file or directory path")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size")
    parser.add_argument("--language", default="en", help="Primary language code")
    parser.add_argument("--output", default="ml_training/datasets/video_training_data",
                        help="Output directory")
    
    args = parser.parse_args()
    
    orchestrator = VideoIngestionOrchestrator(
        output_dir=args.output,
        model_size=args.model
    )
    
    if args.mode == "single":
        examples = orchestrator.ingest_video(args.path, args.language)
        print(f"\n✓ Extracted {len(examples)} training examples")
    else:
        result = orchestrator.ingest_batch(args.path, args.language)
        print(f"\n✓ Batch complete: {result}")


if __name__ == "__main__":
    main()
