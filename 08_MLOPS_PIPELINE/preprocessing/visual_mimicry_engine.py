#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - VISUAL & CONTEXTUAL MIMICRY ENGINE
═══════════════════════════════════════════════════════════════════════════════
Multimodal extraction for visual and behavioral modeling.

Features:
- Azure AI Video Indexer integration
- Emotion and facial movement extraction
- Visual context analysis
- Hook/gesture detection (OpusClip style)
- Behavioral pattern recognition
- Nigerian presenter style analysis

This enables Sisi Lola to replicate the physical pacing and visual
cues of Nigerian content creators.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import tempfile
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import re
import time

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("VisualMimicry")


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

CV2_AVAILABLE = False
PIL_AVAILABLE = False
NUMPY_AVAILABLE = False
TORCH_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    pass

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    pass

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    pass

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class EmotionType(Enum):
    """Detected emotional states."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CONTEMPT = "contempt"


class GestureType(Enum):
    """Types of gestures detected."""
    HAND_WAVE = "hand_wave"
    POINTING = "pointing"
    THUMBS_UP = "thumbs_up"
    OPEN_PALM = "open_palm"
    COUNTING = "counting"
    EMPHASIS = "emphasis"
    HEAD_NOD = "head_nod"
    HEAD_SHAKE = "head_shake"
    SHRUG = "shrug"
    HANDS_TOGETHER = "hands_together"
    UNKNOWN = "unknown"


class HookType(Enum):
    """Types of engagement hooks."""
    QUESTION = "question"
    STATEMENT = "statement"
    DRAMATIC_PAUSE = "dramatic_pause"
    VISUAL_CHANGE = "visual_change"
    TONE_SHIFT = "tone_shift"
    GESTURE_HOOK = "gesture_hook"
    DIRECT_ADDRESS = "direct_address"
    STORY_OPENING = "story_opening"


@dataclass
class FaceDetection:
    """Detected face with attributes."""
    frame_number: int
    timestamp: float
    bounding_box: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    emotion: EmotionType = EmotionType.NEUTRAL
    emotion_confidence: float = 0.0
    age_estimate: Optional[int] = None
    is_speaking: bool = False
    eye_contact: bool = False  # Looking at camera
    face_angle: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # yaw, pitch, roll


@dataclass
class GestureDetection:
    """Detected gesture."""
    frame_number: int
    timestamp: float
    gesture_type: GestureType
    confidence: float
    duration_seconds: float = 0.0
    hand: str = "unknown"  # left, right, both
    intensity: float = 0.5  # 0.0 to 1.0


@dataclass
class VisualHook:
    """Engagement hook detected in video."""
    timestamp: float
    duration: float
    hook_type: HookType
    description: str
    engagement_score: float  # Estimated engagement potential (0-1)
    transcript_snippet: Optional[str] = None
    visual_elements: List[str] = field(default_factory=list)


@dataclass
class SpeakerStyle:
    """Analyzed speaker presentation style."""
    speaking_pace: float  # Words per minute
    gesture_frequency: float  # Gestures per minute
    emotion_variance: float  # How much emotion changes
    eye_contact_ratio: float  # Ratio of frames with eye contact
    dominant_emotions: List[Tuple[EmotionType, float]]
    common_gestures: List[Tuple[GestureType, float]]
    hook_patterns: List[str]
    cultural_markers: List[str]  # Nigerian-specific patterns
    energy_level: str  # "low", "medium", "high"


@dataclass
class VideoAnalysis:
    """Complete video analysis result."""
    video_id: str
    video_path: str
    duration_seconds: float
    frame_count: int
    fps: float
    resolution: Tuple[int, int]
    
    # Detections
    face_detections: List[FaceDetection] = field(default_factory=list)
    gesture_detections: List[GestureDetection] = field(default_factory=list)
    visual_hooks: List[VisualHook] = field(default_factory=list)
    
    # Aggregated analysis
    speaker_style: Optional[SpeakerStyle] = None
    scene_changes: List[float] = field(default_factory=list)  # Timestamps
    
    # Processing info
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_time_seconds: float = 0.0
    
    def to_training_data(self) -> Dict[str, Any]:
        """Convert to training-ready format."""
        return {
            "video_id": self.video_id,
            "duration": self.duration_seconds,
            "style": asdict(self.speaker_style) if self.speaker_style else None,
            "hooks": [asdict(h) for h in self.visual_hooks],
            "emotion_timeline": [
                {"t": f.timestamp, "emotion": f.emotion.value, "conf": f.emotion_confidence}
                for f in self.face_detections if f.emotion_confidence > 0.5
            ],
            "gesture_timeline": [
                {"t": g.timestamp, "gesture": g.gesture_type.value, "conf": g.confidence}
                for g in self.gesture_detections if g.confidence > 0.5
            ]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AZURE VIDEO INDEXER INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class AzureVideoIndexer:
    """
    Integration with Azure AI Video Indexer for comprehensive video analysis.
    
    Extracts:
    - Face detection and identification
    - Emotion recognition
    - Object and scene detection
    - OCR (text on screen)
    - Audio transcription
    - Topic extraction
    - Brand/logo detection
    """
    
    def __init__(self, account_id: str = None, api_key: str = None, 
                 location: str = "trial"):
        """
        Initialize Azure Video Indexer client.
        
        Args:
            account_id: Azure Video Indexer account ID
            api_key: API key for authentication
            location: Account location (e.g., "trial", "eastus")
        """
        self.account_id = account_id or os.getenv("AZURE_VI_ACCOUNT_ID")
        self.api_key = api_key or os.getenv("AZURE_VI_API_KEY")
        self.location = location
        self.access_token = None
        self.token_expiry = None
        
        self.base_url = f"https://api.videoindexer.ai/{location}/Accounts/{self.account_id}"
    
    def _get_access_token(self) -> str:
        """Get or refresh access token."""
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry:
                return self.access_token
        
        try:
            import httpx
            
            url = f"https://api.videoindexer.ai/Auth/{self.location}/Accounts/{self.account_id}/AccessToken"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            
            response = httpx.get(url, headers=headers, params={"allowEdit": "true"})
            response.raise_for_status()
            
            self.access_token = response.text.strip('"')
            self.token_expiry = datetime.now() + timedelta(hours=1)
            
            return self.access_token
            
        except Exception as e:
            logger.error(f"Failed to get Azure access token: {e}")
            return None
    
    def upload_video(self, video_path: Path, name: str = None,
                     language: str = "auto") -> Optional[str]:
        """
        Upload video for indexing.
        
        Args:
            video_path: Local path to video
            name: Display name for video
            language: Language code or "auto" for detection
            
        Returns:
            Video ID if successful
        """
        token = self._get_access_token()
        if not token:
            return None
        
        try:
            import httpx
            
            name = name or video_path.stem
            url = f"{self.base_url}/Videos"
            
            params = {
                "accessToken": token,
                "name": name,
                "language": language,
                "privacy": "Private"
            }
            
            with open(video_path, "rb") as f:
                files = {"file": (video_path.name, f, "video/mp4")}
                response = httpx.post(url, params=params, files=files, timeout=300)
            
            response.raise_for_status()
            result = response.json()
            
            video_id = result.get("id")
            logger.info(f"Uploaded video: {video_id}")
            
            return video_id
            
        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            return None
    
    def get_video_index(self, video_id: str, 
                        wait_for_completion: bool = True) -> Optional[Dict]:
        """
        Get indexed video insights.
        
        Args:
            video_id: Azure Video Indexer video ID
            wait_for_completion: Wait for indexing to complete
            
        Returns:
            Video insights dictionary
        """
        token = self._get_access_token()
        if not token:
            return None
        
        try:
            import httpx
            
            url = f"{self.base_url}/Videos/{video_id}/Index"
            params = {"accessToken": token}
            
            while True:
                response = httpx.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                
                state = result.get("state")
                
                if state == "Processed":
                    return result
                elif state == "Failed":
                    logger.error("Video indexing failed")
                    return None
                elif wait_for_completion:
                    logger.info(f"Indexing in progress: {result.get('progress', 0)}%")
                    time.sleep(30)
                else:
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to get video index: {e}")
            return None
    
    def parse_insights(self, insights: Dict) -> VideoAnalysis:
        """Parse Azure insights into our data structures."""
        videos = insights.get("videos", [{}])
        video_data = videos[0] if videos else {}
        video_insights = video_data.get("insights", {})
        
        # Basic info
        duration = video_data.get("durationInSeconds", 0)
        
        # Extract face detections with emotions
        face_detections = []
        for face in video_insights.get("faces", []):
            for instance in face.get("instances", []):
                start = self._parse_time(instance.get("start", "0:00:00"))
                
                # Get thumbnail frame
                thumbnail_id = face.get("thumbnailId", "")
                
                # Find emotions for this face
                emotion = EmotionType.NEUTRAL
                emotion_conf = 0.0
                
                for sent in video_insights.get("sentiments", []):
                    for sent_instance in sent.get("instances", []):
                        sent_start = self._parse_time(sent_instance.get("start", "0:00:00"))
                        if abs(sent_start - start) < 1.0:
                            emotion = self._map_sentiment(sent.get("sentimentKey", ""))
                            emotion_conf = sent.get("averageScore", 0)
                            break
                
                face_detections.append(FaceDetection(
                    frame_number=int(start * 30),  # Assume 30fps
                    timestamp=start,
                    bounding_box=(0, 0, 0, 0),  # Not available in basic API
                    confidence=face.get("confidence", 0.8),
                    emotion=emotion,
                    emotion_confidence=emotion_conf,
                    is_speaking=bool(face.get("seenDuration", 0) > 0)
                ))
        
        # Extract visual hooks from topics and labels
        hooks = []
        
        # Topics as potential hooks
        for topic in video_insights.get("topics", []):
            for instance in topic.get("instances", []):
                start = self._parse_time(instance.get("start", "0:00:00"))
                end = self._parse_time(instance.get("end", "0:00:00"))
                
                hooks.append(VisualHook(
                    timestamp=start,
                    duration=end - start,
                    hook_type=HookType.STATEMENT,
                    description=topic.get("name", ""),
                    engagement_score=topic.get("confidence", 0.5)
                ))
        
        # Keywords as engagement points
        for keyword in video_insights.get("keywords", []):
            for instance in keyword.get("instances", []):
                start = self._parse_time(instance.get("start", "0:00:00"))
                
                hooks.append(VisualHook(
                    timestamp=start,
                    duration=1.0,
                    hook_type=HookType.STATEMENT,
                    description=f"Keyword: {keyword.get('text', '')}",
                    engagement_score=keyword.get("confidence", 0.5)
                ))
        
        return VideoAnalysis(
            video_id=video_data.get("id", ""),
            video_path="",
            duration_seconds=duration,
            frame_count=int(duration * 30),
            fps=30.0,
            resolution=(0, 0),
            face_detections=face_detections,
            visual_hooks=hooks
        )
    
    def _parse_time(self, time_str: str) -> float:
        """Parse time string to seconds."""
        try:
            parts = time_str.split(":")
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + float(s)
            else:
                return float(time_str)
        except:
            return 0.0
    
    def _map_sentiment(self, sentiment_key: str) -> EmotionType:
        """Map Azure sentiment to emotion type."""
        mapping = {
            "Positive": EmotionType.HAPPY,
            "Negative": EmotionType.SAD,
            "Neutral": EmotionType.NEUTRAL
        }
        return mapping.get(sentiment_key, EmotionType.NEUTRAL)


# ═══════════════════════════════════════════════════════════════════════════════
# LOCAL VIDEO ANALYZER (OpenCV-based)
# ═══════════════════════════════════════════════════════════════════════════════

class LocalVideoAnalyzer:
    """
    Local video analysis using OpenCV and optional deep learning models.
    
    Works without cloud APIs for basic analysis:
    - Face detection
    - Scene change detection
    - Motion analysis
    - Frame extraction
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("data/video_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load face detector
        self.face_cascade = None
        if CV2_AVAILABLE:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    def analyze_video(self, video_path: Path, 
                      sample_rate: int = 1,
                      extract_frames: bool = False) -> VideoAnalysis:
        """
        Analyze video file locally.
        
        Args:
            video_path: Path to video file
            sample_rate: Analyze every Nth frame
            extract_frames: Save key frames to disk
            
        Returns:
            VideoAnalysis object
        """
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV not available. Install with: pip install opencv-python")
        
        start_time = datetime.now()
        
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        video_id = hashlib.md5(str(video_path).encode()).hexdigest()[:12]
        
        face_detections = []
        scene_changes = []
        prev_frame_gray = None
        
        frame_number = 0
        
        logger.info(f"Analyzing video: {video_path.name} ({frame_count} frames)")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample every Nth frame
            if frame_number % sample_rate != 0:
                frame_number += 1
                continue
            
            timestamp = frame_number / fps
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    face_detections.append(FaceDetection(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        bounding_box=(x, y, w, h),
                        confidence=0.8
                    ))
            
            # Scene change detection
            if prev_frame_gray is not None:
                diff = cv2.absdiff(prev_frame_gray, gray)
                mean_diff = np.mean(diff)
                
                # Threshold for scene change
                if mean_diff > 30:
                    scene_changes.append(timestamp)
            
            prev_frame_gray = gray.copy()
            
            # Save key frames
            if extract_frames and frame_number % (sample_rate * 10) == 0:
                frame_path = self.output_dir / f"{video_id}_frame_{frame_number:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
            
            frame_number += 1
        
        cap.release()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        analysis = VideoAnalysis(
            video_id=video_id,
            video_path=str(video_path),
            duration_seconds=duration,
            frame_count=frame_count,
            fps=fps,
            resolution=(width, height),
            face_detections=face_detections,
            scene_changes=scene_changes,
            processing_time_seconds=processing_time
        )
        
        # Compute speaker style
        analysis.speaker_style = self._compute_speaker_style(analysis)
        
        logger.info(f"✓ Analyzed {frame_count} frames in {processing_time:.1f}s")
        
        return analysis
    
    def _compute_speaker_style(self, analysis: VideoAnalysis) -> SpeakerStyle:
        """Compute aggregated speaker style metrics."""
        
        # Emotion distribution
        emotion_counts = {}
        for face in analysis.face_detections:
            emotion = face.emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total_faces = len(analysis.face_detections)
        dominant_emotions = [
            (EmotionType(e), c / total_faces)
            for e, c in sorted(emotion_counts.items(), key=lambda x: -x[1])[:3]
        ] if total_faces > 0 else []
        
        # Eye contact ratio (would need more sophisticated detection)
        eye_contact_ratio = 0.7  # Placeholder
        
        # Gesture frequency (placeholder - would need pose estimation)
        gesture_frequency = 5.0  # Gestures per minute
        
        # Energy level based on scene changes
        scene_change_rate = len(analysis.scene_changes) / max(analysis.duration_seconds / 60, 1)
        if scene_change_rate > 10:
            energy = "high"
        elif scene_change_rate > 5:
            energy = "medium"
        else:
            energy = "low"
        
        return SpeakerStyle(
            speaking_pace=150.0,  # Would need transcript analysis
            gesture_frequency=gesture_frequency,
            emotion_variance=len(set(e.value for e in emotion_counts.keys())) / 7.0,
            eye_contact_ratio=eye_contact_ratio,
            dominant_emotions=dominant_emotions,
            common_gestures=[],
            hook_patterns=[],
            cultural_markers=[],
            energy_level=energy
        )
    
    def extract_key_frames(self, video_path: Path, 
                           num_frames: int = 10) -> List[Path]:
        """Extract evenly-spaced key frames from video."""
        if not CV2_AVAILABLE:
            return []
        
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            cap.release()
            return []
        
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        video_id = hashlib.md5(str(video_path).encode()).hexdigest()[:12]
        output_dir = self.output_dir / video_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                frame_path = output_dir / f"keyframe_{idx:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                saved_paths.append(frame_path)
        
        cap.release()
        return saved_paths


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK & GESTURE DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class HookDetector:
    """
    Detect engagement hooks in video content.
    
    Inspired by OpusClip and similar tools, identifies:
    - Opening hooks (first 3-5 seconds)
    - Transition points
    - Emotional peaks
    - Visual emphasis moments
    - Direct audience engagement
    """
    
    # Nigerian/African cultural engagement patterns
    NIGERIAN_HOOK_PATTERNS = [
        # Greetings
        r"how far",
        r"how body",
        r"how you dey",
        r"my people",
        r"una don hear",
        
        # Engagement phrases
        r"you understand",
        r"you get",
        r"shey you see",
        r"wahala dey",
        r"the thing is",
        
        # Story openers
        r"let me tell you",
        r"make i tell you",
        r"see what happen",
        r"see this one",
        
        # Questions
        r"abi no be so",
        r"you sabi",
        r"na true",
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.NIGERIAN_HOOK_PATTERNS]
    
    def detect_hooks_in_transcript(self, transcript: str, 
                                    segments: List[Dict]) -> List[VisualHook]:
        """
        Detect hooks from transcript and timing.
        
        Args:
            transcript: Full transcript text
            segments: List of {start, end, text} dicts
            
        Returns:
            List of detected hooks
        """
        hooks = []
        
        for segment in segments:
            text = segment.get("text", "")
            start = segment.get("start", 0)
            end = segment.get("end", start + 1)
            
            # Check for Nigerian patterns
            for pattern in self.patterns:
                if pattern.search(text):
                    hooks.append(VisualHook(
                        timestamp=start,
                        duration=end - start,
                        hook_type=HookType.DIRECT_ADDRESS,
                        description=f"Nigerian engagement: '{text[:50]}'",
                        engagement_score=0.8,
                        transcript_snippet=text
                    ))
                    break
            
            # Check for questions
            if "?" in text:
                hooks.append(VisualHook(
                    timestamp=start,
                    duration=end - start,
                    hook_type=HookType.QUESTION,
                    description=f"Question: '{text[:50]}'",
                    engagement_score=0.7,
                    transcript_snippet=text
                ))
            
            # Check for story openers
            if any(opener in text.lower() for opener in 
                   ["let me tell", "i remember", "one day", "so there was"]):
                hooks.append(VisualHook(
                    timestamp=start,
                    duration=end - start,
                    hook_type=HookType.STORY_OPENING,
                    description=f"Story opener: '{text[:50]}'",
                    engagement_score=0.75,
                    transcript_snippet=text
                ))
        
        return hooks
    
    def detect_visual_hooks(self, analysis: VideoAnalysis) -> List[VisualHook]:
        """Detect hooks from visual analysis."""
        hooks = []
        
        # Scene changes as potential hooks
        for i, change_time in enumerate(analysis.scene_changes[:10]):  # First 10
            hooks.append(VisualHook(
                timestamp=change_time,
                duration=1.0,
                hook_type=HookType.VISUAL_CHANGE,
                description=f"Scene change #{i+1}",
                engagement_score=0.6,
                visual_elements=["scene_transition"]
            ))
        
        # Opening hook (first few seconds)
        if analysis.duration_seconds > 5:
            # Find most expressive face in first 5 seconds
            early_faces = [f for f in analysis.face_detections 
                          if f.timestamp < 5.0]
            
            if early_faces:
                # Sort by emotion confidence
                best_face = max(early_faces, key=lambda f: f.emotion_confidence)
                
                hooks.append(VisualHook(
                    timestamp=0,
                    duration=5.0,
                    hook_type=HookType.DIRECT_ADDRESS,
                    description=f"Opening hook - {best_face.emotion.value} expression",
                    engagement_score=0.9,
                    visual_elements=["opening_expression", best_face.emotion.value]
                ))
        
        return hooks


# ═══════════════════════════════════════════════════════════════════════════════
# NIGERIAN PRESENTER STYLE ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class NigerianStyleAnalyzer:
    """
    Analyzes Nigerian/African presenter styles for mimicry.
    
    Identifies:
    - Speech patterns and pacing
    - Gesture vocabulary
    - Emotional expression range
    - Cultural engagement techniques
    - Visual presentation norms
    """
    
    # Nigerian presenter archetypes
    PRESENTER_ARCHETYPES = {
        "storyteller": {
            "energy": "medium",
            "gesture_frequency": "high",
            "emotion_range": "wide",
            "pacing": "varied",
            "hooks": ["story_opening", "dramatic_pause"]
        },
        "educator": {
            "energy": "medium",
            "gesture_frequency": "medium",
            "emotion_range": "moderate",
            "pacing": "steady",
            "hooks": ["question", "direct_address"]
        },
        "entertainer": {
            "energy": "high",
            "gesture_frequency": "very_high",
            "emotion_range": "wide",
            "pacing": "fast",
            "hooks": ["visual_change", "tone_shift"]
        },
        "professional": {
            "energy": "low",
            "gesture_frequency": "low",
            "emotion_range": "narrow",
            "pacing": "steady",
            "hooks": ["statement"]
        }
    }
    
    def analyze_style(self, video_analysis: VideoAnalysis) -> Dict[str, Any]:
        """Analyze presenter style from video analysis."""
        style = video_analysis.speaker_style
        
        if not style:
            return {"archetype": "unknown", "confidence": 0}
        
        # Match to archetype
        scores = {}
        
        for archetype, traits in self.PRESENTER_ARCHETYPES.items():
            score = 0
            
            # Energy match
            if traits["energy"] == style.energy_level:
                score += 25
            
            # Gesture frequency match
            if style.gesture_frequency > 8 and traits["gesture_frequency"] == "very_high":
                score += 25
            elif 4 <= style.gesture_frequency <= 8 and traits["gesture_frequency"] == "high":
                score += 25
            elif 2 <= style.gesture_frequency < 4 and traits["gesture_frequency"] == "medium":
                score += 25
            elif style.gesture_frequency < 2 and traits["gesture_frequency"] == "low":
                score += 25
            
            # Emotion range match
            if style.emotion_variance > 0.5 and traits["emotion_range"] == "wide":
                score += 25
            elif 0.3 <= style.emotion_variance <= 0.5 and traits["emotion_range"] == "moderate":
                score += 25
            elif style.emotion_variance < 0.3 and traits["emotion_range"] == "narrow":
                score += 25
            
            scores[archetype] = score
        
        best_archetype = max(scores, key=scores.get)
        
        return {
            "archetype": best_archetype,
            "confidence": scores[best_archetype] / 100,
            "traits": self.PRESENTER_ARCHETYPES[best_archetype],
            "raw_metrics": {
                "energy_level": style.energy_level,
                "gesture_frequency": style.gesture_frequency,
                "emotion_variance": style.emotion_variance,
                "eye_contact_ratio": style.eye_contact_ratio
            }
        }
    
    def generate_mimicry_profile(self, analyses: List[VideoAnalysis]) -> Dict[str, Any]:
        """
        Generate a mimicry profile from multiple video analyses.
        
        This profile can be used to guide avatar behavior generation.
        """
        if not analyses:
            return {}
        
        # Aggregate metrics
        all_emotions = []
        all_gestures = []
        gesture_frequencies = []
        energy_levels = []
        
        for analysis in analyses:
            if analysis.speaker_style:
                gesture_frequencies.append(analysis.speaker_style.gesture_frequency)
                energy_levels.append(analysis.speaker_style.energy_level)
                all_emotions.extend([e[0] for e in analysis.speaker_style.dominant_emotions])
                all_gestures.extend([g[0] for g in analysis.speaker_style.common_gestures])
        
        # Compute aggregated profile
        avg_gesture_freq = sum(gesture_frequencies) / len(gesture_frequencies) if gesture_frequencies else 0
        
        # Most common energy level
        energy_counts = {}
        for e in energy_levels:
            energy_counts[e] = energy_counts.get(e, 0) + 1
        dominant_energy = max(energy_counts, key=energy_counts.get) if energy_counts else "medium"
        
        # Emotion distribution
        emotion_counts = {}
        for e in all_emotions:
            emotion_counts[e.value] = emotion_counts.get(e.value, 0) + 1
        
        return {
            "sample_size": len(analyses),
            "average_gesture_frequency": avg_gesture_freq,
            "dominant_energy": dominant_energy,
            "emotion_distribution": emotion_counts,
            "recommended_pacing": "varied" if avg_gesture_freq > 5 else "steady",
            "engagement_style": "high_energy" if dominant_energy == "high" else "conversational"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN VISUAL MIMICRY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class VisualMimicryEngine:
    """
    Main engine for visual and contextual mimicry.
    
    Coordinates:
    - Video analysis (local or cloud)
    - Hook detection
    - Style analysis
    - Profile generation
    """
    
    def __init__(self, use_azure: bool = False, output_dir: Path = None):
        self.output_dir = output_dir or Path("data/visual_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.local_analyzer = LocalVideoAnalyzer(self.output_dir)
        self.azure_indexer = AzureVideoIndexer() if use_azure else None
        self.hook_detector = HookDetector()
        self.style_analyzer = NigerianStyleAnalyzer()
    
    def analyze_video(self, video_path: Path, 
                      use_cloud: bool = False,
                      transcript: str = None,
                      segments: List[Dict] = None) -> VideoAnalysis:
        """
        Complete video analysis pipeline.
        
        Args:
            video_path: Path to video file
            use_cloud: Use Azure Video Indexer if available
            transcript: Optional transcript for hook detection
            segments: Optional transcript segments with timing
            
        Returns:
            Complete VideoAnalysis
        """
        logger.info(f"Analyzing: {video_path.name}")
        
        # Primary analysis
        if use_cloud and self.azure_indexer:
            video_id = self.azure_indexer.upload_video(video_path)
            if video_id:
                insights = self.azure_indexer.get_video_index(video_id)
                if insights:
                    analysis = self.azure_indexer.parse_insights(insights)
                    analysis.video_path = str(video_path)
        else:
            analysis = self.local_analyzer.analyze_video(video_path)
        
        # Detect hooks
        if transcript and segments:
            transcript_hooks = self.hook_detector.detect_hooks_in_transcript(
                transcript, segments
            )
            analysis.visual_hooks.extend(transcript_hooks)
        
        visual_hooks = self.hook_detector.detect_visual_hooks(analysis)
        analysis.visual_hooks.extend(visual_hooks)
        
        # Compute style
        style_info = self.style_analyzer.analyze_style(analysis)
        
        # Save analysis
        output_path = self.output_dir / f"{analysis.video_id}_analysis.json"
        with open(output_path, "w") as f:
            json.dump(analysis.to_training_data(), f, indent=2, default=str)
        
        logger.info(f"✓ Analysis saved: {output_path}")
        
        return analysis
    
    def analyze_batch(self, video_dir: Path, 
                      pattern: str = "*.mp4") -> List[VideoAnalysis]:
        """Analyze all videos in a directory."""
        video_files = list(video_dir.glob(pattern))
        
        logger.info(f"Analyzing {len(video_files)} videos...")
        
        analyses = []
        for video_path in video_files:
            try:
                analysis = self.analyze_video(video_path)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {video_path}: {e}")
        
        # Generate aggregate mimicry profile
        if analyses:
            profile = self.style_analyzer.generate_mimicry_profile(analyses)
            profile_path = self.output_dir / "mimicry_profile.json"
            with open(profile_path, "w") as f:
                json.dump(profile, f, indent=2)
            logger.info(f"Generated mimicry profile: {profile_path}")
        
        return analyses


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Visual Mimicry Engine")
    parser.add_argument("input", type=Path, help="Video file or directory")
    parser.add_argument("--output", type=Path, help="Output directory")
    parser.add_argument("--azure", action="store_true", help="Use Azure Video Indexer")
    parser.add_argument("--extract-frames", action="store_true", help="Save key frames")
    parser.add_argument("--sample-rate", type=int, default=5, help="Frame sample rate")
    
    args = parser.parse_args()
    
    engine = VisualMimicryEngine(use_azure=args.azure, output_dir=args.output)
    
    if args.input.is_file():
        analysis = engine.analyze_video(args.input)
        
        print("\n" + "═" * 60)
        print("VIDEO ANALYSIS COMPLETE")
        print("═" * 60)
        print(f"Duration: {analysis.duration_seconds:.1f}s")
        print(f"Faces detected: {len(analysis.face_detections)}")
        print(f"Scene changes: {len(analysis.scene_changes)}")
        print(f"Hooks found: {len(analysis.visual_hooks)}")
        
        if analysis.speaker_style:
            print(f"\nSpeaker Style:")
            print(f"  Energy: {analysis.speaker_style.energy_level}")
            print(f"  Gesture freq: {analysis.speaker_style.gesture_frequency:.1f}/min")
    
    elif args.input.is_dir():
        analyses = engine.analyze_batch(args.input)
        print(f"\nAnalyzed {len(analyses)} videos")


if __name__ == "__main__":
    main()
