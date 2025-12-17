#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - EXTERNAL VIDEO TRANSCRIPT PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════
# Processes completed RecCloud transcripts and generates training data
# December 14, 2025
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_training/logs/external_transcript_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExternalTranscriptProcessor")


# ═══════════════════════════════════════════════════════════════════════════════
# PERSONA PILLAR CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class PersonaPillarClassifier:
    """Classifies transcript segments by Sisi Lola's persona pillars."""
    
    PILLARS = {
        'cultural_ambassador': {
            'keywords': [
                'culture', 'tradition', 'heritage', 'yoruba', 'igbo', 'hausa',
                'nigeria', 'african', 'ancestor', 'elder', 'wisdom', 'proverb',
                'aso oke', 'ankara', 'agbada', 'gele', 'festival', 'ceremony',
                'jollof', 'egusi', 'suya', 'puff puff', 'chin chin', 'fufu',
                'market', 'oja', 'barter', 'haggle', 'mama put'
            ],
            'patterns': [
                r'na so we dey',
                r'our people say',
                r'back home',
                r'in my country',
                r'nigerian way',
                r'african way'
            ]
        },
        'tech_visionary': {
            'keywords': [
                'technology', 'ai', 'artificial intelligence', 'machine learning',
                'startup', 'innovation', 'digital', 'app', 'software', 'coding',
                'fintech', 'blockchain', 'crypto', 'mobile', 'internet',
                'silicon', 'founder', 'entrepreneur', 'venture', 'investment'
            ],
            'patterns': [
                r'tech\s*\w+',
                r'build\s+(?:the|a)\s+future',
                r'disrupting',
                r'scaling',
                r'ai\s+(?:can|will|is)'
            ]
        },
        'african_mother': {
            'keywords': [
                'my child', 'my dear', 'listen', 'advice', 'wisdom', 'teach',
                'learn', 'respect', 'behave', 'properly', 'education',
                'marriage', 'family', 'husband', 'wife', 'children',
                'prayer', 'god', 'bless', 'faith', 'church', 'mosque'
            ],
            'patterns': [
                r'sit down',
                r'let me tell you',
                r'when i was your age',
                r'back in my day',
                r'you children of nowadays',
                r'god forbid',
                r'by his grace'
            ]
        },
        'lagos_hustler': {
            'keywords': [
                'hustle', 'money', 'business', 'grind', 'work', 'earn',
                'naira', 'dollar', 'forex', 'profit', 'loss', 'invest',
                'side hustle', 'oga', 'madam', 'boss', 'customer',
                'lagos', 'island', 'mainland', 'traffic', 'danfo', 'okada'
            ],
            'patterns': [
                r'make money',
                r'secure the bag',
                r'hustle hard',
                r'no be small thing',
                r'e no easy',
                r'man must wack'
            ]
        },
        'diaspora_guide': {
            'keywords': [
                'abroad', 'overseas', 'japa', 'visa', 'immigration', 'migrate',
                'uk', 'usa', 'canada', 'germany', 'australia', 'expat',
                'home', 'family back home', 'send money', 'western union',
                'homesick', 'miss', 'return', 'visit', 'weather', 'cold',
                'culture shock', 'accent', 'adapt', 'integrate'
            ],
            'patterns': [
                r'when i first came',
                r'back home',
                r'in my country',
                r'moving abroad',
                r'living abroad',
                r'left nigeria'
            ]
        },
        'code_switcher': {
            'keywords': [
                'wetin', 'wahala', 'gist', 'jare', 'abi', 'sha', 'shey',
                'na', 'dey', 'don', 'no be', 'e be like', 'dem'
            ],
            'patterns': [
                r'\b(wetin|wahala|gist)\b',
                r'\b(abi|sha|shey|jare)\b',
                r'\bna\s+\w+',
                r'\bdey\s+\w+',
                r'\be\s+don\s+\w+',
                r'[a-z]+\s+(?:sugbon|abi|sha)',  # Mixed language
            ]
        }
    }
    
    def classify_segment(self, text: str, language: str = None) -> List[str]:
        """Classify a text segment into persona pillars."""
        text_lower = text.lower()
        matched_pillars = []
        
        for pillar, criteria in self.PILLARS.items():
            score = 0
            
            # Check keywords
            for keyword in criteria['keywords']:
                if keyword in text_lower:
                    score += 1
            
            # Check patterns
            for pattern in criteria['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 2
            
            # Language-based boost
            if pillar == 'code_switcher' and language in ['yo', 'np', 'ha', 'ig']:
                score += 3
            
            if score >= 2:  # Threshold for classification
                matched_pillars.append(pillar)
        
        # Default to cultural_ambassador if no match
        if not matched_pillars:
            matched_pillars = ['cultural_ambassador']
        
        return matched_pillars


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING EXAMPLE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TrainingExample:
    """A single training example for LLM fine-tuning."""
    id: str
    source: str
    source_video: str
    timestamp: str
    instruction: str
    input_text: str
    output_text: str
    language: str
    persona_pillars: List[str]
    metadata: Dict[str, Any]


class TrainingExampleGenerator:
    """Generates training examples from transcript segments."""
    
    INSTRUCTION_TEMPLATES = {
        'cultural_ambassador': [
            "As a Nigerian cultural expert, explain the following:",
            "Share your knowledge about Nigerian traditions:",
            "Teach about African cultural practices:",
        ],
        'tech_visionary': [
            "As an African tech innovator, discuss:",
            "Explain this technology concept in Nigerian Pidgin:",
            "Share your vision for technology in Africa:",
        ],
        'african_mother': [
            "As an African mother figure, give advice about:",
            "Share maternal wisdom on:",
            "Counsel someone dealing with:",
        ],
        'lagos_hustler': [
            "As a Lagos entrepreneur, discuss:",
            "Share business insights about:",
            "Explain how to succeed in:",
        ],
        'diaspora_guide': [
            "As someone who understands the diaspora experience, explain:",
            "Give advice to Nigerians moving abroad about:",
            "Share your experience regarding:",
        ],
        'code_switcher': [
            "Respond in Nigerian English (Pidgin/Yoruba mix):",
            "Express this thought mixing English and local languages:",
            "Code-switch naturally while discussing:",
        ]
    }
    
    def __init__(self):
        self.classifier = PersonaPillarClassifier()
        self.example_counter = 0
    
    def generate_from_segment(
        self,
        text: str,
        video_id: str,
        timestamp: str,
        language: str,
        video_metadata: Dict[str, Any]
    ) -> Optional[TrainingExample]:
        """Generate a training example from a transcript segment."""
        
        # Skip very short segments
        if len(text.split()) < 10:
            return None
        
        # Classify persona pillars
        pillars = self.classifier.classify_segment(text, language)
        
        # Select instruction template based on primary pillar
        primary_pillar = pillars[0]
        import random
        instruction = random.choice(self.INSTRUCTION_TEMPLATES[primary_pillar])
        
        # Generate example
        self.example_counter += 1
        example_id = f"EXT_{video_id}_{self.example_counter:04d}"
        
        # Extract topic from text (first sentence or phrase)
        topic = self._extract_topic(text)
        
        return TrainingExample(
            id=example_id,
            source='external_video',
            source_video=video_id,
            timestamp=timestamp,
            instruction=instruction,
            input_text=topic,
            output_text=text,
            language=language,
            persona_pillars=pillars,
            metadata={
                'creator': video_metadata.get('creator', ''),
                'category': video_metadata.get('category', ''),
                'tier': video_metadata.get('tier', 1),
            }
        )
    
    def _extract_topic(self, text: str) -> str:
        """Extract a topic/question from the text."""
        # Simple extraction: first sentence up to 100 chars
        sentences = text.split('.')
        if sentences:
            topic = sentences[0].strip()
            if len(topic) > 100:
                topic = topic[:97] + '...'
            return topic
        return text[:100]


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSCRIPT PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

class ExternalTranscriptProcessor:
    """Processes RecCloud transcripts and generates training data."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.example_generator = TrainingExampleGenerator()
    
    def process_transcript(
        self,
        transcript_data: Dict[str, Any],
        video_metadata: Dict[str, Any]
    ) -> List[TrainingExample]:
        """Process a single transcript and generate training examples."""
        examples = []
        video_id = video_metadata.get('video_id', 'UNKNOWN')
        
        # Handle different transcript formats
        segments = transcript_data.get('segments', [])
        if not segments:
            # Try alternative format
            segments = transcript_data.get('results', {}).get('segments', [])
        
        for segment in segments:
            text = segment.get('text', '').strip()
            start_time = segment.get('start', 0)
            language = segment.get('language', video_metadata.get('primary_language', 'en'))
            
            # Format timestamp
            timestamp = f"{int(start_time // 60):02d}:{int(start_time % 60):02d}"
            
            example = self.example_generator.generate_from_segment(
                text=text,
                video_id=video_id,
                timestamp=timestamp,
                language=language,
                video_metadata=video_metadata
            )
            
            if example:
                examples.append(example)
        
        logger.info(f"Generated {len(examples)} examples from {video_id}")
        return examples
    
    def save_examples(self, examples: List[TrainingExample], phase: int = None):
        """Save training examples to JSONL file."""
        if phase:
            output_file = self.output_dir / f"phase{phase}_transcripts.jsonl"
        else:
            output_file = self.output_dir / "external_transcripts.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in examples:
                # Convert to instruction-tuning format
                record = {
                    'id': example.id,
                    'source': example.source,
                    'instruction': example.instruction,
                    'input': example.input_text,
                    'output': example.output_text,
                    'language': example.language,
                    'persona_pillars': example.persona_pillars,
                    'metadata': {
                        'source_video': example.source_video,
                        'timestamp': example.timestamp,
                        **example.metadata
                    }
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(examples)} examples to {output_file}")
        return output_file


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Process external video transcripts and generate training data'
    )
    
    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        help='Process transcripts for specified phase'
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        help='Directory containing transcript JSON files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='ml_training/datasets/external_video_training',
        help='Directory for output JSONL files'
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / args.output_dir
    
    processor = ExternalTranscriptProcessor(output_dir)
    
    # Find transcript files
    if args.input_dir:
        transcript_dir = Path(args.input_dir)
    else:
        transcript_dir = project_root / "ml_training" / "datasets" / "reccloud_transcripts"
    
    if not transcript_dir.exists():
        logger.error(f"Transcript directory not found: {transcript_dir}")
        logger.info("Creating sample transcript for testing...")
        
        # Create a sample transcript for testing
        transcript_dir.mkdir(parents=True, exist_ok=True)
        sample_transcript = {
            "video_id": "EXT_TEST_001",
            "segments": [
                {
                    "start": 0,
                    "end": 30,
                    "text": "Welcome to this discussion about Nigerian culture. Na so we dey here, ready to share the wisdom of our ancestors.",
                    "language": "np"
                },
                {
                    "start": 30,
                    "end": 60,
                    "text": "Technology is transforming Africa. From Lagos to Nairobi, young entrepreneurs are building the future.",
                    "language": "en"
                }
            ]
        }
        sample_metadata = {
            "video_id": "EXT_TEST_001",
            "creator": "Test Creator",
            "category": "test",
            "tier": 1,
            "primary_language": "en"
        }
        
        with open(transcript_dir / "sample_transcript.json", 'w') as f:
            json.dump(sample_transcript, f, indent=2)
        with open(transcript_dir / "sample_metadata.json", 'w') as f:
            json.dump(sample_metadata, f, indent=2)
        
        logger.info(f"Created sample transcript at {transcript_dir}")
    
    # Process all transcript files
    all_examples = []
    
    for transcript_file in transcript_dir.glob("*_transcript.json"):
        # Load transcript
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        
        # Load corresponding metadata
        metadata_file = transcript_file.with_name(
            transcript_file.stem.replace('_transcript', '_metadata') + '.json'
        )
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                video_metadata = json.load(f)
        else:
            video_metadata = {'video_id': transcript_file.stem}
        
        # Process transcript
        examples = processor.process_transcript(transcript_data, video_metadata)
        all_examples.extend(examples)
    
    # Save all examples
    if all_examples:
        output_file = processor.save_examples(all_examples, args.phase)
        print(f"\n✅ Generated {len(all_examples)} training examples")
        print(f"📁 Output file: {output_file}")
    else:
        print("\n⚠️ No examples generated. Check transcript directory.")


if __name__ == '__main__':
    main()
