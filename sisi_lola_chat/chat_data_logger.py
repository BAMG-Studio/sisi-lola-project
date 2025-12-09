"""
SISI LOLA CHAT DATA LOGGER
===========================
Collects chat conversations for retraining and fine-tuning.

This creates a feedback loop:
Chat → Database → Export → Training → Better Chat

Features:
- Automatic logging of all conversations
- Quality ratings for RLHF
- Voice feedback collection
- Export to JSONL for training
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import uuid


class ChatDataLogger:
    """
    Logs all chat interactions for future training.
    
    Usage:
        logger = ChatDataLogger()
        conv_id = logger.start_conversation("gpt4", "elevenlabs")
        msg_id = logger.log_message(conv_id, "user", "How you dey?")
        msg_id = logger.log_message(conv_id, "assistant", "I dey kampe!")
        logger.rate_response(msg_id, response_rating=5)
        logger.export_for_training()
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "ml_training" / "data" / "chat_training_data.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT,
                voice_engine TEXT,
                total_turns INTEGER DEFAULT 0,
                session_notes TEXT
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT,  -- 'user' or 'assistant'
                content TEXT,
                content_hash TEXT,  -- SHA256 hash for deduplication
                -- Quality ratings (for RLHF)
                response_rating INTEGER,  -- 1-5 scale
                voice_naturalness INTEGER,  -- 1-5 scale
                humor_rating INTEGER,  -- 1-5 scale
                cultural_authenticity INTEGER,  -- 1-5 scale
                nigerian_language_quality INTEGER,  -- 1-5 scale for Yoruba/Pidgin accuracy
                -- Safety and training flags
                safety_flag BOOLEAN DEFAULT 0,  -- Mark risky/sensitive content
                do_not_train BOOLEAN DEFAULT 0,  -- Exclude from training export
                -- Metadata
                tokens_used INTEGER,
                generation_time_ms INTEGER,
                model_temperature REAL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        # Voice feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                audio_path TEXT,
                voice_engine TEXT,
                is_natural BOOLEAN,
                pronunciation_issues TEXT,  -- JSON list of problematic words
                intonation_quality INTEGER,  -- 1-5 scale
                accent_authenticity INTEGER,  -- 1-5 scale for Nigerian accent
                user_notes TEXT,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')
        
        # Training exports table (track what was exported)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                message_count INTEGER,
                min_rating_filter INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[OK] Chat data logger initialized: {self.db_path}")
    
    def start_conversation(self, model: str, voice_engine: str = None) -> str:
        """Start a new conversation session"""
        conversation_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO conversations (id, model_used, voice_engine) VALUES (?, ?, ?)',
            (conversation_id, model, voice_engine)
        )
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def log_message(self, 
                    conversation_id: str,
                    role: str,
                    content: str,
                    tokens: int = 0,
                    gen_time_ms: int = 0,
                    temperature: float = None) -> int:
        """
        Log a single message.
        
        Args:
            conversation_id: The conversation session ID
            role: 'user' or 'assistant'
            content: The message text
            tokens: Number of tokens used (for assistant messages)
            gen_time_ms: Generation time in milliseconds
            temperature: Model temperature used
            
        Returns:
            message_id: ID of the logged message (use for rating)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages 
            (conversation_id, role, content, tokens_used, generation_time_ms, model_temperature)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (conversation_id, role, content, tokens, gen_time_ms, temperature))
        
        message_id = cursor.lastrowid
        
        # Update conversation turn count
        cursor.execute(
            'UPDATE conversations SET total_turns = total_turns + 1 WHERE id = ?',
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def rate_response(self, 
                      message_id: int, 
                      response_rating: int = None,
                      voice_naturalness: int = None,
                      humor_rating: int = None,
                      cultural_authenticity: int = None,
                      nigerian_language_quality: int = None):
        """
        Add quality ratings to a response (for RLHF).
        
        All ratings are on a 1-5 scale:
        1 = Poor, 2 = Below Average, 3 = Average, 4 = Good, 5 = Excellent
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if response_rating is not None:
            updates.append('response_rating = ?')
            values.append(min(5, max(1, response_rating)))
        if voice_naturalness is not None:
            updates.append('voice_naturalness = ?')
            values.append(min(5, max(1, voice_naturalness)))
        if humor_rating is not None:
            updates.append('humor_rating = ?')
            values.append(min(5, max(1, humor_rating)))
        if cultural_authenticity is not None:
            updates.append('cultural_authenticity = ?')
            values.append(min(5, max(1, cultural_authenticity)))
        if nigerian_language_quality is not None:
            updates.append('nigerian_language_quality = ?')
            values.append(min(5, max(1, nigerian_language_quality)))
        
        if updates:
            values.append(message_id)
            cursor.execute(
                f'UPDATE messages SET {", ".join(updates)} WHERE id = ?',
                values
            )
            conn.commit()
        
        conn.close()
    
    def log_voice_feedback(self,
                           message_id: int,
                           audio_path: str,
                           voice_engine: str,
                           is_natural: bool,
                           pronunciation_issues: List[str] = None,
                           intonation_quality: int = None,
                           accent_authenticity: int = None,
                           notes: str = None):
        """
        Log detailed feedback about voice quality.
        
        Args:
            message_id: ID of the message that was spoken
            audio_path: Path to the generated audio file
            voice_engine: Which engine was used (elevenlabs, coqui, edge, etc.)
            is_natural: Did the voice sound natural?
            pronunciation_issues: List of words that were mispronounced
            intonation_quality: 1-5 scale
            accent_authenticity: 1-5 scale for Nigerian accent quality
            notes: Free-form notes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO voice_feedback 
            (message_id, audio_path, voice_engine, is_natural, 
             pronunciation_issues, intonation_quality, accent_authenticity, user_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_id, 
            audio_path, 
            voice_engine, 
            is_natural, 
            json.dumps(pronunciation_issues or []), 
            intonation_quality,
            accent_authenticity,
            notes
        ))
        
        conn.commit()
        conn.close()
    
    def export_for_training(self, 
                            output_path: str = None, 
                            min_rating: int = 3,
                            include_unrated: bool = True) -> str:
        """
        Export high-quality conversations for training.
        
        Args:
            output_path: Where to save the JSONL file
            min_rating: Minimum response_rating to include (1-5)
            include_unrated: Include messages without ratings
        
        Returns:
            Path to the generated JSONL file
        """
        if output_path is None:
            export_dir = self.db_path.parent / "exports"
            export_dir.mkdir(exist_ok=True)
            output_path = export_dir / f"training_export_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query based on filters
        if include_unrated:
            cursor.execute('''
                SELECT c.id, c.model_used, m.role, m.content, m.response_rating,
                       m.humor_rating, m.cultural_authenticity, m.nigerian_language_quality
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.response_rating IS NULL OR m.response_rating >= ?
                ORDER BY c.id, m.timestamp
            ''', (min_rating,))
        else:
            cursor.execute('''
                SELECT c.id, c.model_used, m.role, m.content, m.response_rating,
                       m.humor_rating, m.cultural_authenticity, m.nigerian_language_quality
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.response_rating >= ?
                ORDER BY c.id, m.timestamp
            ''', (min_rating,))
        
        rows = cursor.fetchall()
        
        # Group by conversation
        conversations = {}
        for conv_id, model, role, content, rating, humor, cultural, nigerian in rows:
            if conv_id not in conversations:
                conversations[conv_id] = {"model": model, "messages": []}
            conversations[conv_id]["messages"].append({
                "role": role,
                "content": content,
                "ratings": {
                    "overall": rating,
                    "humor": humor,
                    "cultural": cultural,
                    "nigerian_language": nigerian
                }
            })
        
        # Write training data in multiple formats
        examples_count = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            for conv_id, conv_data in conversations.items():
                messages = conv_data["messages"]
                
                # Format 1: Instruction-Response pairs
                for i in range(0, len(messages) - 1, 2):
                    if i + 1 < len(messages):
                        user_msg = messages[i]
                        assistant_msg = messages[i + 1]
                        
                        if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                            training_example = {
                                "instruction": user_msg["content"],
                                "output": assistant_msg["content"],
                                "source": "sisi_lola_chat",
                                "model": conv_data["model"],
                                "ratings": assistant_msg["ratings"]
                            }
                            f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
                            examples_count += 1
        
        # Log the export
        cursor.execute('''
            INSERT INTO exports (file_path, message_count, min_rating_filter)
            VALUES (?, ?, ?)
        ''', (str(output_path), examples_count, min_rating))
        conn.commit()
        conn.close()
        
        print(f"✓ Exported {examples_count} training examples to {output_path}")
        return str(output_path)
    
    def export_voice_feedback(self, output_path: str = None) -> str:
        """Export voice feedback for voice model improvement"""
        if output_path is None:
            export_dir = self.db_path.parent / "exports"
            export_dir.mkdir(exist_ok=True)
            output_path = export_dir / f"voice_feedback_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT vf.*, m.content
            FROM voice_feedback vf
            JOIN messages m ON vf.message_id = m.id
            ORDER BY vf.id
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for row in rows:
                feedback = dict(zip(columns, row))
                if 'pronunciation_issues' in feedback:
                    feedback['pronunciation_issues'] = json.loads(feedback['pronunciation_issues'])
                f.write(json.dumps(feedback, ensure_ascii=False) + '\n')
        
        print(f"✓ Exported voice feedback to {output_path}")
        return str(output_path)
    
    def get_stats(self) -> Dict:
        """Get statistics about collected data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        stats['total_conversations'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages')
        stats['total_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages WHERE role = "assistant"')
        stats['assistant_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages WHERE response_rating IS NOT NULL')
        stats['rated_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(response_rating) FROM messages WHERE response_rating IS NOT NULL')
        avg = cursor.fetchone()[0]
        stats['avg_rating'] = round(avg, 2) if avg else None
        
        cursor.execute('SELECT AVG(humor_rating) FROM messages WHERE humor_rating IS NOT NULL')
        avg = cursor.fetchone()[0]
        stats['avg_humor_rating'] = round(avg, 2) if avg else None
        
        cursor.execute('SELECT AVG(cultural_authenticity) FROM messages WHERE cultural_authenticity IS NOT NULL')
        avg = cursor.fetchone()[0]
        stats['avg_cultural_rating'] = round(avg, 2) if avg else None
        
        cursor.execute('SELECT COUNT(*) FROM voice_feedback')
        stats['voice_feedback_count'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM voice_feedback WHERE is_natural = 1')
        stats['natural_voice_count'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT model_used, COUNT(*) FROM conversations GROUP BY model_used')
        stats['conversations_by_model'] = dict(cursor.fetchall())
        
        cursor.execute('SELECT voice_engine, COUNT(*) FROM conversations WHERE voice_engine IS NOT NULL GROUP BY voice_engine')
        stats['conversations_by_voice'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def get_low_rated_responses(self, max_rating: int = 2) -> List[Dict]:
        """Get responses that need improvement (for review)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.content, m.response_rating, 
                   (SELECT content FROM messages WHERE conversation_id = m.conversation_id 
                    AND timestamp < m.timestamp ORDER BY timestamp DESC LIMIT 1) as user_message
            FROM messages m
            WHERE m.role = 'assistant' AND m.response_rating <= ?
            ORDER BY m.response_rating ASC
        ''', (max_rating,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "response": row[1],
                "rating": row[2],
                "user_message": row[3]
            }
            for row in rows
        ]


# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Chat Data Logger")
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', action='store_true', help='Export training data')
    parser.add_argument('--export-voice', action='store_true', help='Export voice feedback')
    parser.add_argument('--min-rating', type=int, default=3, help='Minimum rating for export')
    parser.add_argument('--low-rated', action='store_true', help='Show low-rated responses')
    
    args = parser.parse_args()
    
    logger = ChatDataLogger()
    
    if args.stats:
        stats = logger.get_stats()
        print("\n📊 Sisi Lola Chat Training Data Stats")
        print("=" * 50)
        print(f"Total Conversations: {stats['total_conversations']}")
        print(f"Total Messages: {stats['total_messages']}")
        print(f"Assistant Messages: {stats['assistant_messages']}")
        print(f"Rated Messages: {stats['rated_messages']}")
        print(f"Average Rating: {stats['avg_rating'] or 'N/A'}/5")
        print(f"Avg Humor Rating: {stats['avg_humor_rating'] or 'N/A'}/5")
        print(f"Avg Cultural Rating: {stats['avg_cultural_rating'] or 'N/A'}/5")
        print(f"\nVoice Feedback: {stats['voice_feedback_count']}")
        print(f"Natural Voice Count: {stats['natural_voice_count']}")
        print(f"\nBy Model: {stats['conversations_by_model']}")
        print(f"By Voice: {stats['conversations_by_voice']}")
    
    if args.export:
        logger.export_for_training(min_rating=args.min_rating)
    
    if args.export_voice:
        logger.export_voice_feedback()
    
    if args.low_rated:
        low = logger.get_low_rated_responses()
        print(f"\n🔍 Low-Rated Responses ({len(low)} found)")
        for item in low[:10]:
            print(f"\nID: {item['id']} | Rating: {item['rating']}/5")
            print(f"User: {item['user_message'][:100]}...")
            print(f"Sisi: {item['response'][:100]}...")
