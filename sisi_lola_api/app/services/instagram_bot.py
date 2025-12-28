"""
SISI LOLA INSTAGRAM BOT
Automated engagement with Sisi Lola's personality
"""

import os
import asyncio
import json
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sisi_lola_instagram")

class MessageType(str, Enum):
    DM = "direct_message"
    COMMENT = "comment"
    MENTION = "mention"
    STORY_REPLY = "story_reply"

@dataclass
class InstagramMessage:
    """Incoming Instagram message"""
    message_id: str
    user_id: str
    username: str
    text: str
    message_type: MessageType
    media_id: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class SisiLolaReply:
    """Outgoing reply from Sisi Lola"""
    text: str
    audio_url: Optional[str] = None
    voice_note: bool = False
    emoji_reaction: Optional[str] = None
    personality_score: float = 0.0


class InstagramAPI:
    """
    Instagram API wrapper for Sisi Lola
    
    Uses Meta's Instagram Graph API for:
    - Reading DMs
    - Replying to messages
    - Commenting on posts
    - Reacting with emojis
    """
    
    def __init__(
        self,
        access_token: str = None,
        instagram_account_id: str = None,
        page_id: str = None
    ):
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = instagram_account_id or os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        if not all([self.access_token, self.instagram_account_id]):
            logger.warning("Instagram credentials not fully configured")
    
    async def get_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent DM conversations"""
        import aiohttp
        
        url = f"{self.base_url}/{self.page_id}/conversations"
        params = {
            "platform": "instagram",
            "access_token": self.access_token,
            "limit": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get conversations: {await response.text()}")
                    return []
    
    async def get_messages(self, conversation_id: str, limit: int = 20) -> List[Dict]:
        """Get messages from a conversation"""
        import aiohttp
        
        url = f"{self.base_url}/{conversation_id}"
        params = {
            "fields": "messages{message,from,created_time,attachments}",
            "access_token": self.access_token,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("messages", {}).get("data", [])
                else:
                    logger.error(f"Failed to get messages: {await response.text()}")
                    return []
    
    async def send_message(
        self,
        recipient_id: str,
        text: str,
        media_url: Optional[str] = None
    ) -> bool:
        """Send a DM to a user"""
        import aiohttp
        
        url = f"{self.base_url}/me/messages"
        
        message_data = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }
        
        if media_url:
            message_data["message"]["attachment"] = {
                "type": "audio",
                "payload": {"url": media_url}
            }
        
        params = {"access_token": self.access_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=message_data, params=params) as response:
                if response.status == 200:
                    logger.info(f"Message sent to {recipient_id}")
                    return True
                else:
                    logger.error(f"Failed to send message: {await response.text()}")
                    return False
    
    async def reply_to_comment(
        self,
        comment_id: str,
        text: str
    ) -> bool:
        """Reply to a comment on a post"""
        import aiohttp
        
        url = f"{self.base_url}/{comment_id}/replies"
        params = {
            "message": text,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    logger.info(f"Replied to comment {comment_id}")
                    return True
                else:
                    logger.error(f"Failed to reply: {await response.text()}")
                    return False
    
    async def get_mentions(self, limit: int = 20) -> List[Dict]:
        """Get posts where Sisi Lola is mentioned"""
        import aiohttp
        
        url = f"{self.base_url}/{self.instagram_account_id}/tags"
        params = {
            "fields": "id,caption,media_url,username,timestamp",
            "access_token": self.access_token,
            "limit": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get mentions: {await response.text()}")
                    return []


class SisiLolaInstagramBot:
    """
    Sisi Lola Instagram Bot
    
    Features:
    - Auto-reply to DMs with personality
    - Respond to comments on posts
    - React to mentions with enthusiasm
    - Send voice notes
    - Maintain conversation context
    """
    
    def __init__(
        self,
        instagram_api: InstagramAPI = None,
        inference_service = None,
        auto_reply: bool = True,
        reply_delay_seconds: int = 5,
        max_daily_messages: int = 100
    ):
        self.instagram = instagram_api or InstagramAPI()
        self.inference_service = inference_service
        self.auto_reply = auto_reply
        self.reply_delay = reply_delay_seconds
        self.max_daily_messages = max_daily_messages
        
        # Tracking
        self.messages_sent_today = 0
        self.last_reset = datetime.now().date()
        self.conversation_contexts: Dict[str, List[Dict]] = {}
        self.processed_messages: set = set()
        
        # Response templates for quick replies
        self.quick_responses = {
            "greetings": [
                "[EN] Hey! [/EN] [NP] How body? Na Sisi Lola be this! [/NP] 💃",
                "[NP] Wetin dey! [/NP] [EN] So glad you reached out! [/EN] 🙌",
                "[YO] Bawo ni! [/YO] [EN] It's your girl Sisi Lola! [/EN] ✨"
            ],
            "thanks": [
                "[EN] Aww, you're so sweet! [/EN] [NP] E dey make my heart full! [/NP] ❤️",
                "[NP] Na you baddest! [/NP] [EN] Thank YOU for the love! [/EN] 💕"
            ],
            "questions": [
                "[EN] Great question! [/EN] [NP] Make I yarn you... [/NP]",
                "[NP] Omo, dis one deep o! [/NP] [EN] Let me share my thoughts... [/EN]"
            ]
        }
    
    async def initialize(self):
        """Initialize the bot with inference service"""
        if self.inference_service is None:
            try:
                from sisi_lola_api.app.services.unified_inference import get_inference_service
                self.inference_service = get_inference_service(
                    load_brain=True,
                    load_voice=True
                )
                logger.info("✅ Inference service loaded")
            except Exception as e:
                logger.warning(f"Failed to load inference service: {e}")
                logger.info("Bot will use fallback responses")
    
    async def generate_reply(
        self,
        message: InstagramMessage,
        context: List[Dict] = None
    ) -> SisiLolaReply:
        """Generate a personalized reply"""
        
        # Reset daily counter
        if datetime.now().date() > self.last_reset:
            self.messages_sent_today = 0
            self.last_reset = datetime.now().date()
        
        # Check rate limit
        if self.messages_sent_today >= self.max_daily_messages:
            logger.warning("Daily message limit reached")
            return SisiLolaReply(
                text="[EN] I've been chatting so much today! [/EN] [NP] Make we continue tomorrow, okay? [/NP] 💤",
                personality_score=1.0
            )
        
        # Detect intent for quick response
        quick_response = self._get_quick_response(message.text)
        
        if self.inference_service:
            try:
                # Use full inference service
                from sisi_lola_api.app.services.unified_inference import ResponseMode, Language
                
                # Detect Scenario
                scenario = "general"
                hustle_keywords = ["advice", "hustle", "relationship", "dating", "job", "work", "japa", "school", "money"]
                if any(w in message.text.lower() for w in hustle_keywords):
                    scenario = "hustle_clinic"
                    logger.info(f"💖 ROUTE: Entering Hustle Clinic for {message.username}")

                response = await self.inference_service.generate(
                    message=message.text,
                    mode=ResponseMode.TEXT_ONLY,
                    language=Language.MIXED,
                    conversation_history=context,
                    max_tokens=350,  # A bit more room for advice
                    temperature=0.8,
                    scenario=scenario
                )
                
                self.messages_sent_today += 1
                
                return SisiLolaReply(
                    text=response.text,
                    personality_score=response.personality_metrics.get("charisma", 0.9),
                    emoji_reaction=self._get_reaction_emoji(message.text)
                )
                
            except Exception as e:
                logger.error(f"Inference error: {e}")
        
        # Fallback to quick response
        self.messages_sent_today += 1
        return SisiLolaReply(
            text=quick_response or "[EN] Thanks for your message! [/EN] [NP] Na gist we go gist! [/NP] 💃",
            personality_score=0.8,
            emoji_reaction=self._get_reaction_emoji(message.text)
        )
    
    def _get_quick_response(self, text: str) -> Optional[str]:
        """Get quick response based on message intent"""
        import random
        
        text_lower = text.lower()
        
        # Greeting detection
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "how are you", "sup", "what's up"]
        if any(g in text_lower for g in greetings):
            return random.choice(self.quick_responses["greetings"])
        
        # Thanks detection
        thanks = ["thank", "thanks", "appreciate", "grateful"]
        if any(t in text_lower for t in thanks):
            return random.choice(self.quick_responses["thanks"])
        
        # Question detection
        if "?" in text:
            return random.choice(self.quick_responses["questions"])
        
        return None
    
    def _get_reaction_emoji(self, text: str) -> str:
        """Get appropriate emoji reaction"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["love", "amazing", "beautiful", "gorgeous"]):
            return "❤️"
        if any(w in text_lower for w in ["funny", "lol", "haha", "🤣"]):
            return "😂"
        if any(w in text_lower for w in ["wow", "incredible", "awesome"]):
            return "😮"
        if any(w in text_lower for w in ["sad", "sorry", "miss"]):
            return "😢"
        if any(w in text_lower for w in ["fire", "hot", "slay"]):
            return "🔥"
        
        return "💃"  # Default Sisi Lola energy
    
    async def process_dm(self, message: InstagramMessage) -> Optional[SisiLolaReply]:
        """Process a DM and optionally auto-reply"""
        
        # Skip if already processed
        if message.message_id in self.processed_messages:
            return None
        
        self.processed_messages.add(message.message_id)
        
        # Get conversation context
        context = self.conversation_contexts.get(message.user_id, [])
        
        # Generate reply
        reply = await self.generate_reply(message, context)
        
        # Update context
        context.append({"role": "user", "content": message.text})
        context.append({"role": "assistant", "content": reply.text})
        self.conversation_contexts[message.user_id] = context[-20:]  # Keep last 20
        
        # Auto-reply if enabled
        if self.auto_reply:
            await asyncio.sleep(self.reply_delay)  # Natural delay
            await self.instagram.send_message(
                recipient_id=message.user_id,
                text=self._clean_for_instagram(reply.text)
            )
            logger.info(f"Auto-replied to {message.username}")
        
        return reply
    
    async def process_comment(
        self,
        comment_id: str,
        username: str,
        text: str
    ) -> Optional[SisiLolaReply]:
        """Process and reply to a comment"""
        
        message = InstagramMessage(
            message_id=comment_id,
            user_id=comment_id,
            username=username,
            text=text,
            message_type=MessageType.COMMENT
        )
        
        reply = await self.generate_reply(message)
        
        if self.auto_reply:
            # Tag user in reply
            tagged_reply = f"@{username} {self._clean_for_instagram(reply.text)}"
            await self.instagram.reply_to_comment(comment_id, tagged_reply)
            logger.info(f"Replied to comment from {username}")
        
        return reply
    
    def _clean_for_instagram(self, text: str) -> str:
        """Clean text for Instagram (remove language tags, limit length)"""
        import re
        
        # Remove language tags
        text = re.sub(r'\[/?(?:EN|NP|YO|IG|HA)\]', '', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Instagram has 1000 char limit for DMs, 2200 for comments
        if len(text) > 900:
            text = text[:897] + "..."
        
        return text
    
    async def run_polling(self, interval_seconds: int = 60):
        """
        Run the bot in polling mode
        
        Checks for new messages every `interval_seconds`
        """
        logger.info("🚀 Starting Sisi Lola Instagram Bot in polling mode...")
        await self.initialize()
        
        while True:
            try:
                # Get conversations
                conversations = await self.instagram.get_conversations(limit=20)
                
                for conv in conversations:
                    conv_id = conv.get("id")
                    if not conv_id:
                        continue
                    
                    # Get messages
                    messages = await self.instagram.get_messages(conv_id, limit=5)
                    
                    for msg in messages:
                        msg_id = msg.get("id")
                        if msg_id in self.processed_messages:
                            continue
                        
                        # Create message object
                        instagram_msg = InstagramMessage(
                            message_id=msg_id,
                            user_id=msg.get("from", {}).get("id", ""),
                            username=msg.get("from", {}).get("name", "friend"),
                            text=msg.get("message", ""),
                            message_type=MessageType.DM
                        )
                        
                        # Process
                        if instagram_msg.text:
                            await self.process_dm(instagram_msg)
                
                logger.info(f"Checked messages. Sent today: {self.messages_sent_today}")
                
            except Exception as e:
                logger.error(f"Polling error: {e}")
            
            await asyncio.sleep(interval_seconds)


# ============================================================================
# WEBHOOK HANDLER FOR REAL-TIME
# ============================================================================

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/instagram", tags=["instagram-bot"])

# Bot instance
_bot: Optional[SisiLolaInstagramBot] = None

def get_bot() -> SisiLolaInstagramBot:
    """Get or create bot instance"""
    global _bot
    if _bot is None:
        _bot = SisiLolaInstagramBot()
    return _bot

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook with Instagram"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    verify_token = os.getenv("INSTAGRAM_VERIFY_TOKEN", "sisi_lola_rocks")
    
    if mode == "subscribe" and token == verify_token:
        logger.info("Webhook verified!")
        return int(challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming Instagram webhooks"""
    try:
        body = await request.json()
        logger.info(f"Webhook received: {json.dumps(body, indent=2)}")
        
        bot = get_bot()
        
        # Process entries
        for entry in body.get("entry", []):
            # Handle messaging
            for messaging in entry.get("messaging", []):
                sender_id = messaging.get("sender", {}).get("id")
                message_data = messaging.get("message", {})
                
                if message_data.get("text"):
                    msg = InstagramMessage(
                        message_id=message_data.get("mid", ""),
                        user_id=sender_id,
                        username="instagram_user",
                        text=message_data.get("text"),
                        message_type=MessageType.DM
                    )
                    
                    # Process asynchronously
                    asyncio.create_task(bot.process_dm(msg))
            
            # Handle comments
            for change in entry.get("changes", []):
                if change.get("field") == "comments":
                    comment = change.get("value", {})
                    await bot.process_comment(
                        comment_id=comment.get("id"),
                        username=comment.get("from", {}).get("username", ""),
                        text=comment.get("text", "")
                    )
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/status")
async def get_bot_status():
    """Get bot status"""
    bot = get_bot()
    return {
        "status": "running",
        "messages_sent_today": bot.messages_sent_today,
        "max_daily_messages": bot.max_daily_messages,
        "auto_reply_enabled": bot.auto_reply,
        "active_conversations": len(bot.conversation_contexts),
        "processed_messages": len(bot.processed_messages)
    }

@router.post("/test-reply")
async def test_reply(message: str):
    """Test the bot's reply generation"""
    bot = get_bot()
    await bot.initialize()
    
    test_msg = InstagramMessage(
        message_id="test_123",
        user_id="test_user",
        username="test_user",
        text=message,
        message_type=MessageType.DM
    )
    
    reply = await bot.generate_reply(test_msg)
    
    return {
        "input": message,
        "reply": reply.text,
        "emoji_reaction": reply.emoji_reaction,
        "personality_score": reply.personality_score
    }
