#!/usr/bin/env python3
"""
🧬 NEUROLOGICAL TRIGGER DETECTION ENGINE
Advanced psychology-based viral content optimization

FEATURES:
- 🧠 Dopamine Trigger Detection
- 🔄 Mirror Neuron Activation Analysis
- 🎯 Curiosity Gap Identification
- ⚡ Pattern Interrupt Recognition
- 👥 Social Proof Detection
- 🎭 Emotional Contagion Analysis
"""

import re
import numpy as np
import pandas as pd
from textblob import TextBlob
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict, Counter
import json
import time
import logging
from typing import Dict, List, Tuple, Any
import cv2
import librosa
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn as nn
from transformers import pipeline
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeurologicalTriggerEngine:
    """
    🧬 NEUROLOGICAL TRIGGER DETECTION ENGINE
    Advanced psychology-based viral content analysis
    """
    
    def __init__(self):
        logger.info("🧬 Initializing Neurological Trigger Engine...")
        
        # Initialize NLP models
        self._initialize_models()
        
        # Define neurological trigger patterns
        self._define_trigger_patterns()
        
        # Initialize psychology databases
        self._initialize_psychology_db()
        
        logger.info("✅ Neurological Trigger Engine Ready!")
    
    def _initialize_models(self):
        """Initialize all NLP and psychology models"""
        try:
            # Sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            # Emotion recognition
            try:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=0 if torch.cuda.is_available() else -1
                )
            except:
                logger.warning("⚠️ Emotion classifier not available")
                self.emotion_classifier = None
            
            # Try to load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("⚠️ spaCy model not found")
                self.nlp = None
            
            # TF-IDF for pattern matching
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            logger.info("✅ Psychology models initialized")
            
        except Exception as e:
            logger.error(f"❌ Model initialization failed: {e}")
            # Initialize minimal fallbacks
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.emotion_classifier = None
            self.nlp = None
    
    def _define_trigger_patterns(self):
        """Define neurological trigger patterns"""
        
        # 🧠 DOPAMINE TRIGGERS - Create anticipation and reward
        self.dopamine_triggers = {
            'high_intensity': [
                r'\b(amazing|incredible|unbelievable|mind[- ]?blowing|extraordinary|phenomenal)\b',
                r'\b(shocking|stunning|jaw[- ]?dropping|breathtaking|explosive)\b',
                r'\b(epic|legendary|insane|crazy|wild|intense)\b',
                r'\b(revolutionary|game[- ]?changing|breakthrough|groundbreaking)\b'
            ],
            'anticipation_builders': [
                r'\bwait until you see\b',
                r'\byou won\'?t believe what happens\b',
                r'\bthis will blow your mind\b',
                r'\bprepare to be amazed\b',
                r'\bget ready for this\b'
            ],
            'reward_signals': [
                r'\bfinally revealed\b',
                r'\bhere\'?s the secret\b',
                r'\bnow watch this\b',
                r'\bthe answer is\b',
                r'\bthis is it\b'
            ]
        }
        
        # 🔄 MIRROR NEURON ACTIVATORS - Create empathy and connection
        self.mirror_neuron_triggers = {
            'first_person_narratives': [
                r'\bi (felt|experienced|discovered|realized|learned)\b',
                r'\bmy (journey|story|experience|transformation)\b',
                r'\bwhen i (was|did|saw|found)\b'
            ],
            'shared_experiences': [
                r'\bwe all (know|feel|experience|remember)\b',
                r'\bif you\'?re like me\b',
                r'\banyone who has ever\b',
                r'\bmost people (think|feel|believe)\b'
            ],
            'emotional_mirroring': [
                r'\bimagine (how|if|being|feeling)\b',
                r'\bpicture this\b',
                r'\bthink about it\b',
                r'\bput yourself in\b'
            ]
        }
        
        # 🎯 CURIOSITY GAPS - Create knowledge gaps that demand closure
        self.curiosity_gap_triggers = {
            'knowledge_gaps': [
                r'\bthe secret (that|to|of|behind)\b',
                r'\bwhat (they|nobody|experts) don\'?t (tell|want|know)\b',
                r'\bthe truth about\b',
                r'\bhidden (truth|secret|fact|reason)\b'
            ],
            'incomplete_information': [
                r'\bbut first\b',
                r'\bbefore (i tell you|we continue|you watch)\b',
                r'\bstay tuned (for|to find out)\b',
                r'\bcoming up next\b'
            ],
            'mystery_creators': [
                r'\bguess what (happened|i found|came next)\b',
                r'\byou\'?ll never guess\b',
                r'\bthe surprising (truth|result|outcome)\b',
                r'\bwhat happens next will\b'
            ]
        }
        
        # ⚡ PATTERN INTERRUPTS - Break expected patterns to grab attention
        self.pattern_interrupt_triggers = {
            'contractions': [
                r'\bbut (actually|wait|here\'?s the thing)\b',
                r'\bhowever[,\s]',
                r'\bactually[,\s]',
                r'\bin reality[,\s]',
                r'\bthe truth is\b'
            ],
            'unexpected_turns': [
                r'\bplot twist\b',
                r'\bhere\'?s the catch\b',
                r'\bstop everything\b',
                r'\bwait[,\s]',
                r'\bhold on\b'
            ],
            'contradiction_signals': [
                r'\bcontrary to (popular )?belief\b',
                r'\bunlike what (most people|you) think\b',
                r'\bit\'?s not what you (think|expect)\b'
            ]
        }
        
        # 👥 SOCIAL PROOF INDICATORS - Leverage social validation
        self.social_proof_triggers = {
            'crowd_validation': [
                r'\bmillions of people\b',
                r'\beveryone is (talking|doing|watching)\b',
                r'\bviral (video|trend|sensation)\b',
                r'\btaking the internet by storm\b'
            ],
            'expert_endorsement': [
                r'\bexperts (say|agree|recommend)\b',
                r'\bscientists (discovered|found|proved)\b',
                r'\bdoctors (recommend|suggest|advise)\b',
                r'\bcelebrities (use|love|endorse)\b'
            ],
            'peer_pressure': [
                r'\bdon\'?t be the only one\b',
                r'\bjoin millions of others\b',
                r'\beveryone else (is|has|knows)\b',
                r'\byou\'?re missing out\b'
            ]
        }
        
        # 🎭 EMOTIONAL CONTAGION TRIGGERS - Spread emotions virally
        self.emotional_contagion_triggers = {
            'high_arousal_positive': [
                r'\b(excited|thrilled|amazed|ecstatic|overjoyed)\b',
                r'\b(incredible|fantastic|awesome|brilliant|outstanding)\b'
            ],
            'high_arousal_negative': [
                r'\b(outraged|furious|shocked|horrified|disgusted)\b',
                r'\b(terrible|awful|disgusting|infuriating|appalling)\b'
            ],
            'surprise_emotions': [
                r'\b(surprised|stunned|amazed|astonished|speechless)\b',
                r'\b(unexpected|sudden|shocking|surprising)\b'
            ]
        }
        
        # 🏆 ACHIEVEMENT TRIGGERS - Create status and accomplishment feelings
        self.achievement_triggers = {
            'success_signals': [
                r'\b(achieved|accomplished|succeeded|won|conquered)\b',
                r'\b(breakthrough|victory|triumph|success|achievement)\b'
            ],
            'transformation_indicators': [
                r'\b(before and after|transformation|changed my life)\b',
                r'\b(from zero to|went from|transformed into)\b'
            ],
            'exclusivity_markers': [
                r'\b(exclusive|limited|secret|private|insider)\b',
                r'\b(only for|special access|behind the scenes)\b'
            ]
        }
    
    def _initialize_psychology_db(self):
        """Initialize psychology pattern databases"""
        
        # Cognitive biases that increase viral potential
        self.cognitive_biases = {
            'confirmation_bias': {
                'patterns': [r'\byou\'?re right to think\b', r'\bas you suspected\b'],
                'viral_multiplier': 1.3
            },
            'availability_heuristic': {
                'patterns': [r'\byou\'?ve probably (seen|heard|noticed)\b'],
                'viral_multiplier': 1.2
            },
            'bandwagon_effect': {
                'patterns': [r'\beveryone is (doing|saying|buying)\b'],
                'viral_multiplier': 1.4
            },
            'loss_aversion': {
                'patterns': [r'\bdon\'?t (miss|lose) out\b', r'\blimited time\b'],
                'viral_multiplier': 1.5
            }
        }
        
        # Psychological hooks ranking
        self.hook_strength_weights = {
            'curiosity_gap': 0.25,
            'dopamine_trigger': 0.20,
            'social_proof': 0.20,
            'mirror_neuron': 0.15,
            'pattern_interrupt': 0.10,
            'emotional_contagion': 0.10
        }
        
        # Viral psychology formulas
        self.viral_formulas = {
            'engagement_prediction': lambda hooks, triggers, emotion: (
                hooks * 0.4 + triggers * 0.3 + emotion * 0.3
            ),
            'share_probability': lambda social_proof, emotion, surprise: (
                social_proof * 0.5 + emotion * 0.3 + surprise * 0.2
            ),
            'retention_score': lambda curiosity, dopamine, narrative: (
                curiosity * 0.4 + dopamine * 0.35 + narrative * 0.25
            )
        }
    
    async def analyze_neurological_triggers(self, text_content, video_path=None, audio_features=None):
        """
        🧬 COMPREHENSIVE NEUROLOGICAL TRIGGER ANALYSIS
        """
        logger.info("🧬 Starting neurological trigger analysis...")
        
        analysis_start = time.time()
        
        # Run all trigger analyses in parallel
        tasks = [
            self._detect_dopamine_triggers(text_content),
            self._detect_mirror_neuron_activators(text_content),
            self._detect_curiosity_gaps(text_content),
            self._detect_pattern_interrupts(text_content),
            self._detect_social_proof(text_content),
            self._detect_emotional_contagion(text_content),
            self._detect_achievement_triggers(text_content),
            self._analyze_cognitive_biases(text_content)
        ]
        
        try:
            results = await asyncio.gather(*tasks)
            
            # Combine all trigger analyses
            comprehensive_analysis = {
                'dopamine_triggers': results[0],
                'mirror_neuron_activators': results[1],
                'curiosity_gaps': results[2],
                'pattern_interrupts': results[3],
                'social_proof': results[4],
                'emotional_contagion': results[5],
                'achievement_triggers': results[6],
                'cognitive_biases': results[7],
                'processing_time': time.time() - analysis_start
            }
            
            # Calculate neurological impact scores
            neurological_scores = self._calculate_neurological_scores(comprehensive_analysis)
            comprehensive_analysis['neurological_scores'] = neurological_scores
            
            # Generate optimization recommendations
            comprehensive_analysis['optimization_recommendations'] = self._generate_trigger_optimizations(comprehensive_analysis)
            
            # Predict viral potential based on triggers
            comprehensive_analysis['viral_prediction'] = self._predict_viral_potential_from_triggers(comprehensive_analysis)
            
            logger.info(f"✅ Neurological analysis complete: {time.time() - analysis_start:.2f}s")
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"❌ Neurological analysis failed: {e}")
            return self._get_fallback_neurological_analysis()
    
    async def _detect_dopamine_triggers(self, text):
        """🧠 Detect dopamine-triggering patterns"""
        try:
            dopamine_analysis = {
                'high_intensity_triggers': [],
                'anticipation_builders': [],
                'reward_signals': [],
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Detect high intensity triggers
            for pattern in self.dopamine_triggers['high_intensity']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    dopamine_analysis['high_intensity_triggers'].append({
                        'trigger': match.group(),
                        'position': match.start(),
                        'intensity': 8.5,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Detect anticipation builders
            for pattern in self.dopamine_triggers['anticipation_builders']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    dopamine_analysis['anticipation_builders'].append({
                        'trigger': match.group(),
                        'position': match.start(),
                        'intensity': 7.5,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Detect reward signals
            for pattern in self.dopamine_triggers['reward_signals']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    dopamine_analysis['reward_signals'].append({
                        'trigger': match.group(),
                        'position': match.start(),
                        'intensity': 9.0,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Calculate total dopamine score
            high_intensity_score = len(dopamine_analysis['high_intensity_triggers']) * 2.0
            anticipation_score = len(dopamine_analysis['anticipation_builders']) * 1.5
            reward_score = len(dopamine_analysis['reward_signals']) * 2.5
            
            dopamine_analysis['total_score'] = min(
                high_intensity_score + anticipation_score + reward_score, 10.0
            )
            
            return dopamine_analysis
            
        except Exception as e:
            logger.error(f"❌ Dopamine trigger detection failed: {e}")
            return {'total_score': 0}
    
    async def _detect_mirror_neuron_activators(self, text):
        """🔄 Detect mirror neuron activation patterns"""
        try:
            mirror_analysis = {
                'first_person_narratives': [],
                'shared_experiences': [],
                'emotional_mirroring': [],
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Detect first person narratives
            for pattern in self.mirror_neuron_triggers['first_person_narratives']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    mirror_analysis['first_person_narratives'].append({
                        'trigger': match.group(),
                        'empathy_score': 7.0,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Detect shared experiences
            for pattern in self.mirror_neuron_triggers['shared_experiences']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    mirror_analysis['shared_experiences'].append({
                        'trigger': match.group(),
                        'empathy_score': 8.0,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Detect emotional mirroring
            for pattern in self.mirror_neuron_triggers['emotional_mirroring']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    mirror_analysis['emotional_mirroring'].append({
                        'trigger': match.group(),
                        'empathy_score': 6.5,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Calculate total mirror neuron score
            narrative_score = len(mirror_analysis['first_person_narratives']) * 1.5
            shared_score = len(mirror_analysis['shared_experiences']) * 2.0
            mirroring_score = len(mirror_analysis['emotional_mirroring']) * 1.0
            
            mirror_analysis['total_score'] = min(
                narrative_score + shared_score + mirroring_score, 10.0
            )
            
            return mirror_analysis
            
        except Exception as e:
            logger.error(f"❌ Mirror neuron detection failed: {e}")
            return {'total_score': 0}
    
    async def _detect_curiosity_gaps(self, text):
        """🎯 Detect curiosity gap patterns"""
        try:
            curiosity_analysis = {
                'knowledge_gaps': [],
                'incomplete_information': [],
                'mystery_creators': [],
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Detect knowledge gaps
            for pattern in self.curiosity_gap_triggers['knowledge_gaps']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    curiosity_analysis['knowledge_gaps'].append({
                        'trigger': match.group(),
                        'curiosity_intensity': 8.5,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Detect incomplete information
            for pattern in self.curiosity_gap_triggers['incomplete_information']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    curiosity_analysis['incomplete_information'].append({
                        'trigger': match.group(),
                        'curiosity_intensity': 7.0,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Detect mystery creators
            for pattern in self.curiosity_gap_triggers['mystery_creators']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    curiosity_analysis['mystery_creators'].append({
                        'trigger': match.group(),
                        'curiosity_intensity': 9.0,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Calculate total curiosity score
            knowledge_score = len(curiosity_analysis['knowledge_gaps']) * 2.5
            incomplete_score = len(curiosity_analysis['incomplete_information']) * 1.5
            mystery_score = len(curiosity_analysis['mystery_creators']) * 3.0
            
            curiosity_analysis['total_score'] = min(
                knowledge_score + incomplete_score + mystery_score, 10.0
            )
            
            return curiosity_analysis
            
        except Exception as e:
            logger.error(f"❌ Curiosity gap detection failed: {e}")
            return {'total_score': 0}
    
    async def _detect_pattern_interrupts(self, text):
        """⚡ Detect pattern interrupt signals"""
        try:
            interrupt_analysis = {
                'contractions': [],
                'unexpected_turns': [],
                'contradiction_signals': [],
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Detect contractions
            for pattern in self.pattern_interrupt_triggers['contractions']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    interrupt_analysis['contractions'].append({
                        'trigger': match.group(),
                        'interrupt_strength': 6.0,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Detect unexpected turns
            for pattern in self.pattern_interrupt_triggers['unexpected_turns']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    interrupt_analysis['unexpected_turns'].append({
                        'trigger': match.group(),
                        'interrupt_strength': 7.5,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Detect contradiction signals
            for pattern in self.pattern_interrupt_triggers['contradiction_signals']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    interrupt_analysis['contradiction_signals'].append({
                        'trigger': match.group(),
                        'interrupt_strength': 8.0,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Calculate total interrupt score
            contraction_score = len(interrupt_analysis['contractions']) * 1.0
            unexpected_score = len(interrupt_analysis['unexpected_turns']) * 1.5
            contradiction_score = len(interrupt_analysis['contradiction_signals']) * 2.0
            
            interrupt_analysis['total_score'] = min(
                contraction_score + unexpected_score + contradiction_score, 10.0
            )
            
            return interrupt_analysis
            
        except Exception as e:
            logger.error(f"❌ Pattern interrupt detection failed: {e}")
            return {'total_score': 0}
    
    async def _detect_social_proof(self, text):
        """👥 Detect social proof indicators"""
        try:
            social_analysis = {
                'crowd_validation': [],
                'expert_endorsement': [],
                'peer_pressure': [],
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Detect crowd validation
            for pattern in self.social_proof_triggers['crowd_validation']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    social_analysis['crowd_validation'].append({
                        'trigger': match.group(),
                        'social_strength': 8.0,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Detect expert endorsement
            for pattern in self.social_proof_triggers['expert_endorsement']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    social_analysis['expert_endorsement'].append({
                        'trigger': match.group(),
                        'social_strength': 9.0,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Detect peer pressure
            for pattern in self.social_proof_triggers['peer_pressure']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    social_analysis['peer_pressure'].append({
                        'trigger': match.group(),
                        'social_strength': 7.5,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Calculate total social proof score
            crowd_score = len(social_analysis['crowd_validation']) * 2.0
            expert_score = len(social_analysis['expert_endorsement']) * 2.5
            peer_score = len(social_analysis['peer_pressure']) * 1.5
            
            social_analysis['total_score'] = min(
                crowd_score + expert_score + peer_score, 10.0
            )
            
            return social_analysis
            
        except Exception as e:
            logger.error(f"❌ Social proof detection failed: {e}")
            return {'total_score': 0}
    
    async def _detect_emotional_contagion(self, text):
        """🎭 Detect emotional contagion patterns"""
        try:
            emotion_analysis = {
                'high_arousal_positive': [],
                'high_arousal_negative': [],
                'surprise_emotions': [],
                'sentiment_intensity': 0,
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Get overall sentiment intensity
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
            emotion_analysis['sentiment_intensity'] = abs(sentiment_scores['compound'])
            
            # Detect high arousal positive emotions
            for pattern in self.emotional_contagion_triggers['high_arousal_positive']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    emotion_analysis['high_arousal_positive'].append({
                        'trigger': match.group(),
                        'emotional_intensity': 8.0,
                        'contagion_potential': 7.5
                    })
            
            # Detect high arousal negative emotions
            for pattern in self.emotional_contagion_triggers['high_arousal_negative']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    emotion_analysis['high_arousal_negative'].append({
                        'trigger': match.group(),
                        'emotional_intensity': 8.5,
                        'contagion_potential': 8.0
                    })
            
            # Detect surprise emotions
            for pattern in self.emotional_contagion_triggers['surprise_emotions']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    emotion_analysis['surprise_emotions'].append({
                        'trigger': match.group(),
                        'emotional_intensity': 7.0,
                        'contagion_potential': 8.5
                    })
            
            # Calculate total emotional contagion score
            positive_score = len(emotion_analysis['high_arousal_positive']) * 1.5
            negative_score = len(emotion_analysis['high_arousal_negative']) * 1.8
            surprise_score = len(emotion_analysis['surprise_emotions']) * 2.0
            sentiment_bonus = emotion_analysis['sentiment_intensity'] * 3.0
            
            emotion_analysis['total_score'] = min(
                positive_score + negative_score + surprise_score + sentiment_bonus, 10.0
            )
            
            return emotion_analysis
            
        except Exception as e:
            logger.error(f"❌ Emotional contagion detection failed: {e}")
            return {'total_score': 0}
    
    async def _detect_achievement_triggers(self, text):
        """🏆 Detect achievement and success triggers"""
        try:
            achievement_analysis = {
                'success_signals': [],
                'transformation_indicators': [],
                'exclusivity_markers': [],
                'total_score': 0
            }
            
            text_lower = text.lower()
            
            # Detect success signals
            for pattern in self.achievement_triggers['success_signals']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    achievement_analysis['success_signals'].append({
                        'trigger': match.group(),
                        'achievement_intensity': 7.5,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Detect transformation indicators
            for pattern in self.achievement_triggers['transformation_indicators']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    achievement_analysis['transformation_indicators'].append({
                        'trigger': match.group(),
                        'achievement_intensity': 8.5,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Detect exclusivity markers
            for pattern in self.achievement_triggers['exclusivity_markers']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    achievement_analysis['exclusivity_markers'].append({
                        'trigger': match.group(),
                        'achievement_intensity': 9.0,
                        'context': text[max(0, match.start()-15):match.end()+15]
                    })
            
            # Calculate total achievement score
            success_score = len(achievement_analysis['success_signals']) * 1.5
            transformation_score = len(achievement_analysis['transformation_indicators']) * 2.0
            exclusivity_score = len(achievement_analysis['exclusivity_markers']) * 2.5
            
            achievement_analysis['total_score'] = min(
                success_score + transformation_score + exclusivity_score, 10.0
            )
            
            return achievement_analysis
            
        except Exception as e:
            logger.error(f"❌ Achievement trigger detection failed: {e}")
            return {'total_score': 0}
    
    async def _analyze_cognitive_biases(self, text):
        """🎯 Analyze cognitive bias exploitation"""
        try:
            bias_analysis = {
                'detected_biases': [],
                'total_score': 0,
                'viral_multiplier': 1.0
            }
            
            text_lower = text.lower()
            
            for bias_name, bias_data in self.cognitive_biases.items():
                for pattern in bias_data['patterns']:
                    matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                    for match in matches:
                        bias_analysis['detected_biases'].append({
                            'bias_type': bias_name,
                            'trigger': match.group(),
                            'viral_multiplier': bias_data['viral_multiplier'],
                            'context': text[max(0, match.start()-20):match.end()+20]
                        })
            
            # Calculate total bias score and viral multiplier
            if bias_analysis['detected_biases']:
                multipliers = [bias['viral_multiplier'] for bias in bias_analysis['detected_biases']]
                bias_analysis['viral_multiplier'] = np.mean(multipliers)
                bias_analysis['total_score'] = min(len(bias_analysis['detected_biases']) * 2.0, 10.0)
            
            return bias_analysis
            
        except Exception as e:
            logger.error(f"❌ Cognitive bias analysis failed: {e}")
            return {'total_score': 0, 'viral_multiplier': 1.0}
    
    def _calculate_neurological_scores(self, analysis_data):
        """📊 Calculate comprehensive neurological impact scores"""
        try:
            scores = {}
            
            # Extract individual trigger scores
            dopamine_score = analysis_data.get('dopamine_triggers', {}).get('total_score', 0)
            mirror_score = analysis_data.get('mirror_neuron_activators', {}).get('total_score', 0)
            curiosity_score = analysis_data.get('curiosity_gaps', {}).get('total_score', 0)
            interrupt_score = analysis_data.get('pattern_interrupts', {}).get('total_score', 0)
            social_score = analysis_data.get('social_proof', {}).get('total_score', 0)
            emotion_score = analysis_data.get('emotional_contagion', {}).get('total_score', 0)
            achievement_score = analysis_data.get('achievement_triggers', {}).get('total_score', 0)
            
            # Calculate weighted neurological impact
            weights = self.hook_strength_weights
            overall_neurological_impact = (
                curiosity_score * weights['curiosity_gap'] +
                dopamine_score * weights['dopamine_trigger'] +
                social_score * weights['social_proof'] +
                mirror_score * weights['mirror_neuron'] +
                interrupt_score * weights['pattern_interrupt'] +
                emotion_score * weights['emotional_contagion']
            )
            
            # Apply cognitive bias multiplier
            bias_multiplier = analysis_data.get('cognitive_biases', {}).get('viral_multiplier', 1.0)
            overall_neurological_impact *= bias_multiplier
            
            scores['overall_neurological_impact'] = min(overall_neurological_impact, 10.0)
            scores['dopamine_impact'] = dopamine_score
            scores['empathy_activation'] = mirror_score
            scores['curiosity_drive'] = curiosity_score
            scores['attention_grab'] = interrupt_score
            scores['social_validation'] = social_score
            scores['emotional_resonance'] = emotion_score
            scores['achievement_appeal'] = achievement_score
            
            # Calculate specific viral metrics using formulas
            scores['engagement_prediction'] = min(
                self.viral_formulas['engagement_prediction'](
                    curiosity_score, dopamine_score, emotion_score
                ), 10.0
            )
            
            scores['share_probability'] = min(
                self.viral_formulas['share_probability'](
                    social_score, emotion_score, interrupt_score
                ), 10.0
            )
            
            scores['retention_score'] = min(
                self.viral_formulas['retention_score'](
                    curiosity_score, dopamine_score, mirror_score
                ), 10.0
            )
            
            return scores
            
        except Exception as e:
            logger.error(f"❌ Neurological score calculation failed: {e}")
            return {'overall_neurological_impact': 5.0}
    
    def _generate_trigger_optimizations(self, analysis_data):
        """💡 Generate optimization recommendations"""
        try:
            recommendations = []
            
            scores = analysis_data.get('neurological_scores', {})
            
            # Dopamine optimization
            if scores.get('dopamine_impact', 0) < 7.0:
                recommendations.append({
                    'type': 'dopamine_enhancement',
                    'priority': 'high',
                    'suggestion': 'Add more anticipation builders like "wait until you see" or "this will blow your mind"',
                    'expected_impact': '+1.5 viral score'
                })
            
            # Curiosity gap optimization
            if scores.get('curiosity_drive', 0) < 6.0:
                recommendations.append({
                    'type': 'curiosity_gap',
                    'priority': 'critical',
                    'suggestion': 'Create knowledge gaps with phrases like "the secret that nobody tells you"',
                    'expected_impact': '+2.0 viral score'
                })
            
            # Social proof optimization
            if scores.get('social_validation', 0) < 5.0:
                recommendations.append({
                    'type': 'social_proof',
                    'priority': 'medium',
                    'suggestion': 'Add social validation like "millions of people are doing this"',
                    'expected_impact': '+1.0 viral score'
                })
            
            # Emotional enhancement
            if scores.get('emotional_resonance', 0) < 6.0:
                recommendations.append({
                    'type': 'emotional_enhancement',
                    'priority': 'high',
                    'suggestion': 'Increase emotional intensity with words like "incredible" or "shocking"',
                    'expected_impact': '+1.2 viral score'
                })
            
            # Pattern interrupts
            if scores.get('attention_grab', 0) < 4.0:
                recommendations.append({
                    'type': 'pattern_interrupt',
                    'priority': 'medium',
                    'suggestion': 'Add attention grabbers like "but wait" or "plot twist"',
                    'expected_impact': '+0.8 viral score'
                })
            
            return sorted(recommendations, key=lambda x: 
                         {'critical': 3, 'high': 2, 'medium': 1}[x['priority']], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Optimization generation failed: {e}")
            return []
    
    def _predict_viral_potential_from_triggers(self, analysis_data):
        """🔮 Predict viral potential based on neurological triggers"""
        try:
            scores = analysis_data.get('neurological_scores', {})
            
            # Base viral prediction
            base_prediction = scores.get('overall_neurological_impact', 5.0)
            
            # Boost for high-impact combinations
            if (scores.get('curiosity_drive', 0) > 7.0 and 
                scores.get('dopamine_impact', 0) > 6.0):
                base_prediction += 1.0
            
            if (scores.get('social_validation', 0) > 6.0 and 
                scores.get('emotional_resonance', 0) > 7.0):
                base_prediction += 0.8
            
            # Apply cognitive bias multiplier
            bias_multiplier = analysis_data.get('cognitive_biases', {}).get('viral_multiplier', 1.0)
            viral_prediction = base_prediction * bias_multiplier
            
            prediction_data = {
                'viral_score': min(viral_prediction, 10.0),
                'confidence': min(scores.get('overall_neurological_impact', 5.0) / 10.0, 1.0),
                'key_drivers': self._identify_key_viral_drivers(scores),
                'viral_category': self._categorize_viral_potential(viral_prediction),
                'time_to_viral': self._estimate_time_to_viral(viral_prediction),
                'platform_recommendations': self._recommend_platforms(analysis_data)
            }
            
            return prediction_data
            
        except Exception as e:
            logger.error(f"❌ Viral prediction failed: {e}")
            return {'viral_score': 5.0, 'confidence': 0.5}
    
    def _identify_key_viral_drivers(self, scores):
        """Identify the strongest neurological drivers"""
        drivers = []
        
        if scores.get('curiosity_drive', 0) > 7.0:
            drivers.append('curiosity_gap')
        if scores.get('dopamine_impact', 0) > 7.0:
            drivers.append('dopamine_triggers')
        if scores.get('social_validation', 0) > 6.0:
            drivers.append('social_proof')
        if scores.get('emotional_resonance', 0) > 7.0:
            drivers.append('emotional_contagion')
        
        return drivers if drivers else ['basic_engagement']
    
    def _categorize_viral_potential(self, viral_score):
        """Categorize viral potential level"""
        if viral_score >= 8.5:
            return 'explosive_viral'
        elif viral_score >= 7.0:
            return 'high_viral'
        elif viral_score >= 5.5:
            return 'moderate_viral'
        else:
            return 'low_viral'
    
    def _estimate_time_to_viral(self, viral_score):
        """Estimate time to reach viral status"""
        if viral_score >= 8.5:
            return '2-6 hours'
        elif viral_score >= 7.0:
            return '6-24 hours'
        elif viral_score >= 5.5:
            return '1-3 days'
        else:
            return '3+ days'
    
    def _recommend_platforms(self, analysis_data):
        """Recommend optimal platforms based on triggers"""
        platform_recommendations = []
        
        scores = analysis_data.get('neurological_scores', {})
        
        # TikTok - high dopamine and emotional content
        if (scores.get('dopamine_impact', 0) > 6.0 and 
            scores.get('emotional_resonance', 0) > 6.0):
            platform_recommendations.append({
                'platform': 'tiktok',
                'suitability': 9.0,
                'reason': 'High dopamine and emotional triggers perfect for TikTok'
            })
        
        # YouTube - curiosity gaps and achievement content
        if (scores.get('curiosity_drive', 0) > 6.0 or 
            scores.get('achievement_appeal', 0) > 5.0):
            platform_recommendations.append({
                'platform': 'youtube',
                'suitability': 8.0,
                'reason': 'Curiosity gaps and achievement content work well on YouTube'
            })
        
        # Instagram - social proof and visual appeal
        if scores.get('social_validation', 0) > 5.0:
            platform_recommendations.append({
                'platform': 'instagram',
                'suitability': 7.5,
                'reason': 'Social proof elements ideal for Instagram engagement'
            })
        
        # Twitter - pattern interrupts and surprise
        if scores.get('attention_grab', 0) > 5.0:
            platform_recommendations.append({
                'platform': 'twitter',
                'suitability': 7.0,
                'reason': 'Pattern interrupts create engagement on Twitter'
            })
        
        return sorted(platform_recommendations, key=lambda x: x['suitability'], reverse=True)
    
    def _get_fallback_neurological_analysis(self):
        """Fallback analysis when main analysis fails"""
        return {
            'neurological_scores': {
                'overall_neurological_impact': 5.0,
                'dopamine_impact': 4.0,
                'empathy_activation': 4.0,
                'curiosity_drive': 4.0,
                'attention_grab': 3.0,
                'social_validation': 3.0,
                'emotional_resonance': 4.0,
                'engagement_prediction': 4.5,
                'share_probability': 4.0,
                'retention_score': 4.5
            },
            'optimization_recommendations': [
                {
                    'type': 'general_enhancement',
                    'priority': 'medium',
                    'suggestion': 'Add more engaging hooks and emotional triggers',
                    'expected_impact': '+1.0 viral score'
                }
            ],
            'viral_prediction': {
                'viral_score': 5.0,
                'confidence': 0.5,
                'viral_category': 'moderate_viral',
                'key_drivers': ['basic_engagement']
            }
        }

# Example usage and testing
if __name__ == "__main__":
    async def main():
        print("🧬 Neurological Trigger Engine - Test Mode")
        
        # Initialize the engine
        trigger_engine = NeurologicalTriggerEngine()
        
        # Test text
        test_text = """
        Wait until you see this incredible transformation! 
        You won't believe what happens next. This amazing discovery 
        will change everything you thought you knew. Scientists are 
        calling it revolutionary, and millions of people are already 
        talking about it. The secret that nobody tells you is about 
        to be revealed. Are you ready for this mind-blowing truth?
        """
        
        # Run analysis
        analysis = await trigger_engine.analyze_neurological_triggers(test_text)
        
        print("\n✅ Neurological Analysis Complete!")
        print(f"🧠 Overall Impact: {analysis['neurological_scores']['overall_neurological_impact']:.1f}/10")
        print(f"🎯 Viral Prediction: {analysis['viral_prediction']['viral_score']:.1f}/10")
        print(f"📈 Category: {analysis['viral_prediction']['viral_category']}")
        print(f"⏰ Time to Viral: {analysis['viral_prediction']['time_to_viral']}")
        
        print("\n🔥 Top Optimization Recommendations:")
        for rec in analysis['optimization_recommendations'][:3]:
            print(f"   {rec['type']}: {rec['suggestion']}")
    
    asyncio.run(main()) 