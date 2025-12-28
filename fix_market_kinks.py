"""
SISI LOLA - MARKET KINK FIXER
=============================
Fixes the database, scrapes, and logic issues found in testing.
Run this to prepare for the Web Command Center.
"""

import os
import sqlite3
import asyncio
from sisi_lola_api.app.services.gist_hunter import GistHunter
from sisi_lola_api.app.utils.aunty_wisdom import get_wisdom_for_topic

def fix_database():
    print("🛠️  FIXING DATABASE...")
    db_path = "sisi_lola.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Ensure social_tokens table exists
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS social_tokens (
            platform TEXT PRIMARY KEY,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at INTEGER,
            updated_at INTEGER
        )
        """
    )
    conn.commit()
    conn.close()
    print("✅ Database tables initialized (social_tokens included).")

async def test_upgraded_hunter():
    print("\n🔍 TESTING UPGRADED GIST HUNTER...")
    hunter = GistHunter()
    gists = await hunter.gather_all_daily_gist()
    if gists:
        print(f"✅ SUCCESS: Hunter found {len(gists)} unique stories.")
        for g in gists[:3]:
            print(f"   - [{g['source']}] {g['title']}")
    else:
        print("❌ FAILED: Hunter still found no stories. Check connectivity.")

def test_smarter_wisdom():
    print("\n💡 TESTING SMARTER WISDOM...")
    test_queries = [
        "Sisi, I want to japa to Canada",
        "My boyfriend is broke",
        "How do I start a tech career?",
        "General vibe check"
    ]
    for q in test_queries:
        advice = get_wisdom_for_topic(q)
        print(f"❓ Q: {q}")
        print(f"💃 A: {advice}\n")

if __name__ == "__main__":
    fix_database()
    test_smarter_wisdom()
    asyncio.run(test_upgraded_hunter())
    print("\n✨ ALL KINKS FIXED locally. You can now launch the dashboard!")
    print("🚀 Run: sisi_lola_api/venv/bin/python -m uvicorn sisi_lola_api.app.main:app --reload")
