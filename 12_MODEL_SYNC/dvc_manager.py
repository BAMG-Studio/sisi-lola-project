#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
📊 DVC MANAGER - Model Version Control with DVC
═══════════════════════════════════════════════════════════════════════════════
Track and version all models with DVC (Data Version Control).
Integrates with local Dropbox-synced storage.

Features:
- Track model files with DVC
- Version tagging
- Rollback support
- Metrics logging
- Integration with training pipeline

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DVCManager")

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DVCConfig:
    """DVC configuration for Sisi Lola."""
    
    # Storage location (Dropbox-synced)
    storage_path: Path = field(default_factory=lambda: PROJECT_ROOT / "dvc-storage")
    
    # DVC remote name
    remote_name: str = "local"
    
    # Model directories to track
    model_dirs: Dict[str, str] = field(default_factory=lambda: {
        "brain": "models/brain",
        "voice": "models/voice", 
        "producer": "models/producer",
        "vision": "models/vision",
    })
    
    # Metrics file
    metrics_file: str = "metrics.json"
    
    # Params file
    params_file: str = "params.yaml"


# ═══════════════════════════════════════════════════════════════════════════════
# DVC MANAGER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class DVCManager:
    """
    Manage model versioning with DVC.
    
    This class provides:
    - Model tracking
    - Version tagging with git
    - Rollback capabilities
    - Metrics logging
    - Integration with training workflows
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[DVCConfig] = None
    ):
        """
        Initialize DVC Manager.
        
        Args:
            project_root: Root of the project
            config: DVC configuration
        """
        self.project_root = project_root or PROJECT_ROOT
        self.config = config or DVCConfig()
        
        # Ensure storage exists
        self.config.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Check DVC availability
        self.dvc_available = self._check_dvc()
        
        logger.info(f"📊 DVC Manager initialized (DVC available: {self.dvc_available})")
    
    def _check_dvc(self) -> bool:
        """Check if DVC is installed and available."""
        try:
            result = subprocess.run(
                ["dvc", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _run_dvc(self, args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a DVC command."""
        return subprocess.run(
            ["dvc"] + args,
            cwd=str(cwd or self.project_root),
            capture_output=True,
            text=True
        )
    
    def _run_git(self, args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a git command."""
        return subprocess.run(
            ["git"] + args,
            cwd=str(cwd or self.project_root),
            capture_output=True,
            text=True
        )
    
    def init(self) -> bool:
        """
        Initialize DVC in the project.
        
        Returns:
            True if successful
        """
        if not self.dvc_available:
            logger.error("DVC not installed. Run: pip install dvc")
            return False
        
        # Check if already initialized
        if (self.project_root / ".dvc").exists():
            logger.info("DVC already initialized")
            return True
        
        # Initialize DVC
        result = self._run_dvc(["init"])
        if result.returncode != 0:
            logger.error(f"DVC init failed: {result.stderr}")
            return False
        
        # Configure local remote
        self.configure_remote()
        
        logger.info("✅ DVC initialized successfully")
        return True
    
    def configure_remote(self, force: bool = False) -> bool:
        """
        Configure the local DVC remote.
        
        Args:
            force: Overwrite existing configuration
            
        Returns:
            True if successful
        """
        storage_path = str(self.config.storage_path.resolve())
        
        # Check if remote exists
        if not force:
            result = self._run_dvc(["remote", "list"])
            if self.config.remote_name in result.stdout:
                logger.info(f"Remote '{self.config.remote_name}' already configured")
                return True
        
        # Add/modify remote
        action = "modify" if force else "add"
        result = self._run_dvc([
            "remote", action, "-f" if force else "",
            self.config.remote_name, storage_path
        ])
        
        # Set as default
        self._run_dvc(["remote", "default", self.config.remote_name])
        
        logger.info(f"✅ Remote configured: {storage_path}")
        return True
    
    def track_model(
        self,
        model_type: str,
        model_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Track a model with DVC.
        
        Args:
            model_type: Type of model (brain, voice, etc.)
            model_path: Path to model (uses default if not specified)
            
        Returns:
            Tracking result
        """
        if not self.dvc_available:
            return {"success": False, "error": "DVC not available"}
        
        # Determine path
        if model_path is None:
            rel_path = self.config.model_dirs.get(model_type)
            if not rel_path:
                return {"success": False, "error": f"Unknown model type: {model_type}"}
            model_path = self.project_root / rel_path
        else:
            model_path = Path(model_path)
        
        if not model_path.exists():
            return {"success": False, "error": f"Path not found: {model_path}"}
        
        # Track with DVC
        result = self._run_dvc(["add", str(model_path)])
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        # Stage the .dvc file
        dvc_file = Path(str(model_path) + ".dvc")
        if dvc_file.exists():
            self._run_git(["add", str(dvc_file)])
        
        logger.info(f"✅ Tracked: {model_path}")
        
        return {
            "success": True,
            "model_type": model_type,
            "path": str(model_path),
            "dvc_file": str(dvc_file) if dvc_file.exists() else None
        }
    
    def push_models(self) -> Dict[str, Any]:
        """
        Push all tracked models to remote storage.
        
        Returns:
            Push result
        """
        if not self.dvc_available:
            return {"success": False, "error": "DVC not available"}
        
        result = self._run_dvc(["push"])
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        logger.info("✅ Models pushed to storage")
        return {"success": True, "output": result.stdout}
    
    def pull_models(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Pull models from remote storage.
        
        Args:
            model_type: Specific model to pull, or all if None
            
        Returns:
            Pull result
        """
        if not self.dvc_available:
            return {"success": False, "error": "DVC not available"}
        
        if model_type:
            rel_path = self.config.model_dirs.get(model_type)
            if rel_path:
                result = self._run_dvc(["pull", rel_path])
            else:
                return {"success": False, "error": f"Unknown model type: {model_type}"}
        else:
            result = self._run_dvc(["pull"])
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        logger.info("✅ Models pulled from storage")
        return {"success": True, "output": result.stdout}
    
    def create_version(
        self,
        version: str,
        model_type: str,
        metrics: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a version tag for a model.
        
        Args:
            version: Version string (e.g., "v1.0.0")
            model_type: Type of model
            metrics: Optional metrics to store
            message: Tag message
            
        Returns:
            Version result
        """
        tag_name = f"{model_type}-{version}"
        
        # Save metrics if provided
        if metrics:
            self.log_metrics(model_type, version, metrics)
        
        # Create git tag
        tag_message = message or f"Sisi Lola {model_type} {version}"
        result = self._run_git(["tag", "-a", tag_name, "-m", tag_message])
        
        if result.returncode != 0:
            # Tag might already exist
            if "already exists" in result.stderr:
                logger.warning(f"Tag {tag_name} already exists")
            else:
                return {"success": False, "error": result.stderr}
        
        logger.info(f"✅ Created version: {tag_name}")
        
        return {
            "success": True,
            "tag": tag_name,
            "model_type": model_type,
            "version": version,
            "metrics": metrics
        }
    
    def log_metrics(
        self,
        model_type: str,
        version: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log training metrics.
        
        Args:
            model_type: Type of model
            version: Model version
            metrics: Metrics dictionary
        """
        metrics_dir = self.project_root / "metrics"
        metrics_dir.mkdir(exist_ok=True)
        
        metrics_file = metrics_dir / f"{model_type}_{version.replace('.', '_')}.json"
        
        # Add metadata
        full_metrics = {
            "model_type": model_type,
            "version": version,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
        
        metrics_file.write_text(json.dumps(full_metrics, indent=2))
        logger.info(f"📊 Metrics logged: {metrics_file}")
    
    def get_version_history(self, model_type: str) -> List[Dict[str, Any]]:
        """
        Get version history for a model.
        
        Args:
            model_type: Type of model
            
        Returns:
            List of versions
        """
        result = self._run_git(["tag", "-l", f"{model_type}-*"])
        
        if result.returncode != 0:
            return []
        
        versions = []
        for tag in result.stdout.strip().split('\n'):
            if tag:
                # Get tag details
                details = self._run_git(["show", tag, "--quiet", "--format=%ai|%s"])
                parts = details.stdout.strip().split('|')
                
                versions.append({
                    "tag": tag,
                    "version": tag.replace(f"{model_type}-", ""),
                    "date": parts[0] if parts else None,
                    "message": parts[1] if len(parts) > 1 else None
                })
        
        return sorted(versions, key=lambda x: x.get("date", ""), reverse=True)
    
    def checkout_version(
        self,
        model_type: str,
        version: str
    ) -> Dict[str, Any]:
        """
        Checkout a specific model version.
        
        Args:
            model_type: Type of model
            version: Version to checkout
            
        Returns:
            Checkout result
        """
        tag_name = f"{model_type}-{version}"
        
        # Get the DVC file at that version
        rel_path = self.config.model_dirs.get(model_type)
        if not rel_path:
            return {"success": False, "error": f"Unknown model type: {model_type}"}
        
        dvc_file = f"{rel_path}.dvc"
        
        # Checkout the specific .dvc file
        result = self._run_git(["checkout", tag_name, "--", dvc_file])
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        # Pull the model data
        self._run_dvc(["checkout", rel_path])
        
        logger.info(f"✅ Checked out: {tag_name}")
        
        return {
            "success": True,
            "tag": tag_name,
            "model_type": model_type,
            "version": version
        }
    
    def status(self) -> Dict[str, Any]:
        """
        Get DVC status.
        
        Returns:
            Status information
        """
        if not self.dvc_available:
            return {"error": "DVC not available"}
        
        result = self._run_dvc(["status"])
        
        return {
            "status": result.stdout,
            "remote": str(self.config.storage_path),
            "tracked_models": list(self.config.model_dirs.keys())
        }
    
    def get_metrics(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all logged metrics.
        
        Args:
            model_type: Filter by model type
            
        Returns:
            List of metrics
        """
        metrics_dir = self.project_root / "metrics"
        if not metrics_dir.exists():
            return []
        
        metrics_list = []
        
        for metrics_file in metrics_dir.glob("*.json"):
            try:
                data = json.loads(metrics_file.read_text())
                if model_type is None or data.get("model_type") == model_type:
                    metrics_list.append(data)
            except Exception as e:
                logger.warning(f"Could not read {metrics_file}: {e}")
        
        return sorted(metrics_list, key=lambda x: x.get("timestamp", ""), reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def track_model(model_type: str, model_path: Optional[str] = None) -> Dict[str, Any]:
    """Track a model with DVC."""
    manager = DVCManager()
    return manager.track_model(model_type, model_path)


def create_version(
    version: str,
    model_type: str,
    metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a model version."""
    manager = DVCManager()
    return manager.create_version(version, model_type, metrics)


def get_versions(model_type: str) -> List[Dict[str, Any]]:
    """Get version history."""
    manager = DVCManager()
    return manager.get_version_history(model_type)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="DVC Model Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init
    subparsers.add_parser("init", help="Initialize DVC")
    
    # Track
    track_parser = subparsers.add_parser("track", help="Track a model")
    track_parser.add_argument("--model-type", "-m", required=True)
    track_parser.add_argument("--path", "-p")
    
    # Push
    subparsers.add_parser("push", help="Push models")
    
    # Pull
    pull_parser = subparsers.add_parser("pull", help="Pull models")
    pull_parser.add_argument("--model-type", "-m")
    
    # Version
    version_parser = subparsers.add_parser("version", help="Create version")
    version_parser.add_argument("--model-type", "-m", required=True)
    version_parser.add_argument("--version", "-v", required=True)
    version_parser.add_argument("--message", help="Tag message")
    
    # History
    history_parser = subparsers.add_parser("history", help="Version history")
    history_parser.add_argument("--model-type", "-m", required=True)
    
    # Status
    subparsers.add_parser("status", help="DVC status")
    
    args = parser.parse_args()
    manager = DVCManager()
    
    if args.command == "init":
        manager.init()
    
    elif args.command == "track":
        result = manager.track_model(args.model_type, args.path)
        print(json.dumps(result, indent=2))
    
    elif args.command == "push":
        result = manager.push_models()
        print(json.dumps(result, indent=2))
    
    elif args.command == "pull":
        result = manager.pull_models(args.model_type)
        print(json.dumps(result, indent=2))
    
    elif args.command == "version":
        result = manager.create_version(args.version, args.model_type, message=args.message)
        print(json.dumps(result, indent=2))
    
    elif args.command == "history":
        versions = manager.get_version_history(args.model_type)
        print(json.dumps(versions, indent=2))
    
    elif args.command == "status":
        status = manager.status()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()
