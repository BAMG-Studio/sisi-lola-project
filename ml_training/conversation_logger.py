#!/usr/bin/env python3
"""
Conversation Logger for Sisi Lola
Logs chatbox interactions for training data ingestion and model fine-tuning
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
import uuid

class ConversationLogger:
    """
    Logs conversations from Sisi Lola chatbox for training data collection.
    Based on recommendations from Perplexity search results.
    """
    
    def __init__(self, log_dir: str = "ml_training/data/chat_logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.raw_log_file = os.path.join(self.log_dir, "chat_logs_raw.jsonl")
        
    def log_interaction(self,
                       session_id: str,
                       user_message: str,
                       model_response: str,
                       model_used: str = "N-ATLaS",
                       metadata: Optional[Dict] = None,
                       rating: Optional[int] = None,
                       keep_for_training: bool = True) -> str:
        """
        Log a single conversation turn.
        
        Args:
            session_id: Unique session identifier
            user_message: User's input message
            model_response: Model's generated response
            model_used: Name of the model used
            metadata: Additional context (platform, language, etc.)
            rating: Optional quality rating (1-5)
            keep_for_training: Flag to mark for training inclusion
            
        Returns:
            interaction_id: Unique ID for this interaction
        """
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            "interaction_id": interaction_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "user_message": user_message,
            "model_response": model_response,
            "model_used": model_used,
            "rating": rating,
            "keep_for_training": keep_for_training,
            "metadata": metadata or {}
        }
        
        # Append to JSONL file
        with open(self.raw_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        return interaction_id
    
    def log_conversation(self,
                        session_id: str,
                        conversation: List[Dict],
                        metadata: Optional[Dict] = None):
        """
        Log a full conversation with multiple turns.
        
        Args:
            session_id: Unique session identifier
            conversation: List of {"role": "user"|"assistant", "content": str}
            metadata: Session-level metadata
        """
        for i in range(0, len(conversation) - 1, 2):
            if i + 1 < len(conversation):
                user_msg = conversation[i]
                assistant_msg = conversation[i + 1]
                
                if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                    self.log_interaction(
                        session_id=session_id,
                        user_message=user_msg.get("content", ""),
                        model_response=assistant_msg.get("content", ""),
                        metadata=metadata
                    )
    
    def update_rating(self, interaction_id: str, rating: int):
        """
        Update the rating for a logged interaction.
        Reads all logs, updates the specific entry, and rewrites.
        """
        if not os.path.exists(self.raw_log_file):
            return
        
        logs = []
        with open(self.raw_log_file, "r", encoding="utf-8") as f:
            for line in f:
                log = json.loads(line.strip())
                if log.get("interaction_id") == interaction_id:
                    log["rating"] = rating
                logs.append(log)
        
        # Rewrite file
        with open(self.raw_log_file, "w", encoding="utf-8") as f:
            for log in logs:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve recent conversation logs.
        """
        if not os.path.exists(self.raw_log_file):
            return []
        
        logs = []
        with open(self.raw_log_file, "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line.strip()))
        
        return logs[-limit:]


if __name__ == "__main__":
    # Test the logger
    logger = ConversationLogger()
    
    test_session = str(uuid.uuid4())
    
    # Log a test interaction
    interaction_id = logger.log_interaction(
        session_id=test_session,
        user_message="How can I learn DevSecOps in Nigeria?",
        model_response="Omo, DevSecOps na very important skill o! You fit start with free resources like LinkedIn Learning and GitHub Actions. E choke!",
        model_used="N-ATLaS",
        metadata={"language": "english_nigerian", "topic": "devsecops"},
        rating=5,
        keep_for_training=True
    )
    
    print(f"Logged interaction: {interaction_id}")
    print(f"Recent logs: {len(logger.get_recent_logs())}")
