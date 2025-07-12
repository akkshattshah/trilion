#!/usr/bin/env python3
"""
NEXT-GENERATION ENHANCED Intelligent Clip Analyzer: VIRAL DETECTION AI SYSTEM
Creates clips with maximum viral potential using advanced AI analysis
ULTRA-ENHANCED: Psychological Triggers + Platform Optimization + Trend Analysis + Enhanced Sentence Boundary Detection
"""
import re
import json
import math
import sys
import time
from enhanced_whisper import EnhancedWhisperProcessor
from enhanced_sentence_boundary_detector import find_enhanced_clip_boundaries_with_sentence_detection
import subprocess
from datetime import timedelta

class AdvancedViralContentAnalyzer:
    def __init__(self):
        # 🔥 NEXT-GENERATION VIRAL HOOK PATTERNS (300+ patterns)
        
        # PSYCHOLOGICAL TRIGGER PATTERNS - Based on viral psychology research
        self.psychological_triggers = {
            # CURIOSITY GAP PATTERNS (Extremely viral)
            "curiosity_gaps": [
                r"you won't believe what happened when",
                r"this (.*?) will change everything",
                r"the secret (.*?) don't want you to know",
                r"what happens next will (shock|amaze|surprise) you",
                r"this one (trick|method|secret) that",
                r"here's what (they|experts|doctors) don't tell you",
                r"the hidden truth about",
                r"what (really|actually) happens when",
                r"this will blow your mind",
                r"you've been doing (.*?) wrong your entire life",
                r"the (shocking|surprising|incredible) reason why",
                r"nobody talks about this but",
                r"this (changes|ruins|destroys) everything",
                r"wait until you see what happens at",
                r"the plot twist that nobody saw coming"
            ],
            
            # FEAR/LOSS AVERSION (Highly engaging)
            "fear_triggers": [
                r"you're losing money if you don't",
                r"this mistake is costing you",
                r"stop doing this before it's too late",
                r"this is destroying your",
                r"why you're failing at",
                r"the (dangerous|deadly) truth about",
                r"this will ruin your",
                r"you're being scammed by",
                r"this is why you can't",
                r"the scary reality of",
                r"what nobody warns you about",
                r"this could happen to you",
                r"before you lose everything",
                r"this is killing your"
            ],
            
            # SOCIAL PROOF & AUTHORITY (Trust builders)
            "authority_triggers": [
                r"\d+ (million|billion) people don't know",
                r"(scientists|doctors|experts|researchers) discovered",
                r"harvard study reveals",
                r"billionaires use this",
                r"celebrities don't want you to know",
                r"wall street doesn't want you to know",
                r"the government is hiding",
                r"big (pharma|tech|corporations) don't want",
                r"what successful people do differently",
                r"the elite's secret to",
                r"insider secrets from",
                r"what the top 1% know",
                r"exclusive insider information"
            ],
            
            # TRANSFORMATION/ASPIRATION (Dream fulfillment)
            "transformation_triggers": [
                r"from (\$\d+|\d+\w+) to (\$\d+|\d+\w+) in",
                r"how I went from (.*?) to (.*?) in",
                r"this changed my life in \d+ days",
                r"the \d+-step system that",
                r"how to (10x|double|triple) your",
                r"the fastest way to",
                r"zero to (hero|millionaire|success) in",
                r"this (technique|method|strategy) made me",
                r"the life-changing",
                r"transform your (life|career|finances) with",
                r"go from broke to rich",
                r"the ultimate guide to becoming",
                r"unlock your potential with"
            ]
        }
        
        # 🎬 PLATFORM-SPECIFIC VIRAL PATTERNS
        self.platform_patterns = {
            "tiktok": {
                # TikTok favors quick, punchy, relatable content
                "hook_starters": [
                    r"pov\s*:",
                    r"tell me you're (.*?) without telling me",
                    r"this is your sign to",
                    r"nobody told me that",
                    r"when you realize",
                    r"the way I (.*?) is",
                    r"things I wish I knew",
                    r"red flags that",
                    r"green flags that",
                    r"if you don't do this",
                    r"normalize (.*?)",
                    r"reminder that",
                    r"unpopular opinion",
                    r"hot take",
                    r"story time",
                    r"plot twist",
                    r"this is why"
                ],
                "trending_words": ["slay", "periodt", "bestie", "vibes", "energy", "iconic", "main character", "no cap", "fr", "literally"],
                "engagement_boost": 2.5  # TikTok multiplier
            },
            
            "instagram": {
                # Instagram favors aspirational, aesthetic, lifestyle content
                "hook_starters": [
                    r"that girl who",
                    r"soft life",
                    r"main character energy",
                    r"glow up tips",
                    r"level up your",
                    r"aesthetic (.*?) that",
                    r"self care routine",
                    r"mindset shift",
                    r"vision board",
                    r"manifestation"
                ],
                "trending_words": ["aesthetic", "vibe", "energy", "glow", "soft", "dreamy", "luxe", "wellness"],
                "engagement_boost": 2.0
            },
            
            "youtube_shorts": {
                # YouTube Shorts favors educational, surprising facts
                "hook_starters": [
                    r"did you know that",
                    r"fun fact",
                    r"science fact",
                    r"mind-blowing fact",
                    r"here's why",
                    r"the reason",
                    r"this is how",
                    r"scientists discovered"
                ],
                "trending_words": ["facts", "science", "discovery", "research", "study", "expert"],
                "engagement_boost": 1.8
            }
        }
        
        # 🔥 EMOTIONAL INTENSITY PATTERNS (Advanced emotion detection)
        self.emotional_patterns = {
            "extreme_excitement": {
                "patterns": [r"(insane|crazy|wild|unbelievable|mind-blowing|epic|legendary)", r"best.*ever", r"greatest.*all time"],
                "score": 5.0
            },
            "shock_surprise": {
                "patterns": [r"(shocking|surprising|jaw-dropping|stunning|incredible)", r"plot twist", r"nobody expected"],
                "score": 4.5
            },
            "controversy": {
                "patterns": [r"controversial", r"unpopular opinion", r"hot take", r"everyone's wrong", r"truth bomb"],
                "score": 4.0
            },
            "urgency_scarcity": {
                "patterns": [r"before it's too late", r"limited time", r"don't wait", r"act now", r"running out"],
                "score": 3.5
            },
            "relatable_struggle": {
                "patterns": [r"why is this so hard", r"nobody tells you", r"the struggle is real", r"we've all been there"],
                "score": 3.0
            }
        }
        
        # 📈 CURRENT VIRAL TRENDS (Updated regularly)
        self.trending_topics = {
            "2024_trends": [
                "soft life", "main character energy", "villain era", "hot girl walk",
                "bed rotting", "quiet luxury", "clean girl aesthetic", "dark academia",
                "corporate girlie", "that girl", "mindful consumption", "digital detox",
                "micro-dosing trends", "biohacking", "manifestation", "shadow work"
            ],
            "business_trends": [
                "passive income", "digital nomad", "side hustle", "entrepreneur life",
                "dropshipping", "affiliate marketing", "personal brand", "online course",
                "stock market", "crypto", "real estate", "financial freedom"
            ],
            "lifestyle_trends": [
                "morning routine", "night routine", "self care", "mental health",
                "productivity", "organization", "minimalism", "sustainability",
                "fitness journey", "glow up", "transformation", "level up"
            ]
        }
        
        # 🎯 ADVANCED HOOK DETECTION SYSTEM
        self.advanced_hooks = {
            # NUMBERED LIST HOOKS (Highly clickable)
            "numbered_lists": [
                r"\d+ (ways|reasons|secrets|tips|tricks|hacks|steps|signs|things)",
                r"top \d+", r"best \d+", r"worst \d+", r"\d+ minute",
                r"\d+ second", r"\d+ hour", r"\d+ day", r"\d+-step"
            ],
            
            # QUESTION HOOKS (Engagement magnets)
            "question_hooks": [
                r"what if I told you",
                r"what would you do if",
                r"have you ever wondered",
                r"did you know that",
                r"what's the difference between",
                r"which one would you choose",
                r"what's your (opinion|thought) on",
                r"am I the only one who",
                r"does anyone else",
                r"why do people",
                r"how many of you",
                r"what's worse"
            ],
            
            # STORYTELLING HOOKS (Narrative engagement)
            "story_hooks": [
                r"story time", r"storytime", r"let me tell you about",
                r"this happened to me", r"true story", r"real talk",
                r"confession time", r"plot twist", r"unexpected ending",
                r"the craziest thing happened", r"you won't believe this"
            ],
            
            # COMPARISON HOOKS (Decision engagement)
            "comparison_hooks": [
                r"(.*?) vs (.*?)", r"rich vs poor", r"then vs now",
                r"expectation vs reality", r"before vs after",
                r"cheap vs expensive", r"fake vs real",
                r"good vs bad", r"right vs wrong"
            ]
        }

    def analyze_transcript_for_viral_segments(self, transcript_text, segments, requested_clips=3, target_platform="tiktok", target_duration=30):
        """
        NEXT-GENERATION VIRAL ANALYSIS with Advanced AI Scoring
        """
        print(f"[AI] 🧠 Starting next-generation viral analysis on {len(segments)} segments...", file=sys.stderr)
        print(f"[AI] 🎯 Target platform: {target_platform.upper()}, Duration: {target_duration}s", file=sys.stderr)
        
        # Phase 1: Multi-dimensional viral scoring
        all_scored_segments = []
        
        for i, segment in enumerate(segments):
            text = segment["text"].strip()
            
            # ADVANCED MULTI-SCORING SYSTEM
            scores = self.calculate_comprehensive_viral_score(text, transcript_text, target_platform)
            
            # Only proceed if segment shows any viral potential
            if scores['total_score'] > 0.5:  # Adjusted threshold
                
                # Find optimal clip boundaries
                clip_segment = self.find_intelligent_clip_boundaries(
                    segments, i, transcript_text, target_duration, scores
                )
                
                if clip_segment:
                    enhanced_segment = {
                        'start_time': clip_segment['start'],
                        'end_time': clip_segment['end'],
                        'text': clip_segment['text'],
                        'duration': clip_segment['end'] - clip_segment['start'],
                        'segment_index': i,
                        
                        # COMPREHENSIVE SCORING
                        'viral_score': scores['total_score'],
                        'hook_strength': scores['hook_strength'],
                        'emotional_intensity': scores['emotional_intensity'],
                        'platform_optimization': scores['platform_optimization'],
                        'psychological_impact': scores['psychological_impact'],
                        'trend_alignment': scores['trend_alignment'],
                        'engagement_prediction': scores['engagement_prediction'],
                        'completeness_score': clip_segment['completeness_score'],
                        
                        # CLASSIFICATION
                        'hook_type': scores['dominant_hook_type'],
                        'viral_category': scores['viral_category'],
                        'target_demographic': scores['target_demographic'],
                        'optimal_platform': scores['optimal_platform'],
                        
                        # QUALITY METRICS
                        'clarity_score': self.calculate_clarity_score(clip_segment['text']),
                        'momentum_score': self.calculate_momentum_score(clip_segment['text'], transcript_text),
                        'replay_potential': self.calculate_replay_potential(clip_segment['text']),
                        'share_probability': self.calculate_share_probability(scores)
                    }
                    
                    all_scored_segments.append(enhanced_segment)
                    
                    if len(all_scored_segments) % 5 == 0:
                        print(f"[AI] 📊 Analyzed {len(all_scored_segments)} potential viral segments...", file=sys.stderr)
        
        print(f"[AI] 🎯 Found {len(all_scored_segments)} segments with viral potential", file=sys.stderr)
        
        # Phase 2: Advanced sorting with platform optimization
        platform_boost = self.platform_patterns.get(target_platform, {}).get('engagement_boost', 1.0)
        
        all_scored_segments = sorted(all_scored_segments, key=lambda x: (
            x['viral_score'] * 0.25 +
            x['hook_strength'] * 0.20 +
            x['emotional_intensity'] * 0.15 +
            x['platform_optimization'] * platform_boost * 0.15 +
            x['psychological_impact'] * 0.10 +
            x['engagement_prediction'] * 0.10 +
            self.calculate_duration_preference(x['duration'], target_duration) * 0.05
        ), reverse=True)
        
        # Phase 3: Intelligent segment selection
        final_clips = self.select_optimal_viral_segments(
            all_scored_segments, requested_clips, target_platform, target_duration
        )
        
        # Phase 4: Enhanced logging with insights
        self.log_viral_analysis_results(final_clips, target_platform)
        
        return final_clips

    def calculate_comprehensive_viral_score(self, text, full_transcript, target_platform="tiktok"):
        """
        Advanced multi-dimensional viral scoring system
        """
        text_lower = text.lower()
        scores = {
            'hook_strength': 0.0,
            'emotional_intensity': 0.0,
            'platform_optimization': 0.0,
            'psychological_impact': 0.0,
            'trend_alignment': 0.0,
            'engagement_prediction': 0.0,
            'total_score': 0.0,
            'dominant_hook_type': 'general',
            'viral_category': 'standard',
            'target_demographic': 'general',
            'optimal_platform': target_platform
        }
        
        # 1. HOOK STRENGTH ANALYSIS
        hook_score, hook_type = self.analyze_hook_strength(text_lower)
        scores['hook_strength'] = hook_score
        scores['dominant_hook_type'] = hook_type
        
        # 2. EMOTIONAL INTENSITY ANALYSIS
        scores['emotional_intensity'] = self.analyze_emotional_intensity(text_lower)
        
        # 3. PLATFORM OPTIMIZATION ANALYSIS
        scores['platform_optimization'] = self.analyze_platform_optimization(text_lower, target_platform)
        
        # 4. PSYCHOLOGICAL TRIGGER ANALYSIS
        scores['psychological_impact'] = self.analyze_psychological_triggers(text_lower)
        
        # 5. TREND ALIGNMENT ANALYSIS
        scores['trend_alignment'] = self.analyze_trend_alignment(text_lower)
        
        # 6. ENGAGEMENT PREDICTION
        scores['engagement_prediction'] = self.predict_engagement_potential(text_lower, scores)
        
        # 7. VIRAL CATEGORY CLASSIFICATION
        scores['viral_category'] = self.classify_viral_category(text_lower, scores)
        
        # 8. TARGET DEMOGRAPHIC IDENTIFICATION
        scores['target_demographic'] = self.identify_target_demographic(text_lower)
        
        # CALCULATE TOTAL SCORE with platform weighting
        platform_weight = self.platform_patterns.get(target_platform, {}).get('engagement_boost', 1.0)
        
        scores['total_score'] = (
            scores['hook_strength'] * 2.5 +
            scores['emotional_intensity'] * 2.0 +
            scores['platform_optimization'] * platform_weight * 1.5 +
            scores['psychological_impact'] * 1.8 +
            scores['trend_alignment'] * 1.2 +
            scores['engagement_prediction'] * 1.0
        )
        
        return scores

    def analyze_hook_strength(self, text):
        """
        Advanced hook strength analysis with pattern recognition
        """
        max_score = 0.0
        dominant_type = 'general'
        
        # Analyze all hook categories
        hook_categories = {
            'psychological_triggers': 5.0,
            'numbered_lists': 4.5,
            'question_hooks': 4.0,
            'story_hooks': 3.5,
            'comparison_hooks': 3.0
        }
        
        for category, base_score in hook_categories.items():
            if category == 'psychological_triggers':
                # Check all psychological trigger categories
                for trigger_type, patterns in self.psychological_triggers.items():
                    for pattern in patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            score = base_score * self.get_trigger_multiplier(trigger_type)
                            if score > max_score:
                                max_score = score
                                dominant_type = trigger_type
            else:
                # Check regular hook patterns
                patterns = self.advanced_hooks.get(category, [])
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        if base_score > max_score:
                            max_score = base_score
                            dominant_type = category
        
        return min(max_score, 10.0), dominant_type

    def analyze_emotional_intensity(self, text):
        """
        Advanced emotional intensity analysis
        """
        total_intensity = 0.0
        
        for emotion_type, data in self.emotional_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    total_intensity += data['score']
        
        # Boost for multiple exclamations, caps, etc.
        if re.search(r'[!]{2,}', text):
            total_intensity += 1.0
        if re.search(r'[A-Z]{3,}', text):
            total_intensity += 0.5
        
        return min(total_intensity, 10.0)

    def analyze_platform_optimization(self, text, platform):
        """
        Platform-specific optimization analysis
        """
        if platform not in self.platform_patterns:
            return 3.0  # Default score
        
        platform_data = self.platform_patterns[platform]
        score = 0.0
        
        # Check platform-specific hook starters
        for pattern in platform_data.get('hook_starters', []):
            if re.search(pattern, text, re.IGNORECASE):
                score += 3.0
                break
        
        # Check trending words for platform
        trending_words = platform_data.get('trending_words', [])
        word_count = sum(1 for word in trending_words if word in text)
        score += min(word_count * 0.5, 2.0)
        
        # Platform-specific bonuses
        if platform == 'tiktok':
            # TikTok loves personal, relatable content
            personal_indicators = ['i', 'me', 'my', 'when i', 'i was', 'i am']
            if any(indicator in text for indicator in personal_indicators):
                score += 1.0
        
        elif platform == 'instagram':
            # Instagram loves aspirational content
            aspirational_words = ['goals', 'aesthetic', 'vibes', 'lifestyle', 'dream']
            if any(word in text for word in aspirational_words):
                score += 1.0
        
        elif platform == 'youtube_shorts':
            # YouTube loves educational content
            educational_indicators = ['how to', 'tutorial', 'learn', 'explain', 'guide']
            if any(indicator in text for indicator in educational_indicators):
                score += 1.0
        
        return min(score, 10.0)

    def analyze_psychological_triggers(self, text):
        """
        Advanced psychological trigger analysis
        """
        total_impact = 0.0
        
        # FOMO (Fear of Missing Out)
        fomo_patterns = [r"limited time", r"don't miss", r"last chance", r"exclusive", r"only \d+"]
        for pattern in fomo_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                total_impact += 2.0
        
        # Social Proof
        social_proof = [r"\d+ million", r"\d+ people", r"everyone is", r"most people", r"celebrities"]
        for pattern in social_proof:
            if re.search(pattern, text, re.IGNORECASE):
                total_impact += 1.5
        
        # Authority
        authority_markers = [r"experts", r"scientists", r"research", r"study shows", r"proven"]
        for pattern in authority_markers:
            if re.search(pattern, text, re.IGNORECASE):
                total_impact += 1.2
        
        # Reciprocity
        reciprocity_triggers = [r"free", r"gift", r"bonus", r"give you", r"share with you"]
        for pattern in reciprocity_triggers:
            if re.search(pattern, text, re.IGNORECASE):
                total_impact += 1.0
        
        return min(total_impact, 10.0)

    def analyze_trend_alignment(self, text):
        """
        Current trend alignment analysis
        """
        trend_score = 0.0
        
        # Check against current trending topics
        for trend_category, trends in self.trending_topics.items():
            for trend in trends:
                if trend.lower() in text:
                    trend_score += 1.5
        
        # Boost for viral format patterns
        viral_formats = [
            r"pov:", r"tell me.*without telling me", r"this is your sign",
            r"nobody:", r"me:", r"also me:", r"everyone:", r"literally nobody:"
        ]
        
        for format_pattern in viral_formats:
            if re.search(format_pattern, text, re.IGNORECASE):
                trend_score += 2.0
        
        return min(trend_score, 10.0)

    def predict_engagement_potential(self, text, scores):
        """
        ML-inspired engagement prediction
        """
        # Base engagement prediction using weighted scores
        base_prediction = (
            scores['hook_strength'] * 0.3 +
            scores['emotional_intensity'] * 0.25 +
            scores['psychological_impact'] * 0.2 +
            scores['platform_optimization'] * 0.15 +
            scores['trend_alignment'] * 0.1
        )
        
        # Length optimization (sweet spot analysis)
        word_count = len(text.split())
        if 10 <= word_count <= 25:
            base_prediction += 1.0
        elif 25 <= word_count <= 40:
            base_prediction += 0.5
        
        # Question boost (questions drive comments)
        if '?' in text:
            base_prediction += 1.0
        
        # Call-to-action boost
        cta_patterns = [r"comment", r"like if", r"share", r"tag", r"follow", r"what do you think"]
        for pattern in cta_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                base_prediction += 0.5
                break
        
        return min(base_prediction, 10.0)

    def classify_viral_category(self, text, scores):
        """
        Classify content into viral categories
        """
        if scores['emotional_intensity'] > 7.0:
            return 'highly_emotional'
        elif scores['hook_strength'] > 6.0:
            return 'strong_hook'
        elif scores['psychological_impact'] > 5.0:
            return 'psychological_trigger'
        elif scores['trend_alignment'] > 4.0:
            return 'trending_topic'
        elif scores['platform_optimization'] > 5.0:
            return 'platform_optimized'
        else:
            return 'standard_content'

    def identify_target_demographic(self, text):
        """
        Identify target demographic for the content
        """
        # Gen Z indicators
        genz_indicators = ['lowkey', 'highkey', 'no cap', 'periodt', 'slay', 'bestie', 'main character']
        if any(indicator in text for indicator in genz_indicators):
            return 'gen_z'
        
        # Millennial indicators
        millennial_indicators = ['adulting', 'side hustle', 'work-life balance', 'anxiety', 'therapy']
        if any(indicator in text for indicator in millennial_indicators):
            return 'millennial'
        
        # Business/Professional
        business_indicators = ['entrepreneur', 'investment', 'business', 'success', 'money', 'finance']
        if any(indicator in text for indicator in business_indicators):
            return 'business_professional'
        
        # Lifestyle/Wellness
        lifestyle_indicators = ['wellness', 'self-care', 'mindfulness', 'healthy', 'fitness']
        if any(indicator in text for indicator in lifestyle_indicators):
            return 'lifestyle_wellness'
        
        return 'general'

    def get_trigger_multiplier(self, trigger_type):
        """
        Get multiplier based on trigger effectiveness
        """
        multipliers = {
            'curiosity_gaps': 1.2,
            'fear_triggers': 1.1,
            'authority_triggers': 1.0,
            'transformation_triggers': 1.15
        }
        return multipliers.get(trigger_type, 1.0)

    def calculate_clarity_score(self, text):
        """
        Calculate content clarity score
        """
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Optimal sentence length for social media
        if 8 <= avg_sentence_length <= 20:
            return 8.0
        elif 5 <= avg_sentence_length <= 25:
            return 6.0
        else:
            return 4.0

    def calculate_momentum_score(self, text, full_transcript):
        """
        Calculate content momentum and build-up
        """
        # Check if content builds to something exciting
        momentum_words = ['then', 'but', 'suddenly', 'however', 'finally', 'ultimately']
        momentum_count = sum(1 for word in momentum_words if word in text.lower())
        
        # Check position in transcript (middle content often has more momentum)
        position_ratio = full_transcript.find(text) / len(full_transcript) if text in full_transcript else 0.5
        
        # Sweet spot is 30-70% through the content
        if 0.3 <= position_ratio <= 0.7:
            position_bonus = 2.0
        else:
            position_bonus = 1.0
        
        return min(momentum_count * 1.5 + position_bonus, 10.0)

    def calculate_replay_potential(self, text):
        """
        Calculate how likely content is to be rewatched
        """
        replay_indicators = [
            r"\d+ (times|seconds|minutes)", r"watch.*again", r"replay",
            r"notice", r"detail", r"easter egg", r"hidden"
        ]
        
        replay_score = 0.0
        for pattern in replay_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                replay_score += 2.0
        
        # Complex content with multiple layers
        if len(text.split(',')) > 3:  # Multiple clauses
            replay_score += 1.0
        
        return min(replay_score, 10.0)

    def calculate_share_probability(self, scores):
        """
        Calculate likelihood of content being shared
        """
        # Sharing factors: emotional impact + social relevance + practical value
        share_score = (
            scores['emotional_intensity'] * 0.4 +
            scores['psychological_impact'] * 0.3 +
            scores['trend_alignment'] * 0.2 +
            scores['hook_strength'] * 0.1
        )
        
        return min(share_score, 10.0)

    def find_intelligent_clip_boundaries(self, segments, center_index, full_transcript, target_duration, scores):
        """
        Intelligent boundary detection with viral optimization
        """
        # Use the existing boundary detection but with viral enhancements
        clip_segment = self.find_complete_thought_boundaries(segments, center_index, full_transcript, target_duration)
        
        if clip_segment:
            # Add viral-specific completeness score
            clip_segment['completeness_score'] = self.calculate_completeness_score(clip_segment['text'])
        
        return clip_segment

    def calculate_completeness_score(self, text):
        """
        Calculate how complete the thought/clip is
        """
        # Check for complete sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) == 0:
            return 3.0
        
        # Check sentence structure
        complete_score = 8.0
        
        # Penalty for incomplete thoughts
        incomplete_indicators = ['and', 'but', 'so', 'because', 'however']
        if any(text.strip().endswith(word) for word in incomplete_indicators):
            complete_score -= 2.0
        
        # Bonus for clear conclusion
        conclusion_indicators = ['therefore', 'so', 'that\'s why', 'in conclusion']
        if any(indicator in text.lower() for indicator in conclusion_indicators):
            complete_score += 1.0
        
        return min(complete_score, 10.0)

    def calculate_duration_preference(self, duration, target_duration=30):
        """
        Duration preference calculation
        """
        diff = abs(duration - target_duration)
        if diff <= 2:
            return 10.0
        elif diff <= 5:
            return 8.0
        elif diff <= 10:
            return 6.0
        else:
            return 3.0

    def select_optimal_viral_segments(self, scored_segments, requested_clips, target_platform, target_duration):
        """
        Select optimal segments with diversity and viral potential
        """
        if not scored_segments:
            return []
        
        final_clips = []
        used_categories = set()
        
        # First pass: Select highest scoring clips from different categories
        for segment in scored_segments:
            if len(final_clips) >= requested_clips:
                break
            
            viral_category = segment.get('viral_category', 'standard')
            
            # Prefer diversity in viral categories
            if viral_category not in used_categories or len(final_clips) < requested_clips // 2:
                final_clips.append(segment)
                used_categories.add(viral_category)
        
        # Second pass: Fill remaining slots with best available
        remaining_clips = requested_clips - len(final_clips)
        if remaining_clips > 0:
            available_segments = [s for s in scored_segments if s not in final_clips]
            final_clips.extend(available_segments[:remaining_clips])
        
        return final_clips[:requested_clips]

    def log_viral_analysis_results(self, final_clips, target_platform):
        """
        Enhanced logging with detailed viral insights
        """
        print(f"\n[AI] �� VIRAL ANALYSIS COMPLETE - {target_platform.upper()}", file=sys.stderr)
        print(f"[AI] 📊 Generated {len(final_clips)} optimized viral clips", file=sys.stderr)
        
        for i, clip in enumerate(final_clips):
            print(f"\n[AI] 🔥 CLIP {i+1} ANALYSIS:", file=sys.stderr)
            print(f"[AI]    🎯 Viral Score: {clip.get('viral_score', 0):.2f}/10", file=sys.stderr)
            print(f"[AI]    🪝 Hook Type: {clip.get('hook_type', 'general')}", file=sys.stderr)
            print(f"[AI]    🎭 Category: {clip.get('viral_category', 'standard')}", file=sys.stderr)
            print(f"[AI]    👥 Demographic: {clip.get('target_demographic', 'general')}", file=sys.stderr)
            print(f"[AI]    📈 Engagement Prediction: {clip.get('engagement_prediction', 0):.1f}/10", file=sys.stderr)
            print(f"[AI]    🔄 Share Probability: {clip.get('share_probability', 0):.1f}/10", file=sys.stderr)
            print(f"[AI]    ⏱️ Duration: {clip.get('duration', 0):.1f}s", file=sys.stderr)
            print(f"[AI]    📝 Preview: {clip.get('text', '')[:80]}...", file=sys.stderr)

    # Enhanced boundary detection with sentence-level analysis
    def find_complete_thought_boundaries(self, segments, center_index, full_transcript, target_duration=30):
        """
        🎯 ENHANCED BOUNDARY DETECTION - Now with proper sentence-level analysis
        Solves the user's complaint about mid-sentence starts by using intelligent sentence grouping
        """
        # Try enhanced sentence detection first
        enhanced_result = find_enhanced_clip_boundaries_with_sentence_detection(
            segments, center_index, full_transcript, target_duration
        )
        
        if enhanced_result:
            print(f"[SUCCESS] Enhanced detection found structured start: '{enhanced_result['text'][:100]}...'", file=sys.stderr)
            return enhanced_result
        
        # Fallback to original logic if enhanced detection fails
        print("[FALLBACK] Using original boundary detection", file=sys.stderr)
        return self.find_complete_thought_boundaries_original(segments, center_index, full_transcript, target_duration)

    def find_complete_thought_boundaries_original(self, segments, center_index, full_transcript, target_duration=30):
        """
        Original boundary detection (renamed as fallback)
        """
        start_idx = center_index
        end_idx = center_index
        
        # Find starting point with viral optimization
        found_valid_start = False
        for i in range(center_index, max(0, center_index - 20), -1):
            if not self.starts_after_sentence_boundary_strict(segments, i):
                continue
                
            text = segments[i]["text"].strip()
            
            if not text or not text[0].isupper():
                continue
                
            if self.is_sentence_continuation(text):
                continue
                
            # Prioritize viral hook starts
            if self.is_powerful_hook_start(text):
                start_idx = i
                found_valid_start = True
                break
            elif self.is_strong_sentence_start(text):
                start_idx = i
                found_valid_start = True

        if not found_valid_start:
            return None

        # Find ending point
        found_valid_end = False
        max_search_ahead = min(len(segments), start_idx + 30)
        
        for i in range(start_idx + 1, max_search_ahead):
            text = segments[i]["text"].strip()
            current_duration = segments[i]["end"] - segments[start_idx]["start"]
            
            if current_duration < target_duration - 5:
                continue
                
            if not self.ends_with_sentence_boundary_strict(text):
                continue
                
            if self.is_incomplete_sentence_ending(text):
                continue
                
            if self.next_segment_continues_sentence(segments, i):
                continue
                
            duration_diff = abs(current_duration - target_duration)
            
            if duration_diff > 5:
                continue
                
            if duration_diff <= 2:
                end_idx = i
                found_valid_end = True
                break
                
            elif duration_diff <= 5:
                end_idx = i
                found_valid_end = True

        if not found_valid_end:
            return None
        
        # Final validation
        clip_text = " ".join([seg["text"].strip() for seg in segments[start_idx:end_idx+1]])
        duration = segments[end_idx]["end"] - segments[start_idx]["start"]
        
        if not self.is_complete_sentence_clip(clip_text):
            return None
            
        min_duration = target_duration - 3
        max_duration = target_duration + 3
        if duration < min_duration or duration > max_duration:
            return None
        
        return {
            'start': segments[start_idx]["start"],
            'end': segments[end_idx]["end"],
            'text': clip_text,
            'completeness_score': 8.0  # Will be recalculated
        }

    # Helper functions adapted from original
    def starts_after_sentence_boundary_strict(self, segments, segment_index):
        """Check if segment starts after sentence boundary"""
        if segment_index == 0:
            return True
        
        previous_segment = segments[segment_index - 1]
        previous_text = previous_segment["text"].strip()
        return self.ends_with_sentence_boundary_strict(previous_text)

    def ends_with_sentence_boundary_strict(self, text):
        """Check if text ends with sentence boundary"""
        text = text.strip()
        return re.search(r'[.!?]\s*$', text) is not None

    def is_sentence_continuation(self, text):
        """Detect sentence continuation"""
        text_lower = text.lower().strip()
        continuation_words = [
            "and", "but", "or", "so", "then", "also", "too", "as well", 
            "because", "since", "while", "when", "where", "which", "that",
            "however", "although", "though", "yet", "still", "even"
        ]
        
        for word in continuation_words:
            if text_lower.startswith(word + " "):
                return True
                
        if text and text[0].islower():
            return True
            
        return False

    def is_incomplete_sentence_ending(self, text):
        """Detect incomplete sentence endings"""
        text = text.strip().lower()
        incomplete_endings = [
            "and", "but", "or", "so", "then", "because", "since", "while",
            "when", "where", "which", "that", "the", "a", "an", "he", "she", 
            "it", "they", "we", "you", "i", "this", "these", "those"
        ]
        
        text_clean = re.sub(r'[.!?]\s*$', '', text).strip()
        last_word = text_clean.split()[-1] if text_clean.split() else ""
        return last_word in incomplete_endings

    def next_segment_continues_sentence(self, segments, current_index):
        """Check if next segment continues sentence"""
        if current_index + 1 >= len(segments):
            return False
            
        next_segment = segments[current_index + 1]["text"].strip()
        
        if not next_segment:
            return False
            
        if next_segment[0].islower():
            return True
            
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
        """Validate complete sentence clip"""
        text = clip_text.strip()
        
        if not text or not text[0].isupper():
            return False
            
        if not re.search(r'[.!?]\s*$', text):
            return False
            
        if self.is_sentence_continuation(text):
            return False
            
        if self.is_incomplete_sentence_ending(text):
            return False
            
        words = text.split()
        if len(words) < 8:
            return False
            
        # Check for common verbs
        common_verbs = [
            "is", "are", "was", "were", "am", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "can", "could", "should", "shall", "may", "might", "must",
            "go", "goes", "went", "gone", "get", "gets", "got", "gotten",
            "make", "makes", "made", "take", "takes", "took", "taken"
        ]
        
        text_lower = text.lower()
        has_verb = any(f" {verb} " in f" {text_lower} " or 
                      text_lower.startswith(f"{verb} ") or 
                      text_lower.endswith(f" {verb}") for verb in common_verbs)
        
        return has_verb

    def is_powerful_hook_start(self, text):
        """Detect powerful viral hook starts"""
        text_lower = text.lower().strip()
        
        # Enhanced viral hook detection
        viral_starters = [
            r"^(what if|did you know|have you ever|why do|how is|what would)",
            r"^(most people don't|scientists discovered|the hidden truth|here's what)",
            r"^(everyone is wrong|you've been lied to|this will destroy|the biggest mistake)",
            r"^(pov:|tell me you're|this is your sign|nobody told me)",
            r"^(story time|plot twist|you won't believe|wait until)"
        ]
        
        for pattern in viral_starters:
            if re.match(pattern, text_lower):
                return True
        
        return False

    def is_strong_sentence_start(self, text):
        """Detect strong sentence start"""
        text = text.strip()
        
        if not text or not text[0].isupper():
            return False
        
        filler_words = ["um", "uh", "so", "well", "like", "you know", "i mean"]
        text_lower = text.lower()
        
        for filler in filler_words:
            if text_lower.startswith(filler + " "):
                return False
        
        return True


# Enhanced main analysis function
def analyze_video_for_viral_clips(video_path, max_clips=3, target_platform="tiktok", target_duration=30):
    """
    NEXT-GENERATION viral clip analysis with advanced AI
    """
    try:
        print("[AI] 🚀 Starting next-generation viral analysis...", file=sys.stderr)
        
        # Initialize enhanced processor
        processor = EnhancedWhisperProcessor()
        transcript_text, segments = processor.process_video(video_path)
        
        # Use advanced analyzer
        analyzer = AdvancedViralContentAnalyzer()
        viral_clips = analyzer.analyze_transcript_for_viral_segments(
            transcript_text, 
            segments,
            requested_clips=max_clips,
            target_platform=target_platform,
            target_duration=target_duration
        )
        
        # Enhanced output formatting
        enhanced_clips = []
        for clip in viral_clips:
            enhanced_clip = {
                'start_time': float(clip['start_time']),
                'end_time': float(clip['end_time']),
                'duration': float(clip['duration']),
                'viral_score': float(clip['viral_score']),
                'hook_type': str(clip['hook_type']),
                'text': str(clip['text']),
                'viral_category': str(clip.get('viral_category', 'standard')),
                'target_demographic': str(clip.get('target_demographic', 'general')),
                'is_fallback': bool(clip.get('is_fallback', False)),
                'selection_method': 'next_generation_ai',
                'quality_metrics': {
                    'hook_strength': float(clip.get('hook_strength', 0)),
                    'emotional_intensity': float(clip.get('emotional_intensity', 0)),
                    'platform_optimization': float(clip.get('platform_optimization', 0)),
                    'psychological_impact': float(clip.get('psychological_impact', 0)),
                    'engagement_prediction': float(clip.get('engagement_prediction', 0)),
                    'share_probability': float(clip.get('share_probability', 0)),
                    'replay_potential': float(clip.get('replay_potential', 0)),
                    'clarity_score': float(clip.get('clarity_score', 0)),
                    'momentum_score': float(clip.get('momentum_score', 0)),
                    'completeness': float(clip.get('completeness_score', 0))
                }
            }
            enhanced_clips.append(enhanced_clip)
        
        print(f"[AI] ✅ Next-generation analysis complete: {len(enhanced_clips)} viral clips generated", file=sys.stderr)
        return enhanced_clips
        
    except Exception as e:
        print(f"[AI] ❌ Enhanced analysis failed: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhanced_viral_analyzer.py <video_path> [max_clips] [platform] [duration]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    max_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    platform = sys.argv[3] if len(sys.argv) > 3 else "tiktok"
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    
    clips = analyze_video_for_viral_clips(video_path, max_clips, platform, duration)
    print(json.dumps(clips, indent=2))
