const express = require('express');
const cors = require('cors');

const app = express();

// CORS configuration
app.use(cors({
  origin: '*',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Range']
}));

app.use(express.json());

const sampleVideoUrl = "https://www.w3schools.com/html/mov_bbb.mp4";
const sampleThumbnailUrl = "https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Viral+Clip";

// Test endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'Trilion Backend is running!',
    status: 'active',
    timestamp: new Date().toISOString(),
    endpoints: {
      analyze: '/analyze',
      clips: '/clips-list',
      test: '/test'
    }
  });
});

// Test endpoint
app.get('/test', (req, res) => {
  res.json({ 
    message: 'Backend is working!',
    timestamp: new Date().toISOString()
  });
});

// Simple viral analysis endpoint
app.post('/analyze', async (req, res) => {
  try {
    const { ytLink, numClips = 3, clipDuration = 30 } = req.body;
    
    if (!ytLink) {
      return res.status(400).json({ error: 'No YouTube link provided' });
    }

    console.log('Analyzing video for viral clips:', ytLink);

    // Generate mock viral clips
    const mockClips = [];
    for (let i = 0; i < numClips; i++) {
      const startTime = Math.floor(Math.random() * 300) + 60;
      const endTime = startTime + clipDuration;
      
      mockClips.push({
        id: Date.now() + i,
        title: `Viral Moment ${i + 1} - This Will Blow Your Mind! 😱`,
        description: `This clip has viral potential due to its emotional impact and relatability.`,
        start_time: `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`,
        end_time: `${Math.floor(endTime / 60)}:${(endTime % 60).toString().padStart(2, '0')}`,
        duration: clipDuration,
        timestamp: Date.now(),
        filename: `viral_clip_${i + 1}.mp4`,
        viral_score: 8.5 + (Math.random() * 1.5),
        thumbnail_url: sampleThumbnailUrl,
        download_url: sampleVideoUrl
      });
    }

    res.json({
      success: true,
      message: 'Viral analysis completed!',
      video_url: ytLink,
      clips: mockClips,
      analysis_summary: {
        total_clips: mockClips.length,
        average_viral_score: (mockClips.reduce((sum, clip) => sum + clip.viral_score, 0) / mockClips.length).toFixed(1),
        recommended_platforms: ['TikTok', 'Instagram Reels', 'YouTube Shorts']
      }
    });

  } catch (error) {
    console.error('Viral analysis error:', error);
    res.status(500).json({ 
      error: 'Failed to analyze video for viral clips',
      details: error.message 
    });
  }
});

// Simple analysis endpoint
app.post('/analyze', async (req, res) => {
  try {
    const { ytLink, numClips = 3, clipDuration = 30 } = req.body;
    
    if (!ytLink) {
      return res.status(400).json({ error: 'No YouTube link provided' });
    }

    console.log('Analyzing video:', ytLink);

    // Generate mock clips
    const mockClips = [];
    for (let i = 0; i < numClips; i++) {
      const startTime = Math.floor(Math.random() * 300) + 60;
      const endTime = startTime + clipDuration;
      
      mockClips.push({
        id: Date.now() + i,
        title: `Clip ${i + 1} - Interesting Moment`,
        description: `This clip contains engaging content.`,
        start_time: `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`,
        end_time: `${Math.floor(endTime / 60)}:${(endTime % 60).toString().padStart(2, '0')}`,
        duration: clipDuration,
        timestamp: Date.now(),
        filename: `clip_${i + 1}.mp4`,
        thumbnail_url: sampleThumbnailUrl,
        download_url: sampleVideoUrl
      });
    }

    res.json({
      success: true,
      message: 'Analysis completed!',
      video_url: ytLink,
      clips: mockClips
    });

  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ 
      error: 'Failed to analyze video',
      details: error.message 
    });
  }
});

const port = process.env.PORT || 5000;
app.listen(port, () => {
  console.log(`Trilion Backend running on port ${port}`);
}); 