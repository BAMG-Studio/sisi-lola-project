#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🤗 HUGGINGFACE SYNC - Model Hub Integration
═══════════════════════════════════════════════════════════════════════════════
Push trained models to HuggingFace Hub and manage versioning.

Features:
- Push models after Modal training
- Create model cards with Nigerian context
- Manage model versions with tags
- Dataset upload for training data versioning

HuggingFace Pro Benefits:
- 10x private storage (100GB)
- Private model repos
- Dataset viewer for private datasets
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HuggingFaceSync")

# Optional imports
try:
    from huggingface_hub import (
        HfApi,
        HfFolder,
        Repository,
        create_repo,
        upload_folder,
        upload_file,
        hf_hub_download,
        snapshot_download,
        ModelCard,
        ModelCardData,
    )
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("huggingface_hub not installed. Run: pip install huggingface_hub")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HFConfig:
    """HuggingFace Hub configuration."""
    
    # Organization/User
    namespace: str = "sisilolalive"
    
    # Model repositories
    models: Dict[str, str] = field(default_factory=lambda: {
        "brain": "sisi-lola-brain-mistral",
        "voice": "sisi-lola-voice-xtts", 
        "personality": "sisi-lola-personality",
        "vision": "sisi-lola-vision-lora",
    })
    
    # Dataset repositories
    datasets: Dict[str, str] = field(default_factory=lambda: {
        "chat_logs": "sisi-lola-chat-logs",
        "voice_samples": "sisi-lola-voice-samples",
        "feedback": "sisi-lola-feedback-data",
    })
    
    # Nigerian-specific metadata
    nigerian_languages: List[str] = field(default_factory=lambda: [
        "yoruba", "igbo", "hausa", "pidgin", "english"
    ])
    
    # Model card template
    model_card_template: str = """
---
language:
- en
- yo
- ig
- ha
- pcm
tags:
- nigerian-ai
- sisi-lola
- conversational
- voice-cloning
license: mit
datasets:
- sisilolalive/sisi-lola-chat-logs
---

# 🇳🇬 {model_name}

{description}

## Model Description

This model is part of the **Sisi Lola** Nigerian AI assistant system.
It has been fine-tuned on authentic Nigerian conversational data
across multiple languages: Yoruba, Igbo, Hausa, Nigerian Pidgin, and English.

### Training Details

- **Base Model**: {base_model}
- **Training Data**: {training_samples} samples
- **Languages**: {languages}
- **Last Updated**: {last_updated}
- **Training Run**: #{run_number}

### Nigerian Cultural Features

- 🎭 Authentic Nigerian personality and expressions
- 🗣️ Multi-language support (Yoruba, Igbo, Hausa, Pidgin, English)
- 🎵 Nigerian musical and cultural references
- 💬 Natural code-switching between languages

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("{repo_id}")
tokenizer = AutoTokenizer.from_pretrained("{repo_id}")
```

## Metrics

| Metric | Value |
|--------|-------|
| Loss | {loss} |
| Nigerian Authenticity Score | {nigerian_score} |
| Language Coverage | {language_coverage} |

## License

MIT License - Free for commercial use with attribution.

## Citation

```bibtex
@misc{{sisilola2026,
  title={{Sisi Lola: Nigerian AI Assistant}},
  author={{BAMG Studio}},
  year={{2026}},
  publisher={{HuggingFace Hub}}
}}
```
"""


# ═══════════════════════════════════════════════════════════════════════════════
# HUGGINGFACE SYNC CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class HuggingFaceSync:
    """
    Synchronize models and datasets with HuggingFace Hub.
    
    This class handles:
    - Pushing trained models to the Hub
    - Creating model cards with Nigerian context
    - Versioning with tags
    - Dataset uploads for training data
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        config: Optional[HFConfig] = None
    ):
        """
        Initialize HuggingFace sync.
        
        Args:
            token: HuggingFace API token
            config: Configuration object
        """
        if not HF_AVAILABLE:
            raise ImportError("huggingface_hub required. Run: pip install huggingface_hub")
        
        self.token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        self.config = config or HFConfig()
        self.api = HfApi(token=self.token)
        
        logger.info(f"🤗 HuggingFace Sync initialized for namespace: {self.config.namespace}")
    
    def get_repo_id(self, model_type: str) -> str:
        """Get full repository ID for a model type."""
        repo_name = self.config.models.get(model_type, model_type)
        return f"{self.config.namespace}/{repo_name}"
    
    def push_model(
        self,
        model_path: Union[str, Path],
        model_type: str,
        training_info: Optional[Dict[str, Any]] = None,
        create_if_missing: bool = True,
        private: bool = True,
    ) -> Dict[str, Any]:
        """
        Push a trained model to HuggingFace Hub.
        
        Args:
            model_path: Path to model directory or file
            model_type: Type of model (brain, voice, personality, vision)
            training_info: Training metadata (loss, samples, etc.)
            create_if_missing: Create repo if it doesn't exist
            private: Make repository private
            
        Returns:
            Upload result with URLs
        """
        model_path = Path(model_path)
        repo_id = self.get_repo_id(model_type)
        
        logger.info(f"📤 Pushing {model_type} model to {repo_id}")
        
        # Create repo if needed
        if create_if_missing:
            try:
                self.api.create_repo(
                    repo_id=repo_id,
                    repo_type="model",
                    private=private,
                    exist_ok=True
                )
            except Exception as e:
                logger.warning(f"Repo creation note: {e}")
        
        # Generate model card
        model_card_content = self._create_model_card(
            model_type=model_type,
            repo_id=repo_id,
            training_info=training_info or {}
        )
        
        # Save model card
        card_path = model_path / "README.md" if model_path.is_dir() else model_path.parent / "README.md"
        card_path.write_text(model_card_content)
        
        # Upload
        if model_path.is_dir():
            result = upload_folder(
                repo_id=repo_id,
                folder_path=str(model_path),
                token=self.token,
                commit_message=f"Update {model_type} model - Run #{training_info.get('run_number', 'manual')}"
            )
        else:
            result = upload_file(
                path_or_fileobj=str(model_path),
                path_in_repo=model_path.name,
                repo_id=repo_id,
                token=self.token,
                commit_message=f"Update {model_type} model"
            )
        
        logger.info(f"✅ Model pushed to: https://huggingface.co/{repo_id}")
        
        return {
            "repo_id": repo_id,
            "url": f"https://huggingface.co/{repo_id}",
            "commit": str(result) if result else "success",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def pull_model(
        self,
        model_type: str,
        output_path: Optional[Union[str, Path]] = None,
        revision: str = "main"
    ) -> Path:
        """
        Pull a model from HuggingFace Hub.
        
        Args:
            model_type: Type of model to pull
            output_path: Where to save the model
            revision: Branch/tag to pull
            
        Returns:
            Path to downloaded model
        """
        repo_id = self.get_repo_id(model_type)
        
        logger.info(f"📥 Pulling {model_type} model from {repo_id}")
        
        local_dir = snapshot_download(
            repo_id=repo_id,
            revision=revision,
            token=self.token,
            local_dir=str(output_path) if output_path else None
        )
        
        logger.info(f"✅ Model downloaded to: {local_dir}")
        return Path(local_dir)
    
    def push_dataset(
        self,
        data_path: Union[str, Path],
        dataset_type: str,
        private: bool = True
    ) -> Dict[str, Any]:
        """
        Push training data to HuggingFace Datasets.
        
        Args:
            data_path: Path to dataset file/folder
            dataset_type: Type (chat_logs, voice_samples, feedback)
            private: Make dataset private
            
        Returns:
            Upload result
        """
        data_path = Path(data_path)
        dataset_name = self.config.datasets.get(dataset_type, dataset_type)
        repo_id = f"{self.config.namespace}/{dataset_name}"
        
        logger.info(f"📤 Pushing dataset to {repo_id}")
        
        # Create dataset repo
        self.api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=private,
            exist_ok=True
        )
        
        # Upload
        if data_path.is_dir():
            result = upload_folder(
                repo_id=repo_id,
                folder_path=str(data_path),
                repo_type="dataset",
                token=self.token
            )
        else:
            result = upload_file(
                path_or_fileobj=str(data_path),
                path_in_repo=data_path.name,
                repo_id=repo_id,
                repo_type="dataset",
                token=self.token
            )
        
        logger.info(f"✅ Dataset pushed to: https://huggingface.co/datasets/{repo_id}")
        
        return {
            "repo_id": repo_id,
            "url": f"https://huggingface.co/datasets/{repo_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_version_tag(
        self,
        model_type: str,
        version: str,
        message: Optional[str] = None
    ) -> str:
        """
        Create a version tag for a model.
        
        Args:
            model_type: Type of model
            version: Version string (e.g., "v1.2.0")
            message: Tag message
            
        Returns:
            Tag name
        """
        repo_id = self.get_repo_id(model_type)
        
        self.api.create_tag(
            repo_id=repo_id,
            tag=version,
            tag_message=message or f"Release {version}"
        )
        
        logger.info(f"🏷️ Created tag {version} for {repo_id}")
        return version
    
    def list_versions(self, model_type: str) -> List[str]:
        """List all version tags for a model."""
        repo_id = self.get_repo_id(model_type)
        refs = self.api.list_repo_refs(repo_id)
        return [tag.name for tag in refs.tags]
    
    def _create_model_card(
        self,
        model_type: str,
        repo_id: str,
        training_info: Dict[str, Any]
    ) -> str:
        """Generate a model card with Nigerian context."""
        
        # Model-specific descriptions
        descriptions = {
            "brain": "Mistral-7B fine-tuned for Nigerian conversational AI with cultural awareness.",
            "voice": "XTTS-v2 voice model trained on Nigerian speech patterns and accents.",
            "personality": "Personality embeddings capturing Sisi Lola's Nigerian character.",
            "vision": "LoRA adapter for consistent Nigerian visual aesthetics.",
        }
        
        base_models = {
            "brain": "mistralai/Mistral-7B-Instruct-v0.2",
            "voice": "coqui/XTTS-v2",
            "personality": "sentence-transformers/all-MiniLM-L6-v2",
            "vision": "stabilityai/stable-diffusion-xl-base-1.0",
        }
        
        return self.config.model_card_template.format(
            model_name=f"Sisi Lola {model_type.title()} Model",
            description=descriptions.get(model_type, "Nigerian AI model component."),
            base_model=base_models.get(model_type, "custom"),
            training_samples=training_info.get("samples", "N/A"),
            languages=", ".join(self.config.nigerian_languages),
            last_updated=datetime.utcnow().strftime("%Y-%m-%d"),
            run_number=training_info.get("run_number", "manual"),
            repo_id=repo_id,
            loss=training_info.get("loss", "N/A"),
            nigerian_score=training_info.get("nigerian_score", "N/A"),
            language_coverage=training_info.get("language_coverage", "5/5")
        )
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """Get information about a model on the Hub."""
        repo_id = self.get_repo_id(model_type)
        
        try:
            info = self.api.model_info(repo_id)
            return {
                "repo_id": repo_id,
                "last_modified": str(info.last_modified),
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "private": info.private
            }
        except Exception as e:
            return {"error": str(e), "repo_id": repo_id}


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def push_model_to_hub(
    model_path: Union[str, Path],
    model_type: str,
    training_info: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to push a model to HuggingFace Hub.
    
    Args:
        model_path: Path to model
        model_type: Type (brain, voice, personality, vision)
        training_info: Training metadata
        token: HF token
        
    Returns:
        Upload result
    """
    sync = HuggingFaceSync(token=token)
    return sync.push_model(model_path, model_type, training_info)


def pull_model_from_hub(
    model_type: str,
    output_path: Optional[Union[str, Path]] = None,
    token: Optional[str] = None
) -> Path:
    """
    Convenience function to pull a model from HuggingFace Hub.
    
    Args:
        model_type: Type of model
        output_path: Where to save
        token: HF token
        
    Returns:
        Path to model
    """
    sync = HuggingFaceSync(token=token)
    return sync.pull_model(model_type, output_path)


def create_model_card(
    model_type: str,
    training_info: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None
) -> str:
    """
    Generate a model card for a Sisi Lola model.
    
    Args:
        model_type: Type of model
        training_info: Training metadata
        output_path: Optional path to save
        
    Returns:
        Model card content
    """
    sync = HuggingFaceSync()
    content = sync._create_model_card(
        model_type=model_type,
        repo_id=sync.get_repo_id(model_type),
        training_info=training_info
    )
    
    if output_path:
        Path(output_path).write_text(content)
    
    return content


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HuggingFace Hub Sync")
    parser.add_argument("action", choices=["push", "pull", "info", "tag"])
    parser.add_argument("--model-type", "-m", required=True)
    parser.add_argument("--path", "-p", help="Model path")
    parser.add_argument("--version", "-v", help="Version tag")
    
    args = parser.parse_args()
    
    sync = HuggingFaceSync()
    
    if args.action == "push":
        result = sync.push_model(args.path, args.model_type)
        print(json.dumps(result, indent=2))
    
    elif args.action == "pull":
        path = sync.pull_model(args.model_type, args.path)
        print(f"Downloaded to: {path}")
    
    elif args.action == "info":
        info = sync.get_model_info(args.model_type)
        print(json.dumps(info, indent=2))
    
    elif args.action == "tag":
        tag = sync.create_version_tag(args.model_type, args.version)
        print(f"Created tag: {tag}")
