"""
SISI LOLA DATA FORGE
====================
The continuous retraining pipeline core.
Captures high-quality interactions and multimodal insights
into a dataset ready for daily LoRA/Fine-tuning.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("data_forge")

class DataForge:
    def __init__(self, data_root: str = "sisi_lola_api/data/training"):
        self.data_root = Path(data_root)
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_root / "interactions.jsonl"
        self.curated_file = self.data_root / "curated_dataset.jsonl"

    def log_interaction(self, input_data: str, response_data: str, metadata: Dict[str, Any] = None):
        """Log a successful interaction for future retraining"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "instruction": "Continue the conversation as Sisi Lola, reflecting her authentic Nigerian personality.",
            "input": input_data,
            "output": response_data,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"DataForge log failed: {e}")

    def ingest_multimodal_gist(self, gist_info: Dict[str, Any]):
        """Log extractions from YouTube/Web for language pattern training"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "multimodal_knowledge",
            "content": gist_info.get("extracted_text"),
            "source": gist_info.get("metadata", {}).get("video_url") or gist_info.get("metadata", {}).get("url"),
            "language_analysis": gist_info.get("language_analysis")
        }
        
        gist_log = self.data_root / "multimodal_gists.jsonl"
        with open(gist_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def prepare_github_action_export(self) -> str:
        """Packages the logs for GitHub Action download"""
        # This could zip the jsonl files or just return the path
        return str(self.log_file)

# Singleton
data_forge = DataForge()
