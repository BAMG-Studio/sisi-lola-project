#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
FEEDBACK DATA PROCESSOR - Curator Module
═══════════════════════════════════════════════════════════════════════════════
Curates and filters feedback for training quality:
- Quality scoring
- Nigerian content bonus
- PII detection and removal
- Duplicate detection
- Cultural relevance scoring
- Training data preparation

Ensures only high-quality, culturally-appropriate data feeds into Modal training.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import re
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sqlite3

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from data_processor.collector import (
    FeedbackDatabase, FeedbackItem, FeedbackBatch,
    FeedbackCategory, FeedbackSentiment, FeedbackSource
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeedbackCurator")


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CurationConfig:
    """Configuration for feedback curation."""
    
    # Quality thresholds
    min_quality_score: float = 0.6
    training_quality_threshold: float = 0.75
    
    # Rating weights
    explicit_rating_weight: float = 0.4
    engagement_weight: float = 0.3
    quality_signal_weight: float = 0.3
    
    # Nigerian content bonus
    nigerian_content_bonus: float = 0.15
    
    # Deduplication
    similarity_threshold: float = 0.85
    
    # PII patterns (for filtering)
    enable_pii_filter: bool = True
    
    # Age filtering
    max_age_days: int = 90
    
    # Category-specific thresholds
    category_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "voice": 0.7,
        "video": 0.75,
        "image": 0.65,
        "text": 0.6,
        "multimodal": 0.7
    })


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY SIGNALS
# ═══════════════════════════════════════════════════════════════════════════════

class QualitySignal:
    """Quality signal calculator for feedback items."""
    
    # Nigerian language/cultural markers
    NIGERIAN_MARKERS = {
        "pidgin": [
            "how far", "no wahala", "wetin", "abeg", "oya", "japa",
            "wahala", "gbedu", "sabi", "dey", "na so", "ehen", "shey",
            "e go", "make i", "o dabo", "abi", "sha", "sef"
        ],
        "yoruba": [
            "e kaaro", "bawo ni", "o dabiran", "olorun", "omo",
            "e ku", "pele", "daadaa", "oju", "eyin"
        ],
        "hausa": [
            "sannu", "yaya", "da godiya", "nagode", "kai",
            "ina kwana", "lafiya lau", "allah ya kiyaye"
        ],
        "igbo": [
            "kedu", "nno", "daalu", "chineke", "nwanne",
            "odi mma", "ndewo", "biko"
        ],
        "nigerian_english": [
            "Lagos", "Naija", "Nigeria", "Abuja", "gist",
            "area", "bros", "oga", "madam", "palaver"
        ]
    }
    
    # Quality indicators
    POSITIVE_INDICATORS = [
        "clear", "good", "great", "excellent", "perfect",
        "authentic", "natural", "accurate", "helpful"
    ]
    
    NEGATIVE_INDICATORS = [
        "bad", "poor", "terrible", "wrong", "fake",
        "unnatural", "robotic", "error", "broken"
    ]
    
    @classmethod
    def calculate_nigerian_relevance(cls, text: str) -> float:
        """
        Calculate Nigerian cultural relevance score.
        
        Args:
            text: Text to analyze
            
        Returns:
            Score from 0.0 to 1.0
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Count markers from each category
        marker_count = 0
        category_hits = 0
        
        for category, markers in cls.NIGERIAN_MARKERS.items():
            category_found = False
            for marker in markers:
                if marker in text_lower:
                    marker_count += 1
                    category_found = True
            if category_found:
                category_hits += 1
        
        # Score based on marker density and category coverage
        marker_score = min(marker_count / 5.0, 1.0)
        category_score = category_hits / len(cls.NIGERIAN_MARKERS)
        
        return (marker_score * 0.6 + category_score * 0.4)
    
    @classmethod
    def calculate_sentiment_quality(cls, text: str) -> Tuple[float, str]:
        """
        Calculate quality based on sentiment signals.
        
        Returns:
            Tuple of (quality_score, sentiment_label)
        """
        if not text:
            return 0.5, "neutral"
        
        text_lower = text.lower()
        
        positive_count = sum(1 for ind in cls.POSITIVE_INDICATORS if ind in text_lower)
        negative_count = sum(1 for ind in cls.NEGATIVE_INDICATORS if ind in text_lower)
        
        if positive_count > negative_count:
            score = 0.5 + min((positive_count - negative_count) * 0.1, 0.5)
            sentiment = "positive"
        elif negative_count > positive_count:
            score = 0.5 - min((negative_count - positive_count) * 0.1, 0.4)
            sentiment = "negative"
        else:
            score = 0.5
            sentiment = "neutral"
        
        return score, sentiment


# ═══════════════════════════════════════════════════════════════════════════════
# PII DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class PIIDetector:
    """Detect and filter personally identifiable information."""
    
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone_intl": r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}',
        "phone_ng": r'0[789][01][0-9]{8}',  # Nigerian phone format
        "credit_card": r'\b[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}\b',
        "ssn": r'\b[0-9]{3}[-\s]?[0-9]{2}[-\s]?[0-9]{4}\b',
        "nin": r'\b[0-9]{11}\b',  # Nigerian NIN
        "bvn": r'\b[0-9]{11}\b',  # Nigerian BVN
        "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }
    
    # Names that might indicate personal info
    NAME_PATTERNS = [
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
    ]
    
    @classmethod
    def detect(cls, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to scan
            
        Returns:
            List of detected PII with type and location
        """
        if not text:
            return []
        
        detections = []
        
        for pii_type, pattern in cls.PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detections.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return detections
    
    @classmethod
    def has_pii(cls, text: str) -> bool:
        """Check if text contains PII."""
        return len(cls.detect(text)) > 0
    
    @classmethod
    def redact(cls, text: str) -> str:
        """
        Redact PII from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
        """
        if not text:
            return text
        
        redacted = text
        
        for pii_type, pattern in cls.PATTERNS.items():
            replacement = f"[{pii_type.upper()}_REDACTED]"
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        
        return redacted


# ═══════════════════════════════════════════════════════════════════════════════
# DUPLICATE DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class DuplicateDetector:
    """Detect duplicate or near-duplicate feedback items."""
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
        self._hash_cache: Dict[str, str] = {}
    
    def compute_hash(self, item: FeedbackItem) -> str:
        """Compute content hash for deduplication."""
        # Use multiple signals for hash
        content_parts = [
            item.content_id,
            item.category.value,
            item.content_type,
            str(item.rating or ""),
            item.comment or ""
        ]
        
        content = "|".join(content_parts)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def is_duplicate(self, item: FeedbackItem,
                     similarity_threshold: float = 0.85) -> bool:
        """
        Check if item is a duplicate.
        
        Args:
            item: Item to check
            similarity_threshold: Similarity threshold for near-duplicates
            
        Returns:
            True if duplicate
        """
        item_hash = self.compute_hash(item)
        
        # Exact duplicate check
        if item_hash in self._hash_cache:
            return True
        
        self._hash_cache[item_hash] = item.id
        
        # For now, just use exact hash matching
        # Could extend to fuzzy matching for near-duplicates
        
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK CURATOR
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackCurator:
    """
    Main curator for filtering and scoring feedback.
    
    Applies quality filters and prepares data for training.
    """
    
    def __init__(self, db: FeedbackDatabase, config: Optional[CurationConfig] = None):
        self.db = db
        self.config = config or CurationConfig()
        self.duplicate_detector = DuplicateDetector(db)
    
    def curate_item(self, item: FeedbackItem) -> Tuple[bool, float, List[str]]:
        """
        Curate a single feedback item.
        
        Args:
            item: Item to curate
            
        Returns:
            Tuple of (is_valid, quality_score, rejection_reasons)
        """
        rejection_reasons = []
        quality_scores = []
        
        # 1. Check for PII
        if self.config.enable_pii_filter:
            if item.comment and PIIDetector.has_pii(item.comment):
                rejection_reasons.append("contains_pii")
                # Redact instead of reject
                item.comment = PIIDetector.redact(item.comment)
        
        # 2. Check for duplicates
        if self.duplicate_detector.is_duplicate(item):
            rejection_reasons.append("duplicate")
            return False, 0.0, rejection_reasons
        
        # 3. Calculate explicit rating score
        if item.rating is not None:
            quality_scores.append(item.rating * self.config.explicit_rating_weight)
        
        # 4. Calculate Nigerian relevance bonus
        nigerian_score = 0.0
        if item.comment:
            nigerian_score = QualitySignal.calculate_nigerian_relevance(item.comment)
            item.cultural_relevance = nigerian_score
        
        if item.language_detected in ["pidgin", "yoruba", "hausa", "igbo"]:
            nigerian_score = max(nigerian_score, 0.8)
        
        # Apply Nigerian bonus
        nigerian_bonus = nigerian_score * self.config.nigerian_content_bonus
        
        # 5. Calculate engagement score (based on source)
        engagement_score = 0.5
        if item.source == FeedbackSource.USER_EXPLICIT:
            engagement_score = 0.7
        elif item.source == FeedbackSource.ENGAGEMENT:
            engagement_score = 0.6
        
        quality_scores.append(engagement_score * self.config.engagement_weight)
        
        # 6. Calculate sentiment-based quality
        if item.comment:
            sentiment_quality, _ = QualitySignal.calculate_sentiment_quality(item.comment)
            quality_scores.append(sentiment_quality * self.config.quality_signal_weight)
        else:
            quality_scores.append(0.5 * self.config.quality_signal_weight)
        
        # 7. Compute final quality score
        base_score = sum(quality_scores) / max(
            self.config.explicit_rating_weight +
            self.config.engagement_weight +
            self.config.quality_signal_weight,
            0.01
        )
        
        final_score = min(base_score + nigerian_bonus, 1.0)
        
        # 8. Check category-specific threshold
        category_threshold = self.config.category_thresholds.get(
            item.category.value,
            self.config.min_quality_score
        )
        
        if final_score < category_threshold:
            rejection_reasons.append(f"below_threshold_{category_threshold}")
        
        # 9. Determine if training-ready
        is_valid = len([r for r in rejection_reasons if r != "contains_pii"]) == 0
        
        return is_valid, final_score, rejection_reasons
    
    def curate_batch(self, items: List[FeedbackItem]) -> Dict[str, Any]:
        """
        Curate a batch of feedback items.
        
        Args:
            items: List of items to curate
            
        Returns:
            Curation results
        """
        results = {
            "total": len(items),
            "accepted": 0,
            "rejected": 0,
            "rejection_reasons": {},
            "avg_quality": 0.0,
            "training_ready": 0,
            "items": []
        }
        
        quality_scores = []
        
        for item in items:
            is_valid, quality_score, rejection_reasons = self.curate_item(item)
            
            # Update item
            item.quality_score = quality_score
            item.is_processed = True
            item.is_training_ready = is_valid and quality_score >= self.config.training_quality_threshold
            item.processed_at = datetime.utcnow().isoformat()
            
            # Save to database
            self.db.mark_processed(item.id, quality_score, item.is_training_ready)
            
            if is_valid:
                results["accepted"] += 1
                quality_scores.append(quality_score)
                
                if item.is_training_ready:
                    results["training_ready"] += 1
            else:
                results["rejected"] += 1
                for reason in rejection_reasons:
                    results["rejection_reasons"][reason] = \
                        results["rejection_reasons"].get(reason, 0) + 1
            
            results["items"].append({
                "id": item.id,
                "valid": is_valid,
                "quality": quality_score,
                "training_ready": item.is_training_ready,
                "reasons": rejection_reasons
            })
        
        results["avg_quality"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        logger.info(f"📊 Curated {results['total']} items: "
                   f"{results['accepted']} accepted, {results['rejected']} rejected, "
                   f"{results['training_ready']} training-ready")
        
        return results
    
    def process_pending(self, limit: int = 100) -> Dict[str, Any]:
        """
        Process pending (unprocessed) feedback items.
        
        Args:
            limit: Maximum items to process
            
        Returns:
            Curation results
        """
        pending = self.db.get_unprocessed(limit=limit)
        
        if not pending:
            logger.info("No pending feedback items")
            return {"total": 0}
        
        return self.curate_batch(pending)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING DATA EXPORTER
# ═══════════════════════════════════════════════════════════════════════════════

class TrainingDataExporter:
    """Export curated feedback for Modal training."""
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
    
    def export_for_voice_training(self, 
                                   output_path: Path,
                                   min_quality: float = 0.75) -> Dict[str, Any]:
        """
        Export voice feedback for TTS/voice cloning training.
        
        Args:
            output_path: Output file path
            min_quality: Minimum quality score
            
        Returns:
            Export statistics
        """
        items = self.db.get_training_ready(
            FeedbackCategory.VOICE,
            min_quality=min_quality
        )
        
        training_data = []
        
        for item in items:
            if item.content_url:
                training_data.append({
                    "audio_url": item.content_url,
                    "rating": item.rating,
                    "quality_score": item.quality_score,
                    "cultural_relevance": item.cultural_relevance,
                    "language": item.language_detected,
                    "tags": item.tags,
                    "model_version": item.model_version
                })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"📤 Exported {len(training_data)} voice samples to {output_path}")
        
        return {
            "category": "voice",
            "count": len(training_data),
            "output_path": str(output_path)
        }
    
    def export_for_video_training(self,
                                   output_path: Path,
                                   min_quality: float = 0.75) -> Dict[str, Any]:
        """
        Export video feedback for video generation training.
        """
        items = self.db.get_training_ready(
            FeedbackCategory.VIDEO,
            min_quality=min_quality
        )
        
        training_data = []
        
        for item in items:
            if item.content_url:
                training_data.append({
                    "video_url": item.content_url,
                    "rating": item.rating,
                    "quality_score": item.quality_score,
                    "cultural_relevance": item.cultural_relevance,
                    "tags": item.tags,
                    "inference_id": item.inference_id
                })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"📤 Exported {len(training_data)} video samples to {output_path}")
        
        return {
            "category": "video",
            "count": len(training_data),
            "output_path": str(output_path)
        }
    
    def export_for_image_training(self,
                                   output_path: Path,
                                   min_quality: float = 0.7) -> Dict[str, Any]:
        """
        Export image feedback for image generation training.
        """
        items = self.db.get_training_ready(
            FeedbackCategory.IMAGE,
            min_quality=min_quality
        )
        
        training_data = []
        
        for item in items:
            if item.content_url:
                training_data.append({
                    "image_url": item.content_url,
                    "rating": item.rating,
                    "quality_score": item.quality_score,
                    "cultural_relevance": item.cultural_relevance,
                    "comment": item.comment,  # Could include prompt info
                    "tags": item.tags
                })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"📤 Exported {len(training_data)} image samples to {output_path}")
        
        return {
            "category": "image",
            "count": len(training_data),
            "output_path": str(output_path)
        }
    
    def export_all(self, output_dir: Path) -> Dict[str, Any]:
        """
        Export all categories for training.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Export statistics for all categories
        """
        results = {}
        
        results["voice"] = self.export_for_voice_training(
            output_dir / "voice_training.json"
        )
        
        results["video"] = self.export_for_video_training(
            output_dir / "video_training.json"
        )
        
        results["image"] = self.export_for_image_training(
            output_dir / "image_training.json"
        )
        
        # Summary
        total_exported = sum(r["count"] for r in results.values())
        results["summary"] = {
            "total_exported": total_exported,
            "output_dir": str(output_dir),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"📦 Total exported: {total_exported} samples")
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Feedback Curator")
    parser.add_argument("--action", choices=["curate", "export", "stats"],
                        default="stats", help="Action to perform")
    parser.add_argument("--limit", type=int, default=100, help="Items to process")
    parser.add_argument("--output", type=str, default="training_data",
                        help="Output directory for exports")
    
    args = parser.parse_args()
    
    db = FeedbackDatabase()
    
    if args.action == "curate":
        curator = FeedbackCurator(db)
        results = curator.process_pending(limit=args.limit)
        print(json.dumps(results, indent=2, default=str))
    
    elif args.action == "export":
        exporter = TrainingDataExporter(db)
        results = exporter.export_all(Path(args.output))
        print(json.dumps(results, indent=2))
    
    elif args.action == "stats":
        stats = db.get_stats()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
