const axios = require('axios');

async function testDurationFix() {
  try {
    console.log('🧪 Testing duration enforcement fix...');
    
    const response = await axios.post('http://localhost:5000/analyze', {
      youtubeUrl: 'https://www.youtube.com/watch?v=31VyYWb5Iy8',
      numClips: 3,
      clipDuration: 15, // Request 15-second clips
      captionStyle: 'single-word',
      fontStyle: 'impact',
      processingMode: 'auto',
      targetPlatform: 'tiktok'
    });
    
    console.log('✅ Response received:');
    console.log('Status:', response.status);
    console.log('Clips created:', response.data.clips.length);
    
    // Check if clips are actually 15 seconds
    response.data.clips.forEach((clip, index) => {
      const startTime = clip.start_time;
      const endTime = clip.end_time;
      
      // Parse time format (MM:SS)
      const startParts = startTime.split(':').map(Number);
      const endParts = endTime.split(':').map(Number);
      
      const startSeconds = startParts[0] * 60 + startParts[1];
      const endSeconds = endParts[0] * 60 + endParts[1];
      const actualDuration = endSeconds - startSeconds;
      
      console.log(`Clip ${index + 1}: ${startTime} -> ${endTime} (${actualDuration}s)`);
      
      if (Math.abs(actualDuration - 15) <= 2) {
        console.log(`  ✅ Duration is correct (${actualDuration}s)`);
      } else {
        console.log(`  ❌ Duration is wrong (${actualDuration}s, expected ~15s)`);
      }
    });
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
  }
}

testDurationFix(); 