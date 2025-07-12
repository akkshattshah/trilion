#!/usr/bin/env python3
"""
Subtitle Generator: Creates perfectly synced FFmpeg drawtext filters from word-level transcripts.
Usage: python subtitle_generator.py transcript.json <duration>
"""
import sys
import json
import os
import math
import re

def escape_text(text):
    # Escape special characters for FFmpeg drawtext
    return text.replace("'", "\\'").replace(':', '\\:').replace(',', '\\,').replace('\\', '\\\\').replace('"', '\\"')

def group_words_into_phrases(words, max_words_per_phrase=3):
    """Group words into short phrases for captions"""
    phrases = []
    current_phrase = []
    
    for word in words:
        current_phrase.append(word)
        
        # Create a phrase when we reach max words or hit punctuation
        if len(current_phrase) >= max_words_per_phrase:
            phrase_text = ' '.join([w['text'] for w in current_phrase])
            phrase_start = current_phrase[0]['start']
            phrase_end = current_phrase[-1]['end']
            
            phrases.append({
                'text': phrase_text,
                'start': phrase_start,
                'end': phrase_end
            })
            current_phrase = []
    
    # Add any remaining words as a phrase
    if current_phrase:
        phrase_text = ' '.join([w['text'] for w in current_phrase])
        phrase_start = current_phrase[0]['start']
        phrase_end = current_phrase[-1]['end']
        
        phrases.append({
            'text': phrase_text,
            'start': phrase_start,
            'end': phrase_end
        })
    
    return phrases

def main():
    if len(sys.argv) < 2:
        print("Usage: python subtitle_generator.py transcript.json <duration>")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    
    if not os.path.exists(transcript_file):
        print(f"Error: Transcript file {transcript_file} not found")
        sys.exit(1)
    
    try:
        with open(transcript_file, 'r') as f:
            transcript_data = json.load(f)
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        sys.exit(1)
    
    # Check if this is a word-level transcript (array of word objects)
    if isinstance(transcript_data, list) and len(transcript_data) > 0:
        if 'start' in transcript_data[0] and 'end' in transcript_data[0] and 'text' in transcript_data[0]:
            # This is a word-level transcript
            words = transcript_data
            
            # Filter words to clip duration
            clip_words = [w for w in words if w['start'] < duration]
            
            if not clip_words:
                # Fallback: simple static text
                font_path = '/Users/jyotisingh/Library/Fonts/DejaVuSans-Bold.ttf'
                print(f"drawtext=text='Caption Ready':fontsize=60:fontcolor=white:fontfile='{font_path}':x=(w-tw)/2:y=1450:box=1:boxcolor=black@0.8:boxborderw=10:enable='between(t,0,{duration})'")
                return
            
            # Group words into phrases
            phrases = group_words_into_phrases(clip_words, max_words_per_phrase=3)
            
            # Limit number of phrases to prevent FFmpeg issues
            if len(phrases) > 20:
                phrases = phrases[:20]
            
            # Generate drawtext filters
            font_path = '/Users/jyotisingh/Library/Fonts/DejaVuSans-Bold.ttf'
            filters = []
            
            for i, phrase in enumerate(phrases):
                if not phrase['text'].strip():
                    continue
                    
                # Use actual timestamps from the transcript
                phrase_start = phrase['start']
                phrase_end = phrase['end']
                
                # Ensure timing doesn't exceed clip duration
                if phrase_start >= duration:
                    break
                    
                phrase_end = min(phrase_end, duration)
                
                # Escape the text
                escaped_phrase = escape_text(phrase['text'])
                
                # Create drawtext filter
                y_pos = 1100 if i % 2 == 0 else 1170  # Lower on 1280px tall video, but not at the edge
                
                filter_str = (
                    f"drawtext=text='{escaped_phrase}':"
                    f"fontsize=90:"
                    f"fontcolor=white:"
                    f"fontfile='{font_path}':"
                    f"x=(w-tw)/2:"
                    f"y={y_pos}:"
                    f"box=1:"
                    f"boxcolor=black@0.8:"
                    f"boxborderw=10:"
                    f"enable='between(t,{phrase_start:.2f},{phrase_end:.2f})'"
                )
                
                filters.append(filter_str)
            
            # Join all filters with commas
            if filters:
                result = ','.join(filters)
                print(result)
            else:
                # Fallback: simple static text
                print(f"drawtext=text='Caption Ready':fontsize=60:fontcolor=white:fontfile='{font_path}':x=(w-tw)/2:y=1450:box=1:boxcolor=black@0.8:boxborderw=10:enable='between(t,0,{duration})'")
            return
    
    # Handle legacy format (single segment with text)
    if isinstance(transcript_data, list):
        segments = transcript_data
    else:
        segments = [transcript_data]
    
    # Extract text and timing
    if not segments:
        print("Error: No transcript segments found")
        sys.exit(1)
    
    segment = segments[0]  # Use first segment
    text = segment.get('text', '')
    start_time = segment.get('start', 0)
    end_time = segment.get('end', duration)
    
    # Extract key phrases from the text (legacy method)
    sentences = re.split(r'[.!?]+', text)
    phrases = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:  # Skip very short sentences
            continue
            
        # Split sentence into words and create 2-3 word phrases
        words = sentence.split()
        for i in range(0, len(words), 2):
            if i + 1 < len(words):
                phrase = f"{words[i]} {words[i+1]}"
            else:
                phrase = words[i]
            
            if len(phrase) > 3:  # Only add meaningful phrases
                phrases.append(phrase)
                
            if len(phrases) >= 15:
                break
                
        if len(phrases) >= 15:
            break
    
    if not phrases:
        # Fallback: simple static text
        font_path = '/Users/jyotisingh/Library/Fonts/DejaVuSans-Bold.ttf'
        print(f"drawtext=text='Caption Ready':fontsize=60:fontcolor=white:fontfile='{font_path}':x=(w-tw)/2:y=1450:box=1:boxcolor=black@0.8:boxborderw=10:enable='between(t,0,{duration})'")
        return
    
    # Calculate timing for each phrase
    phrase_duration = (end_time - start_time) / len(phrases)
    
    # Generate drawtext filters
    font_path = '/Users/jyotisingh/Library/Fonts/DejaVuSans-Bold.ttf'
    filters = []
    
    for i, phrase in enumerate(phrases):
        if not phrase.strip():
            continue
            
        phrase_start = start_time + (i * phrase_duration)
        phrase_end = phrase_start + phrase_duration
        
        # Ensure timing doesn't exceed clip duration
        if phrase_start >= duration:
            break
            
        phrase_end = min(phrase_end, duration)
        
        # Escape the text
        escaped_phrase = escape_text(phrase)
        
        # Create drawtext filter
        y_pos = 1100 if i % 2 == 0 else 1170  # Lower on 1280px tall video, but not at the edge
        
        filter_str = (
            f"drawtext=text='{escaped_phrase}':"
            f"fontsize=90:"
            f"fontcolor=white:"
            f"fontfile='{font_path}':"
            f"x=(w-tw)/2:"
            f"y={y_pos}:"
            f"box=1:"
            f"boxcolor=black@0.8:"
            f"boxborderw=10:"
            f"enable='between(t,{phrase_start:.2f},{phrase_end:.2f})'"
        )
        
        filters.append(filter_str)
    
    # Join all filters with commas
    if filters:
        result = ','.join(filters)
        print(result)
    else:
        # Fallback: simple static text
        print(f"drawtext=text='Caption Ready':fontsize=60:fontcolor=white:fontfile='{font_path}':x=(w-tw)/2:y=1450:box=1:boxcolor=black@0.8:boxborderw=10:enable='between(t,0,{duration})'")

if __name__ == "__main__":
    main() 