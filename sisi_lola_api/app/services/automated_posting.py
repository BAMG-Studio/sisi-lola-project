"""
SISI LOLA AUTOMATED POSTING SERVICE
=====================================
Automated content posting to TikTok, Instagram, and YouTube.
Integrates with vibes production system and scheduling calendar.
"""

import os
import json
import asyncio
import httpx
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import schedule
import time
import dropbox
from threading import Thread

load_dotenv()

# Platform API Configurations
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN") # Optional if using Refresh Token logic

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class PostResult:
    """Result of a post attempt"""
    platform: str
    vibe_id: str
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    posted_at: Optional[str] = None


class AutomatedPostingService:
    """
    Service for automated posting of Sisi Lola vibes to social platforms.
    
    Supports:
    - TikTok (via TikTok API)
    - Instagram (via Graph API)
    - YouTube Shorts (via YouTube Data API)
    - Facebook (via Graph API)
    
    Usage:
        service = AutomatedPostingService()
        
        # Post a single vibe
        result = await service.post_vibe("VIBE001", platform="tiktok")
        
        # Schedule all vibes
        service.schedule_all_vibes()
        service.run_scheduler()
    """
    
    def __init__(self):
        self.vibes_file = PROJECT_ROOT / "03_MEDIA_ASSETS" / "content_queue" / "vibes_batch_december_2025.json"
        self.produced_dir = PROJECT_ROOT / "03_MEDIA_ASSETS" / "produced_vibes"
        self.logs_dir = PROJECT_ROOT / "03_MEDIA_ASSETS" / "posting_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.vibes_data = self._load_vibes()
        self.post_history = self._load_history()
        
    def _load_vibes(self) -> Dict:
        """Load vibes from JSON"""
        if self.vibes_file.exists():
            with open(self.vibes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"vibes": []}
    
    def _load_history(self) -> Dict:
        """Load posting history"""
        history_file = self.logs_dir / "post_history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"posts": []}
    
    def _save_history(self):
        """Save posting history"""
        history_file = self.logs_dir / "post_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.post_history, f, indent=2)
    
    def get_vibe(self, vibe_id: str) -> Optional[Dict]:
        """Get vibe by ID"""
        for vibe in self.vibes_data.get("vibes", []):
            if vibe.get("vibe_id") == vibe_id:
                return vibe
        return None
    
    def get_produced_assets(self, vibe_id: str) -> Dict:
        """Get produced assets for a vibe"""
        metadata_file = self.produced_dir / f"{vibe_id}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    async def _get_public_url(self, local_path: Path) -> Optional[str]:
        """Uploads file to Dropbox and returns a direct download URL"""
        if not DROPBOX_APP_KEY or not DROPBOX_APP_SECRET:
            print("⚠️ Dropbox creds missing, cannot generate public URL for Meta")
            return None
            
        try:
            # Note: For production, we'd use refresh tokens. 
            # For now, we assume a valid access token or a simple upload logic.
            dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN) if DROPBOX_ACCESS_TOKEN else None
            if not dbx:
                print("⚠️ DROPBOX_ACCESS_TOKEN not found in environment.")
                return None
                
            remote_path = f"/sisilola_dispatch/{local_path.name}"
            
            # 1. Upload file
            with open(local_path, "rb") as f:
                dbx.files_upload(f.read(), remote_path, mode=dropbox.files.WriteMode.overwrite)
            
            # 2. Try to create shared link
            try:
                shared_link = dbx.sharing_create_shared_link_with_settings(remote_path)
                url = shared_link.url
            except dropbox.exceptions.ApiError as e:
                # If link already exists, list it
                if e.error.is_shared_link_already_exists():
                    links = dbx.sharing_list_shared_links(path=remote_path, direct_only=True).links
                    if links:
                        url = links[0].url
                    else:
                        return None
                else:
                    raise e
            
            # Convert to direct link (?dl=1)
            return url.replace("?dl=0", "?dl=1")
        except Exception as e:
            if "expired_access_token" in str(e):
                print("❌ Dropbox Token Expired! Please generate a new one from App Console.")
            print(f"❌ Dropbox Upload Error: {e}")
            return None

    async def post_to_tiktok(self, vibe: Dict, video_path: Path) -> PostResult:
        """
        Post to TikTok using TikTok Content Posting API.
        
        Note: Requires TikTok API access and approved app.
        """
        vibe_id = vibe["vibe_id"]
        
        if not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
            return PostResult(
                platform="tiktok",
                vibe_id=vibe_id,
                success=False,
                error="TIKTOK credentials (client_key/secret) not configured"
            )
        
        if not video_path.exists():
            return PostResult(
                platform="tiktok",
                vibe_id=vibe_id,
                success=False,
                error=f"Video file not found: {video_path}"
            )
        
        # TikTok API v2 endpoint (Simplified for demo - requires Access Token)
        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        
        # Look for token in DB first
        from .auth_store import get_social_token
        token_data = get_social_token("tiktok")
        access_token = token_data["access_token"] if token_data else TIKTOK_CLIENT_KEY # fallback to env key if not OAuth flow
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Build caption with hashtags
        hashtags_str = " ".join(f"#{tag}" for tag in vibe.get("hashtags", [])[:10])
        caption = f"{vibe.get('caption', '')[:150]}\n\n{hashtags_str}"
        
        payload = {
            "post_info": {
                "title": vibe.get("title", ""),
                "description": caption,
                "privacy_level": "PUBLIC_TO_EVERYONE"
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_path.stat().st_size
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Initialize upload
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    upload_url = data.get("data", {}).get("upload_url")
                    
                    if upload_url:
                        # Upload video
                        with open(video_path, 'rb') as f:
                            upload_response = await client.put(
                                upload_url,
                                content=f.read(),
                                headers={"Content-Type": "video/mp4"}
                            )
                        
                        if upload_response.status_code == 200:
                            return PostResult(
                                platform="tiktok",
                                vibe_id=vibe_id,
                                success=True,
                                post_id=data.get("data", {}).get("publish_id"),
                                posted_at=datetime.now().isoformat()
                            )
                
                return PostResult(
                    platform="tiktok",
                    vibe_id=vibe_id,
                    success=False,
                    error=f"TikTok API error: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            return PostResult(
                platform="tiktok",
                vibe_id=vibe_id,
                success=False,
                error=str(e)
            )
    
    async def post_to_instagram(self, vibe: Dict, video_path: Path) -> PostResult:
        """
        Post to Instagram Reels using Graph API.
        
        Note: Requires Instagram Business Account and Facebook Developer App.
        """
        vibe_id = vibe["vibe_id"]
        
        # Look for token in DB first
        from .auth_store import get_social_token
        token_data = get_social_token("instagram")
        access_token = token_data["access_token"] if token_data else (INSTAGRAM_ACCESS_TOKEN)
        
        if not access_token:
            return PostResult(
                platform="instagram",
                vibe_id=vibe_id,
                success=False,
                error="Instagram/Meta credentials (access_token) not found in DB or .env"
            )
            
        ig_id = INSTAGRAM_BUSINESS_ACCOUNT_ID or FACEBOOK_PAGE_ID
        if not ig_id:
            return PostResult(
                platform="instagram",
                vibe_id=vibe_id,
                success=False,
                error="Instagram/Meta credentials (ID) not configured"
            )
        
        # Instagram Graph API endpoints
        base_url = f"https://graph.facebook.com/v18.0/{ig_id}"
        
        # Build caption
        hashtags_str = " ".join(f"#{tag}" for tag in vibe.get("hashtags", [])[:30])
        caption = f"{vibe.get('caption', '')}\n\n{hashtags_str}"
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Step 0: Ensure we have a public URL (Meta requirement)
                video_url = await self._get_public_url(video_path)
                if not video_url:
                    return PostResult(
                        platform="instagram",
                        vibe_id=vibe_id,
                        success=False,
                        error="Failed to host video on Dropbox (Required for Instagram API)"
                    )

                # Step 1: Create media container
                create_url = f"{base_url}/media"
                create_params = {
                    "access_token": access_token,
                    "media_type": "REELS",
                    "video_url": video_url, 
                    "caption": caption[:2200],
                    "share_to_feed": "true"
                }
                
                response = await client.post(create_url, params=create_params)
                
                if response.status_code == 200:
                    container_id = response.json().get("id")
                    
                    # Step 2: Polling for status
                    # Reels processing can take 30-300 seconds (5 mins for large or slow days)
                    max_attempts = 30 
                    print(f"   ... Waiting for Meta to digest {vibe_id} (can take a few mins)...")
                    for attempt in range(max_attempts):
                        await asyncio.sleep(15) 
                        status_url = f"https://graph.facebook.com/v18.0/{container_id}"
                        # Start with minimal fields to avoid "nonexisting field" errors
                        status_params = {
                            "fields": "status_code",
                            "access_token": INSTAGRAM_ACCESS_TOKEN
                        }
                        status_resp = await client.get(status_url, params=status_params)
                        if status_resp.status_code == 200:
                            status_data = status_resp.json()
                            status_code = status_data.get("status_code")
                            print(f"   ... [{attempt+1}/{max_attempts}] Item {vibe_id} status: {status_code}")
                            
                            if status_code == "FINISHED":
                                break
                            elif status_code == "ERROR":
                                # If error, try to get details separately
                                detail_resp = await client.get(status_url, params={
                                    "fields": "status_code,status_error_description",
                                    "access_token": INSTAGRAM_ACCESS_TOKEN
                                })
                                error_msg = detail_resp.json().get("status_error_description", "Unknown processing error") if detail_resp.status_code == 200 else "Unknown error"
                                return PostResult(
                                    platform="instagram",
                                    vibe_id=vibe_id,
                                    success=False,
                                    error=f"Instagram processing error: {error_msg}"
                                )
                        else:
                            print(f"   ⚠️ Status fetch error ({status_resp.status_code}): {status_resp.text}")

                        if attempt == max_attempts - 1:
                            return PostResult(
                                platform="instagram",
                                vibe_id=vibe_id,
                                success=False,
                                error="Instagram processing timeout (video still pending after 7.5 mins)"
                            )
                    
                    # Step 3: Publish
                    publish_url = f"{base_url}/media_publish"
                    publish_params = {
                        "access_token": INSTAGRAM_ACCESS_TOKEN,
                        "creation_id": container_id
                    }
                    
                    publish_response = await client.post(publish_url, params=publish_params)
                    
                    if publish_response.status_code == 200:
                        post_id = publish_response.json().get("id")
                        return PostResult(
                            platform="instagram",
                            vibe_id=vibe_id,
                            success=True,
                            post_id=post_id,
                            post_url=f"https://instagram.com/p/{post_id}",
                            posted_at=datetime.now().isoformat()
                        )
                    else:
                        return PostResult(
                            platform="instagram",
                            vibe_id=vibe_id,
                            success=False,
                            error=f"Instagram Publish error: {publish_response.text}"
                        )
                
                return PostResult(
                    platform="instagram",
                    vibe_id=vibe_id,
                    success=False,
                    error=f"Instagram Container error: {response.text}"
                )
                
        except Exception as e:
            return PostResult(
                platform="instagram",
                vibe_id=vibe_id,
                success=False,
                error=str(e)
            )
    
    async def post_to_youtube(self, vibe: Dict, video_path: Path) -> PostResult:
        """
        Post to YouTube Shorts using OAuth.
        """
        vibe_id = vibe["vibe_id"]
        title = vibe.get("title", f"Sisi Lola - {vibe_id}")
        caption = vibe.get("caption", "")
        
        # Check for OAuth token
        token_path = "youtube_token.json"
        if not os.path.exists(token_path):
            return PostResult(
                platform="youtube",
                vibe_id=vibe_id,
                success=False,
                error="YouTube posting requires OAuth setup. Run 'setup_youtube_oauth.py' first."
            )
            
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            creds = Credentials.from_authorized_user_file(token_path)
            youtube = build("youtube", "v3", credentials=creds)
            
            # Auto-add #Shorts to title and description for market readiness
            v_title = title if "#Shorts" in title else f"{title[:90]} #Shorts"
            v_desc = f"{caption}\n\n#Shorts #SisiLola #NewAfrica"
            
            body = {
                "snippet": {
                    "title": v_title,
                    "description": v_desc,
                    "tags": vibe.get("tags", []) + ["Shorts", "SisiLola"],
                    "categoryId": "22"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }
            
            print(f"   📺 Uploading to YouTube Shorts: {v_title}")
            insert_request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(str(video_path), chunksize=1024*1024, resumable=True)
            )
            
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    print(f"   ... Upload {int(status.progress() * 100)}% complete")
            
            return PostResult(
                platform="youtube",
                vibe_id=vibe_id,
                success=True,
                post_id=response.get("id"),
                post_url=f"https://youtu.be/{response.get('id')}",
                posted_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            return PostResult(
                platform="youtube",
                vibe_id=vibe_id,
                success=False,
                error=f"YouTube Upload Error: {str(e)}"
            )
        
    async def post_to_facebook(self, vibe: Dict, video_path: Path) -> PostResult:
        """
        Post to Facebook Page Feed.
        """
        vibe_id = vibe["vibe_id"]
        
        if not FACEBOOK_PAGE_ID or not INSTAGRAM_ACCESS_TOKEN:
            return PostResult(
                platform="facebook",
                vibe_id=vibe_id,
                success=False,
                error="Facebook credentials (FACEBOOK_PAGE_ID/TOKEN) not configured"
            )
            
        return PostResult(
            platform="facebook",
            vibe_id=vibe_id,
            success=False,
            error="Facebook Graph API Posting implementation in progress"
        )
    
    async def post_vibe(self, vibe_id: str, platform: str, video_path: Optional[Path] = None) -> PostResult:
        """
        Post a vibe to a specific platform.
        
        Args:
            vibe_id: The vibe to post
            platform: Target platform (tiktok, instagram, youtube, facebook)
            video_path: Path to video file (if not provided, looks in produced_vibes)
        """
        vibe = self.get_vibe(vibe_id)
        if not vibe:
            return PostResult(
                platform=platform,
                vibe_id=vibe_id,
                success=False,
                error=f"Vibe {vibe_id} not found"
            )
        
        # Find video file
        if not video_path:
            # Look for produced video
            video_path = self.produced_dir / f"{vibe_id}.mp4"
            if not video_path.exists():
                # Try finding any MP4 with vibe_id
                mp4_files = list(self.produced_dir.glob(f"{vibe_id}*.mp4"))
                if mp4_files:
                    video_path = mp4_files[0]
        
        print(f"\n📤 Posting {vibe_id} to {platform}...")
        print(f"   Title: {vibe.get('title')}")
        print(f"   Video: {video_path}")
        
        # Route to platform-specific handler
        platform_norm = platform.lower().replace("_", "")
        if "tiktok" in platform_norm:
            result = await self.post_to_tiktok(vibe, video_path)
        elif any(p in platform_norm for p in ["instagram", "ig", "reels"]):
            result = await self.post_to_instagram(vibe, video_path)
        elif any(p in platform_norm for p in ["youtube", "yt", "shorts"]):
            # Check for YouTube Shorts platform in vibe metadata
            result = await self.post_to_youtube(vibe, video_path)
        elif "facebook" in platform_norm or "fb" in platform_norm:
            result = await self.post_to_facebook(vibe, video_path)
        else:
            result = PostResult(
                platform=platform,
                vibe_id=vibe_id,
                success=False,
                error=f"Unsupported platform: {platform}"
            )
        
        # Log result
        self.post_history["posts"].append({
            "vibe_id": vibe_id,
            "platform": platform,
            "success": result.success,
            "post_id": result.post_id,
            "error": result.error,
            "timestamp": datetime.now().isoformat()
        })
        self._save_history()
        
        if result.success:
            print(f"   ✅ Posted successfully! ID: {result.post_id}")
        else:
            print(f"   ❌ Failed: {result.error}")
        
        return result
    
    def get_scheduled_vibes(self) -> List[Dict]:
        """Get all scheduled vibes with their times"""
        calendar = self.vibes_data.get("deployment_calendar", {})
        scheduled = []
        
        for week, dates in calendar.items():
            for date_str, vibe_info in dates.items():
                vibe = self.get_vibe(vibe_info["vibe_id"])
                if vibe:
                    scheduled.append({
                        "vibe_id": vibe_info["vibe_id"],
                        "date": date_str,
                        "time_wat": vibe_info.get("time_wat", "00:00"),
                        "platform": vibe_info.get("primary_platform"),
                        "title": vibe.get("title"),
                        "scheduled": datetime.fromisoformat(date_str + "T" + vibe_info.get("time_wat", "00:00") + ":00")
                    })
        
        return sorted(scheduled, key=lambda x: x["scheduled"])
    
    def schedule_post_job(self, vibe_id: str, platform: str, post_time: datetime):
        """Schedule a single post job"""
        job_tag = f"{vibe_id}_{platform}"
        
        # Convert to schedule format (HH:MM)
        time_str = post_time.strftime("%H:%M")
        
        def job():
            print(f"\n⏰ Scheduled post triggered: {vibe_id} -> {platform}")
            asyncio.run(self.post_vibe(vibe_id, platform))
        
        # Schedule for the specific date and time
        schedule.every().day.at(time_str).do(job).tag(job_tag)
        print(f"   📅 Scheduled {vibe_id} for {platform} at {time_str}")
    
    def schedule_all_vibes(self):
        """Schedule all vibes from the deployment calendar"""
        scheduled_vibes = self.get_scheduled_vibes()
        
        print(f"\n{'='*60}")
        print(f"📅 SCHEDULING {len(scheduled_vibes)} VIBES")
        print(f"{'='*60}")
        
        for item in scheduled_vibes:
            self.schedule_post_job(
                vibe_id=item["vibe_id"],
                platform=item["platform"],
                post_time=item["scheduled"]
            )
        
        print(f"\n✅ All vibes scheduled!")
        return scheduled_vibes
    
    def run_scheduler(self, blocking: bool = True):
        """
        Run the scheduler.
        
        Args:
            blocking: If True, runs in foreground. If False, runs in background thread.
        """
        print(f"\n🚀 Scheduler running...")
        print(f"   Press Ctrl+C to stop")
        
        if blocking:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        else:
            def run():
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            
            thread = Thread(target=run, daemon=True)
            thread.start()
            return thread
    
    def get_posting_status(self) -> Dict:
        """Get current posting status and upcoming schedule"""
        scheduled = self.get_scheduled_vibes()
        now = datetime.now()
        
        upcoming = [s for s in scheduled if s["scheduled"] > now]
        past = [s for s in scheduled if s["scheduled"] <= now]
        
        # Check what's been posted
        posted_ids = {p["vibe_id"] for p in self.post_history.get("posts", []) if p["success"]}
        
        return {
            "total_scheduled": len(scheduled),
            "upcoming": len(upcoming),
            "completed": len([p for p in past if p["vibe_id"] in posted_ids]),
            "pending": len([p for p in past if p["vibe_id"] not in posted_ids]),
            "next_post": upcoming[0] if upcoming else None,
            "post_history": self.post_history.get("posts", [])[-10:]  # Last 10
        }


# Convenience functions
async def post_now(vibe_id: str, platform: str) -> PostResult:
    """Quick function to post a vibe immediately"""
    service = AutomatedPostingService()
    return await service.post_vibe(vibe_id, platform)


def start_scheduler():
    """Start the automated posting scheduler"""
    service = AutomatedPostingService()
    service.schedule_all_vibes()
    service.run_scheduler()


def show_schedule():
    """Display the posting schedule"""
    service = AutomatedPostingService()
    scheduled = service.get_scheduled_vibes()
    
    print(f"\n{'='*60}")
    print(f"📅 SISI LOLA POSTING SCHEDULE")
    print(f"{'='*60}")
    
    for item in scheduled:
        status = "✅" if item["scheduled"] < datetime.now() else "⏳"
        print(f"{status} {item['date']} @ {item['time_wat']} WAT")
        print(f"   {item['vibe_id']}: {item['title']}")
        print(f"   📱 {item['platform']}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--schedule":
            show_schedule()
        elif cmd == "--start":
            start_scheduler()
        elif cmd == "--status":
            service = AutomatedPostingService()
            status = service.get_posting_status()
            print(json.dumps(status, indent=2, default=str))
        else:
            print("Usage:")
            print("  python automated_posting.py --schedule  # Show schedule")
            print("  python automated_posting.py --start     # Start scheduler")
            print("  python automated_posting.py --status    # Show status")
    else:
        show_schedule()
