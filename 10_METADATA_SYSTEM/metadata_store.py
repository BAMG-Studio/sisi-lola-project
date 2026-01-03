#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SISI LOLA METADATA MANAGEMENT SYSTEM
═══════════════════════════════════════════════════════════════════════════════
                 Centralized Asset Tracking & Data Catalog
                         AWS Glue / Apache Atlas Style
═══════════════════════════════════════════════════════════════════════════════

This module provides comprehensive metadata management for the Sisi Lola system,
tracking all assets across the pipeline including:

- Ingested content (videos, audio, transcripts)
- Training data and samples
- Generated content (images, videos, audio)
- Model checkpoints and versions
- Feedback data and quality metrics

Features:
- SQLite-based metadata store
- Asset lineage tracking
- Quality metrics history
- Nigerian content classification
- Full-text search across assets
"""

import os
import json
import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Types of assets in the system."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TRANSCRIPT = "transcript"
    MODEL = "model"
    CHECKPOINT = "checkpoint"
    LORA = "lora"
    DATASET = "dataset"
    FEEDBACK = "feedback"
    CONFIG = "config"


class AssetStatus(Enum):
    """Asset lifecycle status."""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ARCHIVED = "archived"
    FAILED = "failed"
    DELETED = "deleted"


class NigerianLanguage(Enum):
    """Supported Nigerian languages/dialects."""
    ENGLISH = "english"
    PIDGIN = "pidgin"
    YORUBA = "yoruba"
    HAUSA = "hausa"
    IGBO = "igbo"
    MIXED = "mixed"


@dataclass
class AssetMetadata:
    """
    Core metadata for any asset in the system.
    """
    # Identity
    asset_id: str
    asset_type: AssetType
    name: str
    
    # Location
    storage_path: str
    storage_type: str = "local"  # local, modal_volume, s3, replicate
    
    # Status
    status: AssetStatus = AssetStatus.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Size and format
    size_bytes: int = 0
    format: str = ""
    duration_seconds: float = 0.0
    
    # Nigerian content classification
    language: NigerianLanguage = NigerianLanguage.ENGLISH
    is_nigerian: bool = False
    nigerian_score: float = 0.0
    
    # Quality metrics
    quality_score: float = 0.0
    
    # Lineage
    source_id: Optional[str] = None
    parent_ids: List[str] = field(default_factory=list)
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Checksums
    content_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['asset_type'] = self.asset_type.value
        data['status'] = self.status.value
        data['language'] = self.language.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['parent_ids'] = json.dumps(self.parent_ids)
        data['tags'] = json.dumps(self.tags)
        data['properties'] = json.dumps(self.properties)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetMetadata':
        """Create from dictionary."""
        data['asset_type'] = AssetType(data['asset_type'])
        data['status'] = AssetStatus(data['status'])
        data['language'] = NigerianLanguage(data['language'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['parent_ids'] = json.loads(data['parent_ids']) if isinstance(data['parent_ids'], str) else data['parent_ids']
        data['tags'] = json.loads(data['tags']) if isinstance(data['tags'], str) else data['tags']
        data['properties'] = json.loads(data['properties']) if isinstance(data['properties'], str) else data['properties']
        return cls(**data)


class MetadataStore:
    """
    SQLite-based metadata storage with full-text search.
    """
    
    def __init__(self, db_path: str = "metadata_store.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Main assets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    storage_path TEXT,
                    storage_type TEXT DEFAULT 'local',
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    size_bytes INTEGER DEFAULT 0,
                    format TEXT,
                    duration_seconds REAL DEFAULT 0,
                    language TEXT DEFAULT 'english',
                    is_nigerian INTEGER DEFAULT 0,
                    nigerian_score REAL DEFAULT 0,
                    quality_score REAL DEFAULT 0,
                    source_id TEXT,
                    parent_ids TEXT DEFAULT '[]',
                    tags TEXT DEFAULT '[]',
                    properties TEXT DEFAULT '{}',
                    content_hash TEXT,
                    FOREIGN KEY (source_id) REFERENCES assets(asset_id)
                )
            """)
            
            # Asset lineage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    relationship_type TEXT DEFAULT 'derived',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (parent_id) REFERENCES assets(asset_id),
                    FOREIGN KEY (child_id) REFERENCES assets(asset_id),
                    UNIQUE(parent_id, child_id)
                )
            """)
            
            # Quality history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    metrics TEXT DEFAULT '{}',
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
                )
            """)
            
            # Nigerian content analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nigerian_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT NOT NULL,
                    detected_language TEXT,
                    confidence REAL,
                    dialect_features TEXT DEFAULT '[]',
                    cultural_markers TEXT DEFAULT '[]',
                    analyzed_at TEXT NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
                )
            """)
            
            # Full-text search virtual table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS assets_fts USING fts5(
                    asset_id,
                    name,
                    tags,
                    properties,
                    content=assets,
                    content_rowid=rowid
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_type ON assets(asset_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON assets(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_language ON assets(language)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_nigerian ON assets(is_nigerian)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON assets(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_score ON assets(quality_score)")
            
            logger.info(f"Metadata store initialized at {self.db_path}")
    
    def register_asset(self, metadata: AssetMetadata) -> str:
        """Register a new asset in the metadata store."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            data = metadata.to_dict()
            
            cursor.execute("""
                INSERT INTO assets (
                    asset_id, asset_type, name, storage_path, storage_type,
                    status, created_at, updated_at, size_bytes, format,
                    duration_seconds, language, is_nigerian, nigerian_score,
                    quality_score, source_id, parent_ids, tags, properties, content_hash
                ) VALUES (
                    :asset_id, :asset_type, :name, :storage_path, :storage_type,
                    :status, :created_at, :updated_at, :size_bytes, :format,
                    :duration_seconds, :language, :is_nigerian, :nigerian_score,
                    :quality_score, :source_id, :parent_ids, :tags, :properties, :content_hash
                )
            """, data)
            
            # Update FTS
            cursor.execute("""
                INSERT INTO assets_fts(asset_id, name, tags, properties)
                VALUES (?, ?, ?, ?)
            """, (metadata.asset_id, metadata.name, json.dumps(metadata.tags), json.dumps(metadata.properties)))
            
            # Record lineage
            for parent_id in metadata.parent_ids:
                cursor.execute("""
                    INSERT OR IGNORE INTO asset_lineage (parent_id, child_id, created_at)
                    VALUES (?, ?, ?)
                """, (parent_id, metadata.asset_id, datetime.now().isoformat()))
            
            logger.info(f"Registered asset: {metadata.asset_id} ({metadata.asset_type.value})")
            return metadata.asset_id
    
    def get_asset(self, asset_id: str) -> Optional[AssetMetadata]:
        """Retrieve asset metadata by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,))
            row = cursor.fetchone()
            
            if row:
                return AssetMetadata.from_dict(dict(row))
            return None
    
    def update_asset(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """Update asset metadata."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            updates['updated_at'] = datetime.now().isoformat()
            
            # Handle enum conversions
            if 'status' in updates and isinstance(updates['status'], AssetStatus):
                updates['status'] = updates['status'].value
            if 'language' in updates and isinstance(updates['language'], NigerianLanguage):
                updates['language'] = updates['language'].value
            if 'asset_type' in updates and isinstance(updates['asset_type'], AssetType):
                updates['asset_type'] = updates['asset_type'].value
            
            # Handle list/dict conversions
            if 'tags' in updates:
                updates['tags'] = json.dumps(updates['tags'])
            if 'properties' in updates:
                updates['properties'] = json.dumps(updates['properties'])
            if 'parent_ids' in updates:
                updates['parent_ids'] = json.dumps(updates['parent_ids'])
            
            set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
            updates['asset_id'] = asset_id
            
            cursor.execute(f"UPDATE assets SET {set_clause} WHERE asset_id = :asset_id", updates)
            
            return cursor.rowcount > 0
    
    def delete_asset(self, asset_id: str, soft_delete: bool = True) -> bool:
        """Delete or mark asset as deleted."""
        if soft_delete:
            return self.update_asset(asset_id, {'status': AssetStatus.DELETED})
        else:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM assets WHERE asset_id = ?", (asset_id,))
                cursor.execute("DELETE FROM assets_fts WHERE asset_id = ?", (asset_id,))
                return cursor.rowcount > 0
    
    def search_assets(
        self,
        query: str = None,
        asset_type: AssetType = None,
        status: AssetStatus = None,
        language: NigerianLanguage = None,
        is_nigerian: bool = None,
        min_quality: float = None,
        tags: List[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AssetMetadata]:
        """Search assets with various filters."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if query:
                # Use FTS for text search
                conditions.append("asset_id IN (SELECT asset_id FROM assets_fts WHERE assets_fts MATCH ?)")
                params.append(query)
            
            if asset_type:
                conditions.append("asset_type = ?")
                params.append(asset_type.value)
            
            if status:
                conditions.append("status = ?")
                params.append(status.value)
            
            if language:
                conditions.append("language = ?")
                params.append(language.value)
            
            if is_nigerian is not None:
                conditions.append("is_nigerian = ?")
                params.append(1 if is_nigerian else 0)
            
            if min_quality is not None:
                conditions.append("quality_score >= ?")
                params.append(min_quality)
            
            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f"""
                SELECT * FROM assets
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])
            
            return [AssetMetadata.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_nigerian_assets(
        self,
        language: NigerianLanguage = None,
        min_score: float = 0.5,
        limit: int = 100
    ) -> List[AssetMetadata]:
        """Get Nigerian content assets."""
        return self.search_assets(
            is_nigerian=True,
            language=language,
            min_quality=min_score,
            limit=limit
        )
    
    def get_asset_lineage(self, asset_id: str) -> Dict[str, List[str]]:
        """Get asset lineage (parents and children)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get parents
            cursor.execute("""
                SELECT parent_id FROM asset_lineage WHERE child_id = ?
            """, (asset_id,))
            parents = [row['parent_id'] for row in cursor.fetchall()]
            
            # Get children
            cursor.execute("""
                SELECT child_id FROM asset_lineage WHERE parent_id = ?
            """, (asset_id,))
            children = [row['child_id'] for row in cursor.fetchall()]
            
            return {
                'parents': parents,
                'children': children
            }
    
    def record_quality_metric(
        self,
        asset_id: str,
        quality_score: float,
        metrics: Dict[str, Any] = None
    ):
        """Record quality metric for an asset."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO quality_history (asset_id, quality_score, metrics, recorded_at)
                VALUES (?, ?, ?, ?)
            """, (asset_id, quality_score, json.dumps(metrics or {}), datetime.now().isoformat()))
            
            # Update current quality score
            self.update_asset(asset_id, {'quality_score': quality_score})
    
    def get_quality_history(self, asset_id: str) -> List[Dict[str, Any]]:
        """Get quality history for an asset."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT quality_score, metrics, recorded_at
                FROM quality_history
                WHERE asset_id = ?
                ORDER BY recorded_at DESC
            """, (asset_id,))
            
            return [
                {
                    'quality_score': row['quality_score'],
                    'metrics': json.loads(row['metrics']),
                    'recorded_at': row['recorded_at']
                }
                for row in cursor.fetchall()
            ]
    
    def record_nigerian_analysis(
        self,
        asset_id: str,
        detected_language: str,
        confidence: float,
        dialect_features: List[str] = None,
        cultural_markers: List[str] = None
    ):
        """Record Nigerian content analysis results."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO nigerian_analysis (
                    asset_id, detected_language, confidence,
                    dialect_features, cultural_markers, analyzed_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                asset_id,
                detected_language,
                confidence,
                json.dumps(dialect_features or []),
                json.dumps(cultural_markers or []),
                datetime.now().isoformat()
            ))
            
            # Update asset
            is_nigerian = detected_language.lower() in ['pidgin', 'yoruba', 'hausa', 'igbo']
            self.update_asset(asset_id, {
                'is_nigerian': is_nigerian,
                'nigerian_score': confidence if is_nigerian else 0.0,
                'language': detected_language.lower()
            })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total assets by type
            cursor.execute("""
                SELECT asset_type, COUNT(*) as count
                FROM assets
                WHERE status != 'deleted'
                GROUP BY asset_type
            """)
            stats['by_type'] = {row['asset_type']: row['count'] for row in cursor.fetchall()}
            
            # Total assets by language
            cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM assets
                WHERE status != 'deleted'
                GROUP BY language
            """)
            stats['by_language'] = {row['language']: row['count'] for row in cursor.fetchall()}
            
            # Nigerian content stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_nigerian = 1 THEN 1 ELSE 0 END) as nigerian,
                    AVG(CASE WHEN is_nigerian = 1 THEN nigerian_score ELSE NULL END) as avg_score
                FROM assets
                WHERE status != 'deleted'
            """)
            row = cursor.fetchone()
            stats['nigerian'] = {
                'total': row['total'],
                'nigerian_count': row['nigerian'],
                'percentage': (row['nigerian'] / row['total'] * 100) if row['total'] > 0 else 0,
                'avg_score': row['avg_score'] or 0
            }
            
            # Quality distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN quality_score >= 0.8 THEN 'high'
                        WHEN quality_score >= 0.5 THEN 'medium'
                        ELSE 'low'
                    END as quality_band,
                    COUNT(*) as count
                FROM assets
                WHERE status != 'deleted'
                GROUP BY quality_band
            """)
            stats['quality_distribution'] = {row['quality_band']: row['count'] for row in cursor.fetchall()}
            
            # Storage stats
            cursor.execute("""
                SELECT 
                    SUM(size_bytes) as total_bytes,
                    SUM(duration_seconds) as total_duration
                FROM assets
                WHERE status != 'deleted'
            """)
            row = cursor.fetchone()
            stats['storage'] = {
                'total_bytes': row['total_bytes'] or 0,
                'total_duration_hours': (row['total_duration'] or 0) / 3600
            }
            
            return stats


def generate_asset_id(asset_type: AssetType, content: bytes = None, name: str = None) -> str:
    """Generate a unique asset ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    if content:
        content_hash = hashlib.md5(content).hexdigest()[:8]
    else:
        content_hash = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:8]
    
    return f"{asset_type.value}_{timestamp}_{content_hash}"


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience functions for common operations
# ═══════════════════════════════════════════════════════════════════════════════

def register_video(
    store: MetadataStore,
    name: str,
    storage_path: str,
    duration_seconds: float,
    size_bytes: int = 0,
    language: NigerianLanguage = NigerianLanguage.ENGLISH,
    source_url: str = None,
    **kwargs
) -> str:
    """Register a video asset."""
    metadata = AssetMetadata(
        asset_id=generate_asset_id(AssetType.VIDEO, name=name),
        asset_type=AssetType.VIDEO,
        name=name,
        storage_path=storage_path,
        size_bytes=size_bytes,
        duration_seconds=duration_seconds,
        format="mp4",
        language=language,
        properties={'source_url': source_url, **kwargs}
    )
    return store.register_asset(metadata)


def register_audio(
    store: MetadataStore,
    name: str,
    storage_path: str,
    duration_seconds: float,
    size_bytes: int = 0,
    language: NigerianLanguage = NigerianLanguage.ENGLISH,
    parent_video_id: str = None,
    **kwargs
) -> str:
    """Register an audio asset."""
    metadata = AssetMetadata(
        asset_id=generate_asset_id(AssetType.AUDIO, name=name),
        asset_type=AssetType.AUDIO,
        name=name,
        storage_path=storage_path,
        size_bytes=size_bytes,
        duration_seconds=duration_seconds,
        format="wav",
        language=language,
        parent_ids=[parent_video_id] if parent_video_id else [],
        properties=kwargs
    )
    return store.register_asset(metadata)


def register_transcript(
    store: MetadataStore,
    name: str,
    storage_path: str,
    language: NigerianLanguage = NigerianLanguage.ENGLISH,
    parent_audio_id: str = None,
    **kwargs
) -> str:
    """Register a transcript asset."""
    metadata = AssetMetadata(
        asset_id=generate_asset_id(AssetType.TRANSCRIPT, name=name),
        asset_type=AssetType.TRANSCRIPT,
        name=name,
        storage_path=storage_path,
        format="txt",
        language=language,
        parent_ids=[parent_audio_id] if parent_audio_id else [],
        properties=kwargs
    )
    return store.register_asset(metadata)


def register_model(
    store: MetadataStore,
    name: str,
    storage_path: str,
    model_type: str,
    version: str,
    training_dataset_ids: List[str] = None,
    metrics: Dict[str, float] = None,
    **kwargs
) -> str:
    """Register a trained model."""
    metadata = AssetMetadata(
        asset_id=generate_asset_id(AssetType.MODEL, name=name),
        asset_type=AssetType.MODEL,
        name=name,
        storage_path=storage_path,
        storage_type="modal_volume",
        status=AssetStatus.READY,
        parent_ids=training_dataset_ids or [],
        properties={
            'model_type': model_type,
            'version': version,
            'metrics': metrics or {},
            **kwargs
        }
    )
    return store.register_asset(metadata)


if __name__ == "__main__":
    # Demo usage
    store = MetadataStore("demo_metadata.db")
    
    # Register some sample assets
    video_id = register_video(
        store,
        name="Lagos Tech Talk EP 15",
        storage_path="/data/videos/lagos_tech_15.mp4",
        duration_seconds=1800,
        size_bytes=500_000_000,
        language=NigerianLanguage.PIDGIN,
        source_url="https://youtube.com/watch?v=example"
    )
    
    audio_id = register_audio(
        store,
        name="Lagos Tech Talk EP 15 - Audio",
        storage_path="/data/audio/lagos_tech_15.wav",
        duration_seconds=1800,
        size_bytes=150_000_000,
        language=NigerianLanguage.PIDGIN,
        parent_video_id=video_id
    )
    
    transcript_id = register_transcript(
        store,
        name="Lagos Tech Talk EP 15 - Transcript",
        storage_path="/data/transcripts/lagos_tech_15.txt",
        language=NigerianLanguage.PIDGIN,
        parent_audio_id=audio_id
    )
    
    # Record Nigerian analysis
    store.record_nigerian_analysis(
        video_id,
        detected_language="pidgin",
        confidence=0.92,
        dialect_features=["Nigerian Pidgin", "Lagos accent"],
        cultural_markers=["tech jargon", "naija slang"]
    )
    
    # Get statistics
    stats = store.get_statistics()
    print(f"\nMetadata Store Statistics:")
    print(f"  By Type: {stats['by_type']}")
    print(f"  By Language: {stats['by_language']}")
    print(f"  Nigerian Content: {stats['nigerian']}")
    
    # Search
    nigerian_assets = store.get_nigerian_assets(language=NigerianLanguage.PIDGIN)
    print(f"\nNigerian Pidgin Assets: {len(nigerian_assets)}")
    
    # Get lineage
    lineage = store.get_asset_lineage(audio_id)
    print(f"\nAudio lineage: {lineage}")
