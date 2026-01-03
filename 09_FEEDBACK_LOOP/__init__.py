"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA FEEDBACK LOOP
═══════════════════════════════════════════════════════════════════════════════
Complete Replicate → Modal training feedback loop.

Modules:
- orchestrator: Main orchestration
- replicate_client: State-of-the-art Replicate integration
- webhook_service: FastAPI webhook receiver
- data_processor: Feedback collection and curation
- retraining_triggers: Modal training integration

Usage:
    from feedback_loop import FeedbackLoopOrchestrator
    
    orchestrator = FeedbackLoopOrchestrator()
    await orchestrator.run_full_cycle()
═══════════════════════════════════════════════════════════════════════════════
"""

from pathlib import Path
import sys

# Add module paths
_module_path = Path(__file__).parent
sys.path.insert(0, str(_module_path))

# Version
__version__ = "1.0.0"

# Lazy imports for main components
def get_orchestrator():
    """Get the feedback loop orchestrator."""
    from .orchestrator import FeedbackLoopOrchestrator
    return FeedbackLoopOrchestrator()

def get_replicate_client():
    """Get the Sisi Lola Replicate client."""
    from .replicate_client.sisi_lola_replicate import SisiLolaReplicate
    return SisiLolaReplicate()

def get_collector():
    """Get the feedback collector service."""
    from .data_processor.collector import FeedbackCollectorService
    return FeedbackCollectorService()

def get_curator():
    """Get the feedback curator."""
    from .data_processor.curator import FeedbackCurator, FeedbackDatabase
    db = FeedbackDatabase()
    return FeedbackCurator(db)

def get_scheduler():
    """Get the training scheduler."""
    from .retraining_triggers.scheduler import TrainingScheduler
    return TrainingScheduler()

# Expose key classes for direct import
__all__ = [
    "get_orchestrator",
    "get_replicate_client", 
    "get_collector",
    "get_curator",
    "get_scheduler",
    "__version__"
]
