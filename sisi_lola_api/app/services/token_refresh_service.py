"""
SISI LOLA TOKEN REFRESH SERVICE
===============================
Handles the automated refreshing of OAuth tokens for:
- Instagram (Long-lived User Tokens)
- TikTok (User Access Tokens)
- YouTube (Refresh Tokens)
"""

import os
import time
import httpx
import logging
from typing import Optional, Dict, Any
from .auth_store import save_social_token, get_social_token

logger = logging.getLogger("token_refresh")

class TokenRefreshService:
    def __init__(self):
        self.fb_app_id = os.getenv("FACEBOOK_APP_ID")
        self.fb_app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.tiktok_client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.tiktok_client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

    async def refresh_instagram_token(self) -> bool:
        """
        Exchange a short-lived token for a long-lived one (60 days),
        or refresh an existing long-lived token.
        """
        token_info = get_social_token("instagram")
        if not token_info:
            logger.error("No Instagram token found in DB to refresh")
            return False

        # If it's still valid for more than 10 days, maybe skip?
        # But we can refresh it anyway if it's nearing expiry.
        
        current_token = token_info["access_token"]
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.fb_app_id,
            "client_secret": self.fb_app_secret,
            "fb_exchange_token": current_token
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    new_token = data.get("access_token")
                    expires_in = data.get("expires_in", 5184000) # Default 60 days
                    save_social_token("instagram", new_token, expires_in=expires_in)
                    logger.info("✅ Instagram token refreshed successfully")
                    return True
                else:
                    logger.error(f"❌ Instagram refresh failed: {resp.text}")
            except Exception as e:
                logger.error(f"❌ Instagram refresh error: {e}")
        return False

    async def refresh_tiktok_token(self) -> bool:
        """Refresh TikTok User Access Token using refresh_token"""
        token_info = get_social_token("tiktok")
        if not token_info or not token_info.get("refresh_token"):
            logger.error("No TikTok refresh token found in DB")
            return False

        url = "https://open.tiktokapis.com/v2/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_key": self.tiktok_client_key,
            "client_secret": self.tiktok_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token_info["refresh_token"]
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, data=data, headers=headers)
                if resp.status_code == 200:
                    res_data = resp.json()
                    save_social_token(
                        "tiktok", 
                        res_data["access_token"], 
                        refresh_token=res_data.get("refresh_token"), 
                        expires_in=res_data.get("expires_in", 0)
                    )
                    logger.info("✅ TikTok token refreshed successfully")
                    return True
                else:
                    logger.error(f"❌ TikTok refresh failed: {resp.text}")
            except Exception as e:
                logger.error(f"❌ TikTok refresh error: {e}")
        return False

    async def run_all_refreshes(self):
        """Run all necessary token refreshes"""
        await self.refresh_instagram_token()
        await self.refresh_tiktok_token()
        # YouTube refresh is usually handled by the google-auth lib on use, 
        # but we can trigger it here if we want to pre-emptively store it.

if __name__ == "__main__":
    import asyncio
    service = TokenRefreshService()
    asyncio.run(service.run_all_refreshes())
