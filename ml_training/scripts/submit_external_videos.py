#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - EXTERNAL VIDEO SUBMISSION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
# Batch submission of external videos to RecCloud for transcription
# December 14, 2025
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import csv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

# Try to import the existing RecCloud client
try:
    from ml_training.scripts.reccloud_video_ingestion import RecCloudClient, VideoMetadata
    HAS_RECCLOUD = True
except ImportError:
    HAS_RECCLOUD = False
    print("Warning: RecCloud client not available. Running in dry-run mode.")

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_training/logs/external_video_submission.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExternalVideoSubmission")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExternalVideoConfig:
    """Configuration for external video processing."""
    
    # Base paths
    project_root: Path = Path(__file__).parent.parent.parent
    external_videos_dir: Path = None
    output_dir: Path = None
    tracker_file: Path = None
    
    # Tier directories
    tier_dirs: Dict[str, str] = None
    
    # RecCloud settings
    primary_language: str = "yo"
    secondary_language: str = "en"
    speaker_detection: bool = True
    translation_enabled: bool = True
    dual_transcript: bool = True
    
    # Processing settings
    batch_size: int = 5
    retry_attempts: int = 3
    polling_interval: int = 30
    
    def __post_init__(self):
        self.external_videos_dir = self.project_root / "ml_training" / "external_videos"
        self.output_dir = self.project_root / "ml_training" / "datasets" / "external_video_training"
        self.tracker_file = self.external_videos_dir / "external_videos_tracker.csv"
        
        self.tier_dirs = {
            "tier1_ted": self.external_videos_dir / "tier1_ted",
            "tier1_bbc": self.external_videos_dir / "tier1_bbc",
            "tier1_educational": self.external_videos_dir / "tier1_educational",
            "tier2_youtube": self.external_videos_dir / "tier2_youtube",
            "tier2_podcasts": self.external_videos_dir / "tier2_podcasts",
            "tier3_licensed": self.external_videos_dir / "tier3_licensed",
        }


@dataclass
class ExternalVideo:
    """Represents an external video for processing."""
    video_id: str
    title: str
    creator: str
    source_url: str
    file_path: Path
    metadata_path: Path
    duration_seconds: float
    primary_language: str
    secondary_languages: List[str]
    license_type: str
    tier: int
    category: str
    persona_pillars: List[str]
    attribution: str
    processing_status: str
    cost: float
    notes: str
    acquisition_date: str = None
    processed_date: str = None
    reccloud_job_id: str = None
    expected_examples: int = 0
    
    @classmethod
    def from_metadata(cls, metadata_path: Path, video_path: Path) -> 'ExternalVideo':
        """Create ExternalVideo from metadata JSON file."""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            video_id=data.get('video_id', ''),
            title=data.get('title', ''),
            creator=data.get('creator', ''),
            source_url=data.get('source_url', ''),
            file_path=video_path,
            metadata_path=metadata_path,
            duration_seconds=data.get('duration_seconds', 0),
            primary_language=data.get('primary_language', 'en'),
            secondary_languages=data.get('secondary_languages', []),
            license_type=data.get('license_type', ''),
            tier=data.get('tier', 1),
            category=data.get('category', ''),
            persona_pillars=data.get('persona_pillars', []),
            attribution=data.get('attribution', ''),
            processing_status=data.get('processing_status', 'pending'),
            cost=data.get('cost', 0.0),
            notes=data.get('notes', ''),
            acquisition_date=data.get('acquisition_date', ''),
            expected_examples=data.get('expected_examples', 0),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

class ExternalVideoDiscovery:
    """Discovers and loads external videos from tier directories."""
    
    def __init__(self, config: ExternalVideoConfig):
        self.config = config
    
    def discover_videos(self, phase: int = None) -> List[ExternalVideo]:
        """Discover all external videos, optionally filtered by phase."""
        videos = []
        
        # Map phases to tiers
        phase_tier_map = {
            1: ['tier1_ted', 'tier1_bbc', 'tier1_educational'],
            2: ['tier2_youtube', 'tier2_podcasts'],
            3: ['tier3_licensed'],
        }
        
        # Determine which tier directories to scan
        if phase:
            tier_names = phase_tier_map.get(phase, [])
            tier_dirs = {k: v for k, v in self.config.tier_dirs.items() if k in tier_names}
        else:
            tier_dirs = self.config.tier_dirs
        
        for tier_name, tier_dir in tier_dirs.items():
            if not tier_dir.exists():
                logger.warning(f"Tier directory not found: {tier_dir}")
                continue
            
            # Find all video files
            video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.mp3', '.m4a']
            
            for video_file in tier_dir.iterdir():
                if video_file.suffix.lower() in video_extensions:
                    # Look for corresponding metadata file
                    metadata_file = video_file.with_suffix('.json')
                    
                    if metadata_file.exists():
                        try:
                            video = ExternalVideo.from_metadata(metadata_file, video_file)
                            videos.append(video)
                            logger.info(f"Discovered: {video.title} ({tier_name})")
                        except Exception as e:
                            logger.error(f"Error loading metadata for {video_file}: {e}")
                    else:
                        logger.warning(f"No metadata file for: {video_file}")
        
        logger.info(f"Discovered {len(videos)} external videos")
        return videos
    
    def get_pending_videos(self, phase: int = None) -> List[ExternalVideo]:
        """Get videos that haven't been processed yet."""
        all_videos = self.discover_videos(phase)
        pending = [v for v in all_videos if v.processing_status in ['pending', 'downloaded']]
        logger.info(f"Found {len(pending)} pending videos")
        return pending


# ═══════════════════════════════════════════════════════════════════════════════
# RECCLOUD SUBMISSION
# ═══════════════════════════════════════════════════════════════════════════════

class ExternalVideoSubmitter:
    """Submits external videos to RecCloud for transcription."""
    
    def __init__(self, config: ExternalVideoConfig):
        self.config = config
        self.reccloud_client = None
        
        if HAS_RECCLOUD:
            api_key = os.getenv('RECCLOUD_API_KEY')
            if api_key:
                self.reccloud_client = RecCloudClient(api_key)
                logger.info("RecCloud client initialized")
            else:
                logger.warning("RECCLOUD_API_KEY not found in environment")
    
    def submit_video(self, video: ExternalVideo, dry_run: bool = False) -> Dict[str, Any]:
        """Submit a single video to RecCloud."""
        logger.info(f"Submitting: {video.title}")
        
        if dry_run:
            logger.info(f"[DRY RUN] Would submit: {video.file_path}")
            return {
                'status': 'dry_run',
                'video_id': video.video_id,
                'message': 'Dry run - no actual submission'
            }
        
        if not self.reccloud_client:
            logger.error("RecCloud client not available")
            return {
                'status': 'error',
                'video_id': video.video_id,
                'message': 'RecCloud client not initialized'
            }
        
        try:
            # Create video URL (for RecCloud, videos need to be accessible via URL)
            # This could use Dropbox, S3, or another hosting service
            video_url = self._get_video_url(video)
            
            if not video_url:
                return {
                    'status': 'error',
                    'video_id': video.video_id,
                    'message': 'Could not generate video URL'
                }
            
            # Submit to RecCloud
            result = self.reccloud_client.upload_and_process(
                video_url=video_url,
                primary_lang=video.primary_language,
                translate_to=video.secondary_languages[0] if video.secondary_languages else None,
                dual_transcript=self.config.dual_transcript,
                speaker_detection=self.config.speaker_detection
            )
            
            # Update video status
            video.processing_status = 'processing'
            video.reccloud_job_id = result.get('job_id', '')
            self._update_metadata(video)
            
            return {
                'status': 'submitted',
                'video_id': video.video_id,
                'job_id': result.get('job_id', ''),
                'message': 'Successfully submitted to RecCloud'
            }
            
        except Exception as e:
            logger.error(f"Error submitting {video.title}: {e}")
            return {
                'status': 'error',
                'video_id': video.video_id,
                'message': str(e)
            }
    
    def submit_batch(self, videos: List[ExternalVideo], dry_run: bool = False) -> List[Dict[str, Any]]:
        """Submit a batch of videos to RecCloud."""
        results = []
        
        for i, video in enumerate(videos):
            logger.info(f"Processing {i+1}/{len(videos)}: {video.title}")
            result = self.submit_video(video, dry_run)
            results.append(result)
            
            # Small delay between submissions to avoid rate limiting
            if not dry_run and i < len(videos) - 1:
                import time
                time.sleep(2)
        
        return results
    
    def _get_video_url(self, video: ExternalVideo) -> Optional[str]:
        """Generate a public URL for the video file."""
        # Option 1: If already a URL, use it
        if video.source_url and video.source_url.startswith('http'):
            return video.source_url
        
        # Option 2: Use Dropbox shared link
        dropbox_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        if dropbox_token:
            try:
                import dropbox
                dbx = dropbox.Dropbox(dropbox_token)
                
                # Convert local path to Dropbox path
                dropbox_path = str(video.file_path).replace(
                    'C:/Users/POK28/Dropbox/Sisi_Lola',
                    ''
                ).replace('\\', '/')
                
                # Create shared link
                shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
                return shared_link.url.replace('?dl=0', '?dl=1')
                
            except Exception as e:
                logger.warning(f"Could not create Dropbox link: {e}")
        
        # Option 3: Log warning and return None
        logger.warning(f"No URL available for {video.file_path}")
        return None
    
    def _update_metadata(self, video: ExternalVideo):
        """Update the video's metadata file with current status."""
        try:
            with open(video.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['processing_status'] = video.processing_status
            data['reccloud_job_id'] = video.reccloud_job_id
            data['processed_date'] = datetime.now().isoformat()
            
            with open(video.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

class ExternalVideoTracker:
    """Tracks status of external video processing."""
    
    def __init__(self, config: ExternalVideoConfig):
        self.config = config
        self.tracker_file = config.tracker_file
    
    def update_tracker(self, videos: List[ExternalVideo]):
        """Update the CSV tracker file with current video statuses."""
        fieldnames = [
            'video_id', 'title', 'creator', 'tier', 'phase', 'status', 
            'cost', 'expected_examples', 'date_acquired', 'date_processed',
            'persona_pillars', 'notes', 'reccloud_job_id'
        ]
        
        with open(self.tracker_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for video in videos:
                # Determine phase from tier
                phase = 1 if video.tier == 1 else (2 if video.tier == 2 else 3)
                
                writer.writerow({
                    'video_id': video.video_id,
                    'title': video.title,
                    'creator': video.creator,
                    'tier': video.tier,
                    'phase': phase,
                    'status': video.processing_status,
                    'cost': video.cost,
                    'expected_examples': video.expected_examples,
                    'date_acquired': video.acquisition_date,
                    'date_processed': video.processed_date or '',
                    'persona_pillars': '|'.join(video.persona_pillars),
                    'notes': video.notes,
                    'reccloud_job_id': video.reccloud_job_id or ''
                })
        
        logger.info(f"Updated tracker: {self.tracker_file}")
    
    def get_status_summary(self, videos: List[ExternalVideo]) -> Dict[str, Any]:
        """Get a summary of video processing status."""
        status_counts = {}
        tier_counts = {}
        total_duration = 0
        total_cost = 0
        
        for video in videos:
            # Status counts
            status = video.processing_status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Tier counts
            tier_counts[video.tier] = tier_counts.get(video.tier, 0) + 1
            
            # Totals
            total_duration += video.duration_seconds
            total_cost += video.cost
        
        return {
            'total_videos': len(videos),
            'status_breakdown': status_counts,
            'tier_breakdown': tier_counts,
            'total_duration_minutes': total_duration / 60,
            'total_cost': total_cost,
            'estimated_reccloud_cost': (total_duration / 60) * 0.004  # $0.004 per minute
        }
    
    def print_status(self, videos: List[ExternalVideo]):
        """Print a formatted status report."""
        summary = self.get_status_summary(videos)
        
        print("\n" + "=" * 60)
        print("EXTERNAL VIDEO PROCESSING STATUS")
        print("=" * 60)
        print(f"\nTotal Videos: {summary['total_videos']}")
        print(f"Total Duration: {summary['total_duration_minutes']:.1f} minutes")
        print(f"Total Cost (Videos): ${summary['total_cost']:.2f}")
        print(f"Estimated RecCloud Cost: ${summary['estimated_reccloud_cost']:.2f}")
        
        print("\n--- Status Breakdown ---")
        for status, count in summary['status_breakdown'].items():
            print(f"  {status}: {count}")
        
        print("\n--- Tier Breakdown ---")
        for tier, count in summary['tier_breakdown'].items():
            print(f"  Tier {tier}: {count} videos")
        
        print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Submit external videos to RecCloud for transcription'
    )
    
    parser.add_argument(
        'command',
        choices=['submit', 'status', 'discover', 'update-tracker'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        help='Process only videos from specified phase (1=Tier1, 2=Tier2, 3=Tier3)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually submitting'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all videos, not just pending ones'
    )
    
    args = parser.parse_args()
    
    # Initialize components
    config = ExternalVideoConfig()
    discovery = ExternalVideoDiscovery(config)
    submitter = ExternalVideoSubmitter(config)
    tracker = ExternalVideoTracker(config)
    
    if args.command == 'discover':
        # Just discover and list videos
        videos = discovery.discover_videos(args.phase)
        print(f"\nDiscovered {len(videos)} videos:")
        for v in videos:
            print(f"  - [{v.tier}] {v.title} ({v.processing_status})")
    
    elif args.command == 'status':
        # Show status of all videos
        videos = discovery.discover_videos(args.phase)
        tracker.print_status(videos)
    
    elif args.command == 'update-tracker':
        # Update the tracker CSV
        videos = discovery.discover_videos()
        tracker.update_tracker(videos)
        print(f"Tracker updated: {tracker.tracker_file}")
    
    elif args.command == 'submit':
        # Submit videos to RecCloud
        if args.all:
            videos = discovery.discover_videos(args.phase)
        else:
            videos = discovery.get_pending_videos(args.phase)
        
        if not videos:
            print("No videos to submit.")
            return
        
        print(f"\nSubmitting {len(videos)} videos...")
        if args.dry_run:
            print("[DRY RUN MODE - No actual submissions]")
        
        results = submitter.submit_batch(videos, dry_run=args.dry_run)
        
        # Print results
        print("\n--- Submission Results ---")
        for result in results:
            status_icon = "✅" if result['status'] in ['submitted', 'dry_run'] else "❌"
            print(f"  {status_icon} {result['video_id']}: {result['message']}")
        
        # Update tracker
        if not args.dry_run:
            all_videos = discovery.discover_videos()
            tracker.update_tracker(all_videos)


if __name__ == '__main__':
    main()
