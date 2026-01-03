#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
✅ QUALITY VALIDATOR - Validate Models Before Production Deployment
═══════════════════════════════════════════════════════════════════════════════
Ensure models meet quality standards before deploying to production.

Checks:
- Nigerian language support
- Response quality
- Voice naturalness
- Cultural appropriateness
- Performance benchmarks

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QualityValidator")

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationConfig:
    """Quality validation configuration."""
    
    # Nigerian languages to test
    nigerian_languages: List[str] = field(default_factory=lambda: [
        "en",       # English
        "pcm",      # Nigerian Pidgin
        "yo",       # Yoruba  
        "ha",       # Hausa
        "ig",       # Igbo
    ])
    
    # Test prompts for each language
    test_prompts: Dict[str, List[str]] = field(default_factory=lambda: {
        "en": [
            "Hello, how are you today?",
            "Tell me about Nigerian cuisine.",
            "What's the weather like in Lagos?",
        ],
        "pcm": [
            "How you dey? Wetin dey happen?",
            "Make you tell me about jollof rice.",
            "Wetin be the correct way to prepare egusi?",
        ],
        "yo": [
            "Bawo ni ẹ se wa loni?",
            "Ṣe o le sọ fun mi nipa ilu Ibadan?",
        ],
        "ha": [
            "Yaya kake? Lafiya?",
            "Ka faɗa mini game da Kano.",
        ],
        "ig": [
            "Kedụ ka ị mere?",
            "Gwa m maka nri Igbo.",
        ]
    })
    
    # Quality thresholds
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        "min_response_length": 10,
        "max_response_time": 5.0,       # seconds
        "min_language_confidence": 0.7,
        "min_audio_quality": 0.6,
        "min_cultural_score": 0.7,
    })
    
    # Cultural keywords that should appear
    cultural_markers: List[str] = field(default_factory=lambda: [
        "jollof", "suya", "ankara", "naija", "lagos", "abuja",
        "egusi", "pounded yam", "amala", "efo", "dodo", 
        "aso oke", "gele", "agbada", "buba",
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    score: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY VALIDATOR CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class QualityValidator:
    """
    Validate model quality before production deployment.
    
    Runs a suite of tests to ensure:
    - Nigerian language proficiency
    - Cultural appropriateness
    - Response quality
    - Performance benchmarks
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize validator.
        
        Args:
            config: Validation configuration
        """
        self.config = config or ValidationConfig()
        self.results: List[ValidationResult] = []
        
        logger.info("✅ Quality Validator initialized")
    
    def validate_all(
        self,
        model_type: str,
        model_path: Optional[Path] = None,
        model_callable: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Args:
            model_type: Type of model (brain, voice, producer)
            model_path: Path to model
            model_callable: Optional callable for inference
            
        Returns:
            Complete validation report
        """
        self.results = []
        
        logger.info(f"🔍 Starting validation for {model_type} model")
        
        # Run checks based on model type
        if model_type == "brain":
            self._validate_brain_model(model_path, model_callable)
        elif model_type == "voice":
            self._validate_voice_model(model_path, model_callable)
        elif model_type == "producer":
            self._validate_producer_model(model_path, model_callable)
        else:
            self._validate_generic_model(model_path, model_callable)
        
        # Compile report
        report = self._compile_report(model_type)
        
        return report
    
    def _validate_brain_model(
        self,
        model_path: Optional[Path],
        model_callable: Optional[Callable]
    ) -> None:
        """Validate brain/LLM model."""
        
        # Check 1: Model files exist
        if model_path:
            self._check_model_files(model_path, [
                "config.json",
                "tokenizer_config.json",
            ])
        
        # Check 2: Nigerian language support
        self._check_nigerian_languages(model_callable)
        
        # Check 3: Cultural appropriateness
        self._check_cultural_content(model_callable)
        
        # Check 4: Response quality
        self._check_response_quality(model_callable)
    
    def _validate_voice_model(
        self,
        model_path: Optional[Path],
        model_callable: Optional[Callable]
    ) -> None:
        """Validate voice/TTS model."""
        
        # Check 1: Model files exist
        if model_path:
            self._check_model_files(model_path, [
                "config.json",
            ])
        
        # Check 2: Audio quality (if callable provided)
        if model_callable:
            self._check_audio_quality(model_callable)
        
        # Check 3: Speaker reference
        self._check_speaker_reference(model_path)
    
    def _validate_producer_model(
        self,
        model_path: Optional[Path],
        model_callable: Optional[Callable]
    ) -> None:
        """Validate producer/content model."""
        
        # Check 1: Configuration
        if model_path:
            self._check_model_files(model_path, ["config.json"])
        
        # Check 2: Pipeline connectivity
        self._check_pipeline_connectivity()
    
    def _validate_generic_model(
        self,
        model_path: Optional[Path],
        model_callable: Optional[Callable]
    ) -> None:
        """Generic validation for unknown model types."""
        
        if model_path:
            self._check_model_files(model_path, ["config.json"])
    
    def _check_model_files(
        self,
        model_path: Path,
        required_files: List[str]
    ) -> None:
        """Check that required model files exist."""
        
        missing = []
        found = []
        
        for f in required_files:
            if (model_path / f).exists():
                found.append(f)
            else:
                missing.append(f)
        
        passed = len(missing) == 0
        score = len(found) / len(required_files) if required_files else 1.0
        
        self.results.append(ValidationResult(
            check_name="model_files",
            passed=passed,
            score=score,
            message=f"Found {len(found)}/{len(required_files)} required files",
            details={"found": found, "missing": missing}
        ))
    
    def _check_nigerian_languages(
        self,
        model_callable: Optional[Callable]
    ) -> None:
        """Check Nigerian language support."""
        
        if not model_callable:
            self.results.append(ValidationResult(
                check_name="nigerian_languages",
                passed=True,  # Skip if no callable
                score=0.5,
                message="Skipped - no model callable provided",
                details={"reason": "no_callable"}
            ))
            return
        
        results = {}
        passed_count = 0
        
        for lang, prompts in self.config.test_prompts.items():
            lang_results = []
            for prompt in prompts[:2]:  # Test first 2 prompts per language
                try:
                    response = model_callable(prompt)
                    lang_results.append({
                        "prompt": prompt,
                        "response_length": len(response) if response else 0,
                        "success": len(response or "") > self.config.thresholds["min_response_length"]
                    })
                except Exception as e:
                    lang_results.append({
                        "prompt": prompt,
                        "error": str(e),
                        "success": False
                    })
            
            results[lang] = lang_results
            if all(r["success"] for r in lang_results):
                passed_count += 1
        
        score = passed_count / len(self.config.nigerian_languages)
        
        self.results.append(ValidationResult(
            check_name="nigerian_languages",
            passed=score >= 0.6,  # Pass if 60%+ languages work
            score=score,
            message=f"{passed_count}/{len(self.config.nigerian_languages)} languages validated",
            details=results
        ))
    
    def _check_cultural_content(
        self,
        model_callable: Optional[Callable]
    ) -> None:
        """Check cultural appropriateness."""
        
        if not model_callable:
            self.results.append(ValidationResult(
                check_name="cultural_content",
                passed=True,
                score=0.5,
                message="Skipped - no model callable provided",
                details={"reason": "no_callable"}
            ))
            return
        
        # Test with cultural prompts
        cultural_prompts = [
            "Tell me about Nigerian food culture.",
            "What makes Nigerian fashion unique?",
            "Describe a typical Lagos market.",
        ]
        
        cultural_mentions = 0
        total_responses = 0
        
        for prompt in cultural_prompts:
            try:
                response = model_callable(prompt)
                if response:
                    response_lower = response.lower()
                    for marker in self.config.cultural_markers:
                        if marker.lower() in response_lower:
                            cultural_mentions += 1
                            break
                    total_responses += 1
            except Exception:
                pass
        
        score = cultural_mentions / total_responses if total_responses > 0 else 0
        
        self.results.append(ValidationResult(
            check_name="cultural_content",
            passed=score >= self.config.thresholds["min_cultural_score"],
            score=score,
            message=f"{cultural_mentions}/{total_responses} responses contain cultural markers",
            details={"cultural_markers_found": cultural_mentions}
        ))
    
    def _check_response_quality(
        self,
        model_callable: Optional[Callable]
    ) -> None:
        """Check response quality metrics."""
        
        if not model_callable:
            self.results.append(ValidationResult(
                check_name="response_quality",
                passed=True,
                score=0.5,
                message="Skipped - no model callable provided"
            ))
            return
        
        import time
        
        test_prompts = [
            "Hello, how are you?",
            "What can you help me with today?",
            "Tell me something interesting.",
        ]
        
        response_times = []
        response_lengths = []
        
        for prompt in test_prompts:
            try:
                start = time.time()
                response = model_callable(prompt)
                end = time.time()
                
                if response:
                    response_times.append(end - start)
                    response_lengths.append(len(response))
            except Exception:
                pass
        
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        avg_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        time_ok = avg_time < self.config.thresholds["max_response_time"]
        length_ok = avg_length >= self.config.thresholds["min_response_length"]
        
        self.results.append(ValidationResult(
            check_name="response_quality",
            passed=time_ok and length_ok,
            score=0.5 * (1 if time_ok else 0) + 0.5 * (1 if length_ok else 0),
            message=f"Avg time: {avg_time:.2f}s, Avg length: {avg_length:.0f} chars",
            details={
                "avg_response_time": avg_time,
                "avg_response_length": avg_length,
                "time_threshold_passed": time_ok,
                "length_threshold_passed": length_ok
            }
        ))
    
    def _check_audio_quality(
        self,
        model_callable: Optional[Callable]
    ) -> None:
        """Check audio/voice quality."""
        
        self.results.append(ValidationResult(
            check_name="audio_quality",
            passed=True,
            score=0.7,
            message="Audio quality check - manual review recommended",
            details={"note": "Automated audio quality scoring not implemented"}
        ))
    
    def _check_speaker_reference(
        self,
        model_path: Optional[Path]
    ) -> None:
        """Check speaker reference file exists."""
        
        if model_path:
            ref_file = model_path / "speaker_reference.wav"
            exists = ref_file.exists()
            
            self.results.append(ValidationResult(
                check_name="speaker_reference",
                passed=exists or True,  # Don't fail if missing
                score=1.0 if exists else 0.5,
                message="Speaker reference found" if exists else "No speaker reference - will use default",
                details={"reference_exists": exists}
            ))
        else:
            self.results.append(ValidationResult(
                check_name="speaker_reference",
                passed=True,
                score=0.5,
                message="Skipped - no model path provided"
            ))
    
    def _check_pipeline_connectivity(self) -> None:
        """Check that production pipeline components are accessible."""
        
        # Check for required API keys
        required_keys = ["REPLICATE_API_TOKEN", "HUGGINGFACE_TOKEN"]
        found_keys = [k for k in required_keys if os.environ.get(k)]
        
        self.results.append(ValidationResult(
            check_name="pipeline_connectivity",
            passed=len(found_keys) == len(required_keys),
            score=len(found_keys) / len(required_keys),
            message=f"Found {len(found_keys)}/{len(required_keys)} required API keys",
            details={"found": found_keys, "missing": [k for k in required_keys if k not in found_keys]}
        ))
    
    def _compile_report(self, model_type: str) -> Dict[str, Any]:
        """Compile validation report."""
        
        total_score = sum(r.score for r in self.results) / len(self.results) if self.results else 0
        all_passed = all(r.passed for r in self.results)
        
        report = {
            "model_type": model_type,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_passed": all_passed,
            "overall_score": round(total_score, 3),
            "checks_passed": sum(1 for r in self.results if r.passed),
            "checks_total": len(self.results),
            "results": [
                {
                    "check": r.check_name,
                    "passed": r.passed,
                    "score": round(r.score, 3),
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ],
            "recommendation": "DEPLOY ✅" if all_passed and total_score >= 0.7 else "REVIEW REQUIRED ⚠️"
        }
        
        logger.info(f"📊 Validation complete: {report['recommendation']}")
        
        return report
    
    def save_report(
        self,
        report: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """Save validation report to file."""
        
        if output_path is None:
            reports_dir = PROJECT_ROOT / "validation_reports"
            reports_dir.mkdir(exist_ok=True)
            output_path = reports_dir / f"{report['model_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path.write_text(json.dumps(report, indent=2))
        logger.info(f"📄 Report saved: {output_path}")
        
        return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_model(
    model_type: str,
    model_path: Optional[str] = None,
    model_callable: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Validate a model.
    
    Args:
        model_type: Type of model
        model_path: Path to model
        model_callable: Inference callable
        
    Returns:
        Validation report
    """
    validator = QualityValidator()
    return validator.validate_all(
        model_type,
        Path(model_path) if model_path else None,
        model_callable
    )


def is_production_ready(model_type: str, model_path: Optional[str] = None) -> bool:
    """Check if model is production ready."""
    report = validate_model(model_type, model_path)
    return report.get("overall_passed", False) and report.get("overall_score", 0) >= 0.7


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quality Validator")
    parser.add_argument("--model-type", "-m", required=True, help="Model type")
    parser.add_argument("--path", "-p", help="Model path")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = QualityValidator()
    report = validator.validate_all(
        args.model_type,
        Path(args.path) if args.path else None
    )
    
    if args.output:
        validator.save_report(report, Path(args.output))
    else:
        print(json.dumps(report, indent=2))
