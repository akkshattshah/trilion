#!/usr/bin/env python3
"""
Enhanced Whisper Integration: Improved performance and word-level timing
Inspired by WhisperX but compatible with Python 3.13
"""
import whisper
import torch
import json
import os
import subprocess
import gc
from datetime import timedelta
import numpy as np
import sys

class EnhancedWhisperProcessor:
    def __init__(self, model_size="base"):
        """
        Initialize Enhanced Whisper with optimized settings
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        pass
        
        # Load model with optimizations
        self.model = None
        
    def load_model(self):
        """Load the Whisper model with optimizations"""
        if self.model is None:
            self.model = whisper.load_model(self.model_size, device=self.device)
            
            # Optimize for inference
            if self.device == "cuda":
                self.model.half()  # Use FP16 for faster inference
    
    def transcribe_with_word_timing(self, audio_path, word_timestamps=True):
        """
        Enhanced transcription with improved word-level timing
        """
        self.load_model()
        result = self.model.transcribe(
            audio_path,
            word_timestamps=word_timestamps,
            condition_on_previous_text=False,  # Reduces hallucination
            temperature=0.0,  # More deterministic output
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6
        )
        
        detected_language = result.get("language", "unknown")
        
        # Post-process for better word alignment
        enhanced_segments = []
        
        for segment in result["segments"]:
            enhanced_segment = {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"],
                "words": []
            }
            
            # If word-level timestamps are available
            if "words" in segment and segment["words"]:
                enhanced_segment["words"] = segment["words"]
            else:
                # Fallback: estimate word timing based on speech rate
                enhanced_segment["words"] = self._estimate_word_timing(
                    segment["text"], 
                    segment["start"], 
                    segment["end"]
                )
            
            enhanced_segments.append(enhanced_segment)
        
        # Clean up GPU memory
        if self.device == "cuda":
            gc.collect()
            torch.cuda.empty_cache()
        
        return {
            "language": result.get("language"),
            "segments": enhanced_segments,
            "text": result.get("text", "")
        }
    
    def _estimate_word_timing(self, text, start_time, end_time):
        """
        Estimate word-level timing when not available from Whisper
        """
        words = text.strip().split()
        if not words:
            return []
        
        duration = end_time - start_time
        time_per_word = duration / len(words)
        
        word_timestamps = []
        current_time = start_time
        
        for word in words:
            word_end = current_time + time_per_word
            word_timestamps.append({
                "word": word,
                "start": current_time,
                "end": word_end
            })
            current_time = word_end
        
        return word_timestamps
    
    def generate_viral_captions(self, audio_path, output_dir=".", style="single-word"):
        """
        Generate viral-optimized captions using Enhanced Whisper
        """
        print(f"🔥 Generating viral captions with Enhanced Whisper...")
        
        # Get enhanced transcription
        result = self.transcribe_with_word_timing(audio_path)
        
        # Process segments for viral content
        viral_segments = []
        segment_id = 1
        
        for segment in result["segments"]:
            words = segment.get("words", [])
            
            if style == "single-word":
                # Create single-word captions
                for word_data in words:
                    if isinstance(word_data, dict) and "word" in word_data:
                        viral_segments.append({
                            "id": segment_id,
                            "start": word_data["start"],
                            "end": word_data["end"],
                            "text": word_data["word"].strip()
                        })
                        segment_id += 1
            
            elif style == "two-word":
                # Create 2-word captions for better flow
                for i in range(0, len(words), 2):
                    word_group = words[i:i+2]
                    if len(word_group) > 0:
                        start_time = word_group[0].get("start", segment["start"])
                        end_time = word_group[-1].get("end", segment["end"])
                        text = " ".join([w.get("word", "") for w in word_group]).strip()
                        
                        if text:
                            viral_segments.append({
                                "id": segment_id,
                                "start": start_time,
                                "end": end_time,
                                "text": text
                            })
                            segment_id += 1
            
            else:  # phrase-based
                viral_segments.append({
                    "id": segment_id,
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })
                segment_id += 1
        
        # Generate SRT file
        srt_content = self._generate_srt_content(viral_segments)
        srt_file = os.path.join(output_dir, f"enhanced_{style}_captions.srt")
        
        with open(srt_file, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        # Generate enhanced JSON
        json_data = {
            "enhanced_whisper": True,
            "transcription_info": {
                "language": result.get("language", "unknown"),
                "total_segments": len(viral_segments),
                "style": style,
                "word_level_timing": True,
                "model_size": self.model_size
            },
            "segments": viral_segments,
            "full_transcript": " ".join([s["text"] for s in viral_segments])
        }
        
        json_file = os.path.join(output_dir, f"enhanced_{style}_captions.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
        
        print(f"✅ Generated Enhanced Whisper viral captions:")
        print(f"   📄 SRT: {srt_file}")
        print(f"   📊 JSON: {json_file}")
        print(f"   🎯 Segments: {len(viral_segments)}")
        print(f"   ⚡ Style: {style}")
        
        return {
            "success": True,
            "srt_file": srt_file,
            "json_file": json_file,
            "segments": len(viral_segments),
            "language": result.get("language"),
            "style": style,
            "transcript": json_data["full_transcript"]
        }
    
    def _generate_srt_content(self, segments):
        """Generate SRT content from segments"""
        srt_content = ""
        
        for segment in segments:
            start_time = self._format_timestamp(segment["start"])
            end_time = self._format_timestamp(segment["end"])
            text = segment["text"]
            
            srt_content += f"{segment['id']}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        return srt_content
    
    def _format_timestamp(self, seconds):
        """Format timestamp for SRT (HH:MM:SS,mmm)"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = td.total_seconds() % 60
        milliseconds = int((secs % 1) * 1000)
        secs = int(secs)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def cleanup_models(self):
        """Clean up GPU memory"""
        if self.device == "cuda" and self.model is not None:
            del self.model
            gc.collect()
            torch.cuda.empty_cache()

    def process_video(self, video_path):
        """
        Process a video file directly, extracting audio and transcribing
        Returns transcript text and segments
        """
        # Extract audio for Whisper analysis
        audio_file = "temp_analysis_audio.wav"
        try:
            print("[EXTRACT] Extracting audio...", file=sys.stderr)
            subprocess.run([
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-y", audio_file
            ], check=True, capture_output=True)
            
            # Transcribe the audio
            result = self.transcribe_with_word_timing(audio_file)
            
            # Clean up audio file
            if os.path.exists(audio_file):
                os.remove(audio_file)
            
            return result["text"], result["segments"]
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Audio extraction failed: {e}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"[ERROR] Transcription failed: {e}", file=sys.stderr)
            raise
        finally:
            # Ensure cleanup
            if os.path.exists(audio_file):
                os.remove(audio_file)

def process_video_with_enhanced_whisper(video_file, output_dir=".", style="single-word"):
    """
    Complete video processing pipeline with Enhanced Whisper
    """
    print(f"🎬 Enhanced Whisper Processing: {os.path.basename(video_file)}")
    
    # Extract audio
    audio_file = os.path.join(output_dir, "enhanced_audio.wav")
    
    try:
        subprocess.run([
            "ffmpeg", "-i", video_file,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-y", audio_file
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Audio extraction failed: {e}"}
    
    # Process with Enhanced Whisper
    processor = EnhancedWhisperProcessor()
    
    try:
        result = processor.generate_viral_captions(audio_file, output_dir, style)
        
        # Cleanup
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        processor.cleanup_models()
        
        return result
        
    except Exception as e:
        return {"error": f"Enhanced Whisper processing failed: {e}"}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_whisper.py <video_file> [style] [output_dir]")
        print("Styles: single-word, two-word, phrase")
        sys.exit(1)
    
    video_file = sys.argv[1]
    style = sys.argv[2] if len(sys.argv) > 2 else "single-word"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    
    result = process_video_with_enhanced_whisper(video_file, output_dir, style)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success! Generated {result['segments']} segments")
        print(f"📄 SRT: {result['srt_file']}")
        print(f"📊 JSON: {result['json_file']}") 