#!/usr/bin/env python3
import re
from datetime import timedelta

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

def split_captions_for_engagement(srt_file, max_words_per_caption=2, output_suffix="engaging"):
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
    output_file = f"{output_suffix}_captions.srt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_srt_content)
    
    print(f"✅ Created engaging captions: {output_file}")
    print(f"📊 Original segments: {len(segments)}")
    print(f"📊 New segments: {len(new_segments)}")
    print(f"🎯 Average words per caption: {max_words_per_caption}")
    
    return output_file

def create_single_word_captions(srt_file):
    """Create ultra-engaging single-word captions"""
    return split_captions_for_engagement(srt_file, max_words_per_caption=1, output_suffix="single_word")

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python split_captions.py <srt_file> [--mode single-word|engaging]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    mode = "both"  # default
    
    if len(sys.argv) > 2 and sys.argv[2] == "--mode":
        if len(sys.argv) > 3:
            if sys.argv[3] == "single-word":
                mode = "single-word"
            elif sys.argv[3] == "engaging":
                mode = "engaging"
    
    # Change to the directory containing the input file
    input_dir = os.path.dirname(input_file)
    if input_dir:
        os.chdir(input_dir)
        input_file = os.path.basename(input_file)
    
    print("=== CREATING ENGAGING CAPTIONS (Opus Pro Style) ===")
    
    if mode in ["both", "engaging"]:
        # Create 1-2 word captions
        print("\n🎬 Creating 1-2 word captions...")
        engaging_file = split_captions_for_engagement(input_file, max_words_per_caption=2)
    
    if mode in ["both", "single-word"]:
        # Also create single-word version for maximum engagement
        print("\n🚀 Creating single-word captions...")
        single_word_file = create_single_word_captions(input_file)
    
    # Show preview of both
    print("\n=== PREVIEW: 2-Word Captions ===")
    with open("engaging_captions.srt", 'r') as f:
        lines = f.readlines()
        for i in range(0, min(20, len(lines)), 4):  # Show first 5 segments
            if i + 3 < len(lines):
                print(f"{lines[i].strip()}")
                print(f"{lines[i+1].strip()}")
                print(f"{lines[i+2].strip()}")
                print()
    
    print("\n=== PREVIEW: Single-Word Captions ===")
    with open("single_word_captions.srt", 'r') as f:
        lines = f.readlines()
        for i in range(0, min(20, len(lines)), 4):  # Show first 5 segments
            if i + 3 < len(lines):
                print(f"{lines[i].strip()}")
                print(f"{lines[i+1].strip()}")
                print(f"{lines[i+2].strip()}")
                print() 