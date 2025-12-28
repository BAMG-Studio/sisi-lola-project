"""
SISI LOLA CONVERSATION LOGGER
==============================
Logs all conversations for:
1. Training data refinement
2. Knowledge expansion
3. Performance analytics
4. Error tracking

Stores to local SQLite for dev, can sync to Modal/Cloud for production.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import sqlite3
from threading import Lock

# Database path
LOG_DB_PATH = Path(os.getenv("CONVERSATION_LOG_DB", "sisi_lola_api/data/conversation_logs.db"))
LOG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_db_lock = Lock()


def init_log_db():
    """Initialize the conversation logging database."""
    with sqlite3.connect(str(LOG_DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT NOT NULL,
                sisi_response TEXT,
                scenario TEXT,
                response_time_ms INTEGER,
                model_used TEXT,
                error TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                ip_address TEXT,
                platform TEXT DEFAULT 'web'
            )
        """)
        
        # Index for efficient querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON conversations(created_at)")
        
        conn.commit()
        print(f"📊 Conversation logging initialized at {LOG_DB_PATH}")


def log_conversation(
    user_message: str,
    sisi_response: str,
    session_id: Optional[str] = None,
    scenario: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    model_used: Optional[str] = None,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    platform: str = "web"
):
    """
    Log a conversation exchange for training refinement.
    
    Args:
        user_message: What the user said
        sisi_response: What Sisi responded
        session_id: Unique session identifier
        scenario: The vibe/scenario selected
        response_time_ms: How long inference took
        model_used: Which model was used (Gemini, OpenAI, etc.)
        error: Any error that occurred
        metadata: Additional data (e.g., thought process)
        ip_address: For rate limiting
        platform: web, api, modal, etc.
    """
    with _db_lock:
        try:
            with sqlite3.connect(str(LOG_DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations 
                    (session_id, user_message, sisi_response, scenario, response_time_ms, 
                     model_used, error, metadata, created_at, ip_address, platform)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    user_message,
                    sisi_response,
                    scenario,
                    response_time_ms,
                    model_used,
                    error,
                    json.dumps(metadata) if metadata else None,
                    datetime.now().isoformat(),
                    ip_address,
                    platform
                ))
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Conversation logging error: {e}")


def get_recent_conversations(limit: int = 100, session_id: Optional[str] = None) -> list:
    """Get recent conversations for review/training."""
    with sqlite3.connect(str(LOG_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM conversations 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]


def export_training_data(output_path: Optional[str] = None, min_quality: bool = True) -> str:
    """
    Export conversations as JSONL for fine-tuning.
    
    Args:
        output_path: Where to save the export
        min_quality: Only export successful conversations (no errors)
    """
    output_path = output_path or f"sisi_lola_api/data/training_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    with sqlite3.connect(str(LOG_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM conversations"
        if min_quality:
            query += " WHERE error IS NULL AND sisi_response IS NOT NULL"
        query += " ORDER BY created_at"
        
        cursor.execute(query)
        rows = cursor.fetchall()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for row in rows:
            entry = {
                "messages": [
                    {"role": "user", "content": row["user_message"]},
                    {"role": "assistant", "content": row["sisi_response"]}
                ],
                "scenario": row["scenario"],
                "model": row["model_used"],
                "timestamp": row["created_at"]
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"📦 Exported {len(rows)} conversations to {output_path}")
    return output_path


def get_conversation_stats() -> Dict[str, Any]:
    """Get stats about logged conversations."""
    with sqlite3.connect(str(LOG_DB_PATH)) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE error IS NULL")
        successful = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
        unique_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(response_time_ms) FROM conversations WHERE response_time_ms IS NOT NULL")
        avg_response_time = cursor.fetchone()[0]
        
        return {
            "total_conversations": total,
            "successful_conversations": successful,
            "unique_sessions": unique_sessions,
            "avg_response_time_ms": round(avg_response_time or 0, 2),
            "success_rate": round((successful / total * 100) if total > 0 else 0, 2)
        }


# Initialize on import
init_log_db()
