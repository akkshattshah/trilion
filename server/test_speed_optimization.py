#!/usr/bin/env python3
"""
Speed Optimization Test: Verify that persistent Whisper model dramatically improves performance
"""
import time
import sys
import os
import tempfile
import subprocess
from viral_caption_system import generate_viral_captions_from_video
from persistent_whisper_manager import cleanup_persistent_whisper

def create_test_video(duration=10):
    """Create a short test video for performance testing"""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_video:
        # Create a simple test video with audio
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", "testsrc2=duration={}:size=320x240:rate=30".format(duration),
            "-f", "lavfi", "-i", "sine=frequency=1000:duration={}".format(duration),
            "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
            "-y", tmp_video.name
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return tmp_video.name
        except subprocess.CalledProcessError as e:
            print(f"Failed to create test video: {e}")
            return None

def test_speed_optimization():
    """Test the speed improvement from persistent Whisper model"""
    print("🧪 TESTING PERSISTENT WHISPER SPEED OPTIMIZATION")
    print("=" * 60)
    
    # Create test video
    print("📹 Creating test video...")
    test_video = create_test_video(10)  # 10 second video
    
    if not test_video:
        print("❌ Failed to create test video")
        return
    
    try:
        print(f"✅ Test video created: {test_video}")
        
        # Simulate processing multiple clips (like what happens in production)
        num_clips = 3
        times = []
        
        print(f"\n🔄 Simulating {num_clips} clips processing...")
        print("This tests whether the Whisper model stays loaded between clips")
        
        for i in range(num_clips):
            print(f"\n📊 Processing clip {i + 1}/{num_clips}...")
            start_time = time.time()
            
            # This will use the persistent Whisper model
            result = generate_viral_captions_from_video(
                test_video, 
                output_dir=tempfile.gettempdir(),
                caption_style="single-word"
            )
            
            end_time = time.time()
            clip_time = end_time - start_time
            times.append(clip_time)
            
            if "error" in result:
                print(f"⚠️ Clip {i + 1} had error: {result['error']}")
            else:
                print(f"✅ Clip {i + 1} completed in {clip_time:.2f}s")
                print(f"   Segments: {result.get('base_segments', 'N/A')}")
                print(f"   Enhanced Whisper: {result.get('enhanced_whisper', False)}")
        
        # Cleanup persistent model
        print(f"\n🧹 Cleaning up persistent Whisper model...")
        cleanup_persistent_whisper()
        
        # Analyze results
        print(f"\n📈 PERFORMANCE ANALYSIS:")
        print(f"   First clip:  {times[0]:.2f}s (includes model loading)")
        if len(times) > 1:
            avg_subsequent = sum(times[1:]) / len(times[1:])
            print(f"   Subsequent:  {avg_subsequent:.2f}s (model already loaded)")
            speedup = times[0] / avg_subsequent if avg_subsequent > 0 else 1
            print(f"   Speed boost: {speedup:.1f}x faster after first clip")
            
            if speedup > 2.0:
                print("🚀 EXCELLENT: Major speed improvement detected!")
            elif speedup > 1.5:
                print("✅ GOOD: Noticeable speed improvement")
            else:
                print("⚠️ LIMITED: Speed improvement less than expected")
        
        total_time = sum(times)
        print(f"   Total time:  {total_time:.2f}s for {num_clips} clips")
        print(f"   Average:     {total_time/num_clips:.2f}s per clip")
        
        # Expected performance
        print(f"\n🎯 EXPECTED RESULTS:")
        print(f"   Without optimization: ~15-25s per clip")
        print(f"   With optimization: First clip ~15-25s, subsequent ~3-8s")
        
        if total_time < 30:  # Should be much faster than 30s for 3 clips
            print("🎉 SUCCESS: Speed optimization is working!")
        else:
            print("⚠️ WARNING: Performance may not be optimal")
            
    finally:
        # Cleanup test video
        if os.path.exists(test_video):
            os.remove(test_video)
            print(f"🗑️ Cleaned up test video")

if __name__ == "__main__":
    test_speed_optimization() 