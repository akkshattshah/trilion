#!/usr/bin/env python3
"""
ENHANCED Intelligent Clip Analyzer: VIRAL HOOK DETECTION SYSTEM
Creates clips with powerful hooks, complete thoughts, and maximum viral potential
PHASE 3: Bulletproof System with Enhanced Viral Detection + Enhanced Sentence Boundary Detection
"""
import re
import json
from enhanced_whisper import EnhancedWhisperProcessor
from enhanced_sentence_boundary_detector import find_enhanced_clip_boundaries_with_sentence_detection
import subprocess
from datetime import timedelta
import math
import sys

class ViralContentAnalyzer:
    def __init__(self):
        # ADVANCED VIRAL HOOK PATTERNS - Completely redesigned for maximum viral potential
        
        # RHETORICAL QUESTIONS - Extremely powerful viral hooks
        self.rhetorical_questions = [
            r"what if i told you",
            r"have you ever wondered (why|how|what)",
            r"did you know that",
            r"why do (people|we|they)",
            r"how is it possible",
            r"what would happen if",
            r"can you believe",
            r"is it just me or",
            r"am i the only one who",
            r"does anyone else"
        ]
        
        # FASCINATING FACTS - Very viral content
        self.fascinating_facts = [
            r"most people don't know",
            r"scientists discovered",
            r"the hidden truth about",
            r"here's what they don't tell you",
            r"the secret to",
            r"this will blow your mind",
            r"you won't believe what",
            r"the shocking truth",
            r"this changes everything",
            r"the real reason why"
        ]
        
        # HARD-HITTING STATEMENTS - Controversial viral content
        self.hard_hitting_statements = [
            r"everyone is wrong about",
            r"you've been lied to about",
            r"this will destroy",
            r"the biggest mistake",
            r"why everything you know is wrong",
            r"the uncomfortable truth",
            r"this is why you're failing",
            r"the harsh reality",
            r"what nobody wants to admit",
            r"the brutal truth about"
        ]
        
        # POWERFUL QUOTES - Authority viral content
        self.powerful_quotes = [
            r"as (.*?) said",
            r"according to (.*?)",
            r"(.*?) once said",
            r"the famous quote",
            r"this reminds me of",
            r"as the saying goes",
            r"there's a famous saying",
            r"this quote changed my life"
        ]

        # URGENCY PATTERNS - Time-sensitive viral content
        self.urgency_patterns = [
            r"before it's too late",
            r"this is your last chance",
            r"don't wait until",
            r"time is running out",
            r"you need to act now",
            r"this opportunity won't last",
            r"the clock is ticking",
            r"this is urgent"
        ]
        
        # CURIOSITY GAPS - Strong engagement
        self.curiosity_gaps = [
            r"you won't believe what happened next",
            r"here's where it gets crazy",
            r"plot twist",
            r"but then something unexpected",
            r"this is where it gets interesting",
            r"wait until you hear",
            r"the craziest part is",
            r"this will shock you"
        ]
        
        # PERSONAL STAKES - Personal relevance
        self.personal_stakes = [
            r"this could happen to you",
            r"your future depends on",
            r"this affects everyone",
            r"this is about you",
            r"your success depends on",
            r"this will change your life",
            r"you need to know this",
            r"this is personal"
        ]
        
        # AUTHORITY MARKERS - Credibility
        self.authority_markers = [
            r"research shows",
            r"studies prove",
            r"experts agree",
            r"science confirms",
            r"data reveals",
            r"statistics show",
            r"professionals say",
            r"the evidence is clear"
        ]
        
        # SHOCK PATTERNS - Surprising content
        self.shock_patterns = [
            r"this is insane",
            r"mind-blowing",
            r"unbelievable",
            r"shocking",
            r"crazy",
            r"wild",
            r"insane",
            r"outrageous"
        ]
        
        # EMOTIONAL TRIGGERS - Emotional engagement
        self.emotional_triggers = {
            "fear": ["scared", "afraid", "terrified", "panic", "danger", "threat", "risk"],
            "anger": ["angry", "furious", "outraged", "mad", "upset", "frustrated"],
            "curiosity": ["curious", "wonder", "mystery", "secret", "hidden", "unknown"],
            "excitement": ["excited", "thrilled", "amazing", "incredible", "awesome"],
            "surprise": ["surprised", "shocked", "stunned", "amazed", "wow"],
            "hope": ["hope", "dream", "future", "possibility", "potential", "opportunity"]
        }

    def analyze_transcript_for_viral_segments(self, transcript_text, segments, requested_clips=3, target_platform="tiktok", target_duration=30):
        """
        ENHANCED VIRAL ANALYSIS: Focus on powerful hooks and complete thoughts
        """
        print(f"[INFO] Analyzing {len(segments)} segments for viral content...", file=sys.stderr)
        print(f"[STRICT] Using ULTRA STRICT sentence boundary detection - zero tolerance for mid-sentence cuts", file=sys.stderr)
        
        # Phase 1: Find all segments with viral potential
        all_scored_segments = []
        rejected_count = 0
        boundary_rejected = 0
        
        for i, segment in enumerate(segments):
            text = segment["text"].strip()
            
            # Calculate ENHANCED viral score
            viral_score = self.calculate_viral_hook_score(text, transcript_text, target_platform)
            
            if viral_score > 0.1:  # Much lower threshold to find more viral content
                # Find natural clip boundaries with COMPLETE THOUGHTS
                clip_segment = self.find_complete_thought_boundaries(segments, i, transcript_text, target_duration)
                
                if clip_segment:
                    all_scored_segments.append({
                        'start_time': clip_segment['start'],
                        'end_time': clip_segment['end'],
                        'text': clip_segment['text'],
                        'viral_score': viral_score,
                        'hook_type': clip_segment['hook_type'],
                        'duration': clip_segment['end'] - clip_segment['start'],
                        'segment_index': i,
                        'completeness_score': clip_segment['completeness_score'],
                        'hook_strength': clip_segment['hook_strength'],
                        'emotional_impact': self.calculate_emotional_impact(clip_segment['text']),
                        'attention_score': self.calculate_attention_score(clip_segment['text'])
                    })
                else:
                    boundary_rejected += 1
                    print(f"[BOUNDARY] Rejected segment {i} - failed strict sentence boundary validation", file=sys.stderr)
            else:
                rejected_count += 1
        
        print(f"[INFO] Found {len(all_scored_segments)} segments with viral potential", file=sys.stderr)
        print(f"[STRICT] Rejected {boundary_rejected} segments for sentence boundary violations", file=sys.stderr)
        print(f"[STRICT] Rejected {rejected_count} segments for low viral scores", file=sys.stderr)
        
        # Phase 2: STRICT DURATION-FIRST SORTING - Duration is the #1 priority
        all_scored_segments = sorted(all_scored_segments, key=lambda x: (
            self.calculate_duration_preference(x['duration'], target_duration) * 0.60 +  # 60% weight for duration (PRIORITY #1)
            x['hook_strength'] * 0.20 +
            x['viral_score'] * 0.15 +
            x['completeness_score'] * 0.05
        ), reverse=True)
        
        # Phase 3: Remove overlapping segments (keep the best ones)
        viral_segments = self.remove_overlapping_segments_smart(all_scored_segments)
        print(f"[INFO] After removing overlaps: {len(viral_segments)} segments", file=sys.stderr)
            
        # Phase 4: FORCE DURATION - Cut clips to exact user duration
        final_clips = self.force_duration_clips(viral_segments, requested_clips, segments, target_duration)
            
        # Log the final selection for debugging
        for i, clip in enumerate(final_clips):
            boundary_status = "✅ STRICT BOUNDARIES" if not clip.get('is_fallback', False) else "⚠️ FALLBACK CLIP"
            print(f"[INFO] Clip {i+1}: {boundary_status}, score={clip['viral_score']:.2f}, hook={clip['hook_type']}, duration={clip['duration']:.1f}s", file=sys.stderr)
            print(f"[INFO] Hook strength={clip.get('hook_strength', 0):.2f}, Preview: {clip['text'][:100]}...", file=sys.stderr)
            print(f"[INFO] Selection method: {clip.get('selection_method', 'viral_analysis')}, Fallback: {clip.get('is_fallback', False)}", file=sys.stderr)
        
        return final_clips

    def calculate_viral_hook_score(self, text, full_transcript, target_platform="tiktok"):
        """
        ENHANCED viral scoring - More aggressive detection for better viral content
        """
        text_lower = text.lower()
        score = 0.0
        
        # RHETORICAL QUESTIONS (5.0 points - EXTREMELY viral)
        for pattern in self.rhetorical_questions:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 5.0
                break
        
        # FASCINATING FACTS (4.5 points - Very viral)
        for pattern in self.fascinating_facts:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 4.5
                break
        
        # HARD-HITTING STATEMENTS (4.0 points - Controversial viral)
        for pattern in self.hard_hitting_statements:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 4.0
                break
        
        # POWERFUL QUOTES (3.5 points - Authority viral)
        for pattern in self.powerful_quotes:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 3.5
                break
        
        # URGENCY PATTERNS (3.0 points - Time-sensitive viral)
        for pattern in self.urgency_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 3.0
                break
        
        # CURIOSITY GAPS (3.5 points - Strong engagement)
        for pattern in self.curiosity_gaps:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 3.5
                break
        
        # PERSONAL STAKES (3.0 points - Personal relevance)
        for pattern in self.personal_stakes:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 3.0
                break
        
        # AUTHORITY MARKERS (2.5 points - Credibility)
        for pattern in self.authority_markers:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 2.5
                break
        
        # SHOCK VALUE (2.0 points - Surprising content)
        for pattern in self.shock_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 2.0
                break
        
        # EMOTIONAL TRIGGERS (up to 3.0 points - Emotional engagement)
        emotion_score = 0
        for emotion_type, words in self.emotional_triggers.items():
            emotion_count = sum(1 for word in words if word in text_lower)
            if emotion_count > 0:
                if emotion_type in ["fear", "anger", "curiosity"]:
                    emotion_score += emotion_count * 0.8  # High-impact emotions
                else:
                    emotion_score += emotion_count * 0.5
        score += min(emotion_score, 3.0)
        
        # NUMBERS AND STATISTICS (1.5 points - Concrete data)
        number_patterns = [
            r"\d+%",
            r"\$\d+",
            r"\d+x (more|less|bigger|smaller)",
            r"\d+ (million|billion|thousand)",
            r"\d+ times",
            r"\d+ years",
            r"only \d+",
            r"just \d+"
        ]
        for pattern in number_patterns:
            if re.search(pattern, text_lower):
                score += 1.5
                break
        
        # ENHANCED: BROADER VIRAL PATTERNS (Lower threshold for more content)
        
        # ANY QUESTION (2.0 points - Questions are naturally engaging)
        if re.search(r"\?", text):
            score += 2.0
        
        # EXCLAMATION (1.5 points - Emotional emphasis)
        if re.search(r"!", text):
            score += 1.5
        
        # COMPARISONS (1.5 points - "vs", "versus", "compared to")
        comparison_words = ["vs", "versus", "compared to", "unlike", "different from", "same as"]
        if any(word in text_lower for word in comparison_words):
            score += 1.5
                
        # STORYTELLING MARKERS (1.0 points - Narrative hooks)
        story_words = ["story", "happened", "when", "then", "suddenly", "finally", "eventually"]
        if any(word in text_lower for word in story_words):
            score += 1.0
                
        # ADVICE/INSTRUCTION (1.0 points - Actionable content)
        advice_words = ["should", "need to", "must", "have to", "try", "do this", "avoid"]
        if any(word in text_lower for word in advice_words):
            score += 1.0
        
        # CONTRAST PATTERNS (1.5 points - "but", "however", "although")
        contrast_words = ["but", "however", "although", "despite", "even though", "while"]
        if any(word in text_lower for word in contrast_words):
            score += 1.5
        
        # PERSONAL PRONOUNS (0.5 points - Personal connection)
        personal_words = ["you", "your", "yourself", "i", "me", "my", "we", "our"]
        personal_count = sum(1 for word in personal_words if word in text_lower)
        score += min(personal_count * 0.3, 1.5)
        
        # LENGTH BONUS (0.5 points - Substantial content)
        if len(text.split()) >= 15:
            score += 0.5
        
        return score

    def find_complete_thought_boundaries(self, segments, center_index, full_transcript, target_duration=30):
        """
        🎯 ENHANCED ULTRA STRICT SENTENCE BOUNDARY detection - Now with intelligent sentence grouping
        ZERO tolerance for mid-sentence cuts - every clip is a complete thought
        """
        # Try enhanced sentence detection first
        enhanced_result = find_enhanced_clip_boundaries_with_sentence_detection(
            segments, center_index, full_transcript, target_duration
        )
        
        if enhanced_result:
            print(f"[SUCCESS] Enhanced detection found structured start: '{enhanced_result['text'][:100]}...'", file=sys.stderr)
            return {
                'start': enhanced_result['start'],
                'end': enhanced_result['end'],
                'text': enhanced_result['text'],
                'hook_type': self.identify_hook_type(enhanced_result['text']),
                'completeness_score': enhanced_result['completeness_score'],
                'hook_strength': self.calculate_hook_strength(enhanced_result['text'])
            }
        
        # Fallback to original ultra-strict logic
        print("[FALLBACK] Using original ultra-strict boundary detection", file=sys.stderr)
        start_idx = center_index
        end_idx = center_index
        
        # Phase 1: Find starting point that begins AFTER a sentence boundary (., ?, !)
        # ABSOLUTE REQUIREMENT: Must start after previous segment ended with . ! or ?
        found_valid_start = False
        for i in range(center_index, max(0, center_index - 20), -1):
            # STRICT CHECK: This segment must start after sentence boundary
            if not self.starts_after_sentence_boundary_strict(segments, i):
                continue
                
            text = segments[i]["text"].strip()
            
            # STRICT CHECK: Must start with capital letter (proper sentence start)
            if not text or not text[0].isupper():
                continue
                
            # STRICT CHECK: Cannot start with filler words or continuations
            if self.is_sentence_continuation(text):
                continue
                
            # Prioritize segments with powerful hooks that start after sentence boundaries
            if self.is_powerful_hook_start(text):
                start_idx = i
                found_valid_start = True
                break
            elif self.is_strong_sentence_start(text):
                start_idx = i
                found_valid_start = True
                # Keep looking for an even better hook start

        # If we can't find a valid sentence start, reject this clip
        if not found_valid_start:
            return None

        # Phase 2: Find ending point that ends WITH a sentence boundary (., ?, !)
        # ABSOLUTE REQUIREMENT: Must end with . ! or ?
        found_valid_end = False
        max_search_ahead = min(len(segments), start_idx + 30)
        
        for i in range(start_idx + 1, max_search_ahead):
            text = segments[i]["text"].strip()
            current_duration = segments[i]["end"] - segments[start_idx]["start"]
            
            # Minimum duration check - must be close to target duration
            if current_duration < target_duration - 5:
                continue
                
            # ABSOLUTE REQUIREMENT: Must end with sentence boundary
            if not self.ends_with_sentence_boundary_strict(text):
                continue
                
            # STRICT CHECK: Cannot end with incomplete thoughts or continuations
            if self.is_incomplete_sentence_ending(text):
                continue
                
            # ULTRA STRICT: Check if next segment continues this sentence
            if self.next_segment_continues_sentence(segments, i):
                continue
                
            # 🎯 STRICT DURATION ENFORCEMENT: User's duration is PRIORITY #1
            duration_diff = abs(current_duration - target_duration)
            
            # REJECT any clip that's more than 5 seconds off target
            if duration_diff > 5:
                continue
                
            # Perfect match: Within 2 seconds of target duration
            if duration_diff <= 2:
                end_idx = i
                found_valid_end = True
                break
                
            # Good match: Within 5 seconds of target duration
            elif duration_diff <= 5:
                end_idx = i
                found_valid_end = True
                # Continue looking for perfect match

        # If we can't find a valid sentence end, reject this clip
        if not found_valid_end:
            return None
        
        # Final validation - combine all text and validate complete thought
        clip_text = " ".join([seg["text"].strip() for seg in segments[start_idx:end_idx+1]])
        duration = segments[end_idx]["end"] - segments[start_idx]["start"]
        
        # ULTRA STRICT validation of the complete clip
        if not self.is_complete_sentence_clip(clip_text):
            return None
            
        # STRICT DURATION REQUIREMENTS: User's duration is absolute priority
        min_duration = target_duration - 3  # At least 3 seconds less than target
        max_duration = target_duration + 3  # At most 3 seconds more than target
        if duration < min_duration or duration > max_duration:
            return None
        
        # Calculate quality scores
        hook_type = self.identify_hook_type(clip_text)
        completeness_score = self.calculate_completeness_score(clip_text)
        hook_strength = self.calculate_hook_strength(clip_text)
        
        # Bonus for perfect sentence boundaries
        boundary_bonus = 1.0  # Full bonus for strict sentence boundaries
        
        return {
            'start': segments[start_idx]["start"],
            'end': segments[end_idx]["end"],
            'text': clip_text,
            'hook_type': hook_type,
            'completeness_score': completeness_score + boundary_bonus,
            'hook_strength': hook_strength
        }

    def starts_after_sentence_boundary_strict(self, segments, segment_index):
        """ULTRA STRICT: Check if this segment starts after previous ended with . ! or ?"""
        # First segment always counts as starting after a boundary
        if segment_index == 0:
            return True
        
        # Check if the previous segment ended with sentence boundary
        previous_segment = segments[segment_index - 1]
        previous_text = previous_segment["text"].strip()
        
        # STRICT: Must end with . ! or ? (no other punctuation accepted)
        return self.ends_with_sentence_boundary_strict(previous_text)

    def ends_with_sentence_boundary_strict(self, text):
        """ULTRA STRICT: Text must end with . ! or ? only"""
        text = text.strip()
        # Only accept proper sentence endings
        return re.search(r'[.!?]\s*$', text) is not None

    def is_sentence_continuation(self, text):
        """Detect if text is continuing a previous sentence (should be rejected)"""
        text_lower = text.lower().strip()
        
        # Common continuation words that indicate mid-sentence start
        continuation_words = [
            "and", "but", "or", "so", "then", "also", "too", "as well", 
            "because", "since", "while", "when", "where", "which", "that",
            "however", "although", "though", "yet", "still", "even",
            "plus", "besides", "furthermore", "moreover", "additionally"
        ]
        
        # Check if starts with continuation word
        for word in continuation_words:
            if text_lower.startswith(word + " "):
                return True
                
        # Check for lowercase start (often indicates continuation)
        if text and text[0].islower():
            return True
            
        return False

    def is_incomplete_sentence_ending(self, text):
        """Detect incomplete sentence endings that should be rejected"""
        text = text.strip().lower()
        
        # Incomplete endings that suggest continuation
        incomplete_endings = [
            "and", "but", "or", "so", "then", "because", "since", "while",
            "when", "where", "which", "that", "the", "a", "an", "he", "she", 
            "it", "they", "we", "you", "i", "this", "these", "those"
        ]
        
        # Remove punctuation to check the actual last word
        text_clean = re.sub(r'[.!?]\s*$', '', text).strip()
        last_word = text_clean.split()[-1] if text_clean.split() else ""
        
        return last_word in incomplete_endings

    def next_segment_continues_sentence(self, segments, current_index):
        """Check if the next segment continues the current sentence"""
        if current_index + 1 >= len(segments):
            return False
            
        next_segment = segments[current_index + 1]["text"].strip()
        
        # If next segment doesn't exist or is empty, no continuation
        if not next_segment:
            return False
            
        # If next segment starts with lowercase, likely continuation
        if next_segment[0].islower():
            return True
            
        # Check for continuation words at start of next segment
        continuation_starters = [
            "and", "but", "or", "so", "then", "because", "since", "while",
            "however", "although", "though", "yet", "still", "also", "too"
        ]
        
        next_lower = next_segment.lower()
        for starter in continuation_starters:
            if next_lower.startswith(starter + " "):
                return True
                
        return False

    def is_complete_sentence_clip(self, clip_text):
        """ULTRA STRICT validation that the entire clip is a complete sentence/thought"""
        text = clip_text.strip()
        
        # Must start with capital letter
        if not text or not text[0].isupper():
            return False
            
        # Must end with sentence punctuation
        if not re.search(r'[.!?]\s*$', text):
            return False
            
        # Cannot start with continuation words
        if self.is_sentence_continuation(text):
            return False
            
        # Cannot end with incomplete words
        if self.is_incomplete_sentence_ending(text):
            return False
            
        # Must be substantial (minimum word count for complete thought)
        words = text.split()
        if len(words) < 8:  # At least 8 words for a complete thought
            return False
            
        # Check for obvious incomplete patterns
        incomplete_patterns = [
            r'\.\.\.$',  # Ends with ellipsis
            r'\b(he|she|it|they|we|you|i|the|a|an)\s*[.!?]\s*$',  # Ends with article/pronoun
            r'\b(and|but|or|so|then|because|since|while)\s*[.!?]\s*$',  # Ends with conjunction
        ]
        
        for pattern in incomplete_patterns:
            if re.search(pattern, text.lower()):
                return False
                
        # Must contain at least one verb (basic sentence structure check)
        common_verbs = [
            "is", "are", "was", "were", "am", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "can", "could", "should", "shall", "may", "might", "must",
            "go", "goes", "went", "gone", "get", "gets", "got", "gotten",
            "make", "makes", "made", "take", "takes", "took", "taken",
            "see", "sees", "saw", "seen", "know", "knows", "knew", "known",
            "think", "thinks", "thought", "say", "says", "said", "tell",
            "come", "comes", "came", "want", "wants", "wanted", "need",
            "like", "likes", "liked", "work", "works", "worked", "try",
            "find", "finds", "found", "give", "gives", "gave", "given",
            "use", "uses", "used", "feel", "feels", "felt", "become",
            "leave", "leaves", "left", "put", "puts", "mean", "means", "meant"
        ]
        
        text_lower = text.lower()
        has_verb = any(f" {verb} " in f" {text_lower} " or 
                      text_lower.startswith(f"{verb} ") or 
                      text_lower.endswith(f" {verb}") for verb in common_verbs)
        
        if not has_verb:
            return False
            
        return True

    def is_powerful_hook_start(self, text):
        """Detect text that starts with a powerful viral hook"""
        text_lower = text.lower().strip()
        
        # Question hooks
        if re.match(r"^(what if|did you know|have you ever|why do|how is|what would)", text_lower):
            return True
        
        # Fact hooks
        if re.match(r"^(most people don't|scientists discovered|the hidden truth|here's what)", text_lower):
            return True
        
        # Controversial hooks
        if re.match(r"^(everyone is wrong|you've been lied to|this will destroy|the biggest mistake)", text_lower):
            return True
        
        # Authority hooks
        if re.match(r"^(research shows|studies prove|experts agree|science confirms)", text_lower):
            return True
            
        return False

    def is_strong_sentence_start(self, text):
        """Detect text that starts with a strong sentence"""
        text = text.strip()
        
        # Must start with capital letter
        if not text or not text[0].isupper():
            return False
        
        # Must be substantial (not just filler words)
        filler_words = ["um", "uh", "so", "well", "like", "you know", "i mean"]
        text_lower = text.lower()
        
        for filler in filler_words:
            if text_lower.startswith(filler + " "):
                return False
        
        return True
        
    def is_complete_thought_end(self, text):
        """Detect complete thought endings - ENHANCED for natural pauses"""
        text = text.strip()
        text_lower = text.lower()
        
        # MUST end with sentence boundary (., ?, !)
        if not re.search(r"[.!?]\s*$", text):
            return False
        
        # ULTRA STRONG conclusion phrases that indicate complete thoughts
        ultra_strong_conclusions = [
            "that's why", "which is why", "in conclusion", "the point is", 
            "the bottom line", "to summarize", "that's it", "that's all", 
            "end of story", "period", "that's the truth", "that's the reality",
            "that's exactly what", "that's precisely why", "that's the whole point",
            "and that's how", "and that's what", "and that's when", "and that's where",
            "so there you have it", "so that's the deal", "so that's basically it"
        ]
        
        # Natural pause indicators
        pause_indicators = [
            "but", "however", "although", "though", "yet", "still", "nevertheless",
            "meanwhile", "furthermore", "moreover", "additionally", "also",
            "first", "second", "third", "finally", "lastly", "in addition",
            "on the other hand", "on the flip side", "conversely"
        ]
        
        # Check for ultra strong conclusion phrases
        if any(phrase in text_lower for phrase in ultra_strong_conclusions):
            return True
            
        # Check for natural pause points (but only if they end the sentence)
        if any(indicator in text_lower for indicator in pause_indicators):
            # Make sure the pause indicator is at the end or followed by conclusion
            for indicator in pause_indicators:
                if indicator in text_lower:
                    # Check if it's at the end or followed by a conclusion
                    indicator_pos = text_lower.find(indicator)
                    if indicator_pos > len(text_lower) - len(indicator) - 10:  # Near the end
                        return True
        
        # Question endings that create cliff-hangers
        if re.search(r"\?\s*$", text):
            return True
        
        # Exclamation endings with impact
        if re.search(r"!\s*$", text):
            impact_words = ["amazing", "incredible", "shocking", "wow", "unbelievable", 
                          "crazy", "insane", "mind-blowing", "outrageous", "wild"]
            if any(word in text_lower for word in impact_words):
                return True
        
        # Check for complete sentence structure (subject-verb-object)
        words = text.split()
        if len(words) >= 5:  # Minimum sentence length
            # Look for common sentence endings
            ending_patterns = [
                r"\b(so|therefore|thus|hence|consequently)\b",
                r"\b(and|or|but)\s+that's\b",
                r"\b(this|that|it)\s+is\b",
                r"\b(here|there)\s+you\s+go\b",
                r"\b(that's|here's)\s+(it|all|why|how|what)\b"
            ]
            
            for pattern in ending_patterns:
                if re.search(pattern, text_lower):
                    return True
            
        return False

    def is_natural_pause_point(self, text):
        """Detect STRONG natural pause points in speech - ULTRA STRICT"""
        text = text.strip()
        text_lower = text.lower()
        
        # MUST end with sentence boundary
        if not re.search(r"[.!?]\s*$", text):
            return False
        
        # STRONG topic transition indicators (clear breaks in conversation)
        strong_transitions = [
            "now", "next", "moving on", "let's talk about", "speaking of", 
            "anyway", "alright", "ok", "okay", "so", "well"
        ]
        
        # STRONG pause indicators that suggest breath/thought break
        strong_pauses = [
            "but", "however", "although", "meanwhile", "nevertheless",
            "on the other hand", "conversely", "instead", "actually", "in fact"
        ]
        
        # List conclusion indicators
        list_conclusions = [
            "finally", "lastly", "in conclusion", "to summarize", "bottom line"
        ]
        
        # Strong emphasis/conclusion endings
        strong_endings = [
            "period", "end of story", "that's it", "that's all", "simple as that",
            "you know what i mean", "if you know what i mean", "that's the point",
            "that's what i'm saying", "that's what i'm talking about"
        ]
        
        # Check for strong transitions (must be near the end of the sentence)
        for transition in strong_transitions:
            if transition in text_lower:
                # Check if it's in the last 15 characters of the sentence
                transition_pos = text_lower.rfind(transition)
                if transition_pos > len(text_lower) - 20:
                    return True
        
        # Check for strong pause indicators
        for pause in strong_pauses:
            if pause in text_lower:
                # Must be significant part of the ending
                pause_pos = text_lower.rfind(pause)
                if pause_pos > len(text_lower) - 25:
                    return True
            
        # Check for list conclusions
        if any(conclusion in text_lower for conclusion in list_conclusions):
            return True
        
        # Check for strong emphasis endings
        if any(ending in text_lower for ending in strong_endings):
            return True
        
        # Questions ALWAYS create natural pauses
        if re.search(r"\?\s*$", text):
            return True
        
        # Exclamations with strong emotional words
        if re.search(r"!\s*$", text):
            emotional_words = ["wow", "amazing", "incredible", "unbelievable", "crazy", "insane", "right"]
            if any(word in text_lower for word in emotional_words):
                return True
        
        # Time-based transitions
        time_transitions = ["then", "after that", "following that", "next", "later", "afterwards"]
        if any(transition in text_lower for transition in time_transitions):
            # Check if it's at the end
            for transition in time_transitions:
                if text_lower.endswith(transition + ".") or text_lower.endswith(transition + "!"):
                    return True
            
        return False

    def is_sentence_boundary(self, text):
        """Check if text ends at sentence boundary (., ?, !) - STRICT"""
        text = text.strip()
        # Only allow sentence-ending punctuation, NOT commas or other punctuation
        return re.search(r"[.!?]\s*$", text) is not None

    def starts_after_sentence_boundary(self, segments, segment_index):
        """Check if this segment starts after the previous segment ended with a sentence boundary"""
        # First segment always counts as starting after a boundary
        if segment_index == 0:
            return True
        
        # Check if the previous segment ended with sentence boundary
        previous_segment = segments[segment_index - 1]
        previous_text = previous_segment["text"].strip()
        
        return self.is_sentence_boundary(previous_text)

    def calculate_completeness_score(self, text):
        """Calculate how complete and coherent the thought is"""
        score = 0.0
        text_lower = text.lower()
        
        # Has clear beginning and end
        if re.search(r"^[A-Z]", text) and re.search(r"[.!?]\s*$", text):
            score += 2.0
        
        # Contains complete thoughts
        if len(text.split()) >= 10:
            score += 1.0
        
        # Has logical flow indicators
        flow_words = ["because", "therefore", "however", "although", "but", "so", "then"]
        flow_count = sum(1 for word in flow_words if word in text_lower)
        score += min(flow_count * 0.5, 2.0)
        
        # Has emotional impact
        emotion_words = ["amazing", "incredible", "shocking", "wow", "unbelievable", "crazy"]
        emotion_count = sum(1 for word in emotion_words if word in text_lower)
        score += min(emotion_count * 0.3, 1.0)
        
        return score
        
    def calculate_hook_strength(self, text):
        """Calculate the strength of the viral hook"""
        text_lower = text.lower()
        score = 0.0
        
        # Rhetorical questions are extremely powerful
        if re.search(r"\?", text):
            score += 3.0
        
        # Fascinating facts
        fact_indicators = ["most people don't know", "scientists discovered", "the hidden truth", "you won't believe"]
        if any(indicator in text_lower for indicator in fact_indicators):
            score += 2.5
        
        # Controversial statements
        controversy_indicators = ["everyone is wrong", "you've been lied to", "this will destroy", "the biggest mistake"]
        if any(indicator in text_lower for indicator in controversy_indicators):
            score += 2.0
        
        # Authority markers
        authority_indicators = ["research shows", "studies prove", "experts agree", "science confirms"]
        if any(indicator in text_lower for indicator in authority_indicators):
            score += 1.5
        
        # Numbers and statistics
        if re.search(r"\d+", text):
            score += 1.0
        
        return score

    def calculate_emotional_impact(self, text):
        """Calculate emotional impact of the content"""
        text_lower = text.lower()
        score = 0.0
        
        # High-impact emotions
        high_impact = ["fear", "anger", "curiosity", "surprise", "shock"]
        for emotion in high_impact:
            if emotion in text_lower:
                score += 1.0
        
        # Medium-impact emotions
        medium_impact = ["excitement", "hope", "joy", "sadness", "frustration"]
        for emotion in medium_impact:
            if emotion in text_lower:
                score += 0.5
        
        # Exclamation marks add emotional emphasis
        exclamation_count = text.count("!")
        score += min(exclamation_count * 0.3, 1.0)
        
        return score

    def calculate_attention_score(self, text):
        """Calculate attention-grabbing potential"""
        text_lower = text.lower()
        score = 0.0
        
        # Questions grab attention
        if "?" in text:
            score += 1.0
        
        # Exclamations create urgency
        if "!" in text:
            score += 0.8
        
        # Personal pronouns create connection
        personal_words = ["you", "your", "yourself", "i", "me", "my", "we", "our"]
        personal_count = sum(1 for word in personal_words if word in text_lower)
        score += min(personal_count * 0.2, 1.0)
        
        # Numbers and statistics are attention-grabbing
        if re.search(r"\d+", text):
            score += 0.5
        
        return score

    def calculate_duration_preference(self, duration, target_duration=30):
        """Calculate preference score based on duration (prefer user's target duration)"""
        # Perfect duration is the user's requested duration
        target_duration = float(target_duration)
        
        # Calculate how close we are to the target
        duration_diff = abs(duration - target_duration)
        
        # STRICT scoring based on proximity to user's target
        if duration_diff <= 1:  # Within 1 second: perfect
            return 100.0
        elif duration_diff <= 2:  # Within 2 seconds: excellent
            return 80.0
        elif duration_diff <= 3:  # Within 3 seconds: good
            return 60.0
        elif duration_diff <= 5:  # Within 5 seconds: acceptable
            return 30.0
        else:  # More than 5 seconds off: reject
            return 0.0

    def identify_hook_type(self, text):
        """Identify the type of viral hook used"""
        text_lower = text.lower()
        
        if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.rhetorical_questions):
            return "rhetorical_question"
        elif any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.fascinating_facts):
            return "fascinating_fact"
        elif any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.hard_hitting_statements):
            return "hard_hitting"
        elif any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.curiosity_gaps):
            return "curiosity_gap"
        elif any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.urgency_patterns):
            return "urgency"
        elif any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.personal_stakes):
            return "personal_stakes"
        else:
            return "general"

    def remove_overlapping_segments_smart(self, segments):
        """Remove overlapping segments, keeping the best ones"""
        if not segments:
            return []
        
        # Sort by quality score
        segments = sorted(segments, key=lambda x: x['viral_score'], reverse=True)
        
        non_overlapping = []
        for segment in segments:
            overlaps = False
            for existing in non_overlapping:
                # Check for overlap
                if not (segment['end_time'] <= existing['start_time'] or 
                       segment['start_time'] >= existing['end_time']):
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append(segment)
        
        return non_overlapping

    def select_final_viral_clips(self, viral_segments, requested_clips, all_segments, target_duration=30):
        """
        ENHANCED FINAL CLIP SELECTION: Guarantees exactly requested_clips number of clips
        ALL clips (including fallbacks) must respect strict sentence boundaries
        """
        final_clips = []
        
        # First try to get clips from viral segments
        if viral_segments:
            for segment in viral_segments[:requested_clips]:
                final_clips.append({
                    **segment,
                    'is_fallback': False,
                    'selection_method': 'viral_analysis'
                })
        
        # If we don't have enough viral segments, add fallback clips WITH STRICT BOUNDARIES
        if len(final_clips) < requested_clips:
            print(f"[INFO] Not enough viral segments ({len(final_clips)}/{requested_clips}), adding STRICT BOUNDARY fallback clips...", file=sys.stderr)
            
            # Use user's requested target duration for fallback clips
            optimal_duration = target_duration  # Respect user's duration preference
            
            # Find segments that don't overlap with existing clips AND respect sentence boundaries
            fallback_candidates = []
            
            for i, segment in enumerate(all_segments):
                if not any(self._segments_overlap(
                    (segment['start'], segment['end']), 
                    (clip['start_time'], clip['end_time'])
                ) for clip in final_clips):
                    
                    # STRICT BOUNDARY CHECK: Apply same sentence boundary rules to fallback clips
                    fallback_clip = self.create_strict_boundary_clip(all_segments, i, optimal_duration)
                    
                    if fallback_clip:
                        fallback_candidates.append({
                            'start_time': fallback_clip['start'],
                            'end_time': fallback_clip['end'],
                            'text': fallback_clip['text'],
                        'viral_score': 0.5,  # Neutral score for fallback
                        'hook_type': 'general',
                            'duration': fallback_clip['end'] - fallback_clip['start'],
                        'segment_index': i,
                            'completeness_score': self.calculate_completeness_score(fallback_clip['text']),
                        'hook_strength': 0,
                        'emotional_impact': 0.5,
                        'attention_score': 0.5,
                        'is_fallback': True,
                            'selection_method': 'sentence_boundary_fallback'
                    })
            
            print(f"[STRICT] Found {len(fallback_candidates)} valid sentence-boundary fallback clips", file=sys.stderr)
            
            # Sort fallback candidates by how close they are to optimal duration
            fallback_candidates.sort(key=lambda x: abs(x['duration'] - optimal_duration))
            
            # Add fallback clips until we reach requested_clips (ensuring no overlap)
            while len(final_clips) < requested_clips and fallback_candidates:
                candidate = fallback_candidates.pop(0)
                
                # Double-check no overlap with existing clips
                if not any(self._segments_overlap(
                    (candidate['start_time'], candidate['end_time']), 
                    (clip['start_time'], clip['end_time'])
                ) for clip in final_clips):
                    final_clips.append(candidate)
                    print(f"[FALLBACK] Added strict boundary fallback clip: {candidate['duration']:.1f}s", file=sys.stderr)
        
        # Ensure clips are sorted by start time
        final_clips.sort(key=lambda x: x['start_time'])
        
        # Log final selection details
        for i, clip in enumerate(final_clips):
            method = "VIRAL" if not clip['is_fallback'] else "FALLBACK"
            boundary_quality = "✅ STRICT BOUNDARIES" if not clip['is_fallback'] else "✅ STRICT BOUNDARIES (FALLBACK)"
            print(f"[INFO] Final clip {i+1}/{len(final_clips)}: {method}, {boundary_quality}, duration={clip['duration']:.1f}s", file=sys.stderr)
        
        return final_clips

    def create_strict_boundary_clip(self, segments, center_index, target_duration):
        """
        Create a fallback clip that STRICTLY respects sentence boundaries
        Similar to find_complete_thought_boundaries but optimized for target duration
        """
        # Use the same strict boundary logic but optimize for duration
        start_idx = center_index
        end_idx = center_index
        
        # Phase 1: Find strict sentence start
        found_valid_start = False
        for i in range(center_index, max(0, center_index - 15), -1):
            if not self.starts_after_sentence_boundary_strict(segments, i):
                continue
                
            text = segments[i]["text"].strip()
            
            # Must start with capital letter
            if not text or not text[0].isupper():
                continue
                
            # Cannot start with continuation words
            if self.is_sentence_continuation(text):
                continue
                
            start_idx = i
            found_valid_start = True
            break
        
        if not found_valid_start:
            return None
        
        # Phase 2: Find strict sentence end near target duration
        found_valid_end = False
        max_search_ahead = min(len(segments), start_idx + 25)
        
        best_end_idx = None
        best_duration_diff = float('inf')
        
        for i in range(start_idx + 1, max_search_ahead):
            text = segments[i]["text"].strip()
            current_duration = segments[i]["end"] - segments[start_idx]["start"]
            
            # Must be close to target duration
            if current_duration < target_duration - 5:
                continue
                
            # Must end with sentence boundary
            if not self.ends_with_sentence_boundary_strict(text):
                continue
                
            # Cannot end with incomplete thoughts
            if self.is_incomplete_sentence_ending(text):
                continue
                
            # Cannot continue in next segment
            if self.next_segment_continues_sentence(segments, i):
                continue
                
            # Check how close to target duration
            duration_diff = abs(current_duration - target_duration)
            
            # Accept any valid clip, but prefer ones closer to target duration
            if duration_diff < best_duration_diff:
                best_end_idx = i
                best_duration_diff = duration_diff
                found_valid_end = True
                
            # Stop if we're getting too far from target
            if current_duration > target_duration + 5:
                break
        
        if not found_valid_end or best_end_idx is None:
            return None
            
        end_idx = best_end_idx
        
        # Final validation
        clip_text = " ".join([seg["text"].strip() for seg in segments[start_idx:end_idx+1]])
        
        if not self.is_complete_sentence_clip(clip_text):
            return None
            
        return {
            'start': segments[start_idx]["start"],
            'end': segments[end_idx]["end"],
            'text': clip_text
        }

    def _segments_overlap(self, seg1, seg2):
        """Helper to check if two segments overlap"""
        start1, end1 = seg1
        start2, end2 = seg2
        return start1 < end2 and end1 > start2

    def force_duration_clips(self, viral_segments, requested_clips, all_segments, target_duration):
        """
        FORCE DURATION: Cut clips to exact user-requested duration
        This overrides all sentence boundary logic to give user exactly what they want
        """
        final_clips = []
        
        # First try to get clips from viral segments and force them to target duration
        if viral_segments:
            for segment in viral_segments[:requested_clips]:
                print(f"[FORCE] Processing viral segment: original_duration={segment.get('duration', 'unknown')}s, target={target_duration}s", file=sys.stderr)
                # FORCE the duration to user's target
                forced_clip = self.force_clip_duration(segment, target_duration, all_segments)
                if forced_clip:
                    print(f"[FORCE] Forced clip duration: {forced_clip['duration']:.1f}s", file=sys.stderr)
                    final_clips.append({
                        **forced_clip,
                        'is_fallback': False,
                        'selection_method': 'forced_duration_viral'
                    })
        
        # If we don't have enough viral segments, create forced-duration fallback clips
        if len(final_clips) < requested_clips:
            print(f"[FORCE] Not enough viral segments ({len(final_clips)}/{requested_clips}), creating FORCED DURATION fallback clips...", file=sys.stderr)
            
            # Find segments that don't overlap with existing clips
            fallback_candidates = []
            
            for i, segment in enumerate(all_segments):
                if not any(self._segments_overlap(
                    (segment['start'], segment['end']), 
                    (clip['start_time'], clip['end_time'])
                ) for clip in final_clips):
                    
                    # Create a forced-duration clip from this segment
                    forced_clip = self.create_forced_duration_clip(all_segments, i, target_duration)
                    
                    if forced_clip:
                        fallback_candidates.append({
                            'start_time': forced_clip['start'],
                            'end_time': forced_clip['end'],
                            'text': forced_clip['text'],
                            'viral_score': 0.5,  # Neutral score for fallback
                            'hook_type': 'general',
                            'duration': forced_clip['end'] - forced_clip['start'],
                            'segment_index': i,
                            'completeness_score': self.calculate_completeness_score(forced_clip['text']),
                            'hook_strength': 0,
                            'emotional_impact': 0.5,
                            'attention_score': 0.5,
                            'is_fallback': True,
                            'selection_method': 'forced_duration_fallback'
                        })
            
            print(f"[FORCE] Found {len(fallback_candidates)} forced-duration fallback clips", file=sys.stderr)
            
            # Add fallback clips until we reach requested_clips
            while len(final_clips) < requested_clips and fallback_candidates:
                candidate = fallback_candidates.pop(0)
                
                # Double-check no overlap with existing clips
                if not any(self._segments_overlap(
                    (candidate['start_time'], candidate['end_time']), 
                    (clip['start_time'], clip['end_time'])
                ) for clip in final_clips):
                    final_clips.append(candidate)
                    print(f"[FORCE] Added forced-duration fallback clip: {candidate['duration']:.1f}s", file=sys.stderr)
        
        # Ensure clips are sorted by start time
        final_clips.sort(key=lambda x: x['start_time'])
        
        # Log final selection details
        for i, clip in enumerate(final_clips):
            method = "FORCED VIRAL" if not clip['is_fallback'] else "FORCED FALLBACK"
            print(f"[FORCE] Final clip {i+1}/{len(final_clips)}: {method}, duration={clip['duration']:.1f}s (target: {target_duration}s)", file=sys.stderr)
        
        return final_clips

    def force_clip_duration(self, segment, target_duration, all_segments):
        """
        Force a clip to exactly target_duration by cutting it
        """
        # Handle both field name formats: 'start'/'end' and 'start_time'/'end_time'
        start_time = segment.get('start_time', segment.get('start', 0))
        original_end_time = segment.get('end_time', segment.get('end', 0))
        original_duration = original_end_time - start_time
        
        # If original duration is already close to target, use it
        if abs(original_duration - target_duration) <= 2:
                    return {
            'start_time': start_time,
            'end_time': original_end_time,
            'duration': original_duration,
            'text': segment['text'],
            'viral_score': segment.get('viral_score', 0),
            'hook_type': segment.get('hook_type', 'general')
        }
        
        # Force the duration by cutting to target_duration
        forced_end_time = start_time + target_duration
        
        # Make sure we don't exceed video length
        max_end_time = max(seg['end'] for seg in all_segments)
        if forced_end_time > max_end_time:
            forced_end_time = max_end_time
            start_time = max(0, forced_end_time - target_duration)
        
        # Extract text for the forced duration
        forced_text = self.extract_text_for_duration(all_segments, start_time, forced_end_time)
        
        return {
            'start_time': start_time,
            'end_time': forced_end_time,
            'duration': forced_end_time - start_time,
            'text': forced_text,
            'viral_score': segment.get('viral_score', 0),
            'hook_type': segment.get('hook_type', 'general')
        }

    def create_forced_duration_clip(self, segments, center_index, target_duration):
        """
        Create a fallback clip with forced duration
        """
        # Start from the center segment
        start_time = segments[center_index]['start']
        forced_end_time = start_time + target_duration
        
        # Make sure we don't exceed video length
        max_end_time = max(seg['end'] for seg in segments)
        if forced_end_time > max_end_time:
            forced_end_time = max_end_time
            start_time = max(0, forced_end_time - target_duration)
        
        # Extract text for the forced duration
        forced_text = self.extract_text_for_duration(segments, start_time, forced_end_time)
        
        return {
            'start_time': start_time,
            'end_time': forced_end_time,
            'text': forced_text
        }

    def extract_text_for_duration(self, segments, start_time, end_time):
        """
        Extract text from segments that fall within the specified duration
        """
        text_parts = []
        
        for segment in segments:
            seg_start = segment['start']
            seg_end = segment['end']
            
            # Check if segment overlaps with our time range
            if seg_start < end_time and seg_end > start_time:
                # Get the overlapping portion
                overlap_start = max(seg_start, start_time)
                overlap_end = min(seg_end, end_time)
                
                # If this segment is mostly within our range, include its text
                if (overlap_end - overlap_start) > (seg_end - seg_start) * 0.5:
                    text_parts.append(segment['text'].strip())
        
        return " ".join(text_parts) if text_parts else "Content from video"

def create_smart_clip_title(text, hook_type, clip_number):
    """Create intelligent titles based on actual content"""
    text_lower = text.lower()
    
    # Extract key topics/subjects (using ASCII-safe text)
    if "business" in text_lower or "money" in text_lower or "profit" in text_lower:
        topic = "Business"
    elif "relationship" in text_lower or "love" in text_lower or "dating" in text_lower:
        topic = "Relationships"
    elif "health" in text_lower or "exercise" in text_lower or "fitness" in text_lower:
        topic = "Health"
    elif "technology" in text_lower or "ai" in text_lower or "tech" in text_lower:
        topic = "Tech"
    elif "food" in text_lower or "cook" in text_lower or "eat" in text_lower:
        topic = "Food"
    elif "travel" in text_lower or "country" in text_lower or "city" in text_lower:
        topic = "Travel"
    else:
        topic = "Viral"
    
    # Create hook-specific titles
    if hook_type == "rhetorical_question":
        return f"{topic} Question That Changes Everything"
    elif hook_type == "fascinating_fact":
        return f"{topic} Truth Most People Ignore"
    elif hook_type == "hard_hitting":
        return f"{topic} Story You Need to Hear"
    elif hook_type == "curiosity_gap":
        return f"{topic} Clip {clip_number} - Must Watch"
    elif hook_type == "urgency":
        return f"{topic} Urgent Update"
    elif hook_type == "personal_stakes":
        return f"{topic} Personal Stakes"
    else:
        return f"{topic} Clip {clip_number} - Must Watch"

def create_content_summary(text):
    """Create intelligent content summaries"""
    # Extract first meaningful sentence or key phrase
    sentences = re.split(r'[.!?]+', text)
    
    if len(sentences) > 0:
        first_sentence = sentences[0].strip()
        if len(first_sentence) > 10:
            summary = first_sentence
            if len(summary) > 60:
                summary = summary[:57] + "..."
            return summary
    
    # Fallback to truncated text
    if len(text) > 70:
        return text[:67] + "..."
    return text

def get_clip_quality_rating(viral_score, natural_flow_score):
    """Rate clip quality based on viral and flow scores"""
    total_score = viral_score + natural_flow_score
    
    if total_score >= 5.0:
        return "Exceptional"
    elif total_score >= 4.0:
        return "Excellent"
    elif total_score >= 3.0:
        return "Good"
    elif total_score >= 2.0:
        return "Decent"
    else:
        return "Basic"

def get_enhanced_clip_quality_rating(clip):
    """Enhanced quality rating based on viral hook scoring factors"""
    viral_score = clip.get('viral_score', 0)
    hook_strength = clip.get('hook_strength', 0)
    completeness_score = clip.get('completeness_score', 0)
    emotional_impact = clip.get('emotional_impact', 0)
    attention_score = clip.get('attention_score', 0)
    is_fallback = clip.get('is_fallback', False)
    
    # New weighted total score based on viral hooks
    total_score = (
        hook_strength * 0.35 +        # 35% hook strength (most important)
        viral_score * 0.25 +          # 25% viral score
        completeness_score * 0.20 +   # 20% completeness
        emotional_impact * 0.15 +     # 15% emotional impact
        attention_score * 0.05        # 5% attention grabbing
    )
    
    # Enhanced rating system with hook-focused categories
    if is_fallback:
        if total_score >= 3.0:
            return "⚠️ Lower Quality - Best Available"
        elif total_score >= 2.0:
            return "⚠️ Lower Quality - Acceptable"
        else:
            return "⚠️ Lower Quality - Basic"
    else:
        if total_score >= 8.0:
            return "🔥 VIRAL GOLD - Perfect Hook"
        elif total_score >= 6.0:
            return "🚀 HIGH VIRAL - Strong Hook"
        elif total_score >= 4.0:
            return "✨ GOOD VIRAL - Solid Hook"
        elif total_score >= 2.5:
            return "👍 DECENT - Weak Hook"
        else:
            return "📈 BASIC - No Clear Hook"

def analyze_created_clip(clip_path):
    """
    Analyze a created clip for quality verification
    Returns clean JSON output
    """
    try:
        print("[ANALYZE] Starting clip analysis...", file=sys.stderr)
        processor = EnhancedWhisperProcessor()
        transcript_text, segments = processor.process_video(clip_path)
        
        return {
            'status': 'success',
            'quality_check': 'Created',
            'actual_content': transcript_text[:100] + '...' if len(transcript_text) > 100 else transcript_text
        }
    except Exception as e:
        print(f"[ERROR] Clip analysis failed: {e}", file=sys.stderr)
        return {
            'status': 'error',
            'quality_check': 'Analysis Failed',
            'error': str(e)
        }

def analyze_video_for_viral_clips(video_path, max_clips=3, target_platform="tiktok", target_duration=30):
    """
    ENHANCED VIRAL CLIP ANALYSIS: Main entry point
    Returns clean JSON output for clip information
    """
    try:
        print("[START] Starting enhanced intelligent clip analysis...", file=sys.stderr)
        
        # Initialize whisper processor
        processor = EnhancedWhisperProcessor()
        
        # Get transcript with word-level timing
        transcript_text, segments = processor.process_video(video_path)
        
        # Create analyzer and find viral clips
        analyzer = ViralContentAnalyzer()
        viral_clips = analyzer.analyze_transcript_for_viral_segments(
            transcript_text, 
            segments,
            requested_clips=max_clips,
            target_platform=target_platform,
            target_duration=target_duration
        )
        
        # Clean output for JSON serialization
        clean_clips = []
        for clip in viral_clips:
            clean_clip = {
                'start_time': float(clip['start_time']),
                'end_time': float(clip['end_time']),
                'duration': float(clip['duration']),
                'viral_score': float(clip['viral_score']),
                'hook_type': str(clip['hook_type']),
                'text': str(clip['text']),
                'is_fallback': bool(clip.get('is_fallback', False)),
                'selection_method': str(clip.get('selection_method', 'viral_analysis')),
                'quality_metrics': {
                    'hook_strength': float(clip.get('hook_strength', 0)),
                    'completeness': float(clip.get('completeness_score', 0)),
                    'emotional_impact': float(clip.get('emotional_impact', 0)),
                    'attention_score': float(clip.get('attention_score', 0))
                }
            }
            clean_clips.append(clean_clip)
        
        # Return clean JSON without any emojis or special characters
        return json.dumps({
            'status': 'success',
            'clips': clean_clips,
            'total_clips': len(clean_clips)
        })
        
    except Exception as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python intelligent_clip_analyzer.py <video_file> [max_clips] [platform] [duration]\n")
        sys.stderr.write("Platform options: tiktok, instagram, youtube\n")
        sys.exit(1)
    
    video_file = sys.argv[1]
    max_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    target_platform = sys.argv[3] if len(sys.argv) > 3 else "tiktok"
    target_duration = int(sys.argv[4]) if len(sys.argv) > 4 else 30  # Default to 30 seconds
    
    # Validate platform
    valid_platforms = ["tiktok", "instagram", "youtube"]
    if target_platform not in valid_platforms:
        sys.stderr.write(f"Invalid platform: {target_platform}. Valid options: {', '.join(valid_platforms)}\n")
        sys.exit(1)
    
    result = analyze_video_for_viral_clips(video_file, max_clips, target_platform, target_duration)
    # Output clean JSON only to stdout
    print(result) 