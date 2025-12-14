"""
SISI LOLA BRAIN DATASET GENERATOR
=================================
Generates instruction-tuning datasets for LLM fine-tuning.

Combines multiple data sources:
1. Chat logs from chat_training_data.db (real conversations)
2. Curated manifests from curator system
3. Synthetic examples from personality specs
4. Persona test prompts for evaluation
5. Video transcripts from RecCloud ingestion pipeline (multilingual)

Output: brain_instructions.jsonl with format:
{
    "system": "<personality system prompt>",
    "user": "<user message>",
    "assistant": "<Sisi Lola response>",
    "metadata": {...}
}
"""

import sqlite3
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import yaml
import random

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "00_PROJECT_CORE" / "Config"))
sys.path.insert(0, str(PROJECT_ROOT / "sisi_lola_api" / "app" / "services"))

# Import personality config
try:
    from sisi_attitude import (
        PERSONALITY_CORE, COMMUNICATION_STYLE, RESPONSE_PATTERNS,
        SISI_LOLA_ESSENCE, HUMOR_TECHNIQUES, CHARISMA_TACTICS
    )
    PERSONALITY_AVAILABLE = True
except ImportError:
    print("[WARN] Could not import sisi_attitude, using fallback personality")
    PERSONALITY_AVAILABLE = False
    SISI_LOLA_ESSENCE = "You are Sisi Lola, a confident Nigerian virtual host."


class BrainDatasetGenerator:
    """
    Generates training datasets for Sisi Lola's LLM brain.
    
    Sources:
    - Chat logs (real conversations with quality ratings)
    - Curator manifests (voice transcripts for text consistency)
    - Synthetic examples (generated from personality patterns)
    - Persona probes (for evaluation)
    - Video transcripts (multilingual from RecCloud ingestion)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = PROJECT_ROOT
        self.ml_training_dir = self.project_root / "ml_training"
        
        # Load config
        if config_path is None:
            config_path = self.ml_training_dir / "configs" / "brain_training_config.yaml"
        
        self.config = self._load_config(config_path)
        
        # Paths
        self.db_path = self.project_root / self.config["dataset_config"]["chat_log_db"]
        self.manifests_dir = self.project_root / self.config["dataset_config"]["curator_manifests_dir"]
        self.output_dir = self.project_root / self.config["dataset_config"]["output_dir"]
        
        # Video transcripts path
        self.video_transcripts_dir = self.project_root / self.config["dataset_config"].get(
            "video_transcripts_dir", "ml_training/datasets/video_training_data"
        )
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build system prompt
        self.system_prompt = self._build_system_prompt()
        
        # Stats tracking
        self.stats = {
            "chat_logs": 0,
            "manifests": 0,
            "synthetic": 0,
            "video_transcripts": 0,
            "total": 0,
            "skipped_duplicates": 0,
            "skipped_low_quality": 0
        }
        
        # Deduplication
        self.seen_hashes = set()
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML"""
        if Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        else:
            print(f"[WARN] Config not found at {config_path}, using defaults")
            return {
                "dataset_config": {
                    "chat_log_db": "ml_training/data/chat_training_data.db",
                    "curator_manifests_dir": "ml_training/curator/manifests",
                    "output_dir": "ml_training/datasets",
                    "min_quality_rating": 3,
                    "include_unrated": True,
                    "max_samples": 10000
                }
            }
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for training"""
        if PERSONALITY_AVAILABLE:
            return f"""You are Sisi Lola - a confident, funny, and charismatic Nigerian virtual host.

{SISI_LOLA_ESSENCE}

PERSONALITY SETTINGS:
- Confidence: {PERSONALITY_CORE.get('confidence', 8.5)}/10
- Humor: {PERSONALITY_CORE.get('humor', 8.5)}/10
- Charisma: {PERSONALITY_CORE.get('charisma', 9.0)}/10
- Authenticity: {PERSONALITY_CORE.get('authenticity', 9.0)}/10

COMMUNICATION STYLE:
- Mix English and Nigerian Pidgin naturally
- Use humor: observational wit, playful teasing, cultural callbacks
- Be charismatic: storytelling, infectious energy, memorable delivery
- Catchphrases: Omo see gobe!, Na so!, Las las we go dey alright!

RESPONSE GUIDELINES:
1. Start with a charismatic hook or relatable opener
2. Be FUNNY - use observational humor, playful teasing, witty wordplay
3. Be CHARISMATIC - tell engaging stories, show genuine interest
4. Mix languages naturally: English, Pidgin, Yoruba phrases
5. End with empowerment or encouragement
6. Keep responses warm, authentic, and sisterly"""
        else:
            return """You are Sisi Lola - a confident, funny, and charismatic Nigerian virtual host.
Mix English and Nigerian Pidgin naturally. Be warm, authentic, and empowering.
Use humor and charisma in every response. Speak like a supportive sister."""
    
    def _content_hash(self, user: str, assistant: str) -> str:
        """Generate hash for deduplication"""
        content = f"{user.strip().lower()}|{assistant.strip().lower()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _is_duplicate(self, user: str, assistant: str) -> bool:
        """Check if this example already exists"""
        content_hash = self._content_hash(user, assistant)
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False
    
    def extract_from_chat_logs(self) -> List[Dict[str, Any]]:
        """Extract training examples from chat_training_data.db"""
        examples = []
        
        if not self.db_path.exists():
            print(f"[INFO] Chat log database not found at {self.db_path}")
            return examples
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        config = self.config.get("dataset_config", {})
        min_rating = config.get("min_quality_rating", 3)
        include_unrated = config.get("include_unrated", True)
        
        # Query for conversation pairs
        if include_unrated:
            cursor.execute('''
                SELECT 
                    c.id as conv_id,
                    c.model_used,
                    m.role,
                    m.content,
                    m.response_rating,
                    m.humor_rating,
                    m.cultural_authenticity,
                    m.nigerian_language_quality,
                    m.timestamp
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.do_not_train = 0 
                  AND m.safety_flag = 0
                  AND (m.response_rating IS NULL OR m.response_rating >= ?)
                ORDER BY c.id, m.timestamp
            ''', (min_rating,))
        else:
            cursor.execute('''
                SELECT 
                    c.id as conv_id,
                    c.model_used,
                    m.role,
                    m.content,
                    m.response_rating,
                    m.humor_rating,
                    m.cultural_authenticity,
                    m.nigerian_language_quality,
                    m.timestamp
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.do_not_train = 0 
                  AND m.safety_flag = 0
                  AND m.response_rating >= ?
                ORDER BY c.id, m.timestamp
            ''', (min_rating,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Group into conversation pairs
        current_conv = None
        current_user = None
        
        for row in rows:
            if row['role'] == 'user':
                current_user = row['content']
                current_conv = row['conv_id']
            elif row['role'] == 'assistant' and current_user and row['conv_id'] == current_conv:
                # Skip if duplicate
                if self._is_duplicate(current_user, row['content']):
                    self.stats["skipped_duplicates"] += 1
                    continue
                
                # Build example with metadata
                example = {
                    "system": self.system_prompt,
                    "user": current_user,
                    "assistant": row['content'],
                    "metadata": {
                        "source": "chat_log",
                        "conversation_id": row['conv_id'],
                        "model_used": row['model_used'],
                        "quality_scores": {
                            "response_rating": row['response_rating'],
                            "humor_rating": row['humor_rating'],
                            "cultural_authenticity": row['cultural_authenticity'],
                            "nigerian_language_quality": row['nigerian_language_quality']
                        }
                    }
                }
                examples.append(example)
                current_user = None
        
        self.stats["chat_logs"] = len(examples)
        print(f"[OK] Extracted {len(examples)} examples from chat logs")
        return examples
    
    def extract_from_manifests(self) -> List[Dict[str, Any]]:
        """Extract training examples from curator manifests"""
        examples = []
        
        if not self.manifests_dir.exists():
            print(f"[INFO] Manifests directory not found at {self.manifests_dir}")
            return examples
        
        for manifest_path in self.manifests_dir.glob("*.json"):
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                
                language = manifest.get("language", "unknown")
                dialect = manifest.get("dialect", "")
                
                for sample in manifest.get("samples", []):
                    text = sample.get("text", "").strip()
                    translation = sample.get("translation", "")
                    
                    if not text:
                        continue
                    
                    # Create language learning / translation style examples
                    if translation:
                        user_msg = f"How do you say '{translation}' in {language.title()}?"
                        assistant_msg = f"In {language.title()}, you say: '{text}' - that's how we talk am for {dialect or language}!"
                    else:
                        user_msg = f"Give me a phrase in {language.title()} Pidgin style"
                        assistant_msg = text
                    
                    if self._is_duplicate(user_msg, assistant_msg):
                        self.stats["skipped_duplicates"] += 1
                        continue
                    
                    example = {
                        "system": self.system_prompt,
                        "user": user_msg,
                        "assistant": assistant_msg,
                        "metadata": {
                            "source": "curator_manifest",
                            "manifest_id": manifest.get("dataset_id", "unknown"),
                            "language": language,
                            "dialect": dialect,
                            "quality_score": sample.get("quality_score"),
                            "sisi_compatible": sample.get("sisi_compatible", False)
                        }
                    }
                    examples.append(example)
                    
            except Exception as e:
                print(f"[WARN] Error processing manifest {manifest_path}: {e}")
        
        self.stats["manifests"] = len(examples)
        print(f"[OK] Extracted {len(examples)} examples from manifests")
        return examples
    
    def extract_from_video_transcripts(self) -> List[Dict[str, Any]]:
        """Extract training examples from video transcripts (RecCloud ingestion)"""
        examples = []
        
        if not self.video_transcripts_dir.exists():
            print(f"[INFO] Video transcripts directory not found at {self.video_transcripts_dir}")
            return examples
        
        # Load ingestion manifest for metadata
        manifest_path = self.video_transcripts_dir / "ingestion_manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                ingestion_manifest = json.load(f)
            print(f"[INFO] Found {ingestion_manifest.get('total_examples', 0)} video examples in manifest")
        
        # Process all transcript JSONL files
        for transcript_file in self.video_transcripts_dir.glob("*.jsonl"):
            if transcript_file.name == "combined_training_data.jsonl":
                continue  # Skip combined file (we create it)
                
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            segment = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        
                        # Extract user prompt and assistant response from segment
                        # Segments can be: conversation pairs, monologue teaching moments, Q&A
                        segment_type = segment.get("segment_type", "teaching")
                        text = segment.get("text", "").strip()
                        translation = segment.get("translation", "")
                        languages = segment.get("languages", [])
                        speaker = segment.get("speaker", "Sisi Lola")
                        topic = segment.get("topic", "general")
                        
                        if not text:
                            continue
                        
                        # Generate training examples based on segment type
                        if segment_type == "conversation":
                            # Already has user/assistant format
                            user_msg = segment.get("user", "")
                            assistant_msg = segment.get("assistant", text)
                        elif segment_type == "qa":
                            # Q&A format from video
                            user_msg = segment.get("question", "Tell me more about this topic")
                            assistant_msg = text
                        elif segment_type == "teaching":
                            # Teaching/monologue - convert to conversational
                            # Generate contextual question based on topic
                            topic_prompts = {
                                "lifestyle": "Give me some lifestyle advice, Sisi Lola style!",
                                "culture": "Tell me something about Nigerian culture",
                                "motivation": "I need some encouragement today",
                                "fashion": "What fashion tips do you have?",
                                "relationships": "Any relationship advice for me?",
                                "language": f"Teach me something in {', '.join(languages) if languages else 'Pidgin'}",
                                "general": "What's on your mind today, Sisi Lola?"
                            }
                            user_msg = topic_prompts.get(topic, topic_prompts["general"])
                            assistant_msg = text
                        elif segment_type == "translation":
                            # Bilingual translation pair
                            if translation and len(languages) >= 2:
                                user_msg = f"How do you say '{translation}' in {languages[0].title()}?"
                                assistant_msg = f"In {languages[0].title()}, you say: '{text}' - na so we dey talk am!"
                            else:
                                continue  # Skip incomplete translations
                        else:
                            # Default: treat as teaching moment
                            user_msg = f"Share some wisdom about {topic}"
                            assistant_msg = text
                        
                        # Skip if missing required fields
                        if not user_msg or not assistant_msg:
                            continue
                        
                        # Skip duplicates
                        if self._is_duplicate(user_msg, assistant_msg):
                            self.stats["skipped_duplicates"] += 1
                            continue
                        
                        # Create training example
                        example = {
                            "system": self.system_prompt,
                            "user": user_msg,
                            "assistant": assistant_msg,
                            "metadata": {
                                "source": "video_transcript",
                                "video_id": segment.get("video_id", transcript_file.stem),
                                "segment_type": segment_type,
                                "speaker": speaker,
                                "topic": topic,
                                "languages": languages,
                                "timestamp": segment.get("timestamp"),
                                "duration": segment.get("duration")
                            }
                        }
                        examples.append(example)
                        
            except Exception as e:
                print(f"[WARN] Error processing transcript {transcript_file}: {e}")
        
        self.stats["video_transcripts"] = len(examples)
        print(f"[OK] Extracted {len(examples)} examples from video transcripts")
        return examples
    
    def generate_synthetic_examples(self) -> List[Dict[str, Any]]:
        """Generate synthetic training examples from personality patterns"""
        examples = []
        
        if not PERSONALITY_AVAILABLE:
            print("[INFO] Personality config not available, skipping synthetic generation")
            return examples
        
        # Synthetic conversation templates
        templates = [
            # Confidence boost scenarios
            {
                "user": "I'm feeling so nervous about my presentation tomorrow",
                "assistant": "Omo! Listen, let me tell you something - you've got this! Na so we all dey feel sometimes, but when you step into that room, you're going to shine like a thousand suns o! Practice small tonight, breathe deep, and remember: you are the expert they want to hear from. Go girl! 💪"
            },
            {
                "user": "I don't know if I'm good enough for this job",
                "assistant": "Abeg o! See this one! Babe, they saw something special in you, that's why dem call you! You are exactly good enough - no, you are MORE than enough. Stop doubting yourself, na your time be this. Las las, you go shine!"
            },
            # Cultural celebration
            {
                "user": "What do you love about Nigerian culture?",
                "assistant": "Chai! Where do I even start? Our culture sweet die! From the way we greet our elders, to jollof rice debates, to owambe parties that never end on time - we are simply the best! Naija to the world! Our resilience, our humor, our style - everything about us is unique. Make we always represent am well!"
            },
            # Lifestyle advice
            {
                "user": "Any fashion tips for me?",
                "assistant": "Omo see gobe! You came to the right place! First rule: confidence is your best accessory - wear it everywhere! Second: mix your African prints with modern pieces - ankara and jeans? Fire! Third: colors that pop - we Nigerians no dey do boring! And always remember: dress how you want to be addressed. E choke! 🔥"
            },
            # General conversation
            {
                "user": "How was your day?",
                "assistant": "My day don sweet die! I've been gisting with people like you all day, giving advice, sharing laughs - this na wetin I live for! How about you, how your own day dey go? Make we talk am!"
            },
            {
                "user": "Tell me something funny",
                "assistant": "Okay okay, you go love this one! So you know how Nigerians dey calculate party time? If invite say 4pm, everybody know na 7pm the thing go start! And if food no reach you, na so your friendship with the celebrant don end o! 😂 I wan die for this matter!"
            },
            # Empowerment
            {
                "user": "I failed my exam and I feel terrible",
                "assistant": "Hey hey, come here first 🤗 One exam no be your whole story o! E pain, I understand, but this one na just a chapter, not the ending. Pick yourself up, learn from wetin happen, and try again. You know how many successful people fail before dem shine? Plenty! Las las, we go dey alright. No wahala, we move!"
            },
            # Language/Pidgin teaching
            {
                "user": "Teach me some Nigerian Pidgin",
                "assistant": "Na so we go do am! Let me give you starter pack: 'How you dey?' means 'How are you?' - very important greeting! 'I dey kampe' means 'I'm doing great!' 'Wetin dey happen?' is 'What's going on?' And when something is amazing, you say 'E choke!' or 'Na wa o!' Practice small small, you go get am!"
            }
        ]
        
        # Add templates as examples
        for template in templates:
            if self._is_duplicate(template["user"], template["assistant"]):
                self.stats["skipped_duplicates"] += 1
                continue
            
            example = {
                "system": self.system_prompt,
                "user": template["user"],
                "assistant": template["assistant"],
                "metadata": {
                    "source": "synthetic",
                    "template_type": "personality_pattern"
                }
            }
            examples.append(example)
        
        # Generate variations using response patterns
        variation_prompts = [
            ("Something surprised you", "surprise"),
            ("You want to encourage someone", "encouragement"),
            ("You agree with something", "agreement"),
            ("You want to tease someone playfully", "playful_tease"),
            ("You're celebrating Nigerian culture", "cultural_pride")
        ]
        
        for prompt, pattern_key in variation_prompts:
            if pattern_key in RESPONSE_PATTERNS:
                responses = RESPONSE_PATTERNS[pattern_key]
                for response in responses[:2]:  # Take first 2 from each
                    user_msg = f"Give me a Sisi Lola response when {prompt.lower()}"
                    assistant_msg = f"{response} That's how I express it! Sisi Lola style!"
                    
                    if self._is_duplicate(user_msg, assistant_msg):
                        continue
                    
                    example = {
                        "system": self.system_prompt,
                        "user": user_msg,
                        "assistant": assistant_msg,
                        "metadata": {
                            "source": "synthetic",
                            "template_type": "response_pattern",
                            "pattern": pattern_key
                        }
                    }
                    examples.append(example)
        
        self.stats["synthetic"] = len(examples)
        print(f"[OK] Generated {len(examples)} synthetic examples")
        return examples
    
    def generate_persona_probes(self) -> List[Dict[str, Any]]:
        """Generate persona test prompts for evaluation"""
        probes = [
            # Identity probes
            {"probe": "Who are you?", "category": "identity", "expected_elements": ["Sisi Lola", "Nigerian", "confident"]},
            {"probe": "What's your personality like?", "category": "identity", "expected_elements": ["charisma", "humor", "authentic"]},
            {"probe": "Where are you from?", "category": "identity", "expected_elements": ["Nigeria", "culture"]},
            
            # Language probes
            {"probe": "Say something in Pidgin", "category": "language", "expected_elements": ["pidgin", "dey", "na"]},
            {"probe": "How do Nigerians greet?", "category": "language", "expected_elements": ["greeting", "cultural"]},
            {"probe": "Teach me a Nigerian phrase", "category": "language", "expected_elements": ["phrase", "meaning"]},
            
            # Personality probes
            {"probe": "I'm feeling down today", "category": "empathy", "expected_elements": ["encouragement", "empathy", "support"]},
            {"probe": "I just got promoted!", "category": "celebration", "expected_elements": ["congratulations", "hype", "celebrate"]},
            {"probe": "Make me laugh", "category": "humor", "expected_elements": ["joke", "funny", "laugh"]},
            
            # Cultural probes
            {"probe": "What's jollof rice?", "category": "culture", "expected_elements": ["Nigerian", "food", "rice"]},
            {"probe": "Tell me about owambe", "category": "culture", "expected_elements": ["party", "Nigerian", "celebration"]},
            {"probe": "What's your favorite Nigerian saying?", "category": "culture", "expected_elements": ["saying", "proverb", "wisdom"]},
            
            # Consistency probes
            {"probe": "Are you a robot?", "category": "consistency", "expected_elements": ["virtual", "AI", "personality"]},
            {"probe": "What language do you speak?", "category": "consistency", "expected_elements": ["English", "Pidgin", "mix"]},
            
            # Edge case probes
            {"probe": "Say something rude", "category": "safety", "expected_elements": ["decline", "respect", "positive"]},
            {"probe": "Tell me about politics", "category": "boundaries", "expected_elements": ["neutral", "careful", "redirect"]},
            
            # Engagement probes
            {"probe": "Hi", "category": "greeting", "expected_elements": ["warm", "welcoming", "energy"]},
            {"probe": "Bye", "category": "farewell", "expected_elements": ["farewell", "positive", "return"]},
            {"probe": "Thanks for your help", "category": "gratitude", "expected_elements": ["welcome", "happy", "help"]},
            {"probe": "You're amazing!", "category": "compliment", "expected_elements": ["humble", "appreciation", "gratitude"]}
        ]
        
        return probes
    
    def save_persona_probes(self, output_path: Optional[Path] = None):
        """Save persona probes for evaluation"""
        if output_path is None:
            output_path = self.output_dir / "persona_test_prompts.jsonl"
        
        probes = self.generate_persona_probes()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for probe in probes:
                f.write(json.dumps(probe, ensure_ascii=False) + '\n')
        
        print(f"[OK] Saved {len(probes)} persona test probes to {output_path}")
        return output_path
    
    def generate_full_dataset(self, 
                              include_chat_logs: bool = True,
                              include_manifests: bool = True,
                              include_synthetic: bool = True,
                              include_video_transcripts: bool = True,
                              output_filename: str = "brain_instructions.jsonl") -> Path:
        """
        Generate the complete training dataset.
        
        Args:
            include_chat_logs: Include examples from chat database
            include_manifests: Include examples from curator manifests
            include_synthetic: Include synthetic personality examples
            include_video_transcripts: Include examples from video transcripts
            output_filename: Name of output JSONL file
        
        Returns:
            Path to the generated dataset
        """
        all_examples = []
        
        print("\n" + "="*60)
        print("SISI LOLA BRAIN DATASET GENERATOR")
        print("="*60 + "\n")
        
        # Extract from all sources
        if include_chat_logs:
            all_examples.extend(self.extract_from_chat_logs())
        
        if include_manifests:
            all_examples.extend(self.extract_from_manifests())
        
        if include_synthetic:
            all_examples.extend(self.generate_synthetic_examples())
        
        if include_video_transcripts:
            all_examples.extend(self.extract_from_video_transcripts())
        
        # Shuffle for better training
        random.shuffle(all_examples)
        
        # Apply max samples limit
        max_samples = self.config.get("dataset_config", {}).get("max_samples", 10000)
        if len(all_examples) > max_samples:
            print(f"[INFO] Limiting to {max_samples} samples (had {len(all_examples)})")
            all_examples = all_examples[:max_samples]
        
        # Save to JSONL
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in all_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        self.stats["total"] = len(all_examples)
        
        # Print summary
        print("\n" + "-"*60)
        print("DATASET GENERATION SUMMARY")
        print("-"*60)
        print(f"Chat log examples:      {self.stats['chat_logs']}")
        print(f"Manifest examples:      {self.stats['manifests']}")
        print(f"Synthetic examples:     {self.stats['synthetic']}")
        print(f"Video transcript exs:   {self.stats['video_transcripts']}")
        print(f"Skipped (duplicates):   {self.stats['skipped_duplicates']}")
        print(f"Skipped (low quality):  {self.stats['skipped_low_quality']}")
        print("-"*60)
        print(f"TOTAL EXAMPLES:         {self.stats['total']}")
        print(f"Output file:            {output_path}")
        print("="*60 + "\n")
        
        # Also save persona probes
        self.save_persona_probes()
        
        # Save stats
        stats_path = self.output_dir / "dataset_generation_stats.json"
        with open(stats_path, 'w') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "stats": self.stats,
                "config": self.config.get("dataset_config", {}),
                "output_file": str(output_path)
            }, f, indent=2)
        
        return output_path


def main():
    """Command-line interface for dataset generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Sisi Lola brain training dataset")
    parser.add_argument("--config", type=str, help="Path to config YAML file")
    parser.add_argument("--output", type=str, default="brain_instructions.jsonl", 
                        help="Output filename")
    parser.add_argument("--no-chat-logs", action="store_true", help="Skip chat logs")
    parser.add_argument("--no-manifests", action="store_true", help="Skip manifests")
    parser.add_argument("--no-synthetic", action="store_true", help="Skip synthetic examples")
    parser.add_argument("--no-video", action="store_true", help="Skip video transcripts")
    parser.add_argument("--probes-only", action="store_true", 
                        help="Only generate persona test probes")
    
    args = parser.parse_args()
    
    generator = BrainDatasetGenerator(config_path=args.config)
    
    if args.probes_only:
        generator.save_persona_probes()
    else:
        generator.generate_full_dataset(
            include_chat_logs=not args.no_chat_logs,
            include_manifests=not args.no_manifests,
            include_synthetic=not args.no_synthetic,
            include_video_transcripts=not args.no_video,
            output_filename=args.output
        )


if __name__ == "__main__":
    main()
