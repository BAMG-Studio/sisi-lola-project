"""Webhook Service Module - FastAPI webhook receiver."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from .app import app

__all__ = ["app"]
