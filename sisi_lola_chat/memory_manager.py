"""
SISI LOLA SESSION & MEMORY MANAGEMENT
======================================
Manages conversation context, memory, and relationships:

1. SESSION MEMORY - Current conversation context
2. SHORT-TERM MEMORY - Recent interactions (24-48 hours)
3. LONG-TERM MEMORY - Persistent knowledge and relationships
4. CONTENT MEMORY - Processed content references

This enables Sisi Lola to:
- Remember what was discussed earlier in a session
- Reference past conversations with users
- Build relationships and personalize interactions
- Maintain context across content creation
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from collections import deque
import hashlib


@dataclass
class Message:
    """A single message in conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    message_id: Optional[str] = None
    
    # Metadata
    intent: Optional[str] = None  # generative, technical, conversational
    topics: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    
    # References
    content_ids: List[str] = field(default_factory=list)  # Referenced content
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_openai_format(self) -> Dict:
        """Convert to OpenAI message format"""
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class ContentReference:
    """Reference to processed content"""
    content_id: str
    title: str
    content_type: str  # video, audio, image, text
    source_url: Optional[str]
    summary: Optional[str]
    processed_at: str
    
    # Discussion tracking
    times_referenced: int = 0
    last_referenced: Optional[str] = None


@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Interaction stats
    total_messages: int = 0
    total_sessions: int = 0
    
    # Preferences (learned over time)
    preferred_topics: List[str] = field(default_factory=list)
    preferred_style: str = "casual"
    preferred_response_length: str = "medium"  # short, medium, long
    
    # Relationship
    nickname: Optional[str] = None  # What Sisi calls them
    relationship_level: int = 0  # 0-5 (stranger to bestie)
    
    # Content interaction
    content_created_for: List[str] = field(default_factory=list)
    content_discussed: List[str] = field(default_factory=list)


class SessionMemory:
    """
    Manages the current session context.
    
    Maintains:
    - Current conversation history
    - Active content references
    - Session-specific context
    """
    
    def __init__(self, max_messages: int = 50, max_tokens_estimate: int = 8000):
        self.session_id = self._generate_session_id()
        self.started_at = datetime.now().isoformat()
        
        self.messages: deque = deque(maxlen=max_messages)
        self.max_tokens = max_tokens_estimate
        
        # Active content in this session
        self.active_content: Dict[str, ContentReference] = {}
        
        # Session-level tracking
        self.topics_discussed: List[str] = []
        self.content_created: List[str] = []
        self.user_mood: Optional[str] = None
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def add_message(self, role: str, content: str, **metadata) -> Message:
        """Add a message to the session"""
        message = Message(
            role=role,
            content=content,
            message_id=f"{self.session_id}_{len(self.messages)}",
            **metadata
        )
        self.messages.append(message)
        
        # Update topics if provided
        if metadata.get('topics'):
            self.topics_discussed.extend(metadata['topics'])
        
        return message
    
    def add_content_reference(self, content_ref: ContentReference):
        """Add content reference to session"""
        self.active_content[content_ref.content_id] = content_ref
    
    def get_context_messages(self, max_messages: int = None) -> List[Dict]:
        """Get messages formatted for LLM context"""
        messages = list(self.messages)
        if max_messages:
            messages = messages[-max_messages:]
        return [m.to_openai_format() for m in messages]
    
    def get_summary(self) -> str:
        """Get a summary of the current session"""
        if not self.messages:
            return "No messages in current session."
        
        msg_count = len(self.messages)
        topics = list(set(self.topics_discussed))[:5]
        content_count = len(self.active_content)
        
        summary = f"Session {self.session_id}:\n"
        summary += f"- Messages: {msg_count}\n"
        summary += f"- Topics: {', '.join(topics) if topics else 'General chat'}\n"
        summary += f"- Content referenced: {content_count}\n"
        
        return summary
    
    def clear(self):
        """Clear session memory"""
        self.messages.clear()
        self.active_content.clear()
        self.topics_discussed.clear()
        self.content_created.clear()


class LongTermMemory:
    """
    Persistent memory stored in SQLite.
    
    Stores:
    - User profiles and relationships
    - Conversation summaries
    - Content references
    - Learned preferences
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).parent.parent / "ml_training" / "data" / "sisi_memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_messages INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                preferred_topics TEXT,  -- JSON list
                preferred_style TEXT DEFAULT 'casual',
                nickname TEXT,
                relationship_level INTEGER DEFAULT 0,
                profile_data TEXT  -- Full JSON profile
            )
        ''')
        
        # Conversation summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary TEXT,
                topics TEXT,  -- JSON list
                sentiment TEXT,
                message_count INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Content memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_memory (
                content_id TEXT PRIMARY KEY,
                title TEXT,
                content_type TEXT,
                source_url TEXT,
                summary TEXT,
                full_context TEXT,  -- Full extracted content
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                times_referenced INTEGER DEFAULT 0,
                last_referenced TIMESTAMP,
                topics TEXT,  -- JSON list
                entities TEXT  -- JSON list
            )
        ''')
        
        # Entity memory (people, places, things mentioned)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                entity_type TEXT,  -- person, place, org, topic
                first_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                times_mentioned INTEGER DEFAULT 1,
                context_summary TEXT,
                related_content TEXT  -- JSON list of content_ids
            )
        ''')
        
        # Relationship memory (how entities relate)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity1 TEXT,
                entity2 TEXT,
                relationship_type TEXT,
                strength REAL DEFAULT 0.5,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User methods
    
    def get_or_create_user(self, user_id: str) -> UserProfile:
        """Get existing user or create new one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT profile_data FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            profile_data = json.loads(row[0])
            profile = UserProfile(**profile_data)
            profile.last_seen = datetime.now().isoformat()
            
            # Update last seen
            cursor.execute(
                'UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ?',
                (user_id,)
            )
            conn.commit()
        else:
            profile = UserProfile(user_id=user_id)
            cursor.execute(
                '''INSERT INTO users (user_id, profile_data, preferred_topics)
                   VALUES (?, ?, ?)''',
                (user_id, json.dumps(asdict(profile)), json.dumps([]))
            )
            conn.commit()
        
        conn.close()
        return profile
    
    def update_user(self, profile: UserProfile):
        """Update user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''UPDATE users SET 
               total_messages = ?,
               total_sessions = ?,
               preferred_topics = ?,
               preferred_style = ?,
               nickname = ?,
               relationship_level = ?,
               profile_data = ?,
               last_seen = CURRENT_TIMESTAMP
               WHERE user_id = ?''',
            (
                profile.total_messages,
                profile.total_sessions,
                json.dumps(profile.preferred_topics),
                profile.preferred_style,
                profile.nickname,
                profile.relationship_level,
                json.dumps(asdict(profile)),
                profile.user_id
            )
        )
        conn.commit()
        conn.close()
    
    # Conversation methods
    
    def save_conversation_summary(self, session_id: str, user_id: str,
                                   summary: str, topics: List[str],
                                   message_count: int, sentiment: str = None):
        """Save a conversation summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''INSERT INTO conversation_summaries 
               (session_id, user_id, summary, topics, sentiment, message_count)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (session_id, user_id, summary, json.dumps(topics), sentiment, message_count)
        )
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversation summaries for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT session_id, summary, topics, timestamp 
               FROM conversation_summaries 
               WHERE user_id = ?
               ORDER BY timestamp DESC
               LIMIT ?''',
            (user_id, limit)
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'session_id': row[0],
                'summary': row[1],
                'topics': json.loads(row[2]) if row[2] else [],
                'timestamp': row[3]
            })
        
        conn.close()
        return results
    
    # Content methods
    
    def save_content(self, content_id: str, title: str, content_type: str,
                     source_url: str = None, summary: str = None,
                     full_context: str = None, topics: List[str] = None):
        """Save content to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''INSERT OR REPLACE INTO content_memory 
               (content_id, title, content_type, source_url, summary, 
                full_context, topics, processed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (content_id, title, content_type, source_url, summary,
             full_context, json.dumps(topics or []))
        )
        conn.commit()
        conn.close()
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """Retrieve content from memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM content_memory WHERE content_id = ?',
            (content_id,)
        )
        row = cursor.fetchone()
        
        if row:
            # Update reference count
            cursor.execute(
                '''UPDATE content_memory 
                   SET times_referenced = times_referenced + 1,
                       last_referenced = CURRENT_TIMESTAMP
                   WHERE content_id = ?''',
                (content_id,)
            )
            conn.commit()
            
            result = {
                'content_id': row[0],
                'title': row[1],
                'content_type': row[2],
                'source_url': row[3],
                'summary': row[4],
                'full_context': row[5],
                'processed_at': row[6],
                'times_referenced': row[7],
                'topics': json.loads(row[9]) if row[9] else []
            }
            conn.close()
            return result
        
        conn.close()
        return None
    
    def search_content(self, query: str, limit: int = 5) -> List[Dict]:
        """Search content memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT content_id, title, content_type, summary, source_url
               FROM content_memory 
               WHERE title LIKE ? OR summary LIKE ?
               ORDER BY times_referenced DESC, last_referenced DESC
               LIMIT ?''',
            (f'%{query}%', f'%{query}%', limit)
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'content_id': row[0],
                'title': row[1],
                'content_type': row[2],
                'summary': row[3],
                'source_url': row[4]
            })
        
        conn.close()
        return results
    
    # Entity methods
    
    def remember_entity(self, name: str, entity_type: str, context: str = None):
        """Remember an entity mentioned in conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute(
            'SELECT id, times_mentioned FROM entities WHERE entity_name = ?',
            (name,)
        )
        row = cursor.fetchone()
        
        if row:
            cursor.execute(
                '''UPDATE entities 
                   SET times_mentioned = times_mentioned + 1,
                       context_summary = ?
                   WHERE id = ?''',
                (context, row[0])
            )
        else:
            cursor.execute(
                '''INSERT INTO entities (entity_name, entity_type, context_summary)
                   VALUES (?, ?, ?)''',
                (name, entity_type, context)
            )
        
        conn.commit()
        conn.close()
    
    def get_entity_context(self, name: str) -> Optional[Dict]:
        """Get context about an entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT entity_name, entity_type, times_mentioned, context_summary
               FROM entities WHERE entity_name LIKE ?''',
            (f'%{name}%',)
        )
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'name': row[0],
                'type': row[1],
                'times_mentioned': row[2],
                'context': row[3]
            }
        return None


class MemoryManager:
    """
    Main memory manager that coordinates all memory types.
    
    Usage:
        memory = MemoryManager(user_id="user123")
        
        # Add to current session
        memory.add_message("user", "Tell me about Lagos tech")
        memory.add_message("assistant", "Lagos tech is booming o!")
        
        # Get context for LLM
        context = memory.get_full_context()
        
        # End session (saves to long-term memory)
        memory.end_session()
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        
        # Initialize memory layers
        self.session = SessionMemory()
        self.long_term = LongTermMemory()
        
        # Load user profile
        self.user_profile = self.long_term.get_or_create_user(user_id)
        self.user_profile.total_sessions += 1
    
    def add_message(self, role: str, content: str, **metadata) -> Message:
        """Add a message to session memory"""
        message = self.session.add_message(role, content, **metadata)
        
        # Update user stats
        if role == "user":
            self.user_profile.total_messages += 1
        
        return message
    
    def add_content(self, content_id: str, title: str, content_type: str,
                    summary: str = None, source_url: str = None,
                    full_context: str = None, topics: List[str] = None):
        """Add content to both session and long-term memory"""
        # Add to session
        ref = ContentReference(
            content_id=content_id,
            title=title,
            content_type=content_type,
            source_url=source_url,
            summary=summary,
            processed_at=datetime.now().isoformat()
        )
        self.session.add_content_reference(ref)
        
        # Save to long-term
        self.long_term.save_content(
            content_id=content_id,
            title=title,
            content_type=content_type,
            source_url=source_url,
            summary=summary,
            full_context=full_context,
            topics=topics
        )
        
        # Track in user profile
        self.user_profile.content_discussed.append(content_id)
    
    def get_context_for_llm(self, max_messages: int = 20, 
                            include_history: bool = True) -> List[Dict]:
        """
        Get full context for LLM including:
        - System context with user info
        - Recent conversation history
        - Active content references
        """
        context = []
        
        # Build system context
        system_parts = [
            "You are Sisi Lola, a Nigerian AI assistant.",
            f"User relationship level: {self.user_profile.relationship_level}/5",
        ]
        
        if self.user_profile.nickname:
            system_parts.append(f"Call this user: {self.user_profile.nickname}")
        
        if self.user_profile.preferred_topics:
            topics = ", ".join(self.user_profile.preferred_topics[:3])
            system_parts.append(f"User is interested in: {topics}")
        
        # Add active content context
        if self.session.active_content:
            content_summaries = []
            for cid, ref in self.session.active_content.items():
                content_summaries.append(f"- {ref.title}: {ref.summary or 'No summary'}")
            
            if content_summaries:
                system_parts.append("Content being discussed:\n" + "\n".join(content_summaries))
        
        # Add past conversation context if available
        if include_history:
            past_convs = self.long_term.get_recent_conversations(self.user_id, limit=2)
            if past_convs:
                system_parts.append("Previous conversations:")
                for conv in past_convs:
                    system_parts.append(f"- {conv['timestamp'][:10]}: {conv['summary'][:100]}...")
        
        context.append({
            "role": "system",
            "content": "\n".join(system_parts)
        })
        
        # Add conversation messages
        context.extend(self.session.get_context_messages(max_messages))
        
        return context
    
    def recall_content(self, query: str) -> List[Dict]:
        """Search for relevant content in memory"""
        return self.long_term.search_content(query)
    
    def remember_entity(self, name: str, entity_type: str, context: str = None):
        """Remember an entity mentioned"""
        self.long_term.remember_entity(name, entity_type, context)
    
    def get_entity_info(self, name: str) -> Optional[Dict]:
        """Get info about a remembered entity"""
        return self.long_term.get_entity_context(name)
    
    def update_user_preference(self, key: str, value: Any):
        """Update a user preference"""
        if key == "topics" and isinstance(value, list):
            self.user_profile.preferred_topics.extend(value)
            # Keep unique
            self.user_profile.preferred_topics = list(set(self.user_profile.preferred_topics))[:10]
        elif key == "style":
            self.user_profile.preferred_style = value
        elif key == "nickname":
            self.user_profile.nickname = value
        elif key == "relationship":
            self.user_profile.relationship_level = min(5, max(0, int(value)))
    
    def end_session(self, summary: str = None):
        """
        End the current session.
        Saves conversation summary to long-term memory.
        """
        # Generate summary if not provided
        if not summary:
            msg_count = len(self.session.messages)
            topics = list(set(self.session.topics_discussed))[:5]
            summary = f"Session with {msg_count} messages about: {', '.join(topics) if topics else 'general chat'}"
        
        # Save to long-term memory
        self.long_term.save_conversation_summary(
            session_id=self.session.session_id,
            user_id=self.user_id,
            summary=summary,
            topics=self.session.topics_discussed,
            message_count=len(self.session.messages)
        )
        
        # Update user profile
        self.long_term.update_user(self.user_profile)
        
        # Clear session
        self.session.clear()
        
        print(f"[OK] Session ended. Summary saved.")
    
    def get_relationship_greeting(self) -> str:
        """Get a personalized greeting based on relationship level"""
        level = self.user_profile.relationship_level
        nickname = self.user_profile.nickname
        
        greetings = {
            0: "Hello! Welcome!",
            1: f"Hey there! Good to see you{',' + nickname if nickname else ''}!",
            2: f"Omo! {'My person ' + nickname if nickname else 'You'} don show!",
            3: f"Ehh! {'My bestie ' + nickname if nickname else 'My bestie'}! How body?",
            4: f"Yay! {nickname or 'My ride or die'} is here! I miss you o!",
            5: f"{nickname or 'My soul twin'}!!! Na you be the realest! 💕",
        }
        
        return greetings.get(level, greetings[0])


# Quick access functions
def create_memory_manager(user_id: str = "default") -> MemoryManager:
    """Create a new memory manager instance"""
    return MemoryManager(user_id)


if __name__ == "__main__":
    print("=" * 60)
    print("SISI LOLA MEMORY SYSTEM")
    print("=" * 60)
    
    # Demo
    memory = MemoryManager(user_id="demo_user")
    
    print(f"\n{memory.get_relationship_greeting()}")
    print(f"User profile: {memory.user_profile.user_id}")
    print(f"Sessions: {memory.user_profile.total_sessions}")
    print(f"Relationship level: {memory.user_profile.relationship_level}/5")
    
    # Simulate conversation
    memory.add_message("user", "Tell me about Lagos tech startups")
    memory.add_message("assistant", "Omo! Lagos tech is on fire! Let me gist you...", 
                       topics=["tech", "Lagos", "startups"])
    
    # Add content reference
    memory.add_content(
        content_id="yt_abc123",
        title="Lagos Tech Scene 2024",
        content_type="video",
        summary="Video about emerging tech startups in Lagos",
        source_url="https://youtube.com/watch?v=abc123"
    )
    
    print(f"\nSession: {memory.session.session_id}")
    print(f"Messages: {len(memory.session.messages)}")
    print(f"Active content: {len(memory.session.active_content)}")
    
    # Get LLM context
    context = memory.get_context_for_llm()
    print(f"\nLLM context messages: {len(context)}")
    
    # End session
    memory.end_session("Demo session about Lagos tech")
    print("\nSession ended and saved!")
