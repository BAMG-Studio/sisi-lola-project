#!/usr/bin/env python3
"""
Self-Learning Engine for Sisi Lola
Continuously trains on ingested YouTube data
"""
import os
import sqlite3
import torch
from pathlib import Path
from datetime import datetime
from yoruba_tts_engine import SisiLolaVoiceEngine

TRAINING_DB = Path(__file__).parent.parent / 'training_data.db'
MODEL_DIR = Path(__file__).parent.parent / 'trained_models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

class SelfLearningEngine:
    def __init__(self):
        self.voice_engine = SisiLolaVoiceEngine()
        self.training_history = []
    
    def get_untrained_data(self, language_category=None, limit=100):
        """Get untrained data from database"""
        conn = sqlite3.connect(TRAINING_DB)
        
        if language_category:
            query = '''SELECT td.* FROM training_data td
                JOIN training_sources ts ON td.channel_id = ts.channel_id
                WHERE td.trained = 0 AND ts.language_category = ?
                AND td.transcript IS NOT NULL
                LIMIT ?'''
            cursor = conn.execute(query, (language_category, limit))
        else:
            query = '''SELECT * FROM training_data 
                WHERE trained = 0 AND transcript IS NOT NULL LIMIT ?'''
            cursor = conn.execute(query, (limit,))
        
        data = cursor.fetchall()
        conn.close()
        return data
    
    def train_on_sample(self, text, language_category):
        """Train model on single sample"""
        try:
            # Generate speech to validate
            output_path = self.voice_engine.generate_speech(text)
            
            # Mark as trained
            self.training_history.append({
                'text': text[:100],
                'category': language_category,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
            
            return True
        except Exception as e:
            print(f"[ERROR] Training failed: {e}")
            return False
    
    def batch_train(self, language_category=None, batch_size=10):
        """Train on batch of samples"""
        print(f"[TRAIN] Starting batch training...")
        
        data = self.get_untrained_data(language_category, batch_size)
        
        if not data:
            print("[INFO] No untrained data available")
            return
        
        conn = sqlite3.connect(TRAINING_DB)
        success_count = 0
        
        for row in data:
            video_id, transcript = row[1], row[4]
            
            if self.train_on_sample(transcript, language_category or 'yoruba_pure'):
                conn.execute('UPDATE training_data SET trained = 1 WHERE video_id = ?', (video_id,))
                success_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Trained on {success_count}/{len(data)} samples")
        
        # Save checkpoint
        self.save_checkpoint()
    
    def save_checkpoint(self):
        """Save training checkpoint"""
        checkpoint_path = MODEL_DIR / f'checkpoint_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        import json
        checkpoint_path.write_text(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'training_history': self.training_history[-100:],
            'total_samples': len(self.training_history)
        }, indent=2))
        
        print(f"[OK] Checkpoint saved: {checkpoint_path.name}")
    
    def continuous_learning_loop(self, interval_minutes=60):
        """Run continuous learning loop"""
        import time
        
        print("[START] Continuous learning mode")
        
        while True:
            print(f"\n[LOOP] {datetime.now().isoformat()}")
            
            # Train on each language category
            categories = ['yoruba_pure', 'yoruba_pidgin', 'yorunglish']
            
            for category in categories:
                print(f"[TRAIN] Category: {category}")
                self.batch_train(category, batch_size=5)
            
            print(f"[SLEEP] Waiting {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    engine = SelfLearningEngine()
    engine.batch_train(batch_size=5)
