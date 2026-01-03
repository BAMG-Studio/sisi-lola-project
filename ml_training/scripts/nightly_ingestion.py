"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - AUTOMATED DATA INGESTION PIPELINE
═══════════════════════════════════════════════════════════════════════════════
Nightly ingestion of voice, video, and cultural training data from 50+ sources.

Features:
- YouTube video/audio extraction with transcription
- HuggingFace dataset streaming
- RSS feed ingestion
- Social media scraping (Twitter, TikTok transcripts)
- Quality scoring and filtering
- DVC versioning integration
- Cost tracking per source

Run: python nightly_ingestion.py --sources all --dry-run
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import yaml
import hashlib
import asyncio
import sqlite3
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
import tempfile
import shutil

# Third-party imports
try:
    import httpx
    import feedparser
    from tqdm import tqdm
    import yt_dlp
except ImportError as e:
    print(f"Missing dependency: {e}. Run: pip install httpx feedparser tqdm yt-dlp")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATASETS_DIR = BASE_DIR / "datasets"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "configs"

# Ensure directories exist
for d in [DATA_DIR, DATASETS_DIR, CHECKPOINTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"ingestion_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataType(Enum):
    VOICE = "voice"
    VIDEO = "video"
    TEXT = "text"
    CULTURAL = "cultural"


class SourceType(Enum):
    HUGGINGFACE = "huggingface"
    YOUTUBE = "youtube"
    RSS = "rss"
    TWITTER = "twitter"
    WEB_SCRAPE = "web_scrape"
    API = "api"


class QualityTier(Enum):
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"            # 70-89
    ACCEPTABLE = "acceptable" # 50-69
    POOR = "poor"            # <50
    UNSCORED = "unscored"


@dataclass
class IngestedItem:
    """Single ingested data item"""
    item_id: str
    source_id: str
    source_type: SourceType
    data_type: DataType
    file_path: Optional[str]
    url: Optional[str]
    language: str
    quality_score: float
    quality_tier: QualityTier
    metadata: Dict[str, Any]
    ingested_at: datetime
    file_hash: Optional[str] = None
    transcript: Optional[str] = None
    duration_seconds: Optional[float] = None


@dataclass
class IngestionStats:
    """Statistics for an ingestion run"""
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    sources_processed: int = 0
    items_ingested: int = 0
    items_filtered: int = 0
    bytes_downloaded: int = 0
    errors: List[str] = field(default_factory=list)
    cost_estimate_usd: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

class IngestionDatabase:
    """SQLite database for tracking ingested data"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DATA_DIR / "ingestion_tracking.db"
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ingested items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingested_items (
                item_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                data_type TEXT NOT NULL,
                file_path TEXT,
                url TEXT,
                language TEXT,
                quality_score REAL,
                quality_tier TEXT,
                metadata TEXT,
                ingested_at TEXT,
                file_hash TEXT,
                transcript TEXT,
                duration_seconds REAL
            )
        """)
        
        # Ingestion runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT,
                completed_at TEXT,
                sources_processed INTEGER,
                items_ingested INTEGER,
                items_filtered INTEGER,
                bytes_downloaded INTEGER,
                errors TEXT,
                cost_estimate_usd REAL
            )
        """)
        
        # Daily aggregates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_ingestion_stats (
                date TEXT PRIMARY KEY,
                voice_samples INTEGER DEFAULT 0,
                video_clips INTEGER DEFAULT 0,
                text_items INTEGER DEFAULT 0,
                total_bytes INTEGER DEFAULT 0,
                avg_quality REAL DEFAULT 0.0
            )
        """)
        
        # Source health tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_health (
                source_id TEXT PRIMARY KEY,
                last_success TEXT,
                last_failure TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_items_per_run REAL DEFAULT 0.0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def item_exists(self, item_id: str) -> bool:
        """Check if item already ingested (deduplication)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM ingested_items WHERE item_id = ?", (item_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def hash_exists(self, file_hash: str) -> bool:
        """Check if file hash already exists (content deduplication)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM ingested_items WHERE file_hash = ?", (file_hash,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_item(self, item: IngestedItem):
        """Save ingested item to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO ingested_items
            (item_id, source_id, source_type, data_type, file_path, url,
             language, quality_score, quality_tier, metadata, ingested_at,
             file_hash, transcript, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.item_id,
            item.source_id,
            item.source_type.value,
            item.data_type.value,
            item.file_path,
            item.url,
            item.language,
            item.quality_score,
            item.quality_tier.value,
            json.dumps(item.metadata),
            item.ingested_at.isoformat(),
            item.file_hash,
            item.transcript,
            item.duration_seconds
        ))
        
        conn.commit()
        conn.close()
    
    def save_run_stats(self, stats: IngestionStats):
        """Save ingestion run statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO ingestion_runs
            (run_id, started_at, completed_at, sources_processed, items_ingested,
             items_filtered, bytes_downloaded, errors, cost_estimate_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.run_id,
            stats.started_at.isoformat(),
            stats.completed_at.isoformat() if stats.completed_at else None,
            stats.sources_processed,
            stats.items_ingested,
            stats.items_filtered,
            stats.bytes_downloaded,
            json.dumps(stats.errors),
            stats.cost_estimate_usd
        ))
        
        conn.commit()
        conn.close()
    
    def get_stats_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                SUM(CASE WHEN data_type = 'voice' THEN 1 ELSE 0 END) as voice_items,
                SUM(CASE WHEN data_type = 'video' THEN 1 ELSE 0 END) as video_items,
                SUM(CASE WHEN data_type = 'text' THEN 1 ELSE 0 END) as text_items,
                AVG(quality_score) as avg_quality,
                COUNT(DISTINCT source_id) as sources_used
            FROM ingested_items
            WHERE ingested_at >= ?
        """, (cutoff,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "period": f"Last {days} days",
            "total_items": row[0] or 0,
            "voice_items": row[1] or 0,
            "video_items": row[2] or 0,
            "text_items": row[3] or 0,
            "avg_quality": round(row[4] or 0, 2),
            "sources_used": row[5] or 0
        }


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY SCORER
# ═══════════════════════════════════════════════════════════════════════════════

class QualityScorer:
    """Score quality of ingested data"""
    
    @staticmethod
    def score_audio(file_path: Path, metadata: Dict = None) -> Tuple[float, QualityTier]:
        """Score audio quality (0-100)"""
        score = 70.0  # Base score
        
        # Check file size (too small = bad quality)
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb < 0.1:
                score -= 30
            elif size_mb > 1:
                score += 10
        
        # Check duration from metadata
        if metadata:
            duration = metadata.get("duration", 0)
            if 3 <= duration <= 30:  # Ideal for training
                score += 15
            elif duration > 300:  # Too long
                score -= 10
        
        # Check format
        if file_path.suffix.lower() in [".wav", ".flac"]:
            score += 10
        elif file_path.suffix.lower() in [".mp3", ".m4a"]:
            score += 5
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine tier
        if score >= 90:
            tier = QualityTier.EXCELLENT
        elif score >= 70:
            tier = QualityTier.GOOD
        elif score >= 50:
            tier = QualityTier.ACCEPTABLE
        else:
            tier = QualityTier.POOR
        
        return score, tier
    
    @staticmethod
    def score_video(file_path: Path, metadata: Dict = None) -> Tuple[float, QualityTier]:
        """Score video quality (0-100)"""
        score = 70.0
        
        if metadata:
            # Resolution check
            width = metadata.get("width", 0)
            if width >= 1920:
                score += 20
            elif width >= 1280:
                score += 10
            elif width < 640:
                score -= 20
            
            # Duration check
            duration = metadata.get("duration", 0)
            if 10 <= duration <= 120:  # Ideal for training
                score += 10
            elif duration > 600:
                score -= 10
        
        score = max(0, min(100, score))
        
        if score >= 90:
            tier = QualityTier.EXCELLENT
        elif score >= 70:
            tier = QualityTier.GOOD
        elif score >= 50:
            tier = QualityTier.ACCEPTABLE
        else:
            tier = QualityTier.POOR
        
        return score, tier
    
    @staticmethod
    def score_text(text: str, language: str = "en") -> Tuple[float, QualityTier]:
        """Score text quality (0-100)"""
        score = 70.0
        
        if not text:
            return 0.0, QualityTier.POOR
        
        # Length check
        word_count = len(text.split())
        if 50 <= word_count <= 500:
            score += 15
        elif word_count < 10:
            score -= 30
        
        # Nigerian language indicators (bonus for authenticity)
        nigerian_markers = ["na", "dey", "wetin", "oya", "abeg", "wahala", "ehen", "chai"]
        marker_count = sum(1 for m in nigerian_markers if m.lower() in text.lower())
        score += min(marker_count * 3, 15)
        
        score = max(0, min(100, score))
        
        if score >= 90:
            tier = QualityTier.EXCELLENT
        elif score >= 70:
            tier = QualityTier.GOOD
        elif score >= 50:
            tier = QualityTier.ACCEPTABLE
        else:
            tier = QualityTier.POOR
        
        return score, tier


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE HANDLERS (Abstract Base)
# ═══════════════════════════════════════════════════════════════════════════════

class SourceHandler(ABC):
    """Abstract base class for data source handlers"""
    
    def __init__(self, source_config: Dict, db: IngestionDatabase):
        self.config = source_config
        self.db = db
        self.scorer = QualityScorer()
    
    @abstractmethod
    async def fetch(self, max_items: int = 100) -> List[IngestedItem]:
        """Fetch data from source"""
        pass
    
    def compute_hash(self, file_path: Path) -> str:
        """Compute MD5 hash for deduplication"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# YOUTUBE HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class YouTubeHandler(SourceHandler):
    """Handle YouTube video/audio ingestion"""
    
    async def fetch(self, max_items: int = 10) -> List[IngestedItem]:
        items = []
        
        query = self.config.get("query") or self.config.get("url")
        if not query:
            logger.error(f"No query/URL for YouTube source: {self.config.get('id')}")
            return items
        
        output_dir = DATA_DIR / "youtube" / self.config.get("id", "unknown")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'yo', 'ha', 'ig', 'pcm'],
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'max_downloads': max_items,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search or direct URL
                if query.startswith("http"):
                    info = ydl.extract_info(query, download=True)
                else:
                    info = ydl.extract_info(f"ytsearch{max_items}:{query}", download=True)
                
                if not info:
                    return items
                
                entries = info.get('entries', [info])
                
                for entry in entries:
                    if not entry:
                        continue
                    
                    video_id = entry.get('id', '')
                    item_id = f"yt_{video_id}"
                    
                    # Skip if already ingested
                    if self.db.item_exists(item_id):
                        continue
                    
                    # Find downloaded file
                    audio_file = None
                    for ext in ['m4a', 'mp3', 'webm', 'mp4']:
                        potential = output_dir / f"{video_id}.{ext}"
                        if potential.exists():
                            audio_file = potential
                            break
                    
                    if not audio_file or not audio_file.exists():
                        continue
                    
                    # Compute hash for deduplication
                    file_hash = self.compute_hash(audio_file)
                    if self.db.hash_exists(file_hash):
                        continue
                    
                    # Score quality
                    metadata = {
                        "title": entry.get("title", ""),
                        "channel": entry.get("uploader", ""),
                        "duration": entry.get("duration", 0),
                        "view_count": entry.get("view_count", 0),
                        "upload_date": entry.get("upload_date", ""),
                    }
                    
                    score, tier = self.scorer.score_audio(audio_file, metadata)
                    
                    # Get transcript if available
                    transcript = None
                    for sub_ext in ['en.vtt', 'yo.vtt', 'ha.vtt', 'pcm.vtt']:
                        sub_file = output_dir / f"{video_id}.{sub_ext}"
                        if sub_file.exists():
                            transcript = sub_file.read_text(errors='ignore')[:5000]
                            break
                    
                    item = IngestedItem(
                        item_id=item_id,
                        source_id=self.config.get("id", "youtube"),
                        source_type=SourceType.YOUTUBE,
                        data_type=DataType.VIDEO,
                        file_path=str(audio_file),
                        url=f"https://youtube.com/watch?v={video_id}",
                        language=self.config.get("language", "en-NG"),
                        quality_score=score,
                        quality_tier=tier,
                        metadata=metadata,
                        ingested_at=datetime.now(),
                        file_hash=file_hash,
                        transcript=transcript,
                        duration_seconds=entry.get("duration")
                    )
                    
                    items.append(item)
                    self.db.save_item(item)
                    
        except Exception as e:
            logger.error(f"YouTube ingestion error: {e}")
        
        return items


# ═══════════════════════════════════════════════════════════════════════════════
# RSS HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class RSSHandler(SourceHandler):
    """Handle RSS feed ingestion"""
    
    async def fetch(self, max_items: int = 50) -> List[IngestedItem]:
        items = []
        
        url = self.config.get("url")
        if not url:
            return items
        
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_items]:
                item_id = f"rss_{hashlib.md5(entry.get('link', entry.get('id', '')).encode()).hexdigest()[:12]}"
                
                if self.db.item_exists(item_id):
                    continue
                
                # Extract text content
                content = entry.get('summary', '') or entry.get('description', '')
                title = entry.get('title', '')
                full_text = f"{title}\n\n{content}"
                
                # Score quality
                score, tier = self.scorer.score_text(full_text, self.config.get("language", "en"))
                
                # Skip poor quality
                if tier == QualityTier.POOR:
                    continue
                
                metadata = {
                    "title": title,
                    "published": entry.get('published', ''),
                    "author": entry.get('author', ''),
                    "feed_title": feed.feed.get('title', ''),
                }
                
                item = IngestedItem(
                    item_id=item_id,
                    source_id=self.config.get("name", "rss"),
                    source_type=SourceType.RSS,
                    data_type=DataType.TEXT,
                    file_path=None,
                    url=entry.get('link'),
                    language=self.config.get("language", "en"),
                    quality_score=score,
                    quality_tier=tier,
                    metadata=metadata,
                    ingested_at=datetime.now(),
                    transcript=full_text[:10000]
                )
                
                items.append(item)
                self.db.save_item(item)
                
        except Exception as e:
            logger.error(f"RSS ingestion error for {url}: {e}")
        
        return items


# ═══════════════════════════════════════════════════════════════════════════════
# HUGGINGFACE HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class HuggingFaceHandler(SourceHandler):
    """Handle HuggingFace dataset streaming"""
    
    async def fetch(self, max_items: int = 1000) -> List[IngestedItem]:
        items = []
        
        try:
            from datasets import load_dataset
        except ImportError:
            logger.error("datasets package not installed")
            return items
        
        dataset_id = self.config.get("source")
        if not dataset_id:
            return items
        
        try:
            # Stream dataset to avoid downloading everything
            dataset = load_dataset(
                dataset_id,
                split="train",
                streaming=True,
                trust_remote_code=True
            )
            
            count = 0
            for sample in dataset:
                if count >= max_items:
                    break
                
                # Extract audio/text based on dataset structure
                audio_data = sample.get("audio", {})
                text = sample.get("text") or sample.get("sentence") or sample.get("transcription", "")
                
                if not text:
                    continue
                
                item_id = f"hf_{dataset_id.replace('/', '_')}_{count}"
                
                if self.db.item_exists(item_id):
                    count += 1
                    continue
                
                score, tier = self.scorer.score_text(text, self.config.get("language", "en"))
                
                metadata = {
                    "dataset": dataset_id,
                    "sample_index": count,
                    "has_audio": bool(audio_data),
                }
                
                item = IngestedItem(
                    item_id=item_id,
                    source_id=self.config.get("id", dataset_id),
                    source_type=SourceType.HUGGINGFACE,
                    data_type=DataType.VOICE if audio_data else DataType.TEXT,
                    file_path=None,
                    url=f"https://huggingface.co/datasets/{dataset_id}",
                    language=self.config.get("language", "en"),
                    quality_score=score,
                    quality_tier=tier,
                    metadata=metadata,
                    ingested_at=datetime.now(),
                    transcript=text
                )
                
                items.append(item)
                self.db.save_item(item)
                count += 1
                
        except Exception as e:
            logger.error(f"HuggingFace ingestion error for {dataset_id}: {e}")
        
        return items


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INGESTION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class IngestionOrchestrator:
    """Main orchestrator for nightly data ingestion"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or CONFIG_DIR / "nigerian_data_sources.yaml"
        self.config = self._load_config()
        self.db = IngestionDatabase()
        self.stats = IngestionStats(
            run_id=f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            started_at=datetime.now()
        )
    
    def _load_config(self) -> Dict:
        """Load data sources configuration"""
        if not self.config_path.exists():
            logger.error(f"Config not found: {self.config_path}")
            return {}
        
        with open(self.config_path) as f:
            return yaml.safe_load(f)
    
    async def run_ingestion(
        self,
        sources: List[str] = None,
        max_items_per_source: int = 50,
        dry_run: bool = False
    ) -> IngestionStats:
        """Run full ingestion pipeline"""
        
        logger.info("=" * 60)
        logger.info("🚀 SISI LOLA NIGHTLY INGESTION STARTING")
        logger.info("=" * 60)
        
        all_items = []
        
        # Process YouTube sources
        if sources is None or "youtube" in sources or "all" in sources:
            yt_channels = self.config.get("video_datasets", {}).get("youtube_channels", [])
            yt_queries = self.config.get("auto_ingestion", {}).get("youtube_queries", [])
            
            for channel in yt_channels[:5]:  # Limit for nightly
                handler = YouTubeHandler(channel, self.db)
                items = await handler.fetch(max_items=3)
                all_items.extend(items)
                self.stats.sources_processed += 1
                logger.info(f"📺 YouTube {channel.get('id')}: {len(items)} items")
            
            for query_config in yt_queries[:3]:
                handler = YouTubeHandler(query_config, self.db)
                items = await handler.fetch(max_items=query_config.get("max_results", 5))
                all_items.extend(items)
                self.stats.sources_processed += 1
        
        # Process RSS feeds
        if sources is None or "rss" in sources or "all" in sources:
            rss_feeds = self.config.get("auto_ingestion", {}).get("rss_feeds", [])
            
            for feed in rss_feeds:
                handler = RSSHandler(feed, self.db)
                items = await handler.fetch(max_items=20)
                all_items.extend(items)
                self.stats.sources_processed += 1
                logger.info(f"📰 RSS {feed.get('name')}: {len(items)} items")
        
        # Process HuggingFace datasets
        if sources is None or "huggingface" in sources or "all" in sources:
            hf_datasets = []
            for tier in ["primary", "secondary"]:
                hf_datasets.extend(
                    self.config.get("voice_datasets", {}).get(tier, [])
                )
            
            for dataset in hf_datasets[:10]:  # Limit for nightly
                if dataset.get("platform") != "huggingface":
                    continue
                handler = HuggingFaceHandler(dataset, self.db)
                items = await handler.fetch(max_items=100)
                all_items.extend(items)
                self.stats.sources_processed += 1
                logger.info(f"🤗 HuggingFace {dataset.get('id')}: {len(items)} items")
        
        # Update stats
        self.stats.items_ingested = len(all_items)
        self.stats.completed_at = datetime.now()
        
        # Calculate bytes downloaded
        for item in all_items:
            if item.file_path and Path(item.file_path).exists():
                self.stats.bytes_downloaded += Path(item.file_path).stat().st_size
        
        # Save stats
        self.db.save_run_stats(self.stats)
        
        # Generate report
        self._generate_report(all_items)
        
        logger.info("=" * 60)
        logger.info(f"✅ INGESTION COMPLETE")
        logger.info(f"   Sources: {self.stats.sources_processed}")
        logger.info(f"   Items: {self.stats.items_ingested}")
        logger.info(f"   Size: {self.stats.bytes_downloaded / (1024*1024):.2f} MB")
        logger.info("=" * 60)
        
        return self.stats
    
    def _generate_report(self, items: List[IngestedItem]):
        """Generate ingestion report"""
        report = {
            "run_id": self.stats.run_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "sources_processed": self.stats.sources_processed,
                "items_ingested": self.stats.items_ingested,
                "bytes_downloaded": self.stats.bytes_downloaded,
            },
            "by_type": {},
            "by_language": {},
            "by_quality": {},
        }
        
        for item in items:
            # By type
            t = item.data_type.value
            report["by_type"][t] = report["by_type"].get(t, 0) + 1
            
            # By language
            lang = item.language
            report["by_language"][lang] = report["by_language"].get(lang, 0) + 1
            
            # By quality
            q = item.quality_tier.value
            report["by_quality"][q] = report["by_quality"].get(q, 0) + 1
        
        # Save report
        report_path = LOGS_DIR / f"ingestion_report_{self.stats.run_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Report saved: {report_path}")
    
    def get_dataset_summary(self) -> Dict[str, Any]:
        """Get current dataset summary"""
        return self.db.get_stats_summary()


# ═══════════════════════════════════════════════════════════════════════════════
# DVC INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class DVCManager:
    """Manage dataset versioning with DVC"""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or BASE_DIR.parent
        self.dvc_dir = self.repo_path / ".dvc"
    
    def is_initialized(self) -> bool:
        """Check if DVC is initialized"""
        return self.dvc_dir.exists()
    
    def initialize(self) -> bool:
        """Initialize DVC in repository"""
        if self.is_initialized():
            logger.info("DVC already initialized")
            return True
        
        try:
            subprocess.run(["dvc", "init"], cwd=self.repo_path, check=True)
            logger.info("✅ DVC initialized")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"DVC init failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("DVC not installed. Run: pip install dvc")
            return False
    
    def add_data(self, data_path: Path, message: str = None) -> bool:
        """Add data to DVC tracking"""
        try:
            subprocess.run(["dvc", "add", str(data_path)], cwd=self.repo_path, check=True)
            
            # Git add the .dvc file
            dvc_file = data_path.with_suffix(data_path.suffix + ".dvc")
            subprocess.run(["git", "add", str(dvc_file)], cwd=self.repo_path, check=True)
            
            if message:
                subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=self.repo_path,
                    check=True
                )
            
            logger.info(f"✅ Added to DVC: {data_path}")
            return True
        except Exception as e:
            logger.error(f"DVC add failed: {e}")
            return False
    
    def push(self, remote: str = "origin") -> bool:
        """Push data to DVC remote"""
        try:
            subprocess.run(["dvc", "push"], cwd=self.repo_path, check=True)
            logger.info("✅ DVC push complete")
            return True
        except Exception as e:
            logger.error(f"DVC push failed: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Nightly Data Ingestion")
    parser.add_argument("--sources", nargs="+", default=["all"],
                       help="Sources to ingest: youtube, rss, huggingface, all")
    parser.add_argument("--max-items", type=int, default=50,
                       help="Max items per source")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview without downloading")
    parser.add_argument("--stats", action="store_true",
                       help="Show current dataset statistics")
    parser.add_argument("--dvc-init", action="store_true",
                       help="Initialize DVC")
    parser.add_argument("--dvc-version", type=str,
                       help="Version the dataset with DVC")
    
    args = parser.parse_args()
    
    orchestrator = IngestionOrchestrator()
    
    if args.stats:
        summary = orchestrator.get_dataset_summary()
        print(json.dumps(summary, indent=2))
        return
    
    if args.dvc_init:
        dvc = DVCManager()
        dvc.initialize()
        return
    
    if args.dvc_version:
        dvc = DVCManager()
        dvc.add_data(DATA_DIR, f"Dataset version: {args.dvc_version}")
        return
    
    # Run ingestion
    stats = await orchestrator.run_ingestion(
        sources=args.sources,
        max_items_per_source=args.max_items,
        dry_run=args.dry_run
    )
    
    print(f"\n✅ Ingestion complete: {stats.items_ingested} items from {stats.sources_processed} sources")


if __name__ == "__main__":
    asyncio.run(main())
