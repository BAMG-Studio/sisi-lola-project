#!/usr/bin/env python3
"""
SISI LOLA CHAT DATA CURATION
=============================
Curates chat data for training by:
1. Filtering by quality ratings (RLHF threshold)
2. Excluding safety-flagged content
3. Deduplicating near-identical Q&A pairs
4. Exporting to JSONL format for brain/voice training

Usage:
    python curate_chat_data.py --min-rating 4 --output ml_training/datasets/curated
    python curate_chat_data.py --export-voice --output ml_training/datasets/voice_training.jsonl
"""

import sqlite3
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class ChatDataCurator:
    """
    Curates chat data for high-quality training exports.
    
    Features:
    - Quality filtering: Only export high-rated responses
    - Safety filtering: Exclude risky/sensitive content
    - Deduplication: Remove near-identical Q&A by content hash
    - Format conversion: Export to JSONL for various training targets
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "chat_training_data.db"
        self.db_path = Path(db_path)
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Chat database not found: {self.db_path}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the chat database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        stats['total_messages'] = cursor.fetchone()[0]
        
        # Messages by role
        cursor.execute("SELECT role, COUNT(*) FROM messages GROUP BY role")
        stats['by_role'] = dict(cursor.fetchall())
        
        # Rated messages
        cursor.execute("SELECT COUNT(*) FROM messages WHERE response_rating IS NOT NULL")
        stats['rated_messages'] = cursor.fetchone()[0]
        
        # High-quality messages (rating >= 4)
        cursor.execute("SELECT COUNT(*) FROM messages WHERE response_rating >= 4")
        stats['high_quality'] = cursor.fetchone()[0]
        
        # Safety-flagged messages
        cursor.execute("SELECT COUNT(*) FROM messages WHERE safety_flag = 1")
        stats['safety_flagged'] = cursor.fetchone()[0]
        
        # Do-not-train messages
        cursor.execute("SELECT COUNT(*) FROM messages WHERE do_not_train = 1")
        stats['do_not_train'] = cursor.fetchone()[0]
        
        # Conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stats['total_conversations'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of normalized content for deduplication"""
        # Normalize: lowercase, strip whitespace, remove punctuation variations
        normalized = content.lower().strip()
        normalized = ' '.join(normalized.split())  # Normalize whitespace
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]
    
    def update_content_hashes(self) -> int:
        """Update content_hash for all messages that don't have one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get messages without hashes
        cursor.execute("SELECT id, content FROM messages WHERE content_hash IS NULL")
        messages = cursor.fetchall()
        
        updated = 0
        for msg_id, content in messages:
            if content:
                content_hash = self.compute_content_hash(content)
                cursor.execute(
                    "UPDATE messages SET content_hash = ? WHERE id = ?",
                    (content_hash, msg_id)
                )
                updated += 1
        
        conn.commit()
        conn.close()
        print(f"[OK] Updated {updated} content hashes")
        return updated
    
    def find_duplicates(self) -> List[Tuple[str, int]]:
        """Find duplicate content by hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content_hash, COUNT(*) as count
            FROM messages
            WHERE content_hash IS NOT NULL
            GROUP BY content_hash
            HAVING count > 1
            ORDER BY count DESC
        """)
        
        duplicates = cursor.fetchall()
        conn.close()
        return duplicates
    
    def curate_for_brain_training(
        self,
        min_rating: int = 4,
        include_unrated: bool = False,
        deduplicate: bool = True
    ) -> List[Dict]:
        """
        Curate high-quality Q&A pairs for brain (LLM) training.
        
        Args:
            min_rating: Minimum response_rating to include (1-5)
            include_unrated: Include messages without ratings
            deduplicate: Remove duplicate content by hash
            
        Returns:
            List of training examples in instruction format
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build the query
        if include_unrated:
            rating_filter = "(m.response_rating IS NULL OR m.response_rating >= ?)"
        else:
            rating_filter = "m.response_rating >= ?"
        
        cursor.execute(f"""
            SELECT 
                c.id as conversation_id,
                m.id as message_id,
                m.role,
                m.content,
                m.content_hash,
                m.response_rating,
                m.cultural_authenticity,
                m.nigerian_language_quality
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE {rating_filter}
              AND (m.safety_flag IS NULL OR m.safety_flag = 0)
              AND (m.do_not_train IS NULL OR m.do_not_train = 0)
            ORDER BY c.id, m.timestamp
        """, (min_rating,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Group by conversation
        conversations = defaultdict(list)
        for row in rows:
            conv_id, msg_id, role, content, content_hash, rating, cultural, nigerian = row
            conversations[conv_id].append({
                'role': role,
                'content': content,
                'hash': content_hash,
                'rating': rating,
                'cultural': cultural,
                'nigerian': nigerian
            })
        
        # Build training examples
        seen_hashes = set()
        training_examples = []
        
        for conv_id, messages in conversations.items():
            # Pair user messages with assistant responses
            for i in range(len(messages) - 1):
                if messages[i]['role'] == 'user' and messages[i+1]['role'] == 'assistant':
                    user_msg = messages[i]
                    assistant_msg = messages[i+1]
                    
                    # Deduplication check
                    pair_hash = f"{user_msg.get('hash', '')}:{assistant_msg.get('hash', '')}"
                    if deduplicate and pair_hash in seen_hashes:
                        continue
                    seen_hashes.add(pair_hash)
                    
                    example = {
                        'instruction': user_msg['content'],
                        'output': assistant_msg['content'],
                        'metadata': {
                            'conversation_id': conv_id,
                            'response_rating': assistant_msg.get('rating'),
                            'cultural_authenticity': assistant_msg.get('cultural'),
                            'nigerian_language_quality': assistant_msg.get('nigerian')
                        }
                    }
                    training_examples.append(example)
        
        print(f"[OK] Curated {len(training_examples)} brain training examples")
        return training_examples
    
    def curate_for_voice_training(
        self,
        min_voice_rating: int = 4,
        min_accent_rating: int = 4
    ) -> List[Dict]:
        """
        Curate high-quality text for voice (TTS) training.
        
        Focuses on:
        - High voice naturalness ratings
        - Good accent authenticity
        - Nigerian language content (Yoruba, Pidgin)
        
        Returns:
            List of text samples for TTS training
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                m.content,
                m.voice_naturalness,
                m.nigerian_language_quality,
                vf.accent_authenticity,
                vf.pronunciation_issues
            FROM messages m
            LEFT JOIN voice_feedback vf ON m.id = vf.message_id
            WHERE m.role = 'assistant'
              AND (m.safety_flag IS NULL OR m.safety_flag = 0)
              AND (m.do_not_train IS NULL OR m.do_not_train = 0)
              AND (
                  (m.voice_naturalness IS NOT NULL AND m.voice_naturalness >= ?)
                  OR (vf.accent_authenticity IS NOT NULL AND vf.accent_authenticity >= ?)
              )
            ORDER BY m.voice_naturalness DESC, vf.accent_authenticity DESC
        """, (min_voice_rating, min_accent_rating))
        
        rows = cursor.fetchall()
        conn.close()
        
        voice_samples = []
        seen_content = set()
        
        for content, voice_rating, nigerian_quality, accent, issues in rows:
            if not content or content in seen_content:
                continue
            seen_content.add(content)
            
            # Parse pronunciation issues
            try:
                pronunciation_issues = json.loads(issues) if issues else []
            except json.JSONDecodeError:
                pronunciation_issues = []
            
            voice_samples.append({
                'text': content,
                'voice_naturalness': voice_rating,
                'nigerian_quality': nigerian_quality,
                'accent_authenticity': accent,
                'pronunciation_issues': pronunciation_issues,
                'language': 'yo-NG' if nigerian_quality and nigerian_quality >= 4 else 'en-NG'
            })
        
        print(f"[OK] Curated {len(voice_samples)} voice training samples")
        return voice_samples
    
    def export_to_jsonl(
        self,
        examples: List[Dict],
        output_path: str,
        format_type: str = 'instruction'
    ) -> str:
        """
        Export curated examples to JSONL format.
        
        Args:
            examples: List of training examples
            output_path: Output file path
            format_type: 'instruction' for brain, 'text' for voice
            
        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                if format_type == 'instruction':
                    # Standard instruction format for LLM training
                    line = {
                        'instruction': example['instruction'],
                        'input': '',
                        'output': example['output']
                    }
                elif format_type == 'text':
                    # Simple text format for TTS training
                    line = {
                        'text': example['text'],
                        'language': example.get('language', 'en-NG')
                    }
                else:
                    line = example
                
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        
        print(f"[OK] Exported {len(examples)} examples to {output_path}")
        return str(output_path)
    
    def full_curation_pipeline(
        self,
        output_dir: str = None,
        min_rating: int = 4,
        include_unrated: bool = False
    ) -> Dict[str, str]:
        """
        Run the full curation pipeline.
        
        Steps:
        1. Update content hashes
        2. Find and report duplicates
        3. Curate brain training data
        4. Curate voice training data
        5. Export both to JSONL
        
        Returns:
            Dict with paths to exported files
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "datasets" / "curated"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print("\n" + "="*60)
        print("SISI LOLA CHAT DATA CURATION PIPELINE")
        print("="*60)
        
        # Step 1: Stats
        print("\n[1/5] Database Statistics:")
        stats = self.get_stats()
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        # Step 2: Update hashes
        print("\n[2/5] Updating Content Hashes...")
        self.update_content_hashes()
        
        # Step 3: Find duplicates
        print("\n[3/5] Finding Duplicates...")
        duplicates = self.find_duplicates()
        print(f"  Found {len(duplicates)} duplicate groups")
        
        # Step 4: Curate brain data
        print(f"\n[4/5] Curating Brain Training Data (min_rating={min_rating})...")
        brain_examples = self.curate_for_brain_training(
            min_rating=min_rating,
            include_unrated=include_unrated,
            deduplicate=True
        )
        
        brain_path = output_dir / f"brain_training_{timestamp}.jsonl"
        self.export_to_jsonl(brain_examples, brain_path, format_type='instruction')
        
        # Step 5: Curate voice data
        print("\n[5/5] Curating Voice Training Data...")
        voice_examples = self.curate_for_voice_training(
            min_voice_rating=4,
            min_accent_rating=4
        )
        
        voice_path = output_dir / f"voice_training_{timestamp}.jsonl"
        self.export_to_jsonl(voice_examples, voice_path, format_type='text')
        
        print("\n" + "="*60)
        print("CURATION COMPLETE")
        print("="*60)
        print(f"\nExported files:")
        print(f"  Brain: {brain_path}")
        print(f"  Voice: {voice_path}")
        
        return {
            'brain': str(brain_path),
            'voice': str(voice_path),
            'stats': stats
        }


def main():
    parser = argparse.ArgumentParser(description='Curate Sisi Lola chat data for training')
    parser.add_argument('--db', type=str, help='Path to chat database')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--min-rating', type=int, default=4, help='Minimum rating filter (1-5)')
    parser.add_argument('--include-unrated', action='store_true', help='Include unrated messages')
    parser.add_argument('--export-brain', action='store_true', help='Export brain training data only')
    parser.add_argument('--export-voice', action='store_true', help='Export voice training data only')
    parser.add_argument('--stats-only', action='store_true', help='Show stats without exporting')
    
    args = parser.parse_args()
    
    curator = ChatDataCurator(db_path=args.db)
    
    if args.stats_only:
        stats = curator.get_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return
    
    if args.export_brain:
        examples = curator.curate_for_brain_training(
            min_rating=args.min_rating,
            include_unrated=args.include_unrated
        )
        output = args.output or 'ml_training/datasets/brain_training.jsonl'
        curator.export_to_jsonl(examples, output, format_type='instruction')
    elif args.export_voice:
        examples = curator.curate_for_voice_training()
        output = args.output or 'ml_training/datasets/voice_training.jsonl'
        curator.export_to_jsonl(examples, output, format_type='text')
    else:
        # Full pipeline
        curator.full_curation_pipeline(
            output_dir=args.output,
            min_rating=args.min_rating,
            include_unrated=args.include_unrated
        )


if __name__ == "__main__":
    main()
