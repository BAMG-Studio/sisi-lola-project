"""
SISI LOLA TRAINING DATA COLLECTOR
Intelligent system for collecting, categorizing, and exporting training data from conversations.

Features:
- Real-time conversation logging with metadata
- Language detection and tagging
- Quality scoring for training samples
- Export to multiple formats (JSONL, Parquet, HuggingFace Datasets)
- Auto-categorization by topic, language, quality
- Finetuning-ready dataset generation
"""

import os
import json
import uuid
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib


class ConversationQuality(str, Enum):
    """Quality ratings for training samples"""
    EXCELLENT = "excellent"      # Perfect for training
    GOOD = "good"               # Minor issues, usable
    NEEDS_REVIEW = "needs_review"  # Requires human review
    POOR = "poor"               # Not suitable for training
    CORRECTION = "correction"   # User corrected AI response


class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH = "en"
    PIDGIN = "pcm"          # Nigerian Pidgin
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"
    YORUNGLISH = "yoen"     # Yoruba-English mix
    MIXED = "mixed"


class ContentCategory(str, Enum):
    """Content categories for organizing training data"""
    GREETING = "greeting"
    GENERAL_CHAT = "general_chat"
    CULTURAL = "cultural"
    LANGUAGE_LEARNING = "language_learning"
    MUSIC_ENTERTAINMENT = "music_entertainment"
    LIFESTYLE = "lifestyle"
    MENTAL_HEALTH = "mental_health"
    CAREER_HUSTLE = "career_hustle"
    RELATIONSHIPS = "relationships"
    DIASPORA = "diaspora"
    FAITH_SPIRITUALITY = "faith_spirituality"
    CONTENT_CREATION = "content_creation"
    BRAND_BUILDING = "brand_building"
    TECHNICAL = "technical"
    DEVELOPER_MODE = "developer_mode"  # /BAMG-STUDIO commands
    SYSTEM = "system"


@dataclass
class LanguageSegment:
    """A segment of text in a specific language"""
    language: str
    text: str
    start_pos: int
    end_pos: int
    confidence: float = 1.0


@dataclass
class ConversationTurn:
    """A single turn in a conversation"""
    turn_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    language_segments: List[Dict] = field(default_factory=list)
    detected_languages: List[str] = field(default_factory=list)
    response_time_ms: float = 0
    token_count: int = 0
    quality_score: float = 0.0
    quality_rating: str = "good"
    category: str = "general_chat"
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConversationSession:
    """A complete conversation session"""
    session_id: str
    user_id: str = "anonymous"
    started_at: str = ""
    ended_at: str = ""
    turns: List[Dict] = field(default_factory=list)
    primary_language: str = "mixed"
    categories: List[str] = field(default_factory=list)
    total_quality_score: float = 0.0
    is_developer_session: bool = False
    developer_commands_used: List[str] = field(default_factory=list)
    feedback: Dict = field(default_factory=dict)
    export_ready: bool = False


class TrainingDataCollector:
    """
    Intelligent training data collection system.
    
    Collects conversations, scores quality, extracts language patterns,
    and prepares data for fine-tuning.
    """
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        LanguageCode.PIDGIN: [
            r'\b(wetin|dey|na|wey|abi|sha|wahala|palava|pikin|sabi|shey|abeg)\b',
            r'\bhow (body|far|you dey)\b',
            r'\b(no be|e don|make I|e go)\b',
            r'\b(una|dem|we|sey|nawa)\b',
        ],
        LanguageCode.YORUBA: [
            r'\b(bawo ni|se alaafia|e kaabo|mo ti|omo|jeje|pele|daada)\b',
            r'\b(ehn|shebi|ko le|se o)\b',
            r'\b(ọmọ|àbí|kí ni)\b',
        ],
        LanguageCode.HAUSA: [
            r'\b(sannu|yaya|lafiya|ina|kai|ke|ba|ne|ce)\b',
            r'\b(da kyau|na gode|to mana|yauwa)\b',
        ],
        LanguageCode.IGBO: [
            r'\b(kedu|ndewo|nnọọ|daalu|biko|nwanne)\b',
            r'\b(ọ dị mma|ka ọ dị)\b',
        ],
    }
    
    # Quality indicators
    QUALITY_INDICATORS = {
        'positive': [
            'helpful', 'clear', 'correct', 'yes', 'thanks', 'perfect',
            'exactly', 'love it', 'great', 'awesome'
        ],
        'negative': [
            'wrong', 'no', 'incorrect', 'confused', 'what?', 'huh',
            'not what I asked', 'try again', 'that\'s not right'
        ],
        'correction': [
            'actually', 'I meant', 'let me clarify', 'that should be',
            'the correct answer is', 'it\'s actually'
        ]
    }
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        ContentCategory.GREETING: ['hello', 'hi', 'hey', 'how far', 'bawo', 'sannu', 'kedu'],
        ContentCategory.MUSIC_ENTERTAINMENT: ['music', 'afrobeats', 'song', 'artist', 'burna', 'wizkid', 'davido'],
        ContentCategory.LANGUAGE_LEARNING: ['how do you say', 'what does', 'teach me', 'translate'],
        ContentCategory.MENTAL_HEALTH: ['stress', 'anxiety', 'depression', 'mental', 'therapy', 'lonely'],
        ContentCategory.CAREER_HUSTLE: ['job', 'career', 'hustle', 'money', 'business', 'work'],
        ContentCategory.DIASPORA: ['japa', 'abroad', 'visa', 'relocate', 'diaspora', 'overseas'],
        ContentCategory.CONTENT_CREATION: ['content', 'post', 'video', 'reel', 'tiktok', 'instagram'],
        ContentCategory.BRAND_BUILDING: ['brand', 'audience', 'followers', 'influence'],
        ContentCategory.DEVELOPER_MODE: ['/bamg-studio', '/report', 'developer', 'training', 'finetune'],
    }
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or os.path.join(os.path.expanduser("~"), ".sisi_lola_training_data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-directories
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.export_dir = self.data_dir / "exports"
        
        for d in [self.raw_dir, self.processed_dir, self.export_dir]:
            d.mkdir(exist_ok=True)
        
        # Active sessions
        self.active_sessions: Dict[str, ConversationSession] = {}
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "total_turns": 0,
            "quality_distribution": {},
            "language_distribution": {},
            "category_distribution": {},
        }
        
        self._load_stats()
    
    def _load_stats(self):
        """Load statistics from disk"""
        stats_file = self.data_dir / "stats.json"
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                self.stats = json.load(f)
    
    def _save_stats(self):
        """Save statistics to disk"""
        with open(self.data_dir / "stats.json", 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def start_session(
        self,
        session_id: str = None,
        user_id: str = "anonymous",
        metadata: Dict = None
    ) -> str:
        """Start a new conversation session"""
        session_id = session_id or str(uuid.uuid4())[:8]
        
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            started_at=datetime.now().isoformat(),
            turns=[],
            categories=[],
            is_developer_session=False,
        )
        
        if metadata:
            session.feedback["initial_metadata"] = metadata
        
        self.active_sessions[session_id] = session
        self.stats["total_sessions"] += 1
        
        return session_id
    
    def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        response_time_ms: float = 0,
        metadata: Dict = None
    ) -> Dict:
        """Add a conversation turn and analyze it"""
        
        if session_id not in self.active_sessions:
            session_id = self.start_session(session_id)
        
        session = self.active_sessions[session_id]
        
        # Create turn
        turn = ConversationTurn(
            turn_id=f"{session_id}_{len(session.turns)}",
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            response_time_ms=response_time_ms,
            token_count=len(content.split()),
            metadata=metadata or {}
        )
        
        # Detect languages
        languages, segments = self._detect_languages(content)
        turn.detected_languages = languages
        turn.language_segments = [asdict(s) if isinstance(s, LanguageSegment) else s for s in segments]
        
        # Categorize content
        turn.category = self._categorize_content(content).value
        
        # Quality scoring
        if role == "user":
            # Check for corrections or feedback
            turn.quality_rating = self._assess_user_feedback(content)
        else:
            # Score assistant response
            turn.quality_score = self._score_response_quality(content, session)
            turn.quality_rating = self._rating_from_score(turn.quality_score)
        
        # Check for developer commands
        if "/bamg-studio" in content.lower():
            session.is_developer_session = True
            session.developer_commands_used.append("/BAMG-STUDIO")
            turn.category = ContentCategory.DEVELOPER_MODE.value
        
        if "/report" in content.lower():
            session.developer_commands_used.append("/REPORT")
        
        # Add turn to session
        session.turns.append(asdict(turn))
        
        # Update session categories
        if turn.category not in session.categories:
            session.categories.append(turn.category)
        
        # Update primary language
        if languages:
            session.primary_language = languages[0]
        
        self.stats["total_turns"] += 1
        
        return asdict(turn)
    
    def _detect_languages(self, text: str) -> tuple:
        """Detect languages in text and return segments"""
        text_lower = text.lower()
        detected = []
        segments = []
        
        # Check for explicit language tags
        tag_pattern = r'\[(\w+)\](.*?)\[/\1\]'
        matches = re.finditer(tag_pattern, text, re.DOTALL)
        
        for match in matches:
            lang_code = match.group(1).upper()
            content = match.group(2).strip()
            
            lang_map = {
                'EN': LanguageCode.ENGLISH,
                'NP': LanguageCode.PIDGIN,
                'YO': LanguageCode.YORUBA,
                'IG': LanguageCode.IGBO,
                'HA': LanguageCode.HAUSA,
            }
            
            if lang_code in lang_map:
                lang = lang_map[lang_code]
                if lang.value not in detected:
                    detected.append(lang.value)
                segments.append(LanguageSegment(
                    language=lang.value,
                    text=content,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Check for implicit language patterns
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    if lang.value not in detected:
                        detected.append(lang.value)
                    break
        
        # Default to English if no language detected
        if not detected:
            detected.append(LanguageCode.ENGLISH.value)
        
        return detected, segments
    
    def _categorize_content(self, text: str) -> ContentCategory:
        """Categorize content based on keywords"""
        text_lower = text.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return ContentCategory.GENERAL_CHAT
    
    def _assess_user_feedback(self, user_message: str) -> str:
        """Assess if user feedback indicates quality issues"""
        text_lower = user_message.lower()
        
        # Check for corrections
        for indicator in self.QUALITY_INDICATORS['correction']:
            if indicator in text_lower:
                return ConversationQuality.CORRECTION.value
        
        # Check for negative feedback
        for indicator in self.QUALITY_INDICATORS['negative']:
            if indicator in text_lower:
                return ConversationQuality.NEEDS_REVIEW.value
        
        return ConversationQuality.GOOD.value
    
    def _score_response_quality(self, response: str, session: ConversationSession) -> float:
        """Score response quality from 0-1"""
        score = 0.5  # Base score
        
        # Length check (not too short, not too long)
        word_count = len(response.split())
        if 10 < word_count < 300:
            score += 0.1
        elif word_count < 5 or word_count > 500:
            score -= 0.2
        
        # Language tags present
        if re.search(r'\[(?:EN|NP|YO|IG|HA)\]', response):
            score += 0.1
        
        # Check for repetition (bad)
        words = response.lower().split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:  # Too repetitive
                score -= 0.3
        
        # Check for coherence (simple heuristic: sentence count)
        sentences = re.split(r'[.!?]', response)
        if 2 <= len(sentences) <= 10:
            score += 0.1
        
        # Check for hallucination indicators
        hallucination_patterns = [
            r'User:.*\[/user\]',  # Fake user messages
            r'\[/\w+\]\s*\[/\w+\]',  # Repeated closing tags
            r'(.{20,})\1{2,}',  # Repeated phrases
        ]
        for pattern in hallucination_patterns:
            if re.search(pattern, response):
                score -= 0.3
                break
        
        return max(0, min(1, score))
    
    def _rating_from_score(self, score: float) -> str:
        """Convert numeric score to quality rating"""
        if score >= 0.8:
            return ConversationQuality.EXCELLENT.value
        elif score >= 0.6:
            return ConversationQuality.GOOD.value
        elif score >= 0.4:
            return ConversationQuality.NEEDS_REVIEW.value
        else:
            return ConversationQuality.POOR.value
    
    def end_session(self, session_id: str) -> Dict:
        """End a session and save to disk"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        session.ended_at = datetime.now().isoformat()
        
        # Calculate total quality score
        if session.turns:
            assistant_turns = [t for t in session.turns if t.get('role') == 'assistant']
            if assistant_turns:
                session.total_quality_score = sum(t.get('quality_score', 0) for t in assistant_turns) / len(assistant_turns)
        
        session.export_ready = True
        
        # Save to raw directory
        filename = f"{session_id}_{session.started_at[:10]}.json"
        with open(self.raw_dir / filename, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        # Update stats
        self._save_stats()
        
        # Remove from active
        del self.active_sessions[session_id]
        
        return asdict(session)
    
    def export_for_finetuning(
        self,
        format: str = "jsonl",
        min_quality: str = "good",
        languages: List[str] = None,
        categories: List[str] = None,
        include_developer_sessions: bool = False
    ) -> str:
        """
        Export collected data in a format suitable for fine-tuning.
        
        Args:
            format: Output format (jsonl, parquet, huggingface)
            min_quality: Minimum quality rating to include
            languages: Filter by languages
            categories: Filter by categories
            include_developer_sessions: Include /BAMG-STUDIO sessions
        
        Returns:
            Path to exported file
        """
        quality_order = ['excellent', 'good', 'needs_review', 'poor']
        min_quality_idx = quality_order.index(min_quality)
        
        training_samples = []
        
        # Process raw files
        for file in self.raw_dir.glob("*.json"):
            with open(file, 'r') as f:
                session = json.load(f)
            
            # Filter by developer session
            if session.get('is_developer_session') and not include_developer_sessions:
                continue
            
            # Process turns
            turns = session.get('turns', [])
            for i in range(0, len(turns) - 1, 2):
                if turns[i].get('role') != 'user':
                    continue
                
                user_turn = turns[i]
                assistant_turn = turns[i + 1] if i + 1 < len(turns) else None
                
                if not assistant_turn or assistant_turn.get('role') != 'assistant':
                    continue
                
                # Quality filter
                quality = assistant_turn.get('quality_rating', 'good')
                if quality_order.index(quality) > min_quality_idx:
                    continue
                
                # Language filter
                if languages:
                    detected = assistant_turn.get('detected_languages', [])
                    if not any(l in detected for l in languages):
                        continue
                
                # Category filter
                if categories:
                    if assistant_turn.get('category') not in categories:
                        continue
                
                # Create training sample
                sample = {
                    "instruction": "You are Sisi Lola, a warm and charismatic Nigerian AI virtual host. Respond in a mix of English and Nigerian languages (Pidgin, Yoruba, Igbo, Hausa) using appropriate language tags.",
                    "input": user_turn.get('content', ''),
                    "output": assistant_turn.get('content', ''),
                    "metadata": {
                        "session_id": session.get('session_id'),
                        "languages": assistant_turn.get('detected_languages', []),
                        "category": assistant_turn.get('category'),
                        "quality_score": assistant_turn.get('quality_score', 0),
                        "quality_rating": quality,
                    }
                }
                training_samples.append(sample)
        
        # Export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "jsonl":
            output_path = self.export_dir / f"sisi_lola_training_{timestamp}.jsonl"
            with open(output_path, 'w') as f:
                for sample in training_samples:
                    f.write(json.dumps(sample) + '\n')
        
        elif format == "huggingface":
            # Create HuggingFace dataset format
            output_path = self.export_dir / f"sisi_lola_dataset_{timestamp}"
            output_path.mkdir(exist_ok=True)
            
            # Save as JSON for HuggingFace datasets
            with open(output_path / "train.json", 'w') as f:
                json.dump(training_samples, f, indent=2)
            
            # Create dataset info
            dataset_info = {
                "dataset_name": "sisi-lola-conversations",
                "version": "1.0.0",
                "description": "Nigerian AI virtual host training data",
                "languages": ["en", "pcm", "yo", "ig", "ha"],
                "num_samples": len(training_samples),
                "created_at": timestamp,
            }
            with open(output_path / "dataset_info.json", 'w') as f:
                json.dump(dataset_info, f, indent=2)
        
        return str(output_path)
    
    def generate_report(self, session_id: str = None) -> Dict:
        """
        Generate comprehensive training data report.
        Used when /REPORT command is invoked.
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_sessions": self.stats.get("total_sessions", 0),
                "total_turns": self.stats.get("total_turns", 0),
                "active_sessions": len(self.active_sessions),
            },
            "quality_distribution": {},
            "language_distribution": {},
            "category_distribution": {},
            "recommendations": [],
            "session_details": None,
        }
        
        # Analyze all raw data
        quality_counts = {}
        language_counts = {}
        category_counts = {}
        
        for file in self.raw_dir.glob("*.json"):
            with open(file, 'r') as f:
                session = json.load(f)
            
            for turn in session.get('turns', []):
                # Quality
                q = turn.get('quality_rating', 'good')
                quality_counts[q] = quality_counts.get(q, 0) + 1
                
                # Languages
                for lang in turn.get('detected_languages', []):
                    language_counts[lang] = language_counts.get(lang, 0) + 1
                
                # Categories
                cat = turn.get('category', 'general_chat')
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        report["quality_distribution"] = quality_counts
        report["language_distribution"] = language_counts
        report["category_distribution"] = category_counts
        
        # Generate recommendations
        total_turns = sum(quality_counts.values()) if quality_counts else 1
        
        poor_ratio = quality_counts.get('poor', 0) / total_turns
        if poor_ratio > 0.2:
            report["recommendations"].append({
                "type": "quality_alert",
                "message": f"{poor_ratio*100:.1f}% of responses rated poor. Consider improving system prompts.",
                "priority": "high"
            })
        
        if language_counts.get('en', 0) > sum(language_counts.values()) * 0.8:
            report["recommendations"].append({
                "type": "language_balance",
                "message": "Over 80% English responses. Need more Pidgin/Yoruba/Igbo/Hausa training data.",
                "priority": "medium"
            })
        
        # Session details if requested
        if session_id:
            if session_id in self.active_sessions:
                report["session_details"] = asdict(self.active_sessions[session_id])
            else:
                # Look in raw files
                for file in self.raw_dir.glob(f"{session_id}*.json"):
                    with open(file, 'r') as f:
                        report["session_details"] = json.load(f)
                    break
        
        return report


# Singleton instance
_collector: Optional[TrainingDataCollector] = None

def get_training_collector() -> TrainingDataCollector:
    """Get or create training data collector singleton"""
    global _collector
    if _collector is None:
        _collector = TrainingDataCollector()
    return _collector
