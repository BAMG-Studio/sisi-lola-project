#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🔄 REPLICATE SYNC - Deploy Models from HuggingFace to Replicate
═══════════════════════════════════════════════════════════════════════════════
Automatically deploy trained models from HuggingFace Hub to Replicate for
production inference.

Flow:
    Modal Training → HuggingFace Hub → Replicate → Users

Features:
- Pull models from HuggingFace Hub
- Package with Cog for Replicate
- Deploy and version models
- Sync model metadata

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import shutil
import subprocess
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReplicateSync")

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Optional imports
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    logger.warning("replicate not installed. Run: pip install replicate")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ReplicateConfig:
    """Replicate deployment configuration."""
    
    # Owner/namespace
    owner: str = "bamg-studio"
    
    # Model mappings (HuggingFace → Replicate)
    model_mappings: Dict[str, str] = field(default_factory=lambda: {
        "brain": "sisi-lola-brain",
        "voice": "sisi-lola-voice",
        "producer": "sisi-lola-producer",
        "video": "sisi-lola-video",
    })
    
    # Cog template for each model type
    cog_templates: Dict[str, str] = field(default_factory=lambda: {
        "brain": "brain_cog.yaml",
        "voice": "voice_cog.yaml",
        "producer": "producer_cog.yaml",
    })
    
    # HuggingFace source repos
    hf_sources: Dict[str, str] = field(default_factory=lambda: {
        "brain": "sisilolalive/sisi-lola-brain-mistral",
        "voice": "sisilolalive/sisi-lola-voice-xtts",
        "producer": "sisilolalive/sisi-lola-personality",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# REPLICATE SYNC CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class ReplicateSync:
    """
    Synchronize models from HuggingFace Hub to Replicate.
    
    This class handles:
    - Pulling models from HuggingFace
    - Packaging with Cog
    - Deploying to Replicate
    - Version management
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        config: Optional[ReplicateConfig] = None
    ):
        """
        Initialize Replicate sync.
        
        Args:
            token: Replicate API token
            config: Configuration object
        """
        self.token = token or os.environ.get("REPLICATE_API_TOKEN")
        self.config = config or ReplicateConfig()
        
        if self.token and REPLICATE_AVAILABLE:
            self.client = replicate.Client(api_token=self.token)
        else:
            self.client = None
        
        logger.info(f"🔄 Replicate Sync initialized for: {self.config.owner}")
    
    def get_replicate_model_name(self, model_type: str) -> str:
        """Get full Replicate model name."""
        model_name = self.config.model_mappings.get(model_type, model_type)
        return f"{self.config.owner}/{model_name}"
    
    def sync_from_huggingface(
        self,
        model_type: str,
        hf_token: Optional[str] = None,
        version_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync a model from HuggingFace Hub to Replicate.
        
        Args:
            model_type: Type of model (brain, voice, producer)
            hf_token: HuggingFace token
            version_tag: Optional version to sync
            
        Returns:
            Deployment result
        """
        from .huggingface_sync import HuggingFaceSync
        
        logger.info(f"🔄 Syncing {model_type} from HuggingFace to Replicate")
        
        # Step 1: Pull from HuggingFace
        hf_sync = HuggingFaceSync(token=hf_token)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model"
            
            logger.info("📥 Pulling model from HuggingFace Hub...")
            hf_sync.pull_model(model_type, model_path, revision=version_tag or "main")
            
            # Step 2: Package with Cog
            logger.info("📦 Packaging with Cog...")
            cog_dir = self._prepare_cog_package(model_path, model_type)
            
            # Step 3: Deploy to Replicate
            logger.info("🚀 Deploying to Replicate...")
            result = self._deploy_cog(cog_dir, model_type)
            
            return result
    
    def deploy_local_model(
        self,
        model_path: Union[str, Path],
        model_type: str,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy a local model directory to Replicate.
        
        Args:
            model_path: Path to model directory
            model_type: Type of model
            version: Optional version string
            
        Returns:
            Deployment result
        """
        model_path = Path(model_path)
        
        logger.info(f"📤 Deploying local {model_type} model to Replicate")
        
        # Prepare Cog package
        cog_dir = self._prepare_cog_package(model_path, model_type)
        
        # Deploy
        result = self._deploy_cog(cog_dir, model_type, version)
        
        return result
    
    def _prepare_cog_package(
        self,
        model_path: Path,
        model_type: str
    ) -> Path:
        """
        Prepare a Cog package for Replicate deployment.
        
        Args:
            model_path: Path to model files
            model_type: Type of model
            
        Returns:
            Path to Cog package directory
        """
        # Create Cog directory
        cog_dir = model_path.parent / "cog_package"
        cog_dir.mkdir(exist_ok=True)
        
        # Copy model files
        model_dest = cog_dir / "model"
        if model_path.is_dir():
            shutil.copytree(model_path, model_dest, dirs_exist_ok=True)
        else:
            model_dest.mkdir(exist_ok=True)
            shutil.copy(model_path, model_dest)
        
        # Generate cog.yaml based on model type
        cog_yaml = self._generate_cog_yaml(model_type)
        (cog_dir / "cog.yaml").write_text(cog_yaml)
        
        # Generate predict.py
        predict_py = self._generate_predict_py(model_type)
        (cog_dir / "predict.py").write_text(predict_py)
        
        logger.info(f"📦 Cog package prepared at: {cog_dir}")
        return cog_dir
    
    def _generate_cog_yaml(self, model_type: str) -> str:
        """Generate cog.yaml for a model type."""
        
        base_config = """
build:
  gpu: true
  cuda: "12.1"
  python_version: "3.10"
  python_packages:
    - torch>=2.0.0
    - transformers>=4.35.0
    - huggingface_hub>=0.20.0
"""
        
        type_specific = {
            "brain": """
    - accelerate>=0.24.0
    - bitsandbytes>=0.41.0
    - peft>=0.6.0
predict: "predict.py:Predictor"
""",
            "voice": """
    - TTS>=0.22.0
    - torchaudio>=2.0.0
    - scipy>=1.11.0
    - librosa>=0.10.0
    - soundfile>=0.12.0
predict: "predict.py:Predictor"
""",
            "producer": """
    - replicate>=0.20.0
    - httpx>=0.26.0
    - Pillow>=10.0.0
    - imageio>=2.33.0
predict: "predict.py:Predictor"
"""
        }
        
        return base_config + type_specific.get(model_type, type_specific["brain"])
    
    def _generate_predict_py(self, model_type: str) -> str:
        """Generate predict.py for a model type."""
        
        templates = {
            "brain": '''
"""Sisi Lola Brain - Nigerian Conversational AI"""
import os
from cog import BasePredictor, Input
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class Predictor(BasePredictor):
    def setup(self):
        """Load the model."""
        self.tokenizer = AutoTokenizer.from_pretrained("./model")
        self.model = AutoModelForCausalLM.from_pretrained(
            "./model",
            torch_dtype=torch.float16,
            device_map="auto"
        )
    
    def predict(
        self,
        prompt: str = Input(description="User message"),
        max_tokens: int = Input(description="Max tokens", default=512),
        temperature: float = Input(description="Temperature", default=0.7),
    ) -> str:
        """Generate a response."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
''',
            "voice": '''
"""Sisi Lola Voice - Nigerian TTS"""
import os
from cog import BasePredictor, Input, Path
from TTS.api import TTS
import torch

class Predictor(BasePredictor):
    def setup(self):
        """Load the voice model."""
        self.tts = TTS(model_path="./model", config_path="./model/config.json")
        if torch.cuda.is_available():
            self.tts.to("cuda")
    
    def predict(
        self,
        text: str = Input(description="Text to speak"),
        speaker_wav: Path = Input(description="Reference audio", default=None),
        language: str = Input(description="Language", default="en"),
    ) -> Path:
        """Generate speech."""
        output_path = "/tmp/output.wav"
        
        if speaker_wav:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=str(speaker_wav),
                language=language,
                file_path=output_path
            )
        else:
            self.tts.tts_to_file(text=text, file_path=output_path)
        
        return Path(output_path)
''',
            "producer": '''
"""Sisi Lola Producer - Content Generation Pipeline"""
import os
import replicate
from cog import BasePredictor, Input, Path
from PIL import Image
import httpx

class Predictor(BasePredictor):
    def setup(self):
        """Initialize the producer."""
        self.replicate_token = os.environ.get("REPLICATE_API_TOKEN")
    
    def predict(
        self,
        prompt: str = Input(description="Content prompt"),
        image: Path = Input(description="Reference image", default=None),
        audio: Path = Input(description="Audio for lip-sync", default=None),
        output_type: str = Input(description="Output type", default="video"),
    ) -> Path:
        """Generate content."""
        # This is a placeholder - actual implementation uses Omni-Human etc.
        return Path("/tmp/output.mp4")
'''
        }
        
        return templates.get(model_type, templates["brain"])
    
    def _deploy_cog(
        self,
        cog_dir: Path,
        model_type: str,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy a Cog package to Replicate.
        
        Args:
            cog_dir: Path to Cog package
            model_type: Type of model
            version: Optional version string
            
        Returns:
            Deployment result
        """
        model_name = self.get_replicate_model_name(model_type)
        
        # Run cog push
        try:
            result = subprocess.run(
                ["cog", "push", f"r8.im/{model_name}"],
                cwd=str(cog_dir),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Deployed to: https://replicate.com/{model_name}")
                return {
                    "success": True,
                    "model": model_name,
                    "url": f"https://replicate.com/{model_name}",
                    "version": version or "latest",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"❌ Deployment failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "model": model_name
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Deployment timed out"}
        except FileNotFoundError:
            logger.error("Cog CLI not found. Install with: curl -o cog https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)")
            return {"success": False, "error": "Cog CLI not installed"}
    
    def list_versions(self, model_type: str) -> List[Dict[str, Any]]:
        """List all versions of a model on Replicate."""
        if not self.client:
            return []
        
        model_name = self.get_replicate_model_name(model_type)
        
        try:
            model = self.client.models.get(model_name)
            versions = []
            for v in model.versions.list():
                versions.append({
                    "id": v.id,
                    "created_at": str(v.created_at),
                    "cog_version": v.cog_version
                })
            return versions
        except Exception as e:
            logger.error(f"Error listing versions: {e}")
            return []
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """Get information about a model on Replicate."""
        if not self.client:
            return {"error": "Replicate client not available"}
        
        model_name = self.get_replicate_model_name(model_type)
        
        try:
            model = self.client.models.get(model_name)
            return {
                "name": model_name,
                "url": model.url,
                "description": model.description,
                "visibility": model.visibility,
                "run_count": model.run_count,
                "latest_version": model.latest_version.id if model.latest_version else None
            }
        except Exception as e:
            return {"error": str(e), "model": model_name}


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def deploy_to_replicate(
    model_path: Union[str, Path],
    model_type: str,
    version: Optional[str] = None,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deploy a local model to Replicate.
    
    Args:
        model_path: Path to model
        model_type: Type (brain, voice, producer)
        version: Optional version
        token: Replicate token
        
    Returns:
        Deployment result
    """
    sync = ReplicateSync(token=token)
    return sync.deploy_local_model(model_path, model_type, version)


def sync_from_huggingface(
    model_type: str,
    hf_token: Optional[str] = None,
    replicate_token: Optional[str] = None,
    version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sync a model from HuggingFace Hub to Replicate.
    
    Args:
        model_type: Type of model
        hf_token: HuggingFace token
        replicate_token: Replicate token
        version: Optional version tag
        
    Returns:
        Sync result
    """
    sync = ReplicateSync(token=replicate_token)
    return sync.sync_from_huggingface(model_type, hf_token, version)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Replicate Model Sync")
    parser.add_argument("action", choices=["deploy", "sync", "info", "versions"])
    parser.add_argument("--model-type", "-m", required=True)
    parser.add_argument("--path", "-p", help="Model path")
    parser.add_argument("--version", "-v", help="Version")
    
    args = parser.parse_args()
    
    sync = ReplicateSync()
    
    if args.action == "deploy":
        result = sync.deploy_local_model(args.path, args.model_type, args.version)
        print(json.dumps(result, indent=2))
    
    elif args.action == "sync":
        result = sync.sync_from_huggingface(args.model_type, version_tag=args.version)
        print(json.dumps(result, indent=2))
    
    elif args.action == "info":
        info = sync.get_model_info(args.model_type)
        print(json.dumps(info, indent=2))
    
    elif args.action == "versions":
        versions = sync.list_versions(args.model_type)
        print(json.dumps(versions, indent=2))
