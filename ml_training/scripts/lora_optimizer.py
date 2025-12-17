#!/usr/bin/env python3
"""
Sisi Lola LoRA Optimizer
Supports different LoRA rank configurations for experimentation:
- r=8: Fast training, less expressive
- r=16: Balanced (production recommended)
- r=32: More expressive, complex tasks
- r=64: Maximum expressiveness
"""
import os
import yaml
import torch
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class LoRAConfiguration:
    """LoRA configuration with metadata"""
    name: str
    r: int
    alpha: int
    dropout: float
    description: str
    estimated_params: str


class LoRAOptimizer:
    """
    Manages LoRA configurations for fine-tuning optimization.
    
    Features:
    - Predefined configurations (lightweight, balanced, expressive, maximum)
    - Custom configuration support
    - Target module detection per model type
    - Training parameter estimation
    """
    
    CONFIGURATIONS = {
        'lightweight': LoRAConfiguration(
            name='lightweight',
            r=8,
            alpha=16,
            dropout=0.05,
            description="Fast training, good for simple fine-tuning",
            estimated_params="~4M trainable"
        ),
        'balanced': LoRAConfiguration(
            name='balanced',
            r=16,
            alpha=32,
            dropout=0.1,
            description="Recommended production configuration",
            estimated_params="~8M trainable"
        ),
        'expressive': LoRAConfiguration(
            name='expressive',
            r=32,
            alpha=64,
            dropout=0.1,
            description="Complex multi-task, multi-language learning",
            estimated_params="~16M trainable"
        ),
        'maximum': LoRAConfiguration(
            name='maximum',
            r=64,
            alpha=128,
            dropout=0.15,
            description="Maximum expressiveness, slowest training",
            estimated_params="~32M trainable"
        )
    }
    
    TARGET_MODULES = {
        'mistral': ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        'llama': ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        'gpt2': ["c_attn", "c_proj", "c_fc"],
        'opt': ["q_proj", "k_proj", "v_proj", "out_proj", "fc1", "fc2"],
        'bloom': ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"]
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load optimization config"""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {}
    
    def get_configuration(self, name: str = 'balanced') -> LoRAConfiguration:
        """Get predefined LoRA configuration"""
        if name in self.CONFIGURATIONS:
            return self.CONFIGURATIONS[name]
        
        # Try from config file
        config_lora = self.config.get('lora_optimization', {}).get('configurations', {})
        if name in config_lora:
            cfg = config_lora[name]
            return LoRAConfiguration(
                name=name,
                r=cfg.get('r', 16),
                alpha=cfg.get('alpha', 32),
                dropout=cfg.get('dropout', 0.1),
                description=cfg.get('description', ''),
                estimated_params=cfg.get('estimated_params', 'unknown')
            )
        
        raise ValueError(f"Unknown configuration: {name}. Available: {list(self.CONFIGURATIONS.keys())}")
    
    def detect_model_type(self, model_name: str) -> str:
        """Detect model type from name"""
        model_lower = model_name.lower()
        
        for model_type in self.TARGET_MODULES.keys():
            if model_type in model_lower:
                return model_type
        
        # Default to llama-style modules
        return 'llama'
    
    def get_target_modules(self, model_name: str) -> list:
        """Get target modules for a specific model"""
        model_type = self.detect_model_type(model_name)
        return self.TARGET_MODULES.get(model_type, self.TARGET_MODULES['llama'])
    
    def create_lora_config(
        self,
        model_name: str,
        configuration: str = 'balanced',
        custom_r: Optional[int] = None,
        custom_alpha: Optional[int] = None,
        custom_dropout: Optional[float] = None
    ) -> LoraConfig:
        """
        Create LoRA configuration for a model.
        
        Args:
            model_name: Name/path of the base model
            configuration: Preset configuration name
            custom_r: Override rank value
            custom_alpha: Override alpha value
            custom_dropout: Override dropout value
            
        Returns:
            LoraConfig ready for use with PEFT
        """
        # Get base configuration
        config = self.get_configuration(configuration)
        
        # Apply overrides
        r = custom_r or config.r
        alpha = custom_alpha or config.alpha
        dropout = custom_dropout or config.dropout
        
        # Get target modules
        target_modules = self.get_target_modules(model_name)
        
        print(f"\n📋 LoRA Configuration:")
        print(f"   Preset: {configuration}")
        print(f"   Rank (r): {r}")
        print(f"   Alpha: {alpha}")
        print(f"   Dropout: {dropout}")
        print(f"   Target modules: {target_modules}")
        
        return LoraConfig(
            r=r,
            lora_alpha=alpha,
            target_modules=target_modules,
            lora_dropout=dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
    
    def apply_lora(
        self,
        model,
        model_name: str,
        configuration: str = 'balanced',
        prepare_for_kbit: bool = True
    ):
        """
        Apply LoRA adapter to model.
        
        Args:
            model: The base model
            model_name: Name/path of the base model
            configuration: Preset configuration name
            prepare_for_kbit: Whether to prepare for 4-bit/8-bit training
            
        Returns:
            Model with LoRA adapter applied
        """
        lora_config = self.create_lora_config(model_name, configuration)
        
        # Prepare for k-bit training if needed
        if prepare_for_kbit and hasattr(model, 'is_loaded_in_4bit') and model.is_loaded_in_4bit:
            model = prepare_model_for_kbit_training(model)
            print("   ✅ Prepared for 4-bit training")
        
        # Apply LoRA
        model = get_peft_model(model, lora_config)
        
        # Print trainable parameters
        trainable, total = 0, 0
        for param in model.parameters():
            total += param.numel()
            if param.requires_grad:
                trainable += param.numel()
        
        print(f"\n📊 Trainable Parameters:")
        print(f"   Total: {total:,}")
        print(f"   Trainable: {trainable:,} ({100 * trainable / total:.2f}%)")
        
        return model
    
    def compare_configurations(self) -> Dict[str, Dict]:
        """Compare all available configurations"""
        comparison = {}
        
        for name, config in self.CONFIGURATIONS.items():
            comparison[name] = {
                'rank': config.r,
                'alpha': config.alpha,
                'dropout': config.dropout,
                'description': config.description,
                'estimated_params': config.estimated_params,
                'training_speed': 'fast' if config.r <= 8 else 'medium' if config.r <= 16 else 'slow',
                'expressiveness': 'low' if config.r <= 8 else 'medium' if config.r <= 16 else 'high'
            }
        
        return comparison
    
    def recommend_configuration(
        self,
        task_complexity: str = 'medium',
        available_time: str = 'medium',
        gpu_memory_gb: float = 16.0
    ) -> str:
        """
        Recommend LoRA configuration based on constraints.
        
        Args:
            task_complexity: 'low', 'medium', 'high'
            available_time: 'low', 'medium', 'high'
            gpu_memory_gb: Available GPU memory
            
        Returns:
            Recommended configuration name
        """
        # Memory constraints
        if gpu_memory_gb < 8:
            return 'lightweight'
        
        # Time constraints
        if available_time == 'low':
            return 'lightweight'
        
        # Complexity matching
        complexity_map = {
            'low': 'lightweight',
            'medium': 'balanced',
            'high': 'expressive'
        }
        
        base_recommendation = complexity_map.get(task_complexity, 'balanced')
        
        # Upgrade if we have lots of time and memory
        if available_time == 'high' and gpu_memory_gb >= 24:
            if base_recommendation == 'balanced':
                return 'expressive'
            elif base_recommendation == 'expressive':
                return 'maximum'
        
        return base_recommendation


def main():
    """Demo LoRA optimization"""
    print("="*60)
    print("LoRA Optimization Demo")
    print("="*60)
    
    optimizer = LoRAOptimizer()
    
    # Show all configurations
    print("\n📋 Available Configurations:")
    comparison = optimizer.compare_configurations()
    for name, details in comparison.items():
        print(f"\n  {name}:")
        for key, value in details.items():
            print(f"    {key}: {value}")
    
    # Get recommendation
    print("\n📊 Recommendations:")
    for complexity in ['low', 'medium', 'high']:
        rec = optimizer.recommend_configuration(
            task_complexity=complexity,
            available_time='medium',
            gpu_memory_gb=16
        )
        print(f"  Complexity={complexity}: {rec}")
    
    # Show LoRA config for Mistral
    print("\n📋 Example LoRA Config for Mistral-7B:")
    lora_config = optimizer.create_lora_config(
        model_name="mistralai/Mistral-7B-Instruct-v0.3",
        configuration="balanced"
    )
    

if __name__ == "__main__":
    main()
