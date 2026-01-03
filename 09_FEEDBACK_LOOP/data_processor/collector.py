#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
FEEDBACK DATA PROCESSOR - Collector Module
═══════════════════════════════════════════════════════════════════════════════
Collects and processes feedback from multiple sources:
- Replicate webhook payloads
- User explicit feedback (ratings, comments)
- Implicit feedback (engagement metrics)
- A/B test results

Prepares data for Modal retraining pipeline.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import hashlib
import logging
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import httpx

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeedbackCollector")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS AND DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackSource(str, Enum):
    REPLICATE_WEBHOOK = "replicate_webhook"
    USER_EXPLICIT = "user_explicit"
    ENGAGEMENT = "engagement"
    AB_TEST = "ab_test"
    QUALITY_FILTER = "quality_filter"


class FeedbackCategory(str, Enum):
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    MULTIMODAL = "multimodal"


class FeedbackSentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class FeedbackItem:
    """Single feedback item."""
    id: str
    source: FeedbackSource
    category: FeedbackCategory
    
    # Content info
    content_id: str
    content_type: str
    content_url: Optional[str] = None
    
    # Feedback data
    rating: Optional[float] = None  # 0.0 to 1.0
    sentiment: FeedbackSentiment = FeedbackSentiment.NEUTRAL
    comment: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Metadata
    model_version: Optional[str] = None
    inference_id: Optional[str] = None
    latency_ms: Optional[float] = None
    
    # Nigerian context
    language_detected: Optional[str] = None
    cultural_relevance: float = 0.5
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    processed_at: Optional[str] = None
    
    # Processing state
    is_processed: bool = False
    is_training_ready: bool = False
    quality_score: float = 0.0


@dataclass
class FeedbackBatch:
    """Batch of feedback items for processing."""
    batch_id: str
    items: List[FeedbackItem]
    category: FeedbackCategory
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    total_items: int = 0
    positive_count: int = 0
    negative_count: int = 0
    avg_rating: float = 0.0
    
    def __post_init__(self):
        self.total_items = len(self.items)
        ratings = [i.rating for i in self.items if i.rating is not None]
        self.avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        self.positive_count = len([i for i in self.items if i.sentiment == FeedbackSentiment.POSITIVE])
        self.negative_count = len([i for i in self.items if i.sentiment == FeedbackSentiment.NEGATIVE])


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackDatabase:
    """SQLite database for feedback storage."""
    
    def __init__(self, db_path: str = "feedback_data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_items (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content_id TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    content_url TEXT,
                    rating REAL,
                    sentiment TEXT,
                    comment TEXT,
                    tags TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    model_version TEXT,
                    inference_id TEXT,
                    latency_ms REAL,
                    language_detected TEXT,
                    cultural_relevance REAL,
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    is_processed INTEGER DEFAULT 0,
                    is_training_ready INTEGER DEFAULT 0,
                    quality_score REAL DEFAULT 0.0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_batches (
                    batch_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    total_items INTEGER,
                    positive_count INTEGER,
                    negative_count INTEGER,
                    avg_rating REAL,
                    status TEXT DEFAULT 'pending',
                    processed_at TEXT
                )
            """)
            
            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback_items(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_processed ON feedback_items(is_processed)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_training ON feedback_items(is_training_ready)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback_items(created_at)")
            
            conn.commit()
    
    def insert_feedback(self, item: FeedbackItem):
        """Insert a feedback item."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO feedback_items (
                    id, source, category, content_id, content_type, content_url,
                    rating, sentiment, comment, tags, user_id, session_id,
                    model_version, inference_id, latency_ms,
                    language_detected, cultural_relevance,
                    created_at, processed_at, is_processed, is_training_ready, quality_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id, item.source.value, item.category.value,
                item.content_id, item.content_type, item.content_url,
                item.rating, item.sentiment.value, item.comment,
                json.dumps(item.tags), item.user_id, item.session_id,
                item.model_version, item.inference_id, item.latency_ms,
                item.language_detected, item.cultural_relevance,
                item.created_at, item.processed_at,
                1 if item.is_processed else 0,
                1 if item.is_training_ready else 0,
                item.quality_score
            ))
            conn.commit()
    
    def get_unprocessed(self, category: Optional[FeedbackCategory] = None,
                        limit: int = 100) -> List[FeedbackItem]:
        """Get unprocessed feedback items."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if category:
                rows = conn.execute("""
                    SELECT * FROM feedback_items
                    WHERE is_processed = 0 AND category = ?
                    ORDER BY created_at ASC
                    LIMIT ?
                """, (category.value, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM feedback_items
                    WHERE is_processed = 0
                    ORDER BY created_at ASC
                    LIMIT ?
                """, (limit,)).fetchall()
            
            return [self._row_to_item(row) for row in rows]
    
    def get_training_ready(self, category: FeedbackCategory,
                           min_quality: float = 0.7,
                           limit: int = 1000) -> List[FeedbackItem]:
        """Get items ready for training."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute("""
                SELECT * FROM feedback_items
                WHERE is_training_ready = 1 
                AND category = ?
                AND quality_score >= ?
                ORDER BY quality_score DESC
                LIMIT ?
            """, (category.value, min_quality, limit)).fetchall()
            
            return [self._row_to_item(row) for row in rows]
    
    def mark_processed(self, item_id: str, quality_score: float,
                       is_training_ready: bool):
        """Mark item as processed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE feedback_items
                SET is_processed = 1,
                    quality_score = ?,
                    is_training_ready = ?,
                    processed_at = ?
                WHERE id = ?
            """, (quality_score, 1 if is_training_ready else 0,
                  datetime.utcnow().isoformat(), item_id))
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM feedback_items").fetchone()[0]
            processed = conn.execute("SELECT COUNT(*) FROM feedback_items WHERE is_processed = 1").fetchone()[0]
            training_ready = conn.execute("SELECT COUNT(*) FROM feedback_items WHERE is_training_ready = 1").fetchone()[0]
            
            # By category
            by_category = {}
            for cat in FeedbackCategory:
                count = conn.execute(
                    "SELECT COUNT(*) FROM feedback_items WHERE category = ?",
                    (cat.value,)
                ).fetchone()[0]
                by_category[cat.value] = count
            
            # Average ratings
            avg_rating = conn.execute(
                "SELECT AVG(rating) FROM feedback_items WHERE rating IS NOT NULL"
            ).fetchone()[0]
            
            return {
                "total": total,
                "processed": processed,
                "training_ready": training_ready,
                "by_category": by_category,
                "avg_rating": avg_rating or 0.0
            }
    
    def _row_to_item(self, row) -> FeedbackItem:
        """Convert database row to FeedbackItem."""
        return FeedbackItem(
            id=row["id"],
            source=FeedbackSource(row["source"]),
            category=FeedbackCategory(row["category"]),
            content_id=row["content_id"],
            content_type=row["content_type"],
            content_url=row["content_url"],
            rating=row["rating"],
            sentiment=FeedbackSentiment(row["sentiment"]) if row["sentiment"] else FeedbackSentiment.NEUTRAL,
            comment=row["comment"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            user_id=row["user_id"],
            session_id=row["session_id"],
            model_version=row["model_version"],
            inference_id=row["inference_id"],
            latency_ms=row["latency_ms"],
            language_detected=row["language_detected"],
            cultural_relevance=row["cultural_relevance"],
            created_at=row["created_at"],
            processed_at=row["processed_at"],
            is_processed=bool(row["is_processed"]),
            is_training_ready=bool(row["is_training_ready"]),
            quality_score=row["quality_score"]
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK COLLECTORS
# ═══════════════════════════════════════════════════════════════════════════════

class BaseCollector:
    """Base class for feedback collectors."""
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
    
    def generate_id(self, *parts) -> str:
        """Generate deterministic ID from parts."""
        content = ":".join(str(p) for p in parts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ReplicateWebhookCollector(BaseCollector):
    """Collector for Replicate webhook payloads."""
    
    def collect(self, payload: Dict[str, Any]) -> Optional[FeedbackItem]:
        """
        Process Replicate webhook payload into feedback item.
        
        Args:
            payload: Webhook payload from Replicate
            
        Returns:
            FeedbackItem or None if invalid
        """
        try:
            prediction_id = payload.get("id")
            status = payload.get("status")
            
            if status != "succeeded":
                return None
            
            # Extract model info
            model = payload.get("version", "")
            
            # Determine category from model
            category = self._infer_category(model)
            
            # Extract output
            output = payload.get("output")
            if isinstance(output, list):
                output_url = output[0] if output else None
            elif isinstance(output, str):
                output_url = output
            else:
                output_url = None
            
            # Extract metrics
            metrics = payload.get("metrics", {})
            latency = metrics.get("predict_time", 0) * 1000
            
            # Create feedback item
            item = FeedbackItem(
                id=self.generate_id("replicate", prediction_id),
                source=FeedbackSource.REPLICATE_WEBHOOK,
                category=category,
                content_id=prediction_id,
                content_type=category.value,
                content_url=output_url,
                model_version=model.split(":")[-1][:12] if ":" in model else model,
                inference_id=prediction_id,
                latency_ms=latency,
                # Default rating based on successful inference
                rating=0.5,
                sentiment=FeedbackSentiment.NEUTRAL
            )
            
            self.db.insert_feedback(item)
            logger.info(f"📥 Collected Replicate webhook: {prediction_id}")
            
            return item
            
        except Exception as e:
            logger.error(f"Failed to collect webhook: {e}")
            return None
    
    def _infer_category(self, model: str) -> FeedbackCategory:
        """Infer category from model name."""
        model_lower = model.lower()
        
        if any(x in model_lower for x in ["tts", "speech", "voice", "whisper", "audio"]):
            return FeedbackCategory.VOICE
        elif any(x in model_lower for x in ["video", "omni-human", "wav2lip"]):
            return FeedbackCategory.VIDEO
        elif any(x in model_lower for x in ["flux", "sdxl", "image", "dall", "seedream"]):
            return FeedbackCategory.IMAGE
        elif any(x in model_lower for x in ["llama", "qwen", "gpt", "claude"]):
            return FeedbackCategory.TEXT
        else:
            return FeedbackCategory.MULTIMODAL


class UserFeedbackCollector(BaseCollector):
    """Collector for explicit user feedback."""
    
    def collect_rating(self,
                       content_id: str,
                       rating: float,
                       category: FeedbackCategory,
                       user_id: Optional[str] = None,
                       comment: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> FeedbackItem:
        """
        Collect explicit user rating.
        
        Args:
            content_id: ID of content being rated
            rating: Rating value (0.0 to 1.0)
            category: Content category
            user_id: Optional user identifier
            comment: Optional user comment
            tags: Optional tags
            
        Returns:
            Created FeedbackItem
        """
        # Determine sentiment from rating
        if rating >= 0.7:
            sentiment = FeedbackSentiment.POSITIVE
        elif rating <= 0.3:
            sentiment = FeedbackSentiment.NEGATIVE
        else:
            sentiment = FeedbackSentiment.NEUTRAL
        
        item = FeedbackItem(
            id=self.generate_id("user", content_id, user_id or "anon", datetime.utcnow().isoformat()),
            source=FeedbackSource.USER_EXPLICIT,
            category=category,
            content_id=content_id,
            content_type=category.value,
            rating=rating,
            sentiment=sentiment,
            comment=comment,
            tags=tags or [],
            user_id=user_id
        )
        
        self.db.insert_feedback(item)
        logger.info(f"⭐ Collected user rating: {content_id} = {rating}")
        
        return item
    
    def collect_reaction(self,
                         content_id: str,
                         reaction: str,
                         category: FeedbackCategory,
                         user_id: Optional[str] = None) -> FeedbackItem:
        """
        Collect reaction (like, dislike, love, etc.)
        
        Args:
            content_id: ID of content
            reaction: Reaction type (like, dislike, love, etc.)
            category: Content category
            user_id: Optional user identifier
            
        Returns:
            Created FeedbackItem
        """
        # Map reactions to ratings
        reaction_map = {
            "like": 0.7,
            "love": 1.0,
            "dislike": 0.2,
            "angry": 0.0,
            "wow": 0.8,
            "sad": 0.3,
            "haha": 0.7
        }
        
        rating = reaction_map.get(reaction.lower(), 0.5)
        sentiment = (
            FeedbackSentiment.POSITIVE if rating >= 0.6
            else FeedbackSentiment.NEGATIVE if rating <= 0.3
            else FeedbackSentiment.NEUTRAL
        )
        
        item = FeedbackItem(
            id=self.generate_id("reaction", content_id, user_id or "anon", reaction),
            source=FeedbackSource.USER_EXPLICIT,
            category=category,
            content_id=content_id,
            content_type=category.value,
            rating=rating,
            sentiment=sentiment,
            tags=[f"reaction:{reaction}"],
            user_id=user_id
        )
        
        self.db.insert_feedback(item)
        logger.info(f"👍 Collected reaction: {content_id} = {reaction}")
        
        return item


class EngagementCollector(BaseCollector):
    """Collector for implicit engagement signals."""
    
    def collect_view(self,
                     content_id: str,
                     category: FeedbackCategory,
                     view_duration_seconds: float,
                     total_duration_seconds: float,
                     user_id: Optional[str] = None) -> Optional[FeedbackItem]:
        """
        Collect view engagement signal.
        
        Args:
            content_id: ID of content
            category: Content category
            view_duration_seconds: How long user viewed
            total_duration_seconds: Total content duration
            user_id: Optional user identifier
            
        Returns:
            FeedbackItem or None if not significant
        """
        # Calculate engagement ratio
        if total_duration_seconds <= 0:
            return None
        
        engagement_ratio = min(view_duration_seconds / total_duration_seconds, 1.0)
        
        # Only record significant engagement (>10% or >5 seconds)
        if engagement_ratio < 0.1 and view_duration_seconds < 5:
            return None
        
        # Convert to rating
        rating = engagement_ratio
        sentiment = (
            FeedbackSentiment.POSITIVE if rating >= 0.5
            else FeedbackSentiment.NEUTRAL
        )
        
        item = FeedbackItem(
            id=self.generate_id("view", content_id, user_id or "anon", datetime.utcnow().isoformat()),
            source=FeedbackSource.ENGAGEMENT,
            category=category,
            content_id=content_id,
            content_type=category.value,
            rating=rating,
            sentiment=sentiment,
            tags=["engagement:view"],
            user_id=user_id
        )
        
        self.db.insert_feedback(item)
        logger.info(f"👀 Collected view: {content_id} ({engagement_ratio:.1%})")
        
        return item
    
    def collect_share(self,
                      content_id: str,
                      category: FeedbackCategory,
                      platform: str,
                      user_id: Optional[str] = None) -> FeedbackItem:
        """
        Collect share event (strong positive signal).
        
        Args:
            content_id: ID of content
            category: Content category
            platform: Where shared (whatsapp, twitter, etc.)
            user_id: Optional user identifier
            
        Returns:
            FeedbackItem
        """
        item = FeedbackItem(
            id=self.generate_id("share", content_id, user_id or "anon", platform),
            source=FeedbackSource.ENGAGEMENT,
            category=category,
            content_id=content_id,
            content_type=category.value,
            rating=0.9,  # Shares are strong positive signals
            sentiment=FeedbackSentiment.POSITIVE,
            tags=["engagement:share", f"platform:{platform}"],
            user_id=user_id
        )
        
        self.db.insert_feedback(item)
        logger.info(f"📤 Collected share: {content_id} → {platform}")
        
        return item


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED COLLECTOR SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackCollectorService:
    """
    Unified feedback collection service.
    
    Aggregates feedback from all sources:
    - Replicate webhooks
    - User ratings/reactions
    - Engagement signals
    """
    
    def __init__(self, db_path: str = "feedback_data.db"):
        self.db = FeedbackDatabase(db_path)
        
        self.replicate = ReplicateWebhookCollector(self.db)
        self.user = UserFeedbackCollector(self.db)
        self.engagement = EngagementCollector(self.db)
    
    def collect_webhook(self, payload: Dict[str, Any]) -> Optional[FeedbackItem]:
        """Collect from Replicate webhook."""
        return self.replicate.collect(payload)
    
    def collect_rating(self, **kwargs) -> FeedbackItem:
        """Collect user rating."""
        return self.user.collect_rating(**kwargs)
    
    def collect_reaction(self, **kwargs) -> FeedbackItem:
        """Collect user reaction."""
        return self.user.collect_reaction(**kwargs)
    
    def collect_view(self, **kwargs) -> Optional[FeedbackItem]:
        """Collect view engagement."""
        return self.engagement.collect_view(**kwargs)
    
    def collect_share(self, **kwargs) -> FeedbackItem:
        """Collect share engagement."""
        return self.engagement.collect_share(**kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return self.db.get_stats()
    
    def get_training_batch(self,
                           category: FeedbackCategory,
                           min_quality: float = 0.7,
                           limit: int = 500) -> FeedbackBatch:
        """
        Get batch of items ready for training.
        
        Args:
            category: Category to get
            min_quality: Minimum quality score
            limit: Maximum items
            
        Returns:
            FeedbackBatch
        """
        items = self.db.get_training_ready(category, min_quality, limit)
        
        return FeedbackBatch(
            batch_id=f"batch_{category.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            items=items,
            category=category
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Feedback Collector")
    parser.add_argument("--action", choices=["stats", "collect", "batch"],
                        default="stats", help="Action to perform")
    parser.add_argument("--category", type=str, help="Category for batch")
    
    args = parser.parse_args()
    
    service = FeedbackCollectorService()
    
    if args.action == "stats":
        stats = service.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.action == "batch":
        category = FeedbackCategory(args.category) if args.category else FeedbackCategory.VOICE
        batch = service.get_training_batch(category)
        print(f"Batch: {batch.batch_id}")
        print(f"Items: {batch.total_items}")
        print(f"Avg Rating: {batch.avg_rating:.2f}")


if __name__ == "__main__":
    main()
