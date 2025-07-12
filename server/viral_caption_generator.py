#!/usr/bin/env python3
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import whisper
import json
from datetime import timedelta

def format_time(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_captions_with_whisper(audio_file, model_size="base"):
    """Generate synchronized captions using local Whisper"""
    
    print(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing: {audio_file}")
    result = model.transcribe(audio_file)
    
    print("Full transcript:")
    print(result["text"])
    print(f"\nNumber of segments: {len(result['segments'])}")
    
    # Generate SRT format
    srt_content = ""
    for i, segment in enumerate(result["segments"], 1):
        start_time = format_time(segment["start"])
        end_time = format_time(segment["end"])
        text = segment["text"].strip()
        
        srt_content += f"{i}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
    
    # Save SRT file
    srt_filename = f"{audio_file.rsplit('.', 1)[0]}.srt"
    with open(srt_filename, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    # Generate VTT format
    vtt_content = "WEBVTT\n\n"
    for i, segment in enumerate(result["segments"], 1):
        start_time = format_time(segment["start"]).replace(",", ".")
        end_time = format_time(segment["end"]).replace(",", ".")
        text = segment["text"].strip()
        
        vtt_content += f"{start_time} --> {end_time}\n"
        vtt_content += f"{text}\n\n"
    
    vtt_filename = f"{audio_file.rsplit('.', 1)[0]}.vtt"
    with open(vtt_filename, "w", encoding="utf-8") as f:
        f.write(vtt_content)
    
    # Generate JSON with detailed info
    json_data = {
        "video_info": {
            "duration": result["segments"][-1]["end"] if result["segments"] else 0,
            "segments_count": len(result["segments"]),
            "language": result.get("language", "unknown")
        },
        "segments": [
            {
                "id": i,
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "avg_logprob": segment.get("avg_logprob", None),
                "no_speech_prob": segment.get("no_speech_prob", None)
            }
            for i, segment in enumerate(result["segments"], 1)
        ]
    }
    
    json_filename = f"{audio_file.rsplit('.', 1)[0]}_captions.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\nGenerated caption files:")
    print(f"- {srt_filename} (SubRip format)")
    print(f"- {vtt_filename} (WebVTT format)")
    print(f"- {json_filename} (JSON format)")
    
    return result["segments"]

if __name__ == "__main__":
    import sys
    import subprocess
    import os
    
    if len(sys.argv) != 2:
        print("Usage: python whisper_captions.py <video_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    # Extract audio from video
    audio_file = os.path.join(os.path.dirname(video_file), "extracted_audio.wav")
    
    print("=== WHISPER CAPTION GENERATION ===")
    print(f"Extracting audio from: {video_file}")
    
    # Use ffmpeg to extract audio
    try:
        subprocess.run([
            "ffmpeg", "-i", video_file, 
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-y", audio_file
        ], check=True, capture_output=True)
        print(f"Audio extracted to: {audio_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        sys.exit(1)
    
    print(f"Processing: {audio_file}")
    
    try:
        segments = generate_captions_with_whisper(audio_file, "base")
        
        print("\n=== CAPTION PREVIEW ===")
        for i, segment in enumerate(segments[:5], 1):  # Show first 5 segments
            start_time = format_time(segment["start"])
            end_time = format_time(segment["end"])
            print(f"{i}. [{start_time} --> {end_time}] {segment['text'].strip()}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Trying with smaller model...")
        try:
            segments = generate_captions_with_whisper(audio_file, "tiny")
        except Exception as e2:
            print(f"Error with tiny model: {e2}")
    
    # Clean up extracted audio file
    if os.path.exists(audio_file):
        os.remove(audio_file)
        print(f"\nCleaned up temporary audio file: {audio_file}") 