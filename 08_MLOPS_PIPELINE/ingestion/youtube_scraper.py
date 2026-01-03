#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - ADVANCED YOUTUBE VIDEO SCRAPER & INGESTION PIPELINE
═══════════════════════════════════════════════════════════════════════════════
Automated bulk downloading and ingestion of Nigerian/African content videos.

Uses yt-dlp for robust video scraping with:
- Channel/playlist automation
- Transcript extraction (auto-captions, manual captions)
- Metadata extraction for contextual training
- Rate limiting and retry logic
- Quality filtering for training data

USAGE:
    python youtube_scraper.py --channels "UCxyz123" --output ./data/raw_videos
    python youtube_scraper.py --playlist "PLxyz123" --languages yo,ha,ig,pcm
    python youtube_scraper.py --config ingestion_config.yaml
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import logging
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Generator
from dataclasses import dataclass, asdict, field
from enum import Enum
import re
import concurrent.futures
from functools import wraps

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'scraper.log')
    ]
)
logger = logging.getLogger("YouTubeScraper")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Nigerian/African content channels for training
CURATED_NIGERIAN_CHANNELS = {
    "podcasts": [
        # Nigerian Podcast Channels
        "UCxmcYMpkTrTVqpXX4e4x2dQ",  # Nigerian podcasts
        "UCxKjGkD3vZfX3vH9MFW1E4Q",  # African talk shows
    ],
    "language_learning": [
        # Yoruba teaching channels
        "UCyoruba_learning_channel",
        # Igbo teaching channels
        "UCigbo_learning_channel",
        # Hausa teaching channels
        "UChausa_learning_channel",
    ],
    "cultural_content": [
        # Nigerian cultural content
        "UCnigerian_culture_channel",
    ]
}

# Target Nigerian languages for Sisi Lola
NIGERIAN_LANGUAGES = {
    "yo": "Yoruba",
    "ha": "Hausa", 
    "ig": "Igbo",
    "pcm": "Nigerian Pidgin",
    "en": "English (Nigerian)"
}


class ContentQuality(Enum):
    """Video quality classification for training data."""
    HIGH = "high"      # Clear audio, single speaker, good transcript
    MEDIUM = "medium"  # Acceptable for training with some noise
    LOW = "low"        # May need enhancement before use
    UNSUITABLE = "unsuitable"  # Skip for training


@dataclass
class VideoMetadata:
    """Complete metadata for ingested video."""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_name: str
    upload_date: str
    duration: int  # seconds
    view_count: int
    like_count: int
    comment_count: int
    categories: List[str]
    tags: List[str]
    language: Optional[str]
    detected_languages: List[str]
    has_captions: bool
    caption_languages: List[str]
    thumbnail_url: Optional[str]
    video_url: str
    quality_rating: ContentQuality = ContentQuality.MEDIUM
    ingested_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_status: str = "pending"
    file_path: Optional[str] = None
    audio_path: Optional[str] = None
    transcript_path: Optional[str] = None


@dataclass
class TranscriptSegment:
    """Individual transcript segment with timing."""
    start: float
    end: float
    text: str
    language: Optional[str] = None
    confidence: float = 1.0


@dataclass
class ScraperConfig:
    """Configuration for the scraper."""
    output_dir: Path
    db_path: Path
    max_videos_per_channel: int = 100
    max_duration_seconds: int = 3600  # 1 hour max
    min_duration_seconds: int = 60    # 1 minute min
    download_video: bool = True
    download_audio_only: bool = False
    preferred_formats: List[str] = field(default_factory=lambda: ["mp4", "webm"])
    max_quality: str = "720p"
    extract_captions: bool = True
    caption_languages: List[str] = field(default_factory=lambda: ["en", "yo", "ha", "ig"])
    rate_limit_seconds: float = 2.0
    max_retries: int = 3
    concurrent_downloads: int = 2
    filter_keywords: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITING & RETRY DECORATOR
# ═══════════════════════════════════════════════════════════════════════════════

def rate_limited(delay: float = 1.0):
    """Decorator to rate limit function calls."""
    def decorator(func):
        last_call = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < delay:
                time.sleep(delay - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 5.0):
    """Decorator to retry function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

class IngestionDatabase:
    """SQLite database for tracking ingested videos."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                channel_id TEXT,
                channel_name TEXT,
                upload_date TEXT,
                duration INTEGER,
                view_count INTEGER,
                language TEXT,
                has_captions INTEGER,
                quality_rating TEXT,
                processing_status TEXT,
                file_path TEXT,
                audio_path TEXT,
                transcript_path TEXT,
                metadata_json TEXT,
                ingested_at TEXT,
                last_updated TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                language TEXT,
                transcript_text TEXT,
                segments_json TEXT,
                source TEXT,  -- 'youtube_captions', 'whisper', 'manual'
                created_at TEXT,
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT,
                completed_at TEXT,
                source_type TEXT,  -- 'channel', 'playlist', 'search'
                source_id TEXT,
                videos_found INTEGER,
                videos_ingested INTEGER,
                errors INTEGER,
                config_json TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def video_exists(self, video_id: str) -> bool:
        """Check if video is already in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM videos WHERE video_id = ?", (video_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_video(self, metadata: VideoMetadata):
        """Save video metadata to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO videos 
            (video_id, title, channel_id, channel_name, upload_date, duration,
             view_count, language, has_captions, quality_rating, processing_status,
             file_path, audio_path, transcript_path, metadata_json, ingested_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.video_id,
            metadata.title,
            metadata.channel_id,
            metadata.channel_name,
            metadata.upload_date,
            metadata.duration,
            metadata.view_count,
            metadata.language,
            1 if metadata.has_captions else 0,
            metadata.quality_rating.value,
            metadata.processing_status,
            metadata.file_path,
            metadata.audio_path,
            metadata.transcript_path,
            json.dumps(asdict(metadata)),
            metadata.ingested_at,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_transcript(self, video_id: str, language: str, text: str, 
                        segments: List[TranscriptSegment], source: str):
        """Save transcript to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        segments_json = json.dumps([asdict(s) for s in segments])
        
        cursor.execute("""
            INSERT INTO transcripts (video_id, language, transcript_text, segments_json, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (video_id, language, text, segments_json, source, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_pending_videos(self) -> List[str]:
        """Get list of videos pending processing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT video_id FROM videos WHERE processing_status = 'pending'")
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def update_status(self, video_id: str, status: str):
        """Update video processing status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE videos SET processing_status = ?, last_updated = ? WHERE video_id = ?",
            (status, datetime.now().isoformat(), video_id)
        )
        conn.commit()
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# YOUTUBE SCRAPER
# ═══════════════════════════════════════════════════════════════════════════════

class YouTubeScraper:
    """
    Advanced YouTube scraper for Nigerian/African content ingestion.
    
    Uses yt-dlp for robust downloading with:
    - Automatic caption extraction
    - Quality filtering
    - Rate limiting to avoid bans
    - Resume capability
    """
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.db = IngestionDatabase(config.db_path)
        
        # yt-dlp import check
        try:
            import yt_dlp
            self.yt_dlp = yt_dlp
        except ImportError:
            logger.error("yt-dlp not installed. Run: pip install yt-dlp")
            raise
    
    def _get_yt_opts(self, download: bool = True) -> Dict[str, Any]:
        """Get yt-dlp options based on config."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': not download,
            'ignoreerrors': True,
            'sleep_interval': self.config.rate_limit_seconds,
            'max_sleep_interval': self.config.rate_limit_seconds * 2,
        }
        
        if download:
            opts.update({
                'format': 'bestaudio/best' if self.config.download_audio_only else 'best[height<=720]',
                'outtmpl': str(self.config.output_dir / '%(id)s.%(ext)s'),
                'writesubtitles': self.config.extract_captions,
                'writeautomaticsub': self.config.extract_captions,
                'subtitleslangs': self.config.caption_languages,
                'subtitlesformat': 'json3',
            })
            
            if self.config.download_audio_only:
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }]
        
        return opts
    
    @rate_limited(delay=2.0)
    @retry_on_failure(max_retries=3)
    def get_video_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Extract video information without downloading."""
        opts = self._get_yt_opts(download=False)
        
        with self.yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                return info
            except Exception as e:
                logger.error(f"Failed to get video info: {e}")
                return None
    
    def _parse_metadata(self, info: Dict[str, Any]) -> VideoMetadata:
        """Parse yt-dlp info dict into VideoMetadata."""
        # Detect languages in title/description
        detected_langs = self._detect_languages(
            f"{info.get('title', '')} {info.get('description', '')}"
        )
        
        # Get caption languages
        caption_langs = []
        if info.get('subtitles'):
            caption_langs.extend(info['subtitles'].keys())
        if info.get('automatic_captions'):
            caption_langs.extend(info['automatic_captions'].keys())
        
        return VideoMetadata(
            video_id=info.get('id', ''),
            title=info.get('title', ''),
            description=info.get('description', '')[:1000],  # Truncate
            channel_id=info.get('channel_id', ''),
            channel_name=info.get('channel', ''),
            upload_date=info.get('upload_date', ''),
            duration=info.get('duration', 0),
            view_count=info.get('view_count', 0),
            like_count=info.get('like_count', 0),
            comment_count=info.get('comment_count', 0),
            categories=info.get('categories', []),
            tags=info.get('tags', [])[:20],  # Limit tags
            language=info.get('language'),
            detected_languages=detected_langs,
            has_captions=bool(caption_langs),
            caption_languages=list(set(caption_langs)),
            thumbnail_url=info.get('thumbnail'),
            video_url=info.get('webpage_url', f"https://youtube.com/watch?v={info.get('id')}")
        )
    
    def _detect_languages(self, text: str) -> List[str]:
        """Detect Nigerian languages in text using keywords."""
        detected = []
        text_lower = text.lower()
        
        # Yoruba indicators
        if any(w in text_lower for w in ['yoruba', 'ẹ̀dè', 'àwọn', 'ọ̀rọ̀', 'nàìjá']):
            detected.append('yo')
        
        # Hausa indicators  
        if any(w in text_lower for w in ['hausa', 'hausawa', 'yaren']):
            detected.append('ha')
        
        # Igbo indicators
        if any(w in text_lower for w in ['igbo', 'asụsụ', 'ndi']):
            detected.append('ig')
        
        # Pidgin indicators
        if any(w in text_lower for w in ['pidgin', 'naija', 'wetin', 'how far', 'wahala']):
            detected.append('pcm')
        
        return detected
    
    @rate_limited(delay=3.0)
    @retry_on_failure(max_retries=3)
    def download_video(self, video_url: str) -> Optional[Path]:
        """Download video and return path."""
        opts = self._get_yt_opts(download=True)
        
        with self.yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=True)
                if info:
                    video_id = info.get('id')
                    ext = 'wav' if self.config.download_audio_only else info.get('ext', 'mp4')
                    return self.config.output_dir / f"{video_id}.{ext}"
            except Exception as e:
                logger.error(f"Download failed: {e}")
        return None
    
    def extract_captions(self, video_id: str) -> List[TranscriptSegment]:
        """Extract captions/transcripts for a video."""
        segments = []
        caption_files = list(self.config.output_dir.glob(f"{video_id}*.json3"))
        
        for caption_file in caption_files:
            try:
                with open(caption_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Parse json3 format
                events = data.get('events', [])
                for event in events:
                    if 'segs' in event:
                        text = ''.join(seg.get('utf8', '') for seg in event['segs'])
                        start_ms = event.get('tStartMs', 0)
                        duration_ms = event.get('dDurationMs', 0)
                        
                        segments.append(TranscriptSegment(
                            start=start_ms / 1000,
                            end=(start_ms + duration_ms) / 1000,
                            text=text.strip()
                        ))
                        
            except Exception as e:
                logger.warning(f"Failed to parse caption file {caption_file}: {e}")
        
        return segments
    
    def scrape_channel(self, channel_id: str, max_videos: Optional[int] = None) -> List[VideoMetadata]:
        """Scrape all videos from a channel."""
        max_videos = max_videos or self.config.max_videos_per_channel
        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
        
        logger.info(f"Scraping channel: {channel_id}")
        
        opts = self._get_yt_opts(download=False)
        opts['playlistend'] = max_videos
        
        videos = []
        with self.yt_dlp.YoutubeDL(opts) as ydl:
            try:
                result = ydl.extract_info(channel_url, download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry and not self.db.video_exists(entry.get('id', '')):
                            # Check duration filter
                            duration = entry.get('duration', 0)
                            if self.config.min_duration_seconds <= duration <= self.config.max_duration_seconds:
                                metadata = self._parse_metadata(entry)
                                videos.append(metadata)
                                logger.info(f"  Found: {metadata.title[:50]}...")
                        
            except Exception as e:
                logger.error(f"Channel scrape failed: {e}")
        
        return videos
    
    def scrape_playlist(self, playlist_id: str) -> List[VideoMetadata]:
        """Scrape all videos from a playlist."""
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        logger.info(f"Scraping playlist: {playlist_id}")
        
        opts = self._get_yt_opts(download=False)
        
        videos = []
        with self.yt_dlp.YoutubeDL(opts) as ydl:
            try:
                result = ydl.extract_info(playlist_url, download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry and not self.db.video_exists(entry.get('id', '')):
                            metadata = self._parse_metadata(entry)
                            videos.append(metadata)
                            
            except Exception as e:
                logger.error(f"Playlist scrape failed: {e}")
        
        return videos
    
    def search_videos(self, query: str, max_results: int = 50) -> List[VideoMetadata]:
        """Search for videos matching query."""
        search_url = f"ytsearch{max_results}:{query}"
        
        logger.info(f"Searching: {query}")
        
        opts = self._get_yt_opts(download=False)
        
        videos = []
        with self.yt_dlp.YoutubeDL(opts) as ydl:
            try:
                result = ydl.extract_info(search_url, download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry:
                            metadata = self._parse_metadata(entry)
                            videos.append(metadata)
                            
            except Exception as e:
                logger.error(f"Search failed: {e}")
        
        return videos
    
    def ingest_video(self, metadata: VideoMetadata) -> bool:
        """Download and process a single video."""
        logger.info(f"Ingesting: {metadata.title[:50]}...")
        
        try:
            # Download
            file_path = self.download_video(metadata.video_url)
            
            if file_path and file_path.exists():
                metadata.file_path = str(file_path)
                metadata.processing_status = "downloaded"
                
                # Extract captions
                segments = self.extract_captions(metadata.video_id)
                if segments:
                    transcript_text = ' '.join(s.text for s in segments)
                    transcript_path = self.config.output_dir / f"{metadata.video_id}_transcript.txt"
                    
                    with open(transcript_path, 'w', encoding='utf-8') as f:
                        f.write(transcript_text)
                    
                    metadata.transcript_path = str(transcript_path)
                    
                    # Save transcript to DB
                    self.db.save_transcript(
                        metadata.video_id, 
                        metadata.language or 'unknown',
                        transcript_text,
                        segments,
                        'youtube_captions'
                    )
                
                # Rate quality
                metadata.quality_rating = self._rate_quality(metadata, segments)
                metadata.processing_status = "processed"
                
                # Save to DB
                self.db.save_video(metadata)
                
                logger.info(f"✓ Ingested: {metadata.video_id} ({metadata.quality_rating.value})")
                return True
                
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            metadata.processing_status = "failed"
            self.db.save_video(metadata)
        
        return False
    
    def _rate_quality(self, metadata: VideoMetadata, segments: List[TranscriptSegment]) -> ContentQuality:
        """Rate video quality for training data."""
        score = 0
        
        # Has captions: +30
        if segments:
            score += 30
            
            # Clean transcripts: +20
            total_text = ' '.join(s.text for s in segments)
            if len(total_text) > 500:
                score += 20
        
        # Nigerian language detected: +25
        if metadata.detected_languages:
            score += 25
        
        # Good duration (5-30 min): +15
        if 300 <= metadata.duration <= 1800:
            score += 15
        
        # High engagement: +10
        if metadata.view_count > 1000:
            score += 10
        
        if score >= 70:
            return ContentQuality.HIGH
        elif score >= 40:
            return ContentQuality.MEDIUM
        elif score >= 20:
            return ContentQuality.LOW
        else:
            return ContentQuality.UNSUITABLE
    
    def run_batch_ingestion(self, video_list: List[VideoMetadata]) -> Dict[str, int]:
        """Run batch ingestion on list of videos."""
        stats = {"total": len(video_list), "success": 0, "failed": 0, "skipped": 0}
        
        for metadata in video_list:
            if self.db.video_exists(metadata.video_id):
                stats["skipped"] += 1
                continue
            
            if self.ingest_video(metadata):
                stats["success"] += 1
            else:
                stats["failed"] += 1
            
            # Rate limit between videos
            time.sleep(self.config.rate_limit_seconds)
        
        return stats


# ═══════════════════════════════════════════════════════════════════════════════
# NIGERIAN CONTENT DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

class NigerianContentDiscovery:
    """
    Automated discovery of Nigerian/African content for training.
    
    Searches for:
    - Nigerian language teaching videos
    - African podcasts
    - Native speaker conversations
    - Cultural content
    """
    
    # Curated search queries for Nigerian content
    DISCOVERY_QUERIES = [
        # Language learning
        "Learn Yoruba language tutorial",
        "Hausa language lesson for beginners",
        "Igbo language basics",
        "Nigerian pidgin English tutorial",
        
        # Podcasts
        "Nigerian podcast interview",
        "African podcast conversation",
        "Lagos podcast discussion",
        "Naija talk show",
        
        # Cultural content
        "Yoruba storytelling traditional",
        "Hausa folktales stories",
        "Igbo cultural discussion",
        "Nigerian comedy sketch",
        
        # News/Discussion
        "Nigeria news discussion Yoruba",
        "African current affairs podcast",
        "Nollywood interview behind scenes",
    ]
    
    def __init__(self, scraper: YouTubeScraper):
        self.scraper = scraper
    
    def discover_content(self, max_per_query: int = 20) -> List[VideoMetadata]:
        """Discover Nigerian content using curated queries."""
        all_videos = []
        seen_ids = set()
        
        for query in self.DISCOVERY_QUERIES:
            logger.info(f"Discovering: {query}")
            videos = self.scraper.search_videos(query, max_results=max_per_query)
            
            for video in videos:
                if video.video_id not in seen_ids:
                    seen_ids.add(video.video_id)
                    all_videos.append(video)
            
            time.sleep(2)  # Rate limit between queries
        
        # Sort by detected Nigerian languages and view count
        all_videos.sort(
            key=lambda v: (len(v.detected_languages), v.view_count),
            reverse=True
        )
        
        return all_videos
    
    def discover_from_channels(self) -> List[VideoMetadata]:
        """Discover content from curated Nigerian channels."""
        all_videos = []
        
        for category, channels in CURATED_NIGERIAN_CHANNELS.items():
            logger.info(f"Scraping {category} channels...")
            for channel_id in channels:
                try:
                    videos = self.scraper.scrape_channel(channel_id)
                    all_videos.extend(videos)
                    logger.info(f"  Found {len(videos)} videos from {channel_id}")
                except Exception as e:
                    logger.error(f"  Failed to scrape {channel_id}: {e}")
        
        return all_videos


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola YouTube Content Ingestion")
    parser.add_argument("--output", type=Path, default=Path("data/raw_videos"),
                        help="Output directory for downloaded content")
    parser.add_argument("--db", type=Path, default=Path("data/ingestion.db"),
                        help="Database path for tracking")
    parser.add_argument("--channel", type=str, help="YouTube channel ID to scrape")
    parser.add_argument("--playlist", type=str, help="YouTube playlist ID to scrape")
    parser.add_argument("--search", type=str, help="Search query for videos")
    parser.add_argument("--discover", action="store_true", 
                        help="Run Nigerian content discovery")
    parser.add_argument("--max-videos", type=int, default=50,
                        help="Maximum videos to process")
    parser.add_argument("--audio-only", action="store_true",
                        help="Download audio only (WAV)")
    
    args = parser.parse_args()
    
    # Create config
    config = ScraperConfig(
        output_dir=args.output,
        db_path=args.db,
        max_videos_per_channel=args.max_videos,
        download_audio_only=args.audio_only
    )
    
    # Initialize scraper
    scraper = YouTubeScraper(config)
    
    videos = []
    
    if args.discover:
        discovery = NigerianContentDiscovery(scraper)
        videos = discovery.discover_content()
        logger.info(f"Discovered {len(videos)} videos")
    
    elif args.channel:
        videos = scraper.scrape_channel(args.channel)
    
    elif args.playlist:
        videos = scraper.scrape_playlist(args.playlist)
    
    elif args.search:
        videos = scraper.search_videos(args.search, max_results=args.max_videos)
    
    if videos:
        logger.info(f"Processing {len(videos)} videos...")
        stats = scraper.run_batch_ingestion(videos[:args.max_videos])
        
        print("\n" + "═" * 60)
        print("INGESTION COMPLETE")
        print("═" * 60)
        print(f"  Total:   {stats['total']}")
        print(f"  Success: {stats['success']}")
        print(f"  Failed:  {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        print("═" * 60)


if __name__ == "__main__":
    main()
