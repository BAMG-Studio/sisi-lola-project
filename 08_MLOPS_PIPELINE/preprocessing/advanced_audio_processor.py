#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - ADVANCED AUDIO PROCESSOR WITH STFT & VOICE ISOLATION
═══════════════════════════════════════════════════════════════════════════════
Professional audio preprocessing for AI voice training:

- Voice Isolation: Separates clean dialogue from background noise
- STFT Processing: Short-time Fourier Transform for spectral analysis
- Noise Reduction: Advanced denoising using spectral gating
- Audio Enhancement: Quality improvement for training data
- Nigerian Dialect Optimization: Specialized processing for tonal languages

Based on 2026 best practices for multimodal AI training.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("AudioProcessor")


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

NUMPY_AVAILABLE = False
SCIPY_AVAILABLE = False
LIBROSA_AVAILABLE = False
TORCH_AVAILABLE = False
TORCHAUDIO_AVAILABLE = False
NOISEREDUCE_AVAILABLE = False
DEMUCS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    pass

try:
    from scipy import signal
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    pass

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    pass

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    pass

try:
    import torchaudio
    import torchaudio.transforms as T
    TORCHAUDIO_AVAILABLE = True
except ImportError:
    pass

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class AudioQuality(Enum):
    """Audio quality classification."""
    EXCELLENT = "excellent"  # Clean studio quality
    GOOD = "good"           # Minor background noise
    ACCEPTABLE = "acceptable"  # Noticeable noise but usable
    POOR = "poor"           # Heavy noise, needs enhancement
    UNUSABLE = "unusable"   # Cannot be salvaged


@dataclass
class AudioMetrics:
    """Metrics extracted from audio analysis."""
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: int
    rms_energy: float
    peak_amplitude: float
    snr_db: float  # Signal-to-noise ratio
    spectral_centroid_mean: float
    spectral_bandwidth_mean: float
    zero_crossing_rate: float
    silence_ratio: float  # Proportion of silence
    clipping_ratio: float  # Proportion of clipped samples
    quality_rating: AudioQuality
    
    
@dataclass
class ProcessingConfig:
    """Configuration for audio processing."""
    # STFT parameters
    n_fft: int = 2048
    hop_length: int = 512
    win_length: int = 2048
    window: str = "hann"
    
    # Voice isolation
    enable_voice_isolation: bool = True
    isolation_model: str = "demucs"  # or "spectral_gating"
    
    # Noise reduction
    enable_noise_reduction: bool = True
    noise_reduce_strength: float = 0.7  # 0.0 to 1.0
    stationary_noise: bool = True
    
    # Enhancement
    enable_enhancement: bool = True
    target_loudness_lufs: float = -14.0
    normalize: bool = True
    
    # Output
    target_sample_rate: int = 22050  # Standard for TTS
    output_format: str = "wav"
    output_bit_depth: int = 16
    
    # Nigerian language optimizations
    preserve_tones: bool = True  # Important for tonal languages
    tonal_emphasis_db: float = 2.0


@dataclass
class ProcessedAudio:
    """Result of audio processing."""
    input_path: str
    output_path: str
    original_metrics: AudioMetrics
    processed_metrics: AudioMetrics
    processing_steps: List[str]
    stft_features_path: Optional[str] = None
    spectrogram_path: Optional[str] = None
    processing_time_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# STFT PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

class STFTProcessor:
    """
    Short-time Fourier Transform processor for audio analysis.
    
    STFT is more effective than raw waveforms for AI training because:
    - Captures frequency content over time
    - Separates harmonic from noise components
    - Enables spectral manipulation
    - Better represents speech characteristics
    """
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
    
    def compute_stft(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Compute Short-time Fourier Transform.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate
            
        Returns:
            Complex STFT matrix
        """
        if LIBROSA_AVAILABLE:
            stft = librosa.stft(
                audio,
                n_fft=self.config.n_fft,
                hop_length=self.config.hop_length,
                win_length=self.config.win_length,
                window=self.config.window
            )
        elif SCIPY_AVAILABLE:
            _, _, stft = signal.stft(
                audio,
                fs=sr,
                nperseg=self.config.n_fft,
                noverlap=self.config.n_fft - self.config.hop_length,
                window=self.config.window
            )
        else:
            raise RuntimeError("No STFT library available. Install librosa or scipy.")
        
        return stft
    
    def compute_inverse_stft(self, stft_matrix: np.ndarray, length: int = None) -> np.ndarray:
        """
        Reconstruct audio from STFT.
        
        Args:
            stft_matrix: Complex STFT matrix
            length: Expected output length
            
        Returns:
            Reconstructed audio signal
        """
        if LIBROSA_AVAILABLE:
            audio = librosa.istft(
                stft_matrix,
                hop_length=self.config.hop_length,
                win_length=self.config.win_length,
                window=self.config.window,
                length=length
            )
        elif SCIPY_AVAILABLE:
            _, audio = signal.istft(
                stft_matrix,
                nperseg=self.config.n_fft,
                noverlap=self.config.n_fft - self.config.hop_length,
                window=self.config.window
            )
        else:
            raise RuntimeError("No STFT library available")
        
        return audio
    
    def compute_magnitude_phase(self, stft_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Separate magnitude and phase from complex STFT."""
        magnitude = np.abs(stft_matrix)
        phase = np.angle(stft_matrix)
        return magnitude, phase
    
    def magnitude_phase_to_stft(self, magnitude: np.ndarray, phase: np.ndarray) -> np.ndarray:
        """Reconstruct complex STFT from magnitude and phase."""
        return magnitude * np.exp(1j * phase)
    
    def compute_mel_spectrogram(self, audio: np.ndarray, sr: int, 
                                 n_mels: int = 80) -> np.ndarray:
        """
        Compute Mel spectrogram for TTS training.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            n_mels: Number of Mel bands
            
        Returns:
            Mel spectrogram in dB scale
        """
        if not LIBROSA_AVAILABLE:
            raise RuntimeError("librosa required for Mel spectrogram")
        
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=sr,
            n_fft=self.config.n_fft,
            hop_length=self.config.hop_length,
            win_length=self.config.win_length,
            n_mels=n_mels
        )
        
        # Convert to dB scale
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        return mel_spec_db
    
    def extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """
        Extract comprehensive spectral features for training.
        
        Returns dictionary with:
        - stft: Complex STFT
        - magnitude: Magnitude spectrogram
        - mel_spec: Mel spectrogram
        - mfcc: MFCCs
        - spectral_centroid: Spectral centroid over time
        - spectral_bandwidth: Spectral bandwidth over time
        """
        features = {}
        
        if LIBROSA_AVAILABLE:
            # STFT
            stft = self.compute_stft(audio, sr)
            features['stft'] = stft
            features['magnitude'] = np.abs(stft)
            
            # Mel spectrogram
            features['mel_spec'] = self.compute_mel_spectrogram(audio, sr)
            
            # MFCCs
            features['mfcc'] = librosa.feature.mfcc(
                y=audio, sr=sr, n_mfcc=13,
                hop_length=self.config.hop_length
            )
            
            # Spectral features
            features['spectral_centroid'] = librosa.feature.spectral_centroid(
                y=audio, sr=sr, hop_length=self.config.hop_length
            )[0]
            
            features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
                y=audio, sr=sr, hop_length=self.config.hop_length
            )[0]
            
            # Zero crossing rate
            features['zcr'] = librosa.feature.zero_crossing_rate(
                audio, hop_length=self.config.hop_length
            )[0]
        
        return features
    
    def save_features(self, features: Dict[str, np.ndarray], output_path: Path):
        """Save extracted features to disk."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as numpy compressed archive
        np.savez_compressed(
            output_path,
            **{k: v for k, v in features.items() if isinstance(v, np.ndarray)}
        )
        
        logger.info(f"Saved features to {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE ISOLATION
# ═══════════════════════════════════════════════════════════════════════════════

class VoiceIsolator:
    """
    Isolates voice from background noise and music.
    
    Methods:
    1. Spectral Gating: Fast, lightweight, good for mild noise
    2. Demucs: Deep learning based, best for complex backgrounds
    3. Adobe/DaVinci Neural Engine (via CLI if available)
    """
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.stft_processor = STFTProcessor(config)
    
    def isolate_voice_spectral(self, audio: np.ndarray, sr: int, 
                               noise_sample: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Isolate voice using spectral gating.
        
        Args:
            audio: Input audio
            sr: Sample rate
            noise_sample: Optional noise-only sample for profiling
            
        Returns:
            Voice-isolated audio
        """
        if not NUMPY_AVAILABLE:
            return audio
        
        # Compute STFT
        stft = self.stft_processor.compute_stft(audio, sr)
        magnitude, phase = self.stft_processor.compute_magnitude_phase(stft)
        
        # Estimate noise floor
        if noise_sample is not None:
            noise_stft = self.stft_processor.compute_stft(noise_sample, sr)
            noise_magnitude = np.mean(np.abs(noise_stft), axis=1, keepdims=True)
        else:
            # Use first 0.5 seconds as noise reference
            noise_frames = int(0.5 * sr / self.config.hop_length)
            noise_magnitude = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Spectral gating
        gain_factor = 2.0  # Amplify voice above noise threshold
        threshold = noise_magnitude * gain_factor
        
        # Soft gating to preserve voice quality
        mask = np.clip((magnitude - threshold) / threshold, 0, 1)
        
        # Apply mask
        processed_magnitude = magnitude * mask
        
        # Reconstruct
        processed_stft = self.stft_processor.magnitude_phase_to_stft(
            processed_magnitude, phase
        )
        
        return self.stft_processor.compute_inverse_stft(processed_stft, len(audio))
    
    def isolate_voice_noisereduce(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Use noisereduce library for voice isolation.
        """
        if not NOISEREDUCE_AVAILABLE:
            logger.warning("noisereduce not available, falling back to spectral")
            return self.isolate_voice_spectral(audio, sr)
        
        # Reduce stationary noise
        reduced = nr.reduce_noise(
            y=audio,
            sr=sr,
            stationary=self.config.stationary_noise,
            prop_decrease=self.config.noise_reduce_strength
        )
        
        return reduced
    
    def isolate_voice_demucs(self, audio_path: Path, output_path: Path) -> Path:
        """
        Use Demucs (Facebook's source separation) for voice isolation.
        
        Demucs provides state-of-the-art voice/music separation.
        """
        try:
            # Check if demucs is available
            result = subprocess.run(
                ["python", "-m", "demucs", "--help"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError("Demucs not available")
            
            # Run demucs separation
            output_dir = output_path.parent / "demucs_output"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "python", "-m", "demucs",
                "--two-stems", "vocals",
                "-o", str(output_dir),
                str(audio_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Find vocals output
            vocals_path = list(output_dir.glob("*/vocals.wav"))
            if vocals_path:
                return vocals_path[0]
            
        except Exception as e:
            logger.warning(f"Demucs failed: {e}, falling back to noisereduce")
        
        # Fallback
        return audio_path
    
    def isolate_voice(self, audio: np.ndarray, sr: int, 
                      method: str = "auto") -> np.ndarray:
        """
        Main voice isolation method.
        
        Args:
            audio: Input audio
            sr: Sample rate
            method: "spectral", "noisereduce", "demucs", or "auto"
            
        Returns:
            Voice-isolated audio
        """
        if method == "auto":
            if NOISEREDUCE_AVAILABLE:
                method = "noisereduce"
            else:
                method = "spectral"
        
        if method == "noisereduce":
            return self.isolate_voice_noisereduce(audio, sr)
        elif method == "spectral":
            return self.isolate_voice_spectral(audio, sr)
        else:
            return audio


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO QUALITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class AudioQualityAnalyzer:
    """
    Analyzes audio quality for training data curation.
    
    Measures:
    - Signal-to-noise ratio
    - Clipping detection
    - Silence ratio
    - Spectral quality
    """
    
    def __init__(self):
        pass
    
    def analyze(self, audio: np.ndarray, sr: int) -> AudioMetrics:
        """
        Comprehensive audio quality analysis.
        """
        # Basic metrics
        duration = len(audio) / sr
        channels = 1 if audio.ndim == 1 else audio.shape[0]
        bit_depth = 16  # Assume 16-bit
        
        # Energy metrics
        rms = np.sqrt(np.mean(audio ** 2))
        peak = np.max(np.abs(audio))
        
        # SNR estimation (simplified)
        noise_floor = np.percentile(np.abs(audio), 10)
        snr = 20 * np.log10(rms / (noise_floor + 1e-10))
        
        # Spectral metrics
        if LIBROSA_AVAILABLE:
            spectral_centroid = np.mean(
                librosa.feature.spectral_centroid(y=audio, sr=sr)
            )
            spectral_bandwidth = np.mean(
                librosa.feature.spectral_bandwidth(y=audio, sr=sr)
            )
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio))
        else:
            spectral_centroid = 0
            spectral_bandwidth = 0
            zcr = 0
        
        # Silence ratio
        silence_threshold = 0.01
        silence_ratio = np.sum(np.abs(audio) < silence_threshold) / len(audio)
        
        # Clipping ratio
        clipping_threshold = 0.99
        clipping_ratio = np.sum(np.abs(audio) > clipping_threshold) / len(audio)
        
        # Quality rating
        quality = self._rate_quality(snr, silence_ratio, clipping_ratio)
        
        return AudioMetrics(
            duration_seconds=duration,
            sample_rate=sr,
            channels=channels,
            bit_depth=bit_depth,
            rms_energy=float(rms),
            peak_amplitude=float(peak),
            snr_db=float(snr),
            spectral_centroid_mean=float(spectral_centroid),
            spectral_bandwidth_mean=float(spectral_bandwidth),
            zero_crossing_rate=float(zcr),
            silence_ratio=float(silence_ratio),
            clipping_ratio=float(clipping_ratio),
            quality_rating=quality
        )
    
    def _rate_quality(self, snr: float, silence_ratio: float, 
                      clipping_ratio: float) -> AudioQuality:
        """Rate overall audio quality."""
        score = 100
        
        # SNR scoring
        if snr >= 30:
            score -= 0
        elif snr >= 20:
            score -= 10
        elif snr >= 15:
            score -= 25
        elif snr >= 10:
            score -= 40
        else:
            score -= 60
        
        # Silence penalty
        if silence_ratio > 0.5:
            score -= 30
        elif silence_ratio > 0.3:
            score -= 15
        
        # Clipping penalty
        if clipping_ratio > 0.1:
            score -= 50
        elif clipping_ratio > 0.01:
            score -= 20
        
        if score >= 80:
            return AudioQuality.EXCELLENT
        elif score >= 60:
            return AudioQuality.GOOD
        elif score >= 40:
            return AudioQuality.ACCEPTABLE
        elif score >= 20:
            return AudioQuality.POOR
        else:
            return AudioQuality.UNUSABLE


# ═══════════════════════════════════════════════════════════════════════════════
# NIGERIAN DIALECT OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

class NigerianDialectOptimizer:
    """
    Specialized audio processing for Nigerian tonal languages.
    
    Yoruba, Igbo, and Hausa are tonal languages where pitch
    variations carry semantic meaning. This optimizer:
    - Preserves tonal information
    - Enhances pitch clarity
    - Maintains natural prosody
    """
    
    # Fundamental frequency ranges for Nigerian languages
    F0_RANGES = {
        "yo": (100, 400),  # Yoruba - 3 tones (high, mid, low)
        "ig": (100, 350),  # Igbo - 2 tones (high, low) + downstep
        "ha": (100, 300),  # Hausa - 2 tones (high, low)
        "pcm": (80, 350),  # Pidgin - varied, English-influenced
    }
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
    
    def enhance_tones(self, audio: np.ndarray, sr: int, 
                      language: str = "yo") -> np.ndarray:
        """
        Enhance tonal clarity for Nigerian languages.
        
        Args:
            audio: Input audio
            sr: Sample rate
            language: Language code (yo, ig, ha, pcm)
            
        Returns:
            Tone-enhanced audio
        """
        if not LIBROSA_AVAILABLE:
            return audio
        
        f0_min, f0_max = self.F0_RANGES.get(language, (100, 400))
        
        # Extract harmonic and percussive components
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Enhance harmonic (tonal) component slightly
        emphasis_linear = 10 ** (self.config.tonal_emphasis_db / 20)
        enhanced_harmonic = harmonic * emphasis_linear
        
        # Recombine
        enhanced = enhanced_harmonic + percussive
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val * 0.95
        
        return enhanced
    
    def extract_pitch_contour(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Extract pitch contour for tone analysis."""
        if not LIBROSA_AVAILABLE:
            return np.array([])
        
        # Use pyin for robust pitch tracking
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=80,
            fmax=500,
            sr=sr
        )
        
        return f0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AUDIO PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

class AdvancedAudioProcessor:
    """
    Complete audio processing pipeline for Sisi Lola training data.
    
    Pipeline:
    1. Load and analyze input audio
    2. Voice isolation (remove background)
    3. Noise reduction
    4. Nigerian dialect optimization
    5. STFT feature extraction
    6. Quality validation
    7. Export processed audio and features
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Initialize components
        self.stft_processor = STFTProcessor(self.config)
        self.voice_isolator = VoiceIsolator(self.config)
        self.quality_analyzer = AudioQualityAnalyzer()
        self.dialect_optimizer = NigerianDialectOptimizer(self.config)
        
        # Track processing stats
        self.stats = {
            "processed": 0,
            "failed": 0,
            "by_quality": {}
        }
    
    def load_audio(self, audio_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio file and return waveform + sample rate."""
        if LIBROSA_AVAILABLE:
            audio, sr = librosa.load(audio_path, sr=None, mono=True)
        elif TORCHAUDIO_AVAILABLE:
            waveform, sr = torchaudio.load(str(audio_path))
            audio = waveform.numpy().mean(axis=0)  # Mono
        elif SCIPY_AVAILABLE:
            sr, audio = wavfile.read(audio_path)
            audio = audio.astype(np.float32) / 32768.0
        else:
            raise RuntimeError("No audio loading library available")
        
        return audio, sr
    
    def save_audio(self, audio: np.ndarray, sr: int, output_path: Path):
        """Save processed audio to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95
        
        if SCIPY_AVAILABLE:
            audio_int16 = (audio * 32767).astype(np.int16)
            wavfile.write(output_path, sr, audio_int16)
        elif TORCHAUDIO_AVAILABLE:
            tensor = torch.from_numpy(audio).unsqueeze(0)
            torchaudio.save(str(output_path), tensor, sr)
        else:
            raise RuntimeError("No audio saving library available")
        
        logger.info(f"Saved audio to {output_path}")
    
    def resample(self, audio: np.ndarray, sr_orig: int, sr_target: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        if sr_orig == sr_target:
            return audio
        
        if LIBROSA_AVAILABLE:
            return librosa.resample(audio, orig_sr=sr_orig, target_sr=sr_target)
        elif TORCHAUDIO_AVAILABLE:
            tensor = torch.from_numpy(audio).unsqueeze(0)
            resampler = T.Resample(sr_orig, sr_target)
            return resampler(tensor).numpy().squeeze()
        else:
            logger.warning("No resampling library available")
            return audio
    
    def normalize_loudness(self, audio: np.ndarray, sr: int, 
                           target_lufs: float = -14.0) -> np.ndarray:
        """Normalize audio to target loudness (LUFS)."""
        try:
            import pyloudnorm as pyln
            
            meter = pyln.Meter(sr)
            current_lufs = meter.integrated_loudness(audio)
            
            if np.isinf(current_lufs):
                return audio
            
            gain_db = target_lufs - current_lufs
            gain_linear = 10 ** (gain_db / 20)
            
            normalized = audio * gain_linear
            
            # Prevent clipping
            max_val = np.max(np.abs(normalized))
            if max_val > 1.0:
                normalized = normalized / max_val * 0.95
            
            return normalized
            
        except ImportError:
            # Simple peak normalization fallback
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                return audio / max_val * 0.95
            return audio
    
    def process(self, input_path: Path, output_path: Path,
                language: str = "en",
                extract_features: bool = True) -> ProcessedAudio:
        """
        Full audio processing pipeline.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for processed output
            language: Language code for dialect optimization
            extract_features: Whether to extract STFT features
            
        Returns:
            ProcessedAudio result object
        """
        start_time = datetime.now()
        processing_steps = []
        
        try:
            # 1. Load audio
            logger.info(f"Processing: {input_path.name}")
            audio, sr = self.load_audio(input_path)
            processing_steps.append("loaded")
            
            # 2. Analyze original quality
            original_metrics = self.quality_analyzer.analyze(audio, sr)
            logger.info(f"  Original quality: {original_metrics.quality_rating.value}")
            
            # 3. Voice isolation
            if self.config.enable_voice_isolation:
                audio = self.voice_isolator.isolate_voice(audio, sr)
                processing_steps.append("voice_isolated")
            
            # 4. Noise reduction
            if self.config.enable_noise_reduction:
                audio = self.voice_isolator.isolate_voice_noisereduce(audio, sr)
                processing_steps.append("noise_reduced")
            
            # 5. Nigerian dialect optimization
            if language in ["yo", "ig", "ha", "pcm"] and self.config.preserve_tones:
                audio = self.dialect_optimizer.enhance_tones(audio, sr, language)
                processing_steps.append(f"tone_enhanced_{language}")
            
            # 6. Resample to target
            if sr != self.config.target_sample_rate:
                audio = self.resample(audio, sr, self.config.target_sample_rate)
                sr = self.config.target_sample_rate
                processing_steps.append("resampled")
            
            # 7. Loudness normalization
            if self.config.enable_enhancement:
                audio = self.normalize_loudness(
                    audio, sr, self.config.target_loudness_lufs
                )
                processing_steps.append("normalized")
            
            # 8. Analyze processed quality
            processed_metrics = self.quality_analyzer.analyze(audio, sr)
            logger.info(f"  Processed quality: {processed_metrics.quality_rating.value}")
            
            # 9. Save processed audio
            self.save_audio(audio, sr, output_path)
            processing_steps.append("saved")
            
            # 10. Extract and save STFT features
            features_path = None
            if extract_features:
                features = self.stft_processor.extract_spectral_features(audio, sr)
                features_path = output_path.with_suffix('.npz')
                self.stft_processor.save_features(features, features_path)
                processing_steps.append("features_extracted")
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update stats
            self.stats["processed"] += 1
            quality = processed_metrics.quality_rating.value
            self.stats["by_quality"][quality] = self.stats["by_quality"].get(quality, 0) + 1
            
            return ProcessedAudio(
                input_path=str(input_path),
                output_path=str(output_path),
                original_metrics=original_metrics,
                processed_metrics=processed_metrics,
                processing_steps=processing_steps,
                stft_features_path=str(features_path) if features_path else None,
                processing_time_seconds=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.stats["failed"] += 1
            
            return ProcessedAudio(
                input_path=str(input_path),
                output_path=str(output_path),
                original_metrics=AudioMetrics(
                    duration_seconds=0, sample_rate=0, channels=0, bit_depth=0,
                    rms_energy=0, peak_amplitude=0, snr_db=0,
                    spectral_centroid_mean=0, spectral_bandwidth_mean=0,
                    zero_crossing_rate=0, silence_ratio=0, clipping_ratio=0,
                    quality_rating=AudioQuality.UNUSABLE
                ),
                processed_metrics=AudioMetrics(
                    duration_seconds=0, sample_rate=0, channels=0, bit_depth=0,
                    rms_energy=0, peak_amplitude=0, snr_db=0,
                    spectral_centroid_mean=0, spectral_bandwidth_mean=0,
                    zero_crossing_rate=0, silence_ratio=0, clipping_ratio=0,
                    quality_rating=AudioQuality.UNUSABLE
                ),
                processing_steps=processing_steps,
                processing_time_seconds=0,
                success=False,
                error_message=str(e)
            )
    
    def process_batch(self, input_dir: Path, output_dir: Path,
                      language: str = "en",
                      file_pattern: str = "*.wav") -> List[ProcessedAudio]:
        """Process all audio files in a directory."""
        results = []
        audio_files = list(input_dir.glob(file_pattern))
        
        logger.info(f"Processing {len(audio_files)} files from {input_dir}")
        
        for audio_file in audio_files:
            output_path = output_dir / audio_file.name
            result = self.process(audio_file, output_path, language)
            results.append(result)
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Audio Processor")
    parser.add_argument("input", type=Path, help="Input audio file or directory")
    parser.add_argument("--output", type=Path, help="Output path")
    parser.add_argument("--language", type=str, default="en",
                        choices=["en", "yo", "ha", "ig", "pcm"],
                        help="Language code for dialect optimization")
    parser.add_argument("--no-isolation", action="store_true",
                        help="Disable voice isolation")
    parser.add_argument("--no-features", action="store_true",
                        help="Don't extract STFT features")
    parser.add_argument("--sample-rate", type=int, default=22050,
                        help="Target sample rate")
    
    args = parser.parse_args()
    
    config = ProcessingConfig(
        enable_voice_isolation=not args.no_isolation,
        target_sample_rate=args.sample_rate
    )
    
    processor = AdvancedAudioProcessor(config)
    
    if args.input.is_file():
        output = args.output or args.input.with_stem(args.input.stem + "_processed")
        result = processor.process(
            args.input, output, 
            language=args.language,
            extract_features=not args.no_features
        )
        
        if result.success:
            print(f"\n✓ Processed: {result.output_path}")
            print(f"  Quality: {result.processed_metrics.quality_rating.value}")
            print(f"  SNR: {result.processed_metrics.snr_db:.1f} dB")
            print(f"  Time: {result.processing_time_seconds:.2f}s")
        else:
            print(f"\n✗ Failed: {result.error_message}")
    
    elif args.input.is_dir():
        output_dir = args.output or args.input / "processed"
        results = processor.process_batch(
            args.input, output_dir,
            language=args.language
        )
        
        print(f"\nProcessed: {len([r for r in results if r.success])}")
        print(f"Failed: {len([r for r in results if not r.success])}")


if __name__ == "__main__":
    main()
