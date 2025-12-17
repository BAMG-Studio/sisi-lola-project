#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - RECCLOUD INGESTION RUNNER (Quick Start CLI)
# ═══════════════════════════════════════════════════════════════════════════════
# Ready-to-run script for developers: single command to ingest all videos
# Usage:
#   python reccloud_ingest_runner.py batch                    # Process all videos
#   python reccloud_ingest_runner.py single "path/to/video.mp4"  # Single video
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Try to import WhisperVideoIngestion (local Whisper), fallback to RecCloud
try:
    from ml_training.scripts.whisper_video_ingestion import (
        VideoIngestionOrchestrator,
        TrainingExample,
        LanguageCode
    )
    TRANSCRIPTION_BACKEND = "whisper"
    logger.info("Using Whisper backend for transcription")
except ImportError:
    from ml_training.scripts.reccloud_video_ingestion import (
        VideoIngestionOrchestrator,
        VideoTranscriptFormat,
        LanguageCode
    )
    TRANSCRIPTION_BACKEND = "reccloud"
    logger.info("Using RecCloud backend for transcription")

# Setup logging
log_dir = PROJECT_ROOT / "ml_training" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'reccloud_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Video source directory
VIDEO_SOURCE_DIR = os.getenv(
    "VIDEO_SOURCE_DIR",
    "C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS"
)

# Output directory
OUTPUT_DIR = os.getenv(
    "RECCLOUD_OUTPUT_DIR",
    "ml_training/datasets/video_training_data"
)

# Transcription settings
PRIMARY_LANGUAGE = "en"              # Primary transcription language
SECONDARY_LANGUAGES = ["yo", "np"]   # Languages to translate to (Yoruba, Pidgin)
TRANSCRIPT_FORMAT = "dual"           # "single" | "dual" | "multi"

# Processing settings
BATCH_SIZE = 5                       # Max videos to process simultaneously
SKIP_EXISTING = True                 # Skip videos already ingested
RETRY_FAILED = True                  # Retry failed videos


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

class RecCloudIngestRunner:
    """
    Main orchestrator for video ingestion with manifest tracking.
    Supports both Whisper (local) and RecCloud (API) backends.
    """
    
    def __init__(self):
        # Check for API key if using RecCloud
        self.api_key = os.getenv("RECCLOUD_API_KEY")
        
        # Initialize orchestrator based on backend
        if TRANSCRIPTION_BACKEND == "whisper":
            # Use local Whisper - no API key needed
            self.orchestrator = VideoIngestionOrchestrator(
                output_dir=OUTPUT_DIR,
                model_size="base"  # Use base model for balance of speed/accuracy
            )
            logger.info("Initialized Whisper transcriber (local)")
        else:
            if not self.api_key:
                logger.error("RECCLOUD_API_KEY not set!")
                raise ValueError("RECCLOUD_API_KEY not set")
            self.orchestrator = VideoIngestionOrchestrator(
                reccloud_api_key=self.api_key,
                output_dir=OUTPUT_DIR
            )
        
        # Setup output directory
        self.output_dir = PROJECT_ROOT / OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load/create ingestion manifest
        self.manifest_path = self.output_dir / "ingestion_manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> dict:
        """Load or create video ingestion manifest."""
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "videos_processed": [],
            "total_examples": 0,
            "languages": {},
            "topics": {},
            "errors": []
        }
    
    def _save_manifest(self):
        """Save ingestion manifest."""
        self.manifest["last_updated"] = datetime.now().isoformat()
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def _should_skip(self, video_path: str) -> bool:
        """Check if video was already processed."""
        if not SKIP_EXISTING:
            return False
        
        video_name = Path(video_path).stem
        for entry in self.manifest.get("videos_processed", []):
            if entry.get("video_name") == video_name and entry.get("status") == "success":
                return True
        
        return False
    
    def _update_manifest_stats(self, examples: list):
        """Update manifest statistics from examples."""
        for ex in examples:
            # Track languages
            for lang in ex.get("languages", []):
                self.manifest["languages"][lang] = self.manifest["languages"].get(lang, 0) + 1
            
            # Track topics
            topic = ex.get("topic", "general")
            self.manifest["topics"][topic] = self.manifest["topics"].get(topic, 0) + 1
    
    def ingest_single_video(self, video_path: str) -> int:
        """
        Ingest a single video.
        
        Returns:
            Number of training examples extracted
        """
        video_path = str(video_path)
        video_name = Path(video_path).stem
        
        logger.info(f"\n[→] Processing: {video_name}")
        
        # Check if already processed
        if self._should_skip(video_path):
            logger.info(f"[⊘] Skipping (already processed): {video_name}")
            return 0
        
        try:
            # Call orchestrator based on backend
            if TRANSCRIPTION_BACKEND == "whisper":
                examples = self.orchestrator.ingest_video(
                    video_path=video_path,
                    primary_language=PRIMARY_LANGUAGE
                )
            else:
                # RecCloud backend
                format_enum = VideoTranscriptFormat(TRANSCRIPT_FORMAT)
                examples = self.orchestrator.ingest_video(
                    video_path=video_path,
                    primary_language=PRIMARY_LANGUAGE,
                    secondary_languages=SECONDARY_LANGUAGES,
                    transcript_format=format_enum
                )
            
            # Update manifest
            self.manifest["videos_processed"].append({
                "video_name": video_name,
                "video_path": video_path,
                "processed_at": datetime.now().isoformat(),
                "examples_extracted": len(examples),
                "status": "success"
            })
            self.manifest["total_examples"] += len(examples)
            
            # Update stats
            example_dicts = [{"languages": ex.languages, "topic": ex.topic} for ex in examples]
            self._update_manifest_stats(example_dicts)
            
            self._save_manifest()
            
            logger.info(f"[✓] Completed: {video_name} ({len(examples)} examples)")
            return len(examples)
        
        except Exception as e:
            logger.exception(f"[✗] Failed: {video_name} - {e}")
            self.manifest["errors"].append({
                "video_name": video_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self._save_manifest()
            return 0
    
    def ingest_batch(self, video_dir: str = None) -> dict:
        """
        Ingest all videos in a directory.
        
        Args:
            video_dir: Directory containing videos (default: VIDEO_SOURCE_DIR)
        
        Returns:
            Summary report
        """
        video_dir = Path(video_dir or VIDEO_SOURCE_DIR)
        
        if not video_dir.exists():
            logger.error(f"Video directory not found: {video_dir}")
            return {"error": f"Directory not found: {video_dir}"}
        
        # Find all video files
        video_patterns = ["*.mp4", "*.mov", "*.avi", "*.mkv"]
        video_files = []
        for pattern in video_patterns:
            video_files.extend(video_dir.glob(pattern))
        
        video_files = sorted(set(video_files))  # Remove duplicates, sort
        
        if not video_files:
            logger.warning(f"No video files found in {video_dir}")
            return {"error": "No video files found"}
        
        logger.info(f"\n╔════════════════════════════════════════════════════════════╗")
        logger.info(f"║    SISI LOLA - BATCH VIDEO INGESTION                       ║")
        logger.info(f"║    Found {len(video_files):3d} video files                                 ║")
        logger.info(f"╚════════════════════════════════════════════════════════════╝\n")
        
        # Process videos
        total_examples = 0
        processed = 0
        skipped = 0
        failed = 0
        
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"\n[{i}/{len(video_files)}] {video_file.name}")
            
            if self._should_skip(str(video_file)):
                logger.info(f"  ⊘ Skipping (already processed)")
                skipped += 1
                continue
            
            count = self.ingest_single_video(str(video_file))
            if count > 0:
                total_examples += count
                processed += 1
            else:
                failed += 1
        
        # Final report
        logger.info(f"\n╔════════════════════════════════════════════════════════════╗")
        logger.info(f"║    BATCH INGESTION COMPLETE                                ║")
        logger.info(f"╚════════════════════════════════════════════════════════════╝\n")
        
        logger.info(f"Videos processed: {processed}")
        logger.info(f"Videos skipped:   {skipped}")
        logger.info(f"Videos failed:    {failed}")
        logger.info(f"Total examples:   {self.manifest['total_examples']}")
        logger.info(f"\nLanguages: {json.dumps(self.manifest['languages'], indent=2)}")
        logger.info(f"Topics: {json.dumps(self.manifest['topics'], indent=2)}")
        
        if self.manifest['errors']:
            logger.warning(f"\nErrors ({len(self.manifest['errors'])}):")
            for err in self.manifest['errors'][-5:]:  # Show last 5
                logger.warning(f"  - {err['video_name']}: {err['error']}")
        
        logger.info(f"\nManifest saved: {self.manifest_path}")
        
        return {
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "total_examples": self.manifest['total_examples'],
            "manifest_path": str(self.manifest_path)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def print_usage():
    """Print usage instructions."""
    print("""
╔════════════════════════════════════════════════════════════╗
║    SISI LOLA - RECCLOUD VIDEO INGESTION                   ║
╚════════════════════════════════════════════════════════════╝

Usage:
  python reccloud_ingest_runner.py batch                     # Process all videos
  python reccloud_ingest_runner.py single "path/to/video.mp4"  # Single video
  python reccloud_ingest_runner.py status                    # Show manifest status

Environment Variables:
  RECCLOUD_API_KEY     - Your RecCloud API key (required)
  VIDEO_SOURCE_DIR     - Directory with video files
  RECCLOUD_OUTPUT_DIR  - Output directory for training data

Examples:
  export RECCLOUD_API_KEY="your_key_here"
  python reccloud_ingest_runner.py batch
""")


if __name__ == "__main__":
    logger.info("Starting RecCloud Video Ingestion Runner...\n")
    
    try:
        runner = RecCloudIngestRunner()
        
        # Parse command-line arguments
        mode = sys.argv[1] if len(sys.argv) > 1 else "help"
        
        if mode == "single" and len(sys.argv) > 2:
            video_file = sys.argv[2]
            if not Path(video_file).exists():
                logger.error(f"Video file not found: {video_file}")
                sys.exit(1)
            count = runner.ingest_single_video(video_file)
            logger.info(f"\n[✓] Extracted {count} training examples")
        
        elif mode == "batch":
            video_dir = sys.argv[2] if len(sys.argv) > 2 else None
            result = runner.ingest_batch(video_dir)
            logger.info(f"\n[✓] Batch complete: {result}")
        
        elif mode == "status":
            print(f"\nManifest: {runner.manifest_path}")
            print(json.dumps(runner.manifest, indent=2))
        
        else:
            print_usage()
            sys.exit(0)
        
        logger.info("\n[✓] Ingestion complete!")
        sys.exit(0)
    
    except ValueError as e:
        logger.error(str(e))
        print_usage()
        sys.exit(1)
    except Exception as e:
        logger.exception(f"[!] Fatal error: {e}")
        sys.exit(1)
