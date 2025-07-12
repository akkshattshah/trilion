#!/usr/bin/env python3
"""
Persistent Whisper Manager: Keep model loaded in memory across multiple clips
MASSIVE PERFORMANCE BOOST: Load once, use many times
"""
import sys
import json
import os
from enhanced_whisper import EnhancedWhisperProcessor

class PersistentWhisperManager:
    """
    Singleton manager that keeps Whisper model loaded in memory
    """
    _instance = None
    _processor = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize_model(self, model_size="base"):
        """Initialize the persistent Whisper model"""
        if self._processor is None:
            self._processor = EnhancedWhisperProcessor(model_size=model_size)
            # Pre-load the model to keep it in memory
            self._processor.load_model()
        
        return self._processor
    
    def get_processor(self):
        """Get the persistent processor (initialize if needed)"""
        if self._processor is None:
            return self.initialize_model()
        return self._processor
    
    def cleanup_models(self):
        """Clean up models (only call at the very end)"""
        if self._processor is not None:
            self._processor.cleanup_models()
            self._processor = None

# Global instance
persistent_manager = PersistentWhisperManager()

def get_persistent_whisper():
    """Get the persistent Whisper processor"""
    return persistent_manager.get_processor()

def cleanup_persistent_whisper():
    """Cleanup persistent models (call at end of session)"""
    persistent_manager.cleanup_models()

# Fast transcription function using persistent model
def fast_transcribe_with_persistent_model(audio_path, word_timestamps=True):
    """
    Fast transcription using persistent Whisper model
    No model loading overhead - massive speed boost!
    """
    processor = get_persistent_whisper()
    
    # Skip the load_model() call since it's already loaded
    # Use the existing transcribe_with_word_timing but without reloading
    result = processor.model.transcribe(
        audio_path,
        word_timestamps=word_timestamps,
        condition_on_previous_text=False,
        temperature=0.0,
        compression_ratio_threshold=2.4,
        logprob_threshold=-1.0,
        no_speech_threshold=0.6
    )
    
    detected_language = result.get("language", "unknown")
    
    # Post-process for better word alignment (same as original)
    enhanced_segments = []
    
    for segment in result["segments"]:
        enhanced_segment = {
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"],
            "words": []
        }
        
        if "words" in segment and segment["words"]:
            enhanced_segment["words"] = segment["words"]
        else:
            enhanced_segment["words"] = processor._estimate_word_timing(
                segment["text"], 
                segment["start"], 
                segment["end"]
            )
        
        enhanced_segments.append(enhanced_segment)
    
    return {
        "language": result.get("language"),
        "segments": enhanced_segments,
        "text": result.get("text", "")
    }

if __name__ == "__main__":
    # Test the persistent manager
    import tempfile
    import subprocess
    
    if len(sys.argv) != 2:
        print("Usage: python3 persistent_whisper_manager.py <video_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    # Extract audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        try:
            subprocess.run([
                "ffmpeg", "-i", video_file,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-y", tmp_audio.name
            ], check=True, capture_output=True)
            
            # Test fast transcription
            result = fast_transcribe_with_persistent_model(tmp_audio.name)
            
            print(f"\n✅ SUCCESS: Fast transcription completed!")
            print(f"Language: {result['language']}")
            print(f"Segments: {len(result['segments'])}")
            
            # Cleanup
            cleanup_persistent_whisper()
            
        finally:
            if os.path.exists(tmp_audio.name):
                os.remove(tmp_audio.name) 