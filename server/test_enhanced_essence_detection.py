#!/usr/bin/env python3
"""
Test script for enhanced essence detection and perfect beginning prioritization
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_sentence_boundary_detector import EnhancedSentenceBoundaryDetector, find_enhanced_clip_boundaries_with_sentence_detection

def test_essence_detection():
    """Test the video essence detection with the bedroom-to-millions example"""
    
    # Sample transcript from a success story video (like the bedroom-to-millions example)
    sample_transcript = """
    So there I was, sitting in my bedroom with just $500 to my name. 
    I had quit my job because I was tired of the 9-to-5 grind. 
    The problem was that I didn't know how to make money online.
    
    But then I discovered the secret to building a million-dollar business from home.
    Here's how I turned $500 into $2 million in just 18 months.
    
    The first thing you need to understand is that passive income is the key.
    I started with a simple SaaS product that solved a real problem.
    The solution was to create something that people would pay for monthly.
    
    My marketing strategy was simple but effective. I focused on customer acquisition
    through social media and content marketing. The revenue model was subscription-based.
    
    Point number one: Start with a problem that people are willing to pay to solve.
    Point number two: Build a recurring revenue stream.
    Point number three: Scale through automation and systems.
    
    Today, I'm generating $50,000 in passive income every month.
    The business runs itself while I travel the world.
    """
    
    detector = EnhancedSentenceBoundaryDetector()
    
    print("🎯 TESTING VIDEO ESSENCE DETECTION")
    print("=" * 50)
    
    # Test essence detection
    essence_data = detector.detect_video_essence(sample_transcript)
    
    if essence_data and essence_data.get("main_essence"):
        essence_category, essence_info = essence_data["main_essence"]
        print(f"✅ MAIN ESSENCE DETECTED: {essence_category.replace('_', ' ').title()}")
        print(f"📊 Score: {essence_info['score']}")
        print(f"🎯 Top matches: {essence_info['matches'][:3]}")
    else:
        print("❌ No essence detected")
    
    print("\n" + "=" * 50)
    
    # Test essence-rich segment detection
    word_segments = [
        {"start": 0.0, "end": 0.3, "text": "So"},
        {"start": 0.3, "end": 0.6, "text": "there"},
        {"start": 0.6, "end": 1.0, "text": "I"},
        {"start": 1.0, "end": 1.3, "text": "was"},
        {"start": 1.3, "end": 1.6, "text": "sitting"},
        {"start": 1.6, "end": 2.0, "text": "in"},
        {"start": 2.0, "end": 2.3, "text": "my"},
        {"start": 2.3, "end": 2.6, "text": "bedroom"},
        {"start": 2.6, "end": 3.0, "text": "with"},
        {"start": 3.0, "end": 3.3, "text": "just"},
        {"start": 3.3, "end": 3.6, "text": "$500"},
        {"start": 3.6, "end": 4.0, "text": "to"},
        {"start": 4.0, "end": 4.3, "text": "my"},
        {"start": 4.3, "end": 4.6, "text": "name."},
        {"start": 4.6, "end": 5.0, "text": "I"},
        {"start": 5.0, "end": 5.3, "text": "had"},
        {"start": 5.3, "end": 5.6, "text": "quit"},
        {"start": 5.6, "end": 6.0, "text": "my"},
        {"start": 6.0, "end": 6.3, "text": "job"},
        {"start": 6.3, "end": 6.6, "text": "because"},
        {"start": 6.6, "end": 7.0, "text": "I"},
        {"start": 7.0, "end": 7.3, "text": "was"},
        {"start": 7.3, "end": 7.6, "text": "tired"},
        {"start": 7.6, "end": 8.0, "text": "of"},
        {"start": 8.0, "end": 8.3, "text": "the"},
        {"start": 8.3, "end": 8.6, "text": "9-to-5"},
        {"start": 8.6, "end": 9.0, "text": "grind."},
        {"start": 9.0, "end": 9.3, "text": "The"},
        {"start": 9.3, "end": 9.6, "text": "problem"},
        {"start": 9.6, "end": 10.0, "text": "was"},
        {"start": 10.0, "end": 10.3, "text": "that"},
        {"start": 10.3, "end": 10.6, "text": "I"},
        {"start": 10.6, "end": 11.0, "text": "didn't"},
        {"start": 11.0, "end": 11.3, "text": "know"},
        {"start": 11.3, "end": 11.6, "text": "how"},
        {"start": 11.6, "end": 12.0, "text": "to"},
        {"start": 12.0, "end": 12.3, "text": "make"},
        {"start": 12.3, "end": 12.6, "text": "money"},
        {"start": 12.6, "end": 13.0, "text": "online."},
        {"start": 13.0, "end": 13.3, "text": "But"},
        {"start": 13.3, "end": 13.6, "text": "then"},
        {"start": 13.6, "end": 14.0, "text": "I"},
        {"start": 14.0, "end": 14.3, "text": "discovered"},
        {"start": 14.3, "end": 14.6, "text": "the"},
        {"start": 14.6, "end": 15.0, "text": "secret"},
        {"start": 15.0, "end": 15.3, "text": "to"},
        {"start": 15.3, "end": 15.6, "text": "building"},
        {"start": 15.6, "end": 16.0, "text": "a"},
        {"start": 16.0, "end": 16.3, "text": "million-dollar"},
        {"start": 16.3, "end": 16.6, "text": "business"},
        {"start": 16.6, "end": 17.0, "text": "from"},
        {"start": 17.0, "end": 17.3, "text": "home."},
        {"start": 17.3, "end": 17.6, "text": "Here's"},
        {"start": 17.6, "end": 18.0, "text": "how"},
        {"start": 18.0, "end": 18.3, "text": "I"},
        {"start": 18.3, "end": 18.6, "text": "turned"},
        {"start": 18.6, "end": 19.0, "text": "$500"},
        {"start": 19.0, "end": 19.3, "text": "into"},
        {"start": 19.3, "end": 19.6, "text": "$2"},
        {"start": 19.6, "end": 20.0, "text": "million"},
        {"start": 20.0, "end": 20.3, "text": "in"},
        {"start": 20.3, "end": 20.6, "text": "just"},
        {"start": 20.6, "end": 21.0, "text": "18"},
        {"start": 21.0, "end": 21.3, "text": "months."},
        {"start": 21.3, "end": 21.6, "text": "Point"},
        {"start": 21.6, "end": 22.0, "text": "number"},
        {"start": 22.0, "end": 22.3, "text": "one:"},
        {"start": 22.3, "end": 22.6, "text": "Start"},
        {"start": 22.6, "end": 23.0, "text": "with"},
        {"start": 23.0, "end": 23.3, "text": "a"},
        {"start": 23.3, "end": 23.6, "text": "problem"},
        {"start": 23.6, "end": 24.0, "text": "that"},
        {"start": 24.0, "end": 24.3, "text": "people"},
        {"start": 24.3, "end": 24.6, "text": "are"},
        {"start": 24.6, "end": 25.0, "text": "willing"},
        {"start": 25.0, "end": 25.3, "text": "to"},
        {"start": 25.3, "end": 25.6, "text": "pay"},
        {"start": 25.6, "end": 26.0, "text": "to"},
        {"start": 26.0, "end": 26.3, "text": "solve."}
    ]
    
    print("🎬 TESTING ENHANCED CLIP BOUNDARY DETECTION")
    print("=" * 50)
    
    # Test the enhanced boundary detection
    result = find_enhanced_clip_boundaries_with_sentence_detection(
        segments=word_segments,
        center_index=15,  # Around "secret to building"
        full_transcript=sample_transcript,
        target_duration=30
    )
    
    if result:
        print(f"\n✅ ENHANCED CLIP CREATED SUCCESSFULLY!")
        print(f"📝 Start text: \"{result.get('start_text', 'N/A')}\"")
        print(f"⏰ Duration: {result['end'] - result['start']:.1f}s")
        print(f"📊 Quality: {result['start_quality']:.1f}")
    else:
        print("❌ Failed to create enhanced clip")

if __name__ == "__main__":
    test_essence_detection() 