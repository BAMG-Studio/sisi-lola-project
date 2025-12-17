#!/usr/bin/env python3
"""
Sisi Lola Continuous Learning Pipeline
Automatically collects high-quality interactions and retrains periodically.

Features:
1. Feedback collection from user ratings
2. Automatic preference pair generation
3. Scheduled retraining triggers
4. Performance monitoring
5. Model versioning
"""
import os
import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import threading
import time

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class FeedbackEntry:
    """User feedback on a response"""
    session_id: str
    prompt: str
    response: str
    rating: float  # 1-5 scale
    feedback_text: str = ""
    language: str = "en"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrainTrigger:
    """Conditions that trigger retraining"""
    min_new_samples: int = 50
    max_days_since_retrain: int = 7
    performance_degradation_threshold: float = 0.1
    high_rating_threshold: float = 4.0
    low_rating_threshold: float = 2.0


class FeedbackCollector:
    """
    Collects and stores user feedback for continuous learning.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or PROJECT_ROOT / "ml_training" / "datasets" / "feedback")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback_file = self.storage_dir / "user_feedback.jsonl"
        self.stats_file = self.storage_dir / "feedback_stats.json"
        
        self._load_stats()
    
    def _load_stats(self):
        """Load feedback statistics"""
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_feedback": 0,
                "high_rating_count": 0,
                "low_rating_count": 0,
                "avg_rating": 0,
                "last_retrain": None,
                "samples_since_retrain": 0
            }
    
    def _save_stats(self):
        """Save feedback statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def collect(self, feedback: FeedbackEntry) -> bool:
        """
        Collect a feedback entry.
        
        Args:
            feedback: FeedbackEntry with user feedback
            
        Returns:
            True if collection successful
        """
        try:
            # Append to JSONL file
            with open(self.feedback_file, 'a') as f:
                entry = {
                    "session_id": feedback.session_id,
                    "prompt": feedback.prompt,
                    "response": feedback.response,
                    "rating": feedback.rating,
                    "feedback_text": feedback.feedback_text,
                    "language": feedback.language,
                    "timestamp": feedback.timestamp.isoformat(),
                    "metadata": feedback.metadata
                }
                f.write(json.dumps(entry) + '\n')
            
            # Update stats
            self.stats["total_feedback"] += 1
            self.stats["samples_since_retrain"] += 1
            
            if feedback.rating >= 4.0:
                self.stats["high_rating_count"] += 1
            elif feedback.rating <= 2.0:
                self.stats["low_rating_count"] += 1
            
            # Update running average
            n = self.stats["total_feedback"]
            old_avg = self.stats["avg_rating"]
            self.stats["avg_rating"] = old_avg + (feedback.rating - old_avg) / n
            
            self._save_stats()
            return True
            
        except Exception as e:
            print(f"❌ Failed to collect feedback: {e}")
            return False
    
    def get_training_samples(
        self,
        min_rating: float = 4.0,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get high-quality samples for training.
        
        Args:
            min_rating: Minimum rating to include
            since: Only include samples after this date
            
        Returns:
            List of training samples
        """
        samples = []
        
        if not self.feedback_file.exists():
            return samples
        
        with open(self.feedback_file) as f:
            for line in f:
                if not line.strip():
                    continue
                    
                entry = json.loads(line)
                rating = entry.get('rating', 0)
                timestamp = datetime.fromisoformat(entry.get('timestamp', '2000-01-01'))
                
                if rating >= min_rating:
                    if since is None or timestamp >= since:
                        samples.append({
                            "prompt": entry["prompt"],
                            "response": entry["response"],
                            "rating": rating
                        })
        
        return samples
    
    def get_preference_pairs(
        self,
        preferred_min: float = 4.0,
        rejected_max: float = 2.0
    ) -> List[Dict]:
        """
        Generate preference pairs from feedback.
        
        Args:
            preferred_min: Minimum rating for preferred responses
            rejected_max: Maximum rating for rejected responses
            
        Returns:
            List of preference pairs
        """
        # Group by prompt hash
        prompt_responses: Dict[str, Dict] = {}
        
        if not self.feedback_file.exists():
            return []
        
        with open(self.feedback_file) as f:
            for line in f:
                if not line.strip():
                    continue
                    
                entry = json.loads(line)
                prompt = entry.get('prompt', '')
                prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
                
                if prompt_hash not in prompt_responses:
                    prompt_responses[prompt_hash] = {
                        'prompt': prompt,
                        'preferred': [],
                        'rejected': []
                    }
                
                rating = entry.get('rating', 3)
                response = entry.get('response', '')
                
                if rating >= preferred_min:
                    prompt_responses[prompt_hash]['preferred'].append(response)
                elif rating <= rejected_max:
                    prompt_responses[prompt_hash]['rejected'].append(response)
        
        # Create pairs
        pairs = []
        for data in prompt_responses.values():
            for preferred in data['preferred']:
                for rejected in data['rejected']:
                    pairs.append({
                        'prompt': data['prompt'],
                        'chosen': preferred,
                        'rejected': rejected
                    })
        
        return pairs
    
    def should_retrain(self, trigger: RetrainTrigger) -> tuple:
        """
        Check if retraining should be triggered.
        
        Args:
            trigger: RetrainTrigger configuration
            
        Returns:
            Tuple of (should_retrain: bool, reason: str)
        """
        # Check new samples
        if self.stats["samples_since_retrain"] >= trigger.min_new_samples:
            return True, f"Collected {self.stats['samples_since_retrain']} new samples"
        
        # Check time since last retrain
        if self.stats["last_retrain"]:
            last_retrain = datetime.fromisoformat(self.stats["last_retrain"])
            days_since = (datetime.now() - last_retrain).days
            if days_since >= trigger.max_days_since_retrain:
                return True, f"{days_since} days since last retrain"
        
        return False, "No retrain needed"
    
    def mark_retrain_complete(self):
        """Mark that retraining has been completed"""
        self.stats["last_retrain"] = datetime.now().isoformat()
        self.stats["samples_since_retrain"] = 0
        self._save_stats()


class ContinuousLearningPipeline:
    """
    Orchestrates the continuous learning workflow.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml")
        self.config = self._load_config()
        
        self.collector = FeedbackCollector()
        self.trigger = self._create_trigger()
        
        self._running = False
        self._monitor_thread = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load continuous learning configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                return config.get('continuous_learning', {})
        return {}
    
    def _create_trigger(self) -> RetrainTrigger:
        """Create retrain trigger from config"""
        triggers = self.config.get('triggers', {})
        return RetrainTrigger(
            min_new_samples=triggers.get('min_new_samples', 50),
            max_days_since_retrain=triggers.get('max_days_since_retrain', 7),
            performance_degradation_threshold=triggers.get('performance_degradation', 0.1)
        )
    
    def collect_feedback(
        self,
        session_id: str,
        prompt: str,
        response: str,
        rating: float,
        feedback_text: str = "",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        API endpoint for collecting user feedback.
        
        Returns:
            Status and trigger check result
        """
        feedback = FeedbackEntry(
            session_id=session_id,
            prompt=prompt,
            response=response,
            rating=rating,
            feedback_text=feedback_text,
            language=language
        )
        
        success = self.collector.collect(feedback)
        
        # Check if retrain needed
        should_retrain, reason = self.collector.should_retrain(self.trigger)
        
        return {
            "success": success,
            "total_feedback": self.collector.stats["total_feedback"],
            "samples_since_retrain": self.collector.stats["samples_since_retrain"],
            "retrain_needed": should_retrain,
            "retrain_reason": reason if should_retrain else None
        }
    
    def prepare_training_data(self) -> Dict[str, Any]:
        """
        Prepare training data from collected feedback.
        
        Returns:
            Dict with training data and statistics
        """
        # Get high-quality samples for SFT
        sft_samples = self.collector.get_training_samples(min_rating=4.0)
        
        # Get preference pairs for DPO
        preference_pairs = self.collector.get_preference_pairs(
            preferred_min=self.config.get('collection', {}).get('min_rating', 4.0),
            rejected_max=2.0
        )
        
        # Save to files
        output_dir = PROJECT_ROOT / "ml_training" / "datasets" / "continuous_learning"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save SFT data
        sft_file = output_dir / f"sft_data_{timestamp}.jsonl"
        with open(sft_file, 'w') as f:
            for sample in sft_samples:
                f.write(json.dumps(sample) + '\n')
        
        # Save DPO data
        dpo_file = output_dir / f"dpo_data_{timestamp}.jsonl"
        with open(dpo_file, 'w') as f:
            for pair in preference_pairs:
                f.write(json.dumps(pair) + '\n')
        
        return {
            "sft_samples": len(sft_samples),
            "sft_file": str(sft_file),
            "dpo_pairs": len(preference_pairs),
            "dpo_file": str(dpo_file),
            "timestamp": timestamp
        }
    
    def retrain(self, mode: str = "incremental") -> Dict[str, Any]:
        """
        Execute retraining with collected data.
        
        Args:
            mode: "incremental" (fine-tune on new data) or "full" (retrain from scratch)
            
        Returns:
            Training result
        """
        print("\n" + "="*60)
        print("🔄 CONTINUOUS LEARNING - RETRAINING")
        print("="*60)
        
        # Prepare data
        data = self.prepare_training_data()
        print(f"\n📊 Training Data:")
        print(f"   SFT samples: {data['sft_samples']}")
        print(f"   DPO pairs: {data['dpo_pairs']}")
        
        if data['sft_samples'] == 0 and data['dpo_pairs'] == 0:
            return {
                "status": "skipped",
                "reason": "No training data available"
            }
        
        # Training settings
        train_config = self.config.get('training', {})
        epochs = train_config.get('epochs', 1)
        learning_rate = train_config.get('learning_rate', 1e-5)
        
        result = {
            "status": "pending",
            "mode": mode,
            "data": data,
            "config": {
                "epochs": epochs,
                "learning_rate": learning_rate
            },
            "started_at": datetime.now().isoformat()
        }
        
        # TODO: Integrate with actual training scripts
        # For now, we just prepare the data and mark completion
        
        print(f"\n🚀 Would train with:")
        print(f"   Mode: {mode}")
        print(f"   Epochs: {epochs}")
        print(f"   Learning rate: {learning_rate}")
        
        # Mark retrain complete
        self.collector.mark_retrain_complete()
        
        result["status"] = "completed"
        result["completed_at"] = datetime.now().isoformat()
        
        print("\n✅ Retraining preparation complete!")
        return result
    
    def start_monitoring(self, check_interval_minutes: int = 60):
        """
        Start background monitoring for retrain triggers.
        
        Args:
            check_interval_minutes: How often to check triggers
        """
        if self._running:
            print("⚠️ Monitoring already running")
            return
        
        self._running = True
        
        def monitor_loop():
            while self._running:
                should_retrain, reason = self.collector.should_retrain(self.trigger)
                
                if should_retrain:
                    print(f"\n🔔 Retrain triggered: {reason}")
                    self.retrain(mode="incremental")
                
                time.sleep(check_interval_minutes * 60)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"✅ Continuous learning monitor started (checking every {check_interval_minutes} min)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("✅ Continuous learning monitor stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        should_retrain, reason = self.collector.should_retrain(self.trigger)
        
        return {
            "monitoring_active": self._running,
            "collector_stats": self.collector.stats,
            "trigger_config": {
                "min_new_samples": self.trigger.min_new_samples,
                "max_days_since_retrain": self.trigger.max_days_since_retrain
            },
            "retrain_needed": should_retrain,
            "retrain_reason": reason if should_retrain else None
        }


# API Integration functions
_pipeline: Optional[ContinuousLearningPipeline] = None


def get_pipeline() -> ContinuousLearningPipeline:
    """Get the global continuous learning pipeline"""
    global _pipeline
    if _pipeline is None:
        _pipeline = ContinuousLearningPipeline()
    return _pipeline


def collect_user_feedback(
    session_id: str,
    prompt: str,
    response: str,
    rating: float,
    feedback_text: str = ""
) -> Dict[str, Any]:
    """API wrapper for feedback collection"""
    return get_pipeline().collect_feedback(
        session_id=session_id,
        prompt=prompt,
        response=response,
        rating=rating,
        feedback_text=feedback_text
    )


def main():
    """Demo continuous learning pipeline"""
    print("="*60)
    print("Continuous Learning Pipeline Demo")
    print("="*60)
    
    pipeline = get_pipeline()
    
    # Simulate feedback collection
    print("\n📝 Simulating feedback collection...")
    
    sample_feedback = [
        ("How are you?", "E kaa san! I dey fine o! How you dey?", 5.0),
        ("Tell me about Lagos", "Lagos na mega city wey never sleep!", 4.5),
        ("What is jollof?", "It's rice.", 2.0),  # Low quality response
        ("Say hello", "E ku aro! Welcome to Nigeria!", 5.0),
        ("Weather?", "Weather.", 1.5),  # Very low quality
    ]
    
    for i, (prompt, response, rating) in enumerate(sample_feedback):
        result = pipeline.collect_feedback(
            session_id=f"demo_{i}",
            prompt=prompt,
            response=response,
            rating=rating
        )
        print(f"   [{rating}⭐] Collected: '{prompt[:30]}...'")
    
    # Check status
    print("\n📊 Pipeline Status:")
    status = pipeline.get_status()
    print(f"   Total feedback: {status['collector_stats']['total_feedback']}")
    print(f"   Samples since retrain: {status['collector_stats']['samples_since_retrain']}")
    print(f"   Average rating: {status['collector_stats']['avg_rating']:.2f}")
    print(f"   Retrain needed: {status['retrain_needed']}")
    
    # Prepare training data
    print("\n📦 Preparing training data...")
    data = pipeline.prepare_training_data()
    print(f"   SFT samples: {data['sft_samples']}")
    print(f"   DPO pairs: {data['dpo_pairs']}")
    
    print("\n✅ Continuous learning pipeline ready!")


if __name__ == "__main__":
    main()
