"""
SISI LOLA OPTUNA HYPERPARAMETER SEARCH
======================================
Automated hyperparameter optimization for brain model training.

Uses Optuna to search for optimal:
- LoRA rank and alpha
- Learning rate
- Batch size
- Weight decay
- Warmup ratio

Results are stored in SQLite for persistence and can be visualized
with Optuna's built-in dashboard.
"""

import os
import yaml
import torch
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from functools import partial

try:
    import optuna
    from optuna.trial import Trial
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("[WARN] Optuna not installed. Run: pip install optuna")

from transformers import (
    AutoModelForCausalLM, AutoTokenizer, 
    TrainingArguments, Trainer, BitsAndBytesConfig,
    EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset, concatenate_datasets


class OptunaTrainer:
    """Hyperparameter search using Optuna"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent
        
        # Load config
        if config_path is None:
            config_path = self.project_root / "ml_training" / "configs" / "brain_training_config.yaml"
        
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.hp_config = self.config.get("hyperparameter_search", {})
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Optuna settings
        self.study_name = self.hp_config.get("study_name", "sisi_lola_brain_tuning")
        self.n_trials = self.hp_config.get("n_trials", 20)
        
        storage_path = self.hp_config.get("storage", "sqlite:///ml_training/optuna_studies.db")
        if storage_path.startswith("sqlite:///") and not storage_path.startswith("sqlite:////"):
            # Relative path - make absolute
            relative = storage_path.replace("sqlite:///", "")
            absolute = self.project_root / relative
            storage_path = f"sqlite:///{absolute}"
        self.storage = storage_path
        
        # Search space from config
        self.search_space = self.hp_config.get("search_space", {})
        
        # Cache datasets
        self._train_dataset = None
        self._val_dataset = None
        self._tokenizer = None
    
    def load_model(self, lora_rank: int, lora_alpha: int, lora_dropout: float):
        """Load model with specific LoRA configuration"""
        model_id = os.getenv("BRAIN_MODEL", "gpt2")  # Use small model for search
        
        print(f"Loading model: {model_id}")
        
        if "gpt2" in model_id.lower():
            model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
            target_modules = ["c_attn", "c_proj"]
        else:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto"
            )
            target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Apply LoRA
        lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        if hasattr(model, 'is_loaded_in_4bit') and model.is_loaded_in_4bit:
            model = prepare_model_for_kbit_training(model)
        
        model = get_peft_model(model, lora_config)
        
        return model, tokenizer
    
    def load_datasets(self):
        """Load and cache datasets"""
        if self._train_dataset is not None:
            return self._train_dataset, self._val_dataset
        
        datasets_list = []
        
        # Load brain instructions
        brain_path = self.project_root / "ml_training" / "datasets" / "brain_instructions.jsonl"
        if brain_path.exists():
            data = []
            with open(brain_path) as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        text = f"<|system|>\n{item.get('system', '')}\n<|user|>\n{item['user']}\n<|assistant|>\n{item['assistant']}"
                        data.append({"text": text})
            if data:
                datasets_list.append(Dataset.from_list(data))
        
        # Load NaijaSenti
        try:
            naija = load_dataset("HausaNLP/NaijaSenti", split="train")
            datasets_list.append(naija)
        except:
            pass
        
        if not datasets_list:
            raise ValueError("No training data found!")
        
        combined = concatenate_datasets(datasets_list)
        split = combined.train_test_split(test_size=0.2, seed=42)
        
        self._train_dataset = split["train"]
        self._val_dataset = split["test"]
        
        print(f"Loaded {len(self._train_dataset)} train / {len(self._val_dataset)} val samples")
        
        return self._train_dataset, self._val_dataset
    
    def format_prompt(self, example, tokenizer):
        """Tokenize example"""
        system = self.config.get("system_prompts", {}).get("sisi_lola_core", "You are Sisi Lola.")
        text = example.get('text', '')
        
        if "<|system|>" not in text:
            prompt = f"<|system|>\n{system}\n<|user|>\n{text}\n<|assistant|>\n"
        else:
            prompt = text
        
        tokenized = tokenizer(prompt, truncation=True, max_length=512, padding="max_length")
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
    
    def objective(self, trial: "Trial") -> float:
        """
        Optuna objective function.
        
        Returns validation loss (lower is better).
        """
        # Sample hyperparameters
        space = self.search_space
        
        lora_rank = trial.suggest_categorical(
            "lora_rank", 
            space.get("lora_rank", [4, 8, 16])
        )
        lora_alpha = trial.suggest_categorical(
            "lora_alpha", 
            space.get("lora_alpha", [16, 32, 64])
        )
        lora_dropout = trial.suggest_float(
            "lora_dropout",
            space.get("lora_dropout", {}).get("min", 0.01),
            space.get("lora_dropout", {}).get("max", 0.1)
        )
        learning_rate = trial.suggest_float(
            "learning_rate",
            space.get("learning_rate", {}).get("min", 1e-5),
            space.get("learning_rate", {}).get("max", 5e-4),
            log=True
        )
        batch_size = trial.suggest_categorical(
            "batch_size",
            space.get("batch_size", [2, 4, 8])
        )
        weight_decay = trial.suggest_float(
            "weight_decay",
            space.get("weight_decay", {}).get("min", 0.0),
            space.get("weight_decay", {}).get("max", 0.1)
        )
        warmup_ratio = trial.suggest_float(
            "warmup_ratio",
            space.get("warmup_ratio", {}).get("min", 0.0),
            space.get("warmup_ratio", {}).get("max", 0.2)
        )
        
        print(f"\n{'='*60}")
        print(f"Trial {trial.number}: rank={lora_rank}, alpha={lora_alpha}, lr={learning_rate:.2e}")
        print(f"{'='*60}")
        
        try:
            # Load model with sampled config
            model, tokenizer = self.load_model(lora_rank, lora_alpha, lora_dropout)
            
            # Get datasets
            train_dataset, val_dataset = self.load_datasets()
            
            # Tokenize
            train_tokenized = train_dataset.map(
                lambda x: self.format_prompt(x, tokenizer),
                batched=False,
                remove_columns=train_dataset.column_names
            )
            val_tokenized = val_dataset.map(
                lambda x: self.format_prompt(x, tokenizer),
                batched=False,
                remove_columns=val_dataset.column_names
            )
            
            # Training args
            output_dir = self.project_root / "ml_training" / "optuna_trials" / f"trial_{trial.number}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            training_args = TrainingArguments(
                output_dir=str(output_dir),
                num_train_epochs=1,  # Quick evaluation
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                gradient_accumulation_steps=max(1, 16 // batch_size),
                learning_rate=learning_rate,
                weight_decay=weight_decay,
                warmup_ratio=warmup_ratio,
                fp16=torch.cuda.is_available(),
                logging_steps=50,
                eval_strategy="steps",
                eval_steps=100,
                save_strategy="no",  # Don't save intermediate
                report_to="none",
                max_steps=200 if torch.cuda.is_available() else 50,  # Quick eval
            )
            
            # Train
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_tokenized,
                eval_dataset=val_tokenized,
                processing_class=tokenizer,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
            )
            
            trainer.train()
            
            # Evaluate
            eval_results = trainer.evaluate()
            val_loss = eval_results.get("eval_loss", float("inf"))
            
            print(f"Trial {trial.number} - Validation Loss: {val_loss:.4f}")
            
            # Cleanup
            del model, trainer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return val_loss
            
        except Exception as e:
            print(f"Trial {trial.number} failed: {e}")
            return float("inf")
    
    def run_search(self, n_trials: Optional[int] = None) -> Dict[str, Any]:
        """
        Run hyperparameter search.
        
        Returns best hyperparameters.
        """
        if not OPTUNA_AVAILABLE:
            raise RuntimeError("Optuna not installed. Run: pip install optuna")
        
        n_trials = n_trials or self.n_trials
        
        print("\n" + "="*80)
        print("SISI LOLA OPTUNA HYPERPARAMETER SEARCH")
        print("="*80)
        print(f"Study: {self.study_name}")
        print(f"Trials: {n_trials}")
        print(f"Storage: {self.storage}")
        print("="*80 + "\n")
        
        # Create or load study
        study = optuna.create_study(
            study_name=self.study_name,
            storage=self.storage,
            direction="minimize",
            load_if_exists=True
        )
        
        # Run optimization
        study.optimize(self.objective, n_trials=n_trials)
        
        # Report results
        print("\n" + "="*80)
        print("SEARCH COMPLETE!")
        print("="*80)
        print(f"Best trial: {study.best_trial.number}")
        print(f"Best validation loss: {study.best_value:.4f}")
        print("\nBest hyperparameters:")
        for key, value in study.best_params.items():
            print(f"  {key}: {value}")
        
        # Save best params
        results = {
            "study_name": self.study_name,
            "n_trials": len(study.trials),
            "best_trial": study.best_trial.number,
            "best_value": study.best_value,
            "best_params": study.best_params,
            "completed_at": datetime.now().isoformat()
        }
        
        results_path = self.project_root / "ml_training" / "optuna_trials" / "best_params.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📁 Results saved to: {results_path}")
        
        return study.best_params
    
    def get_best_params(self) -> Optional[Dict[str, Any]]:
        """Load best parameters from previous search"""
        results_path = self.project_root / "ml_training" / "optuna_trials" / "best_params.json"
        if results_path.exists():
            with open(results_path) as f:
                results = json.load(f)
            return results.get("best_params")
        return None


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Optuna hyperparameter search for Sisi Lola")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials")
    parser.add_argument("--config", type=str, help="Path to config YAML")
    parser.add_argument("--show-best", action="store_true", help="Show best params from previous run")
    
    args = parser.parse_args()
    
    searcher = OptunaTrainer(config_path=args.config)
    
    if args.show_best:
        best = searcher.get_best_params()
        if best:
            print("Best hyperparameters from previous search:")
            for k, v in best.items():
                print(f"  {k}: {v}")
        else:
            print("No previous search results found.")
    else:
        if not OPTUNA_AVAILABLE:
            print("Error: Optuna not installed. Run: pip install optuna")
            return
        
        searcher.run_search(n_trials=args.trials)


if __name__ == "__main__":
    main()
