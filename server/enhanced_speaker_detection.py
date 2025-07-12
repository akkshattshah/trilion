#!/usr/bin/env python3
"""
Enhanced Speaker Detection System
Determines if video contains visible speaking person or is content-based (text/graphics)
"""

import cv2
import numpy as np
import sys
import json
import tempfile
import os
import subprocess
from pathlib import Path
import mediapipe as mp
import argparse
import logging

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def extract_video_frames(video_path, start_time, end_time, sample_rate=1):
    """Extract every frame from video for analysis (absolute best)"""
    frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return frames
    fps = cap.get(cv2.CAP_PROP_FPS)
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_count = start_frame
    while frame_count < end_frame and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        frame_count += 1
    cap.release()
    return frames

def detect_faces_in_frame(frame):
    """Detect faces in a single frame using MediaPipe"""
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            results = face_detection.process(rgb_frame)
            faces = []
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x = int(bboxC.xmin * iw)
                    y = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)
                    faces.append((x, y, w, h))
            return len(faces), faces
    except Exception as e:
        print(f"MediaPipe face detection error: {e}", file=sys.stderr)
        return 0, []

def analyze_content_type(frames):
    """Analyze if content is text/graphics based or person-based"""
    text_indicators = 0
    graphics_indicators = 0
    
    for frame in frames:
        height, width = frame.shape[:2]
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Check for text-like patterns (high contrast edges)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (height * width)
        
        # Check for solid color regions (common in text overlays)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_peaks = len([i for i, count in enumerate(hist) if count > height * width * 0.1])
        
        # High edge density + few color peaks = likely text/graphics
        if edge_density > 0.05 and hist_peaks < 5:
            text_indicators += 1
        
        # Check for graphics patterns
        # Look for uniform regions and geometric patterns
        blur = cv2.GaussianBlur(gray, (15, 15), 0)
        diff = cv2.absdiff(gray, blur)
        uniform_regions = np.sum(diff < 10) / (height * width)
        
        if uniform_regions > 0.7:  # Lots of uniform regions
            graphics_indicators += 1
    
    return text_indicators, graphics_indicators

def enhanced_speaker_detection(video_path, start_time, end_time, output_path):
    """
    Enhanced speaker detection that determines video content type
    Returns analysis with processing recommendation
    """
    try:
        print(f"[SPEAKER_DETECT] Analyzing video content type for: {os.path.basename(video_path)}", file=sys.stderr)
        
        # Extract sample frames
        frames = extract_video_frames(video_path, start_time, end_time, sample_rate=2)
        
        if not frames:
            result = {
                'error': 'Could not extract frames from video',
                'processing_method': 'resize',  # Default to safe option
                'confidence': 0.0
            }
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            return
        
        print(f"[SPEAKER_DETECT] Extracted {len(frames)} frames for analysis", file=sys.stderr)
        
        # Analyze for faces across all frames
        total_faces = 0
        face_frames = 0
        largest_face_area = 0
        face_positions = []
        all_face_boxes = []
        
        for i, frame in enumerate(frames):
            face_count, faces = detect_faces_in_frame(frame)
            
            if face_count > 0:
                face_frames += 1
                total_faces += face_count
                
                # Track largest face for cropping reference
                for (x, y, w, h) in faces:
                    face_area = w * h
                    if face_area > largest_face_area:
                        largest_face_area = face_area
                        # Store face position as percentage of frame
                        frame_height, frame_width = frame.shape[:2]
                        face_positions.append({
                            'x_percent': (x + w/2) / frame_width,
                            'y_percent': (y + h/2) / frame_height,
                            'width_percent': w / frame_width,
                            'height_percent': h / frame_height,
                            'area': face_area
                        })
                # Use the largest face in this frame
                largest = max(faces, key=lambda f: f[2]*f[3])
                x, y, w, h = largest
                all_face_boxes.append((x, y, w, h))
        
        # Analyze content type
        text_indicators, graphics_indicators = analyze_content_type(frames)
        
        # Calculate detection metrics
        face_frequency = face_frames / len(frames) if frames else 0
        avg_faces_per_frame = total_faces / len(frames) if frames else 0
        
        # Get video dimensions for analysis
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        # Decision logic
        has_visible_speaker = False
        processing_method = 'resize'  # Default
        confidence = 0.0
        reasoning = []
        
        # Face detection analysis
        if face_frequency > 0.3:  # Faces in >30% of frames
            has_visible_speaker = True
            confidence += 0.4
            reasoning.append(f"Faces detected in {face_frequency:.1%} of frames")
        
        if avg_faces_per_frame >= 0.5:  # Average of 0.5+ faces per frame
            has_visible_speaker = True
            confidence += 0.3
            reasoning.append(f"Average {avg_faces_per_frame:.1f} faces per frame")
        
        # Content type analysis
        text_ratio = text_indicators / len(frames) if frames else 0
        graphics_ratio = graphics_indicators / len(frames) if frames else 0
        
        if text_ratio > 0.6:  # >60% frames look like text/graphics
            has_visible_speaker = False
            confidence += 0.4
            reasoning.append(f"High text/graphics content detected ({text_ratio:.1%})")
        
        if graphics_ratio > 0.7:  # >70% frames are graphics-heavy
            has_visible_speaker = False
            confidence += 0.3
            reasoning.append(f"High graphics content detected ({graphics_ratio:.1%})")
        
        # Face size analysis (if faces detected)
        if face_positions:
            avg_face_size = np.mean([pos['width_percent'] * pos['height_percent'] for pos in face_positions])
            if avg_face_size > 0.05:  # Face takes up >5% of frame
                has_visible_speaker = True
                confidence += 0.2
                reasoning.append(f"Significant face size detected ({avg_face_size:.1%} of frame)")
        
        # Final decision
        if has_visible_speaker and confidence > 0.5:
            processing_method = 'crop'
            confidence = min(confidence, 1.0)
        else:
            processing_method = 'resize'
            confidence = max(0.1, 1.0 - confidence)
        
        # Compute robust crop box if faces detected
        crop_params = None
        if all_face_boxes:
            # Compute the tightest box that contains all faces, with padding
            x0 = min([x for x, y, w, h in all_face_boxes])
            y0 = min([y for x, y, w, h in all_face_boxes])
            x1 = max([x+w for x, y, w, h in all_face_boxes])
            y1 = max([y+h for x, y, w, h in all_face_boxes])
            # Add padding (10% of width/height)
            pad_x = int(0.10 * (x1 - x0))
            pad_y = int(0.15 * (y1 - y0))
            crop_x = max(0, x0 - pad_x)
            crop_y = max(0, y0 - pad_y)
            crop_x2 = x1 + pad_x
            crop_y2 = y1 + pad_y
            # Get video dimensions
            cap = cv2.VideoCapture(video_path)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            crop_x2 = min(frame_width, crop_x2)
            crop_y2 = min(frame_height, crop_y2)
            crop_width = crop_x2 - crop_x
            crop_height = crop_y2 - crop_y
            # If crop box is out of bounds, shift inward
            if crop_x < 0: crop_x = 0
            if crop_y < 0: crop_y = 0
            if crop_x + crop_width > frame_width:
                crop_x = frame_width - crop_width
            if crop_y + crop_height > frame_height:
                crop_y = frame_height - crop_height
            crop_params = {
                'crop_x': int(crop_x),
                'crop_y': int(crop_y),
                'crop_width': int(crop_width),
                'crop_height': int(crop_height),
                'face_detection_confidence': float(confidence)
            }
            # Optional: Save debug image
            try:
                debug_img = frames[len(frames)//2].copy()
                cv2.rectangle(debug_img, (crop_x, crop_y), (crop_x+crop_width, crop_y+crop_height), (0,255,0), 3)
                for (x, y, w, h) in all_face_boxes:
                    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (255,0,0), 2)
                cv2.imwrite('debug_crop_box.jpg', debug_img)
            except Exception as e:
                print(f"Debug image save failed: {e}", file=sys.stderr)
        else:
            # Fallback: center crop
            crop_params = {
                'crop_x': int((frame_width - int(frame_width * 9/16)) / 2),
                'crop_y': 0,
                'crop_width': int(frame_width * 9/16),
                'crop_height': frame_height,
                'face_detection_confidence': 0.0
            }
        
        # Prepare result
        result = {
            'has_visible_speaker': has_visible_speaker,
            'processing_method': processing_method,
            'confidence': confidence,
            'face_detection_stats': {
                'faces_detected': total_faces,
                'face_frequency': face_frequency,
                'avg_faces_per_frame': avg_faces_per_frame,
                'frames_analyzed': len(frames)
            },
            'content_analysis': {
                'text_indicators': text_ratio,
                'graphics_indicators': graphics_ratio,
                'likely_content_type': 'text/graphics' if not has_visible_speaker else 'person/speaker'
            },
            'reasoning': reasoning,
            'crop_params': crop_params,
            'video_dimensions': {
                'width': frame_width,
                'height': frame_height,
                'aspect_ratio': frame_width / frame_height
            }
        }
        
        print(f"[SPEAKER_DETECT] Analysis complete:", file=sys.stderr)
        print(f"  - Content type: {result['content_analysis']['likely_content_type']}", file=sys.stderr)
        print(f"  - Processing method: {processing_method}", file=sys.stderr)
        print(f"  - Confidence: {confidence:.2f}", file=sys.stderr)
        print(f"  - Reasoning: {'; '.join(reasoning)}", file=sys.stderr)
        
        # Save result
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
    except Exception as e:
        print(f"[SPEAKER_DETECT] Error during analysis: {e}", file=sys.stderr)
        # Fallback result
        result = {
            'error': str(e),
            'processing_method': 'resize',  # Safe default
            'confidence': 0.0,
            'has_visible_speaker': False
        }
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

def dynamic_face_crop(video_path, output_path, target_aspect=9/16, padding=0.35, out_res=(720, 1280)):
    """
    Dynamic per-frame face tracking and cropping using MediaPipe.
    Always outputs a true 9:16 vertical video (default 720x1280). Adds black bars if needed.
    """
    import mediapipe as mp
    import cv2
    import numpy as np

    mp_face_detection = mp.solutions.face_detection

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    face_boxes = []
    frames = []

    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        for _ in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)
            if results.detections:
                largest = max(results.detections, key=lambda d: d.location_data.relative_bounding_box.width * d.location_data.relative_bounding_box.height)
                bboxC = largest.location_data.relative_bounding_box
                x = int(bboxC.xmin * frame_width)
                y = int(bboxC.ymin * frame_height)
                w = int(bboxC.width * frame_width)
                h = int(bboxC.height * frame_height)
                face_boxes.append((x, y, w, h))
            else:
                face_boxes.append(None)
    cap.release()

    for i in range(len(face_boxes)):
        if face_boxes[i] is None:
            prev = next = None
            for j in range(i-1, -1, -1):
                if face_boxes[j] is not None:
                    prev = face_boxes[j]
                    break
            for j in range(i+1, len(face_boxes)):
                if face_boxes[j] is not None:
                    next = face_boxes[j]
                    break
            if prev and next:
                face_boxes[i] = tuple(int((p+n)/2) for p, n in zip(prev, next))
            elif prev:
                face_boxes[i] = prev
            elif next:
                face_boxes[i] = next
            else:
                face_boxes[i] = (frame_width//2, frame_height//2, frame_width//3, frame_height//2)

    window = 5
    smoothed_boxes = []
    for i in range(len(face_boxes)):
        x, y, w, h = 0, 0, 0, 0
        count = 0
        for j in range(max(0, i-window), min(len(face_boxes), i+window+1)):
            bx, by, bw, bh = face_boxes[j]
            x += bx
            y += by
            w += bw
            h += bh
            count += 1
        smoothed_boxes.append((x//count, y//count, w//count, h//count))

    out_w, out_h = out_res  # e.g., (720, 1280) for 9:16
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

    # -------------------------------------------------------------
    # Set up logging to a file alongside the output video so that
    # every run has its own detailed crop log for debugging.
    # -------------------------------------------------------------
    log_file = os.path.splitext(output_path)[0] + "_crop.log"
    logger = logging.getLogger("dynamic_face_crop")
    logger.setLevel(logging.DEBUG)
    # Avoid duplicate handlers when function is called multiple times
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == log_file for h in logger.handlers):
        fh = logging.FileHandler(log_file, mode='w')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.info(f"START dynamic_face_crop | video={video_path} | output={output_path}")

    detection_ratio = sum(1 for b in face_boxes if b is not None) / len(face_boxes) if face_boxes else 0
    crop_mode = detection_ratio >= 0.2  # Only crop when faces are present in >=20% of frames
    logger.info(f"Face detection ratio: {detection_ratio:.2%} | crop_mode={'ON' if crop_mode else 'OFF'}")

    if not crop_mode:
        logger.warning("Not enough face detections – falling back to full-frame rescale mode")
        for idx, frame in enumerate(frames):
            frame_aspect = frame_width / frame_height
            target_aspect = out_w / out_h
            if abs(frame_aspect - target_aspect) < 0.01:
                resized = cv2.resize(frame, (out_w, out_h))
            elif frame_aspect > target_aspect:
                new_w = out_w
                new_h = int(out_w / frame_aspect)
                resized = cv2.resize(frame, (new_w, new_h))
                pad_top = (out_h - new_h) // 2
                pad_bottom = out_h - new_h - pad_top
                resized = cv2.copyMakeBorder(resized, pad_top, pad_bottom, 0, 0, cv2.BORDER_CONSTANT, value=[0,0,0])
            else:
                new_h = out_h
                new_w = int(out_h * frame_aspect)
                resized = cv2.resize(frame, (new_w, new_h))
                pad_left = (out_w - new_w) // 2
                pad_right = out_w - new_w - pad_left
                resized = cv2.copyMakeBorder(resized, 0, 0, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0,0,0])
            if idx % 30 == 0:  # Log roughly every second of video
                logger.debug(f"Frame {idx}: RESCALE mode | frame_aspect={frame_aspect:.3f}")
            out.write(resized)
        out.release()
        logger.info("Finished RESCALE mode processing; output saved")
        
        # Add audio from original video using FFmpeg
        temp_video_path = output_path + "_temp_video_only.mp4"
        os.rename(output_path, temp_video_path)
        
        try:
            # Combine rescaled video with original audio
            ffmpeg_cmd = [
                'ffmpeg', '-i', temp_video_path, '-i', video_path,
                '-c:v', 'copy', '-c:a', 'copy', '-map', '0:v:0', '-map', '1:a:0',
                '-y', output_path
            ]
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                os.remove(temp_video_path)
                logger.info("Audio successfully added to rescaled video")
                print(f"[DYNAMIC CROP] Not enough face detections ({detection_ratio:.0%}); used rescale mode with audio.")
            else:
                # Fallback: keep video-only version
                os.rename(temp_video_path, output_path)
                logger.warning(f"Audio combination failed: {result.stderr}")
                print(f"[DYNAMIC CROP] Not enough face detections ({detection_ratio:.0%}); used rescale mode (no audio).")
        except Exception as e:
            # Fallback: keep video-only version
            os.rename(temp_video_path, output_path)
            logger.warning(f"Audio combination error: {e}")
            print(f"[DYNAMIC CROP] Not enough face detections ({detection_ratio:.0%}); used rescale mode (no audio).")
        return

    # Cropping mode below this line
    for i, frame in enumerate(frames):
        x, y, w, h = smoothed_boxes[i]
        face_frac_w = w / frame_width
        face_frac_h = h / frame_height
        # Only use full frame if face is extremely large (>80% of frame)
        # Otherwise, always crop to focus on the speaker and remove background
        if face_frac_w > 0.80 or face_frac_h > 0.80:
            # Resize with pillarbox if needed
            frame_aspect = frame_width / frame_height
            target_aspect = out_w / out_h
            if abs(frame_aspect - target_aspect) < 0.01:
                resized = cv2.resize(frame, (out_w, out_h))
            elif frame_aspect > target_aspect:
                # Add black bars left/right
                new_w = out_w
                new_h = int(out_w / frame_aspect)
                resized = cv2.resize(frame, (new_w, new_h))
                pad_top = (out_h - new_h) // 2
                pad_bottom = out_h - new_h - pad_top
                resized = cv2.copyMakeBorder(resized, pad_top, pad_bottom, 0, 0, cv2.BORDER_CONSTANT, value=[0,0,0])
            else:
                # Add black bars top/bottom
                new_h = out_h
                new_w = int(out_h * frame_aspect)
                resized = cv2.resize(frame, (new_w, new_h))
                pad_left = (out_w - new_w) // 2
                pad_right = out_w - new_w - pad_left
                resized = cv2.copyMakeBorder(resized, 0, 0, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0,0,0])
            if i % 30 == 0:
                logger.debug(f"Frame {i}: FULL FRAME | face_frac_w={face_frac_w:.3f} face_frac_h={face_frac_h:.3f}")
            out.write(resized)
        else:
            # ---------------------------------------------------
            # CROP MODE: Take a vertical slice centered on the face,
            # wide enough to show body language (about 60% of frame height)
            # ---------------------------------------------------
            
            # Calculate crop dimensions
            crop_height = frame_height  # Use full height
            crop_width = int(frame_height * 9/16)  # 9:16 aspect ratio
            
            # Center crop on face
            face_center_x = x + w//2
            crop_x = max(0, min(frame_width - crop_width, face_center_x - crop_width//2))
            
            # Crop and scale
            cropped = frame[0:crop_height, crop_x:crop_x + crop_width]
            
            if cropped.shape[0] > 0 and cropped.shape[1] > 0:
                resized = cv2.resize(cropped, (out_w, out_h))
                logger.debug(f"Frame {i}: CROP | face_center_x={face_center_x} crop_width={crop_width}")
            else:
                # Emergency fallback
                resized = cv2.resize(frame, (out_w, out_h))
                logger.warning(f"Frame {i}: Crop failed, using full frame")
            
            out.write(resized)
    out.release()
    logger.info("Finished CROPPING mode processing; output saved")
    
    # Add audio from original video using FFmpeg
    temp_video_path = output_path + "_temp_video_only.mp4"
    os.rename(output_path, temp_video_path)
    
    try:
        # Combine cropped video with original audio
        ffmpeg_cmd = [
            'ffmpeg', '-i', temp_video_path, '-i', video_path,
            '-c:v', 'copy', '-c:a', 'copy', '-map', '0:v:0', '-map', '1:a:0',
            '-y', output_path
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            os.remove(temp_video_path)
            logger.info("Audio successfully added to cropped video")
            print(f"[DYNAMIC CROP] Saved cropped video with audio to {output_path} | log={log_file}")
        else:
            # Fallback: keep video-only version
            os.rename(temp_video_path, output_path)
            logger.warning(f"Audio combination failed: {result.stderr}")
            print(f"[DYNAMIC CROP] Saved cropped video (no audio) to {output_path} | log={log_file}")
    except Exception as e:
        # Fallback: keep video-only version
        os.rename(temp_video_path, output_path)
        logger.warning(f"Audio combination error: {e}")
        print(f"[DYNAMIC CROP] Saved cropped video (no audio) to {output_path} | log={log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dynamic-crop', action='store_true', help='Run dynamic face crop mode')
    parser.add_argument('--out-width', type=int, default=720, help='Output width (default 720)')
    parser.add_argument('--out-height', type=int, default=1280, help='Output height (default 1280)')
    parser.add_argument('video_path', nargs='?', help='Input video path')
    parser.add_argument('output_path', nargs='?', help='Output video path')
    parser.add_argument('start_time', nargs='?', help='(Unused in dynamic crop)')
    parser.add_argument('end_time', nargs='?', help='(Unused in dynamic crop)')
    parser.add_argument('output_json', nargs='?', help='(Unused in dynamic crop)')
    args = parser.parse_args()

    if args.dynamic_crop:
        if not args.video_path or not args.output_path:
            print("Usage: python enhanced_speaker_detection.py --dynamic-crop <video_path> <output_path> [--out-width 720 --out-height 1280]", file=sys.stderr)
            sys.exit(1)
        dynamic_face_crop(args.video_path, args.output_path, target_aspect=9/16, padding=0.35, out_res=(args.out_width, args.out_height))
    else:
        if len(sys.argv) != 5:
            print("Usage: python enhanced_speaker_detection.py <video_path> <start_time> <end_time> <output_json>")
            sys.exit(1)
        video_path = sys.argv[1]
        start_time = float(sys.argv[2])
        end_time = float(sys.argv[3])
        output_path = sys.argv[4]
        enhanced_speaker_detection(video_path, start_time, end_time, output_path) 