#!/usr/bin/env python3
"""
PROFESSIONAL MULTI-LAYERED FACE DETECTION AND TRACKING SYSTEM
- Multiple detection models (OpenCV DNN, Haar, MediaPipe)
- Advanced Kalman filtering for smooth tracking
- Face landmark detection for precise centering
- Quality validation and scoring
- Robust fallback mechanisms
"""

import cv2
import json
import sys
import os
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import collections.abc
import librosa
from scipy.signal import butter, filtfilt
import math
from scipy.optimize import minimize
import time

# Try to import MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe not available. Install with: pip install mediapipe")

class KalmanFilter:
    """Advanced Kalman filter for smooth face tracking"""
    def __init__(self, process_noise=0.01, measurement_noise=0.1):
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        
        # State: [x, y, vx, vy] (position and velocity)
        self.state = np.zeros(4)
        self.covariance = np.eye(4) * 100
        
        # Transition matrix (constant velocity model)
        self.F = np.array([[1, 0, 1, 0],
                          [0, 1, 0, 1],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])
        
        # Measurement matrix (we observe position only)
        self.H = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0]])
        
        # Process noise covariance
        self.Q = np.array([[0.25, 0, 0.5, 0],
                          [0, 0.25, 0, 0.5],
                          [0.5, 0, 1, 0],
                          [0, 0.5, 0, 1]]) * process_noise
        
        # Measurement noise covariance
        self.R = np.eye(2) * measurement_noise
        
        self.initialized = False
    
    def predict(self):
        """Predict next state"""
        self.state = self.F @ self.state
        self.covariance = self.F @ self.covariance @ self.F.T + self.Q
        return self.state[:2]  # Return predicted position
    
    def update(self, measurement):
        """Update with new measurement"""
        if not self.initialized:
            self.state[:2] = measurement
            self.initialized = True
            return self.state[:2]
        
        # Predict step
        predicted_state = self.F @ self.state
        predicted_covariance = self.F @ self.covariance @ self.F.T + self.Q
        
        # Update step
        innovation = measurement - self.H @ predicted_state
        innovation_covariance = self.H @ predicted_covariance @ self.H.T + self.R
        kalman_gain = predicted_covariance @ self.H.T @ np.linalg.inv(innovation_covariance)
        
        self.state = predicted_state + kalman_gain @ innovation
        self.covariance = (np.eye(4) - kalman_gain @ self.H) @ predicted_covariance
        
        return self.state[:2]

class ProfessionalFaceTracker:
    """Professional-grade multi-layered face detection and tracking system"""
    
    def __init__(self):
        print("🔧 Initializing Professional Face Tracking System...")
        
        # Initialize multiple detection methods
        self._init_opencv_detectors()
        self._init_mediapipe()
        self._init_dnn_models()
        
        # Tracking state
        self.active_trackers = {}  # face_id -> KalmanFilter
        self.face_history = {}     # face_id -> List[detection_data]
        self.next_face_id = 0
        self.frame_count = 0
        
        # Quality thresholds
        self.min_face_size = 20  # Reduced from 30
        self.max_face_size_ratio = 0.9  # Increased from 0.8
        self.confidence_threshold = 0.1  # Reduced from 0.3
        
        # Centering parameters
        self.target_face_ratio = 0.25  # Face should be 25% of frame height
        self.center_margin = 0.1       # 10% margin from center
        
        # Audio analysis parameters
        self.audio_chunk_duration = 0.1  # 100ms chunks
        self.speaking_threshold = 0.02   # RMS threshold for speech
        
        print("✅ Professional Face Tracking System initialized")
    
    def _init_opencv_detectors(self):
        """Initialize OpenCV cascade classifiers"""
        self.opencv_detectors = {}
        cascade_files = [
            ('frontal_default', cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'),
            ('frontal_alt', cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'),
            ('frontal_alt2', cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'),
            ('profile', cv2.data.haarcascades + 'haarcascade_profileface.xml'),
        ]
        
        for name, path in cascade_files:
            try:
                detector = cv2.CascadeClassifier(path)
                if not detector.empty():
                    self.opencv_detectors[name] = detector
                    print(f"✅ Loaded {name} cascade")
            except:
                print(f"⚠️ Failed to load {name} cascade")
    
    def _init_mediapipe(self):
        """Initialize MediaPipe face detection"""
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
                    model_selection=1,  # 0 for short-range, 1 for full-range
                    min_detection_confidence=0.3
                )
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=3,
                    refine_landmarks=True,
                    min_detection_confidence=0.3,
                    min_tracking_confidence=0.3
                )
                print("✅ MediaPipe face detection initialized")
                self.mediapipe_available = True
            except Exception as e:
                print(f"⚠️ MediaPipe initialization failed: {e}")
                self.mediapipe_available = False
        else:
            self.mediapipe_available = False
    
    def _init_dnn_models(self):
        """Initialize DNN-based face detection models"""
        self.dnn_models = {}
        
        # Try to load OpenCV DNN face detector
        model_paths = [
            ('opencv_dnn', 'opencv_face_detector_uint8.pb', 'opencv_face_detector.pbtxt'),
            ('caffe_dnn', 'deploy.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel'),
        ]
        
        for name, model_file, config_file in model_paths:
            try:
                if os.path.exists(model_file) and os.path.exists(config_file):
                    if name == 'opencv_dnn':
                        net = cv2.dnn.readNetFromTensorflow(model_file, config_file)
                    else:
                        net = cv2.dnn.readNetFromCaffe(config_file, model_file)
                    self.dnn_models[name] = net
                    print(f"✅ Loaded {name} DNN model")
            except Exception as e:
                print(f"⚠️ Failed to load {name}: {e}")
    
    def detect_faces_multi_layer(self, frame, timestamp: float = 0.0) -> List[Dict]:
        """Multi-layered face detection using all available methods"""
        h, w = frame.shape[:2]
        all_detections = []
        
        # Layer 1: MediaPipe Detection (most accurate)
        if self.mediapipe_available:
            mp_faces = self._detect_mediapipe(frame)
            for face in mp_faces:
                face['method'] = 'mediapipe'
                face['layer'] = 1
                face['timestamp'] = timestamp
                all_detections.append(face)
        
        # Layer 2: DNN Models
        for model_name, net in self.dnn_models.items():
            dnn_faces = self._detect_dnn(frame, net, model_name)
            for face in dnn_faces:
                face['method'] = model_name
                face['layer'] = 2
                face['timestamp'] = timestamp
                all_detections.append(face)
        
        # Layer 3: OpenCV Cascade Classifiers
        for detector_name, detector in self.opencv_detectors.items():
            cascade_faces = self._detect_opencv(frame, detector, detector_name)
            for face in cascade_faces:
                face['method'] = detector_name
                face['layer'] = 3
                face['timestamp'] = timestamp
                all_detections.append(face)
        
        # Fusion and validation
        validated_faces = self._validate_and_fuse_detections(all_detections, frame.shape)
        
        # Track faces across frames
        tracked_faces = self._track_faces_advanced(validated_faces, timestamp)
        
        # Score and rank faces
        scored_faces = self._score_faces(tracked_faces, frame)
        
        print(f"🎯 Frame {self.frame_count}: {len(all_detections)} raw → {len(validated_faces)} validated → {len(scored_faces)} final")
        self.frame_count += 1
        
        return scored_faces
    
    def _detect_mediapipe(self, frame) -> List[Dict]:
        """MediaPipe face detection with landmarks"""
        faces = []
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_face_detection.process(rgb_frame)
            
            if results.detections:
                h, w = frame.shape[:2]
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    # Ensure valid coordinates
                    x = max(0, x)
                    y = max(0, y)
                    width = min(width, w - x)
                    height = min(height, h - y)
                    
                    # Get face landmarks for better centering
                    landmarks = self._get_face_landmarks(frame, x, y, width, height)
                    
                    faces.append({
                        'x': x, 'y': y, 'width': width, 'height': height,
                        'confidence': detection.score[0],
                        'landmarks': landmarks,
                        'quality_score': self._calculate_quality_score(frame, x, y, width, height)
                    })
        except Exception as e:
            print(f"MediaPipe detection error: {e}")
        
        return faces
    
    def _get_face_landmarks(self, frame, x, y, w, h) -> Dict:
        """Extract face landmarks for precise centering"""
        landmarks = {}
        try:
            if self.mediapipe_available:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.mp_face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    h_img, w_img = frame.shape[:2]
                    
                    # Key landmark indices
                    LEFT_EYE = 33
                    RIGHT_EYE = 263
                    NOSE_TIP = 1
                    MOUTH_CENTER = 13
                    
                    landmarks['left_eye'] = (
                        int(face_landmarks.landmark[LEFT_EYE].x * w_img),
                        int(face_landmarks.landmark[LEFT_EYE].y * h_img)
                    )
                    landmarks['right_eye'] = (
                        int(face_landmarks.landmark[RIGHT_EYE].x * w_img),
                        int(face_landmarks.landmark[RIGHT_EYE].y * h_img)
                    )
                    landmarks['nose'] = (
                        int(face_landmarks.landmark[NOSE_TIP].x * w_img),
                        int(face_landmarks.landmark[NOSE_TIP].y * h_img)
                    )
                    landmarks['mouth'] = (
                        int(face_landmarks.landmark[MOUTH_CENTER].x * w_img),
                        int(face_landmarks.landmark[MOUTH_CENTER].y * h_img)
                    )
                    
                    # Calculate face center from landmarks
                    if all(key in landmarks for key in ['left_eye', 'right_eye', 'nose']):
                        eye_center_x = (landmarks['left_eye'][0] + landmarks['right_eye'][0]) // 2
                        eye_center_y = (landmarks['left_eye'][1] + landmarks['right_eye'][1]) // 2
                        landmarks['face_center'] = (
                            (eye_center_x + landmarks['nose'][0]) // 2,
                            (eye_center_y + landmarks['nose'][1]) // 2
                        )
        except Exception as e:
            print(f"Landmark detection error: {e}")
        
        return landmarks
    
    def _detect_dnn(self, frame, net, model_name) -> List[Dict]:
        """DNN-based face detection"""
        faces = []
        try:
            h, w = frame.shape[:2]
            
            if model_name == 'opencv_dnn':
                blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
                net.setInput(blob)
                detections = net.forward()
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.1:  # Lowered from 0.2 to 0.1
                        x1 = int(detections[0, 0, i, 3] * w)
                        y1 = int(detections[0, 0, i, 4] * h)
                        x2 = int(detections[0, 0, i, 5] * w)
                        y2 = int(detections[0, 0, i, 6] * h)
                        
                        x, y = max(0, x1), max(0, y1)
                        width = min(x2 - x1, w - x)
                        height = min(y2 - y1, h - y)
                        
                        if width > 0 and height > 0:
                            faces.append({
                                'x': x, 'y': y, 'width': width, 'height': height,
                                'confidence': float(confidence),
                                'landmarks': {},
                                'quality_score': self._calculate_quality_score(frame, x, y, width, height)
                            })
            
            elif model_name == 'caffe_dnn':
                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
                net.setInput(blob)
                detections = net.forward()
                
                for i in range(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.1:  # Lowered from 0.2 to 0.1
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        x, y, x2, y2 = box.astype("int")
                        
                        x, y = max(0, x), max(0, y)
                        width = min(x2 - x, w - x)
                        height = min(y2 - y, h - y)
                        
                        if width > 0 and height > 0:
                            faces.append({
                                'x': x, 'y': y, 'width': width, 'height': height,
                                'confidence': float(confidence),
                                'landmarks': {},
                                'quality_score': self._calculate_quality_score(frame, x, y, width, height)
                            })
        
        except Exception as e:
            print(f"DNN detection error ({model_name}): {e}")
        
        return faces
    
    def _detect_opencv(self, frame, detector, detector_name) -> List[Dict]:
        """OpenCV cascade-based face detection"""
        faces = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            # Multiple scale factors for better detection
            scale_factors = [1.05, 1.1, 1.15]
            min_neighbors_list = [3, 4, 5]
            
            for scale_factor in scale_factors:
                for min_neighbors in min_neighbors_list:
                    detections = detector.detectMultiScale(
                        gray,
                        scaleFactor=scale_factor,
                        minNeighbors=min_neighbors,
                        minSize=(self.min_face_size, self.min_face_size),
                        maxSize=(int(frame.shape[1] * self.max_face_size_ratio), 
                                int(frame.shape[0] * self.max_face_size_ratio)),
                        flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_CANNY_PRUNING
                    )
                    
                    for (x, y, w, h) in detections:
                        # Calculate confidence based on detection quality
                        confidence = self._calculate_cascade_confidence(gray, x, y, w, h, scale_factor, min_neighbors)
                        
                        faces.append({
                            'x': x, 'y': y, 'width': w, 'height': h,
                            'confidence': confidence,
                            'landmarks': {},
                            'quality_score': self._calculate_quality_score(frame, x, y, w, h),
                            'scale_factor': scale_factor,
                            'min_neighbors': min_neighbors
                        })
        
        except Exception as e:
            print(f"OpenCV detection error ({detector_name}): {e}")
        
        return faces
    
    def _calculate_cascade_confidence(self, gray_frame, x, y, w, h, scale_factor, min_neighbors):
        """Calculate confidence score for cascade detection"""
        try:
            # Base confidence from parameters
            base_conf = 0.5 + (min_neighbors - 3) * 0.1 + (1.15 - scale_factor) * 0.5
            
            # Size factor (prefer medium-sized faces)
            frame_area = gray_frame.shape[0] * gray_frame.shape[1]
            face_area = w * h
            size_ratio = face_area / frame_area
            optimal_ratio = 0.15
            size_factor = 1.0 - abs(size_ratio - optimal_ratio) / optimal_ratio
            size_factor = max(0.1, min(1.0, size_factor))
            
            # Position factor (slight preference for center)
            center_x = x + w/2
            center_y = y + h/2
            frame_center_x = gray_frame.shape[1] / 2
            frame_center_y = gray_frame.shape[0] / 2
            distance_from_center = np.sqrt((center_x - frame_center_x)**2 + (center_y - frame_center_y)**2)
            max_distance = np.sqrt((gray_frame.shape[1]/2)**2 + (gray_frame.shape[0]/2)**2)
            position_factor = 1.0 - (distance_from_center / max_distance) * 0.2
            
            # Image quality factor
            face_roi = gray_frame[y:y+h, x:x+w]
            if face_roi.size > 0:
                sharpness = cv2.Laplacian(face_roi, cv2.CV_64F).var()
                quality_factor = min(1.0, sharpness / 1000)  # Normalize sharpness
            else:
                quality_factor = 0.5
            
            confidence = base_conf * size_factor * position_factor * quality_factor
            return max(0.1, min(1.0, confidence))
        
        except:
            return 0.5
    
    def _calculate_quality_score(self, frame, x, y, w, h) -> float:
        """Calculate quality score for face detection"""
        try:
            if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
                return 0.0
            
            face_roi = frame[y:y+h, x:x+w]
            if face_roi.size == 0:
                return 0.0
            
            # Convert to grayscale for analysis
            gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 500)
            
            # Contrast (standard deviation)
            contrast = np.std(gray_roi)
            contrast_score = min(1.0, contrast / 50)
            
            # Brightness (avoid too dark or too bright)
            brightness = np.mean(gray_roi)
            brightness_score = 1.0 - abs(brightness - 128) / 128
            
            # Size score (prefer medium sizes)
            frame_area = frame.shape[0] * frame.shape[1]
            face_area = w * h
            size_ratio = face_area / frame_area
            optimal_size = 0.15
            size_score = 1.0 - abs(size_ratio - optimal_size) / optimal_size
            size_score = max(0.0, min(1.0, size_score))
            
            # Overall quality
            quality = (sharpness_score * 0.3 + contrast_score * 0.2 + 
                      brightness_score * 0.2 + size_score * 0.3)
            
            return max(0.0, min(1.0, quality))
        
        except:
            return 0.0
    
    def _validate_and_fuse_detections(self, detections: List[Dict], frame_shape: Tuple) -> List[Dict]:
        """Validate and fuse multiple detections"""
        if not detections:
            return []
        
        h, w = frame_shape[:2]
        valid_detections = []
        
        # Filter out invalid detections
        for detection in detections:
            if self._is_valid_detection(detection, w, h):
                valid_detections.append(detection)
        
        if not valid_detections:
            return []
        
        # Group overlapping detections
        groups = self._group_overlapping_detections(valid_detections)
        
        # Fuse each group into a single detection
        fused_detections = []
        for group in groups:
            fused = self._fuse_detection_group(group)
            if fused:
                fused_detections.append(fused)
        
        return fused_detections
    
    def _is_valid_detection(self, detection: Dict, frame_width: int, frame_height: int) -> bool:
        """Validate individual detection"""
        x, y, w, h = detection['x'], detection['y'], detection['width'], detection['height']
        
        # Check bounds
        if x < 0 or y < 0 or x + w > frame_width or y + h > frame_height:
            return False
        
        # Check minimum size
        if w < self.min_face_size or h < self.min_face_size:
            return False
        
        # Check maximum size
        max_size = min(frame_width, frame_height) * self.max_face_size_ratio
        if w > max_size or h > max_size:
            return False
        
        # Check aspect ratio (faces should be roughly square)
        aspect_ratio = w / h
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            return False
        
        # Check confidence
        if detection['confidence'] < self.confidence_threshold:
            return False
        
        return True
    
    def _group_overlapping_detections(self, detections: List[Dict]) -> List[List[Dict]]:
        """Group overlapping detections using clustering"""
        if len(detections) <= 1:
            return [detections] if detections else []
        
        groups = []
        used = set()
        
        for i, det1 in enumerate(detections):
            if i in used:
                continue
            
            group = [det1]
            used.add(i)
            
            for j, det2 in enumerate(detections[i+1:], i+1):
                if j in used:
                    continue
                
                overlap = self._calculate_overlap_ratio(det1, det2)
                if overlap > 0.3:  # 30% overlap threshold
                    group.append(det2)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_overlap_ratio(self, det1: Dict, det2: Dict) -> float:
        """Calculate IoU (Intersection over Union) of two detections"""
        x1_1, y1_1 = det1['x'], det1['y']
        x2_1, y2_1 = x1_1 + det1['width'], y1_1 + det1['height']
        
        x1_2, y1_2 = det2['x'], det2['y']
        x2_2, y2_2 = x1_2 + det2['width'], y1_2 + det2['height']
        
        # Calculate intersection
        x_overlap = max(0, min(x2_1, x2_2) - max(x1_1, x1_2))
        y_overlap = max(0, min(y2_1, y2_2) - max(y1_1, y1_2))
        intersection = x_overlap * y_overlap
        
        # Calculate union
        area1 = det1['width'] * det1['height']
        area2 = det2['width'] * det2['height']
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _fuse_detection_group(self, group: List[Dict]) -> Optional[Dict]:
        """Fuse a group of overlapping detections"""
        if not group:
            return None
        
        if len(group) == 1:
            return group[0]
        
        # Weight detections by confidence and quality
        weights = []
        for det in group:
            # Prioritize MediaPipe and DNN detections
            layer_weight = {1: 3.0, 2: 2.0, 3: 1.0}.get(det.get('layer', 3), 1.0)
            weight = det['confidence'] * det['quality_score'] * layer_weight
            weights.append(weight)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return group[0]  # Fallback to first detection
        
        # Weighted average of coordinates
        x = sum(det['x'] * w for det, w in zip(group, weights)) / total_weight
        y = sum(det['y'] * w for det, w in zip(group, weights)) / total_weight
        width = sum(det['width'] * w for det, w in zip(group, weights)) / total_weight
        height = sum(det['height'] * w for det, w in zip(group, weights)) / total_weight
        
        # Best confidence and quality from the group
        best_confidence = max(det['confidence'] for det in group)
        best_quality = max(det['quality_score'] for det in group)
        
        # Combine landmarks if available
        landmarks = {}
        for det in group:
            if det['landmarks']:
                landmarks.update(det['landmarks'])
        
        # Use method from highest layer detection
        best_layer = min(det.get('layer', 3) for det in group)
        best_method = next(det['method'] for det in group if det.get('layer', 3) == best_layer)
        
        return {
            'x': int(x),
            'y': int(y),
            'width': int(width),
            'height': int(height),
            'confidence': best_confidence,
            'quality_score': best_quality,
            'landmarks': landmarks,
            'method': f"fused_{best_method}",
            'layer': best_layer,
            'fused_count': len(group)
        }
    
    def extract_audio_features(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """Extract audio features to identify speaking activity"""
        try:
            # Load audio
            audio, sr = librosa.load(video_path, sr=22050, offset=start_time, duration=end_time-start_time)
            
            # Calculate RMS energy over time
            hop_length = int(sr * self.audio_chunk_duration)
            rms = librosa.feature.rms(y=audio, hop_length=hop_length, frame_length=hop_length*2)[0]
            
            # Calculate spectral centroid (brightness indicator)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=hop_length)[0]
            
            # Calculate MFCC features (speech characteristics)
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, hop_length=hop_length)
            
            # Time stamps for each audio frame
            time_frames = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
            
            # Detect speaking activity (enhanced with spectral features)
            speaking_frames = (rms > self.speaking_threshold) & (spectral_centroid > np.mean(spectral_centroid) * 0.5)
            
            return {
                'time_frames': time_frames + start_time,  # Absolute timestamps
                'rms_energy': rms,
                'spectral_centroid': spectral_centroid,
                'mfccs': mfccs,
                'speaking_activity': speaking_frames,
                'audio_duration': end_time - start_time,
                'sample_rate': sr
            }
        except Exception as e:
            print(f"⚠️ Audio analysis failed: {e}")
            return None
    
    def detect_faces_advanced(self, frame, timestamp: float = 0.0):
        """Advanced face detection using OpenCV methods with improved scoring"""
        h, w = frame.shape[:2]
        all_faces = []
        
        # Method 1: DNN-based detection (most accurate if available)
        if self.use_dnn:
            try:
                blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
                self.net.setInput(blob)
                detections = self.net.forward()
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.3:  # Lowered from 0.5 to 0.3
                        x1 = int(detections[0, 0, i, 3] * w)
                        y1 = int(detections[0, 0, i, 4] * h)
                        x2 = int(detections[0, 0, i, 5] * w)
                        y2 = int(detections[0, 0, i, 6] * h)
                        
                        # Ensure valid coordinates
                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(w, x2)
                        y2 = min(h, y2)
                        
                        if x2 > x1 and y2 > y1:
                            all_faces.append({
                                'x': x1, 'y': y1, 'width': x2-x1, 'height': y2-y1,
                                'confidence': confidence,
                                'method': 'dnn',
                                'timestamp': timestamp
                            })
            except Exception as e:
                print(f"DNN detection error: {e}")
        
        # Method 2: Haar Cascade methods (fallback or primary if no DNN)
        # Always try Haar cascades regardless of DNN results for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better detection
        gray = cv2.equalizeHist(gray)
        
        # More aggressive cascade parameters for better detection
        cascade_methods = [
            (self.face_cascade_default, 'haar_default', 1.05, 2),  # More sensitive
            (self.face_cascade_alt, 'haar_alt', 1.03, 2),         # More sensitive
            (self.face_cascade_alt2, 'haar_alt2', 1.05, 2),       # More sensitive
            (self.profile_cascade, 'haar_profile', 1.03, 3)        # More sensitive
        ]
        
        for cascade, method_name, scale_factor, min_neighbors in cascade_methods:
            faces = cascade.detectMultiScale(
                gray, 
                scaleFactor=scale_factor, 
                minNeighbors=min_neighbors, 
                minSize=(20, 20),                          # Reduced from (30, 30)
                maxSize=(int(w*0.9), int(h*0.9)),         # Increased from 0.8 to 0.9
                flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_CANNY_PRUNING
            )
            
            print(f"🔍 {method_name}: Found {len(faces)} faces")  # Debug info
            
            for (x, y, fw, fh) in faces:
                # Enhanced confidence calculation
                face_area = fw * fh
                frame_area = w * h
                
                # Size factor (prefer medium-sized faces)
                optimal_face_ratio = 0.15  # 15% of frame
                size_ratio = face_area / frame_area
                size_factor = 1.0 - abs(size_ratio - optimal_face_ratio) / optimal_face_ratio
                size_factor = max(0.1, min(1.0, size_factor))  # Reduced min from 0.2 to 0.1
                
                # Position factor (prefer center faces slightly)
                center_x = x + fw/2
                center_y = y + fh/2
                frame_center_x = w / 2
                frame_center_y = h / 2
                position_factor = 1.0 - (abs(center_x - frame_center_x) + abs(center_y - frame_center_y)) / (w + h)
                position_factor = max(0.3, position_factor)  # Reduced min from 0.5 to 0.3
                
                # Base confidence based on method
                base_confidence = 0.8 if method_name == 'haar_default' else 0.7
                confidence = base_confidence * size_factor * position_factor
                
                all_faces.append({
                    'x': x, 'y': y, 'width': fw, 'height': fh,
                    'confidence': confidence,
                    'method': method_name,
                    'timestamp': timestamp,
                    'size_factor': size_factor,
                    'position_factor': position_factor
                })
        
        print(f"🎯 Total faces detected: {len(all_faces)}")  # Debug info
        
        # Remove duplicate detections
        unique_faces = self._remove_duplicate_faces_advanced(all_faces)
        
        print(f"✅ Unique faces after deduplication: {len(unique_faces)}")  # Debug info
        
        # Track faces across frames
        tracked_faces = self._track_faces_advanced(unique_faces, timestamp)
        
        return tracked_faces
    
    def estimate_mouth_activity(self, frame, face_bbox: Dict) -> float:
        """Estimate mouth/speaking activity using basic image processing"""
        try:
            x, y, w, h = face_bbox['x'], face_bbox['y'], face_bbox['width'], face_bbox['height']
            
            # Extract lower face region (mouth area)
            mouth_y_start = int(y + h * 0.6)  # Lower 40% of face
            mouth_y_end = int(y + h * 0.9)
            mouth_x_start = int(x + w * 0.25)  # Center 50% horizontally
            mouth_x_end = int(x + w * 0.75)
            
            # Ensure valid coordinates
            mouth_y_start = max(0, min(mouth_y_start, frame.shape[0]))
            mouth_y_end = max(mouth_y_start, min(mouth_y_end, frame.shape[0]))
            mouth_x_start = max(0, min(mouth_x_start, frame.shape[1]))
            mouth_x_end = max(mouth_x_start, min(mouth_x_end, frame.shape[1]))
            
            if mouth_y_end <= mouth_y_start or mouth_x_end <= mouth_x_start:
                return 0.0
            
            mouth_region = frame[mouth_y_start:mouth_y_end, mouth_x_start:mouth_x_end]
            gray_mouth = cv2.cvtColor(mouth_region, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture variance (speaking tends to create more texture/movement)
            laplacian_var = cv2.Laplacian(gray_mouth, cv2.CV_64F).var()
            
            # Normalize based on face size
            normalized_activity = min(1.0, laplacian_var / (w * h * 0.1))
            
            return normalized_activity
        except Exception as e:
            return 0.0
    
    def _track_faces_advanced(self, detections: List[Dict], timestamp: float) -> List[Dict]:
        """Advanced face tracking with Kalman filtering"""
        if not detections:
            return []
        
        # Initialize new trackers for new faces
        self._match_and_update_trackers(detections, timestamp)
        
        # Apply Kalman filtering to tracked faces
        tracked_faces = []
        for detection in detections:
            face_id = detection.get('face_id', -1)
            if face_id in self.active_trackers:
                tracker = self.active_trackers[face_id]
                
                # Current position
                current_pos = np.array([
                    detection['x'] + detection['width'] / 2,
                    detection['y'] + detection['height'] / 2
                ])
                
                # Update tracker
                smoothed_pos = tracker.update(current_pos)
                
                # Update detection with smoothed position
                detection['smoothed_x'] = smoothed_pos[0] - detection['width'] / 2
                detection['smoothed_y'] = smoothed_pos[1] - detection['height'] / 2
                detection['face_id'] = face_id
                
                # Add tracking quality
                detection['tracking_quality'] = self._assess_tracking_quality(face_id, detection)
                
                tracked_faces.append(detection)
        
        # Clean up old trackers
        self._cleanup_trackers(timestamp)
        
        return tracked_faces
    
    def _match_and_update_trackers(self, detections: List[Dict], timestamp: float):
        """Match detections to existing trackers or create new ones"""
        # Predict positions for existing trackers
        predictions = {}
        for face_id, tracker in self.active_trackers.items():
            predictions[face_id] = tracker.predict()
        
        # Match detections to predictions
        used_trackers = set()
        for detection in detections:
            center = np.array([
                detection['x'] + detection['width'] / 2,
                detection['y'] + detection['height'] / 2
            ])
            
            best_match = None
            best_distance = float('inf')
            
            for face_id, predicted_pos in predictions.items():
                if face_id in used_trackers:
                    continue
                
                distance = np.linalg.norm(center - predicted_pos)
                # Consider size similarity as well
                if face_id in self.face_history:
                    last_detection = self.face_history[face_id][-1]
                    size_diff = abs(detection['width'] - last_detection['width']) / last_detection['width']
                    adjusted_distance = distance * (1 + size_diff)
                else:
                    adjusted_distance = distance
                
                if adjusted_distance < best_distance and adjusted_distance < 150:  # Max movement threshold
                    best_distance = adjusted_distance
                    best_match = face_id
            
            if best_match is not None:
                detection['face_id'] = best_match
                used_trackers.add(best_match)
                
                # Update history
                if best_match not in self.face_history:
                    self.face_history[best_match] = []
                self.face_history[best_match].append({
                    'timestamp': timestamp,
                    'x': detection['x'],
                    'y': detection['y'],
                    'width': detection['width'],
                    'height': detection['height'],
                    'confidence': detection['confidence'],
                    'quality_score': detection['quality_score']
                })
                
                # Keep only recent history
                if len(self.face_history[best_match]) > 30:
                    self.face_history[best_match] = self.face_history[best_match][-30:]
            else:
                # Create new tracker
                new_id = self.next_face_id
                self.next_face_id += 1
                
                detection['face_id'] = new_id
                self.active_trackers[new_id] = KalmanFilter()
                self.face_history[new_id] = [{
                    'timestamp': timestamp,
                    'x': detection['x'],
                    'y': detection['y'],
                    'width': detection['width'],
                    'height': detection['height'],
                    'confidence': detection['confidence'],
                    'quality_score': detection['quality_score']
                }]
    
    def _assess_tracking_quality(self, face_id: int, detection: Dict) -> float:
        """Assess quality of face tracking"""
        if face_id not in self.face_history:
            return 0.5
        
        history = self.face_history[face_id]
        if len(history) < 2:
            return 0.5
        
        # Consistency in size
        sizes = [h['width'] * h['height'] for h in history[-10:]]
        size_variance = np.var(sizes) if len(sizes) > 1 else 0
        size_consistency = max(0, 1.0 - size_variance / 10000)
        
        # Smoothness of movement
        if len(history) >= 3:
            positions = [(h['x'] + h['width']/2, h['y'] + h['height']/2) for h in history[-5:]]
            velocities = []
            for i in range(1, len(positions)):
                dx = positions[i][0] - positions[i-1][0]
                dy = positions[i][1] - positions[i-1][1]
                velocities.append(math.sqrt(dx*dx + dy*dy))
            
            velocity_variance = np.var(velocities) if len(velocities) > 1 else 0
            movement_smoothness = max(0, 1.0 - velocity_variance / 1000)
        else:
            movement_smoothness = 0.5
        
        # Detection consistency
        confidences = [h['confidence'] for h in history[-10:]]
        avg_confidence = np.mean(confidences)
        
        # Overall tracking quality
        quality = (size_consistency * 0.3 + movement_smoothness * 0.4 + avg_confidence * 0.3)
        return max(0.0, min(1.0, quality))
    
    def _cleanup_trackers(self, current_timestamp: float):
        """Remove trackers that haven't been updated recently"""
        timeout = 2.0  # 2 seconds timeout
        to_remove = []
        
        for face_id, history in self.face_history.items():
            if history and current_timestamp - history[-1]['timestamp'] > timeout:
                to_remove.append(face_id)
        
        for face_id in to_remove:
            if face_id in self.active_trackers:
                del self.active_trackers[face_id]
            if face_id in self.face_history:
                del self.face_history[face_id]
    
    def _score_faces(self, faces: List[Dict], frame) -> List[Dict]:
        """Score and rank faces for primary speaker detection"""
        for face in faces:
            # Base score from detection confidence and quality
            base_score = (face['confidence'] + face['quality_score']) / 2
            
            # Tracking quality bonus
            tracking_bonus = face.get('tracking_quality', 0.5) * 0.3
            
            # Size preference (medium-sized faces)
            frame_area = frame.shape[0] * frame.shape[1]
            face_area = face['width'] * face['height']
            size_ratio = face_area / frame_area
            optimal_ratio = self.target_face_ratio
            size_score = 1.0 - abs(size_ratio - optimal_ratio) / optimal_ratio
            size_score = max(0.0, min(1.0, size_score))
            size_bonus = size_score * 0.2
            
            # Center preference
            face_center_x = face['x'] + face['width'] / 2
            face_center_y = face['y'] + face['height'] / 2
            frame_center_x = frame.shape[1] / 2
            frame_center_y = frame.shape[0] / 2
            
            distance_from_center = math.sqrt(
                (face_center_x - frame_center_x)**2 + (face_center_y - frame_center_y)**2
            )
            max_distance = math.sqrt((frame.shape[1]/2)**2 + (frame.shape[0]/2)**2)
            center_score = 1.0 - (distance_from_center / max_distance)
            center_bonus = center_score * 0.1
            
            # Landmark bonus
            landmark_bonus = 0.1 if face['landmarks'] else 0.0
            
            # Fusion bonus (multiple detectors agreed)
            fusion_bonus = 0.1 if face.get('fused_count', 1) > 1 else 0.0
            
            # Final score
            face['overall_score'] = (base_score + tracking_bonus + size_bonus + 
                                   center_bonus + landmark_bonus + fusion_bonus)
        
        # Sort by score (highest first)
        faces.sort(key=lambda f: f['overall_score'], reverse=True)
        
        return faces
    
    def analyze_video_clip_professional(self, video_path: str, start_time: float, end_time: float, 
                                      target_width: int = 1080, target_height: int = 1920) -> Dict:
        """Professional video analysis with multi-layered face detection and precision centering"""
        print(f"🎯 Starting PROFESSIONAL face detection analysis...")
        
        # Extract audio features
        audio_features = self.extract_audio_features(video_path, start_time, end_time)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "Could not open video file"}
        
        # Video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Frame range
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        all_frame_data = []
        frame_count = 0
        total_frames = end_frame - start_frame
        
        # Intelligent sampling strategy
        if total_frames > 120:  # For longer clips, sample more intelligently
            sample_interval = max(1, total_frames // 60)  # Target 60 samples
        else:
            sample_interval = 1  # Analyze every frame for short clips
        
        print(f"🔍 Analyzing {total_frames} frames with interval {sample_interval}...")
        
        while cap.isOpened() and frame_count < total_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_timestamp = start_time + (frame_count / fps)
            
            if frame_count % sample_interval == 0:
                # Multi-layered face detection
                faces = self.detect_faces_multi_layer(frame, current_timestamp)
                
                # Correlate with audio if available
                if audio_features:
                    faces = self._correlate_with_audio(faces, audio_features, current_timestamp)
                
                all_frame_data.append({
                    'timestamp': current_timestamp,
                    'faces': faces,
                    'frame_number': start_frame + frame_count,
                    'frame_quality': self._assess_frame_quality(frame)
                })
                
                if len(all_frame_data) % 10 == 0:
                    print(f"  📊 Processed {len(all_frame_data)} frames...")
            
            frame_count += 1
        
        cap.release()
        
        if not all_frame_data:
            return self._get_fallback_crop_params(video_width, video_height, target_width, target_height)
        
        # Identify primary speaker
        primary_speaker = self._identify_primary_speaker(all_frame_data)
        
        # Generate precision tracking path
        tracking_path = self._generate_precision_tracking_path(all_frame_data, primary_speaker)
        
        # Calculate precision crop parameters with face centering
        crop_params = self._calculate_precision_crop_params(
            tracking_path, video_width, video_height, target_width, target_height, primary_speaker
        )
        
        result = self._to_json_serializable({
            "video_width": video_width,
            "video_height": video_height,
            "target_width": target_width,
            "target_height": target_height,
            "clip_duration": end_time - start_time,
            "primary_speaker_id": primary_speaker['face_id'] if primary_speaker else None,
            "speaker_confidence": primary_speaker['confidence'] if primary_speaker else 0.0,
            "detection_method": primary_speaker['method'] if primary_speaker else 'none',
            "tracking_path": tracking_path,
            "crop_params": crop_params,
            "frames_analyzed": len(all_frame_data),
            "audio_analysis_available": audio_features is not None,
            "quality_assessment": self._assess_overall_quality(all_frame_data, primary_speaker),
            "professional_features": {
                "multi_layer_detection": True,
                "kalman_filtering": True,
                "landmark_centering": bool(primary_speaker and primary_speaker.get('landmarks')),
                "audio_correlation": audio_features is not None,
                "precision_tracking": True
            }
        })
        
        print(f"✅ PROFESSIONAL analysis complete!")
        if primary_speaker:
            print(f"🎤 Primary speaker detected (ID: {primary_speaker['face_id']}, method: {primary_speaker['method']}, confidence: {primary_speaker['confidence']:.2f})")
            print(f"📐 Precision crop: x={crop_params['crop_x']}, y={crop_params['crop_y']}, size={crop_params['crop_width']}x{crop_params['crop_height']}")
        
        return result
    
    def _correlate_with_audio(self, faces: List[Dict], audio_features: Dict, timestamp: float) -> List[Dict]:
        """Enhanced audio-visual correlation for speaker identification"""
        if not audio_features or not faces:
            return faces
        
        # Find closest audio frame
        audio_times = audio_features['time_frames']
        closest_idx = np.argmin(np.abs(audio_times - timestamp))
        
        # Audio activity at this timestamp
        is_speaking = audio_features['speaking_activity'][closest_idx]
        audio_energy = audio_features['rms_energy'][closest_idx]
        spectral_centroid = audio_features['spectral_centroid'][closest_idx]
        
        for face in faces:
            # Audio correlation score
            if is_speaking:
                audio_score = min(1.0, audio_energy * 10)  # Normalize
                spectral_score = min(1.0, spectral_centroid / 2000)
                face['audio_correlation'] = (audio_score + spectral_score) / 2
                face['is_speaking_frame'] = True
            else:
                face['audio_correlation'] = 0.0
                face['is_speaking_frame'] = False
            
            # Store audio features
            face['audio_energy'] = float(audio_energy)
            face['spectral_centroid'] = float(spectral_centroid)
        
        return faces
    
    def _assess_frame_quality(self, frame) -> float:
        """Assess overall frame quality"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Sharpness
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 100)
            
            # Brightness
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 128) / 128
            
            # Contrast
            contrast = np.std(gray)
            contrast_score = min(1.0, contrast / 50)
            
            return (sharpness_score + brightness_score + contrast_score) / 3
        except:
            return 0.5
    
    def _identify_primary_speaker(self, frame_data: List[Dict]) -> Optional[Dict]:
        """Identify the primary speaker using comprehensive analysis"""
        if not frame_data:
            return None
        
        # Collect all face appearances
        face_stats = {}
        
        for frame in frame_data:
            for face in frame['faces']:
                face_id = face.get('face_id', -1)
                if face_id == -1:
                    continue
                
                if face_id not in face_stats:
                    face_stats[face_id] = {
                        'appearances': 0,
                        'total_confidence': 0.0,
                        'total_quality': 0.0,
                        'total_overall_score': 0.0,
                        'audio_correlation_sum': 0.0,
                        'speaking_frames': 0,
                        'tracking_quality_sum': 0.0,
                        'best_detection': None,
                        'method': face.get('method', 'unknown'),
                        'has_landmarks': bool(face.get('landmarks'))
                    }
                
                stats = face_stats[face_id]
                stats['appearances'] += 1
                stats['total_confidence'] += face['confidence']
                stats['total_quality'] += face['quality_score']
                stats['total_overall_score'] += face.get('overall_score', 0.5)
                stats['audio_correlation_sum'] += face.get('audio_correlation', 0.0)
                stats['tracking_quality_sum'] += face.get('tracking_quality', 0.5)
                
                if face.get('is_speaking_frame', False):
                    stats['speaking_frames'] += 1
                
                # Keep best detection for this face
                if (stats['best_detection'] is None or 
                    face.get('overall_score', 0) > stats['best_detection'].get('overall_score', 0)):
                    stats['best_detection'] = face
        
        if not face_stats:
            return None
        
        # Score each face
        min_appearances = max(2, len(frame_data) // 20)  # Must appear in at least 5% of frames
        candidates = []
        
        for face_id, stats in face_stats.items():
            if stats['appearances'] < min_appearances:
                continue
            
            # Average scores
            avg_confidence = stats['total_confidence'] / stats['appearances']
            avg_quality = stats['total_quality'] / stats['appearances']
            avg_overall_score = stats['total_overall_score'] / stats['appearances']
            avg_audio_correlation = stats['audio_correlation_sum'] / stats['appearances']
            avg_tracking_quality = stats['tracking_quality_sum'] / stats['appearances']
            
            # Speaking ratio
            speaking_ratio = stats['speaking_frames'] / stats['appearances']
            
            # Consistency bonus (more appearances = more consistent)
            consistency_score = min(1.0, stats['appearances'] / len(frame_data))
            
            # Method bonus (prefer more advanced detection methods)
            method_bonus = {
                'mediapipe': 1.0,
                'fused_mediapipe': 1.1,
                'opencv_dnn': 0.9,
                'caffe_dnn': 0.9,
                'fused_opencv_dnn': 0.95,
                'fused_caffe_dnn': 0.95
            }.get(stats['method'], 0.7)
            
            # Landmark bonus
            landmark_bonus = 0.1 if stats['has_landmarks'] else 0.0
            
            # Final primary speaker score
            primary_score = (
                avg_confidence * 0.15 +
                avg_quality * 0.15 +
                avg_overall_score * 0.2 +
                avg_audio_correlation * 0.2 +
                speaking_ratio * 0.15 +
                consistency_score * 0.1 +
                avg_tracking_quality * 0.05
            ) * method_bonus + landmark_bonus
            
            candidates.append({
                'face_id': face_id,
                'primary_score': primary_score,
                'confidence': avg_confidence,
                'quality_score': avg_quality,
                'speaking_ratio': speaking_ratio,
                'appearances': stats['appearances'],
                'method': stats['method'],
                'landmarks': stats['best_detection'].get('landmarks', {}),
                'best_detection': stats['best_detection']
            })
        
        if not candidates:
            return None
        
        # Return the best candidate
        best_candidate = max(candidates, key=lambda c: c['primary_score'])
        
        print(f"🎤 Primary speaker analysis:")
        print(f"   Face ID: {best_candidate['face_id']}")
        print(f"   Score: {best_candidate['primary_score']:.3f}")
        print(f"   Method: {best_candidate['method']}")
        print(f"   Speaking ratio: {best_candidate['speaking_ratio']:.2f}")
        print(f"   Appearances: {best_candidate['appearances']}/{len(frame_data)}")
        
        return best_candidate
    
    def _generate_precision_tracking_path(self, frame_data: List[Dict], primary_speaker: Optional[Dict]) -> List[Dict]:
        """Generate precision tracking path with face centering"""
        if not primary_speaker:
            return []
        
        speaker_id = primary_speaker['face_id']
        tracking_points = []
        
        # Extract speaker positions
        for frame in frame_data:
            speaker_face = None
            for face in frame['faces']:
                if face.get('face_id') == speaker_id:
                    speaker_face = face
                    break
            
            if speaker_face:
                # Use smoothed position if available, otherwise original
                if 'smoothed_x' in speaker_face:
                    center_x = speaker_face['smoothed_x'] + speaker_face['width'] / 2
                    center_y = speaker_face['smoothed_y'] + speaker_face['height'] / 2
                else:
                    center_x = speaker_face['x'] + speaker_face['width'] / 2
                    center_y = speaker_face['y'] + speaker_face['height'] / 2
                
                # Use landmark-based center if available
                if speaker_face['landmarks'] and 'face_center' in speaker_face['landmarks']:
                    landmark_center = speaker_face['landmarks']['face_center']
                    # Blend landmark center with detection center
                    center_x = (center_x + landmark_center[0]) / 2
                    center_y = (center_y + landmark_center[1]) / 2
                
                tracking_points.append({
                    'timestamp': frame['timestamp'],
                    'face_x': center_x,
                    'face_y': center_y,
                    'face_width': speaker_face['width'],
                    'face_height': speaker_face['height'],
                    'confidence': speaker_face['confidence'],
                    'quality_score': speaker_face['quality_score'],
                    'tracking_quality': speaker_face.get('tracking_quality', 0.5),
                    'is_speaking': speaker_face.get('is_speaking_frame', False),
                    'audio_correlation': speaker_face.get('audio_correlation', 0.0),
                    'has_landmarks': bool(speaker_face['landmarks'])
                })
        
        # Apply advanced smoothing
        return self._apply_precision_smoothing(tracking_points)
    
    def _apply_precision_smoothing(self, tracking_points: List[Dict]) -> List[Dict]:
        """Apply precision smoothing with multiple techniques"""
        if len(tracking_points) < 3:
            return tracking_points
        
        # Extract coordinates
        x_coords = [p['face_x'] for p in tracking_points]
        y_coords = [p['face_y'] for p in tracking_points]
        
        # 1. Gaussian smoothing
        x_gaussian = self._gaussian_smooth(x_coords, sigma=1.5)
        y_gaussian = self._gaussian_smooth(y_coords, sigma=1.5)
        
        # 2. Kalman smoothing for ultra-smooth tracking
        x_kalman = self._kalman_smooth(x_gaussian)
        y_kalman = self._kalman_smooth(y_gaussian)
        
        # 3. Momentum-based smoothing
        x_final = self._apply_momentum(x_kalman, factor=0.8)
        y_final = self._apply_momentum(y_kalman, factor=0.8)
        
        # Update tracking points
        for i, point in enumerate(tracking_points):
            point['face_x'] = float(x_final[i])
            point['face_y'] = float(y_final[i])
        
        return tracking_points
    
    def _gaussian_smooth(self, data: List[float], sigma: float) -> List[float]:
        """Enhanced Gaussian smoothing"""
        if len(data) < 3:
            return data
        
        # Adaptive kernel size based on data length
        kernel_size = min(len(data) // 2, int(6 * sigma + 1))
        if kernel_size % 2 == 0:
            kernel_size += 1
        kernel_size = max(3, kernel_size)
        
        # Create Gaussian kernel
        x = np.arange(-(kernel_size // 2), kernel_size // 2 + 1)
        kernel = np.exp(-(x**2) / (2 * sigma**2))
        kernel = kernel / np.sum(kernel)
        
        # Apply convolution with reflection padding
        data_array = np.array(data)
        pad_width = kernel_size // 2
        padded_data = np.pad(data_array, pad_width, mode='reflect')
        smoothed = np.convolve(padded_data, kernel, mode='same')
        
        return smoothed[pad_width:-pad_width].tolist()
    
    def _kalman_smooth(self, data: List[float]) -> List[float]:
        """Apply Kalman smoothing for ultra-smooth tracking"""
        if len(data) < 2:
            return data
        
        # Simple 1D Kalman filter for position smoothing
        smoothed = [data[0]]
        estimate = data[0]
        estimate_error = 1.0
        
        for measurement in data[1:]:
            # Prediction step
            prediction = estimate
            prediction_error = estimate_error + 0.1  # Process noise
            
            # Update step
            kalman_gain = prediction_error / (prediction_error + 0.5)  # Measurement noise
            estimate = prediction + kalman_gain * (measurement - prediction)
            estimate_error = (1 - kalman_gain) * prediction_error
            
            smoothed.append(estimate)
        
        return smoothed
    
    def _apply_momentum(self, data: List[float], factor: float = 0.7) -> List[float]:
        """Apply momentum-based smoothing"""
        if len(data) < 3:
            return data
        
        smoothed = [data[0], data[1]]
        velocity = data[1] - data[0]
        
        for i in range(2, len(data)):
            # Calculate desired movement
            target_velocity = data[i] - smoothed[-1]
            
            # Apply momentum
            velocity = velocity * factor + target_velocity * (1 - factor)
            new_position = smoothed[-1] + velocity
            
            smoothed.append(new_position)
        
        return smoothed
    
    def _calculate_precision_crop_params(self, tracking_path: List[Dict], video_width: int, video_height: int,
                                       target_width: int, target_height: int, primary_speaker: Optional[Dict]) -> Dict:
        """Calculate precision crop parameters with perfect face centering"""
        if not tracking_path or not primary_speaker:
            return self._get_fallback_crop_params(video_width, video_height, target_width, target_height)
        
        # Target aspect ratio
        target_aspect = target_width / target_height
        
        # Calculate crop dimensions
        if video_height * target_aspect <= video_width:
            # Video is wide enough, crop horizontally
            crop_height = video_height
            crop_width = int(video_height * target_aspect)
        else:
            # Video is too narrow, crop vertically
            crop_width = video_width
            crop_height = int(video_width / target_aspect)
        
        # Calculate weighted average position (exponential weighting favoring recent frames)
        weights = np.exp(np.linspace(0, 2, len(tracking_path)))
        total_weight = np.sum(weights)
        
        x_positions = [p['face_x'] for p in tracking_path]
        y_positions = [p['face_y'] for p in tracking_path]
        face_widths = [p['face_width'] for p in tracking_path]
        face_heights = [p['face_height'] for p in tracking_path]
        
        # Weighted averages
        avg_face_x = np.average(x_positions, weights=weights)
        avg_face_y = np.average(y_positions, weights=weights)
        avg_face_width = np.average(face_widths, weights=weights)
        avg_face_height = np.average(face_heights, weights=weights)
        
        # Target face size (should be about 25% of crop height)
        target_face_height = crop_height * self.target_face_ratio
        face_scale_factor = target_face_height / avg_face_height if avg_face_height > 0 else 1.0
        
        # Calculate optimal crop position to center the face
        # Face should be centered horizontally and positioned in upper third vertically
        target_face_x_in_crop = crop_width / 2
        target_face_y_in_crop = crop_height * 0.35  # Slightly above center
        
        crop_x = avg_face_x - target_face_x_in_crop
        crop_y = avg_face_y - target_face_y_in_crop
        
        # Ensure crop stays within video bounds with smart constraints
        margin = min(video_width, video_height) * 0.02  # 2% margin
        crop_x = max(margin, min(crop_x, video_width - crop_width - margin))
        crop_y = max(margin, min(crop_y, video_height - crop_height - margin))
        
        # Calculate quality metrics
        position_variance_x = np.var(x_positions) if len(x_positions) > 1 else 0
        position_variance_y = np.var(y_positions) if len(y_positions) > 1 else 0
        avg_confidence = np.mean([p['confidence'] for p in tracking_path])
        avg_quality = np.mean([p['quality_score'] for p in tracking_path])
        speaking_frames = sum(1 for p in tracking_path if p.get('is_speaking', False))
        speaking_ratio = speaking_frames / len(tracking_path)
        
        # Tracking smoothness score
        movements = []
        for i in range(1, len(tracking_path)):
            dx = tracking_path[i]['face_x'] - tracking_path[i-1]['face_x']
            dy = tracking_path[i]['face_y'] - tracking_path[i-1]['face_y']
            movements.append(math.sqrt(dx*dx + dy*dy))
        
        movement_variance = np.var(movements) if len(movements) > 1 else 0
        smoothness_score = max(0.0, 1.0 - movement_variance / 100)
        
        return {
            "crop_x": int(crop_x),
            "crop_y": int(crop_y),
            "crop_width": crop_width,
            "crop_height": crop_height,
            "tracking_method": "professional_precision_tracking",
            "face_detection_confidence": float(avg_confidence),
            "face_quality_score": float(avg_quality),
            "dynamic_tracking": True,
            "speaking_person_tracking": True,
            "precision_centering": True,
            "landmark_guided": any(p.get('has_landmarks', False) for p in tracking_path),
            "kalman_filtered": True,
            "multi_layer_detection": True,
            "position_variance_x": float(position_variance_x),
            "position_variance_y": float(position_variance_y),
            "speaking_ratio": float(speaking_ratio),
            "smoothness_score": float(smoothness_score),
            "tracking_points": len(tracking_path),
            "face_scale_factor": float(face_scale_factor),
            "primary_speaker_method": primary_speaker.get('method', 'unknown'),
            "centering_accuracy": self._calculate_centering_accuracy(tracking_path, crop_x, crop_y, crop_width, crop_height)
        }
    
    def _calculate_centering_accuracy(self, tracking_path: List[Dict], crop_x: int, crop_y: int, 
                                    crop_width: int, crop_height: int) -> float:
        """Calculate how well the crop centers the face"""
        if not tracking_path:
            return 0.0
        
        target_center_x = crop_x + crop_width / 2
        target_center_y = crop_y + crop_height * 0.35  # Target position
        
        deviations = []
        for point in tracking_path:
            face_x, face_y = point['face_x'], point['face_y']
            deviation = math.sqrt((face_x - target_center_x)**2 + (face_y - target_center_y)**2)
            # Normalize by crop size
            normalized_deviation = deviation / math.sqrt(crop_width**2 + crop_height**2)
            deviations.append(normalized_deviation)
        
        avg_deviation = np.mean(deviations)
        accuracy = max(0.0, 1.0 - avg_deviation * 4)  # Scale factor
        return float(accuracy)
    
    def _get_fallback_crop_params(self, video_width: int, video_height: int, 
                                target_width: int, target_height: int) -> Dict:
        """Fallback to center crop with professional metadata"""
        target_aspect = target_width / target_height
        
        if video_height * target_aspect <= video_width:
            crop_height = video_height
            crop_width = int(video_height * target_aspect)
        else:
            crop_width = video_width
            crop_height = int(video_width / target_aspect)
        
        crop_x = (video_width - crop_width) // 2
        crop_y = (video_height - crop_height) // 2
        
        return {
            "crop_x": crop_x,
            "crop_y": crop_y,
            "crop_width": crop_width,
            "crop_height": crop_height,
            "tracking_method": "center_crop_fallback",
            "face_detection_confidence": 0.0,
            "dynamic_tracking": False,
            "speaking_person_tracking": False,
            "precision_centering": False,
            "error": "No primary speaker detected - using center crop"
        }
    
    def _assess_overall_quality(self, frame_data: List[Dict], primary_speaker: Optional[Dict]) -> Dict:
        """Assess overall quality of the analysis"""
        if not frame_data:
            return {"quality": "poor", "reason": "no_frames_analyzed"}
        
        if not primary_speaker:
            return {"quality": "poor", "reason": "no_primary_speaker_detected"}
        
        # Calculate quality metrics
        speaker_appearances = primary_speaker['appearances']
        total_frames = len(frame_data)
        coverage = speaker_appearances / total_frames
        
        avg_confidence = primary_speaker['confidence']
        speaking_ratio = primary_speaker['speaking_ratio']
        
        # Overall quality score
        quality_score = (coverage * 0.4 + avg_confidence * 0.3 + speaking_ratio * 0.3)
        
        if quality_score > 0.8:
            quality = "excellent"
        elif quality_score > 0.6:
            quality = "good"
        elif quality_score > 0.4:
            quality = "fair"
        else:
            quality = "poor"
        
        return {
            "quality": quality,
            "overall_score": float(quality_score),
            "coverage": float(coverage),
            "confidence": float(avg_confidence),
            "speaking_ratio": float(speaking_ratio),
            "frames_analyzed": total_frames,
            "speaker_appearances": speaker_appearances,
            "detection_method": primary_speaker.get('method', 'unknown')
        }
    
    def _to_json_serializable(self, obj):
        """Convert numpy types to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_json_serializable(v) for v in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

# Backward compatibility classes
class AdvancedSpeakingPersonTracker(ProfessionalFaceTracker):
    def analyze_video_clip_speaking_person(self, video_path: str, start_time: float, end_time: float, 
                                         target_width: int = 1080, target_height: int = 1920) -> Dict:
        """Backward compatibility method - redirects to professional analysis"""
        return self.analyze_video_clip_professional(video_path, start_time, end_time, target_width, target_height)

class EnhancedFaceCenteredCropper(ProfessionalFaceTracker):
    def analyze_video_clip_enhanced(self, video_path: str, start_time: float, end_time: float, 
                                   target_width: int = 1080, target_height: int = 1920) -> Dict:
        """Redirect to professional analysis"""
        return self.analyze_video_clip_professional(video_path, start_time, end_time, target_width, target_height)

class FaceCenteredCropper(ProfessionalFaceTracker):
    def analyze_video_clip(self, video_path: str, start_time: float, end_time: float, 
                          target_width: int = 1080, target_height: int = 1920) -> Dict:
        """Redirect to professional analysis"""
        return self.analyze_video_clip_professional(video_path, start_time, end_time, target_width, target_height)

def main():
    if len(sys.argv) != 5:
        print("Usage: python face_detection.py <video_path> <start_time> <end_time> <output_json_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    start_time = float(sys.argv[2])
    end_time = float(sys.argv[3])
    output_path = sys.argv[4]
    
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found")
        sys.exit(1)
    
    # Initialize professional tracker
    tracker = ProfessionalFaceTracker()
    
    # Analyze with professional system
    result = tracker.analyze_video_clip_professional(video_path, start_time, end_time)
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    else:
        print(f"🎯 PROFESSIONAL analysis complete!")
        crop_params = result['crop_params']
        quality = result['quality_assessment']
        
        print(f"📐 Precision crop: x={crop_params['crop_x']}, y={crop_params['crop_y']}, "
              f"size={crop_params['crop_width']}x{crop_params['crop_height']}")
        print(f"🔍 Method: {crop_params['tracking_method']}")
        print(f"🎤 Speaker detected: {crop_params.get('speaking_person_tracking', False)}")
        print(f"📊 Speaking ratio: {crop_params.get('speaking_ratio', 0):.2f}")
        print(f"✨ Overall quality: {quality['quality']} (score: {quality.get('overall_score', 0):.2f})")
        print(f"🎯 Centering accuracy: {crop_params.get('centering_accuracy', 0):.2f}")
        print(f"🎪 Features: Precision={crop_params.get('precision_centering', False)}, "
              f"Landmarks={crop_params.get('landmark_guided', False)}, "
              f"Kalman={crop_params.get('kalman_filtered', False)}")

if __name__ == "__main__":
    main() 