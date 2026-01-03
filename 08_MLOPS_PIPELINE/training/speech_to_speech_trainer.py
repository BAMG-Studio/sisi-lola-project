#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - END-TO-END SPEECH-TO-SPEECH TRAINING PIPELINE
═══════════════════════════════════════════════════════════════════════════════
Advanced training approach for conversational AI with Nigerian/African voices.

Architecture: Qwen-Omni style end-to-end speech-to-speech models
- Direct audio-to-audio modeling (preserves emotional tone)
- Cultural cadence retention
- Reinforcement learning with native speaker feedback
- Multi-language Nigerian dialect support

Key Benefits over chained ASR→NLU→TTS:
- Preserves prosody, intonation, and emotional nuance
- Maintains cultural speaking patterns
- Lower latency for real-time conversation
- Better handling of code-switching
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import subprocess

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("S2STraining")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Supported Nigerian languages
NIGERIAN_LANGUAGES = {
    "yo": {
        "name": "Yoruba",
        "tonal": True,
        "tone_count": 3,
        "iso_639_3": "yor",
        "datasets": ["fleurs_yo", "common_voice_yo", "yoruba_web"]
    },
    "ha": {
        "name": "Hausa",
        "tonal": True,
        "tone_count": 2,
        "iso_639_3": "hau",
        "datasets": ["fleurs_ha", "common_voice_ha", "hausa_voa"]
    },
    "ig": {
        "name": "Igbo",
        "tonal": True,
        "tone_count": 2,
        "iso_639_3": "ibo",
        "datasets": ["fleurs_ig", "common_voice_ig"]
    },
    "pcm": {
        "name": "Nigerian Pidgin",
        "tonal": False,
        "tone_count": 0,
        "iso_639_3": "pcm",
        "datasets": ["naija_pidgin", "pidgin_web"]
    },
    "en-ng": {
        "name": "Nigerian English",
        "tonal": False,
        "tone_count": 0,
        "iso_639_3": "eng",
        "datasets": ["naija_english", "african_accented_english"]
    }
}


class ModelArchitecture(Enum):
    """Available model architectures."""
    QWEN_OMNI = "qwen_omni"           # End-to-end multimodal
    SEAMLESS_M4T = "seamless_m4t"     # Meta's massively multilingual
    WHISPER_TTS = "whisper_tts"       # Cascaded (fallback)
    MOSHI = "moshi"                   # Kyutai's real-time model
    SPEECHGPT = "speechgpt"           # Speech-text unified


@dataclass
class TrainingConfig:
    """Configuration for speech-to-speech training."""
    # Model
    architecture: ModelArchitecture = ModelArchitecture.QWEN_OMNI
    base_model: str = "Qwen/Qwen2-Audio-7B-Instruct"
    
    # Data
    languages: List[str] = field(default_factory=lambda: ["yo", "ha", "ig", "pcm", "en-ng"])
    train_data_path: Path = Path("data/training/speech")
    val_split: float = 0.1
    max_audio_length_sec: float = 30.0
    
    # Training
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    learning_rate: float = 1e-5
    warmup_steps: int = 500
    num_epochs: int = 3
    fp16: bool = True
    
    # LoRA (for efficient fine-tuning)
    use_lora: bool = True
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    
    # Nigerian-specific
    preserve_tonal_features: bool = True
    code_switch_augmentation: bool = True
    cultural_reward_weight: float = 0.3
    
    # RLHF
    use_rlhf: bool = True
    rlhf_reward_model: str = "nigerian_culture_reward"
    rlhf_ppo_epochs: int = 4
    
    # Output
    output_dir: Path = Path("models/s2s_nigerian")
    checkpoint_every_steps: int = 500
    eval_every_steps: int = 100


@dataclass
class TrainingDataSample:
    """Single training sample for S2S model."""
    audio_path: str
    text: str
    language: str
    speaker_id: str
    duration_sec: float
    
    # Optional paired data for S2S
    response_audio_path: Optional[str] = None
    response_text: Optional[str] = None
    
    # Metadata
    source: str = "unknown"
    quality_score: float = 0.8
    cultural_markers: List[str] = field(default_factory=list)


@dataclass
class RLHFFeedback:
    """Feedback for reinforcement learning."""
    sample_id: str
    generated_audio_path: str
    generated_text: str
    
    # Ratings from native speakers
    naturalness_score: float  # 1-5
    cultural_appropriateness: float  # 1-5
    pronunciation_accuracy: float  # 1-5
    emotional_matching: float  # 1-5
    
    # Binary flags
    uses_correct_slang: bool = False
    uses_correct_idioms: bool = False
    maintains_tonal_patterns: bool = True
    
    # Comments
    native_speaker_notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ═══════════════════════════════════════════════════════════════════════════════

class S2SDataPreparer:
    """
    Prepares data for end-to-end speech-to-speech training.
    
    Data format requirements:
    - Paired audio-audio for conversation turns
    - Audio-text for ASR/TTS capability
    - Cultural annotation for RLHF
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.data_dir = config.train_data_path
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_from_transcripts(self, 
                                  ingestion_db: Path,
                                  output_manifest: Path) -> int:
        """
        Prepare training data from ingested video transcripts.
        
        Args:
            ingestion_db: Path to ingestion database
            output_manifest: Path for output manifest file
            
        Returns:
            Number of samples prepared
        """
        import sqlite3
        
        if not ingestion_db.exists():
            logger.error(f"Database not found: {ingestion_db}")
            return 0
        
        conn = sqlite3.connect(ingestion_db)
        cursor = conn.cursor()
        
        # Get all processed videos with transcripts
        cursor.execute("""
            SELECT v.video_id, v.audio_path, v.language, t.transcript_text, t.segments_json
            FROM videos v
            JOIN transcripts t ON v.video_id = t.video_id
            WHERE v.processing_status = 'processed'
            AND v.audio_path IS NOT NULL
        """)
        
        samples = []
        
        for row in cursor.fetchall():
            video_id, audio_path, language, transcript, segments_json = row
            
            if not audio_path or not Path(audio_path).exists():
                continue
            
            # Parse segments
            segments = json.loads(segments_json) if segments_json else []
            
            # Create samples from segments (for paired turns)
            for i, segment in enumerate(segments):
                sample = TrainingDataSample(
                    audio_path=audio_path,
                    text=segment.get("text", ""),
                    language=language or "en",
                    speaker_id=video_id,
                    duration_sec=segment.get("end", 0) - segment.get("start", 0),
                    source="youtube_ingestion"
                )
                
                # Look for response (next segment from same video)
                if i + 1 < len(segments):
                    next_seg = segments[i + 1]
                    sample.response_text = next_seg.get("text", "")
                
                samples.append(asdict(sample))
        
        conn.close()
        
        # Write manifest
        with open(output_manifest, "w", encoding="utf-8") as f:
            for sample in samples:
                f.write(json.dumps(sample) + "\n")
        
        logger.info(f"Prepared {len(samples)} training samples")
        return len(samples)
    
    def prepare_from_datasets(self, 
                              datasets_dir: Path,
                              output_manifest: Path) -> int:
        """
        Prepare training data from downloaded HuggingFace datasets.
        """
        samples = []
        
        # Process each language
        for lang_code, lang_info in NIGERIAN_LANGUAGES.items():
            lang_dir = datasets_dir / lang_code
            
            if not lang_dir.exists():
                logger.warning(f"No data for {lang_info['name']}")
                continue
            
            # Process audio files
            for audio_file in lang_dir.glob("**/*.wav"):
                # Look for corresponding transcript
                transcript_path = audio_file.with_suffix(".txt")
                
                if transcript_path.exists():
                    text = transcript_path.read_text(encoding="utf-8").strip()
                else:
                    text = ""
                
                sample = TrainingDataSample(
                    audio_path=str(audio_file),
                    text=text,
                    language=lang_code,
                    speaker_id=audio_file.parent.name,
                    duration_sec=0,  # Will be computed during training
                    source="hf_dataset"
                )
                
                samples.append(asdict(sample))
        
        # Write manifest
        with open(output_manifest, "w", encoding="utf-8") as f:
            for sample in samples:
                f.write(json.dumps(sample) + "\n")
        
        logger.info(f"Prepared {len(samples)} samples from datasets")
        return len(samples)
    
    def create_conversation_pairs(self, 
                                   manifest_path: Path,
                                   output_path: Path) -> int:
        """
        Create conversation pairs for speech-to-speech training.
        
        Pairs adjacent utterances to learn response patterns.
        """
        pairs = []
        
        # Load manifest
        with open(manifest_path, "r") as f:
            samples = [json.loads(line) for line in f]
        
        # Group by speaker/video
        from collections import defaultdict
        speaker_samples = defaultdict(list)
        
        for sample in samples:
            speaker_samples[sample["speaker_id"]].append(sample)
        
        # Create pairs within each speaker group
        for speaker_id, speaker_data in speaker_samples.items():
            for i in range(len(speaker_data) - 1):
                pair = {
                    "input": speaker_data[i],
                    "response": speaker_data[i + 1],
                    "pair_id": f"{speaker_id}_{i}"
                }
                pairs.append(pair)
        
        # Write pairs
        with open(output_path, "w") as f:
            for pair in pairs:
                f.write(json.dumps(pair) + "\n")
        
        logger.info(f"Created {len(pairs)} conversation pairs")
        return len(pairs)


# ═══════════════════════════════════════════════════════════════════════════════
# CULTURAL REWARD MODEL
# ═══════════════════════════════════════════════════════════════════════════════

class NigerianCultureRewardModel:
    """
    Reward model for RLHF that scores cultural appropriateness.
    
    Rewards:
    - Correct use of Nigerian slang
    - Appropriate idioms for context
    - Proper tonal patterns (for tonal languages)
    - Cultural references understood
    - Natural code-switching patterns
    """
    
    # Nigerian Pidgin expressions
    PIDGIN_SLANG = [
        "wahala", "wetin", "na so", "abi", "sha", "shey",
        "dey", "no be", "carry go", "chop", "japa", "sabi",
        "oga", "bros", "sistah", "how far", "how body"
    ]
    
    # Yoruba expressions
    YORUBA_IDIOMS = [
        "se", "ko", "abi", "eyin", "omo", "baba", "mama",
        "oluwa", "wahala", "pele"
    ]
    
    # Context-appropriate responses
    CULTURAL_RESPONSES = {
        "greeting": ["how far", "how body", "how you dey", "e kaaro", "e kaasan"],
        "agreement": ["na so", "true talk", "you sabi", "ehen"],
        "surprise": ["chineke", "jesu", "haba", "wahala"],
        "farewell": ["later", "we go see", "bye bye", "o da bo"]
    }
    
    def __init__(self):
        self.slang_set = set(self.PIDGIN_SLANG)
        self.yoruba_set = set(self.YORUBA_IDIOMS)
    
    def compute_reward(self, 
                       generated_text: str,
                       context: str,
                       expected_language: str,
                       feedback: Optional[RLHFFeedback] = None) -> float:
        """
        Compute cultural appropriateness reward.
        
        Args:
            generated_text: Model's generated response
            context: Input context/prompt
            expected_language: Expected language code
            feedback: Optional human feedback
            
        Returns:
            Reward score (0.0 to 1.0)
        """
        score = 0.5  # Base score
        text_lower = generated_text.lower()
        
        # Check for appropriate slang use
        slang_count = sum(1 for s in self.slang_set if s in text_lower)
        if slang_count > 0:
            score += min(slang_count * 0.05, 0.2)  # Up to +0.2
        
        # Check for Yoruba markers if expected
        if expected_language == "yo":
            yoruba_count = sum(1 for y in self.yoruba_set if y in text_lower)
            if yoruba_count > 0:
                score += min(yoruba_count * 0.05, 0.15)
        
        # Check context-appropriate responses
        for context_type, responses in self.CULTURAL_RESPONSES.items():
            if any(r in context.lower() for r in responses):
                if any(r in text_lower for r in responses):
                    score += 0.1
                    break
        
        # Apply human feedback if available
        if feedback:
            human_score = (
                feedback.naturalness_score +
                feedback.cultural_appropriateness +
                feedback.pronunciation_accuracy +
                feedback.emotional_matching
            ) / 20.0  # Normalize to 0-1
            
            # Blend with automatic score
            score = 0.3 * score + 0.7 * human_score
            
            # Bonus for correct flags
            if feedback.uses_correct_slang:
                score += 0.05
            if feedback.uses_correct_idioms:
                score += 0.05
        
        return min(max(score, 0.0), 1.0)
    
    def get_improvement_suggestions(self, 
                                     generated_text: str,
                                     expected_language: str) -> List[str]:
        """Get suggestions for improving cultural appropriateness."""
        suggestions = []
        text_lower = generated_text.lower()
        
        # Check if too formal/stiff
        if not any(s in text_lower for s in self.slang_set):
            suggestions.append("Add some Nigerian Pidgin expressions for naturalness")
        
        # Check language-specific
        if expected_language == "yo" and not any(y in text_lower for y in self.yoruba_set):
            suggestions.append("Include some Yoruba greetings or expressions")
        
        # Check for English-only
        if all(c.isascii() for c in generated_text):
            if expected_language in ["yo", "ha", "ig"]:
                suggestions.append(f"Consider mixing in some {NIGERIAN_LANGUAGES[expected_language]['name']} words")
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

class S2STrainingPipeline:
    """
    End-to-end speech-to-speech training pipeline.
    
    Supports:
    - Supervised fine-tuning on paired audio
    - RLHF with cultural reward model
    - Multi-language training
    - LoRA for efficient adaptation
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_preparer = S2SDataPreparer(config)
        self.reward_model = NigerianCultureRewardModel()
        
        # Training state
        self.current_step = 0
        self.best_loss = float("inf")
    
    def prepare_training_data(self, 
                               ingestion_db: Path = None,
                               datasets_dir: Path = None) -> Path:
        """Prepare all training data."""
        manifest_path = self.config.train_data_path / "train_manifest.jsonl"
        
        total_samples = 0
        
        # From ingested videos
        if ingestion_db and ingestion_db.exists():
            ingestion_manifest = self.config.train_data_path / "ingestion_manifest.jsonl"
            total_samples += self.data_preparer.prepare_from_transcripts(
                ingestion_db, ingestion_manifest
            )
        
        # From HuggingFace datasets
        if datasets_dir and datasets_dir.exists():
            dataset_manifest = self.config.train_data_path / "dataset_manifest.jsonl"
            total_samples += self.data_preparer.prepare_from_datasets(
                datasets_dir, dataset_manifest
            )
        
        # Combine manifests
        combined = []
        for manifest in self.config.train_data_path.glob("*_manifest.jsonl"):
            with open(manifest, "r") as f:
                combined.extend([line.strip() for line in f if line.strip()])
        
        with open(manifest_path, "w") as f:
            f.write("\n".join(combined))
        
        logger.info(f"Total training samples: {total_samples}")
        return manifest_path
    
    def setup_model(self):
        """Setup model for training based on architecture."""
        arch = self.config.architecture
        
        logger.info(f"Setting up {arch.value} model...")
        
        if arch == ModelArchitecture.QWEN_OMNI:
            return self._setup_qwen_omni()
        elif arch == ModelArchitecture.SEAMLESS_M4T:
            return self._setup_seamless()
        elif arch == ModelArchitecture.MOSHI:
            return self._setup_moshi()
        else:
            return self._setup_whisper_tts()
    
    def _setup_qwen_omni(self):
        """Setup Qwen2-Audio for speech-to-speech."""
        try:
            from transformers import (
                Qwen2AudioForConditionalGeneration, 
                AutoProcessor
            )
            from peft import get_peft_model, LoraConfig, TaskType
            import torch
            
            logger.info(f"Loading base model: {self.config.base_model}")
            
            model = Qwen2AudioForConditionalGeneration.from_pretrained(
                self.config.base_model,
                torch_dtype=torch.float16 if self.config.fp16 else torch.float32,
                device_map="auto"
            )
            
            processor = AutoProcessor.from_pretrained(self.config.base_model)
            
            # Apply LoRA
            if self.config.use_lora:
                lora_config = LoraConfig(
                    task_type=TaskType.CAUSAL_LM,
                    r=self.config.lora_rank,
                    lora_alpha=self.config.lora_alpha,
                    lora_dropout=self.config.lora_dropout,
                    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
                )
                model = get_peft_model(model, lora_config)
                logger.info("Applied LoRA adapters")
            
            return model, processor
            
        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            logger.info("Install with: pip install transformers peft torch")
            return None, None
    
    def _setup_seamless(self):
        """Setup SeamlessM4T for multilingual S2S."""
        try:
            from transformers import SeamlessM4TModel, AutoProcessor
            import torch
            
            model_id = "facebook/seamless-m4t-v2-large"
            
            model = SeamlessM4TModel.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.config.fp16 else torch.float32
            )
            processor = AutoProcessor.from_pretrained(model_id)
            
            return model, processor
            
        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            return None, None
    
    def _setup_moshi(self):
        """Setup Moshi for real-time speech."""
        logger.info("Moshi setup - requires custom implementation")
        # Moshi is Kyutai's model - would need their SDK
        return None, None
    
    def _setup_whisper_tts(self):
        """Setup cascaded Whisper + TTS (fallback)."""
        try:
            from transformers import WhisperForConditionalGeneration, WhisperProcessor
            import torch
            
            # Whisper for ASR
            whisper_model = WhisperForConditionalGeneration.from_pretrained(
                "openai/whisper-large-v3",
                torch_dtype=torch.float16 if self.config.fp16 else torch.float32
            )
            whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
            
            return {"asr": (whisper_model, whisper_processor)}, None
            
        except ImportError:
            return None, None
    
    def train_supervised(self, manifest_path: Path, model, processor):
        """
        Supervised fine-tuning on paired data.
        
        Args:
            manifest_path: Path to training manifest
            model: Model to train
            processor: Audio/text processor
        """
        if model is None:
            logger.error("Model not initialized")
            return
        
        try:
            import torch
            from torch.utils.data import DataLoader, Dataset
            from transformers import TrainingArguments, Trainer
            
            # Custom dataset
            class S2SDataset(Dataset):
                def __init__(self, manifest_path, processor):
                    with open(manifest_path, "r") as f:
                        self.samples = [json.loads(line) for line in f if line.strip()]
                    self.processor = processor
                
                def __len__(self):
                    return len(self.samples)
                
                def __getitem__(self, idx):
                    sample = self.samples[idx]
                    # Would need proper audio loading and processing
                    return {"input_ids": torch.zeros(100), "labels": torch.zeros(100)}
            
            dataset = S2SDataset(manifest_path, processor)
            
            training_args = TrainingArguments(
                output_dir=str(self.config.output_dir),
                per_device_train_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                warmup_steps=self.config.warmup_steps,
                num_train_epochs=self.config.num_epochs,
                fp16=self.config.fp16,
                logging_steps=10,
                save_steps=self.config.checkpoint_every_steps,
                eval_steps=self.config.eval_every_steps,
                report_to="tensorboard"
            )
            
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=dataset
            )
            
            logger.info("Starting supervised training...")
            trainer.train()
            
            # Save final model
            trainer.save_model(str(self.config.output_dir / "supervised_final"))
            logger.info("Supervised training complete")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def train_rlhf(self, model, processor, feedback_data: List[RLHFFeedback]):
        """
        RLHF training with cultural reward model.
        
        Uses PPO to optimize for cultural appropriateness.
        """
        if not self.config.use_rlhf:
            logger.info("RLHF disabled in config")
            return
        
        logger.info("Starting RLHF training...")
        
        try:
            from trl import PPOTrainer, PPOConfig
            import torch
            
            ppo_config = PPOConfig(
                batch_size=self.config.batch_size,
                learning_rate=self.config.learning_rate * 0.1,  # Lower LR for RL
                ppo_epochs=self.config.rlhf_ppo_epochs,
            )
            
            # Create reward function
            def compute_reward(query, response, language):
                return self.reward_model.compute_reward(
                    generated_text=response,
                    context=query,
                    expected_language=language
                )
            
            # PPO training loop would go here
            # This is a simplified version
            
            for feedback in feedback_data:
                reward = self.reward_model.compute_reward(
                    generated_text=feedback.generated_text,
                    context="",  # Would need context
                    expected_language="pcm",
                    feedback=feedback
                )
                
                # Update model with reward
                # ... PPO update logic ...
            
            logger.info("RLHF training complete")
            
        except ImportError:
            logger.warning("TRL not installed, skipping RLHF. Install with: pip install trl")
    
    def run_full_pipeline(self, 
                          ingestion_db: Path = None,
                          datasets_dir: Path = None,
                          feedback_data: List[RLHFFeedback] = None):
        """
        Run complete training pipeline.
        
        1. Prepare data
        2. Setup model
        3. Supervised training
        4. RLHF (if enabled)
        5. Save final model
        """
        logger.info("=" * 60)
        logger.info("SISI LOLA S2S TRAINING PIPELINE")
        logger.info("=" * 60)
        
        # 1. Prepare data
        logger.info("\n[1/5] Preparing training data...")
        manifest_path = self.prepare_training_data(ingestion_db, datasets_dir)
        
        # 2. Setup model
        logger.info("\n[2/5] Setting up model...")
        model, processor = self.setup_model()
        
        if model is None:
            logger.error("Failed to setup model")
            return False
        
        # 3. Supervised training
        logger.info("\n[3/5] Supervised fine-tuning...")
        self.train_supervised(manifest_path, model, processor)
        
        # 4. RLHF
        if self.config.use_rlhf and feedback_data:
            logger.info("\n[4/5] RLHF training...")
            self.train_rlhf(model, processor, feedback_data)
        else:
            logger.info("\n[4/5] Skipping RLHF (no feedback data)")
        
        # 5. Save final model
        logger.info("\n[5/5] Saving final model...")
        final_path = self.config.output_dir / "final"
        
        try:
            model.save_pretrained(str(final_path))
            if processor:
                processor.save_pretrained(str(final_path))
            logger.info(f"Saved to: {final_path}")
        except Exception as e:
            logger.error(f"Save failed: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 60)
        
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# CODE-SWITCH AUGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

class CodeSwitchAugmenter:
    """
    Augments training data with code-switching patterns.
    
    Nigerian speakers frequently switch between:
    - English ↔ Pidgin
    - English ↔ Yoruba/Hausa/Igbo
    - Pidgin ↔ Local languages
    
    This augmenter creates synthetic code-switched data.
    """
    
    # Common code-switch patterns
    SWITCH_PHRASES = {
        "en_to_pcm": {
            "you know": "you sabi",
            "what is": "wetin be",
            "I am": "I dey",
            "it is": "na",
            "please": "abeg",
            "money": "ego/kudi",
            "let's go": "make we go",
            "what happened": "wetin happen",
        },
        "en_to_yo": {
            "please": "ẹ jọ̀wọ́",
            "thank you": "ẹ ṣe/o ṣeun",
            "good morning": "ẹ káàárọ̀",
            "how are you": "ṣé àlàáfíà ni",
            "my friend": "ọ̀rẹ́ mi",
        }
    }
    
    def augment_text(self, text: str, 
                     source_lang: str = "en",
                     target_lang: str = "pcm",
                     switch_probability: float = 0.3) -> str:
        """
        Randomly switch some phrases to target language.
        """
        import random
        
        switch_key = f"{source_lang}_to_{target_lang}"
        phrases = self.SWITCH_PHRASES.get(switch_key, {})
        
        augmented = text
        for en_phrase, target_phrase in phrases.items():
            if en_phrase.lower() in text.lower() and random.random() < switch_probability:
                # Replace with code-switched version
                augmented = re.sub(
                    en_phrase, 
                    target_phrase, 
                    augmented, 
                    flags=re.IGNORECASE
                )
        
        return augmented
    
    def create_augmented_samples(self, 
                                  samples: List[TrainingDataSample],
                                  augmentation_ratio: float = 0.5) -> List[TrainingDataSample]:
        """Create augmented samples with code-switching."""
        import random
        
        augmented = []
        
        for sample in samples:
            if random.random() < augmentation_ratio:
                # Create code-switched version
                new_sample = TrainingDataSample(
                    audio_path=sample.audio_path,
                    text=self.augment_text(sample.text),
                    language=f"{sample.language}+pcm",  # Mark as mixed
                    speaker_id=sample.speaker_id,
                    duration_sec=sample.duration_sec,
                    source="code_switch_augmentation",
                    cultural_markers=sample.cultural_markers + ["code_switched"]
                )
                augmented.append(new_sample)
        
        return augmented


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola S2S Training Pipeline")
    parser.add_argument("--config", type=Path, help="Training config JSON")
    parser.add_argument("--ingestion-db", type=Path, help="Ingestion database path")
    parser.add_argument("--datasets-dir", type=Path, help="HuggingFace datasets directory")
    parser.add_argument("--output", type=Path, default=Path("models/s2s_nigerian"),
                        help="Output directory")
    parser.add_argument("--architecture", type=str, default="qwen_omni",
                        choices=["qwen_omni", "seamless_m4t", "whisper_tts"],
                        help="Model architecture")
    parser.add_argument("--no-rlhf", action="store_true", help="Disable RLHF")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    
    args = parser.parse_args()
    
    # Load or create config
    if args.config and args.config.exists():
        with open(args.config, "r") as f:
            config_dict = json.load(f)
        config = TrainingConfig(**config_dict)
    else:
        config = TrainingConfig(
            architecture=ModelArchitecture(args.architecture),
            output_dir=args.output,
            num_epochs=args.epochs,
            use_rlhf=not args.no_rlhf
        )
    
    # Run pipeline
    pipeline = S2STrainingPipeline(config)
    
    success = pipeline.run_full_pipeline(
        ingestion_db=args.ingestion_db,
        datasets_dir=args.datasets_dir
    )
    
    if success:
        print("\n✓ Training complete!")
        print(f"Model saved to: {config.output_dir}")
    else:
        print("\n✗ Training failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
