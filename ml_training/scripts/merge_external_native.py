#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# SISI LOLA - MERGE EXTERNAL AND NATIVE VIDEO DATA
# ═══════════════════════════════════════════════════════════════════════════════
# Combines external video transcripts with native Sisi Lola content
# December 14, 2025
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_training/logs/merge_external_native.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MergeExternalNative")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class MergeConfig:
    """Configuration for merging datasets."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        
        # Input directories
        self.native_data_dir = self.project_root / "ml_training" / "datasets" / "video_training_data"
        self.external_data_dir = self.project_root / "ml_training" / "datasets" / "external_video_training"
        self.chat_data_dir = self.project_root / "ml_training" / "datasets"
        
        # Output directory
        self.output_dir = self.project_root / "ml_training" / "datasets" / "unified"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Target distribution
        self.target_distribution = {
            'cultural_ambassador': 0.20,
            'tech_visionary': 0.20,
            'african_mother': 0.15,
            'lagos_hustler': 0.15,
            'diaspora_guide': 0.15,
            'code_switcher': 0.15,
        }
        
        # Target language distribution
        self.target_language_distribution = {
            'en': 0.40,
            'yo': 0.30,
            'np': 0.20,
            'ha': 0.05,
            'ig': 0.05,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADER
# ═══════════════════════════════════════════════════════════════════════════════

class DataLoader:
    """Loads training data from various sources."""
    
    def __init__(self, config: MergeConfig):
        self.config = config
    
    def load_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load records from a JSONL file."""
        records = []
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Error parsing line in {file_path}: {e}")
        return records
    
    def load_native_data(self) -> List[Dict[str, Any]]:
        """Load native Sisi Lola video transcripts."""
        records = []
        
        for jsonl_file in self.config.native_data_dir.glob("*.jsonl"):
            file_records = self.load_jsonl(jsonl_file)
            for record in file_records:
                record['source'] = 'native_video'
            records.extend(file_records)
            logger.info(f"Loaded {len(file_records)} records from {jsonl_file.name}")
        
        return records
    
    def load_external_data(self) -> List[Dict[str, Any]]:
        """Load external video transcripts."""
        records = []
        
        for jsonl_file in self.config.external_data_dir.glob("*.jsonl"):
            file_records = self.load_jsonl(jsonl_file)
            for record in file_records:
                record['source'] = 'external_video'
            records.extend(file_records)
            logger.info(f"Loaded {len(file_records)} records from {jsonl_file.name}")
        
        return records
    
    def load_chat_data(self) -> List[Dict[str, Any]]:
        """Load chat log training data."""
        records = []
        
        # Look for brain dataset or chat exports
        chat_files = [
            self.config.chat_data_dir / "brain_training_data.jsonl",
            self.config.chat_data_dir / "chat_exports.jsonl",
            self.config.chat_data_dir / "curated_chat_samples.jsonl",
        ]
        
        for chat_file in chat_files:
            if chat_file.exists():
                file_records = self.load_jsonl(chat_file)
                for record in file_records:
                    record['source'] = 'chat_logs'
                records.extend(file_records)
                logger.info(f"Loaded {len(file_records)} records from {chat_file.name}")
        
        return records
    
    def load_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all training data sources."""
        return {
            'native': self.load_native_data(),
            'external': self.load_external_data(),
            'chat': self.load_chat_data(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class DataAnalyzer:
    """Analyzes training data distribution."""
    
    def analyze(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the distribution of training data."""
        analysis = {
            'total_records': len(records),
            'source_distribution': defaultdict(int),
            'language_distribution': defaultdict(int),
            'persona_distribution': defaultdict(int),
        }
        
        for record in records:
            # Source
            source = record.get('source', 'unknown')
            analysis['source_distribution'][source] += 1
            
            # Language
            language = record.get('language', 'en')
            analysis['language_distribution'][language] += 1
            
            # Persona pillars
            pillars = record.get('persona_pillars', ['unknown'])
            if isinstance(pillars, str):
                pillars = [pillars]
            for pillar in pillars:
                analysis['persona_distribution'][pillar] += 1
        
        # Convert defaultdicts to regular dicts
        analysis['source_distribution'] = dict(analysis['source_distribution'])
        analysis['language_distribution'] = dict(analysis['language_distribution'])
        analysis['persona_distribution'] = dict(analysis['persona_distribution'])
        
        return analysis
    
    def print_analysis(self, analysis: Dict[str, Any]):
        """Print a formatted analysis report."""
        print("\n" + "=" * 60)
        print("TRAINING DATA ANALYSIS")
        print("=" * 60)
        
        print(f"\nTotal Records: {analysis['total_records']}")
        
        print("\n--- Source Distribution ---")
        for source, count in sorted(analysis['source_distribution'].items()):
            pct = (count / analysis['total_records']) * 100
            print(f"  {source}: {count} ({pct:.1f}%)")
        
        print("\n--- Language Distribution ---")
        for lang, count in sorted(analysis['language_distribution'].items()):
            pct = (count / analysis['total_records']) * 100
            print(f"  {lang}: {count} ({pct:.1f}%)")
        
        print("\n--- Persona Pillar Distribution ---")
        for pillar, count in sorted(analysis['persona_distribution'].items()):
            pct = (count / analysis['total_records']) * 100
            print(f"  {pillar}: {count} ({pct:.1f}%)")
        
        print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MERGER
# ═══════════════════════════════════════════════════════════════════════════════

class DataMerger:
    """Merges and balances training data from multiple sources."""
    
    def __init__(self, config: MergeConfig):
        self.config = config
    
    def merge(
        self,
        native_data: List[Dict[str, Any]],
        external_data: List[Dict[str, Any]],
        chat_data: List[Dict[str, Any]],
        balance: bool = True
    ) -> List[Dict[str, Any]]:
        """Merge all data sources into a unified dataset."""
        
        # Combine all data
        all_data = []
        all_data.extend(native_data)
        all_data.extend(external_data)
        all_data.extend(chat_data)
        
        logger.info(f"Combined {len(all_data)} total records")
        
        if balance:
            all_data = self._balance_personas(all_data)
        
        # Shuffle data
        import random
        random.shuffle(all_data)
        
        # Add unified IDs
        for i, record in enumerate(all_data):
            record['unified_id'] = f"UNIFIED_{i:06d}"
        
        return all_data
    
    def _balance_personas(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balance data by persona pillars."""
        # Group by primary persona
        by_persona = defaultdict(list)
        
        for record in data:
            pillars = record.get('persona_pillars', ['cultural_ambassador'])
            if isinstance(pillars, str):
                pillars = [pillars]
            primary = pillars[0] if pillars else 'cultural_ambassador'
            by_persona[primary].append(record)
        
        # Calculate target counts
        total = len(data)
        target_counts = {
            pillar: int(total * pct)
            for pillar, pct in self.config.target_distribution.items()
        }
        
        # Sample or oversample to balance
        balanced = []
        import random
        
        for pillar, target in target_counts.items():
            available = by_persona.get(pillar, [])
            
            if len(available) >= target:
                # Downsample
                balanced.extend(random.sample(available, target))
            else:
                # Use all available + oversample
                balanced.extend(available)
                if available:
                    extras_needed = target - len(available)
                    extras = random.choices(available, k=extras_needed)
                    balanced.extend(extras)
        
        logger.info(f"Balanced data: {len(data)} -> {len(balanced)} records")
        return balanced
    
    def save_unified(self, data: List[Dict[str, Any]], filename: str = "unified_training_data.jsonl"):
        """Save the unified dataset."""
        output_file = self.config.output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(data)} records to {output_file}")
        return output_file
    
    def save_splits(
        self,
        data: List[Dict[str, Any]],
        train_ratio: float = 0.9,
        val_ratio: float = 0.05,
        test_ratio: float = 0.05
    ) -> Dict[str, Path]:
        """Save train/val/test splits."""
        import random
        random.shuffle(data)
        
        total = len(data)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        splits = {
            'train': data[:train_end],
            'val': data[train_end:val_end],
            'test': data[val_end:],
        }
        
        output_files = {}
        for split_name, split_data in splits.items():
            output_file = self.config.output_dir / f"{split_name}.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for record in split_data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            output_files[split_name] = output_file
            logger.info(f"Saved {len(split_data)} {split_name} records to {output_file}")
        
        return output_files


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Merge external and native video training data'
    )
    
    parser.add_argument(
        '--no-balance',
        action='store_true',
        help='Skip persona balancing'
    )
    
    parser.add_argument(
        '--splits',
        action='store_true',
        help='Generate train/val/test splits'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze existing data, do not merge'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='unified_training_data.jsonl',
        help='Output filename'
    )
    
    args = parser.parse_args()
    
    # Initialize components
    config = MergeConfig()
    loader = DataLoader(config)
    analyzer = DataAnalyzer()
    merger = DataMerger(config)
    
    # Load all data
    print("\n📂 Loading training data...")
    all_data = loader.load_all_data()
    
    native_count = len(all_data['native'])
    external_count = len(all_data['external'])
    chat_count = len(all_data['chat'])
    total = native_count + external_count + chat_count
    
    print(f"\n📊 Data Summary:")
    print(f"  Native videos:   {native_count:,} records")
    print(f"  External videos: {external_count:,} records")
    print(f"  Chat logs:       {chat_count:,} records")
    print(f"  ─────────────────────────────")
    print(f"  Total:           {total:,} records")
    
    if args.analyze_only:
        # Just analyze and exit
        all_records = all_data['native'] + all_data['external'] + all_data['chat']
        analysis = analyzer.analyze(all_records)
        analyzer.print_analysis(analysis)
        return
    
    # Merge data
    print("\n🔄 Merging datasets...")
    unified_data = merger.merge(
        all_data['native'],
        all_data['external'],
        all_data['chat'],
        balance=not args.no_balance
    )
    
    # Analyze merged data
    print("\n📊 Analyzing merged data...")
    analysis = analyzer.analyze(unified_data)
    analyzer.print_analysis(analysis)
    
    # Save unified dataset
    print("\n💾 Saving unified dataset...")
    output_file = merger.save_unified(unified_data, args.output)
    print(f"✅ Saved to: {output_file}")
    
    # Generate splits if requested
    if args.splits:
        print("\n📁 Generating train/val/test splits...")
        split_files = merger.save_splits(unified_data)
        for split_name, split_file in split_files.items():
            print(f"  {split_name}: {split_file}")
    
    print("\n🎉 Merge complete!")
    print(f"\nNext steps:")
    print(f"  1. Review merged data: {output_file}")
    print(f"  2. Run training: python ml_training/modal_unified_training.py --dataset {output_file.name}")


if __name__ == '__main__':
    main()
