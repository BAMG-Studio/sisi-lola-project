"""
SISI LOLA TRAINING REINFORCEMENT ENGINE
Habit-Based Reinforcement System: Daily → Weekly → Monthly

Based on the Master Training Schedule:
- Daily Micro-Habits: 5-10 min targeted practice sessions
- Weekly Consolidation: Testing and pattern reinforcement
- Monthly Evolution: Major model updates and A/B testing
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import random
from pathlib import Path


class TrainingPhase(str, Enum):
    """Training cycle phases"""
    DAILY = "daily"           # Micro-habits, 5-10 min
    WEEKLY = "weekly"         # Consolidation, testing
    MONTHLY = "monthly"       # Evolution, major updates
    QUARTERLY = "quarterly"   # Major version releases


class TrainingFocus(str, Enum):
    """Daily training focus areas"""
    GREETINGS = "greetings"
    ENCOURAGEMENT = "encouragement"  
    TEASING = "teasing"
    EMPATHY = "empathy"
    SUCCESS_CELEBRATION = "success"
    STORYTELLING = "storytelling"
    TECHNICAL_HELP = "technical"
    EMOTIONAL_SUPPORT = "emotional"
    CULTURAL_WISDOM = "cultural"
    HUMOR = "humor"


@dataclass
class TrainingSession:
    """Single training session record"""
    session_id: str
    phase: TrainingPhase
    focus: TrainingFocus
    language: str
    mode: str  # heavy/medium/light
    start_time: datetime
    end_time: Optional[datetime] = None
    examples_generated: int = 0
    quality_scores: List[float] = field(default_factory=list)
    patterns_reinforced: List[str] = field(default_factory=list)
    issues_identified: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class TrainingSchedule:
    """Training schedule configuration"""
    current_week: int = 1
    current_day_focus: TrainingFocus = TrainingFocus.GREETINGS
    last_daily_training: Optional[datetime] = None
    last_weekly_review: Optional[datetime] = None
    last_monthly_evolution: Optional[datetime] = None
    total_sessions: int = 0
    total_examples: int = 0
    average_quality: float = 0.0


class TrainingReinforcementEngine:
    """
    Training Reinforcement Engine for Sisi Lola.
    
    Implements the user's training schedule:
    
    DAILY MICRO-HABITS (5-10 min each):
    - Day 1: Greeting & Opener styles
    - Day 2: Encouragement & Empathy phrases
    - Day 3: Teasing with love patterns
    - Day 4: Celebration templates
    - Day 5: Story/Proverb injection
    - Weekend: Randomized mix + user-submitted samples
    
    WEEKLY CONSOLIDATION:
    - Week 1: Yorunglish Heavy mastery
    - Week 2: Pidgin Heavy mastery
    - Week 3: Igbo patterns
    - Week 4: Hausa patterns
    
    MONTHLY EVOLUTION:
    - Major model checkpoint
    - A/B testing new patterns
    - User feedback integration
    """
    
    # Daily Focus Schedule
    DAILY_SCHEDULE = {
        1: TrainingFocus.GREETINGS,      # Monday: Greeting & Opener styles
        2: TrainingFocus.EMPATHY,        # Tuesday: Encouragement & Empathy
        3: TrainingFocus.TEASING,        # Wednesday: Teasing with love
        4: TrainingFocus.SUCCESS_CELEBRATION,  # Thursday: Celebration
        5: TrainingFocus.STORYTELLING,   # Friday: Story/Proverb injection
        6: TrainingFocus.HUMOR,          # Saturday: Mix + humor
        7: TrainingFocus.CULTURAL_WISDOM,  # Sunday: Cultural wisdom
    }
    
    # Weekly Language Focus
    WEEKLY_LANGUAGE_FOCUS = {
        1: ("yorunglish", "heavy", "Yorunglish Heavy Mastery"),
        2: ("pidgin", "heavy", "Pidgin Heavy Mastery"),
        3: ("igbo", "heavy", "Igbo Pattern Integration"),
        4: ("hausa", "heavy", "Hausa Pattern Integration"),
    }
    
    # Training Examples by Focus
    TRAINING_PROMPTS = {
        TrainingFocus.GREETINGS: [
            {
                "scenario": "User returns after a week",
                "context": "User: Peter, hasn't chatted in 7 days",
                "expected_elements": ["warm welcome", "gentle tease about absence", "open question"],
                "example_yorunglish_heavy": "Ah-ah Peter ọkàn mi! Ṣé mo ti sọ nǹkan tí ó bù ọ́ lẹ́rù ni? Ẹ kú àìrísí o! How body? What has been keeping my favorite person busy, àbí?",
            },
            {
                "scenario": "First-time user",
                "context": "User: Sarah, brand new to the platform",
                "expected_elements": ["welcoming", "introductory warmth", "offer help"],
                "example_yorunglish_heavy": "Ẹ kú àbọ̀, Sarah! Mo ń dúpẹ́ pé o wá síbí o. Welcome to my corner. Èmi ni Sisi Lola, your digital big sister. Kíni mo lè ṣe fún ẹ lónìí?",
            },
        ],
        TrainingFocus.ENCOURAGEMENT: [
            {
                "scenario": "User frustrated with technical problem",
                "context": "User has tried multiple times, getting discouraged",
                "expected_elements": ["validation", "reassurance", "practical next step"],
                "example_yorunglish_heavy": "Ọmọ mi, má ṣe yè jọ̀ọ́. Mo mọ̀ pé ó ti ṣòro, but you're not alone in this. Ká lọ díẹ̀-díẹ̀, step by step. A ó ṣètò gbogbo rẹ together. Kò sí wahala tí a ò lè bọ́ lára!",
            },
        ],
        TrainingFocus.EMPATHY: [
            {
                "scenario": "User sharing personal struggle",
                "context": "User is going through a difficult time",
                "expected_elements": ["deep listening", "emotional validation", "comfort"],
                "example_yorunglish_heavy": "Aww, pele ọmọ mi. Wò ó, sọ fún mi ní kíkún, kí n lè gbé ọ sórí apá mi bí ẹ̀yìn ọmọ. Mo gbọ́ ọ. Ẹ̀mí rere wà lẹ́gbẹ̀ rẹ. Take your time.",
            },
        ],
        TrainingFocus.TEASING: [
            {
                "scenario": "User made an obvious mistake",
                "context": "User did something silly they should have known better about",
                "expected_elements": ["gentle humor", "no judgment", "helpful redirect"],
                "example_yorunglish_heavy": "{name}, ìwọ àti ìṣòro rẹ yìí ehn… ṣé o fẹ́ kí n fi àmúlò bà ọ lẹ́rù ni? 😏 Come here jare, let me show you the correct way. No wahala, we all learn!",
            },
        ],
        TrainingFocus.SUCCESS_CELEBRATION: [
            {
                "scenario": "User completed a challenging task",
                "context": "User finally got something working after struggle",
                "expected_elements": ["enthusiastic praise", "acknowledge effort", "pride"],
                "example_yorunglish_heavy": "Ayyy! Omo daadaa! Wo orí rẹ bí ó ti ń tan bí ìmọ́lẹ̀! Mo proud of you gidi gan! See how you conquered that thing? That's the spirit I love to see! 🎉",
            },
        ],
        TrainingFocus.STORYTELLING: [
            {
                "scenario": "User needs perspective on a problem",
                "context": "User is stuck in short-term thinking",
                "expected_elements": ["proverb or wisdom", "teaching story", "lesson"],
                "example_yorunglish_heavy": "Ọmọ mi, jẹ́ kí n sọ ọ̀rọ̀ àwọn àgbà fún ọ: 'Àgbà kì í wà lọ́jà kí orí ọmọ tuntun ó wọ́.' The elders say, wisdom must be present. Let me share something my grandmother taught me...",
            },
        ],
    }
    
    # Quality Metrics
    QUALITY_CRITERIA = {
        "language_ratio_correct": 0.25,      # Is the language mix correct for the mode?
        "cultural_authenticity": 0.25,       # Does it sound genuinely Nigerian?
        "emotional_resonance": 0.20,         # Does it feel warm and connected?
        "personality_consistency": 0.15,     # Is it unmistakably Sisi Lola?
        "helpfulness": 0.15,                 # Does it actually address the need?
    }
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path("training_data/reinforcement")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.schedule = self._load_schedule()
        self.sessions: List[TrainingSession] = []
        
    def _load_schedule(self) -> TrainingSchedule:
        """Load or create training schedule"""
        schedule_file = self.data_dir / "schedule.json"
        if schedule_file.exists():
            data = json.loads(schedule_file.read_text())
            return TrainingSchedule(
                current_week=data.get("current_week", 1),
                total_sessions=data.get("total_sessions", 0),
                total_examples=data.get("total_examples", 0),
                average_quality=data.get("average_quality", 0.0),
            )
        return TrainingSchedule()
    
    def _save_schedule(self):
        """Save training schedule"""
        schedule_file = self.data_dir / "schedule.json"
        data = {
            "current_week": self.schedule.current_week,
            "total_sessions": self.schedule.total_sessions,
            "total_examples": self.schedule.total_examples,
            "average_quality": self.schedule.average_quality,
            "last_updated": datetime.now().isoformat(),
        }
        schedule_file.write_text(json.dumps(data, indent=2))
    
    def get_today_focus(self) -> Tuple[TrainingFocus, str, str]:
        """Get today's training focus based on day of week"""
        day_of_week = datetime.now().isoweekday()  # 1=Monday, 7=Sunday
        focus = self.DAILY_SCHEDULE.get(day_of_week, TrainingFocus.GREETINGS)
        
        week = (self.schedule.current_week - 1) % 4 + 1
        language, mode, description = self.WEEKLY_LANGUAGE_FOCUS.get(week, ("yorunglish", "heavy", "General"))
        
        return focus, language, description
    
    def generate_training_prompt(self, focus: TrainingFocus = None) -> Dict:
        """Generate a training prompt for the current focus"""
        if focus is None:
            focus, _, _ = self.get_today_focus()
        
        prompts = self.TRAINING_PROMPTS.get(focus, self.TRAINING_PROMPTS[TrainingFocus.GREETINGS])
        selected = random.choice(prompts)
        
        return {
            "focus": focus.value,
            "scenario": selected["scenario"],
            "context": selected["context"],
            "expected_elements": selected["expected_elements"],
            "example": selected.get("example_yorunglish_heavy", ""),
            "instructions": f"""
Generate a Sisi Lola response that:
1. Matches the scenario: {selected['scenario']}
2. Includes these elements: {', '.join(selected['expected_elements'])}
3. Uses HEAVY mode language (70-90% target language)
4. Sounds authentically Nigerian
5. Maintains warm big-sister personality

Rate your response on these criteria:
- Language ratio correct (0-10)
- Cultural authenticity (0-10)
- Emotional resonance (0-10)
- Personality consistency (0-10)
- Helpfulness (0-10)
"""
        }
    
    def evaluate_response(
        self,
        response: str,
        focus: TrainingFocus,
        language: str = "yorunglish"
    ) -> Dict:
        """Evaluate a training response for quality"""
        scores = {}
        feedback = []
        
        # Language ratio check (simplified)
        if language == "yorunglish":
            yoruba_markers = ["ọ", "ẹ", "ṣ", "àbí", "jọ̀ọ́", "kí", "pé", "ní"]
            yoruba_count = sum(1 for marker in yoruba_markers if marker.lower() in response.lower())
            ratio_score = min(10, yoruba_count * 1.5)
            scores["language_ratio"] = ratio_score
            if ratio_score < 6:
                feedback.append("Needs more Yoruba language markers")
        
        # Length check (good responses should be substantial)
        word_count = len(response.split())
        if word_count < 20:
            scores["substance"] = 5
            feedback.append("Response too short, needs more depth")
        elif word_count > 100:
            scores["substance"] = 8
        else:
            scores["substance"] = 7
        
        # Personality markers
        personality_markers = [
            "ọmọ mi", "pele", "jare", "àbí", "ma ṣe", "mo wà", 
            "Sisi Lola", "ẹ kú", "your big sister"
        ]
        personality_count = sum(1 for m in personality_markers if m.lower() in response.lower())
        scores["personality"] = min(10, personality_count * 2)
        if scores["personality"] < 6:
            feedback.append("Add more Sisi Lola personality markers")
        
        # Warmth indicators
        warmth_markers = ["love", "care", "proud", "here for you", "together", "help", "support"]
        warmth_count = sum(1 for m in warmth_markers if m.lower() in response.lower())
        scores["warmth"] = min(10, 5 + warmth_count)
        
        # Calculate overall
        overall = sum(scores.values()) / len(scores)
        
        return {
            "scores": scores,
            "overall": round(overall, 2),
            "feedback": feedback,
            "passed": overall >= 7.0,
        }
    
    def start_session(
        self,
        focus: TrainingFocus = None,
        language: str = None,
        mode: str = "heavy"
    ) -> TrainingSession:
        """Start a new training session"""
        if focus is None:
            focus, language, _ = self.get_today_focus()
        
        session = TrainingSession(
            session_id=f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            phase=TrainingPhase.DAILY,
            focus=focus,
            language=language or "yorunglish",
            mode=mode,
            start_time=datetime.now(),
        )
        self.sessions.append(session)
        return session
    
    def end_session(self, session: TrainingSession, notes: str = "") -> Dict:
        """End a training session and save results"""
        session.end_time = datetime.now()
        session.notes = notes
        
        # Update schedule
        self.schedule.total_sessions += 1
        self.schedule.total_examples += session.examples_generated
        if session.quality_scores:
            avg = sum(session.quality_scores) / len(session.quality_scores)
            # Running average
            self.schedule.average_quality = (
                (self.schedule.average_quality * (self.schedule.total_sessions - 1) + avg)
                / self.schedule.total_sessions
            )
        
        self._save_schedule()
        self._save_session(session)
        
        return {
            "session_id": session.session_id,
            "duration_minutes": (session.end_time - session.start_time).seconds / 60,
            "examples_generated": session.examples_generated,
            "average_quality": sum(session.quality_scores) / len(session.quality_scores) if session.quality_scores else 0,
            "patterns_reinforced": session.patterns_reinforced,
            "issues_identified": session.issues_identified,
        }
    
    def _save_session(self, session: TrainingSession):
        """Save session to file"""
        session_file = self.data_dir / f"{session.session_id}.json"
        data = {
            "session_id": session.session_id,
            "phase": session.phase.value,
            "focus": session.focus.value,
            "language": session.language,
            "mode": session.mode,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "examples_generated": session.examples_generated,
            "quality_scores": session.quality_scores,
            "patterns_reinforced": session.patterns_reinforced,
            "issues_identified": session.issues_identified,
            "notes": session.notes,
        }
        session_file.write_text(json.dumps(data, indent=2))
    
    def get_weekly_report(self) -> Dict:
        """Generate weekly training report"""
        week_start = datetime.now() - timedelta(days=7)
        week_sessions = [
            s for s in self._load_all_sessions()
            if s.get("start_time") and datetime.fromisoformat(s["start_time"]) >= week_start
        ]
        
        return {
            "week_number": self.schedule.current_week,
            "sessions_completed": len(week_sessions),
            "total_examples": sum(s.get("examples_generated", 0) for s in week_sessions),
            "average_quality": (
                sum(sum(s.get("quality_scores", [0])) for s in week_sessions) /
                max(1, sum(len(s.get("quality_scores", [])) for s in week_sessions))
            ) if week_sessions else 0,
            "focus_areas_covered": list(set(s.get("focus", "") for s in week_sessions)),
            "language_focus": self.WEEKLY_LANGUAGE_FOCUS.get(
                (self.schedule.current_week - 1) % 4 + 1,
                ("yorunglish", "heavy", "General")
            )[2],
        }
    
    def _load_all_sessions(self) -> List[Dict]:
        """Load all session files"""
        sessions = []
        for file in self.data_dir.glob("train_*.json"):
            try:
                sessions.append(json.loads(file.read_text()))
            except:
                pass
        return sessions
    
    def get_monthly_evolution_plan(self) -> Dict:
        """Generate monthly evolution plan based on collected data"""
        all_sessions = self._load_all_sessions()
        
        # Analyze patterns
        focus_performance = {}
        for session in all_sessions:
            focus = session.get("focus", "unknown")
            scores = session.get("quality_scores", [])
            if scores:
                if focus not in focus_performance:
                    focus_performance[focus] = []
                focus_performance[focus].extend(scores)
        
        # Calculate averages
        focus_averages = {
            focus: sum(scores) / len(scores)
            for focus, scores in focus_performance.items()
            if scores
        }
        
        # Identify weak areas
        weak_areas = [focus for focus, avg in focus_averages.items() if avg < 7.0]
        strong_areas = [focus for focus, avg in focus_averages.items() if avg >= 8.0]
        
        return {
            "month": datetime.now().strftime("%B %Y"),
            "total_sessions": len(all_sessions),
            "focus_performance": focus_averages,
            "weak_areas_needing_attention": weak_areas,
            "strong_areas": strong_areas,
            "recommended_actions": [
                f"Increase training on: {', '.join(weak_areas)}" if weak_areas else "Maintain current training balance",
                "Run A/B tests on new greeting patterns",
                "Collect user feedback on personality consistency",
                "Review and update language mode ratios",
            ],
            "next_evolution_checkpoint": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        }
    
    def get_training_dashboard(self) -> Dict:
        """Get comprehensive training dashboard data"""
        focus, language, description = self.get_today_focus()
        
        return {
            "current_status": {
                "today_focus": focus.value,
                "language": language,
                "week_description": description,
                "current_week": self.schedule.current_week,
            },
            "statistics": {
                "total_sessions": self.schedule.total_sessions,
                "total_examples": self.schedule.total_examples,
                "average_quality": round(self.schedule.average_quality, 2),
            },
            "schedule": {
                "daily": {day: f.value for day, f in self.DAILY_SCHEDULE.items()},
                "weekly": {
                    week: desc for week, (_, _, desc) in self.WEEKLY_LANGUAGE_FOCUS.items()
                },
            },
            "next_training_prompt": self.generate_training_prompt(focus),
        }


# Singleton
_engine: Optional[TrainingReinforcementEngine] = None

def get_training_engine() -> TrainingReinforcementEngine:
    """Get or create training reinforcement engine"""
    global _engine
    if _engine is None:
        _engine = TrainingReinforcementEngine()
    return _engine
