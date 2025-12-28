"""
SISI LOLA GIST HUNTER - THE CULTURAL RADAR (V2 SUPREME)
==========================================================
Scrapes trending Nigerian topics, Afrobeats news, and current gists
to provide 'Soji' intelligence for Sisi's Radio Show & Chat.
Expanded to include Africa, Global, Politics, Religion, and more.
"""

import os
import httpx
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional

class GistHunter:
    def __init__(self):
        self.sources = {
            "general": "https://www.pulse.ng/news",
            "bellanaija": "https://www.bellanaija.com/",
            "political": "https://punchng.com/topics/news/",
            "sports": "https://punchng.com/topics/sports/",
            "entertainment": "https://www.pulse.ng/entertainment",
            "africa": "https://www.premiumtimesng.com/category/foreign/africa-news",
            "global": "https://www.premiumtimesng.com/category/foreign/world-news",
            "lifestyle": "https://www.premiumtimesng.com/category/lifestyle",
            "tech": "https://punchng.com/topics/technology/",
            "money": "https://nairametrics.com/category/finance/",
            "religion": "https://www.vanguardngr.com/category/religion/",
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    async def fetch_category_gist(self, category: str) -> List[Dict[str, str]]:
        """Scrape latest from a specific category URL"""
        url = self.sources.get(category, self.sources["general"])
        print(f"🔍 HUNTER: Scouting {category} radar at {url}...")
        
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url, timeout=20.0)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    articles = soup.find_all(['h1', 'h2', 'h3', 'a'], limit=30)
                    gists = []
                    
                    for art in articles:
                        title = art.get_text(strip=True)
                        link = art.get('href') if art.name == 'a' else (art.find('a').get('href') if art.find('a') else None)
                        
                        if title and len(title) > 25 and link and link.startswith('http'):
                            gists.append({
                                "title": title,
                                "url": link,
                                "source": category.capitalize()
                            })
                            if len(gists) >= 15: break
                    return gists
            except Exception as e:
                print(f"❌ {category} scrape failed: {e}")
        return []

    async def sync_radar_v2(self, scope: str = "nigeria") -> str:
        """
        Orchestrate a targeted hunt based on scope.
        Scopes: nigeria, africa, global
        """
        if scope == "nigeria":
            categories = ["general", "political", "sports", "entertainment", "money", "religion"]
        elif scope == "africa":
            categories = ["africa", "lifestyle"]
        elif scope == "global":
            categories = ["global", "tech"]
        else:
            categories = ["general"]

        tasks = [self.fetch_category_gist(cat) for cat in categories]
        results = await asyncio.gather(*tasks)
        
        # Flatten and unique
        all_gists = [item for sublist in results for item in sublist]
        unique_gists = []
        seen = set()
        for g in all_gists:
            if g['title'].lower() not in seen:
                unique_gists.append(g)
                seen.add(g['title'].lower())
        
        briefing = self.generate_daily_briefing(unique_gists, scope)
        
        # Save to specific scope file if needed, but primary is daily_briefing.txt
        output_path = "sisi_lola_api/data/daily_briefing.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Append or overwrite? Let's append with a timestamp if overwrite is not desired, 
        # but for Sisi's brain, we want the CURRENT context. So overwrite the main one.
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(briefing)
            
        return briefing

    def generate_daily_briefing(self, gists: List[Dict[str, str]], scope: str = "nigeria") -> str:
        """Format gists for Sisi's LLM consumption"""
        briefing = f"DAILY GIST REPORT [{scope.upper()}] - {datetime.now().strftime('%d %b %Y')}\n"
        briefing += "="*60 + "\n"
        briefing += "INSTRUCTION: Sisi, use these REAL-WORLD events to inform your gists today. Be very specific!\n\n"
        
        for i, gist in enumerate(gists, 1):
            briefing += f"{i}. [{gist['source']}] {gist['title']}\n"
        return briefing

async def main():
    hunter = GistHunter()
    # Default sync all for initialization
    for scope in ["nigeria", "africa", "global"]:
        await hunter.sync_radar_v2(scope)
    print("✅ Supreme Gist Hunter Sync Complete.")

if __name__ == "__main__":
    asyncio.run(main())
