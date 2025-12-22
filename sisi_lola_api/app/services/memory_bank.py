"""
SISI LOLA MEMORY BANK
Persistent storage for chat history and "Personal Facts" about the user.
Uses SQLite for lightweight, fast retrieval.
"""

import os
import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

class MemoryBank:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "sisilola_memory.db")
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            # 1. Chat History Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    language_tags TEXT,
                    timestamp INTEGER
                )
            """)
            # 2. User Profile / Facts Table (The "Personality Intelligence")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    fact_key TEXT,
                    fact_value TEXT,
                    importance REAL DEFAULT 1.0,
                    timestamp INTEGER,
                    UNIQUE(session_id, fact_key)
                )
            """)
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str, tags: List[str] = None):
        now = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO chat_history (session_id, role, content, language_tags, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, json.dumps(tags or []), now)
            )
            conn.commit()
            
    def get_history(self, session_id: str, limit: int = 15) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cur.fetchall()
            # Reverse to get chronological order
            return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def store_user_fact(self, session_id: str, key: str, value: str):
        now = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_facts (session_id, fact_key, fact_value, timestamp)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id, fact_key) DO UPDATE SET
                fact_value = excluded.fact_value,
                timestamp = excluded.timestamp
            """, (session_id, key, value, now))
            conn.commit()

    def get_user_facts(self, session_id: str) -> Dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT fact_key, fact_value FROM user_facts WHERE session_id = ?", (session_id,))
            rows = cur.fetchall()
            return {row[0]: row[1] for row in rows}

    def get_memory_context(self, session_id: str) -> str:
        """Constructs a memory summary for the system prompt"""
        facts = self.get_user_facts(session_id)
        if not facts:
            return ""
        
        summary = "\n[MEMORABLE FACTS ABOUT THIS USER]:\n"
        for k, v in facts.items():
            summary += f"- {k.replace('_', ' ').capitalize()}: {v}\n"
        return summary

# Global Singleton
memory_bank = MemoryBank()
