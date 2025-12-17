#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - UNIFIED CONFIG LOADER
# ═══════════════════════════════════════════════════════════════════════════════
# Secure configuration management for video ingestion pipeline
# Features:
#   - YAML config loading with validation
#   - Environment variable interpolation
#   - Secret key management (never logged)
#   - Multiple config profiles
# ═══════════════════════════════════════════════════════════════════════════════

import os
import re
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DATACLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RecCloudConfig:
    """RecCloud API configuration."""
    api_key: str = ""
    base_url: str = "https://api.reccloud.com/v1"
    timeout: int = 300
    max_retries: int = 3
    cost_per_minute: float = 0.0006


@dataclass
class ModalConfig:
    """Modal Whisper configuration."""
    enabled: bool = False
    function_name: str = "whisper_transcribe"
    timeout: int = 600
    gpu_type: str = "A100"
    cost_per_minute: float = 0.0002


@dataclass
class TranscriptionConfig:
    """Transcription pipeline configuration."""
    backend: str = "reccloud"  # "reccloud" | "modal"
    primary_language: str = "en"
    secondary_languages: List[str] = field(default_factory=lambda: ["yo", "np"])
    transcript_format: str = "dual"
    speaker_diarization: bool = True
    timestamp_alignment: bool = True


@dataclass
class VideoIngestionConfig:
    """Video source and processing configuration."""
    video_source_dir: str = "C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS"
    output_dir: str = "ml_training/datasets/video_training_data"
    batch_size: int = 5
    skip_existing: bool = True
    retry_failed: bool = True
    video_extensions: List[str] = field(default_factory=lambda: [".mp4", ".mov", ".avi", ".mkv"])


@dataclass
class TrainingConfig:
    """ML training configuration."""
    target_examples: int = 1750
    chat_examples: int = 500
    video_examples: int = 1250
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    lora_rank: int = 64
    epochs: int = 3


@dataclass
class UnifiedConfig:
    """Complete unified configuration for the ingestion pipeline."""
    reccloud: RecCloudConfig = field(default_factory=RecCloudConfig)
    modal: ModalConfig = field(default_factory=ModalConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    video: VideoIngestionConfig = field(default_factory=VideoIngestionConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG LOADER
# ═══════════════════════════════════════════════════════════════════════════════

class ConfigLoader:
    """
    Secure configuration loader with environment variable interpolation.
    
    Features:
        - YAML config loading
        - Environment variable substitution (${VAR_NAME} syntax)
        - Secret masking in logs
        - Config validation
        - Profile support (dev, staging, prod)
    """
    
    # Pattern to match ${VAR_NAME} or ${VAR_NAME:default}
    ENV_PATTERN = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)(:[^}]*)?\}')
    
    # Keys that should never be logged
    SECRET_KEYS = {'api_key', 'secret', 'password', 'token', 'key'}
    
    def __init__(self, config_path: Optional[str] = None, profile: str = "default"):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to YAML config file
            profile: Config profile to use (default, dev, staging, prod)
        """
        self.profile = profile
        
        # Find config file
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self._find_config_file()
        
        # Load configuration
        self._raw_config: Dict[str, Any] = {}
        self._config: Optional[UnifiedConfig] = None
    
    def _find_config_file(self) -> Path:
        """Find configuration file in standard locations."""
        search_paths = [
            Path(__file__).parent / "unified_ingestion_config.yaml",
            Path(__file__).parent.parent / "config.yaml",
            Path.cwd() / "ml_training" / "configs" / "unified_ingestion_config.yaml",
            Path.cwd() / "config.yaml",
        ]
        
        for path in search_paths:
            if path.exists():
                logger.info(f"Found config file: {path}")
                return path
        
        logger.warning("No config file found, using defaults")
        return search_paths[0]  # Use default path
    
    def _interpolate_env(self, value: Any) -> Any:
        """
        Replace ${VAR_NAME} with environment variable values.
        
        Supports ${VAR_NAME:default} syntax for default values.
        """
        if not isinstance(value, str):
            return value
        
        def replace_env(match):
            var_name = match.group(1)
            default = match.group(2)
            
            # Get from environment
            env_value = os.getenv(var_name)
            
            if env_value is not None:
                return env_value
            elif default:
                return default[1:]  # Remove leading ':'
            else:
                logger.warning(f"Environment variable not set: {var_name}")
                return ""
        
        return self.ENV_PATTERN.sub(replace_env, value)
    
    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively process config with env interpolation."""
        processed = {}
        
        for key, value in config.items():
            if isinstance(value, dict):
                processed[key] = self._process_config(value)
            elif isinstance(value, list):
                processed[key] = [
                    self._process_config(item) if isinstance(item, dict)
                    else self._interpolate_env(item)
                    for item in value
                ]
            else:
                processed[key] = self._interpolate_env(value)
        
        return processed
    
    def _mask_secrets(self, config: Dict[str, Any], path: str = "") -> Dict[str, Any]:
        """Mask secret values for logging."""
        masked = {}
        
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                masked[key] = self._mask_secrets(value, current_path)
            elif key.lower() in self.SECRET_KEYS:
                masked[key] = "***MASKED***"
            else:
                masked[key] = value
        
        return masked
    
    def load(self) -> UnifiedConfig:
        """
        Load and parse configuration.
        
        Returns:
            UnifiedConfig with all settings
        """
        if self._config:
            return self._config
        
        # Load YAML if exists
        if self.config_path.exists():
            with open(self.config_path) as f:
                self._raw_config = yaml.safe_load(f) or {}
        else:
            logger.info("Creating default configuration")
            self._raw_config = {}
        
        # Select profile
        if self.profile != "default" and self.profile in self._raw_config:
            profile_config = self._raw_config[self.profile]
        else:
            profile_config = self._raw_config
        
        # Process environment variables
        processed = self._process_config(profile_config)
        
        # Log masked config
        logger.debug(f"Loaded config: {self._mask_secrets(processed)}")
        
        # Build typed config
        self._config = self._build_config(processed)
        
        return self._config
    
    def _build_config(self, data: Dict[str, Any]) -> UnifiedConfig:
        """Build typed UnifiedConfig from dict."""
        config = UnifiedConfig()
        
        # RecCloud settings
        if 'reccloud' in data:
            rc = data['reccloud']
            config.reccloud = RecCloudConfig(
                api_key=rc.get('api_key', os.getenv('RECCLOUD_API_KEY', '')),
                base_url=rc.get('base_url', 'https://api.reccloud.com/v1'),
                timeout=rc.get('timeout', 300),
                max_retries=rc.get('max_retries', 3),
                cost_per_minute=rc.get('cost_per_minute', 0.0006)
            )
        else:
            config.reccloud.api_key = os.getenv('RECCLOUD_API_KEY', '')
        
        # Modal settings
        if 'modal' in data:
            m = data['modal']
            config.modal = ModalConfig(
                enabled=m.get('enabled', False),
                function_name=m.get('function_name', 'whisper_transcribe'),
                timeout=m.get('timeout', 600),
                gpu_type=m.get('gpu_type', 'A100'),
                cost_per_minute=m.get('cost_per_minute', 0.0002)
            )
        
        # Transcription settings
        if 'transcription' in data:
            t = data['transcription']
            config.transcription = TranscriptionConfig(
                backend=t.get('backend', os.getenv('TRANSCRIPTION_BACKEND', 'reccloud')),
                primary_language=t.get('primary_language', 'en'),
                secondary_languages=t.get('secondary_languages', ['yo', 'np']),
                transcript_format=t.get('transcript_format', 'dual'),
                speaker_diarization=t.get('speaker_diarization', True),
                timestamp_alignment=t.get('timestamp_alignment', True)
            )
        
        # Video ingestion settings
        if 'video' in data:
            v = data['video']
            config.video = VideoIngestionConfig(
                video_source_dir=v.get('video_source_dir', 'C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS'),
                output_dir=v.get('output_dir', 'ml_training/datasets/video_training_data'),
                batch_size=v.get('batch_size', 5),
                skip_existing=v.get('skip_existing', True),
                retry_failed=v.get('retry_failed', True),
                video_extensions=v.get('video_extensions', ['.mp4', '.mov', '.avi', '.mkv'])
            )
        
        # Training settings
        if 'training' in data:
            tr = data['training']
            config.training = TrainingConfig(
                target_examples=tr.get('target_examples', 1750),
                chat_examples=tr.get('chat_examples', 500),
                video_examples=tr.get('video_examples', 1250),
                model_name=tr.get('model_name', 'mistralai/Mistral-7B-Instruct-v0.2'),
                lora_rank=tr.get('lora_rank', 64),
                epochs=tr.get('epochs', 3)
            )
        
        return config
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        config = self.load()
        errors = []
        
        # Validate backend selection
        if config.transcription.backend not in ('reccloud', 'modal'):
            errors.append(f"Invalid transcription backend: {config.transcription.backend}")
        
        # Validate RecCloud API key if using RecCloud
        if config.transcription.backend == 'reccloud' and not config.reccloud.api_key:
            errors.append("RecCloud API key is required when using RecCloud backend")
        
        # Validate video source directory
        video_dir = Path(config.video.video_source_dir)
        if not video_dir.exists():
            errors.append(f"Video source directory not found: {video_dir}")
        
        # Validate language codes
        valid_languages = {'en', 'yo', 'np', 'ha', 'ig'}
        for lang in config.transcription.secondary_languages:
            if lang not in valid_languages:
                errors.append(f"Invalid language code: {lang}")
        
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
        
        return errors
    
    def get_transcription_backend(self) -> str:
        """Get active transcription backend."""
        return self.load().transcription.backend
    
    def get_api_key(self) -> str:
        """Get RecCloud API key securely."""
        return self.load().reccloud.api_key


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_config_instance: Optional[ConfigLoader] = None


def get_config(profile: str = "default") -> UnifiedConfig:
    """
    Get configuration singleton.
    
    Args:
        profile: Config profile to use
        
    Returns:
        UnifiedConfig instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigLoader(profile=profile)
    
    return _config_instance.load()


def validate_config() -> List[str]:
    """Validate current configuration."""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigLoader()
    
    return _config_instance.validate()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.DEBUG)
    
    loader = ConfigLoader()
    config = loader.load()
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║    SISI LOLA - CONFIGURATION SUMMARY                       ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print(f"Config file: {loader.config_path}")
    print(f"Profile: {loader.profile}")
    print()
    
    print("Transcription Backend:", config.transcription.backend)
    print("Primary Language:", config.transcription.primary_language)
    print("Secondary Languages:", config.transcription.secondary_languages)
    print("Video Source:", config.video.video_source_dir)
    print("Output Dir:", config.video.output_dir)
    print()
    
    errors = loader.validate()
    if errors:
        print("⚠ Validation Errors:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✓ Configuration valid!")
