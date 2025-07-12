#!/usr/bin/env python3
"""
Simple Subtitle Generator - Outputs SRT file for FFmpeg subtitles filter
- Split by sentence (., !, ?)
- Each caption is a phrase or short sentence (max 2 lines)
- Each caption stays on screen for at least 2 seconds
- Distribute timing across all captions
- For clips, start at 0 seconds (not original video timestamp)
"""
import json
import sys
import re
from datetime import timedelta

def split_sentences(text, max_words_per_line=10):
    # Split on . ! ?
    raw_sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = []
    for s in raw_sentences:
        words = s.strip().split()
        # If sentence is too long, split into lines
        for i in range(0, len(words), max_words_per_line):
            line = ' '.join(words[i:i+max_words_per_line])
            if line:
                sentences.append(line)
    return sentences

def srt_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int((td.total_seconds() - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python simple_subtitle_generator.py transcript.json output.srt")
        sys.exit(1)
    transcript_file = sys.argv[1]
    srt_file = sys.argv[2]
    with open(transcript_file, 'r') as f:
        data = json.load(f)
    text = data[0]['text']
    # For clips, always start at 0 seconds
    start_time = 0.0
    # Duration is the clip duration
    duration = float(data[0]['end']) - float(data[0]['start'])
    # Split into sentences/lines
    captions = split_sentences(text, max_words_per_line=10)
    min_caption_duration = 2.0  # seconds
    n_captions = len(captions)
    # Calculate duration per caption
    total_min_time = n_captions * min_caption_duration
    if total_min_time > duration:
        # If not enough time, stretch video duration to fit all captions
        duration_per_caption = duration / n_captions
    else:
        duration_per_caption = min_caption_duration
    # Write SRT
    with open(srt_file, 'w') as f:
        cur_time = 0.0
        for i, caption in enumerate(captions):
            start = start_time + cur_time
            end = start + duration_per_caption
            if end > duration:
                end = duration
            f.write(f"{i+1}\n")
            f.write(f"{srt_timestamp(start)} --> {srt_timestamp(end)}\n")
            # Split into max 2 lines
            words = caption.split()
            if len(words) > 10:
                f.write(' '.join(words[:10]) + '\n')
                f.write(' '.join(words[10:]) + '\n')
            else:
                f.write(caption + '\n')
            f.write('\n')
            cur_time += duration_per_caption
            if start + duration_per_caption >= duration:
                break

if __name__ == "__main__":
    main() 