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
const { spawn } = require('child_process');
const youtubeDl = require('youtube-dl-exec');

// Initialize AI clients only when needed
let openai = null;
let anthropic = null;

function initializeAIClients() {
  if (!openai && process.env.OPENAI_API_KEY) {
    openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }
  
  if (!anthropic && process.env.ANTHROPIC_API_KEY) {
    anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY
    });
  }
}

// Check for required environment variables (warn but don't exit)
const requiredEnvVars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.warn('⚠️  Missing environment variables:', missingVars);
  console.warn('Some features may be limited. Set these for full functionality:');
  missingVars.forEach(varName => console.warn(`  - ${varName}`));
} else {
  console.log('✅ All AI API keys configured');
  initializeAIClients();
}

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

// Content Security Policy middleware
app.use((req, res, next) => {
  const isDevelopment = process.env.NODE_ENV !== 'production';
  
  if (isDevelopment) {
    // More permissive CSP for development
    res.setHeader('Content-Security-Policy', 
      "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:; " +
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
      "font-src 'self' https://fonts.gstatic.com; " +
      "img-src 'self' data: https: blob:; " +
      "connect-src 'self' https://trilion-backend-bojb.onrender.com https://api.openai.com https://api.anthropic.com ws: wss: http://localhost:*; " +
      "media-src 'self' https: blob:; " +
      "frame-src 'self'; " +
      "worker-src 'self' blob:; " +
      "object-src 'none'; " +
      "base-uri 'self'; " +
      "form-action 'self'"
    );
  } else {
    // Stricter CSP for production
    res.setHeader('Content-Security-Policy', 
      "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline'; " +
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
      "font-src 'self' https://fonts.gstatic.com; " +
      "img-src 'self' data: https:; " +
      "connect-src 'self' https://trilion-backend-bojb.onrender.com https://api.openai.com https://api.anthropic.com; " +
      "media-src 'self' https:; " +
      "frame-src 'self'; " +
      "object-src 'none'; " +
      "base-uri 'self'; " +
      "form-action 'self'"
    );
  }
  next();
});

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

const mediaDir = path.join(__dirname, 'media');
if (!fs.existsSync(mediaDir)) {
  fs.mkdirSync(mediaDir, { recursive: true });
}

// Helper function to download video with fallback methods
async function downloadVideo(ytLink, outputPath) {
  console.log(`Downloading video from: ${ytLink}`);
  
  // Method 1: Try ytdl-core first
  try {
    console.log('Attempting download with ytdl-core...');
    await downloadWithYtdlCore(ytLink, outputPath);
    console.log('Video download completed with ytdl-core');
    return;
  } catch (ytdlError) {
    console.error('ytdl-core failed:', ytdlError.message);
    
    // Method 2: Try youtube-dl as fallback
    try {
      console.log('Attempting download with youtube-dl...');
      await downloadWithYoutubeDl(ytLink, outputPath);
      console.log('Video download completed with youtube-dl');
      return;
    } catch (youtubeDlError) {
      console.error('youtube-dl failed:', youtubeDlError.message);
      
      // Method 3: Try alternative ytdl-core options
      try {
        console.log('Attempting download with alternative ytdl-core options...');
        await downloadWithAlternativeYtdl(ytLink, outputPath);
        console.log('Video download completed with alternative options');
        return;
      } catch (altError) {
        console.error('All download methods failed');
        throw new Error(`All download methods failed. The video may be unavailable, private, or region-restricted. Please try a different YouTube video.`);
      }
    }
  }
}

// Method 1: ytdl-core with enhanced options
async function downloadWithYtdlCore(ytLink, outputPath) {
  return new Promise((resolve, reject) => {
    const options = {
      quality: 'highestaudio',
      filter: 'audioonly',
      requestOptions: {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
      }
    };
    
    try {
      const video = ytdl(ytLink, options);
      const writeStream = fs.createWriteStream(outputPath);
      
      video.pipe(writeStream);
      
      video.on('end', () => resolve());
      video.on('error', (error) => {
        if (error.statusCode === 410) {
          reject(new Error('Video is unavailable or private'));
        } else if (error.statusCode === 403) {
          reject(new Error('Access denied - video may be age-restricted'));
        } else if (error.statusCode === 404) {
          reject(new Error('Video not found'));
        } else {
          reject(new Error(`ytdl-core error: ${error.message}`));
        }
      });
      
      writeStream.on('error', (error) => {
        reject(new Error(`Write error: ${error.message}`));
      });
      
      setTimeout(() => {
        video.destroy();
        reject(new Error('Download timeout'));
      }, 300000);
      
    } catch (error) {
      reject(new Error(`ytdl-core initialization failed: ${error.message}`));
    }
  });
}

// Method 2: youtube-dl fallback
async function downloadWithYoutubeDl(ytLink, outputPath) {
  try {
    await youtubeDl(ytLink, {
      output: outputPath,
      format: 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
      extractAudio: true,
      audioFormat: 'mp3',
      audioQuality: '0'
    });
  } catch (error) {
    throw new Error(`youtube-dl failed: ${error.message}`);
  }
}

// Method 3: Alternative ytdl-core options
async function downloadWithAlternativeYtdl(ytLink, outputPath) {
  return new Promise((resolve, reject) => {
    const options = {
      quality: 'lowestaudio',
      filter: 'audioonly',
      requestOptions: {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
      }
    };
    
    try {
      const video = ytdl(ytLink, options);
      const writeStream = fs.createWriteStream(outputPath);
      
      video.pipe(writeStream);
      
      video.on('end', () => resolve());
      video.on('error', (error) => {
        reject(new Error(`Alternative ytdl-core failed: ${error.message}`));
      });
      
      writeStream.on('error', (error) => {
        reject(new Error(`Write error: ${error.message}`));
      });
      
      setTimeout(() => {
        video.destroy();
        reject(new Error('Alternative download timeout'));
      }, 300000);
      
    } catch (error) {
      reject(new Error(`Alternative ytdl-core initialization failed: ${error.message}`));
    }
  });
}

// Helper function to extract audio using fluent-ffmpeg with better error handling
async function extractAudio(videoPath, audioPath) {
  return new Promise((resolve, reject) => {
    console.log('Extracting audio...');
    
    // Check if input file exists
    if (!fs.existsSync(videoPath)) {
      reject(new Error(`Input video file not found: ${videoPath}`));
      return;
    }
    
    // Get file size to check if it's valid
    const stats = fs.statSync(videoPath);
    if (stats.size === 0) {
      reject(new Error('Input video file is empty'));
      return;
    }
    
    ffmpeg(videoPath)
      .toFormat('mp3')
      .audioChannels(2)
      .audioFrequency(44100)
      .audioQuality(0)
      .outputOptions([
        '-acodec', 'libmp3lame',
        '-ar', '44100',
        '-ac', '2',
        '-b:a', '192k'
      ])
      .on('start', (commandLine) => {
        console.log('FFmpeg command:', commandLine);
      })
      .on('progress', (progress) => {
        console.log('Processing: ' + progress.percent + '% done');
      })
      .on('end', () => {
        console.log('Audio extraction completed');
        resolve();
      })
      .on('error', (error) => {
        console.error('Audio extraction error:', error);
        // Try alternative approach if first fails
        console.log('Trying alternative audio extraction...');
        ffmpeg(videoPath)
          .toFormat('wav')
          .on('end', () => {
            console.log('Alternative audio extraction completed (WAV)');
            resolve();
          })
          .on('error', (altError) => {
            console.error('Alternative audio extraction also failed:', altError);
            reject(new Error(`Audio extraction failed: ${error.message}. Alternative method also failed: ${altError.message}`));
          })
          .save(audioPath.replace('.mp3', '.wav'));
      })
      .save(audioPath);
  });
}

// Helper function to create video clips using fluent-ffmpeg with better error handling
async function createVideoClip(inputPath, outputPath, startTime, duration) {
  return new Promise((resolve, reject) => {
    console.log(`Creating clip: ${startTime}s for ${duration}s`);
    
    // Check if input file exists
    if (!fs.existsSync(inputPath)) {
      reject(new Error(`Input video file not found: ${inputPath}`));
      return;
    }
    
    // Get file size to check if it's valid
    const stats = fs.statSync(inputPath);
    if (stats.size === 0) {
      reject(new Error('Input video file is empty'));
      return;
    }
    
    ffmpeg(inputPath)
      .setStartTime(startTime)
      .setDuration(duration)
      .videoCodec('libx264')
      .audioCodec('aac')
      .outputOptions([
        '-preset', 'fast',
        '-crf', '23',
        '-movflags', '+faststart',
        '-pix_fmt', 'yuv420p'
      ])
      .on('start', (commandLine) => {
        console.log('FFmpeg clip command:', commandLine);
      })
      .on('progress', (progress) => {
        console.log('Clip processing: ' + progress.percent + '% done');
      })
      .on('end', () => {
        console.log('Video clip created successfully');
        resolve();
      })
      .on('error', (error) => {
        console.error('Video clip creation error:', error);
        // Try alternative approach with different settings
        console.log('Trying alternative clip creation...');
        ffmpeg(inputPath)
          .setStartTime(startTime)
          .setDuration(duration)
          .videoCodec('libx264')
          .audioCodec('copy')
          .outputOptions(['-preset', 'ultrafast', '-crf', '28'])
          .on('end', () => {
            console.log('Alternative video clip created successfully');
            resolve();
          })
          .on('error', (altError) => {
            console.error('Alternative clip creation also failed:', altError);
            reject(new Error(`Video clip creation failed: ${error.message}. Alternative method also failed: ${altError.message}`));
          })
          .save(outputPath);
      })
      .save(outputPath);
  });
}

// Helper function to run Python AI analysis
async function runPythonAnalysis(audioPath, videoPath, numClips, targetDuration) {
  return new Promise((resolve, reject) => {
    console.log('Running Python AI analysis...');
    
    const pythonScript = `
import sys
import json
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from intelligent_clip_analyzer import analyze_video_for_viral_clips
    result = analyze_video_for_viral_clips('${videoPath}', max_clips=${numClips}, target_platform="tiktok", target_duration=${targetDuration})
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    
    const pythonProcess = spawn('python3', ['-c', pythonScript], {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let stdout = '';
    let stderr = '';
    
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          if (result.error) {
            reject(new Error(result.error));
          } else {
            resolve(result);
          }
        } catch (parseError) {
          reject(new Error(`Failed to parse Python output: ${parseError.message}`));
        }
      } else {
        reject(new Error(`Python process failed with code ${code}: ${stderr}`));
      }
    });
    
    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
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

// YouTube link validation endpoint with multiple methods
app.post('/validate-youtube', async (req, res) => {
  const { ytLink } = req.body;
  
  if (!ytLink) {
    return res.status(400).json({ error: 'No YouTube link provided' });
  }
  
  try {
    console.log(`Validating YouTube link: ${ytLink}`);
    
    // Method 1: Try ytdl-core first
    try {
      const info = await ytdl.getInfo(ytLink);
      
      return res.json({
        valid: true,
        title: info.videoDetails.title,
        duration: info.videoDetails.lengthSeconds,
        author: info.videoDetails.author.name,
        viewCount: info.videoDetails.viewCount,
        message: 'YouTube link is valid and accessible',
        method: 'ytdl-core'
      });
    } catch (ytdlError) {
      console.log('ytdl-core validation failed, trying youtube-dl...');
      
      // Method 2: Try youtube-dl as fallback
      try {
        const info = await youtubeDl(ytLink, {
          dumpSingleJson: true,
          noCheckCertificates: true,
          noWarnings: true,
          preferFreeFormats: true
        });
        
        return res.json({
          valid: true,
          title: info.title,
          duration: info.duration,
          uploader: info.uploader,
          viewCount: info.view_count,
          message: 'YouTube link is valid and accessible',
          method: 'youtube-dl'
        });
      } catch (youtubeDlError) {
        console.log('youtube-dl validation also failed');
        
        // Both methods failed
        let errorMessage = 'Video is unavailable or has restrictions';
        if (ytdlError.statusCode === 410) {
          errorMessage = 'Video is unavailable or private';
        } else if (ytdlError.statusCode === 403) {
          errorMessage = 'Video is age-restricted or region-blocked';
        } else if (ytdlError.statusCode === 404) {
          errorMessage = 'Video not found';
        }
        
        return res.status(400).json({
          valid: false,
          error: errorMessage,
          details: 'Both validation methods failed',
          suggestions: [
            'Try a different YouTube video',
            'Check if the video is public and accessible',
            'Use demo mode to test the interface'
          ]
        });
      }
    }
  } catch (error) {
    console.error('YouTube validation error:', error);
    
    res.status(400).json({
      valid: false,
      error: 'YouTube link validation failed',
      details: error.message,
      suggestions: [
        'Try a different YouTube video',
        'Use demo mode to test the interface'
      ]
    });
  }
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

// Main analysis endpoint
app.post('/analyze', async (req, res) => {
  console.log('POST /analyze received');
  console.log('Request body:', req.body);
  const { ytLink, numClips = 3, clipDuration = 30, demoMode = false } = req.body;
  console.log('Received YouTube link:', ytLink);
  console.log('Number of clips:', numClips);
  console.log('Clip duration:', clipDuration);
  console.log('Demo mode:', demoMode);
  
  if (!ytLink && !demoMode) {
    return res.status(400).json({ error: 'No YouTube link provided' });
  }

  try {
    // Generate unique filenames
    const timestamp = Date.now();
    const videoFile = `video_${timestamp}.mp4`;
    const audioFile = `audio_${timestamp}.mp3`;
    const videoPath = path.join(mediaDir, videoFile);
    const audioPath = path.join(mediaDir, audioFile);
    
    let videoDownloaded = false;
    
    if (demoMode) {
      console.log('Running in demo mode - skipping video download');
      videoDownloaded = true;
    } else {
      console.log('Starting video download...');
      
      try {
        // Download video using multiple fallback methods
        await downloadVideo(ytLink, videoPath);
        videoDownloaded = true;
        console.log('Video downloaded successfully');
      } catch (downloadError) {
        console.error('Video download failed:', downloadError.message);
        
        // Return helpful error message with more specific guidance
        return res.status(400).json({
          error: 'Video download failed',
          details: downloadError.message,
          suggestions: [
            'Try a different YouTube video (some videos have restrictions)',
            'Check if the video is public and not age-restricted',
            'Use demo mode to test the interface without downloading',
            'Try shorter videos (under 10 minutes) for better compatibility',
            'Contact support if the issue persists with multiple videos'
          ],
          alternative: 'Use demo mode to test the interface while we work on compatibility'
        });
      }
    }
    
    if (demoMode) {
      console.log('Demo mode: Generating sample clips...');
      
      // Generate demo clips
      const clips = [];
      for (let i = 0; i < numClips; i++) {
        const startTime = i * clipDuration;
        const endTime = startTime + clipDuration;
        
        clips.push({
          id: i + 1,
          filename: `demo_clip_${timestamp}_${i + 1}.mp4`,
          url: `/clips/demo_clip_${timestamp}_${i + 1}.mp4`,
          download_url: `/download/demo_clip_${timestamp}_${i + 1}.mp4`,
          start_time: `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`,
          end_time: `${Math.floor(endTime / 60)}:${(endTime % 60).toString().padStart(2, '0')}`,
          duration: clipDuration,
          title: `🔥 VIRAL MOMENT ${i + 1} - MUST WATCH! 🔥`,
          description: `Demo viral clip ${i + 1} - This would be AI-generated content based on the video analysis`,
          viral_score: Math.floor(Math.random() * 40) + 60, // 60-100
          platform: 'tiktok',
          demo: true
        });
      }
      
      console.log(`Demo mode completed. Generated ${clips.length} sample clips.`);
      
      return res.json({
        success: true,
        message: `Demo mode: Generated ${clips.length} sample viral clips!`,
        clips: clips,
        analysis: {
          total_clips_requested: numClips,
          total_clips_created: clips.length,
          target_duration: clipDuration,
          platform: 'tiktok',
          demo_mode: true
        }
      });
    }
    
    console.log('Video downloaded, extracting audio...');
    
    // Extract audio for analysis
    await extractAudio(videoPath, audioPath);
    
    console.log('Audio extracted, running AI analysis...');
    
    // Run Python AI analysis
    let analysisResult;
    try {
      analysisResult = await runPythonAnalysis(audioPath, videoPath, numClips, clipDuration);
      console.log('AI analysis completed:', analysisResult);
    } catch (pythonError) {
      console.error('Python analysis failed, falling back to AI analysis:', pythonError);
      
      // Check if AI clients are available
      if (!process.env.OPENAI_API_KEY || !process.env.ANTHROPIC_API_KEY) {
        throw new Error('AI analysis requires OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables');
      }
      
      // Initialize AI clients if needed
      initializeAIClients();
      
      if (!openai || !anthropic) {
        throw new Error('Failed to initialize AI clients');
      }
      
      // Fallback: Use AI analysis directly
      const transcription = await openai.audio.transcriptions.create({
        file: fs.createReadStream(audioPath),
        model: "whisper-1",
        response_format: "verbose_json",
        timestamp_granularities: ["word"]
      });
      
      // Enhanced prompt for viral clip identification
      const enhancedPrompt = `You are a VIRAL CONTENT EXPERT. Find the MOST VIRAL moments in this video transcript and create clips that will get maximum engagement.

VIRAL CONTENT CRITERIA:
1. **EMOTIONAL TRIGGERS**: Moments that make people feel strong emotions
2. **CONTROVERSIAL STATEMENTS**: Bold claims or statements that spark debate
3. **SHOCKING REVELATIONS**: Unexpected facts or surprising statistics
4. **RELATABLE PROBLEMS**: Issues that most people face
5. **ASPIRATIONAL CONTENT**: Success stories or lifestyle content
6. **HUMOR**: Genuinely funny moments
7. **EDUCATIONAL VALUE**: "Mind-blowing" facts or insights

Create exactly ${numClips} clips, each ${clipDuration} seconds, with realistic timestamps.

Return ONLY valid JSON:
{
  "clips": [
    {
      "start_time": "MM:SS",
      "end_time": "MM:SS", 
      "title": "[VIRAL TITLE WITH CAPS AND EMOJIS]",
      "description": "Why this will go viral: [specific reason]"
    }
  ]
}

Transcript: ${transcription.text}`;

      const analysis = await anthropic.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 2000,
        messages: [{
          role: "user",
          content: enhancedPrompt
        }]
      });
      
      const analysisText = analysis.content[0].text;
      const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        analysisResult = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('Failed to parse AI analysis');
      }
    }
    
    // Create video clips
    const clips = [];
    const clipData = analysisResult.clips || analysisResult.clip_suggestions || [];
    
    for (let i = 0; i < Math.min(numClips, clipData.length); i++) {
      const clip = clipData[i];
      const startTime = timeToSeconds(clip.start_time);
      const endTime = timeToSeconds(clip.end_time);
      const duration = endTime - startTime;
      
      const clipFilename = `clip_${timestamp}_${i + 1}.mp4`;
      const clipPath = path.join(mediaDir, clipFilename);
      
      console.log(`Creating clip ${i + 1}: ${clip.start_time} to ${clip.end_time}`);
      
      try {
        await createVideoClip(videoPath, clipPath, startTime, duration);
        
        clips.push({
          id: i + 1,
          filename: clipFilename,
          url: `/clips/${clipFilename}`,
          download_url: `/download/${clipFilename}`,
          start_time: clip.start_time,
          end_time: clip.end_time,
          duration: duration,
          title: clip.title || `Viral Clip ${i + 1}`,
          description: clip.description || 'AI-generated viral content',
          viral_score: clip.viral_score || Math.floor(Math.random() * 40) + 60, // 60-100
          platform: clip.platform || 'tiktok'
        });
      } catch (clipError) {
        console.error(`Failed to create clip ${i + 1}:`, clipError);
        // Continue with other clips
      }
    }
    
    // Clean up temporary files
    try {
      fs.unlinkSync(audioPath);
      console.log('Cleaned up temporary audio file');
    } catch (cleanupError) {
      console.error('Failed to cleanup audio file:', cleanupError);
    }
    
    console.log(`Analysis completed. Created ${clips.length} clips.`);
    
    res.json({
      success: true,
      message: `Successfully analyzed video and created ${clips.length} viral clips!`,
      clips: clips,
      analysis: {
        total_clips_requested: numClips,
        total_clips_created: clips.length,
        target_duration: clipDuration,
        platform: 'tiktok'
      }
    });
    
  } catch (error) {
    console.error('Analysis failed:', error);
    res.status(500).json({
      error: 'Failed to analyze video',
      details: error.message
    });
  }
});

// Get list of available clips
app.get('/clips-list', (req, res) => {
  try {
    const files = fs.readdirSync(mediaDir);
    const clips = files
      .filter(file => file.endsWith('.mp4') && file.startsWith('clip_'))
      .map(file => ({
        filename: file,
        url: `/clips/${file}`,
        download_url: `/download/${file}`,
        size: fs.statSync(path.join(mediaDir, file)).size
      }));
    
    res.json({
      success: true,
      clips: clips,
      total: clips.length
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to get clips list',
      details: error.message
    });
  }
});

// Helper function to convert time string to seconds
function timeToSeconds(timeStr) {
  const parts = timeStr.split(':').map(Number);
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  } else if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  }
  return 0;
}

// YouTube upload endpoint
app.post('/upload-to-youtube', async (req, res) => {
  const { clipFilename, title, description, tags } = req.body;
  
  if (!clipFilename || !title) {
    return res.status(400).json({ error: 'Clip filename and title are required' });
  }
  
  try {
    const clipPath = path.join(mediaDir, clipFilename);
    if (!fs.existsSync(clipPath)) {
      return res.status(404).json({ error: 'Clip file not found' });
    }
    
    const uploadManager = new YouTubeUploadManager();
    const result = await uploadManager.uploadVideo(clipPath, title, description, tags);
    
    res.json({
      success: true,
      message: 'Video uploaded to YouTube successfully!',
      videoId: result.videoId,
      url: `https://www.youtube.com/watch?v=${result.videoId}`
    });
    
  } catch (error) {
    console.error('YouTube upload failed:', error);
    res.status(500).json({
      error: 'Failed to upload to YouTube',
      details: error.message
    });
  }
});

const PORT = process.env.PORT || 10000;

app.listen(PORT, () => {
  console.log(`🚀 Trilion Backend Server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔍 Test endpoint: http://localhost:${PORT}/test`);
  console.log(`🎬 Main endpoint: http://localhost:${PORT}/analyze`);
});

module.exports = app; 