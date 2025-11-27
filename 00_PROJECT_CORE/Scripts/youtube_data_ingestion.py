#!/usr/bin/env python3
"""
YouTube Data Ingestion System for Sisi Lola
Continuously ingests Yoruba content for training
"""
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build

env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

TRAINING_DB = Path(__file__).parent.parent / 'training_data.db'

class YouTubeDataIngestion:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(TRAINING_DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS training_sources (
            id INTEGER PRIMARY KEY,
            channel_id TEXT UNIQUE,
            channel_name TEXT,
            language_category TEXT,
            subscriber_count INTEGER,
            video_count INTEGER,
            last_ingested TEXT,
            status TEXT
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS training_data (
            id INTEGER PRIMARY KEY,
            video_id TEXT UNIQUE,
            channel_id TEXT,
            title TEXT,
            transcript TEXT,
            language_detected TEXT,
            duration INTEGER,
            ingested_at TEXT,
            trained BOOLEAN DEFAULT 0
        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS language_categories (
            id INTEGER PRIMARY KEY,
            category TEXT UNIQUE,
            description TEXT,
            sample_count INTEGER DEFAULT 0,
            last_trained TEXT
        )''')
        
        # Seed language categories
        categories = [
            ('yoruba_pure', 'Pure Yoruba content'),
            ('yoruba_pidgin', 'Yoruba with Nigerian Pidgin'),
            ('yorunglish', 'Yoruba-English code-switching'),
            ('nigerian_english', 'Nigerian English accent'),
            ('afrobeats_yoruba', 'Afrobeats music with Yoruba lyrics')
        ]
        
        conn.executemany('INSERT OR IGNORE INTO language_categories (category, description) VALUES (?, ?)', categories)
        conn.commit()
        conn.close()
    
    def search_yoruba_creators(self, max_results=50):
        """Search for top Yoruba content creators"""
        queries = [
            'yoruba podcast',
            'yoruba comedy',
            'yoruba news',
            'yoruba vlog',
            'yoruba tutorial'
        ]
        
        channels = []
        for query in queries:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='channel',
                maxResults=max_results,
                relevanceLanguage='yo'
            )
            response = request.execute()
            
            for item in response.get('items', []):
                channels.append({
                    'channel_id': item['id']['channelId'],
                    'channel_name': item['snippet']['title'],
                    'description': item['snippet']['description']
                })
        
        return channels
    
    def add_training_source(self, channel_id, language_category='yoruba_pure'):
        """Add channel as training source"""
        conn = sqlite3.connect(TRAINING_DB)
        
        # Get channel details
        request = self.youtube.channels().list(
            part='statistics,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if response['items']:
            channel = response['items'][0]
            stats = channel['statistics']
            
            conn.execute('''INSERT OR REPLACE INTO training_sources 
                (channel_id, channel_name, language_category, subscriber_count, video_count, last_ingested, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (channel_id, channel['snippet']['title'], language_category,
                 int(stats.get('subscriberCount', 0)), int(stats.get('videoCount', 0)),
                 datetime.now().isoformat(), 'active'))
            
            conn.commit()
            print(f"[OK] Added: {channel['snippet']['title']}")
        
        conn.close()
    
    def ingest_channel_videos(self, channel_id, max_videos=10):
        """Ingest recent videos from channel"""
        request = self.youtube.search().list(
            part='snippet',
            channelId=channel_id,
            type='video',
            maxResults=max_videos,
            order='date'
        )
        response = request.execute()
        
        conn = sqlite3.connect(TRAINING_DB)
        
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            
            conn.execute('''INSERT OR IGNORE INTO training_data 
                (video_id, channel_id, title, ingested_at)
                VALUES (?, ?, ?, ?)''',
                (video_id, channel_id, item['snippet']['title'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Ingested {len(response.get('items', []))} videos")

if __name__ == '__main__':
    ingestion = YouTubeDataIngestion()
    print("[OK] YouTube ingestion system ready")
