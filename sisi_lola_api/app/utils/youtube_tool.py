"""
Sisi Lola YouTube Transcript & Vision Tool
Allows Sisi Lola to "see" what is happening in a video or link.
"""

import re
import httpx
from typing import Optional

async def get_youtube_info(url: str) -> str:
    """
    Fetches transcript or metadata for a YouTube video.
    """
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if not video_id_match:
        return "I can't find the video ID in that link, darling. Check am again."
    
    video_id = video_id_match.group(1)
    
    # Try using a transcript API or fallback to metadata scraping
    # For now, we'll provide a robust metadata fetcher
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # We use an oembed or simple scrape to get title/owner if transcript is unavailable
            response = await client.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json")
            if response.status_code == 200:
                data = response.json()
                return f"Video Title: {data.get('title')}\nAuthor: {data.get('author_name')}\nStatus: I've scanned the metadata. Tell me what specific part you want to discuss!"
            else:
                return "The video seems private or restricted, omo. I no fit enter inside."
    except Exception as e:
        return f"Small wahala occurred while trying to watch that: {str(e)}"

def extract_urls(text: str) -> list:
    """Find URLs in text"""
    return re.findall(r'(https?://[^\s]+)', text)
