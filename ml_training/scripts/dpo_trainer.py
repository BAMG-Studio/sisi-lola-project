#!/usr/bin/env python3
"""
Sisi Lola DPO (Direct Preference Optimization) Trainer
Aligns model outputs with human preferences for better responses.

DPO improves:
- Response quality and helpfulness
- Cultural authenticity
- Safety and alignment
- User satisfaction

Based on: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
"""
import os
import sys
import json
import yaml
import torch
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datasets import Dataset

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class PreferencePair:
    """A preference pair for DPO training"""
    prompt: str
    chosen: str  # Preferred response
    rejected: str  # Non-preferred response
    metadata: Dict[str, Any] = None


class DPODatasetBuilder:
    """
    Builds preference datasets from user feedback.
    
    Sources:
    1. Explicit ratings (4-5 stars = preferred, 1-2 = rejected)
    2. A/B test results
    3. Human annotation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml")
        self.config = self._load_config()
        self.preference_pairs: List[PreferencePair] = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load DPO configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                return config.get('dpo_config', {})
        return {}
    
    def add_from_ratings(
        self,
        feedback_file: str,
        min_preferred_rating: float = 4.0,
        max_rejected_rating: float = 2.0
    ) -> int:
        """
        Build preference pairs from user ratings.
        
        Args:
            feedback_file: Path to feedback JSONL file
            min_preferred_rating: Minimum rating for preferred responses
            max_rejected_rating: Maximum rating for rejected responses
            
        Returns:
            Number of pairs added
        """
        pairs_added = 0
        feedback_path = Path(feedback_file)
        
        if not feedback_path.exists():
            print(f"⚠️ Feedback file not found: {feedback_file}")
            return 0
        
        # Group by prompt
        prompt_responses: Dict[str, List[Tuple[str, float]]] = {}
        
        with open(feedback_path) as f:
            for line in f:
                if not line.strip():
                    continue
                    
                item = json.loads(line)
                prompt = item.get('prompt', '')
                response = item.get('response', '')
                rating = item.get('rating', 3.0)
                
                if prompt not in prompt_responses:
                    prompt_responses[prompt] = []
                prompt_responses[prompt].append((response, rating))
        
        # Create pairs
        for prompt, responses in prompt_responses.items():
            preferred = [r for r, rating in responses if rating >= min_preferred_rating]
            rejected = [r for r, rating in responses if rating <= max_rejected_rating]
            
            # Create all combinations
            for chosen in preferred:
                for rej in rejected:
                    self.preference_pairs.append(PreferencePair(
                        prompt=prompt,
                        chosen=chosen,
                        rejected=rej,
                        metadata={'source': 'user_ratings'}
                    ))
                    pairs_added += 1
        
        print(f"✅ Added {pairs_added} preference pairs from ratings")
        return pairs_added
    
    def add_from_ab_tests(self, ab_results_file: str) -> int:
        """
        Build preference pairs from A/B test results.
        
        Args:
            ab_results_file: Path to A/B test results JSONL
            
        Returns:
            Number of pairs added
        """
        pairs_added = 0
        results_path = Path(ab_results_file)
        
        if not results_path.exists():
            print(f"⚠️ A/B results file not found: {ab_results_file}")
            return 0
        
        with open(results_path) as f:
            for line in f:
                if not line.strip():
                    continue
                    
                item = json.loads(line)
                prompt = item.get('prompt', '')
                response_a = item.get('response_a', '')
                response_b = item.get('response_b', '')
                winner = item.get('winner', '')  # 'a' or 'b'
                
                if winner == 'a':
                    chosen, rejected = response_a, response_b
                elif winner == 'b':
                    chosen, rejected = response_b, response_a
                else:
                    continue  # Tie, skip
                
                self.preference_pairs.append(PreferencePair(
                    prompt=prompt,
                    chosen=chosen,
                    rejected=rejected,
                    metadata={'source': 'ab_test'}
                ))
                pairs_added += 1
        
        print(f"✅ Added {pairs_added} preference pairs from A/B tests")
        return pairs_added
    
    def add_synthetic_pairs(
        self,
        prompts: List[str],
        base_model,
        tokenizer,
        temperature_good: float = 0.7,
        temperature_bad: float = 1.5
    ) -> int:
        """
        Generate synthetic preference pairs using temperature sampling.
        Lower temperature = more focused, higher = more random/worse.
        
        Args:
            prompts: List of prompts to generate pairs for
            base_model: The LLM to use for generation
            tokenizer: The tokenizer
            temperature_good: Temperature for "good" responses
            temperature_bad: Temperature for "bad" responses
            
        Returns:
            Number of pairs added
        """
        pairs_added = 0
        
        for prompt in prompts:
            try:
                inputs = tokenizer(prompt, return_tensors="pt")
                
                # Generate "good" response (lower temperature)
                with torch.no_grad():
                    good_output = base_model.generate(
                        **inputs,
                        max_new_tokens=256,
                        temperature=temperature_good,
                        do_sample=True
                    )
                chosen = tokenizer.decode(good_output[0], skip_special_tokens=True)
                
                # Generate "bad" response (higher temperature)
                with torch.no_grad():
                    bad_output = base_model.generate(
                        **inputs,
                        max_new_tokens=256,
                        temperature=temperature_bad,
                        do_sample=True
                    )
                rejected = tokenizer.decode(bad_output[0], skip_special_tokens=True)
                
                self.preference_pairs.append(PreferencePair(
                    prompt=prompt,
                    chosen=chosen,
                    rejected=rejected,
                    metadata={'source': 'synthetic', 'temp_good': temperature_good, 'temp_bad': temperature_bad}
                ))
                pairs_added += 1
                
            except Exception as e:
                print(f"⚠️ Failed to generate pair for prompt: {e}")
        
        print(f"✅ Added {pairs_added} synthetic preference pairs")
        return pairs_added
    
    def save(self, output_path: str):
        """Save preference pairs to JSONL file"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w') as f:
            for pair in self.preference_pairs:
                f.write(json.dumps({
                    'prompt': pair.prompt,
                    'chosen': pair.chosen,
                    'rejected': pair.rejected,
                    'metadata': pair.metadata
                }) + '\n')
        
        print(f"✅ Saved {len(self.preference_pairs)} pairs to {output_path}")
    
    def to_dataset(self) -> Dataset:
        """Convert to HuggingFace Dataset for training"""
        data = {
            'prompt': [p.prompt for p in self.preference_pairs],
            'chosen': [p.chosen for p in self.preference_pairs],
            'rejected': [p.rejected for p in self.preference_pairs]
        }
        return Dataset.from_dict(data)


class DPOTrainer:
    """
    Direct Preference Optimization trainer.
    
    Trains the model to prefer chosen responses over rejected ones
    without needing a separate reward model.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml")
        self.config = self._load_config()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load DPO configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                return config.get('dpo_config', {})
        return {}
    
    def train(
        self,
        model,
        tokenizer,
        dataset: Dataset,
        output_dir: str = "ml_training/checkpoints/dpo_lora",
        beta: float = 0.1,
        epochs: int = 1,
        batch_size: int = 4,
        learning_rate: float = 5e-7
    ) -> str:
        """
        Train model using DPO.
        
        Args:
            model: The policy model (with LoRA adapter)
            tokenizer: The tokenizer
            dataset: Preference dataset with prompt/chosen/rejected
            output_dir: Where to save the trained adapter
            beta: KL divergence penalty coefficient
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for DPO
            
        Returns:
            Path to saved adapter
        """
        try:
            from trl import DPOTrainer as TRLDPOTrainer, DPOConfig
        except ImportError:
            print("❌ TRL library not installed. Install with: pip install trl")
            print("   Running in simulation mode...")
            return self._simulate_training(output_dir)
        
        print("\n" + "="*60)
        print("🎯 DPO TRAINING")
        print("="*60)
        print(f"   Beta: {beta}")
        print(f"   Epochs: {epochs}")
        print(f"   Batch size: {batch_size}")
        print(f"   Learning rate: {learning_rate}")
        print(f"   Dataset size: {len(dataset)}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # DPO configuration
        dpo_config = DPOConfig(
            output_dir=str(output_path),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            beta=beta,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            fp16=torch.cuda.is_available(),
            report_to="none"
        )
        
        # Create reference model (frozen copy)
        ref_model = model.base_model.model if hasattr(model, 'base_model') else None
        
        # Initialize DPO trainer
        trainer = TRLDPOTrainer(
            model=model,
            ref_model=ref_model,
            args=dpo_config,
            train_dataset=dataset,
            tokenizer=tokenizer
        )
        
        # Train
        print("\n🚀 Starting DPO training...")
        train_result = trainer.train()
        
        # Save
        print(f"\n💾 Saving DPO adapter to {output_path}")
        model.save_pretrained(output_path)
        tokenizer.save_pretrained(output_path)
        
        # Save metadata
        metadata = {
            "training_type": "DPO",
            "beta": beta,
            "epochs": epochs,
            "dataset_size": len(dataset),
            "trained_on": datetime.now().isoformat(),
            "training_loss": train_result.training_loss
        }
        
        with open(output_path / "dpo_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("\n✅ DPO training complete!")
        return str(output_path)
    
    def _simulate_training(self, output_dir: str) -> str:
        """Simulate DPO training when TRL not available"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "training_type": "DPO (simulated)",
            "note": "Install TRL for actual training: pip install trl",
            "simulated_on": datetime.now().isoformat()
        }
        
        with open(output_path / "dpo_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ DPO simulation complete. Output: {output_path}")
        return str(output_path)


def main():
    """Demo DPO training pipeline"""
    print("="*60)
    print("DPO Training Pipeline Demo")
    print("="*60)
    
    # Build preference dataset
    builder = DPODatasetBuilder()
    
    # Check for existing feedback
    feedback_file = PROJECT_ROOT / "ml_training" / "datasets" / "user_feedback.jsonl"
    if feedback_file.exists():
        builder.add_from_ratings(str(feedback_file))
    else:
        print(f"\n⚠️ No feedback file found at {feedback_file}")
        print("   Creating sample preference pairs for demo...")
        
        # Add sample pairs
        sample_pairs = [
            PreferencePair(
                prompt="What's the best jollof rice?",
                chosen="Omo! Nigerian jollof is the GOAT, no cap! The way we season it with bay leaves, thyme, and that smoky party jollof flavor... nothing compares! Ghana try, but Nigeria own dey hit different! 🇳🇬",
                rejected="I think jollof rice is good. It's a rice dish from West Africa.",
                metadata={'source': 'demo'}
            ),
            PreferencePair(
                prompt="Tell me about Lagos",
                chosen="E ku aro! Lagos na the centre of excellence, my friend! From the hustle of Oshodi to the vibes of Victoria Island, this city never sleeps. We get Suya, Amala, and Owambe every weekend! Lagos no dey carry last! 🌆",
                rejected="Lagos is a city in Nigeria. It has many people.",
                metadata={'source': 'demo'}
            ),
            PreferencePair(
                prompt="How do you greet in Yoruba?",
                chosen="Ah, you wan learn Yoruba? E ku ise! Let me break it down:\n• Morning: E ku aro (good morning)\n• Afternoon: E ku osan (good afternoon)\n• Evening: E ku irole (good evening)\n• General: E kaa san (how are you?)\nYoruba language dey sweet like honey! Oya, practice am! 😊",
                rejected="In Yoruba you can say hello.",
                metadata={'source': 'demo'}
            )
        ]
        
        builder.preference_pairs.extend(sample_pairs)
    
    # Save dataset
    output_file = PROJECT_ROOT / "ml_training" / "datasets" / "preference_pairs.jsonl"
    builder.save(str(output_file))
    
    # Convert to dataset
    dataset = builder.to_dataset()
    print(f"\n📊 Created preference dataset with {len(dataset)} pairs")
    
    # Show sample
    print("\n📋 Sample preference pair:")
    print(f"   Prompt: {dataset[0]['prompt'][:50]}...")
    print(f"   Chosen: {dataset[0]['chosen'][:50]}...")
    print(f"   Rejected: {dataset[0]['rejected'][:50]}...")
    
    print("\n✅ DPO pipeline ready! Run with actual model for training.")


if __name__ == "__main__":
    main()
