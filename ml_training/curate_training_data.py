#!/usr/bin/env python3
"""
Training Data Curation Pipeline for Sisi Lola
Filters and transforms chatbox logs into instruction-following training examples
Based on N-ATLaS training requirements
"""

import json
import os
from typing import List, Dict
from datetime import datetime

class TrainingDataCurator:
    """
    Curates chat logs into training-ready instruction format for N-ATLaS fine-tuning.
    """
    
    def __init__(self, 
                 raw_logs_file: str = "ml_training/data/chat_logs/chat_logs_raw.jsonl",
                 output_file: str = "ml_training/data/sisi_lola_chat_instructions.jsonl"):
        self.raw_logs_file = raw_logs_file
        self.output_file = output_file
        self.personality_system_prompt = self._load_personality_prompt()
        
    def _load_personality_prompt(self) -> str:
        """
        Load Sisi Lola's personality system prompt
        """
        return """You are Sisi Lola, a confident, funny, and charismatic Nigerian virtual host.

Personality traits:
- Confidence: 8.5/10
- Humor: 8.5/10 ✨  
- Charisma: 9.0/10 ✨
- Authenticity: 9.0/10
- Empowerment: 9.0/10

Communication style:
- Mix English and Nigerian Pidgin naturally
- Use observational humor and witty wordplay
- Tell stories with charismatic energy
- Use catchphrases: "Omo see gobe!", "E choke!", "Las las, we go dey alright!"

You help with:
- DevSecOps explanations in Naija context
- Social media and creator advice
- Diaspora life discussions
- Nigerian culture and technology

Always be authentic, empowering, and culturally grounded."""
    
    def _quality_filter(self, log_entry: Dict) -> bool:
        """
        Filter for high-quality interactions worth training on.
        
        Criteria:
        - Must be marked for training
        - Rating >= 3 (if rated)
        - Non-empty messages
        - No toxic/spam content (basic check)
        """
        # Must be marked for training
        if not log_entry.get("keep_for_training", False):
            return False
        
        # Check rating if present
        rating = log_entry.get("rating")
        if rating is not None and rating < 3:
            return False
        
        # Non-empty messages
        user_msg = log_entry.get("user_message", "").strip()
        model_resp = log_entry.get("model_response", "").strip()
        
        if not user_msg or not model_resp:
            return False
        
        # Basic spam/toxic filter (expand this as needed)
        spam_keywords = ["spam", "scam", "click here", "buy now"]
        toxic_keywords = ["hate", "kill", "die"]
        
        text_lower = (user_msg + " " + model_resp).lower()
        
        for keyword in spam_keywords + toxic_keywords:
            if keyword in text_lower:
                return False
        
        return True
    
    def _convert_to_instruction_format(self, log_entry: Dict) -> Dict:
        """
        Convert a chat log entry to instruction-following format.
        
        Format:
        {
            "system": <personality_prompt>,
            "user": <user_message>,
            "assistant": <model_response>,
            "metadata": {...}
        }
        """
        return {
            "system": self.personality_system_prompt,
            "user": log_entry["user_message"],
            "assistant": log_entry["model_response"],
            "metadata": {
                "interaction_id": log_entry["interaction_id"],
                "timestamp": log_entry["timestamp"],
                "model_used": log_entry["model_used"],
                "rating": log_entry.get("rating"),
                **log_entry.get("metadata", {})
            }
        }
    
    def curate(self, min_quality_score: int = 3) -> int:
        """
        Process raw logs and create curated training data.
        
        Returns:
            Number of training examples created
        """
        if not os.path.exists(self.raw_logs_file):
            print(f"No raw logs found at {self.raw_logs_file}")
            return 0
        
        # Read all raw logs
        raw_logs = []
        with open(self.raw_logs_file, "r", encoding="utf-8") as f:
            for line in f:
                raw_logs.append(json.loads(line.strip()))
        
        print(f"Processing {len(raw_logs)} raw log entries...")
        
        # Filter and convert
        training_examples = []
        for log in raw_logs:
            if self._quality_filter(log):
                training_examples.append(self._convert_to_instruction_format(log))
        
        # Write curated data
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, "w", encoding="utf-8") as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
        
        print(f"Created {len(training_examples)} training examples")
        print(f"Output: {self.output_file}")
        
        return len(training_examples)
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the curated dataset.
        """
        if not os.path.exists(self.output_file):
            return {"total_examples": 0}
        
        examples = []
        with open(self.output_file, "r", encoding="utf-8") as f:
            for line in f:
                examples.append(json.loads(line.strip()))
        
        # Calculate stats
        languages = {}
        topics = {}
        
        for ex in examples:
            metadata = ex.get("metadata", {})
            lang = metadata.get("language", "unknown")
            topic = metadata.get("topic", "general")
            
            languages[lang] = languages.get(lang, 0) + 1
            topics[topic] = topics.get(topic, 0) + 1
        
        return {
            "total_examples": len(examples),
            "languages": languages,
            "topics": topics
        }


if __name__ == "__main__":
    curator = TrainingDataCurator()
    
    # Curate the data
    count = curator.curate()
    
    # Show stats
    stats = curator.get_stats()
    print("\nDataset Statistics:")
    print(json.dumps(stats, indent=2))
