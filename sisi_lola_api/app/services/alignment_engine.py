"""
SISI LOLA ALIGNMENT ENGINE
Automates political, cultural, and behavioral alignment based on user interactions.
Ensures Sisi Lola stays true to her "Africa's AI Virtual Host" ideals.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AlignmentEngine:
    def __init__(self, memory_bank=None):
        self.memory_bank = memory_bank
        self.alignment_cache = {}
        
    def get_cultural_aura(self, session_id: str) -> str:
        """
        Generates a dynamic "Aura" prompt based on the user's cultural context 
        extracted from the memory bank.
        """
        if not self.memory_bank:
            return ""
            
        facts = self.memory_bank.get_user_facts(session_id)
        if not facts:
            return ""
            
        # Extract location and cultural markers
        location = facts.get("location", "Africa")
        interest = facts.get("interest", "Afrobeats and Tech")
        name = facts.get("name", "Friend")
        
        aura = f"""
        [CULTURAL AURA ACTIVE]
        - Current Context: You are speaking with {name} from {location}.
        - Interaction Style: Prioritize topics related to {interest}.
        - Geographic Alignment: Use local Lagos/African references specifically relevant to {location}.
        """
        return aura

    def log_alignment_feedback(self, session_id: str, feedback_type: str, details: str):
        """Logs behavior that needs alignment (e.g. user corrected a fact or accent)"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "type": feedback_type,
            "details": details
        }
        
        # Save to a local alignment file for future fine-tuning
        log_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "alignment_logs.jsonl")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        logger.info(f"📊 Alignment feedback logged for session {session_id}")

# Global instance
alignment_engine = AlignmentEngine()
