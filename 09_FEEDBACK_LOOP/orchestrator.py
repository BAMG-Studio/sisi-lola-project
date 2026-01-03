#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA FEEDBACK LOOP ORCHESTRATOR
═══════════════════════════════════════════════════════════════════════════════

              ╔═══════════════════════════════════════════════════════╗
              ║     REPLICATE → MODAL FEEDBACK LOOP ARCHITECTURE      ║
              ╚═══════════════════════════════════════════════════════╝

    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │   REPLICATE     │         │  FEEDBACK LOOP  │         │     MODAL       │
    │   (Inference)   │ ──────► │   (This File)   │ ──────► │   (Training)    │
    │                 │         │                 │         │                 │
    │  🧠 Brain       │         │  📥 Collector   │         │  🏋️ Voice       │
    │  👁️ Eyes        │ Webhook │  🔍 Curator     │ Trigger │  🎬 Video       │
    │  🗣️ Voice       │ ──────► │  📊 Quality     │ ──────► │  🖼️ Image       │
    │  🎬 Video       │         │  🚀 Trigger     │         │  📝 Text        │
    │  💜 Heart       │         │  📈 Monitor     │         │                 │
    └─────────────────┘         └─────────────────┘         └─────────────────┘
           │                           │                           │
           └───────────────────────────┼───────────────────────────┘
                                       │
                               ┌───────▼───────┐
                               │  🇳🇬 Nigerian  │
                               │   Content     │
                               │   Priority    │
                               └───────────────┘

This orchestrator:
1. Receives webhooks from Replicate predictions
2. Collects and curates feedback
3. Applies Nigerian content bonuses
4. Triggers Modal retraining when thresholds are met
5. Monitors the entire pipeline

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import yaml
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add project paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("FeedbackLoopOrchestrator")


# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS (with graceful fallbacks)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from data_processor.collector import (
        FeedbackCollectorService, 
        FeedbackCategory,
        FeedbackItem
    )
    COLLECTOR_AVAILABLE = True
except ImportError:
    COLLECTOR_AVAILABLE = False
    logger.warning("Collector module not available")

try:
    from data_processor.curator import (
        FeedbackCurator,
        FeedbackDatabase,
        CurationConfig,
        TrainingDataExporter
    )
    CURATOR_AVAILABLE = True
except ImportError:
    CURATOR_AVAILABLE = False
    logger.warning("Curator module not available")

try:
    from retraining_triggers.scheduler import (
        TrainingScheduler,
        TriggerConfig
    )
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    logger.warning("Scheduler module not available")

try:
    from replicate_client.sisi_lola_replicate import (
        SisiLolaReplicate,
        Modality
    )
    REPLICATE_CLIENT_AVAILABLE = True
except ImportError:
    REPLICATE_CLIENT_AVAILABLE = False
    logger.warning("Replicate client not available")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / "config" / "feedback_config.yaml"
    
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    logger.warning("Config file not found, using defaults")
    return {}


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK LOOP ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackLoopOrchestrator:
    """
    Main orchestrator for the Replicate → Modal feedback loop.
    
    This is the central hub that coordinates:
    - Feedback collection from multiple sources
    - Quality filtering and curation
    - Training trigger evaluation
    - Modal job submission
    
    Usage:
        orchestrator = FeedbackLoopOrchestrator()
        
        # Process incoming webhook
        await orchestrator.process_webhook(payload)
        
        # Run curation cycle
        await orchestrator.run_curation_cycle()
        
        # Check and trigger training
        await orchestrator.check_training_triggers()
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Optional configuration override
        """
        self.config = config or load_config()
        
        # Initialize components
        self._init_collector()
        self._init_curator()
        self._init_scheduler()
        self._init_replicate_client()
        
        logger.info("🔄 Feedback Loop Orchestrator initialized")
        self._log_component_status()
    
    def _init_collector(self):
        """Initialize feedback collector."""
        if COLLECTOR_AVAILABLE:
            db_path = self.config.get("general", {}).get("databases", {}).get(
                "feedback", "feedback_data.db"
            )
            self.collector = FeedbackCollectorService(db_path)
        else:
            self.collector = None
    
    def _init_curator(self):
        """Initialize feedback curator."""
        if CURATOR_AVAILABLE:
            db_path = self.config.get("general", {}).get("databases", {}).get(
                "feedback", "feedback_data.db"
            )
            
            # Create curation config from YAML
            filter_config = self.config.get("quality_filter", {})
            
            curation_config = CurationConfig(
                min_quality_score=filter_config.get("min_quality_score", 0.6),
                training_quality_threshold=filter_config.get(
                    "training_quality_threshold", 0.75
                ),
                nigerian_content_bonus=filter_config.get("nigerian", {}).get(
                    "bonus_score", 0.15
                )
            )
            
            db = FeedbackDatabase(db_path)
            self.curator = FeedbackCurator(db, curation_config)
            self.exporter = TrainingDataExporter(db)
        else:
            self.curator = None
            self.exporter = None
    
    def _init_scheduler(self):
        """Initialize training scheduler."""
        if SCHEDULER_AVAILABLE:
            trigger_db_path = self.config.get("general", {}).get("databases", {}).get(
                "triggers", "trigger_history.db"
            )
            feedback_db_path = self.config.get("general", {}).get("databases", {}).get(
                "feedback", "feedback_data.db"
            )
            
            # Create trigger config from YAML
            retraining_config = self.config.get("retraining", {})
            
            trigger_config = TriggerConfig(
                min_feedback_items=retraining_config.get("thresholds", {}).get(
                    "min_feedback_items", 100
                ),
                min_training_ready_items=retraining_config.get("thresholds", {}).get(
                    "min_training_ready_items", 50
                ),
                min_hours_between_training=retraining_config.get("timing", {}).get(
                    "min_hours_between_training", 24
                ),
                max_daily_training_cost_usd=retraining_config.get("cost", {}).get(
                    "max_daily_usd", 50.0
                )
            )
            
            self.scheduler = TrainingScheduler(
                config=trigger_config,
                trigger_db_path=trigger_db_path,
                feedback_db_path=feedback_db_path
            )
        else:
            self.scheduler = None
    
    def _init_replicate_client(self):
        """Initialize Replicate client."""
        if REPLICATE_CLIENT_AVAILABLE:
            try:
                webhook_config = self.config.get("replicate", {}).get("webhook", {})
                webhook_url = os.getenv("REPLICATE_WEBHOOK_URL")
                
                self.replicate = SisiLolaReplicate(webhook_url=webhook_url)
            except Exception as e:
                logger.warning(f"Replicate client init failed: {e}")
                self.replicate = None
        else:
            self.replicate = None
    
    def _log_component_status(self):
        """Log status of all components."""
        components = {
            "Collector": self.collector is not None,
            "Curator": self.curator is not None,
            "Scheduler": self.scheduler is not None,
            "Replicate": self.replicate is not None
        }
        
        for name, available in components.items():
            status = "✅" if available else "❌"
            logger.info(f"  {status} {name}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WEBHOOK PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming Replicate webhook.
        
        This is called when Replicate sends a prediction completion webhook.
        
        Args:
            payload: Webhook payload from Replicate
            
        Returns:
            Processing result
        """
        if not self.collector:
            return {"error": "Collector not available"}
        
        logger.info(f"📥 Processing webhook: {payload.get('id', 'unknown')}")
        
        try:
            # Collect the feedback
            item = self.collector.collect_webhook(payload)
            
            if item:
                logger.info(f"✅ Collected: {item.id}")
                
                # Immediately curate if curator available
                if self.curator:
                    is_valid, quality, reasons = self.curator.curate_item(item)
                    
                    return {
                        "status": "processed",
                        "item_id": item.id,
                        "quality_score": quality,
                        "is_valid": is_valid,
                        "training_ready": item.is_training_ready
                    }
                
                return {
                    "status": "collected",
                    "item_id": item.id
                }
            
            return {"status": "skipped", "reason": "invalid_payload"}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CURATION CYCLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def run_curation_cycle(self, limit: int = 100) -> Dict[str, Any]:
        """
        Run a curation cycle on pending feedback.
        
        This processes unprocessed feedback items through the quality filter.
        
        Args:
            limit: Maximum items to process
            
        Returns:
            Curation results
        """
        if not self.curator:
            return {"error": "Curator not available"}
        
        logger.info(f"🔍 Running curation cycle (limit: {limit})")
        
        results = self.curator.process_pending(limit=limit)
        
        logger.info(
            f"📊 Curated {results.get('total', 0)} items: "
            f"{results.get('accepted', 0)} accepted, "
            f"{results.get('training_ready', 0)} training-ready"
        )
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TRAINING TRIGGERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def check_training_triggers(self, 
                                       category: Optional[str] = None) -> Dict[str, Any]:
        """
        Check and trigger training if conditions are met.
        
        Args:
            category: Specific category to check, or None for all
            
        Returns:
            Trigger results
        """
        if not self.scheduler:
            return {"error": "Scheduler not available"}
        
        logger.info(f"🚀 Checking training triggers ({category or 'all'})")
        
        results = await self.scheduler.check_and_trigger(category)
        
        if results.get("triggered"):
            for t in results["triggered"]:
                logger.info(f"✅ Triggered training: {t['category']} ({t['run_id']})")
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DATA EXPORT
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def export_training_data(self, output_dir: str = "training_export") -> Dict[str, Any]:
        """
        Export curated data for training.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Export results
        """
        if not self.exporter:
            return {"error": "Exporter not available"}
        
        logger.info(f"📤 Exporting training data to {output_dir}")
        
        return self.exporter.export_all(Path(output_dir))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS AND MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the feedback loop."""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "collector": self.collector is not None,
                "curator": self.curator is not None,
                "scheduler": self.scheduler is not None,
                "replicate": self.replicate is not None
            }
        }
        
        # Get collector stats
        if self.collector:
            status["feedback_stats"] = self.collector.get_stats()
        
        # Get scheduler status
        if self.scheduler:
            status["training_status"] = self.scheduler.get_status()
        
        return status
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FULL CYCLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def run_full_cycle(self) -> Dict[str, Any]:
        """
        Run a full feedback loop cycle.
        
        This:
        1. Curates pending feedback
        2. Checks training triggers
        3. Exports data if needed
        
        Returns:
            Full cycle results
        """
        logger.info("🔄 Running full feedback loop cycle")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "curation": None,
            "triggers": None,
            "export": None
        }
        
        # Step 1: Curate pending feedback
        results["curation"] = await self.run_curation_cycle()
        
        # Step 2: Check training triggers
        results["triggers"] = await self.check_training_triggers()
        
        # Step 3: Export if training was triggered
        if results["triggers"].get("triggered"):
            results["export"] = await self.export_training_data()
        
        logger.info("✅ Full cycle complete")
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_orchestrator() -> FeedbackLoopOrchestrator:
    """Create and return a configured orchestrator."""
    return FeedbackLoopOrchestrator()


async def process_replicate_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Quick function to process a webhook."""
    orchestrator = create_orchestrator()
    return await orchestrator.process_webhook(payload)


async def run_feedback_cycle() -> Dict[str, Any]:
    """Quick function to run a feedback cycle."""
    orchestrator = create_orchestrator()
    return await orchestrator.run_full_cycle()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Feedback Loop Orchestrator")
    parser.add_argument("--action", choices=[
        "status", "curate", "trigger", "export", "cycle"
    ], default="status", help="Action to perform")
    parser.add_argument("--category", type=str, help="Specific category")
    parser.add_argument("--limit", type=int, default=100, help="Processing limit")
    parser.add_argument("--output", type=str, default="training_export", help="Export output")
    
    args = parser.parse_args()
    
    orchestrator = create_orchestrator()
    
    async def run_action():
        if args.action == "status":
            status = orchestrator.get_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.action == "curate":
            results = await orchestrator.run_curation_cycle(limit=args.limit)
            print(json.dumps(results, indent=2, default=str))
        
        elif args.action == "trigger":
            results = await orchestrator.check_training_triggers(args.category)
            print(json.dumps(results, indent=2, default=str))
        
        elif args.action == "export":
            results = await orchestrator.export_training_data(args.output)
            print(json.dumps(results, indent=2, default=str))
        
        elif args.action == "cycle":
            results = await orchestrator.run_full_cycle()
            print(json.dumps(results, indent=2, default=str))
    
    asyncio.run(run_action())


if __name__ == "__main__":
    main()
