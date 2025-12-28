"""
SISI LOLA DAILY BRIEFING JOB
============================
Automated job to refresh the Daily Gist Briefing.
Ensures Sisi Lola is always 'Soji' (up to date).
"""

import asyncio
import schedule
import time
from threading import Thread
from .gist_hunter import GistHunter

async def refresh_gist():
    print("🌅 DAILY JOB: Running the Morning Gist Hunt...")
    hunter = GistHunter()
    try:
        gists = await hunter.gather_all_daily_gist()
        briefing = hunter.generate_daily_briefing(gists)
        
        output_path = "sisi_lola_api/data/daily_briefing.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(briefing)
        print("✅ DAILY JOB: Sisi is now updated with the latest headlines!")
    except Exception as e:
        print(f"❌ DAILY JOB: Gist hunt failed: {e}")

def run_refresh():
    asyncio.run(refresh_gist())

def start_gist_scheduler():
    # Schedule to run every day at 6:00 AM WAT
    schedule.every().day.at("06:00").do(run_refresh)
    
    # Run once at startup to ensure it's not empty
    run_refresh()
    
    print("⏳ Gist Scheduler active. Next run at 06:00 AM.")
    
    def job_loop():
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    thread = Thread(target=job_loop, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    start_gist_scheduler()
    while True:
        time.sleep(1)
