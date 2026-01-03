#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - REPLICATE → MODAL FEEDBACK LOOP WEBHOOK SERVICE
═══════════════════════════════════════════════════════════════════════════════
FastAPI webhook receiver for production inference data collection.

Features:
- Secure webhook verification (Replicate signatures)
- Real-time prediction data capture
- Quality filtering (avoid noise)
- Explicit user feedback collection
- Automatic retraining trigger checks
- Performance monitoring

Run: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
- POST /webhooks/replicate - Receive Replicate prediction webhooks
- POST /feedback/explicit - Receive user feedback
- GET /health - Health check
- GET /metrics - Current metrics
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import hmac
import hashlib
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import sqlite3
import aiofiles
from contextlib import asynccontextmanager

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import httpx

# Local imports
try:
    from .quality_filter import QualityFilter, QualityConfig
    from .models import (
        PredictionWebhook, UserFeedback, PredictionData, 
        FeedbackData, WebhookStatus, RetrainingStatus
    )
except ImportError:
    # Standalone mode
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("FeedbackWebhook")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class Settings:
    """Application settings from environment."""
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DATA_DIR = PROJECT_ROOT / "09_FEEDBACK_LOOP" / "data"
    
    # Database
    DB_PATH = DATA_DIR / "feedback_loop.db"
    
    # Webhook security
    REPLICATE_WEBHOOK_SECRET = os.getenv("REPLICATE_WEBHOOK_SECRET", "")
    WEBHOOK_SECRET_FALLBACK = os.getenv("SISI_LOLA_WEBHOOK_SECRET", "sisi-lola-2026")
    
    # Thresholds
    MIN_SAMPLES_FOR_RETRAIN = int(os.getenv("MIN_SAMPLES_RETRAIN", "500"))
    MAX_DAYS_BEFORE_RETRAIN = int(os.getenv("MAX_DAYS_RETRAIN", "14"))
    PERFORMANCE_THRESHOLD = float(os.getenv("PERFORMANCE_THRESHOLD", "0.85"))
    
    # External services
    MODAL_WEBHOOK_URL = os.getenv("MODAL_WEBHOOK_URL", "")
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    
    # Replicate
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")


settings = Settings()


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ModalityType(str, Enum):
    """Supported modality types."""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


class PredictionStatus(str, Enum):
    """Prediction status from Replicate."""
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class PredictionInput(BaseModel):
    """Generic prediction input."""
    prompt: Optional[str] = None
    text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    modality: Optional[ModalityType] = None
    vibe_id: Optional[str] = None
    language: Optional[str] = "en"
    
    class Config:
        extra = "allow"


class PredictionOutput(BaseModel):
    """Generic prediction output."""
    text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: Optional[float] = None
    
    class Config:
        extra = "allow"


class PredictionMetrics(BaseModel):
    """Prediction performance metrics."""
    predict_time: Optional[float] = None
    total_time: Optional[float] = None
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None


class ReplicateWebhookPayload(BaseModel):
    """Full Replicate webhook payload."""
    id: str
    version: Optional[str] = None
    status: PredictionStatus
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Union[Dict, List, str]] = None
    error: Optional[str] = None
    logs: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    urls: Optional[Dict[str, str]] = None


class UserFeedbackInput(BaseModel):
    """User feedback submission."""
    prediction_id: str
    rating: int = Field(ge=1, le=5)
    feedback_type: str = Field(..., regex="^(helpful|inaccurate|offensive|other)$")
    correction: Optional[str] = None
    modality: Optional[ModalityType] = None
    comments: Optional[str] = None
    
    @validator("rating")
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class RetrainingTriggerResponse(BaseModel):
    """Response from retraining trigger check."""
    should_retrain: bool
    reason: str
    priority: str  # "high", "medium", "low", "none"
    metrics: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    database_connected: bool
    samples_collected: int
    last_retrain: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackDatabase:
    """SQLite database for feedback loop data."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                status TEXT,
                modality TEXT,
                input_json TEXT,
                output_json TEXT,
                metrics_json TEXT,
                latency_ms REAL,
                quality_score REAL,
                is_high_quality INTEGER DEFAULT 0,
                created_at TEXT,
                completed_at TEXT,
                received_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id TEXT,
                rating INTEGER,
                feedback_type TEXT,
                correction TEXT,
                comments TEXT,
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        """)
        
        # Retraining runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retraining_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                triggered_at TEXT,
                completed_at TEXT,
                status TEXT,
                trigger_reason TEXT,
                samples_used INTEGER,
                metrics_before_json TEXT,
                metrics_after_json TEXT,
                modal_job_id TEXT
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                modality TEXT,
                avg_latency_ms REAL,
                success_rate REAL,
                avg_quality_score REAL,
                sample_count INTEGER
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_quality ON predictions(is_high_quality)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_modality ON predictions(modality)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_rating ON user_feedback(rating)")
        
        conn.commit()
        conn.close()
    
    async def save_prediction(self, prediction: ReplicateWebhookPayload, 
                               quality_score: float, is_high_quality: bool,
                               modality: str):
        """Save prediction to database."""
        # Calculate latency
        latency_ms = None
        if prediction.started_at and prediction.completed_at:
            start = datetime.fromisoformat(prediction.started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(prediction.completed_at.replace("Z", "+00:00"))
            latency_ms = (end - start).total_seconds() * 1000
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO predictions 
            (id, status, modality, input_json, output_json, metrics_json,
             latency_ms, quality_score, is_high_quality, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction.id,
            prediction.status.value,
            modality,
            json.dumps(prediction.input),
            json.dumps(prediction.output) if prediction.output else None,
            json.dumps(prediction.metrics) if prediction.metrics else None,
            latency_ms,
            quality_score,
            1 if is_high_quality else 0,
            prediction.created_at,
            prediction.completed_at
        ))
        
        conn.commit()
        conn.close()
    
    async def save_user_feedback(self, feedback: UserFeedbackInput):
        """Save user feedback."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_feedback 
            (prediction_id, rating, feedback_type, correction, comments)
            VALUES (?, ?, ?, ?, ?)
        """, (
            feedback.prediction_id,
            feedback.rating,
            feedback.feedback_type,
            feedback.correction,
            feedback.comments
        ))
        
        # Update prediction quality score based on feedback
        if feedback.rating >= 4:
            cursor.execute("""
                UPDATE predictions 
                SET is_high_quality = 1, quality_score = quality_score + 0.2
                WHERE id = ?
            """, (feedback.prediction_id,))
        
        conn.commit()
        conn.close()
    
    async def get_high_quality_count(self) -> int:
        """Get count of high-quality samples."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE is_high_quality = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    async def get_last_retraining(self) -> Optional[datetime]:
        """Get date of last retraining run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT completed_at FROM retraining_runs 
            WHERE status = 'completed' 
            ORDER BY completed_at DESC LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        return None
    
    async def get_performance_metrics(self, days: int = 7) -> Dict[str, float]:
        """Get aggregated performance metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT 
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate,
                AVG(quality_score) as avg_quality,
                COUNT(*) as total_count
            FROM predictions
            WHERE received_at >= ?
        """, (cutoff,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "avg_latency_ms": row[0] or 0,
            "success_rate": row[1] or 0,
            "avg_quality_score": row[2] or 0,
            "total_predictions": row[3] or 0
        }
    
    async def get_samples_for_training(self, limit: int = 10000) -> List[Dict]:
        """Get high-quality samples for retraining."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, f.correction, f.rating as feedback_rating
            FROM predictions p
            LEFT JOIN user_feedback f ON p.id = f.prediction_id
            WHERE p.is_high_quality = 1 AND p.status = 'succeeded'
            ORDER BY p.quality_score DESC
            LIMIT ?
        """, (limit,))
        
        samples = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return samples


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY FILTER
# ═══════════════════════════════════════════════════════════════════════════════

class InlineQualityFilter:
    """
    Intelligent quality filter for production data.
    Filters out noise, spam, PII, and low-value interactions.
    """
    
    # Nigerian Pidgin spam indicators
    SPAM_PATTERNS = [
        "buy now", "click here", "free money", "bitcoin", "crypto scam",
        "nigerian prince", "lottery winner", "password", "credit card"
    ]
    
    # PII patterns (regex)
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone_ng": r'\b(?:\+234|0)\s*[789]\d{9}\b',
        "phone_us": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "nin": r'\b\d{11}\b'  # Nigerian NIN
    }
    
    def __init__(self, min_length: int = 10, max_length: int = 5000,
                 min_confidence: float = 0.5):
        self.min_length = min_length
        self.max_length = max_length
        self.min_confidence = min_confidence
        
        import re
        self.pii_regexes = {k: re.compile(v) for k, v in self.PII_PATTERNS.items()}
    
    def should_keep(self, prediction: ReplicateWebhookPayload) -> tuple[bool, float]:
        """
        Determine if prediction should be kept for retraining.
        
        Returns:
            (should_keep, quality_score)
        """
        # Skip failed predictions
        if prediction.status != PredictionStatus.SUCCEEDED:
            return False, 0.0
        
        # Get input text
        input_text = self._extract_input_text(prediction.input)
        
        # Length check
        if not self._check_length(input_text):
            return False, 0.0
        
        # Spam check
        if self._is_spam(input_text):
            return False, 0.0
        
        # PII check (critical for privacy)
        if self._contains_pii(input_text):
            return False, 0.0
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(prediction, input_text)
        
        return quality_score >= self.min_confidence, quality_score
    
    def _extract_input_text(self, input_data: Dict) -> str:
        """Extract text from various input formats."""
        text_fields = ["prompt", "text", "message", "query", "input"]
        
        for field in text_fields:
            if field in input_data and input_data[field]:
                return str(input_data[field])
        
        return json.dumps(input_data)
    
    def _check_length(self, text: str) -> bool:
        """Check if text length is within bounds."""
        length = len(text.strip())
        return self.min_length <= length <= self.max_length
    
    def _is_spam(self, text: str) -> bool:
        """Check for spam patterns."""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.SPAM_PATTERNS)
    
    def _contains_pii(self, text: str) -> bool:
        """Check for PII in text."""
        for name, regex in self.pii_regexes.items():
            if regex.search(text):
                logger.warning(f"PII detected ({name}), filtering out")
                return True
        return False
    
    def _calculate_quality_score(self, prediction: ReplicateWebhookPayload, 
                                  input_text: str) -> float:
        """Calculate composite quality score (0.0 to 1.0)."""
        score = 0.4  # Base score
        
        # Latency bonus (fast = good infrastructure)
        if prediction.metrics and prediction.metrics.get("predict_time"):
            predict_time = prediction.metrics["predict_time"]
            if predict_time < 2.0:
                score += 0.1
            elif predict_time < 5.0:
                score += 0.05
        
        # Output quality bonus
        if prediction.output:
            output_str = str(prediction.output)
            if len(output_str) > 50:
                score += 0.15
            if len(output_str) > 200:
                score += 0.1
        
        # Nigerian content bonus (more valuable for Sisi Lola)
        nigerian_indicators = ["naija", "wahala", "dey", "abeg", "oya", "lagos", 
                                "abuja", "yoruba", "hausa", "igbo", "pidgin"]
        input_lower = input_text.lower()
        nigerian_count = sum(1 for ind in nigerian_indicators if ind in input_lower)
        if nigerian_count > 0:
            score += min(nigerian_count * 0.05, 0.2)
        
        # Vibe context bonus
        if "vibe" in str(prediction.input).lower():
            score += 0.1
        
        return min(score, 1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# RETRAINING TRIGGER
# ═══════════════════════════════════════════════════════════════════════════════

class RetrainingTrigger:
    """
    Automated retraining trigger logic.
    Determines when to initiate Modal GPU training.
    """
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
        self.min_samples = settings.MIN_SAMPLES_FOR_RETRAIN
        self.max_days = settings.MAX_DAYS_BEFORE_RETRAIN
        self.performance_threshold = settings.PERFORMANCE_THRESHOLD
    
    async def should_trigger(self) -> RetrainingTriggerResponse:
        """
        Multi-criteria check for retraining triggers.
        """
        checks = {
            "sample_count": await self._check_sample_count(),
            "time_elapsed": await self._check_time_elapsed(),
            "performance": await self._check_performance()
        }
        
        # High priority: Performance degradation
        if checks["performance"]["triggered"]:
            return RetrainingTriggerResponse(
                should_retrain=True,
                reason=f"Performance below threshold ({checks['performance']['current']:.2f} < {self.performance_threshold})",
                priority="high",
                metrics=checks
            )
        
        # Medium priority: Enough samples + time elapsed
        if checks["sample_count"]["triggered"] and checks["time_elapsed"]["triggered"]:
            return RetrainingTriggerResponse(
                should_retrain=True,
                reason=f"Sufficient samples ({checks['sample_count']['current']}) and time elapsed ({checks['time_elapsed']['days']} days)",
                priority="medium",
                metrics=checks
            )
        
        # Low priority: Just enough samples
        if checks["sample_count"]["triggered"]:
            return RetrainingTriggerResponse(
                should_retrain=True,
                reason=f"Sufficient samples collected ({checks['sample_count']['current']})",
                priority="low",
                metrics=checks
            )
        
        return RetrainingTriggerResponse(
            should_retrain=False,
            reason="No trigger conditions met",
            priority="none",
            metrics=checks
        )
    
    async def _check_sample_count(self) -> Dict:
        """Check if enough high-quality samples collected."""
        count = await self.db.get_high_quality_count()
        return {
            "triggered": count >= self.min_samples,
            "current": count,
            "threshold": self.min_samples,
            "progress": min(count / self.min_samples * 100, 100)
        }
    
    async def _check_time_elapsed(self) -> Dict:
        """Check time since last retraining."""
        last_retrain = await self.db.get_last_retraining()
        
        if last_retrain:
            days_elapsed = (datetime.utcnow() - last_retrain).days
        else:
            days_elapsed = 999  # Never retrained
        
        return {
            "triggered": days_elapsed >= self.max_days,
            "days": days_elapsed,
            "threshold": self.max_days,
            "progress": min(days_elapsed / self.max_days * 100, 100)
        }
    
    async def _check_performance(self) -> Dict:
        """Check if model performance has degraded."""
        metrics = await self.db.get_performance_metrics(days=7)
        current = metrics.get("success_rate", 1.0)
        
        return {
            "triggered": current < self.performance_threshold,
            "current": current,
            "threshold": self.performance_threshold
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODAL INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class ModalTriggerService:
    """
    Service to trigger Modal training jobs.
    """
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
    
    async def trigger_retraining(self, reason: str, priority: str) -> Dict:
        """
        Trigger Modal retraining job via GitHub Actions or direct API.
        """
        logger.info(f"🚀 Triggering Modal retraining: {reason} (priority: {priority})")
        
        # Get samples for training
        samples = await self.db.get_samples_for_training(limit=5000)
        
        if not samples:
            return {"status": "error", "message": "No samples available for training"}
        
        # Save training data file
        training_data_path = settings.DATA_DIR / "training_export" / f"samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        training_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(training_data_path, "w") as f:
            for sample in samples:
                await f.write(json.dumps(sample) + "\n")
        
        # Record retraining run
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO retraining_runs (triggered_at, status, trigger_reason, samples_used)
            VALUES (?, 'pending', ?, ?)
        """, (datetime.utcnow().isoformat(), reason, len(samples)))
        run_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # If Modal webhook configured, trigger directly
        if settings.MODAL_WEBHOOK_URL:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        settings.MODAL_WEBHOOK_URL,
                        json={
                            "run_id": run_id,
                            "training_data": str(training_data_path),
                            "sample_count": len(samples),
                            "priority": priority,
                            "trigger_reason": reason
                        },
                        timeout=30.0
                    )
                    response.raise_for_status()
                    
                    logger.info(f"✅ Modal training triggered: run_id={run_id}")
                    return {
                        "status": "triggered",
                        "run_id": run_id,
                        "samples": len(samples),
                        "data_path": str(training_data_path)
                    }
            except Exception as e:
                logger.error(f"Failed to trigger Modal: {e}")
        
        # Otherwise, just save data for GitHub Actions to pick up
        return {
            "status": "pending",
            "run_id": run_id,
            "samples": len(samples),
            "data_path": str(training_data_path),
            "message": "Training data prepared. GitHub Actions will process on next run."
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Application state
app_state = {
    "start_time": datetime.utcnow(),
    "predictions_received": 0,
    "feedback_received": 0
}

# Initialize database
db = FeedbackDatabase(settings.DB_PATH)
quality_filter = InlineQualityFilter()
retrain_trigger = RetrainingTrigger(db)
modal_service = ModalTriggerService(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🇳🇬 Sisi Lola Feedback Loop Service starting...")
    logger.info(f"   Database: {settings.DB_PATH}")
    logger.info(f"   Min samples for retrain: {settings.MIN_SAMPLES_FOR_RETRAIN}")
    yield
    logger.info("Shutting down Feedback Loop Service...")


app = FastAPI(
    title="Sisi Lola Feedback Loop",
    description="Replicate → Modal Feedback Loop for continuous learning",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Replicate webhook signature."""
    if not settings.REPLICATE_WEBHOOK_SECRET:
        # Fall back to our own secret
        secret = settings.WEBHOOK_SECRET_FALLBACK
    else:
        secret = settings.REPLICATE_WEBHOOK_SECRET
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected}")


def detect_modality(input_data: Dict) -> ModalityType:
    """Detect modality from input data."""
    if "audio" in str(input_data).lower() or "voice" in str(input_data).lower():
        return ModalityType.VOICE
    if "video" in str(input_data).lower():
        return ModalityType.VIDEO
    if "image" in str(input_data).lower():
        return ModalityType.IMAGE
    if "document" in str(input_data).lower() or "pdf" in str(input_data).lower():
        return ModalityType.DOCUMENT
    return ModalityType.TEXT


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.utcnow() - app_state["start_time"]).total_seconds()
    samples = await db.get_high_quality_count()
    last_retrain = await db.get_last_retraining()
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        uptime_seconds=uptime,
        database_connected=True,
        samples_collected=samples,
        last_retrain=last_retrain.isoformat() if last_retrain else None
    )


@app.post("/webhooks/replicate")
async def receive_replicate_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    webhook_id: Optional[str] = Header(None, alias="webhook-id"),
    webhook_signature: Optional[str] = Header(None, alias="x-replicate-signature")
):
    """
    Receive webhooks from Replicate production inference.
    
    Events: start, output, logs, completed
    """
    payload_bytes = await request.body()
    
    # Verify signature (optional but recommended)
    if webhook_signature and settings.REPLICATE_WEBHOOK_SECRET:
        if not verify_webhook_signature(payload_bytes, webhook_signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        payload = await request.json()
        prediction = ReplicateWebhookPayload(**payload)
    except Exception as e:
        logger.error(f"Failed to parse webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    
    app_state["predictions_received"] += 1
    
    # Only process completed predictions
    if prediction.status != PredictionStatus.SUCCEEDED:
        return {"status": "skipped", "reason": f"Status: {prediction.status}"}
    
    # Apply quality filter
    should_keep, quality_score = quality_filter.should_keep(prediction)
    
    # Detect modality
    modality = detect_modality(prediction.input)
    
    # Save to database (always, for analytics)
    await db.save_prediction(prediction, quality_score, should_keep, modality.value)
    
    logger.info(f"Prediction {prediction.id}: quality={quality_score:.2f}, keep={should_keep}, modality={modality.value}")
    
    # Check retraining triggers in background
    background_tasks.add_task(check_and_trigger_retraining)
    
    return {
        "status": "processed",
        "prediction_id": prediction.id,
        "quality_score": quality_score,
        "kept_for_training": should_keep,
        "modality": modality.value
    }


@app.post("/feedback/explicit")
async def receive_user_feedback(
    feedback: UserFeedbackInput,
    background_tasks: BackgroundTasks
):
    """
    Receive explicit user feedback on predictions.
    Highest quality signal for retraining.
    """
    await db.save_user_feedback(feedback)
    
    app_state["feedback_received"] += 1
    
    logger.info(f"Feedback for {feedback.prediction_id}: rating={feedback.rating}, type={feedback.feedback_type}")
    
    # High ratings are gold for training
    if feedback.rating >= 4:
        logger.info(f"⭐ High-quality feedback received for {feedback.prediction_id}")
    
    # Corrections are even more valuable
    if feedback.correction:
        logger.info(f"📝 Correction provided for {feedback.prediction_id}")
    
    # Check retraining triggers
    background_tasks.add_task(check_and_trigger_retraining)
    
    return {
        "status": "received",
        "prediction_id": feedback.prediction_id,
        "message": "Thank you for your feedback!"
    }


@app.get("/metrics")
async def get_metrics():
    """Get current metrics and statistics."""
    performance = await db.get_performance_metrics(days=7)
    high_quality = await db.get_high_quality_count()
    last_retrain = await db.get_last_retraining()
    
    return {
        "predictions_received": app_state["predictions_received"],
        "feedback_received": app_state["feedback_received"],
        "high_quality_samples": high_quality,
        "performance": performance,
        "last_retraining": last_retrain.isoformat() if last_retrain else None,
        "uptime_seconds": (datetime.utcnow() - app_state["start_time"]).total_seconds()
    }


@app.get("/trigger/status", response_model=RetrainingTriggerResponse)
async def check_trigger_status():
    """Check current retraining trigger status."""
    return await retrain_trigger.should_trigger()


@app.post("/trigger/manual")
async def manual_trigger(background_tasks: BackgroundTasks, reason: str = "Manual trigger via API"):
    """Manually trigger retraining."""
    result = await modal_service.trigger_retraining(reason, priority="high")
    return result


@app.get("/samples/export")
async def export_samples(limit: int = 1000):
    """Export high-quality samples for external use."""
    samples = await db.get_samples_for_training(limit=limit)
    return {
        "count": len(samples),
        "samples": samples
    }


async def check_and_trigger_retraining():
    """Background task to check and trigger retraining."""
    trigger_response = await retrain_trigger.should_trigger()
    
    if trigger_response.should_retrain:
        logger.info(f"🎯 Retraining triggered: {trigger_response.reason}")
        await modal_service.trigger_retraining(
            trigger_response.reason,
            trigger_response.priority
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
