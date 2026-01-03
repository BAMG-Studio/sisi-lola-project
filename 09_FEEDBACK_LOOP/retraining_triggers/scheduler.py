#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
RETRAINING TRIGGER SCHEDULER
═══════════════════════════════════════════════════════════════════════════════
Intelligent scheduling for triggering Modal retraining based on feedback signals.

Features:
- Threshold-based triggering (feedback volume, quality scores)
- Time-based scheduling (prevent too frequent retraining)
- Category-specific triggers (voice, video, image)
- Integration with GitHub Actions
- Cost estimation before triggering
- Nigerian content prioritization

Ensures efficient use of GPU resources while keeping models fresh.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import sqlite3
import logging
import asyncio
import httpx
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RetrainingScheduler")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class TriggerReason(str, Enum):
    FEEDBACK_VOLUME = "feedback_volume"
    QUALITY_IMPROVEMENT = "quality_improvement"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    NIGERIAN_CONTENT_BOOST = "nigerian_content_boost"


@dataclass
class TriggerConfig:
    """Configuration for retraining triggers."""
    
    # Volume thresholds
    min_feedback_items: int = 100
    min_training_ready_items: int = 50
    
    # Quality thresholds  
    min_avg_quality: float = 0.7
    quality_improvement_threshold: float = 0.05  # 5% improvement
    
    # Time constraints
    min_hours_between_training: int = 24
    max_days_since_last_training: int = 7
    
    # Nigerian content bonus
    nigerian_content_weight: float = 1.5
    nigerian_bonus_threshold: int = 30  # Items with Nigerian markers
    
    # Cost constraints
    max_daily_training_cost_usd: float = 50.0
    estimated_cost_per_hour: Dict[str, float] = field(default_factory=lambda: {
        "voice": 3.0,  # A100 cost
        "video": 4.0,
        "image": 3.0
    })
    
    # Category-specific settings
    category_configs: Dict[str, Dict] = field(default_factory=lambda: {
        "voice": {
            "min_items": 50,
            "max_training_hours": 2,
            "priority": 1
        },
        "video": {
            "min_items": 30,
            "max_training_hours": 4,
            "priority": 2
        },
        "image": {
            "min_items": 100,
            "max_training_hours": 2,
            "priority": 3
        }
    })


# ═══════════════════════════════════════════════════════════════════════════════
# TRIGGER DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class TriggerDatabase:
    """Database for tracking training triggers and history."""
    
    def __init__(self, db_path: str = "trigger_history.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_runs (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    trigger_reason TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT DEFAULT 'pending',
                    samples_used INTEGER,
                    estimated_cost_usd REAL,
                    actual_cost_usd REAL,
                    final_loss REAL,
                    checkpoint_path TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trigger_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluated_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    should_trigger INTEGER,
                    reason TEXT,
                    feedback_count INTEGER,
                    training_ready_count INTEGER,
                    avg_quality REAL,
                    nigerian_content_count INTEGER,
                    hours_since_last_training REAL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_category 
                ON training_runs(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_started 
                ON training_runs(started_at)
            """)
            
            conn.commit()
    
    def record_training_run(self, 
                            run_id: str,
                            category: str,
                            trigger_reason: TriggerReason,
                            samples_used: int,
                            estimated_cost: float) -> None:
        """Record a new training run."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO training_runs (
                    id, category, trigger_reason, started_at, 
                    samples_used, estimated_cost_usd
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                run_id, category, trigger_reason.value,
                datetime.utcnow().isoformat(),
                samples_used, estimated_cost
            ))
            conn.commit()
    
    def complete_training_run(self,
                               run_id: str,
                               status: str,
                               final_loss: Optional[float] = None,
                               actual_cost: Optional[float] = None,
                               checkpoint_path: Optional[str] = None) -> None:
        """Mark training run as complete."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE training_runs 
                SET completed_at = ?,
                    status = ?,
                    final_loss = ?,
                    actual_cost_usd = ?,
                    checkpoint_path = ?
                WHERE id = ?
            """, (
                datetime.utcnow().isoformat(),
                status, final_loss, actual_cost, checkpoint_path, run_id
            ))
            conn.commit()
    
    def get_last_training(self, category: str) -> Optional[Dict[str, Any]]:
        """Get last training run for category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM training_runs
                WHERE category = ?
                ORDER BY started_at DESC
                LIMIT 1
            """, (category,)).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_daily_cost(self) -> float:
        """Get total training cost for today."""
        today = datetime.utcnow().date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT COALESCE(SUM(COALESCE(actual_cost_usd, estimated_cost_usd)), 0)
                FROM training_runs
                WHERE date(started_at) = ?
            """, (today,)).fetchone()
            
            return result[0] if result else 0.0
    
    def record_evaluation(self, evaluation: Dict[str, Any]) -> None:
        """Record trigger evaluation for analytics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO trigger_evaluations (
                    evaluated_at, category, should_trigger, reason,
                    feedback_count, training_ready_count, avg_quality,
                    nigerian_content_count, hours_since_last_training
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                evaluation["category"],
                1 if evaluation["should_trigger"] else 0,
                evaluation.get("reason"),
                evaluation.get("feedback_count", 0),
                evaluation.get("training_ready_count", 0),
                evaluation.get("avg_quality", 0),
                evaluation.get("nigerian_content_count", 0),
                evaluation.get("hours_since_last_training")
            ))
            conn.commit()
    
    def get_training_history(self, 
                              category: Optional[str] = None,
                              limit: int = 20) -> List[Dict[str, Any]]:
        """Get training history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if category:
                rows = conn.execute("""
                    SELECT * FROM training_runs
                    WHERE category = ?
                    ORDER BY started_at DESC
                    LIMIT ?
                """, (category, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM training_runs
                    ORDER BY started_at DESC
                    LIMIT ?
                """, (limit,)).fetchall()
            
            return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK STATS COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackStatsCollector:
    """Collect statistics from feedback database for trigger evaluation."""
    
    def __init__(self, feedback_db_path: str = "feedback_data.db"):
        self.feedback_db_path = feedback_db_path
    
    def get_stats_for_category(self, category: str) -> Dict[str, Any]:
        """Get feedback statistics for a category."""
        with sqlite3.connect(self.feedback_db_path) as conn:
            # Total feedback
            total = conn.execute("""
                SELECT COUNT(*) FROM feedback_items
                WHERE category = ?
            """, (category,)).fetchone()[0]
            
            # Training ready
            training_ready = conn.execute("""
                SELECT COUNT(*) FROM feedback_items
                WHERE category = ? AND is_training_ready = 1
            """, (category,)).fetchone()[0]
            
            # Average quality
            avg_quality = conn.execute("""
                SELECT AVG(quality_score) FROM feedback_items
                WHERE category = ? AND quality_score > 0
            """, (category,)).fetchone()[0] or 0.0
            
            # Nigerian content count
            nigerian_count = conn.execute("""
                SELECT COUNT(*) FROM feedback_items
                WHERE category = ? AND cultural_relevance > 0.5
            """, (category,)).fetchone()[0]
            
            # Recent items (last 24 hours)
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            recent = conn.execute("""
                SELECT COUNT(*) FROM feedback_items
                WHERE category = ? AND created_at > ?
            """, (category, yesterday)).fetchone()[0]
            
            return {
                "category": category,
                "total_feedback": total,
                "training_ready": training_ready,
                "avg_quality": avg_quality,
                "nigerian_content_count": nigerian_count,
                "recent_24h": recent
            }


# ═══════════════════════════════════════════════════════════════════════════════
# TRIGGER EVALUATOR
# ═══════════════════════════════════════════════════════════════════════════════

class TriggerEvaluator:
    """Evaluate whether retraining should be triggered."""
    
    def __init__(self, 
                 config: TriggerConfig,
                 trigger_db: TriggerDatabase,
                 feedback_stats: FeedbackStatsCollector):
        self.config = config
        self.trigger_db = trigger_db
        self.feedback_stats = feedback_stats
    
    def evaluate(self, category: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluate whether training should be triggered for category.
        
        Args:
            category: Category to evaluate (voice, video, image)
            
        Returns:
            Tuple of (should_trigger, reason, evaluation_details)
        """
        # Collect current stats
        stats = self.feedback_stats.get_stats_for_category(category)
        
        # Get last training info
        last_training = self.trigger_db.get_last_training(category)
        
        # Calculate hours since last training
        hours_since_last = None
        if last_training and last_training.get("started_at"):
            last_time = datetime.fromisoformat(last_training["started_at"])
            hours_since_last = (datetime.utcnow() - last_time).total_seconds() / 3600
        
        evaluation = {
            "category": category,
            "should_trigger": False,
            "reason": None,
            "feedback_count": stats["total_feedback"],
            "training_ready_count": stats["training_ready"],
            "avg_quality": stats["avg_quality"],
            "nigerian_content_count": stats["nigerian_content_count"],
            "hours_since_last_training": hours_since_last,
            "daily_cost_so_far": self.trigger_db.get_daily_cost()
        }
        
        # Check daily cost limit
        if evaluation["daily_cost_so_far"] >= self.config.max_daily_training_cost_usd:
            evaluation["reason"] = "daily_cost_limit_reached"
            self.trigger_db.record_evaluation(evaluation)
            return False, "daily_cost_limit_reached", evaluation
        
        # Check minimum time between trainings
        if hours_since_last is not None:
            if hours_since_last < self.config.min_hours_between_training:
                evaluation["reason"] = "too_soon_after_last_training"
                self.trigger_db.record_evaluation(evaluation)
                return False, "too_soon_after_last_training", evaluation
        
        # Category-specific config
        cat_config = self.config.category_configs.get(category, {})
        min_items = cat_config.get("min_items", self.config.min_training_ready_items)
        
        # Check if enough training-ready items
        if stats["training_ready"] >= min_items:
            evaluation["should_trigger"] = True
            evaluation["reason"] = "sufficient_training_data"
            self.trigger_db.record_evaluation(evaluation)
            return True, TriggerReason.FEEDBACK_VOLUME.value, evaluation
        
        # Check Nigerian content bonus
        if stats["nigerian_content_count"] >= self.config.nigerian_bonus_threshold:
            effective_items = int(
                stats["training_ready"] * self.config.nigerian_content_weight
            )
            if effective_items >= min_items:
                evaluation["should_trigger"] = True
                evaluation["reason"] = "nigerian_content_bonus"
                self.trigger_db.record_evaluation(evaluation)
                return True, TriggerReason.NIGERIAN_CONTENT_BOOST.value, evaluation
        
        # Check if too long since last training (forced refresh)
        if hours_since_last is not None:
            if hours_since_last >= self.config.max_days_since_last_training * 24:
                if stats["training_ready"] >= min_items // 2:  # Relaxed threshold
                    evaluation["should_trigger"] = True
                    evaluation["reason"] = "scheduled_refresh"
                    self.trigger_db.record_evaluation(evaluation)
                    return True, TriggerReason.SCHEDULED.value, evaluation
        
        evaluation["reason"] = "thresholds_not_met"
        self.trigger_db.record_evaluation(evaluation)
        return False, "thresholds_not_met", evaluation
    
    def evaluate_all(self) -> Dict[str, Dict[str, Any]]:
        """Evaluate all categories."""
        results = {}
        
        for category in ["voice", "video", "image"]:
            should_trigger, reason, details = self.evaluate(category)
            results[category] = {
                "should_trigger": should_trigger,
                "reason": reason,
                "details": details
            }
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING SCHEDULER
# ═══════════════════════════════════════════════════════════════════════════════

class TrainingScheduler:
    """
    Scheduler for triggering Modal training jobs.
    
    Integrates with the feedback loop to automatically trigger retraining
    when conditions are met.
    """
    
    def __init__(self,
                 config: Optional[TriggerConfig] = None,
                 trigger_db_path: str = "trigger_history.db",
                 feedback_db_path: str = "feedback_data.db"):
        self.config = config or TriggerConfig()
        self.trigger_db = TriggerDatabase(trigger_db_path)
        self.feedback_stats = FeedbackStatsCollector(feedback_db_path)
        self.evaluator = TriggerEvaluator(
            self.config, self.trigger_db, self.feedback_stats
        )
        
        # GitHub Actions integration
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPOSITORY", "")
    
    async def check_and_trigger(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Check conditions and trigger training if appropriate.
        
        Args:
            category: Specific category to check, or None for all
            
        Returns:
            Trigger results
        """
        if category:
            categories = [category]
        else:
            categories = ["voice", "video", "image"]
        
        results = {"triggered": [], "skipped": []}
        
        for cat in categories:
            should_trigger, reason, details = self.evaluator.evaluate(cat)
            
            if should_trigger:
                try:
                    run_id = await self._trigger_training(cat, reason, details)
                    results["triggered"].append({
                        "category": cat,
                        "run_id": run_id,
                        "reason": reason
                    })
                    logger.info(f"🚀 Triggered training for {cat}: {run_id}")
                except Exception as e:
                    logger.error(f"Failed to trigger training for {cat}: {e}")
                    results["skipped"].append({
                        "category": cat,
                        "reason": f"trigger_error: {str(e)}"
                    })
            else:
                results["skipped"].append({
                    "category": cat,
                    "reason": reason
                })
        
        return results
    
    async def _trigger_training(self,
                                 category: str,
                                 reason: str,
                                 details: Dict[str, Any]) -> str:
        """Trigger actual training job."""
        # Generate run ID
        run_id = f"{category}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Estimate cost
        cat_config = self.config.category_configs.get(category, {})
        max_hours = cat_config.get("max_training_hours", 2)
        cost_per_hour = self.config.estimated_cost_per_hour.get(category, 3.0)
        estimated_cost = max_hours * cost_per_hour
        
        # Record training run
        self.trigger_db.record_training_run(
            run_id=run_id,
            category=category,
            trigger_reason=TriggerReason(reason) if reason in [e.value for e in TriggerReason] else TriggerReason.MANUAL,
            samples_used=details.get("training_ready_count", 0),
            estimated_cost=estimated_cost
        )
        
        # Trigger GitHub Actions workflow (if configured)
        if self.github_token and self.github_repo:
            await self._trigger_github_workflow(category, run_id, details)
        
        return run_id
    
    async def _trigger_github_workflow(self,
                                        category: str,
                                        run_id: str,
                                        details: Dict[str, Any]) -> None:
        """Trigger GitHub Actions workflow for training."""
        if not self.github_token:
            logger.warning("GitHub token not configured, skipping workflow trigger")
            return
        
        owner, repo = self.github_repo.split("/")
        
        payload = {
            "event_type": "training_triggered",
            "client_payload": {
                "category": category,
                "run_id": run_id,
                "training_ready_count": details.get("training_ready_count", 0),
                "avg_quality": details.get("avg_quality", 0),
                "trigger_source": "feedback_loop_scheduler"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{owner}/{repo}/dispatches",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Triggered GitHub workflow for {category}")
            else:
                logger.warning(f"GitHub workflow trigger returned {response.status_code}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        evaluations = self.evaluator.evaluate_all()
        history = self.trigger_db.get_training_history(limit=10)
        daily_cost = self.trigger_db.get_daily_cost()
        
        return {
            "evaluations": evaluations,
            "recent_training": history,
            "daily_cost_usd": daily_cost,
            "daily_cost_limit_usd": self.config.max_daily_training_cost_usd,
            "cost_remaining_usd": max(0, self.config.max_daily_training_cost_usd - daily_cost)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Retraining Scheduler")
    parser.add_argument("--action", choices=["check", "trigger", "status", "history"],
                        default="status", help="Action to perform")
    parser.add_argument("--category", type=str, help="Specific category")
    
    args = parser.parse_args()
    
    scheduler = TrainingScheduler()
    
    if args.action == "status":
        status = scheduler.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.action == "check":
        if args.category:
            should_trigger, reason, details = scheduler.evaluator.evaluate(args.category)
            print(f"Category: {args.category}")
            print(f"Should Trigger: {should_trigger}")
            print(f"Reason: {reason}")
            print(json.dumps(details, indent=2, default=str))
        else:
            results = scheduler.evaluator.evaluate_all()
            print(json.dumps(results, indent=2, default=str))
    
    elif args.action == "trigger":
        async def run():
            results = await scheduler.check_and_trigger(args.category)
            print(json.dumps(results, indent=2))
        
        asyncio.run(run())
    
    elif args.action == "history":
        history = scheduler.trigger_db.get_training_history(args.category)
        print(json.dumps(history, indent=2))


if __name__ == "__main__":
    main()
