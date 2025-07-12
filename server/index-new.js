const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const fsExtra = require('fs-extra');
const OpenAI = require('openai');
const Anthropic = require('@anthropic-ai/sdk');
const YouTubeUploadManager = require('./youtube-upload-manager');
const ytdl = require('ytdl-core');
const ffmpeg = require('fluent-ffmpeg');
const axios = require('axios');

// Validate required environment variables
const requiredEnvVars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('❌ Missing required environment variables:', missingVars);
  console.error('Please set the following environment variables:');
  missingVars.forEach(varName => console.error(`  - ${varName}`));
  process.exit(1);
}

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const app = express();

// Enhanced CORS configuration
const corsOrigins = process.env.NODE_ENV === 'production' 
  ? [process.env.CORS_ORIGIN || 'https://trilion-frontend.onrender.com']
  : ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002'];

app.use(cors({
  origin: corsOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Range']
}));

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

const mediaDir = path.join(__dirname, 'media');
if (!fs.existsSync(mediaDir)) {
  fs.mkdirSync(mediaDir, { recursive: true });
}

// Test endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'Trilion Backend Server is running!', 
    status: 'active',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    endpoints: {
      analyze: '/analyze',
      clips: '/clips-list',
      test: '/test'
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Simple test endpoint
app.get('/test', (req, res) => {
  res.json({ 
    message: 'Test endpoint working!',
    apiKeys: {
      openai: process.env.OPENAI_API_KEY ? 'Configured' : 'Missing',
      anthropic: process.env.ANTHROPIC_API_KEY ? 'Configured' : 'Missing',
      youtube: process.env.YOUTUBE_CLIENT_ID ? 'Configured' : 'Missing'
    }
  });
});

// Enhanced static file serving with proper video headers
app.use('/clips', (req, res, next) => {
  // Set proper headers for video streaming
  res.setHeader('Accept-Ranges', 'bytes');
  res.setHeader('Cache-Control', 'public, max-age=3600');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Range');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  next();
}, express.static(mediaDir));

// Download endpoint for clips
app.get('/download/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(mediaDir, filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath, filename);
  } else {
    res.status(404).json({ error: 'File not found' });
  }
});

// Helper function to download video using ytdl-core
async function downloadVideo(ytLink, outputPath) {
  return new Promise((resolve, reject) => {
    console.log(`Downloading video from: ${ytLink}`);
    
    const video = ytdl(ytLink, {
      quality: 'highestaudio',
      filter: 'audioonly'
    });
    
    const writeStream = fs.createWriteStream(outputPath);
    
    video.pipe(writeStream);
    
    video.on('end', () => {
      console.log('Video download completed');
      resolve();
    });
    
    video.on('error', (error) => {
      console.error('Video download error:', error);
      reject(error);
    });
    
    writeStream.on('error', (error) => {
      console.error('Write stream error:', error);
      reject(error);
    });
  });
}

// Helper function to extract audio using fluent-ffmpeg
async function extractAudio(videoPath, audioPath) {
  return new Promise((resolve, reject) => {
    console.log('Extracting audio...');
    
    ffmpeg(videoPath)
      .toFormat('mp3')
      .on('end', () => {
        console.log('Audio extraction completed');
        resolve();
      })
      .on('error', (error) => {
        console.error('Audio extraction error:', error);
        reject(error);
      })
      .save(audioPath);
  });
}

app.post('/analyze', async (req, res) => {
  console.log('POST /analyze received');
  console.log('Request body:', req.body);
  const { ytLink, numClips = 3, clipDuration = 30 } = req.body;
  console.log('Received YouTube link:', ytLink);
  console.log('Number of clips:', numClips);
  console.log('Clip duration:', clipDuration);
  
  if (!ytLink) {
    return res.status(400).json({ error: 'No YouTube link provided' });
  }

  try {
    console.log('Starting mock analysis for:', ytLink);
    
    // Generate mock clips for now (since external tools aren't available on Render)
    const timestamp = Date.now();
    const clipSuggestions = [];
    
    for (let i = 0; i < numClips; i++) {
      const startTime = Math.floor(Math.random() * 300) + 60; // 1-6 minutes
      const endTime = startTime + clipDuration;
      
      const viralTitles = [
        `This Will BLOW Your Mind! 😱 Viral Moment ${i + 1}`,
        `You Won't BELIEVE What Happens Next! 🚨`,
        `The TRUTH About This Will Shock You! 💀`,
        `This Changed My Life Forever! 💰`,
        `INSANE Revelation That Went Viral! 🔥`
      ];
      
      const viralDescriptions = [
        `This clip has viral potential due to its emotional impact and relatability.`,
        `The shocking revelation in this moment will make people stop scrolling.`,
        `This controversial statement sparked millions of views and debates.`,
        `The unexpected twist in this clip is pure viral gold.`,
        `This relatable problem that everyone faces but rarely discusses.`
      ];
      
      clipSuggestions.push({
        id: i + 1,
        title: viralTitles[i % viralTitles.length],
        description: viralDescriptions[i % viralDescriptions.length],
        start_time: `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`,
        end_time: `${Math.floor(endTime / 60)}:${(endTime % 60).toString().padStart(2, '0')}`,
        duration: clipDuration,
        timestamp: Date.now(),
        filename: `clip_${timestamp}_${i + 1}.mp4`,
        viral_score: 8.5 + (Math.random() * 1.5),
        thumbnail_url: `https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Viral+Clip+${i + 1}`,
        download_url: `/clips/clip_${timestamp}_${i + 1}.mp4`,
        hook_type: ['emotional', 'controversial', 'shocking', 'relatable', 'aspirational'][i % 5],
        natural_flow_score: 7.5 + (Math.random() * 2.5),
        quality_rating: ['Excellent', 'Good', 'Very Good'][Math.floor(Math.random() * 3)],
        analysis_method: 'AI-powered viral detection',
        post_analysis: {
          quality_check: 'Passed all viral criteria',
          actual_content: 'High engagement potential detected',
          language_confirmed: 'English content verified'
        }
      });
    }
    
    console.log('Generated mock clips:', clipSuggestions);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    res.json({
      success: true,
      message: 'Mock video analysis completed successfully! (Note: This is a demo version)',
      clips: clipSuggestions,
      analysis_provider: 'mock',
      transcript_length: 0,
      note: 'Full video processing requires FFmpeg and yt-dlp which are not available on Render free tier. This demo shows the UI and clip generation logic.'
    });
    
  } catch (error) {
    console.error('Error in /analyze:', error);
    res.status(500).json({
      error: 'Analysis failed',
      details: error.message
    });
  }
});

// Get list of available clips
app.get('/clips-list', (req, res) => {
  try {
    const files = fs.readdirSync(mediaDir);
    const clips = files
      .filter(file => file.endsWith('.mp4'))
      .map(file => ({
        filename: file,
        size: fs.statSync(path.join(mediaDir, file)).size,
        created: fs.statSync(path.join(mediaDir, file)).birthtime,
        url: `/clips/${file}`
      }));
    
    res.json({
      success: true,
      clips: clips,
      total: clips.length
    });
  } catch (error) {
    console.error('Error getting clips list:', error);
    res.status(500).json({
      error: 'Failed to get clips list',
      details: error.message
    });
  }
});

// Enhanced viral analysis endpoint
app.post('/analyze-viral', async (req, res) => {
  console.log('POST /analyze-viral received');
  const { ytLink, numClips = 3, clipDuration = 30 } = req.body;
  
  if (!ytLink) {
    return res.status(400).json({ error: 'No YouTube link provided' });
  }

  try {
    console.log('Starting enhanced viral analysis for:', ytLink);
    
    // Generate enhanced mock clips
    const timestamp = Date.now();
    const clipSuggestions = [];
    
    const viralTemplates = [
      {
        title: "This Will BLOW Your Mind! 😱 The TRUTH Revealed!",
        description: "Shocking revelation that challenges everything you thought you knew",
        hook_type: "shocking_revelation",
        viral_score: 9.2
      },
      {
        title: "You Won't BELIEVE What Happens Next! 🚨 INSANE!",
        description: "Unexpected twist that will make you question reality",
        hook_type: "emotional_trigger",
        viral_score: 8.8
      },
      {
        title: "The TRUTH About This Will Shock You! 💀 EXPOSED!",
        description: "Controversial statement that sparks intense debate",
        hook_type: "controversial_statement",
        viral_score: 9.0
      },
      {
        title: "This Changed My Life Forever! 💰 MIND-BLOWING!",
        description: "Life-changing revelation that everyone needs to hear",
        hook_type: "aspirational_content",
        viral_score: 8.7
      },
      {
        title: "INSANE Revelation That Went Viral! 🔥 UNBELIEVABLE!",
        description: "Mind-blowing fact that will make you want to share immediately",
        hook_type: "educational_value",
        viral_score: 9.1
      }
    ];
    
    for (let i = 0; i < numClips; i++) {
      const startTime = Math.floor(Math.random() * 300) + 60;
      const endTime = startTime + clipDuration;
      const template = viralTemplates[i % viralTemplates.length];
      
      clipSuggestions.push({
        id: i + 1,
        title: template.title,
        description: template.description,
        start_time: `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`,
        end_time: `${Math.floor(endTime / 60)}:${(endTime % 60).toString().padStart(2, '0')}`,
        duration: clipDuration,
        timestamp: Date.now(),
        filename: `viral_clip_${timestamp}_${i + 1}.mp4`,
        viral_score: template.viral_score + (Math.random() * 0.8),
        thumbnail_url: `https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Viral+${i + 1}`,
        download_url: `/clips/viral_clip_${timestamp}_${i + 1}.mp4`,
        hook_type: template.hook_type,
        natural_flow_score: 8.0 + (Math.random() * 2.0),
        quality_rating: 'Excellent',
        analysis_method: 'Advanced AI viral detection',
        engagement_prediction: {
          views: Math.floor(Math.random() * 1000000) + 100000,
          likes: Math.floor(Math.random() * 50000) + 5000,
          shares: Math.floor(Math.random() * 10000) + 1000,
          comments: Math.floor(Math.random() * 5000) + 500
        },
        post_analysis: {
          quality_check: 'Passed all viral criteria',
          actual_content: 'High engagement potential detected',
          language_confirmed: 'English content verified',
          viral_potential: 'Very High',
          recommended_platforms: ['TikTok', 'Instagram Reels', 'YouTube Shorts']
        }
      });
    }
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    res.json({
      success: true,
      message: 'Enhanced viral analysis completed successfully!',
      clips: clipSuggestions,
      analysis_provider: 'enhanced_mock',
      total_clips: clipSuggestions.length,
      average_viral_score: (clipSuggestions.reduce((sum, clip) => sum + clip.viral_score, 0) / clipSuggestions.length).toFixed(2),
      note: 'This is a demo version showing the enhanced viral analysis capabilities.'
    });
    
  } catch (error) {
    console.error('Error in /analyze-viral:', error);
    res.status(500).json({
      error: 'Enhanced viral analysis failed',
      details: error.message
    });
  }
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`🚀 Trilion Backend Server running on port ${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 Health check: http://localhost:${PORT}/health`);
  console.log(`🧪 Test endpoint: http://localhost:${PORT}/test`);
  console.log(`📁 Media directory: ${mediaDir}`);
});

module.exports = app; 