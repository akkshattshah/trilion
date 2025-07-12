#!/usr/bin/env python3
"""
Viral Caption System: Ultra-engaging captions for TikTok/Instagram Reels style videos
Enhanced with WhisperX for 70x faster processing and superior word-level accuracy
OPTIMIZED VERSION: Uses persistent Whisper model for MASSIVE speed boost
"""
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Use PERSISTENT Whisper for massive speed boost
from persistent_whisper_manager import fast_transcribe_with_persistent_model, get_persistent_whisper, cleanup_persistent_whisper
import json
import os
import sys
import subprocess
import re
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

def parse_srt_time(time_str):
    """Parse SRT time format to seconds"""
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split(',')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    return total_seconds

def format_srt_time(seconds):
    """Convert seconds to SRT time format"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_viral_captions_from_video(video_file, output_dir=".", caption_style="single-word"):
    """
    Generate viral captions from video file using WhisperX
    Returns: dict with caption files and metadata
    """
    # Extract audio from video
    audio_file = os.path.join(output_dir, "viral_audio.wav")
    try:
        subprocess.run([
            "ffmpeg", "-i", video_file, 
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-y", audio_file
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Audio extraction failed: {e}"}
    
    # Generate transcription with PERSISTENT Enhanced Whisper (MASSIVE SPEED BOOST!)
    try:
        # Use persistent Whisper model - NO RELOAD NEEDED!
        result = fast_transcribe_with_persistent_model(audio_file, word_timestamps=True)
        
        # Check if detected language is English
        detected_language = result.get("language", "unknown")
        
        if detected_language != "en":
            return {
                "error": f"Language not supported: {detected_language}. Viral captions are currently only available for English audio. Please use an English video.",
                "detected_language": detected_language,
                "supported_languages": ["en"]
            }
        
        # Generate enhanced viral captions using Enhanced Whisper word-level data
        viral_segments = []
        segment_id = 1
        
        # Process segments with word-level precision
        for segment in result["segments"]:
            words = segment.get("words", [])
            
            if caption_style == "single-word":
                # Create single-word captions with precise timing
                for word_data in words:
                    if isinstance(word_data, dict) and "word" in word_data:
                        viral_segments.append({
                            "id": segment_id,
                            "start": word_data["start"],
                            "end": word_data["end"],
                            "text": word_data["word"].strip()
                        })
                        segment_id += 1
            
            elif caption_style == "engaging":
                # Create 1-2 word engaging captions
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
            
            else:  # both or fallback
                # Use phrase-level segments
                viral_segments.append({
                    "id": segment_id,
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })
                segment_id += 1
        
        # Generate base SRT with enhanced timing
        base_srt_file = os.path.join(output_dir, "base_captions.srt")
        srt_content = ""
        for seg in viral_segments:
            start_time = format_time(seg["start"])
            end_time = format_time(seg["end"])
            text = seg["text"]
            
            srt_content += f"{seg['id']}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        with open(base_srt_file, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        # NO cleanup here - keep model persistent for next clip!
            
    except Exception as e:
        return {"error": f"Enhanced Whisper transcription failed: {e}"}
    
    # Generate viral caption styles
    caption_files = {}
    
    if caption_style in ["single-word", "both"]:
        single_word_file = create_single_word_captions(base_srt_file, output_dir)
        caption_files["single_word"] = single_word_file
    
    if caption_style in ["engaging", "both"]:
        engaging_file = create_engaging_captions(base_srt_file, output_dir)
        caption_files["engaging"] = engaging_file
    
    # Clean up temporary files
    if os.path.exists(audio_file):
        os.remove(audio_file)
    
    return {
        "success": True,
        "base_segments": len(viral_segments),
        "caption_files": caption_files,
        "transcript": " ".join([s["text"] for s in viral_segments]),
        "enhanced_whisper": True,
        "word_level_timing": True
    }

def create_single_word_captions(srt_file, output_dir):
    """Create ultra-viral single-word captions"""
    return split_captions_for_engagement(srt_file, output_dir, max_words_per_caption=1, output_suffix="single_word")

def create_engaging_captions(srt_file, output_dir):
    """Create engaging 1-2 word captions"""
    return split_captions_for_engagement(srt_file, output_dir, max_words_per_caption=2, output_suffix="engaging")

def split_captions_for_engagement(srt_file, output_dir, max_words_per_caption=1, output_suffix="viral"):
    """Split existing captions into shorter, more engaging segments"""
    
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse existing SRT segments
    segments = re.findall(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', content, re.DOTALL)
    
    new_segments = []
    segment_id = 1
    
    for old_id, start_time, end_time, text in segments:
        start_seconds = parse_srt_time(start_time)
        end_seconds = parse_srt_time(end_time)
        duration = end_seconds - start_seconds
        
        # Clean and split text into words
        words = text.strip().split()
        
        if len(words) <= max_words_per_caption:
            # If already short enough, keep as is
            new_segments.append((segment_id, start_seconds, end_seconds, text.strip()))
            segment_id += 1
        else:
            # Split into smaller chunks
            word_groups = []
            for i in range(0, len(words), max_words_per_caption):
                word_groups.append(' '.join(words[i:i + max_words_per_caption]))
            
            # Calculate timing for each word group
            time_per_group = duration / len(word_groups)
            
            for i, word_group in enumerate(word_groups):
                group_start = start_seconds + (i * time_per_group)
                group_end = start_seconds + ((i + 1) * time_per_group)
                
                new_segments.append((segment_id, group_start, group_end, word_group))
                segment_id += 1
    
    # Generate new SRT content
    new_srt_content = ""
    for seg_id, start, end, text in new_segments:
        start_time = format_srt_time(start)
        end_time = format_srt_time(end)
        
        new_srt_content += f"{seg_id}\n"
        new_srt_content += f"{start_time} --> {end_time}\n"
        new_srt_content += f"{text}\n\n"
    
    # Save the new SRT file
    output_file = os.path.join(output_dir, f"{output_suffix}_captions.srt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_srt_content)
    
    print(f"✅ Created {output_suffix} captions: {len(new_segments)} segments")
    return output_file

def generate_ffmpeg_viral_filter(srt_file, style="impact"):
    """Generate FFmpeg filter for viral-style captions"""
    
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse SRT segments
    segments = re.findall(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', content, re.DOTALL)
    
    filters = []
    
    # Font styling based on style
    if style == "impact":
        font_settings = {
            "fontsize": 90,  # Reduced from 24/28 to 90 for 1280px tall video
            "fontcolor": "white",
            "fontfile": "/System/Library/Fonts/Impact.ttf",
            "outline": 3,
            "outlinecolor": "black",
            "bold": 1,
            "y_position": "h-th-120"  # 120px from bottom
        }
    else:  # default
        font_settings = {
            "fontsize": 80,
            "fontcolor": "white",
            "fontfile": "/System/Library/Fonts/Helvetica.ttc",
            "outline": 2,
            "outlinecolor": "black",
            "bold": 1,
            "y_position": "h-th-140"
        }
    
    for i, (seg_id, start_time, end_time, text) in enumerate(segments):
        if not text.strip():
            continue
            
        # Convert time to seconds
        start_seconds = parse_srt_time(start_time)
        end_seconds = parse_srt_time(end_time)
        
        # Escape text for FFmpeg
        escaped_text = text.replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
        
        # Create drawtext filter
        filter_str = (
            f"drawtext=text='{escaped_text}':"
            f"fontsize={font_settings['fontsize']}:"
            f"fontcolor={font_settings['fontcolor']}:"
            f"fontfile='{font_settings['fontfile']}':"
            f"x=(w-tw)/2:"
            f"y={font_settings['y_position']}:"
            f"outline={font_settings['outline']}:"
            f"outlinecolor={font_settings['outlinecolor']}:"
            f"enable='between(t,{start_seconds:.3f},{end_seconds:.3f})'"
        )
        
        filters.append(filter_str)
        
        # Limit to prevent FFmpeg overload
        if len(filters) >= 100:
            break
    
    # Join all filters
    if filters:
        return ','.join(filters)
    else:
        return f"drawtext=text='VIRAL READY':fontsize=24:fontcolor=white:x=(w-tw)/2:y=h-th-60"

def process_video_with_viral_captions(video_file, output_file, caption_style="single-word", font_style="impact", processing_mode="crop"):
    """
    Complete pipeline: video -> viral captions -> final video
    Processing mode affects caption positioning:
    - crop: Normal positioning for cropped videos
    - resize: Lower positioning for rescaled videos (in black bar area)
    """
    print(f"🎬 PROCESSING: {os.path.basename(video_file)}")
    
    video_dir = os.path.dirname(video_file)
    
    # Generate viral captions
    caption_result = generate_viral_captions_from_video(video_file, video_dir, caption_style)
    
    if "error" in caption_result:
        return caption_result
    
    # Get the appropriate caption file
    if caption_style == "single-word":
        srt_file = caption_result["caption_files"]["single_word"]
    else:
        srt_file = caption_result["caption_files"]["engaging"]
    
    # Apply captions to video using subtitle filter (much more reliable)
    print("🎯 Applying viral captions to video...")
    print(f"📍 Caption positioning mode: {processing_mode} {'(bottom black bar)' if processing_mode == 'resize' else '(over video content)'}")
    
    # Font styling based on style and processing mode
    # For rescaled videos, place captions in the bottom black bar area
    if processing_mode == "resize":
        # Rescaled mode: position captions in the bottom black bar
        # MarginV=1400+ ensures captions appear below the 608px scaled video content
        if font_style == "impact":
            font_settings = "FontName='Impact',FontSize=22,PrimaryColour=&Hffffff,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0,Bold=1,MarginV=1400"
        else:  # default
            font_settings = "FontName='Helvetica',FontSize=20,PrimaryColour=&Hffffff,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0,Bold=1,MarginV=1420"
    else:
        # Cropped mode: normal positioning over video content  
        if font_style == "impact":
            font_settings = "FontName='Impact',FontSize=22,PrimaryColour=&Hffffff,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0,Bold=1,MarginV=140"
        else:  # default
            font_settings = "FontName='Helvetica',FontSize=20,PrimaryColour=&Hffffff,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0,Bold=1,MarginV=160"
    
    ffmpeg_cmd = [
        "ffmpeg", "-i", video_file,
        "-vf", f"subtitles={srt_file}:force_style='{font_settings},Alignment=10'",
        "-c:a", "copy",
        "-y", output_file
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        
        # Clean up temporary SRT files
        for caption_file in caption_result["caption_files"].values():
            if os.path.exists(caption_file):
                os.remove(caption_file)
        
        return {
            "success": True,
            "output_file": output_file,
            "segments": caption_result["base_segments"],
            "transcript": caption_result["transcript"]
        }
        
    except subprocess.CalledProcessError as e:
        return {"error": f"Video processing failed: {e}"}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python viral_caption_system.py <video_file> <output_file> [style] [font] [processing_mode]")
        print("Styles: single-word, engaging, both")
        print("Fonts: impact, default")
        print("Processing modes: resize, crop, auto")
        sys.exit(1)
    
    video_file = sys.argv[1]
    output_file = sys.argv[2]
    caption_style = sys.argv[3] if len(sys.argv) > 3 else "single-word"
    font_style = sys.argv[4] if len(sys.argv) > 4 else "impact"
    processing_mode = sys.argv[5] if len(sys.argv) > 5 else "crop"
    
    result = process_video_with_viral_captions(video_file, output_file, caption_style, font_style, processing_mode)
    
    if result.get("success"):
        print(f"✅ SUCCESS! Viral video created: {result['output_file']}")
        print(f"📊 Segments: {result['segments']}")
    else:
        print(f"❌ ERROR: {result.get('error')}") 