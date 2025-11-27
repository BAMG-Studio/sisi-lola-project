"""
Voice Training Data Preparation for Sisi Lola

This script prepares audio recordings for XTTS v2 fine-tuning.

Tasks:
1. Convert audio files to required format (22050Hz, mono, WAV)
2. Segment long recordings into shorter clips (10-30 seconds)
3. Generate metadata.csv with transcriptions
4. Validate audio quality (no clipping, clear speech)
5. Organize data for training

Usage:
    python prepare_training_data.py --input_dir "04_AUDIO_CORE/01_Voice_Samples" --output_dir "voice_training_data"
"""
import os
import sys
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import librosa
    import soundfile as sf
    import numpy as np
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install librosa soundfile numpy")
    sys.exit(1)


class VoiceDataPreparer:
    """Prepare voice recordings for XTTS v2 training"""
    
    TARGET_SR = 22050  # Sample rate for XTTS
    MIN_DURATION = 3.0  # Minimum clip duration (seconds)
    MAX_DURATION = 30.0  # Maximum clip duration (seconds)
    MIN_RMS = 0.01  # Minimum RMS energy (filter silence)
    MAX_RMS = 0.95  # Maximum RMS energy (filter clipping)
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.wavs_dir = self.output_dir / "wavs"
        self.metadata_file = self.output_dir / "metadata.csv"
        
        # Create directories
        self.wavs_dir.mkdir(parents=True, exist_ok=True)
        
        self.clips: List[Dict] = []
    
    def process_all_files(self) -> None:
        """Process all audio files in input directory"""
        audio_files = list(self.input_dir.glob("*.wav")) + \
                     list(self.input_dir.glob("*.mp3")) + \
                     list(self.input_dir.glob("*.m4a"))
        
        if not audio_files:
            print(f"⚠️  No audio files found in {self.input_dir}")
            return
        
        print(f"📂 Found {len(audio_files)} audio files\n")
        
        for audio_file in audio_files:
            print(f"Processing: {audio_file.name}")
            self.process_file(audio_file)
        
        print(f"\n✅ Processed {len(self.clips)} clips")
        self.save_metadata()
    
    def process_file(self, audio_path: Path) -> None:
        """Process a single audio file"""
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.TARGET_SR, mono=True)
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Segment into clips
            clips = self._segment_audio(audio, sr, audio_path.stem)
            
            # Save each clip
            for clip_data in clips:
                self._save_clip(clip_data)
            
        except Exception as e:
            print(f"  ❌ Error processing {audio_path.name}: {e}")
    
    def _segment_audio(
        self,
        audio: np.ndarray,
        sr: int,
        base_name: str
    ) -> List[Dict]:
        """
        Segment audio into training clips.
        
        Strategy:
        1. Detect speech/silence using energy
        2. Split on silence boundaries
        3. Ensure clips are within min/max duration
        """
        # Detect non-silent intervals
        intervals = librosa.effects.split(
            audio,
            top_db=30,  # Silence threshold
            frame_length=2048,
            hop_length=512
        )
        
        clips = []
        clip_idx = 0
        
        for start_frame, end_frame in intervals:
            start_sec = start_frame / sr
            end_sec = end_frame / sr
            duration = end_sec - start_sec
            
            # Skip clips that are too short or too long
            if duration < self.MIN_DURATION:
                continue
            if duration > self.MAX_DURATION:
                # Further segment long clips
                clips.extend(self._split_long_clip(
                    audio[start_frame:end_frame],
                    sr,
                    base_name,
                    clip_idx
                ))
                clip_idx += len(clips)
                continue
            
            # Extract clip
            clip_audio = audio[start_frame:end_frame]
            
            # Quality check
            if not self._quality_check(clip_audio):
                continue
            
            clip_data = {
                'audio': clip_audio,
                'filename': f"{base_name}_{clip_idx:04d}.wav",
                'duration': duration,
                'text': self._get_transcript(base_name),  # Load from script files
                'speaker_id': 'sisi_lola',
                'language': self._detect_language(base_name)
            }
            
            clips.append(clip_data)
            clip_idx += 1
        
        return clips
    
    def _split_long_clip(
        self,
        audio: np.ndarray,
        sr: int,
        base_name: str,
        start_idx: int
    ) -> List[Dict]:
        """Split a long clip into smaller segments"""
        clips = []
        duration = len(audio) / sr
        
        # Calculate number of segments
        num_segments = int(np.ceil(duration / self.MAX_DURATION))
        segment_length = len(audio) // num_segments
        
        for i in range(num_segments):
            start = i * segment_length
            end = min((i + 1) * segment_length, len(audio))
            
            segment = audio[start:end]
            segment_duration = len(segment) / sr
            
            if segment_duration < self.MIN_DURATION:
                continue
            
            clip_data = {
                'audio': segment,
                'filename': f"{base_name}_{start_idx + i:04d}.wav",
                'duration': segment_duration,
                'text': self._get_transcript(base_name),
                'speaker_id': 'sisi_lola',
                'language': self._detect_language(base_name)
            }
            clips.append(clip_data)
        
        return clips
    
    def _quality_check(self, audio: np.ndarray) -> bool:
        """Check audio quality (no clipping, sufficient energy)"""
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio**2))
        
        # Check for clipping
        if np.max(np.abs(audio)) > 0.99:
            return False
        
        # Check energy levels
        if rms < self.MIN_RMS or rms > self.MAX_RMS:
            return False
        
        return True
    
    def _get_transcript(self, base_name: str) -> str:
        """
        Get transcript from corresponding script file.
        
        Looks for SCRIPT_{base_name}.txt in the input directory.
        """
        # Try to find matching script file
        script_file = self.input_dir / f"SCRIPT_{base_name}.txt"
        
        if script_file.exists():
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract script section
                if '## SCRIPT:' in content:
                    script = content.split('## SCRIPT:')[1].split('---')[0]
                    return script.strip()
        
        # Fallback to filename
        return base_name.replace('_', ' ').title()
    
    def _detect_language(self, base_name: str) -> str:
        """Detect language from filename"""
        base_lower = base_name.lower()
        
        if 'pidgin' in base_lower:
            return 'pcm'  # Nigerian Pidgin
        elif 'yoruba' in base_lower:
            return 'yo'
        elif 'italian' in base_lower:
            return 'it'
        elif 'swahili' in base_lower:
            return 'sw'
        elif 'hausa' in base_lower:
            return 'ha'
        elif 'igbo' in base_lower:
            return 'ig'
        else:
            return 'en'  # Default to English
    
    def _save_clip(self, clip_data: Dict) -> None:
        """Save audio clip to disk"""
        output_path = self.wavs_dir / clip_data['filename']
        
        # Save audio
        sf.write(output_path, clip_data['audio'], self.TARGET_SR)
        
        # Add to metadata
        self.clips.append({
            'filename': clip_data['filename'],
            'text': clip_data['text'],
            'speaker_id': clip_data['speaker_id'],
            'language': clip_data['language'],
            'duration': clip_data['duration']
        })
        
        print(f"  ✓ Saved: {clip_data['filename']} ({clip_data['duration']:.1f}s)")
    
    def save_metadata(self) -> None:
        """Save metadata.csv for XTTS training"""
        with open(self.metadata_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            
            # Write header
            writer.writerow(['filename', 'text', 'speaker_id', 'language'])
            
            # Write data
            for clip in self.clips:
                writer.writerow([
                    clip['filename'],
                    clip['text'],
                    clip['speaker_id'],
                    clip['language']
                ])
        
        print(f"\n✅ Metadata saved to: {self.metadata_file}")
        
        # Print statistics
        self._print_statistics()
    
    def _print_statistics(self) -> None:
        """Print dataset statistics"""
        total_duration = sum(clip['duration'] for clip in self.clips)
        
        # Count by language
        lang_counts = {}
        for clip in self.clips:
            lang = clip['language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        print("\n📊 Dataset Statistics:")
        print(f"   Total clips: {len(self.clips)}")
        print(f"   Total duration: {total_duration / 60:.1f} minutes")
        print(f"   Average clip length: {total_duration / len(self.clips):.1f} seconds")
        print(f"\n   By language:")
        for lang, count in sorted(lang_counts.items()):
            print(f"     {lang}: {count} clips")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare voice recordings for XTTS v2 training"
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        default='04_AUDIO_CORE/01_Voice_Samples',
        help='Directory containing raw audio files'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default='voice_training_data',
        help='Output directory for processed data'
    )
    
    args = parser.parse_args()
    
    print("🎙️  Sisi Lola Voice Training Data Preparation\n")
    
    preparer = VoiceDataPreparer(args.input_dir, args.output_dir)
    preparer.process_all_files()
    
    print("\n🎉 Done! Next steps:")
    print("   1. Review the clips in voice_training_data/wavs/")
    print("   2. Check metadata.csv for accuracy")
    print("   3. Record more samples if needed (target: 3-5 hours)")
    print("   4. Run: python train_xtts_sisi_lola.py")


if __name__ == "__main__":
    main()
