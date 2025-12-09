"""
SISI LOLA PROMPT INTENT CLASSIFIER
===================================
Intelligently classifies user prompts into:
1. GENERATIVE - Create content (videos, reels, podcasts, ads)
2. TECHNICAL - Code, configuration, system questions
3. CONVERSATIONAL - Chat, gossip, discussion, Q&A

This allows Sisi Lola to respond appropriately and route
to the correct processing pipeline.
"""

import re
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Literal
from datetime import datetime


class IntentCategory(Enum):
    """Primary intent categories"""
    GENERATIVE = "generative"  # Create content
    TECHNICAL = "technical"    # Technical/system questions
    CONVERSATIONAL = "conversational"  # Discussion/chat


class GenerativeSubtype(Enum):
    """Subtypes for generative content"""
    # Short form (< 3 minutes)
    REEL = "reel"              # 15-60 seconds
    SNIPPET = "snippet"        # Quick clip
    AD = "ad"                  # Advertisement
    CAPTION = "caption"        # Text caption only
    THUMBNAIL = "thumbnail"    # Image generation
    
    # Long form (> 3 minutes)
    EPISODE = "episode"        # Full show episode
    PODCAST = "podcast"        # Podcast episode
    LIVE_SESSION = "live"      # Live stream content
    DOCUMENTARY = "documentary" # Educational/documentary
    INTERVIEW = "interview"    # Interview format


class ContentDuration(Enum):
    """Duration classification"""
    MICRO = "micro"      # < 30 seconds
    SHORT = "short"      # 30 sec - 3 minutes
    MEDIUM = "medium"    # 3 - 15 minutes
    LONG = "long"        # 15 - 45 minutes
    EXTENDED = "extended" # 45 - 120 minutes


@dataclass
class ClassifiedIntent:
    """Result of intent classification"""
    # Primary classification
    category: IntentCategory
    confidence: float  # 0.0 to 1.0
    
    # For generative intents
    generative_subtype: Optional[GenerativeSubtype] = None
    duration: Optional[ContentDuration] = None
    
    # Extracted parameters
    topic: Optional[str] = None
    style: Optional[str] = None
    platform: Optional[str] = None  # Target platform
    
    # Context
    requires_content_input: bool = False  # Needs URL/file processing
    content_urls: List[str] = field(default_factory=list)
    file_paths: List[str] = field(default_factory=list)
    
    # Raw analysis
    keywords_matched: List[str] = field(default_factory=list)
    reasoning: Optional[str] = None


class PromptIntentClassifier:
    """
    Classifies prompts to determine how Sisi Lola should respond.
    
    Usage:
        classifier = PromptIntentClassifier()
        
        # Generative prompt
        result = classifier.classify("Create a 60-second reel about Lagos tech")
        # -> IntentCategory.GENERATIVE, GenerativeSubtype.REEL
        
        # Conversational prompt
        result = classifier.classify("What do you think about this video?")
        # -> IntentCategory.CONVERSATIONAL
        
        # Technical prompt
        result = classifier.classify("How do I configure the API?")
        # -> IntentCategory.TECHNICAL
    """
    
    # Keyword patterns for classification
    GENERATIVE_KEYWORDS = {
        # Creation verbs
        'create', 'generate', 'make', 'produce', 'build', 'design',
        'write', 'compose', 'draft', 'craft', 'develop',
        
        # Content types
        'reel', 'reels', 'video', 'videos', 'content', 'post',
        'podcast', 'episode', 'show', 'ad', 'advertisement',
        'caption', 'captions', 'snippet', 'clip', 'trailer',
        'thumbnail', 'cover', 'image', 'graphic',
        'script', 'scripts', 'screenplay', 'outline',
        'live', 'livestream', 'broadcast', 'stream',
        
        # Duration hints
        'short', 'quick', 'brief', 'long', 'full', 'extended',
        'seconds', 'minutes', 'hour',
        
        # Platform mentions
        'instagram', 'tiktok', 'youtube', 'facebook', 'twitter',
        'linkedin', 'reddit',
    }
    
    TECHNICAL_KEYWORDS = {
        # Technical terms
        'api', 'code', 'config', 'configuration', 'setup', 'install',
        'error', 'bug', 'fix', 'debug', 'troubleshoot',
        'deploy', 'server', 'database', 'function', 'class',
        'import', 'export', 'integrate', 'connect',
        
        # Questions about system
        'how to', 'how do i', 'configure', 'setting', 'settings',
        'command', 'terminal', 'run', 'execute',
        'file', 'folder', 'directory', 'path',
        'python', 'javascript', 'docker', 'git',
    }
    
    CONVERSATIONAL_KEYWORDS = {
        # Discussion starters
        'what do you think', 'tell me about', 'explain', 'discuss',
        'why', 'how come', 'what about', 'opinion',
        
        # Gossip/casual
        'gossip', 'gist', 'yarn', 'chat', 'talk', 'story',
        'heard', 'see', 'know', 'believe',
        
        # Reactions
        'interesting', 'amazing', 'wow', 'funny', 'crazy',
        'love', 'hate', 'like', 'feel',
        
        # Questions
        'who', 'what', 'where', 'when', 'why', 'which',
        
        # Nigerian pidgin
        'wetin', 'shey', 'abeg', 'oya', 'wahala', 'gist', 'yarn',
    }
    
    # Content type detection patterns
    DURATION_PATTERNS = {
        ContentDuration.MICRO: [
            r'(\d+)\s*sec(ond)?s?',
            r'quick\s+(clip|snippet|video)',
            r'15\s*(-|to)\s*30',
        ],
        ContentDuration.SHORT: [
            r'(30|45|60)\s*sec',
            r'(1|2|3)\s*min',
            r'reel',
            r'short\s+(video|clip|form)',
            r'tiktok',
        ],
        ContentDuration.MEDIUM: [
            r'(5|10|15)\s*min',
            r'(5|10|15)\s*minute',
            r'youtube\s+short',
        ],
        ContentDuration.LONG: [
            r'(20|25|30|35|40|45)\s*min',
            r'full\s+episode',
            r'podcast',
            r'episode',
        ],
        ContentDuration.EXTENDED: [
            r'(60|90|120)\s*min',
            r'(1|2)\s*hour',
            r'live\s+(session|stream|show)',
            r'full\s+show',
            r'extended',
        ],
    }
    
    SUBTYPE_PATTERNS = {
        GenerativeSubtype.REEL: [r'reel', r'instagram.*video', r'tiktok'],
        GenerativeSubtype.SNIPPET: [r'snippet', r'clip', r'quick\s+video'],
        GenerativeSubtype.AD: [r'ad\b', r'advertisement', r'promo', r'commercial'],
        GenerativeSubtype.CAPTION: [r'caption', r'text\s+only', r'write.*for'],
        GenerativeSubtype.THUMBNAIL: [r'thumbnail', r'cover\s+image', r'poster'],
        GenerativeSubtype.EPISODE: [r'episode', r'full\s+video', r'youtube\s+video'],
        GenerativeSubtype.PODCAST: [r'podcast', r'audio\s+show', r'talk\s+show'],
        GenerativeSubtype.LIVE_SESSION: [r'live', r'livestream', r'broadcast'],
        GenerativeSubtype.DOCUMENTARY: [r'documentary', r'educational', r'explainer'],
        GenerativeSubtype.INTERVIEW: [r'interview', r'conversation\s+with', r'sit\s+down'],
    }
    
    # URL patterns
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+'
    )
    
    # File path patterns
    FILE_PATTERN = re.compile(
        r'(?:[A-Za-z]:[/\\]|[/\\]|\.\.?[/\\])[^\s<>"{}|\\^`\[\]:*?]+'
    )
    
    def __init__(self, use_llm: bool = False, llm_client=None):
        """
        Initialize the classifier.
        
        Args:
            use_llm: If True, use LLM for enhanced classification
            llm_client: Optional LLM client for enhanced classification
        """
        self.use_llm = use_llm
        self.llm_client = llm_client
    
    def classify(self, prompt: str) -> ClassifiedIntent:
        """
        Classify a user prompt.
        
        Args:
            prompt: The user's input text
            
        Returns:
            ClassifiedIntent with all classification details
        """
        prompt_lower = prompt.lower()
        
        # Extract URLs and file paths
        urls = self.URL_PATTERN.findall(prompt)
        files = self.FILE_PATTERN.findall(prompt)
        
        # Calculate keyword matches
        gen_score, gen_keywords = self._score_keywords(prompt_lower, self.GENERATIVE_KEYWORDS)
        tech_score, tech_keywords = self._score_keywords(prompt_lower, self.TECHNICAL_KEYWORDS)
        conv_score, conv_keywords = self._score_keywords(prompt_lower, self.CONVERSATIONAL_KEYWORDS)
        
        # Boost scores based on context
        if urls or files:
            conv_score += 0.2  # Content likely triggers discussion
        
        # Determine primary category
        scores = {
            IntentCategory.GENERATIVE: gen_score,
            IntentCategory.TECHNICAL: tech_score,
            IntentCategory.CONVERSATIONAL: conv_score,
        }
        
        # If all scores are low, default to conversational
        if max(scores.values()) < 0.1:
            category = IntentCategory.CONVERSATIONAL
            confidence = 0.5
        else:
            category = max(scores, key=scores.get)
            total = sum(scores.values()) or 1
            confidence = scores[category] / total
        
        # Build result
        result = ClassifiedIntent(
            category=category,
            confidence=min(confidence, 0.99),
            requires_content_input=bool(urls or files),
            content_urls=urls,
            file_paths=files,
            keywords_matched=gen_keywords + tech_keywords + conv_keywords,
        )
        
        # Extract details for generative prompts
        if category == IntentCategory.GENERATIVE:
            result.generative_subtype = self._detect_subtype(prompt_lower)
            result.duration = self._detect_duration(prompt_lower)
            result.topic = self._extract_topic(prompt)
            result.platform = self._detect_platform(prompt_lower)
            result.style = self._detect_style(prompt_lower)
        
        # Generate reasoning
        result.reasoning = self._generate_reasoning(result, scores)
        
        return result
    
    def _score_keywords(self, text: str, keywords: set) -> Tuple[float, List[str]]:
        """Score text based on keyword matches"""
        matched = []
        for keyword in keywords:
            if keyword in text:
                matched.append(keyword)
        
        # Score is based on number of matches, normalized
        score = min(len(matched) / 5, 1.0)
        return score, matched
    
    def _detect_subtype(self, text: str) -> Optional[GenerativeSubtype]:
        """Detect the generative content subtype"""
        for subtype, patterns in self.SUBTYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return subtype
        return GenerativeSubtype.REEL  # Default to reel
    
    def _detect_duration(self, text: str) -> ContentDuration:
        """Detect the intended content duration"""
        for duration, patterns in self.DURATION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return duration
        return ContentDuration.SHORT  # Default to short
    
    def _detect_platform(self, text: str) -> Optional[str]:
        """Detect target platform"""
        platforms = {
            'instagram': ['instagram', 'ig', 'insta'],
            'tiktok': ['tiktok', 'tik tok'],
            'youtube': ['youtube', 'yt'],
            'facebook': ['facebook', 'fb'],
            'twitter': ['twitter', 'x.com'],
            'linkedin': ['linkedin'],
        }
        
        for platform, keywords in platforms.items():
            for keyword in keywords:
                if keyword in text:
                    return platform
        return None
    
    def _detect_style(self, text: str) -> Optional[str]:
        """Detect content style hints"""
        styles = {
            'casual': ['casual', 'relaxed', 'chill', 'fun'],
            'professional': ['professional', 'formal', 'business'],
            'educational': ['educational', 'informative', 'explain', 'teach'],
            'entertaining': ['entertaining', 'funny', 'comedy', 'humor'],
            'dramatic': ['dramatic', 'serious', 'intense'],
            'trendy': ['trendy', 'viral', 'trending', 'popular'],
        }
        
        for style, keywords in styles.items():
            for keyword in keywords:
                if keyword in text:
                    return style
        return 'casual'  # Default
    
    def _extract_topic(self, text: str) -> Optional[str]:
        """Extract the main topic from the prompt"""
        # Remove common prefixes
        topic = text
        prefixes = [
            r'^create\s+(a\s+)?',
            r'^make\s+(a\s+)?',
            r'^generate\s+(a\s+)?',
            r'^i\s+want\s+(a\s+)?',
            r'^can\s+you\s+(create\s+)?(a\s+)?',
        ]
        
        for prefix in prefixes:
            topic = re.sub(prefix, '', topic, flags=re.IGNORECASE)
        
        # Remove duration/format mentions
        topic = re.sub(r'\d+\s*(sec|min|hour|second|minute)s?', '', topic)
        topic = re.sub(r'(reel|video|podcast|episode|ad|clip)\s*(about|on)?', '', topic, flags=re.IGNORECASE)
        topic = re.sub(r'for\s+(instagram|tiktok|youtube|facebook)', '', topic, flags=re.IGNORECASE)
        
        topic = topic.strip()
        
        # Limit length
        if len(topic) > 100:
            topic = topic[:100] + "..."
        
        return topic if topic else None
    
    def _generate_reasoning(self, result: ClassifiedIntent, scores: Dict) -> str:
        """Generate human-readable reasoning"""
        parts = []
        
        parts.append(f"Classified as {result.category.value.upper()} "
                    f"(confidence: {result.confidence:.0%})")
        
        if result.keywords_matched:
            parts.append(f"Keywords: {', '.join(result.keywords_matched[:5])}")
        
        if result.category == IntentCategory.GENERATIVE:
            if result.generative_subtype:
                parts.append(f"Content type: {result.generative_subtype.value}")
            if result.duration:
                parts.append(f"Duration: {result.duration.value}")
            if result.platform:
                parts.append(f"Target: {result.platform}")
        
        if result.content_urls:
            parts.append(f"Contains {len(result.content_urls)} URL(s)")
        
        return " | ".join(parts)


class IntentRouter:
    """
    Routes classified intents to appropriate handlers.
    
    Usage:
        router = IntentRouter()
        router.register_handler(IntentCategory.GENERATIVE, generative_handler)
        router.register_handler(IntentCategory.CONVERSATIONAL, chat_handler)
        
        response = router.route(classified_intent, prompt, context)
    """
    
    def __init__(self):
        self.handlers: Dict[IntentCategory, callable] = {}
        self.default_handler = None
    
    def register_handler(self, category: IntentCategory, handler: callable):
        """Register a handler for an intent category"""
        self.handlers[category] = handler
    
    def set_default_handler(self, handler: callable):
        """Set the default handler for unregistered categories"""
        self.default_handler = handler
    
    def route(self, intent: ClassifiedIntent, prompt: str, context: Dict = None) -> any:
        """
        Route the intent to the appropriate handler.
        
        Args:
            intent: The classified intent
            prompt: The original prompt
            context: Additional context (conversation history, etc.)
            
        Returns:
            Handler response
        """
        handler = self.handlers.get(intent.category, self.default_handler)
        
        if handler is None:
            raise ValueError(f"No handler registered for {intent.category}")
        
        return handler(intent, prompt, context or {})


# Quick classification function
def classify_prompt(prompt: str) -> ClassifiedIntent:
    """Quick function to classify a prompt"""
    classifier = PromptIntentClassifier()
    return classifier.classify(prompt)


if __name__ == "__main__":
    # Demo
    classifier = PromptIntentClassifier()
    
    test_prompts = [
        "Create a 60-second reel about Lagos tech startups",
        "Can you make a full podcast episode about Nigerian music?",
        "What do you think about this video? https://youtube.com/watch?v=123",
        "How do I configure the API settings?",
        "Gist me about the latest Nollywood drama!",
        "Generate an Instagram ad for our new product",
        "I want a 2-hour live session discussing Afrobeats",
        "Write a caption for my post about African fashion",
    ]
    
    print("=" * 70)
    print("SISI LOLA INTENT CLASSIFIER DEMO")
    print("=" * 70)
    
    for prompt in test_prompts:
        print(f"\nPrompt: \"{prompt[:50]}...\"" if len(prompt) > 50 else f"\nPrompt: \"{prompt}\"")
        result = classifier.classify(prompt)
        print(f"  → {result.reasoning}")
        if result.topic:
            print(f"  → Topic: {result.topic}")
