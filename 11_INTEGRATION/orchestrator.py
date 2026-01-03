#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    SISI LOLA MASTER ORCHESTRATOR
═══════════════════════════════════════════════════════════════════════════════
         Unified Integration Layer for All System Components
═══════════════════════════════════════════════════════════════════════════════

This is the central nervous system that connects:
- 08_MLOPS_PIPELINE: Ingestion, preprocessing, training
- 09_FEEDBACK_LOOP: Replicate inference, Modal training, feedback collection
- 10_METADATA_SYSTEM: Asset tracking and lineage
- sisi_lola_chat: Streamlit dashboard

Key Features:
- Event-driven architecture
- Async task processing
- Nigerian content prioritization
- Cost management ($50/day limit)
- Unified logging and monitoring
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """System event types."""
    # Content events
    CONTENT_INGESTED = "content.ingested"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_GENERATED = "content.generated"
    
    # Training events
    TRAINING_TRIGGERED = "training.triggered"
    TRAINING_STARTED = "training.started"
    TRAINING_COMPLETED = "training.completed"
    TRAINING_FAILED = "training.failed"
    
    # Feedback events
    FEEDBACK_RECEIVED = "feedback.received"
    FEEDBACK_PROCESSED = "feedback.processed"
    
    # Inference events
    INFERENCE_REQUESTED = "inference.requested"
    INFERENCE_COMPLETED = "inference.completed"
    
    # System events
    COST_LIMIT_WARNING = "system.cost_warning"
    COST_LIMIT_EXCEEDED = "system.cost_exceeded"
    HEALTH_CHECK = "system.health_check"
    
    # Quality events
    QUALITY_THRESHOLD_MET = "quality.threshold_met"
    QUALITY_DEGRADATION = "quality.degradation"


@dataclass
class SystemEvent:
    """Represents a system event."""
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    correlation_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type.value,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'correlation_id': self.correlation_id
        }


class EventBus:
    """
    Simple event bus for component communication.
    """
    
    def __init__(self):
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.event_queue = queue.Queue()
        self.running = False
        self._worker_thread = None
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Handler registered for {event_type.value}")
    
    def publish(self, event: SystemEvent):
        """Publish an event."""
        self.event_queue.put(event)
        logger.debug(f"Event published: {event.event_type.value}")
    
    def start(self):
        """Start event processing."""
        self.running = True
        self._worker_thread = threading.Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
        logger.info("Event bus started")
    
    def stop(self):
        """Stop event processing."""
        self.running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("Event bus stopped")
    
    def _process_events(self):
        """Process events from queue."""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                self._dispatch_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    def _dispatch_event(self, event: SystemEvent):
        """Dispatch event to handlers."""
        handlers = self.handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type.value}: {e}")


class ComponentStatus(Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status for a component."""
    name: str
    status: ComponentStatus
    last_check: datetime
    latency_ms: float = 0
    error_message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)


class SisiLolaOrchestrator:
    """
    Master orchestrator for the Sisi Lola system.
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.event_bus = EventBus()
        
        # Component references (lazy loaded)
        self._metadata_store = None
        self._data_catalog = None
        self._lineage_tracker = None
        self._replicate_client = None
        self._feedback_collector = None
        self._training_scheduler = None
        
        # State
        self.component_health: Dict[str, ComponentHealth] = {}
        self.daily_cost = 0.0
        self.cost_limit = self.config.get('daily_cost_limit', 50.0)
        
        # Nigerian content tracking
        self.nigerian_content_ratio = 0.0
        self.nigerian_bonus_multiplier = 1.5
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration."""
        default_config = {
            'daily_cost_limit': 50.0,
            'nigerian_bonus': 1.5,
            'quality_threshold': 0.7,
            'training_trigger_samples': 1000,
            'replicate_token': os.getenv('REPLICATE_API_TOKEN'),
            'modal_workspace': os.getenv('MODAL_WORKSPACE', 'default'),
            'components': {
                'metadata_store': {
                    'db_path': 'data/metadata_store.db'
                },
                'feedback_loop': {
                    'db_path': 'data/feedback_data.db'
                },
                'training': {
                    'gpu_type': 'A100-40GB',
                    'max_concurrent_jobs': 2
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                import yaml
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_event_handlers(self):
        """Setup internal event handlers."""
        # Content events
        self.event_bus.subscribe(EventType.CONTENT_INGESTED, self._on_content_ingested)
        self.event_bus.subscribe(EventType.CONTENT_PROCESSED, self._on_content_processed)
        
        # Feedback events
        self.event_bus.subscribe(EventType.FEEDBACK_RECEIVED, self._on_feedback_received)
        
        # Training events
        self.event_bus.subscribe(EventType.TRAINING_COMPLETED, self._on_training_completed)
        
        # System events
        self.event_bus.subscribe(EventType.COST_LIMIT_WARNING, self._on_cost_warning)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Component Accessors (Lazy Loading)
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def metadata_store(self):
        """Get metadata store (lazy load)."""
        if self._metadata_store is None:
            try:
                from metadata_system import MetadataStore
                db_path = self.config['components']['metadata_store']['db_path']
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                self._metadata_store = MetadataStore(db_path)
            except ImportError:
                logger.warning("MetadataStore not available")
        return self._metadata_store
    
    @property
    def data_catalog(self):
        """Get data catalog (lazy load)."""
        if self._data_catalog is None and self.metadata_store:
            try:
                from metadata_system import DataCatalog
                self._data_catalog = DataCatalog(self.metadata_store)
            except ImportError:
                logger.warning("DataCatalog not available")
        return self._data_catalog
    
    @property
    def lineage_tracker(self):
        """Get lineage tracker (lazy load)."""
        if self._lineage_tracker is None:
            try:
                from metadata_system import LineageTracker
                self._lineage_tracker = LineageTracker("data/lineage")
            except ImportError:
                logger.warning("LineageTracker not available")
        return self._lineage_tracker
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Event Handlers
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _on_content_ingested(self, event: SystemEvent):
        """Handle content ingestion event."""
        payload = event.payload
        
        # Register in metadata store
        if self.metadata_store:
            from metadata_system import register_video, NigerianLanguage
            
            language = NigerianLanguage.ENGLISH
            if payload.get('is_nigerian'):
                lang_str = payload.get('language', 'english').lower()
                try:
                    language = NigerianLanguage(lang_str)
                except ValueError:
                    language = NigerianLanguage.MIXED
            
            asset_id = register_video(
                self.metadata_store,
                name=payload['title'],
                storage_path=payload['path'],
                duration_seconds=payload.get('duration', 0),
                size_bytes=payload.get('size', 0),
                language=language,
                source_url=payload.get('url')
            )
            
            logger.info(f"Registered ingested content: {asset_id}")
    
    def _on_content_processed(self, event: SystemEvent):
        """Handle content processing completion."""
        payload = event.payload
        
        # Record lineage
        if self.lineage_tracker:
            if payload.get('type') == 'audio_extraction':
                self.lineage_tracker.record_audio_extraction(
                    payload['source_id'],
                    payload['output_id']
                )
            elif payload.get('type') == 'transcription':
                self.lineage_tracker.record_transcription(
                    payload['source_id'],
                    payload['output_id'],
                    payload.get('model', 'whisper'),
                    payload.get('confidence', 0.9)
                )
    
    def _on_feedback_received(self, event: SystemEvent):
        """Handle feedback event."""
        payload = event.payload
        
        # Track cost
        cost = payload.get('cost', 0)
        self.daily_cost += cost
        
        # Check cost limit
        if self.daily_cost > self.cost_limit * 0.8:
            self.event_bus.publish(SystemEvent(
                event_type=EventType.COST_LIMIT_WARNING,
                payload={'current': self.daily_cost, 'limit': self.cost_limit},
                source='orchestrator'
            ))
        
        # Apply Nigerian bonus
        if payload.get('is_nigerian'):
            quality = payload.get('quality', 0)
            payload['adjusted_quality'] = quality * self.nigerian_bonus_multiplier
    
    def _on_training_completed(self, event: SystemEvent):
        """Handle training completion."""
        payload = event.payload
        
        # Record model provenance
        if self.lineage_tracker:
            self.lineage_tracker.record_training(
                dataset_ids=payload.get('dataset_ids', []),
                model_asset_id=payload['model_id'],
                model_name=payload['model_name'],
                model_type=payload.get('model_type', 'unknown'),
                training_config=payload.get('config', {}),
                metrics=payload.get('metrics', {}),
                nigerian_ratio=payload.get('nigerian_ratio', 0),
                dialects=payload.get('dialects', [])
            )
        
        logger.info(f"Training completed: {payload['model_name']}")
    
    def _on_cost_warning(self, event: SystemEvent):
        """Handle cost warning."""
        payload = event.payload
        logger.warning(f"Cost warning: ${payload['current']:.2f} / ${payload['limit']:.2f}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # High-Level Operations
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def ingest_content(
        self,
        url: str,
        content_type: str = "youtube"
    ) -> Dict[str, Any]:
        """
        Ingest content from a URL.
        """
        correlation_id = f"ingest_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        try:
            # Import ingestion module
            from mlops_pipeline.ingestion import youtube_scraper
            
            # Perform ingestion
            result = await youtube_scraper.ingest_video(url)
            
            # Publish event
            self.event_bus.publish(SystemEvent(
                event_type=EventType.CONTENT_INGESTED,
                payload=result,
                source='orchestrator',
                correlation_id=correlation_id
            ))
            
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def generate_content(
        self,
        modality: str,  # brain, voice, video, image
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content using Replicate models.
        """
        # Check cost limit
        if self.daily_cost >= self.cost_limit:
            return {'status': 'error', 'error': 'Daily cost limit exceeded'}
        
        correlation_id = f"gen_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        try:
            # Import replicate client
            from feedback_loop import SisiLolaReplicate
            
            client = SisiLolaReplicate()
            
            # Generate based on modality
            if modality == 'brain':
                result = await client.brain.think(prompt, **kwargs)
            elif modality == 'voice':
                result = await client.voice.speak(prompt, **kwargs)
            elif modality == 'video':
                result = await client.video.generate(prompt, **kwargs)
            elif modality == 'image':
                result = await client.eyes.see(prompt, **kwargs)
            else:
                return {'status': 'error', 'error': f'Unknown modality: {modality}'}
            
            # Track cost
            cost = result.get('cost', 0)
            self.daily_cost += cost
            
            # Publish event
            self.event_bus.publish(SystemEvent(
                event_type=EventType.CONTENT_GENERATED,
                payload={
                    'modality': modality,
                    'prompt': prompt,
                    'result': result,
                    'cost': cost
                },
                source='orchestrator',
                correlation_id=correlation_id
            ))
            
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def trigger_training(
        self,
        training_type: str,  # voice, vision, language
        dataset_ids: List[str] = None,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Trigger a training job on Modal.
        """
        # Check cost limit
        if self.daily_cost >= self.cost_limit * 0.9:
            return {'status': 'error', 'error': 'Cost limit nearly exceeded, training blocked'}
        
        correlation_id = f"train_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        try:
            # Publish trigger event
            self.event_bus.publish(SystemEvent(
                event_type=EventType.TRAINING_TRIGGERED,
                payload={
                    'training_type': training_type,
                    'dataset_ids': dataset_ids,
                    'config': config
                },
                source='orchestrator',
                correlation_id=correlation_id
            ))
            
            # Import training module
            from feedback_loop.retraining_triggers import ModalTrainingIntegration
            
            training = ModalTrainingIntegration()
            
            # Trigger based on type
            if training_type == 'voice':
                job_id = training.trigger_voice_training(dataset_ids, config)
            elif training_type == 'vision':
                job_id = training.trigger_vision_training(dataset_ids, config)
            elif training_type == 'language':
                job_id = training.trigger_language_training(dataset_ids, config)
            else:
                return {'status': 'error', 'error': f'Unknown training type: {training_type}'}
            
            return {'status': 'success', 'job_id': job_id}
            
        except Exception as e:
            logger.error(f"Training trigger failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Health Monitoring
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check health of a specific component."""
        start_time = datetime.now()
        
        try:
            if component_name == 'metadata_store':
                if self.metadata_store:
                    stats = self.metadata_store.get_statistics()
                    return ComponentHealth(
                        name=component_name,
                        status=ComponentStatus.HEALTHY,
                        last_check=datetime.now(),
                        latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                        metrics={'total_assets': sum(stats.get('by_type', {}).values())}
                    )
            
            elif component_name == 'event_bus':
                return ComponentHealth(
                    name=component_name,
                    status=ComponentStatus.HEALTHY if self.event_bus.running else ComponentStatus.UNHEALTHY,
                    last_check=datetime.now(),
                    latency_ms=0,
                    metrics={'queue_size': self.event_bus.event_queue.qsize()}
                )
            
        except Exception as e:
            return ComponentHealth(
                name=component_name,
                status=ComponentStatus.UNHEALTHY,
                last_check=datetime.now(),
                error_message=str(e)
            )
        
        return ComponentHealth(
            name=component_name,
            status=ComponentStatus.UNKNOWN,
            last_check=datetime.now()
        )
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        components = ['metadata_store', 'event_bus']
        
        health_status = {}
        for component in components:
            health = self.check_component_health(component)
            health_status[component] = {
                'status': health.status.value,
                'latency_ms': health.latency_ms,
                'error': health.error_message,
                'metrics': health.metrics
            }
        
        # Overall status
        all_healthy = all(h['status'] == 'healthy' for h in health_status.values())
        any_unhealthy = any(h['status'] == 'unhealthy' for h in health_status.values())
        
        if all_healthy:
            overall = 'healthy'
        elif any_unhealthy:
            overall = 'unhealthy'
        else:
            overall = 'degraded'
        
        return {
            'overall_status': overall,
            'components': health_status,
            'daily_cost': self.daily_cost,
            'cost_limit': self.cost_limit,
            'cost_utilization': (self.daily_cost / self.cost_limit) * 100,
            'timestamp': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Lifecycle Management
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start(self):
        """Start the orchestrator."""
        logger.info("Starting Sisi Lola Orchestrator...")
        
        # Start event bus
        self.event_bus.start()
        
        # Publish health check
        self.event_bus.publish(SystemEvent(
            event_type=EventType.HEALTH_CHECK,
            payload=self.get_system_health(),
            source='orchestrator'
        ))
        
        logger.info("Sisi Lola Orchestrator started")
    
    def stop(self):
        """Stop the orchestrator."""
        logger.info("Stopping Sisi Lola Orchestrator...")
        
        # Stop event bus
        self.event_bus.stop()
        
        logger.info("Sisi Lola Orchestrator stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = {
            'orchestrator': {
                'daily_cost': self.daily_cost,
                'cost_limit': self.cost_limit,
                'cost_remaining': self.cost_limit - self.daily_cost,
                'nigerian_bonus': self.nigerian_bonus_multiplier
            },
            'event_bus': {
                'queue_size': self.event_bus.event_queue.qsize(),
                'handler_count': sum(len(h) for h in self.event_bus.handlers.values())
            }
        }
        
        if self.metadata_store:
            stats['metadata'] = self.metadata_store.get_statistics()
        
        if self.data_catalog:
            stats['catalog'] = self.data_catalog.get_summary()
        
        return stats


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Orchestrator")
    parser.add_argument('--config', type=str, help='Config file path')
    parser.add_argument('--health', action='store_true', help='Show system health')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    orchestrator = SisiLolaOrchestrator(args.config)
    
    if args.health:
        health = orchestrator.get_system_health()
        print(json.dumps(health, indent=2))
    elif args.stats:
        stats = orchestrator.get_statistics()
        print(json.dumps(stats, indent=2, default=str))
    else:
        # Run orchestrator
        orchestrator.start()
        
        try:
            print("Sisi Lola Orchestrator running. Press Ctrl+C to stop.")
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop()


if __name__ == "__main__":
    main()
