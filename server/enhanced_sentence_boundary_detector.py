#!/usr/bin/env python3
"""
ENHANCED SENTENCE BOUNDARY DETECTOR
Solves the problem of clips starting mid-sentence by implementing intelligent sentence grouping
and enhanced pattern recognition for structured content beginnings.
NOW WITH: Video essence detection and perfect beginning prioritization
"""

import re
import sys


class EnhancedSentenceBoundaryDetector:
    def __init__(self):
        # 🎯 STRUCTURED CONTENT PATTERNS - Exactly what the user requested
        self.structured_beginnings = {
            # Numbered/Organized Content
            "numbered_points": [
                r"^(point|tip|step|reason|way|method|rule|fact|secret|hack)\s+(number\s+)?\d+",
                r"^(the\s+)?(first|second|third|fourth|fifth|next|final)\s+(point|tip|step|reason|way|method)",
                r"^\d+\.\s*",  # "1. Something"
                r"^number\s+\d+",
                r"^lesson\s+\d+",
                r"^chapter\s+\d+"
            ],
            
            # Question Starters - Natural hooks
            "question_hooks": [
                r"^how\s+to\s+",
                r"^what\s+if\s+",
                r"^why\s+do\s+",
                r"^have\s+you\s+ever\s+",
                r"^did\s+you\s+know\s+",
                r"^do\s+you\s+know\s+",
                r"^can\s+you\s+",
                r"^would\s+you\s+",
                r"^are\s+you\s+",
                r"^is\s+it\s+true\s+that\s+"
            ],
            
            # Instructional Content
            "instructional_starts": [
                r"^here's\s+how\s+",
                r"^this\s+is\s+how\s+",
                r"^let\s+me\s+show\s+you\s+",
                r"^let\s+me\s+tell\s+you\s+",
                r"^i'm\s+going\s+to\s+show\s+you\s+",
                r"^today\s+we're\s+going\s+to\s+",
                r"^first\s+thing\s+you\s+need\s+",
                r"^the\s+first\s+thing\s+"
            ],
            
            # Story/Narrative Starters
            "story_hooks": [
                r"^so\s+there\s+i\s+was\s+",
                r"^picture\s+this\s+",
                r"^imagine\s+if\s+",
                r"^let\s+me\s+tell\s+you\s+about\s+",
                r"^this\s+happened\s+to\s+me\s+",
                r"^once\s+upon\s+a\s+time\s+",
                r"^story\s+time\s+"
            ],
            
            # Attention Grabbers
            "attention_grabbers": [
                r"^listen\s+",
                r"^attention\s+",
                r"^hold\s+on\s+",
                r"^wait\s+",
                r"^stop\s+",
                r"^pause\s+",
                r"^look\s+",
                r"^watch\s+this\s+"
            ]
        }
        
        # 🎯 VIDEO ESSENCE PATTERNS - Detect the main idea/gold knowledge
        self.essence_patterns = {
            # Success/Money Stories
            "success_stories": [
                r"(made|earned|generated|built)\s+\$?\d+[k|m|b]?\s+(dollars?|money|revenue|income)",
                r"(started|began|launched)\s+(with|from)\s+\$?\d+",
                r"(turned|converted)\s+\$?\d+\s+into\s+\$?\d+",
                r"(million|billion|thousand)\s+(dollar|revenue|business)",
                r"(bedroom|garage|basement)\s+(business|startup|company)",
                r"(quit|left)\s+(job|work)\s+(to|and)\s+(start|build|create)",
                r"(passive|recurring)\s+(income|revenue|money)"
            ],
            
            # How-to/Educational Content
            "how_to_content": [
                r"how\s+to\s+(make|earn|build|create|start|grow|scale)",
                r"the\s+(secret|key|trick|method|strategy|formula)\s+to",
                r"(step|steps)\s+(to|for)\s+",
                r"(process|method|approach|technique)\s+(that|which)",
                r"(learn|discover|find)\s+(how|what|why|when)"
            ],
            
            # Problem-Solution Patterns
            "problem_solution": [
                r"(problem|issue|challenge)\s+(was|is|that)",
                r"(solution|answer|fix)\s+(is|was|came|found)",
                r"(struggled|failed|tried)\s+(but|until|when)",
                r"(realized|discovered|figured)\s+(out|that)",
                r"(turned|changed|transformed)\s+(everything|it|around)"
            ],
            
            # Specific Business/Entrepreneurship
            "business_essence": [
                r"(saas|software|app|product|service)\s+(that|which)",
                r"(customer|client|user)\s+(acquisition|retention|satisfaction)",
                r"(marketing|advertising|promotion)\s+(strategy|campaign|method)",
                r"(pricing|monetization|revenue)\s+(model|strategy|approach)",
                r"(team|hiring|recruitment)\s+(process|strategy|method)"
            ]
        }
        
        # 🔄 SENTENCE BOUNDARY MARKERS
        self.sentence_endings = r'[.!?]+\s*$'
        self.strong_pause_markers = r'[.!?]\s+$'
        
        # 🚫 CONTINUATION WORDS - These indicate mid-sentence starts
        self.continuation_indicators = [
            "and", "but", "or", "so", "then", "also", "too", "plus",
            "because", "since", "while", "when", "where", "which", "that",
            "however", "although", "though", "yet", "still", "even",
            "furthermore", "moreover", "additionally", "besides"
        ]
        
        # ⚠️ WEAK ENDINGS - Don't start clips after these
        self.weak_endings = [
            "the", "a", "an", "and", "but", "or", "so", "then",
            "he", "she", "it", "they", "we", "you", "i", "this", "these", "those"
        ]
    
    def detect_video_essence(self, full_transcript):
        """
        🎯 DETECT THE MAIN ESSENCE/IDEA OF THE VIDEO
        Returns the most important themes and patterns found
        """
        essence_scores = {}
        transcript_lower = full_transcript.lower()
        
        # Score each essence category
        for category, patterns in self.essence_patterns.items():
            score = 0
            matches = []
            
            for pattern in patterns:
                matches_found = re.findall(pattern, transcript_lower)
                if matches_found:
                    score += len(matches_found) * 2  # Weight by frequency
                    matches.extend(matches_found)
            
            if score > 0:
                essence_scores[category] = {
                    "score": score,
                    "matches": matches[:5],  # Top 5 matches
                    "patterns": patterns
                }
        
        # Sort by score to find the main essence
        sorted_essence = sorted(essence_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return {
            "main_essence": sorted_essence[0] if sorted_essence else None,
            "all_essences": essence_scores,
            "transcript_length": len(full_transcript)
        }
    
    def find_essence_rich_segments(self, sentence_segments, essence_data):
        """
        🎯 FIND SEGMENTS THAT CONTAIN THE VIDEO'S ESSENCE/GOLD KNOWLEDGE
        Prioritize these for clip selection
        """
        if not essence_data or not essence_data.get("main_essence"):
            return []
        
        essence_category, essence_info = essence_data["main_essence"]
        patterns = essence_info["patterns"]
        
        essence_segments = []
        
        for i, segment in enumerate(sentence_segments):
            text = segment["text"].lower()
            essence_score = 0
            
            # Check if this segment contains essence patterns
            for pattern in patterns:
                if re.search(pattern, text):
                    essence_score += 3  # High weight for essence content
            
            if essence_score > 0:
                essence_segments.append({
                    "index": i,
                    "segment": segment,
                    "essence_score": essence_score,
                    "category": essence_category
                })
        
        # Sort by essence score
        essence_segments.sort(key=lambda x: x["essence_score"], reverse=True)
        return essence_segments
    
    def group_words_into_sentences(self, word_segments):
        """
        Group word-level segments into proper sentence chunks
        This solves the core problem of working with individual words
        """
        if not word_segments:
            return []
        
        sentence_groups = []
        current_sentence = []
        
        for i, segment in enumerate(word_segments):
            text = segment["text"].strip()
            current_sentence.append(segment)
            
            # Check if this word ends a sentence
            if self.is_sentence_ending_word(text):
                # Look ahead to confirm this is really a sentence end
                if self.confirm_sentence_boundary(word_segments, i):
                    # Create sentence group
                    sentence_group = self.create_sentence_group(current_sentence)
                    if sentence_group:
                        sentence_groups.append(sentence_group)
                    current_sentence = []
        
        # Handle remaining words (incomplete sentence at end)
        if current_sentence:
            sentence_group = self.create_sentence_group(current_sentence)
            if sentence_group:
                sentence_groups.append(sentence_group)
        
        # Debug logging
        print(f"📝 GROUPED {len(word_segments)} WORDS INTO {len(sentence_groups)} SENTENCES:", file=sys.stderr)
        for i, group in enumerate(sentence_groups):
            print(f"   Sentence {i}: \"{group['text']}\" ({group['start']:.1f}s - {group['end']:.1f}s)", file=sys.stderr)
        
        return sentence_groups
    
    def create_sentence_group(self, word_segments):
        """Create a sentence group from word segments"""
        if not word_segments:
            return None
        
        # Combine all text
        full_text = " ".join(seg["text"].strip() for seg in word_segments)
        
        # Calculate timing
        start_time = word_segments[0]["start"]
        end_time = word_segments[-1]["end"]
        
        return {
            "start": start_time,
            "end": end_time,
            "text": full_text.strip(),
            "word_count": len(word_segments),
            "words": word_segments
        }
    
    def is_sentence_ending_word(self, text):
        """Check if a word ends with sentence punctuation"""
        return bool(re.search(self.sentence_endings, text))
    
    def confirm_sentence_boundary(self, segments, current_index):
        """Confirm this is actually a sentence boundary by looking ahead"""
        # If this is the last segment, it's definitely a boundary
        if current_index >= len(segments) - 1:
            return True
        
        # Look at the next segment
        next_segment = segments[current_index + 1]
        next_text = next_segment["text"].strip()
        
        # If next segment starts with capital letter, likely new sentence
        if next_text and next_text[0].isupper():
            return True
        
        # If next segment starts with continuation word, not a boundary
        next_lower = next_text.lower()
        if any(next_lower.startswith(word + " ") for word in self.continuation_indicators):
            return False
        
        return True
    
    def find_optimal_clip_start(self, sentence_segments, center_index, search_range=10, essence_data=None):
        """
        🎯 FIND THE OPTIMAL STARTING POINT - PRIORITIZING PERFECT BEGINNINGS
        Now with essence detection and enhanced logging
        """
        best_start_idx = center_index
        best_score = 0
        best_reason = "default center point"
        
        # Search backwards from center point for better starting points
        start_search = max(0, center_index - search_range)
        
        print(f"🔍 SEARCHING FOR PERFECT CLIP START:", file=sys.stderr)
        print(f"   📍 Center index: {center_index}", file=sys.stderr)
        print(f"   🔍 Search range: {start_search} to {center_index}", file=sys.stderr)
        
        for i in range(center_index, start_search - 1, -1):
            if i >= len(sentence_segments):
                continue
                
            sentence = sentence_segments[i]
            text = sentence["text"].strip()
            
            # Calculate start quality score
            score = self.calculate_start_quality_score(text)
            reason = self.get_start_reason(text)
            
            # 🎯 ESSENCE BONUS: If this segment contains the video's essence, boost score
            if essence_data and essence_data.get("main_essence"):
                essence_category, essence_info = essence_data["main_essence"]
                if self.segment_contains_essence(text, essence_info["patterns"]):
                    score += 15  # Significant boost for essence content
                    reason += " + ESSENCE CONTENT"
            
            # Prefer starting points that are closer to center but with good structure
            distance_penalty = (center_index - i) * 0.3  # Reduced penalty to prioritize quality
            final_score = score - distance_penalty
            
            # Log each potential start point
            print(f"   📝 Index {i}: \"{text[:50]}{'...' if len(text) > 50 else ''}\"", file=sys.stderr)
            print(f"      Score: {final_score:.1f} (base: {score:.1f}, penalty: {distance_penalty:.1f})", file=sys.stderr)
            print(f"      Reason: {reason}", file=sys.stderr)
            
            if final_score > best_score:
                best_score = final_score
                best_start_idx = i
                best_reason = reason
        
        # 🎯 FINAL LOGGING - Show the chosen start
        chosen_text = sentence_segments[best_start_idx]["text"].strip()
        print(f"✅ CHOSEN CLIP START:", file=sys.stderr)
        print(f"   📍 Index: {best_start_idx}", file=sys.stderr)
        print(f"   🎯 Score: {best_score:.1f}", file=sys.stderr)
        print(f"   📝 Text: \"{chosen_text}\"", file=sys.stderr)
        print(f"   💡 Reason: {best_reason}", file=sys.stderr)
        print(f"   ⏰ Time: {sentence_segments[best_start_idx]['start']:.1f}s", file=sys.stderr)
        
        return best_start_idx
    
    def segment_contains_essence(self, text, patterns):
        """Check if a text segment contains essence patterns"""
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def get_start_reason(self, text):
        """Get the reason why this text makes a good start"""
        text_lower = text.lower().strip()
        
        # Check structured beginnings
        for category, patterns in self.structured_beginnings.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return f"STRUCTURED: {category.replace('_', ' ').title()}"
        
        # Check if it's a proper sentence start
        if text and text[0].isupper():
            first_word = text.split()[0].lower() if text.split() else ""
            if first_word not in self.continuation_indicators:
                return "PROPER SENTENCE START"
            else:
                return "CONTINUATION WORD (avoid)"
        
        return "UNKNOWN"
    
    def calculate_start_quality_score(self, text):
        """
        Calculate how good this text is as a clip starting point
        Enhanced with better pattern recognition
        """
        if not text:
            return -10
        
        text_lower = text.lower().strip()
        score = 0
        
        # 🎯 STRUCTURED CONTENT BONUS (Highest Priority)
        for category, patterns in self.structured_beginnings.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if category in ["numbered_points", "question_hooks"]:
                        score += 15  # Highest priority
                    elif category in ["instructional_starts", "story_hooks"]:
                        score += 12
                    else:
                        score += 8
                    break  # Only count first match per category
        
        # ✅ PROPER SENTENCE START
        if text and text[0].isupper():
            first_word = text.split()[0].lower() if text.split() else ""
            
            # Penalize continuation words heavily
            if first_word in self.continuation_indicators:
                score -= 20  # Heavy penalty for mid-sentence starts
            else:
                score += 5  # Bonus for proper sentence start
        
        # 📏 LENGTH BONUS - Prefer substantial content
        word_count = len(text.split())
        if 5 <= word_count <= 20:
            score += 3  # Sweet spot for viral clips
        elif word_count < 3:
            score -= 5  # Too short
        
        # 🚫 PENALIZE WEAK ENDINGS
        if text_lower.endswith(tuple(self.weak_endings)):
            score -= 8
        
        return score
    
    def find_optimal_clip_end(self, sentence_segments, start_idx, target_duration, max_search=15):
        """
        Find the optimal ending point that maintains sentence integrity
        """
        best_end_idx = start_idx
        best_score = 0
        
        max_search_idx = min(len(sentence_segments), start_idx + max_search)
        
        print(f"🔍 SEARCHING FOR CLIP END:", file=sys.stderr)
        print(f"   📍 Start index: {start_idx}", file=sys.stderr)
        print(f"   🎯 Target duration: {target_duration}s", file=sys.stderr)
        print(f"   🔍 Search range: {start_idx + 1} to {max_search_idx}", file=sys.stderr)
        
        for i in range(start_idx + 1, max_search_idx):
            sentence = sentence_segments[i]
            
            # Calculate duration so far
            current_duration = sentence["end"] - sentence_segments[start_idx]["start"]
            
            # Calculate end quality score
            score = self.calculate_end_quality_score(sentence["text"], current_duration, target_duration)
            
            print(f"   📝 Index {i}: \"{sentence['text'][:50]}{'...' if len(sentence['text']) > 50 else ''}\"", file=sys.stderr)
            print(f"      Duration: {current_duration:.1f}s, Score: {score:.1f}", file=sys.stderr)
            
            # Accept if we have a reasonable duration and good score
            if current_duration >= target_duration - 5 and score > best_score:
                best_score = score
                best_end_idx = i
            elif current_duration >= target_duration - 10 and best_end_idx == start_idx:
                # If we haven't found a good end yet, accept this one
                best_score = score
                best_end_idx = i
        
        print(f"✅ CHOSEN CLIP END:", file=sys.stderr)
        print(f"   📍 Index: {best_end_idx}", file=sys.stderr)
        print(f"   🎯 Score: {best_score:.1f}", file=sys.stderr)
        print(f"   📝 Text: \"{sentence_segments[best_end_idx]['text']}\"", file=sys.stderr)
        print(f"   ⏰ Duration: {sentence_segments[best_end_idx]['end'] - sentence_segments[start_idx]['start']:.1f}s", file=sys.stderr)
        
        return best_end_idx
    
    def calculate_end_quality_score(self, text, current_duration, target_duration):
        """Calculate how good this text is as a clip ending point"""
        score = 0
        
        # 🎯 DURATION PREFERENCE
        duration_diff = abs(current_duration - target_duration)
        
        if duration_diff <= 2:
            score += 10  # Perfect duration
        elif duration_diff <= 5:
            score += 7   # Good duration
        elif duration_diff <= 8:
            score += 4   # Acceptable duration
        else:
            score -= 2   # Too far from target
        
        # 📝 ENDING QUALITY
        text_lower = text.lower().strip()
        
        # Ends with strong punctuation
        if re.search(r'[.!?]\s*$', text):
            score += 3
        
        # Complete thought indicators
        complete_endings = [
            "that's it", "done", "finished", "complete", "final", "end",
            "conclusion", "summary", "basically", "essentially", "ultimately"
        ]
        
        if any(ending in text_lower for ending in complete_endings):
            score += 2
        
        # 🚫 PENALTIES FOR BAD ENDINGS
        # Ends with weak words
        words = text_lower.split()
        if words and words[-1] in self.weak_endings:
            score -= 3
        
        # Ends with continuation words
        if any(text_lower.endswith(" " + word) for word in self.continuation_indicators):
            score -= 5
        
        return score
    
    def validate_clip_boundaries(self, sentence_segments, start_idx, end_idx):
        """
        Final validation that the clip boundaries create a coherent clip
        """
        if start_idx >= end_idx or start_idx >= len(sentence_segments) or end_idx >= len(sentence_segments):
            print(f"❌ Invalid indices: start={start_idx}, end={end_idx}, total={len(sentence_segments)}", file=sys.stderr)
            return False
        
        # Get full clip text
        clip_sentences = sentence_segments[start_idx:end_idx + 1]
        full_text = " ".join(s["text"] for s in clip_sentences)
        
        print(f"🔍 VALIDATING CLIP:", file=sys.stderr)
        print(f"   📝 Full text: \"{full_text}\"", file=sys.stderr)
        print(f"   📊 Word count: {len(full_text.split())}", file=sys.stderr)
        print(f"   ⏰ Duration: {clip_sentences[-1]['end'] - clip_sentences[0]['start']:.1f}s", file=sys.stderr)
        
        # Must have substantial content
        if len(full_text.split()) < 8:
            print(f"❌ Too short: {len(full_text.split())} words", file=sys.stderr)
            return False
        
        # Must start properly
        if not full_text or not full_text[0].isupper():
            print(f"❌ Doesn't start with capital: '{full_text[:10]}...'", file=sys.stderr)
            return False
        
        # Must end properly
        if not re.search(r'[.!?]\s*$', full_text):
            print(f"❌ Doesn't end with punctuation: '{full_text[-10:]}'", file=sys.stderr)
            return False
        
        # Duration check
        duration = clip_sentences[-1]["end"] - clip_sentences[0]["start"]
        if duration < 5 or duration > 60:  # Reasonable duration bounds
            print(f"❌ Duration out of bounds: {duration:.1f}s", file=sys.stderr)
            return False
        
        print(f"✅ CLIP VALIDATION PASSED", file=sys.stderr)
        return True
    
    def create_enhanced_clip_boundaries(self, word_segments, center_word_index, target_duration=30, essence_data=None):
        """
        🎯 MAIN FUNCTION: Create enhanced clip boundaries that start at proper sentence beginnings
        This addresses the user's core complaint about mid-sentence starts
        NOW WITH: Video essence detection and perfect beginning prioritization
        """
        try:
            # Step 1: Group words into sentences
            sentence_segments = self.group_words_into_sentences(word_segments)
            
            if not sentence_segments:
                return None
            
            # Step 2: Find which sentence contains our center word
            center_sentence_idx = self.find_sentence_containing_word(sentence_segments, word_segments, center_word_index)
            
            if center_sentence_idx is None:
                center_sentence_idx = len(sentence_segments) // 2
            
            # Step 3: Find optimal starting sentence (prioritizing structured beginnings + essence)
            start_idx = self.find_optimal_clip_start(sentence_segments, center_sentence_idx, essence_data=essence_data)
            
            # Step 4: Find optimal ending sentence
            end_idx = self.find_optimal_clip_end(sentence_segments, start_idx, target_duration)
            
            # Step 5: Validate boundaries
            if not self.validate_clip_boundaries(sentence_segments, start_idx, end_idx):
                return None
            
            # Step 6: Create final clip data
            clip_sentences = sentence_segments[start_idx:end_idx + 1]
            
            # 🎯 ENHANCED LOGGING - Show exactly what the clip starts with
            start_text = clip_sentences[0]["text"].strip()
            print(f"🎬 FINAL CLIP BOUNDARIES:", file=sys.stderr)
            print(f"   📍 Start: {clip_sentences[0]['start']:.1f}s", file=sys.stderr)
            print(f"   📍 End: {clip_sentences[-1]['end']:.1f}s", file=sys.stderr)
            print(f"   📍 Duration: {clip_sentences[-1]['end'] - clip_sentences[0]['start']:.1f}s", file=sys.stderr)
            print(f"   📝 CLIP STARTS WITH: \"{start_text}\"", file=sys.stderr)
            print(f"   📊 Quality Score: {self.calculate_start_quality_score(start_text):.1f}", file=sys.stderr)
            
            return {
                "start": clip_sentences[0]["start"],
                "end": clip_sentences[-1]["end"],
                "text": " ".join(s["text"] for s in clip_sentences),
                "sentence_count": len(clip_sentences),
                "start_quality": self.calculate_start_quality_score(start_text),
                "end_quality": self.calculate_end_quality_score(
                    clip_sentences[-1]["text"], 
                    clip_sentences[-1]["end"] - clip_sentences[0]["start"],
                    target_duration
                ),
                "duration": clip_sentences[-1]["end"] - clip_sentences[0]["start"],
                "start_text": start_text  # Add the actual start text for verification
            }
            
        except Exception as e:
            print(f"[ERROR] Enhanced boundary detection failed: {e}", file=sys.stderr)
            return None
    
    def find_sentence_containing_word(self, sentence_segments, word_segments, word_index):
        """Find which sentence contains the given word index"""
        if word_index >= len(word_segments):
            return None
        
        target_word = word_segments[word_index]
        target_time = target_word["start"]
        
        for i, sentence in enumerate(sentence_segments):
            if sentence["start"] <= target_time <= sentence["end"]:
                return i
        
        return None


# Integration function to replace existing boundary detection
def find_enhanced_clip_boundaries_with_sentence_detection(segments, center_index, full_transcript, target_duration=30):
    """
    🎯 ENHANCED REPLACEMENT for existing boundary detection
    Solves the mid-sentence start problem by using intelligent sentence grouping
    NOW WITH: Video essence detection and perfect beginning prioritization
    """
    detector = EnhancedSentenceBoundaryDetector()
    
    # 🎯 STEP 1: DETECT VIDEO ESSENCE
    print(f"🎯 ANALYZING VIDEO ESSENCE:", file=sys.stderr)
    essence_data = detector.detect_video_essence(full_transcript)
    
    if essence_data and essence_data.get("main_essence"):
        essence_category, essence_info = essence_data["main_essence"]
        print(f"   🏆 MAIN ESSENCE: {essence_category.replace('_', ' ').title()}", file=sys.stderr)
        print(f"   📊 Score: {essence_info['score']}", file=sys.stderr)
        print(f"   🎯 Top matches: {essence_info['matches'][:3]}", file=sys.stderr)
    else:
        print(f"   ⚠️ No clear essence detected", file=sys.stderr)
    
    # 🎯 STEP 2: USE ENHANCED DETECTION WITH ESSENCE
    result = detector.create_enhanced_clip_boundaries(
        word_segments=segments,
        center_word_index=center_index,
        target_duration=target_duration,
        essence_data=essence_data
    )
    
    if result:
        print(f"🎉 [ENHANCED] Found structured clip start: '{result['text'][:50]}...' (quality: {result['start_quality']})", file=sys.stderr)
        return {
            'start': result['start'],
            'end': result['end'],
            'text': result['text'],
            'completeness_score': 8.0 + (result['start_quality'] / 10),
            'sentence_count': result['sentence_count'],
            'start_quality': result['start_quality'],
            'end_quality': result['end_quality'],
            'essence_data': essence_data
        }
    
    return None


if __name__ == "__main__":
    # Test the enhanced detector
    print("Enhanced Sentence Boundary Detector - Ready to fix mid-sentence clip starts!") 