"""
SISI LOLA MODEL COMPARISON HARNESS
==================================
Evaluates multiple trained models/adapters against the persona test set.

Features:
- Runs persona test prompts against multiple models
- Scores responses using rule-based and semantic evaluation
- Generates comparison report with rankings
- Saves results to model_registry.json for production selection
"""

import os
import json
import yaml
import torch
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import re


@dataclass
class ModelScore:
    """Scores for a single model"""
    model_id: str
    model_path: str
    total_score: float
    avg_response_time_ms: float
    identity_score: float
    language_score: float
    empathy_score: float
    humor_score: float
    culture_score: float
    safety_score: float
    consistency_score: float
    num_probes_passed: int
    total_probes: int
    evaluated_at: str
    

class ModelComparer:
    """Compare multiple models using persona test prompts"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent
        
        # Load config
        if config_path is None:
            config_path = self.project_root / "ml_training" / "configs" / "brain_training_config.yaml"
        
        if Path(config_path).exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
        
        # Paths
        self.probes_path = self.project_root / "ml_training" / "datasets" / "personality_test_prompts.jsonl"
        self.checkpoints_dir = self.project_root / "ml_training" / "checkpoints"
        self.registry_path = self.project_root / "ml_training" / "configs" / "model_registry.json"
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load probes
        self.probes = self._load_probes()
        
        # Category weights for scoring
        self.category_weights = {
            "identity": 1.5,      # Most important - must be Sisi Lola
            "language": 1.2,      # Important - pidgin/Nigerian language
            "empathy": 1.0,
            "humor": 1.0,
            "culture": 1.2,       # Important - Nigerian culture
            "safety": 1.5,        # Critical - must decline unsafe requests
            "consistency": 1.0,
            "greeting": 0.8,
            "farewell": 0.8,
            "gratitude": 0.8,
            "compliment": 0.8,
            "lifestyle": 0.9,
            "empowerment": 1.0,
            "engagement": 0.8,
            "celebration": 1.0,
            "boundaries": 1.2,    # Important - maintain boundaries
        }
    
    def _load_probes(self) -> List[Dict[str, Any]]:
        """Load persona test prompts"""
        probes = []
        if self.probes_path.exists():
            with open(self.probes_path) as f:
                for line in f:
                    if line.strip():
                        probes.append(json.loads(line))
        else:
            print(f"[WARN] Probes file not found at {self.probes_path}")
        return probes
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for generation"""
        return """You are Sisi Lola - a confident, funny, and charismatic Nigerian virtual host.
Mix English and Nigerian Pidgin naturally. Be warm, authentic, and empowering.
Use humor and charisma in every response. Speak like a supportive sister.
Your catchphrases include: "Omo see gobe!", "Na so!", "Las las we go dey alright!"
Be culturally authentic, celebrate Nigerian culture, and always uplift others."""
    
    def load_model(self, model_path: str) -> Tuple[Any, Any, str]:
        """
        Load a model/adapter for evaluation.
        
        Supports:
        - Base models (huggingface ID or local path)
        - LoRA adapters (with adapter_config.json)
        """
        model_path = Path(model_path)
        
        # Check if this is a LoRA adapter
        is_adapter = (model_path / "adapter_config.json").exists()
        
        if is_adapter:
            # Load adapter config to get base model
            with open(model_path / "adapter_config.json") as f:
                adapter_config = json.load(f)
            
            base_model_id = adapter_config.get("base_model_name_or_path", "gpt2")
            print(f"Loading base model: {base_model_id}")
            
            # Load base model
            if "gpt2" in base_model_id.lower():
                model = AutoModelForCausalLM.from_pretrained(base_model_id)
            else:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16
                )
                model = AutoModelForCausalLM.from_pretrained(
                    base_model_id,
                    quantization_config=bnb_config,
                    device_map="auto"
                )
            
            # Load adapter
            print(f"Loading LoRA adapter from: {model_path}")
            model = PeftModel.from_pretrained(model, str(model_path))
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model_id = f"{base_model_id}+LoRA"
        else:
            # Direct model loading
            model_id = str(model_path)
            print(f"Loading model directly: {model_id}")
            
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model.eval()
        return model, tokenizer, model_id
    
    def generate_response(self, model, tokenizer, prompt: str, max_new_tokens: int = 150) -> Tuple[str, float]:
        """Generate a response and measure time"""
        system_prompt = self._build_system_prompt()
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
        
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id
            )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Decode and extract response
        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        if "<|assistant|>" in full_output:
            response = full_output.split("<|assistant|>")[-1].strip()
        else:
            # Just take the new generated part
            response = full_output[len(full_prompt):].strip()
        
        return response, elapsed_ms
    
    def score_response(self, response: str, probe: Dict[str, Any]) -> Dict[str, float]:
        """
        Score a response against a probe's expected elements.
        
        Returns dict with:
        - element_score: How many expected elements were present
        - rubric_score: Scoring based on rubric (must_include, should_include, bonus)
        - length_score: Appropriate response length
        - persona_score: Contains persona markers
        """
        response_lower = response.lower()
        scores = {}
        
        # Element matching
        expected = probe.get("expected_elements", [])
        matched_elements = sum(1 for elem in expected if elem.lower() in response_lower)
        scores["element_score"] = matched_elements / max(len(expected), 1)
        
        # Rubric scoring
        rubric = probe.get("scoring_rubric", {})
        
        must_include = rubric.get("must_include", [])
        must_score = sum(1 for elem in must_include if elem.lower() in response_lower)
        must_score = must_score / max(len(must_include), 1) if must_include else 1.0
        
        should_include = rubric.get("should_include", [])
        should_score = sum(1 for elem in should_include if elem.lower() in response_lower)
        should_score = should_score / max(len(should_include), 1) if should_include else 0.5
        
        bonus = rubric.get("bonus", [])
        bonus_score = sum(0.2 for elem in bonus if elem.lower() in response_lower)
        
        scores["rubric_score"] = (must_score * 0.5 + should_score * 0.3 + min(bonus_score, 0.2))
        
        # Length appropriateness (not too short, not too long)
        length = len(response)
        if length < 20:
            scores["length_score"] = 0.2  # Too short
        elif length < 50:
            scores["length_score"] = 0.5
        elif length < 500:
            scores["length_score"] = 1.0  # Good length
        else:
            scores["length_score"] = 0.7  # Maybe too long
        
        # Persona markers (Sisi Lola indicators)
        persona_markers = [
            "sisi lola", "omo", "na so", "dey", "wetin", "abeg", 
            "naija", "wahala", "las las", "e choke", "nigeria"
        ]
        persona_matches = sum(1 for m in persona_markers if m in response_lower)
        scores["persona_score"] = min(persona_matches / 3, 1.0)  # Cap at 1.0
        
        # Combined score
        scores["combined"] = (
            scores["element_score"] * 0.3 +
            scores["rubric_score"] * 0.4 +
            scores["length_score"] * 0.1 +
            scores["persona_score"] * 0.2
        )
        
        return scores
    
    def evaluate_model(self, model_path: str) -> ModelScore:
        """
        Evaluate a single model against all probes.
        
        Returns ModelScore with all metrics.
        """
        print(f"\n{'='*60}")
        print(f"Evaluating: {model_path}")
        print(f"{'='*60}")
        
        try:
            model, tokenizer, model_id = self.load_model(model_path)
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return None
        
        # Initialize category scores
        category_scores: Dict[str, List[float]] = {}
        response_times = []
        passed_probes = 0
        
        for i, probe in enumerate(self.probes):
            category = probe.get("category", "unknown")
            
            # Generate response
            try:
                response, elapsed_ms = self.generate_response(model, tokenizer, probe["probe"])
                response_times.append(elapsed_ms)
            except Exception as e:
                print(f"  [WARN] Probe {i+1} failed: {e}")
                continue
            
            # Score response
            scores = self.score_response(response, probe)
            
            # Track by category
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(scores["combined"])
            
            # Count as passed if combined score >= 0.5
            if scores["combined"] >= 0.5:
                passed_probes += 1
            
            # Print progress
            status = "✓" if scores["combined"] >= 0.5 else "✗"
            print(f"  {status} [{category}] {probe['probe'][:40]}... ({scores['combined']:.2f})")
        
        # Calculate category averages
        def avg_category(cat: str) -> float:
            if cat in category_scores and category_scores[cat]:
                return sum(category_scores[cat]) / len(category_scores[cat])
            return 0.0
        
        # Calculate weighted total score
        total_weighted = 0.0
        total_weight = 0.0
        for cat, scores_list in category_scores.items():
            weight = self.category_weights.get(cat, 1.0)
            avg = sum(scores_list) / len(scores_list) if scores_list else 0.0
            total_weighted += avg * weight
            total_weight += weight
        
        total_score = total_weighted / total_weight if total_weight > 0 else 0.0
        
        result = ModelScore(
            model_id=model_id,
            model_path=str(model_path),
            total_score=total_score,
            avg_response_time_ms=sum(response_times) / len(response_times) if response_times else 0.0,
            identity_score=avg_category("identity"),
            language_score=avg_category("language"),
            empathy_score=avg_category("empathy"),
            humor_score=avg_category("humor"),
            culture_score=avg_category("culture"),
            safety_score=avg_category("safety"),
            consistency_score=avg_category("consistency"),
            num_probes_passed=passed_probes,
            total_probes=len(self.probes),
            evaluated_at=datetime.now().isoformat()
        )
        
        # Clean up
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return result
    
    def compare_all_checkpoints(self) -> List[ModelScore]:
        """Evaluate all checkpoints in the checkpoints directory"""
        results = []
        
        # Find all checkpoint directories
        if not self.checkpoints_dir.exists():
            print(f"[WARN] Checkpoints directory not found: {self.checkpoints_dir}")
            return results
        
        checkpoints = []
        for item in self.checkpoints_dir.iterdir():
            if item.is_dir():
                # Check if it's a valid model/adapter
                if (item / "adapter_config.json").exists() or (item / "config.json").exists():
                    checkpoints.append(item)
        
        print(f"\nFound {len(checkpoints)} checkpoints to evaluate")
        
        for checkpoint in checkpoints:
            result = self.evaluate_model(str(checkpoint))
            if result:
                results.append(result)
        
        # Sort by total score
        results.sort(key=lambda x: x.total_score, reverse=True)
        
        return results
    
    def generate_report(self, results: List[ModelScore]) -> str:
        """Generate a comparison report"""
        report = []
        report.append("\n" + "="*80)
        report.append("SISI LOLA MODEL COMPARISON REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("="*80 + "\n")
        
        if not results:
            report.append("No models evaluated.")
            return "\n".join(report)
        
        report.append("RANKING BY TOTAL SCORE:")
        report.append("-"*80)
        
        for i, result in enumerate(results, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "  "
            report.append(f"{medal} #{i}: {result.model_id}")
            report.append(f"    Total Score: {result.total_score:.3f}")
            report.append(f"    Probes Passed: {result.num_probes_passed}/{result.total_probes}")
            report.append(f"    Avg Response Time: {result.avg_response_time_ms:.0f}ms")
            report.append("")
        
        report.append("\nCATEGORY BREAKDOWN (Top Model):")
        report.append("-"*80)
        top = results[0]
        report.append(f"  Identity:    {top.identity_score:.3f}")
        report.append(f"  Language:    {top.language_score:.3f}")
        report.append(f"  Empathy:     {top.empathy_score:.3f}")
        report.append(f"  Humor:       {top.humor_score:.3f}")
        report.append(f"  Culture:     {top.culture_score:.3f}")
        report.append(f"  Safety:      {top.safety_score:.3f}")
        report.append(f"  Consistency: {top.consistency_score:.3f}")
        
        report.append("\n" + "="*80)
        report.append(f"RECOMMENDED MODEL: {results[0].model_path}")
        report.append("="*80)
        
        return "\n".join(report)
    
    def save_to_registry(self, results: List[ModelScore]):
        """Save results to model_registry.json"""
        registry = {
            "last_updated": datetime.now().isoformat(),
            "recommended_model": results[0].model_path if results else None,
            "models": [asdict(r) for r in results]
        }
        
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"\n✅ Results saved to: {self.registry_path}")


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare Sisi Lola models")
    parser.add_argument("--model", type=str, help="Evaluate a specific model path")
    parser.add_argument("--all", action="store_true", help="Evaluate all checkpoints")
    parser.add_argument("--output", type=str, help="Save report to file")
    parser.add_argument("--config", type=str, help="Path to config YAML")
    
    args = parser.parse_args()
    
    comparer = ModelComparer(config_path=args.config)
    
    if args.model:
        # Evaluate single model
        result = comparer.evaluate_model(args.model)
        if result:
            print(f"\n📊 Results for {args.model}:")
            print(f"   Total Score: {result.total_score:.3f}")
            print(f"   Probes Passed: {result.num_probes_passed}/{result.total_probes}")
    elif args.all:
        # Compare all checkpoints
        results = comparer.compare_all_checkpoints()
        report = comparer.generate_report(results)
        print(report)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n📁 Report saved to: {args.output}")
        
        if results:
            comparer.save_to_registry(results)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
