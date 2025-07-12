require('dotenv').config();
console.log("SERVER STARTED");
const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const OpenAI = require('openai');
const Anthropic = require('@anthropic-ai/sdk');
const YouTubeUploadManager = require('./youtube-upload-manager');
const { spawnSync } = require('child_process');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const app = express();

// Enhanced CORS configuration for production
app.use(cors({
  origin: [
    'http://localhost:3000',
    'http://localhost:3001', 
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'https://trilion-frontend.onrender.com',
    'https://trilion.vercel.app',
    process.env.CORS_ORIGIN
  ].filter(Boolean),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Range']
}));

app.use(express.json());

const mediaDir = path.join(__dirname, 'media');
if (!fs.existsSync(mediaDir)) {
  fs.mkdirSync(mediaDir);
}

// Test endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'Server is running! No file storage - clips are temporary analysis only.',
    status: 'active',
    timestamp: new Date().toISOString(),
    endpoints: {
      analyze: '/analyze',
      clips: '/clips-list',
      test: '/test'
    }
  });
});

// Simple test endpoint for viral analysis
app.post('/test-viral', (req, res) => {
  res.json({ 
    message: 'Viral analysis endpoint is accessible',
    received: req.body,
    timestamp: new Date().toISOString()
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

  // Generate unique filenames
  const timestamp = Date.now();
  const videoFile = `video_${timestamp}.mp4`;
  const audioFile = `audio_${timestamp}.mp3`;
  const videoPath = path.join(mediaDir, videoFile);
  const audioPath = path.join(mediaDir, audioFile);
  
  // Download full video first
  const ytDlpVideoCmd = `yt-dlp -f 'best[height<=720]' -o '${videoPath}' -- '${ytLink}'`;
  
  exec(ytDlpVideoCmd, async (err, stdout, stderr) => {
    console.log('yt-dlp video stdout:', stdout);
    console.log('yt-dlp video stderr:', stderr);
    if (err) {
      console.error('yt-dlp video error:', err);
      return res.status(500).json({ error: 'Failed to download video.', details: stderr });
    }
    
    // Check if video file exists
    fs.access(videoPath, fs.constants.F_OK, async (fileErr) => {
      if (fileErr) {
        console.error('Video file not found after yt-dlp:', videoPath);
        return res.status(500).json({ error: 'Video file not found after download.' });
      }
      
      console.log('Video downloaded, extracting audio for transcription...');
      
      // Extract audio for transcription
      const ffmpegAudioCmd = `ffmpeg -i '${videoPath}' -vn -acodec mp3 '${audioPath}' -y`;
      
      exec(ffmpegAudioCmd, async (audioErr, audioStdout, audioStderr) => {
        if (audioErr) {
          console.error('FFmpeg audio extraction error:', audioErr);
          return res.status(500).json({ error: 'Failed to extract audio for transcription.' });
        }
        
        console.log('Audio extracted, starting transcription...');
        
        try {
          // Transcribe the audio using OpenAI Whisper (word-level, non-destructive upgrade)
          const wordlevelTranscription = await openai.audio.transcriptions.create({
            file: fs.createReadStream(audioPath),
            model: "whisper-1",
            response_format: "verbose_json",
            timestamp_granularities: ["word"]
          });
          // Save the full word-level transcript
          const wordlevelJsonFile = path.join(mediaDir, `video_${timestamp}_wordlevel.json`);
          fs.writeFileSync(wordlevelJsonFile, JSON.stringify(wordlevelTranscription, null, 2));
          
          console.log('Transcription completed, analyzing for viral hooks...');
          
          // Enhanced prompt for viral clip identification
          const enhancedPrompt = `You are a VIRAL CONTENT EXPERT with 10+ years experience creating viral videos for TikTok, Instagram Reels, and YouTube Shorts. You have analyzed millions of viral videos and understand exactly what makes content go viral.

Your task: Find the MOST VIRAL moments in this video transcript and create clips that will get maximum engagement.

VIRAL CONTENT CRITERIA (in order of importance):
1. **EMOTIONAL TRIGGERS**: Moments that make people feel strong emotions (shock, anger, joy, fear, surprise)
2. **CONTROVERSIAL STATEMENTS**: Bold claims, unpopular opinions, or statements that spark debate
3. **SHOCKING REVELATIONS**: Unexpected facts, surprising statistics, or "I didn't know that" moments
4. **RELATABLE PROBLEMS**: Issues that most people face but rarely discuss openly
5. **ASPIRATIONAL CONTENT**: Success stories, wealth reveals, or lifestyle content
6. **HUMOR**: Genuinely funny moments, clever wordplay, or ironic situations
7. **EDUCATIONAL VALUE**: "Mind-blowing" facts or insights that make people want to share

CLIP CREATION RULES:
- Target duration: ${clipDuration} seconds (but end at natural speech boundaries)
- Start at the EXACT moment the viral hook begins
- End when the topic/sentence naturally concludes
- Create exactly ${numClips} clips
- Each clip should be a COMPLETE viral moment

TIMESTAMP ANALYSIS:
- Read the transcript and identify where viral moments occur
- Estimate timestamps based on content flow and speaking pace
- Focus on the MOST engaging 30-60 seconds of each viral moment
- Avoid generic timestamps - be specific and realistic

TITLE CREATION:
- Use CAPS for emphasis on key words
- Include emojis when appropriate (😱 💀 🚨 💰 etc.)
- Make it sound like a clickbait headline that people can't resist
- Keep it under 60 characters for social media

Return ONLY valid JSON:
{
  "clip_suggestions": [
    {
      "start_time": "MM:SS",
      "end_time": "MM:SS", 
      "title": "[VIRAL TITLE WITH CAPS AND EMOJIS]",
      "description": "Why this will go viral: [specific reason based on viral criteria]"
    }
  ]
}

Transcript: ${wordlevelTranscription.text}`;

          // Try Claude first, fallback to GPT if needed
          let analysis;
          let usedProvider = null;
          try {
            analysis = await anthropic.messages.create({
              model: "claude-3-5-sonnet-20241022",
              max_tokens: 2000,
              messages: [{
                role: "user",
                content: enhancedPrompt
              }]
            });
            usedProvider = 'claude';
            console.log('Using Claude for analysis');
          } catch (claudeError) {
            console.error('Claude failed:', claudeError);
            try {
              // Fallback to GPT
              analysis = await openai.chat.completions.create({
                model: "gpt-4o-mini",
                max_tokens: 2000,
                messages: [{
                  role: "user",
                  content: enhancedPrompt
                }],
                response_format: { type: "json_object" }
              });
              usedProvider = 'openai';
              console.log('Using GPT for analysis');
            } catch (gptError) {
              console.error('Both Claude and OpenAI failed:', gptError);
              return res.status(500).json({
                error: 'Both Claude and OpenAI analysis failed.',
                details: {
                  claude: claudeError.message || claudeError,
                  openai: gptError.message || gptError
                }
              });
            }
          }
          console.log('Analysis completed with provider:', usedProvider);
          
          // Parse the analysis response (handle both Claude and GPT)
          let analysisText;
          if (analysis.content && analysis.content[0]) {
            // Claude response
            analysisText = analysis.content[0].text;
          } else if (analysis.choices && analysis.choices[0]) {
            // GPT response
            analysisText = analysis.choices[0].message.content;
          } else {
            throw new Error('Invalid analysis response format');
          }
          
          console.log('Analysis response:', analysisText);
          
          // Parse the analysis to get clip timestamps
          let clipSuggestions = [];
          try {
            // Try to extract JSON from the response
            const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              const analysisData = JSON.parse(jsonMatch[0]);
              clipSuggestions = analysisData.clip_suggestions || [];
            } else {
              throw new Error('No JSON found in response');
            }
            
            // Validate and fix timestamps if they're generic
            clipSuggestions = clipSuggestions.map((clip, index) => {
              // If timestamps are generic (00:00-00:30), generate more realistic ones
              if (clip.start_time === "00:00" && clip.end_time === "00:30") {
                const startSeconds = Math.floor(Math.random() * 60) + 30; // 30-90 seconds
                const duration = Math.floor(Math.random() * 30) + 15; // 15-45 seconds
                const endSeconds = startSeconds + duration;
                
                return {
                  ...clip,
                  start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                  end_time: `${Math.floor(endSeconds / 60)}:${(endSeconds % 60).toString().padStart(2, '0')}`,
                  title: `${clip.title} (AI-generated timestamp)`
                };
              }
              return clip;
            });
            
            console.log('Parsed clip suggestions:', clipSuggestions);
          } catch (parseError) {
            console.error('Failed to parse analysis:', parseError);
            // Fallback: create clips with realistic timestamps
            const videoDuration = 300; // Assume 5 minutes if we can't determine
            clipSuggestions = [];
            for (let i = 0; i < numClips; i++) {
              const startSeconds = Math.floor(Math.random() * (videoDuration - clipDuration)) + 30;
              const endSeconds = startSeconds + clipDuration;
              
              clipSuggestions.push({
                start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                end_time: `${Math.floor(endSeconds / 60)}:${(endSeconds % 60).toString().padStart(2, '0')}`,
                title: `Viral Clip ${i + 1}`,
                description: `Engaging content from the video`
              });
            }
          }
          
          // Create clips with face-centered cropping
          const clips = [];
          const minClipSizeBytes = 100 * 1024; // 100 KB minimum for a valid video
          
          // 🎯 ANALYZE VIDEO TYPE ONCE FOR CONSISTENT PROCESSING
          console.log('🎯 Analyzing overall video type for consistent processing...');
          
          let globalProcessingMethod = 'resize'; // Default to safe option
          let globalSpeakerAnalysis = null;
          
          // Analyze a representative sample of the video (middle 30 seconds)
          const sampleDuration = Math.min(30, clipSuggestions.length > 0 ? timeToSeconds(clipSuggestions[0].end_time) - timeToSeconds(clipSuggestions[0].start_time) : 30);
          const sampleStart = Math.max(0, (timeToSeconds(clipSuggestions[0]?.end_time || '0:30') / 2) - (sampleDuration / 2));
          const globalAnalysisFile = `global_analysis_${timestamp}.json`;
          const globalAnalysisPath = path.join(mediaDir, globalAnalysisFile);
          
          const globalDetectionCmd = `python3 enhanced_speaker_detection.py '${videoPath}' ${sampleStart} ${sampleStart + sampleDuration} '${globalAnalysisPath}'`;
          
          try {
            await new Promise((resolve, reject) => {
              exec(globalDetectionCmd, (globalErr, globalStdout, globalStderr) => {
                if (globalErr) {
                  console.error('🚨 Global speaker detection error:', globalErr);
                  console.log('Global detection stderr:', globalStderr);
                  resolve(); // Continue with default
                } else {
                  console.log('✅ Global speaker detection completed:', globalStdout);
                  resolve();
                }
              });
            });
            
            // Read global analysis results
            if (fs.existsSync(globalAnalysisPath)) {
              globalSpeakerAnalysis = JSON.parse(fs.readFileSync(globalAnalysisPath, 'utf8'));
              
              if (!globalSpeakerAnalysis.error) {
                globalProcessingMethod = globalSpeakerAnalysis.processing_method || 'resize';
                
                console.log('🎬 GLOBAL VIDEO TYPE DETERMINED:');
                if (globalProcessingMethod === 'crop') {
                  console.log('   🎤 SPEAKER-BASED VIDEO - Will crop all clips to focus on speaker');
                  console.log(`   Confidence: ${globalSpeakerAnalysis.confidence?.toFixed(2)}`);
                  console.log(`   Content type: ${globalSpeakerAnalysis.content_analysis?.likely_content_type}`);
                } else {
                  console.log('   📱 CONTENT-BASED VIDEO - Will resize all clips to preserve visual information');
                  console.log(`   Content type: ${globalSpeakerAnalysis.content_analysis?.likely_content_type}`);
                  console.log(`   Reasoning: ${globalSpeakerAnalysis.reasoning?.join('; ')}`);
                }
                console.log('   🔄 Applying this method to ALL clips for consistency...');
              }
              
              // Clean up global analysis file
              fs.unlinkSync(globalAnalysisPath);
            }
          } catch (globalError) {
            console.log('🔄 Global speaker detection failed, using default resize for all clips...');
          }
          
          for (let i = 0; i < Math.min(clipSuggestions.length, numClips); i++) {
            const clip = clipSuggestions[i];
            const clipFileName = `clip_${timestamp}_${i + 1}.mp4`;
            const clipPath = path.join(mediaDir, clipFileName);

            // Convert timestamps to seconds
            const startSeconds = timeToSeconds(clip.start_time);
            const endSeconds = timeToSeconds(clip.end_time);
            const duration = endSeconds - startSeconds;

            // 🚀 USE GLOBAL PROCESSING METHOD FOR ALL CLIPS
            console.log(`🎬 Processing clip ${i + 1}/${numClips} with CONSISTENT method: ${globalProcessingMethod.toUpperCase()}`);
            
            // Generate subtitles for this clip
            console.log(`Generating subtitles for clip ${i + 1}...`);
            
            // Extract transcript for this specific clip segment
            const clipTranscript = wordlevelTranscription.text; // We'll use the full transcript for now

            // Save the transcription for this clip as a JSON file
            const transcriptJsonFile = path.join(mediaDir, `clip_${timestamp}_${i + 1}_transcript.json`);
            // For now, store as a single segment; update this if you have word-level timing
            const transcriptJson = [
              {
                start: startSeconds,
                end: endSeconds,
                text: clipTranscript.trim()
              }
            ];
            fs.writeFileSync(transcriptJsonFile, JSON.stringify(transcriptJson, null, 2));
            
            // Save the word-level transcript for this clip (non-destructive)
            const wordlevelClipFile = path.join(mediaDir, `clip_${timestamp}_${i + 1}_wordlevel.json`);
            if (wordlevelTranscription.words) {
              // Extract only words within this clip's time window
              const wordlevelClip = wordlevelTranscription.words.filter(w => w.start >= startSeconds && w.end <= endSeconds);
              fs.writeFileSync(wordlevelClipFile, JSON.stringify(wordlevelClip, null, 2));
            }

            // Generate synced captions (non-destructive)
            const syncedSubtitleCmd = `python3 subtitle_generator.py '${wordlevelClipFile}' ${duration}`;
            let syncedSubtitleFilter = '';
            try {
              const syncedSubtitleResult = await new Promise((resolve, reject) => {
                exec(syncedSubtitleCmd, (subtitleErr, subtitleStdout, subtitleStderr) => {
                  if (subtitleErr) {
                    resolve('');
                  } else {
                    resolve(subtitleStdout.trim());
                  }
                });
              });
              if (syncedSubtitleResult) {
                syncedSubtitleFilter = syncedSubtitleResult;
              }
            } catch (e) {}

            // Output a new captioned video (non-destructive)
            if (syncedSubtitleFilter) {
              const syncedCaptionedFile = path.join(mediaDir, `clip_${timestamp}_${i + 1}_synced_captioned.mp4`);
              const ffmpegSyncedCmd = `ffmpeg -i '${clipPath}' -vf "${syncedSubtitleFilter}" -c:a copy '${syncedCaptionedFile}' -y`;
              exec(ffmpegSyncedCmd, () => {});
            }

            // 🎯 APPLY CONSISTENT PROCESSING METHOD TO ALL CLIPS
            let extractCmd;
            if (globalProcessingMethod === 'crop' && globalSpeakerAnalysis?.crop_params) {
              // Speaker-based video - use intelligent cropping for ALL clips
              const cropParams = globalSpeakerAnalysis.crop_params;
              extractCmd = `ffmpeg -i '${videoPath}' -i '../logo-removebg-preview.png' -ss ${startSeconds} -t ${duration} -filter_complex "[0:v]crop=${cropParams.crop_width}:${cropParams.crop_height}:${cropParams.crop_x}:${cropParams.crop_y},scale=1080:1920[v];[1:v]scale=150:-1,format=rgba,colorchannelmixer=aa=0.4[logo];[v][logo]overlay=W-w-20:(H-h)/2:format=auto,format=yuv420p[out]" -map "[out]" -map 0:a -c:a copy '${clipPath}' -y`;
              console.log(`   🎤 Using intelligent crop (speaker-focused) + middle-right watermark`);
            } else if (globalProcessingMethod === 'resize') {
              // Content-based video - resize ALL clips to preserve visual information
              extractCmd = `ffmpeg -i '${videoPath}' -i '../logo-removebg-preview.png' -ss ${startSeconds} -t ${duration} -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[v];[1:v]scale=150:-1,format=rgba,colorchannelmixer=aa=0.4[logo];[v][logo]overlay=W-w-20:(H-h)/2:format=auto,format=yuv420p[out]" -map "[out]" -map 0:a -c:a copy '${clipPath}' -y`;
              console.log(`   📱 Using content-preserving resize + middle-right watermark`);
            } else {
              // Fallback to center crop if something went wrong
              extractCmd = `ffmpeg -i '${videoPath}' -i '../logo-removebg-preview.png' -ss ${startSeconds} -t ${duration} -filter_complex "[0:v]crop=ih*9/16:ih,scale=1080:1920[v];[1:v]scale=150:-1,format=rgba,colorchannelmixer=aa=0.4[logo];[v][logo]overlay=W-w-20:(H-h)/2:format=auto,format=yuv420p[out]" -map "[out]" -map 0:a -c:a copy '${clipPath}' -y`;
              console.log(`   🔄 Using fallback center crop + middle-right watermark`);
            }

            let clipSuccess = false;
            let ffmpegError = null;
            let ffmpegStderr = '';
            await new Promise((resolve) => {
              exec(extractCmd, (clipErr, clipStdout, clipStderr) => {
                ffmpegStderr = clipStderr;
                console.log(`FFmpeg stderr for clip ${i + 1}:`, clipStderr);
                if (clipErr) {
                  console.error(`Error creating clip ${i + 1}:`, clipErr);
                  console.error(`ffmpeg stderr for clip ${i + 1}:`, clipStderr);
                  ffmpegError = clipErr.message || 'Unknown ffmpeg error';
                  resolve();
                } else {
                  // Check file size
                  let fileSize = 0;
                  try {
                    if (fs.existsSync(clipPath)) {
                      fileSize = fs.statSync(clipPath).size;
                    }
                  } catch (sizeErr) {
                    fileSize = 0;
                  }
                  if (fileSize >= minClipSizeBytes) {
                    console.log(`✅ Clip ${i + 1} created successfully:`, clipFileName, `(${fileSize} bytes)`);
                    clipSuccess = true;
                  } else {
                    console.error(`Clip ${i + 1} failed: file too small (${fileSize} bytes)`);
                    ffmpegError = 'Clip file too small or empty';
                  }
                  resolve();
                }
              });
            });

            if (clipSuccess) {
              clips.push({
                filename: clipFileName,
                title: clip.title,
                description: clip.description,
                start_time: clip.start_time,
                end_time: clip.end_time,
                // Consistent processing information for ALL clips
                processing_method: globalProcessingMethod,
                has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                // Legacy face tracking info for compatibility
                face_centered: globalProcessingMethod === 'crop',
                face_tracking_enabled: globalProcessingMethod === 'crop',
                face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                vertical_format: true,
                aspect_ratio: '9:16',
                failed: false,
                error: null
              });
            } else {
              clips.push({
                filename: clipFileName,
                title: clip.title,
                description: clip.description,
                start_time: clip.start_time,
                end_time: clip.end_time,
                // Consistent processing information for ALL clips (even failed ones)
                processing_method: globalProcessingMethod,
                has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                // Legacy face tracking info for compatibility
                face_centered: globalProcessingMethod === 'crop',
                face_tracking_enabled: globalProcessingMethod === 'crop',
                face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                vertical_format: true,
                aspect_ratio: '9:16',
                failed: true,
                error: ffmpegError || ffmpegStderr || 'Unknown error during clip creation'
              });
            }
          }
          
          // Only return valid (non-failed) clips to the frontend, but include failed ones with error info for UI warnings
          const validClips = clips.filter(c => !c.failed);
          const failedClips = clips.filter(c => c.failed);
          if (failedClips.length > 0) {
            console.warn(`Some clips failed to generate:`, failedClips.map(c => c.error));
          }

          // Clean up temporary files
          fs.unlink(audioPath, (unlinkErr) => {
            if (unlinkErr) {
              console.error('Error deleting audio file:', unlinkErr);
            } else {
              console.log('Audio file cleaned up successfully:', audioFile);
            }
          });
          
          fs.unlink(videoPath, (unlinkErr) => {
            if (unlinkErr) {
              console.error('Error deleting video file:', unlinkErr);
            } else {
              console.log('Video file cleaned up successfully:', videoFile);
            }
          });
          
          res.json({
            message: failedClips.length > 0 ? `Some clips failed to generate. See 'clips' for details.` : 'Clips created successfully!',
            clips: clips
          });
        } catch (error) {
          console.error('Error:', error);
          res.status(500).json({ error: 'Failed to process video.', details: error.message });
        }
      });
    });
  });
});

// ================================
// 🎯 VIRAL CAPTION ENDPOINTS
// ================================

// Add viral captions to existing clip
app.post('/add-viral-captions', async (req, res) => {
  console.log('POST /add-viral-captions received');
  const { clipFilename, captionStyle = 'single-word', fontStyle = 'impact' } = req.body;
  
  if (!clipFilename) {
    return res.status(400).json({ error: 'No clip filename provided' });
  }
  
  const clipPath = path.join(mediaDir, clipFilename);
  if (!fs.existsSync(clipPath)) {
    return res.status(404).json({ error: 'Clip file not found' });
  }
  
  // Generate viral captioned version
  const timestamp = Date.now();
  const viralFilename = `viral_${captionStyle}_${timestamp}_${clipFilename}`;
  const viralPath = path.join(mediaDir, viralFilename);
  
  console.log(`Adding ${captionStyle} viral captions to: ${clipFilename}`);
  
  // Use our viral caption system
  const viralCmd = `/opt/homebrew/bin/python3.10 viral_caption_system.py '${clipPath}' '${viralPath}' ${captionStyle} ${fontStyle} ${req.body.processingMode || 'crop'}`;
  
  exec(viralCmd, (err, stdout, stderr) => {
    console.log('Viral caption stdout:', stdout);
    console.log('Viral caption stderr:', stderr);
    
    if (err) {
      console.error('Viral caption error:', err);
      
      // Check if it's a language detection error
      if (stdout && stdout.includes('Language not supported')) {
        const errorMatch = stdout.match(/Language not supported: (\w+)\./);
        const detectedLang = errorMatch ? errorMatch[1] : 'unknown';
        return res.status(400).json({ 
          error: `Language not supported: ${detectedLang}. Viral captions are currently only available for English audio. Please use an English video.`,
          detected_language: detectedLang,
          supported_languages: ['en']
        });
      }
      
      return res.status(500).json({ 
        error: 'Failed to add viral captions', 
        details: stderr || err.message 
      });
    }
    
    // Check if viral video was created
    if (fs.existsSync(viralPath)) {
      const fileSize = fs.statSync(viralPath).size;
      res.json({
        message: 'Viral captions added successfully!',
        viralFilename: viralFilename,
        originalFilename: clipFilename,
        captionStyle: captionStyle,
        fontStyle: fontStyle,
        fileSize: fileSize
      });
    } else {
      res.status(500).json({ error: 'Viral video file was not created' });
    }
  });
});

// Create viral clips directly from YouTube link
app.post('/analyze-viral', async (req, res) => {
  console.log('DEBUG: /analyze-viral req.body:', req.body);
  console.log('POST /analyze-viral received');
  const { ytLink, numClips = 3, clipDuration = 30, captionStyle = 'single-word', fontStyle = 'impact', processingMode = 'auto' } = req.body;
  
  if (!ytLink) {
    return res.status(400).json({ error: 'No YouTube link provided' });
  }
  
  console.log('Creating viral clips for:', ytLink);
  console.log('Caption style:', captionStyle, 'Font style:', fontStyle);
  console.log('🎯 USER SELECTED PROCESSING MODE:', processingMode);
  
  // Generate unique filenames
  const timestamp = Date.now();
  const videoFile = `video_${timestamp}.mp4`;
  const videoPath = path.join(mediaDir, videoFile);
  
  // Download video
  const ytDlpCmd = `yt-dlp -f 'best[height<=720]' -o '${videoPath}' -- '${ytLink}'`;
  
  exec(ytDlpCmd, async (err, stdout, stderr) => {
    if (err) {
      console.error('yt-dlp error:', err);
      return res.status(500).json({ error: 'Failed to download video', details: stderr });
    }
    
    // Check if video exists
    if (!fs.existsSync(videoPath)) {
      return res.status(500).json({ error: 'Video file not found after download' });
    }
    
    try {
      // Use enhanced intelligent clip analyzer to find viral content
      console.log('🧠 Running enhanced intelligent clip analysis...');
      const targetPlatform = req.body.platform || 'tiktok'; // Default to TikTok
      const analysisCmd = `python3 intelligent_clip_analyzer.py "${videoPath}" ${numClips} ${targetPlatform} ${clipDuration}`;
      
      let viralAnalysis;
      try {
        const { execSync } = require('child_process');
        // Capture stdout and stderr separately
        const analysisResult = execSync(analysisCmd, { 
          encoding: 'utf8', 
          timeout: 120000,
          maxBuffer: 10 * 1024 * 1024, // 10MB buffer to prevent ENOBUFS
          stdio: ['pipe', 'pipe', 'pipe']  // Separate stdin, stdout, stderr
        });
        
        // Only parse stdout for JSON
        try {
        viralAnalysis = JSON.parse(analysisResult);
        
          if (!viralAnalysis.status || viralAnalysis.status === 'error') {
            throw new Error(viralAnalysis.message || 'Analysis failed');
        }
          
          // Convert the new format to match existing code
          viralAnalysis = {
            success: true,
            clips_found: viralAnalysis.clips ? viralAnalysis.clips.length : (viralAnalysis.total_clips || 0),
            viral_clips: viralAnalysis.clips.map(clip => ({
              start_time: clip.start_time,
              end_time: clip.end_time,
              duration: clip.duration,
              viral_score: clip.viral_score,
              hook_type: clip.hook_type,
              text: clip.text,
              is_fallback: clip.is_fallback,
              hook_strength: clip.quality_metrics.hook_strength,
              completeness_score: clip.quality_metrics.completeness,
              emotional_impact: clip.quality_metrics.emotional_impact,
              attention_score: clip.quality_metrics.attention_score
            }))
          };
        
        console.log(`✅ Intelligent analysis found ${viralAnalysis.clips_found} viral clips!`);
        } catch (parseError) {
          console.error('Failed to parse analysis result:', parseError);
          throw new Error('Failed to parse analysis output');
        }
      } catch (error) {
        console.error('❌ Intelligent analysis failed:', error.message);
        console.log('📧 Falling back to time-based clip selection...');
        
        // Create fallback clips using time-based selection
        viralAnalysis = {
          success: false,
          viral_clips: Array.from({length: numClips}, (_, i) => ({
            start_time: i * 90 + 30, // Start at 30s, 120s, etc.
            end_time: i * 90 + 30 + clipDuration,
            duration: clipDuration,
            hook_type: 'time_based_fallback',
            viral_score: 0.5, // Low score to indicate this is fallback content
            title: `📊 Best Available Clip ${i + 1}`,
            description: 'Time-based selection (intelligent analysis unavailable)',
            quality_rating: 'Basic'
          })),
          clips_found: numClips,
          error: 'Intelligent analysis failed - using time-based fallback',
          suggestion: 'Try content with question hooks, contrarian statements, or shocking revelations'
        };
      }
      
      // Create viral clips based on intelligent analysis
      const viralClips = [];
      const clipData = viralAnalysis.viral_clips || [];
      
      console.log(`📊 Processing ${clipData.length} clips from intelligent analysis...`);
      console.log(`🔍 Requested clips: ${numClips}, Available clips: ${clipData.length}`);
      
      // Check if no clips found at all
      if (clipData.length === 0) {
        console.log('🚫 NO CLIPS CREATED - No content found with any viral potential');
        
        // Clean up original video before returning
        if (fs.existsSync(videoPath)) {
          fs.unlinkSync(videoPath);
        }
        
        return res.json({
          message: `🚫 No clips created - No content found with viral potential. Try content with stronger hooks like questions, contrarian statements, or shocking revelations.`,
          clips: [],
          successfulClips: 0,
          failedClips: 0,
          captionStyle: captionStyle,
          fontStyle: fontStyle,
          analysis_method: 'AI Intelligence',
          analysis_success: true,
          total_viral_clips_found: 0,
          reason: 'No segments found with measurable viral potential',
          viral_analysis_details: {
            content_analyzed: true,
            recommendation: 'Try videos with question hooks ("Why do..."), contrarian statements ("But actually..."), or shocking revelations'
          }
        });
      }
      
      // 🎯 DETERMINE PROCESSING METHOD BASED ON USER CHOICE
      console.log('🎯 Determining processing method for consistent viral processing...');
      console.log(`👤 User selected: ${processingMode}`);
      
      let globalProcessingMethod = 'resize'; // Default to safe option
      let globalSpeakerAnalysis = null;
      
      if (processingMode === 'auto') {
        // AUTO-DETECT: Analyze the first clip segment as representative sample
        console.log('🤖 Running auto-detection...');
        const firstClip = clipData[0];
        const sampleStart = Math.floor(firstClip.start_time);
        const sampleDuration = Math.floor(firstClip.duration || clipDuration);
        const globalAnalysisFile = `global_viral_analysis_${timestamp}.json`;
        const globalAnalysisPath = path.join(mediaDir, globalAnalysisFile);
        
        const globalDetectionCmd = `python3 enhanced_speaker_detection.py '${videoPath}' ${sampleStart} ${sampleStart + sampleDuration} '${globalAnalysisPath}'`;
        
        try {
          await new Promise((resolve, reject) => {
            exec(globalDetectionCmd, (globalErr, globalStdout, globalStderr) => {
              if (globalErr) {
                console.error('🚨 Auto-detection error:', globalErr);
                console.log('Auto-detection stderr:', globalStderr);
                resolve(); // Continue with default
              } else {
                console.log('✅ Auto-detection completed:', globalStdout);
                resolve();
              }
            });
          });
          
          // Read global analysis results
          if (fs.existsSync(globalAnalysisPath)) {
            globalSpeakerAnalysis = JSON.parse(fs.readFileSync(globalAnalysisPath, 'utf8'));
            
            if (!globalSpeakerAnalysis.error) {
              globalProcessingMethod = globalSpeakerAnalysis.processing_method || 'resize';
              
              console.log('🎬 AUTO-DETECTED VIDEO TYPE:');
              if (globalProcessingMethod === 'crop') {
                console.log('   🎤 SPEAKER-BASED VIDEO - Will crop all viral clips to focus on speaker');
                console.log(`   Confidence: ${globalSpeakerAnalysis.confidence?.toFixed(2)}`);
                console.log(`   Content type: ${globalSpeakerAnalysis.content_analysis?.likely_content_type}`);
              } else {
                console.log('   📱 CONTENT-BASED VIDEO - Will resize all viral clips to preserve visual information');
                console.log(`   Content type: ${globalSpeakerAnalysis.content_analysis?.likely_content_type}`);
                console.log(`   Reasoning: ${globalSpeakerAnalysis.reasoning?.join('; ')}`);
              }
              console.log('   🔄 Applying this method to ALL viral clips for consistency...');
            }
            
            // Clean up global analysis file
            fs.unlinkSync(globalAnalysisPath);
          }
        } catch (globalError) {
          console.log('🔄 Auto-detection failed, using default resize for all clips...');
        }
      } else if (processingMode === 'crop') {
        // USER CHOSE CROP: Force cropping with face detection
        console.log('🎤 USER SELECTED: Cropped mode - Using face detection for ALL clips');
        globalProcessingMethod = 'crop';
        
        // Still run speaker detection to get crop parameters for face detection
        const firstClip = clipData[0];
        const sampleStart = Math.floor(firstClip.start_time);
        const sampleDuration = Math.floor(firstClip.duration || clipDuration);
        const globalAnalysisFile = `global_viral_analysis_${timestamp}.json`;
        const globalAnalysisPath = path.join(mediaDir, globalAnalysisFile);
        
        const globalDetectionCmd = `python3 enhanced_speaker_detection.py '${videoPath}' ${sampleStart} ${sampleStart + sampleDuration} '${globalAnalysisPath}'`;
        
        try {
          await new Promise((resolve, reject) => {
            exec(globalDetectionCmd, (globalErr, globalStdout, globalStderr) => {
              if (globalErr) {
                console.error('🚨 Face detection error:', globalErr);
                console.log('Face detection stderr:', globalStderr);
              } else {
                console.log('✅ Face detection analysis completed:', globalStdout);
              }
              resolve(); // Continue regardless of result
            });
          });
          
          // Read crop parameters if available
          if (fs.existsSync(globalAnalysisPath)) {
            globalSpeakerAnalysis = JSON.parse(fs.readFileSync(globalAnalysisPath, 'utf8'));
            console.log('🎯 Using enhanced face detection for cropping');
            
            // Clean up global analysis file
            fs.unlinkSync(globalAnalysisPath);
          }
        } catch (globalError) {
          console.log('⚠️ Face detection failed, will use center crop as fallback...');
        }
      } else if (processingMode === 'resize') {
        // USER CHOSE RESIZE: Force resizing to preserve all content
        console.log('📱 USER SELECTED: Rescaled mode - Preserving all visual content');
        globalProcessingMethod = 'resize';
        
        // Create mock analysis for consistency
        globalSpeakerAnalysis = {
          has_visible_speaker: false,
          content_analysis: {
            likely_content_type: 'user_selected_resize'
          },
          confidence: 1.0,
          reasoning: ['User manually selected resize mode to preserve visual content']
        };
      }
      
      for (let i = 0; i < clipData.length; i++) {
        const clip = clipData[i];
        const startSeconds = Math.floor(clip.start_time);
        const duration = Math.floor(clipDuration);
        
        // ----------------------------------------------------------------
        // NEW 4-STEP PIPELINE: Raw -> (Conditional)Crop -> Scale -> Captions
        // ----------------------------------------------------------------
        const rawFilename = `raw_clip_${timestamp}_${i + 1}.mp4`;
        const rawPath = path.join(mediaDir, rawFilename);
        
        const croppedFilename = `cropped_clip_${timestamp}_${i + 1}.mp4`;
        const croppedPath = path.join(mediaDir, croppedFilename);
        
        const clipFilename = `viral_clip_${timestamp}_${i + 1}.mp4`;
        const clipPath = path.join(mediaDir, clipFilename);

        console.log(`🎬 Creating viral clip ${i + 1}/${clipData.length}...`);
        console.log(`🕐 Clip timing: startSeconds=${startSeconds}, duration=${duration}, endSeconds=${startSeconds + duration}`);
        console.log(`📁 File paths: raw=${rawFilename}, final=${clipFilename}`);
        
        // STEP 1: Extract raw clip segment (no processing)
        console.log('🎞️  STEP 1: Extracting raw clip with re-encoding to fix sync...');
        console.log(`📋 Raw extraction: ffmpeg -i ${videoPath} -ss ${startSeconds} -t ${duration} -c:v libx264 -c:a aac`);
        const rawStartTime = Date.now();
        const rawCmd = [
          'ffmpeg', '-i', videoPath,
          '-ss', startSeconds.toString(),
          '-t', duration.toString(),
          '-c:v', 'libx264', '-c:a', 'aac', '-y', rawPath
        ];
        const rawResult = spawnSync(rawCmd[0], rawCmd.slice(1), { stdio: 'inherit' });
        const rawEndTime = Date.now();
        console.log(`⏱️  Raw extraction took ${rawEndTime - rawStartTime}ms, exit code: ${rawResult.status}`);
        // Probe raw clip metadata for debugging
        try {
          const { execSync } = require('child_process');
          const rawStats = fs.statSync(rawPath);
          console.log(`📊 Raw clip created: ${rawStats.size} bytes`);
          const probeCmd = `ffprobe -v quiet -select_streams v:0 -show_entries stream=duration,start_time,codec_name,width,height -of csv=p=0 "${rawPath}"`;
          const rawMetadata = execSync(probeCmd, { encoding: 'utf8' }).trim();
          console.log(`🔍 Raw clip metadata: ${rawMetadata}`);
        } catch (probeError) {
          console.warn(`⚠️  Could not probe raw clip: ${probeError.message}`);
        }
        
        if (rawResult.status !== 0) {
          console.error(`Raw clip extraction failed for clip ${i + 1}`);
          continue;
        }

        let sourceForScaling = rawPath;

        // DEBUG LOGS for mode
        const normalizedProcessingMode = (processingMode || '').toLowerCase().trim();
        console.log('DEBUG: processingMode =', processingMode, '| normalizedProcessingMode =', normalizedProcessingMode, '| globalProcessingMethod =', globalProcessingMethod);

        // STEP 2: Dynamic face crop (720x1280 vertical) - ONLY IF PROCESSING MODE IS NOT 'resize'
        if (normalizedProcessingMode !== 'resize') {
          console.log('   🤖 Running dynamic face crop ...');
          const cropResult = spawnSync('/opt/homebrew/bin/python3.10', [
            path.join(__dirname, 'enhanced_speaker_detection.py'),
            '--dynamic-crop', rawPath, croppedPath
          ], { stdio: 'inherit' });
          if (cropResult.status !== 0) {
            console.warn(`   ⚠️  Dynamic crop failed, using raw clip as fallback`);
            fs.copyFileSync(rawPath, croppedPath);
          }
          sourceForScaling = croppedPath;
        } else {
          console.log('   📱 Skipping face crop (resize mode selected)');
          sourceForScaling = rawPath;
        }

        // STEP 3: Scale to 1080x1920 + watermark
        console.log('🖼️  STEP 3: Scaling to 1080x1920 & adding watermark...');
        console.log(`📋 Scale command: ffmpeg -i ${sourceForScaling} + watermark -> ${clipPath}`);
        const scaleStartTime = Date.now();
        const scaleCmd = [
          'ffmpeg', '-i', sourceForScaling, '-i', '../logo-removebg-preview.png',
          '-filter_complex', "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[v];[1:v]scale=150:-1,format=rgba,colorchannelmixer=aa=0.4[logo];[v][logo]overlay=W-w-20:(H-h)/2:format=auto,format=yuv420p[out]",
          '-map', '[out]', '-map', '0:a?', '-c:a', 'copy', '-y', clipPath
        ];
        const scaleResult = spawnSync(scaleCmd[0], scaleCmd.slice(1), { stdio: 'inherit' });
        const scaleEndTime = Date.now();
        console.log(`⏱️  Scaling took ${scaleEndTime - scaleStartTime}ms, exit code: ${scaleResult.status}`);
        if (scaleResult.status !== 0) {
          console.error(`Scaling failed for clip ${i + 1}`);
          continue;
        }

        // Clean up intermediate files
        [rawPath, croppedPath].forEach(p => { 
          try { if (fs.existsSync(p)) fs.unlinkSync(p); } catch(e){} 
        });

        // STEP 4: Continue with viral captions (clip is now proper 1080x1920 vertical)
        console.log(`📹 STEP 4: Final clip ready, proceeding to viral captions...`);
        console.log(`🔍 Final clip path: ${clipPath}`);
        // Check final clip metadata
        try {
          const finalStats = fs.statSync(clipPath);
          console.log(`📊 Final clip size: ${finalStats.size} bytes`);
        } catch (e) { console.warn(`⚠️  Could not check final clip: ${e.message}`); }
        
        await new Promise((resolve) => {
          // Skip old extractCmd - clip is already processed above
            
            // Add viral captions
            const viralFilename = `VIRAL_${captionStyle}_${timestamp}_${i + 1}.mp4`;
            const viralPath = path.join(mediaDir, viralFilename);
            
            console.log(`🎨 STEP 5: Adding viral captions...`);
            console.log(`📋 Caption command: viral_caption_system.py '${clipPath}' '${viralPath}' ${captionStyle} ${fontStyle} ${normalizedProcessingMode}`);
            const captionStartTime = Date.now();
            const viralCmd = `/opt/homebrew/bin/python3.10 viral_caption_system.py '${clipPath}' '${viralPath}' ${captionStyle} ${fontStyle} ${normalizedProcessingMode}`;
            
            exec(viralCmd, (viralErr, viralStdout, viralStderr) => {
              const captionEndTime = Date.now();
              console.log(`⏱️  Viral caption processing took ${captionEndTime - captionStartTime}ms`);
              console.log(`Viral processing for clip ${i + 1}:`);
              console.log('Stdout:', viralStdout);
              console.log('Stderr:', viralStderr);
              
              // Check for language detection errors
              if (viralErr && viralStdout && viralStdout.includes('Language not supported')) {
                const errorMatch = viralStdout.match(/Language not supported: (\w+)\./);
                const detectedLang = errorMatch ? errorMatch[1] : 'unknown';
                
                console.log(`Language not supported for clip ${i + 1}: ${detectedLang}`);
                
                // Add failed clip to results
                viralClips.push({
                  filename: viralFilename,
                  title: `❌ FAILED Clip ${i + 1} - Language Error`,
                  description: `Language not supported: ${detectedLang}. Only English audio is supported.`,
                  start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                  end_time: `${Math.floor((startSeconds + duration) / 60)}:${((startSeconds + duration) % 60).toString().padStart(2, '0')}`,
                  captionStyle: captionStyle,
                  fontStyle: fontStyle,
                  fileSize: 0,
                  hook_type: clip.hook_type || 'unknown',
                  viral_score: clip.viral_score || 0,
                  analysis_method: viralAnalysis.success ? 'AI Intelligence' : 'Random Fallback',
                  // Consistent processing information for ALL clips
                  processing_method: globalProcessingMethod,
                  has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                  content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                  speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                  detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                  // Legacy face tracking info for compatibility
                  face_tracking_enabled: globalProcessingMethod === 'crop',
                  face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                  crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                  vertical_format: true,
                  aspect_ratio: '9:16',
                  failed: true,
                  error: `Language not supported: ${detectedLang}. Only English audio is supported.`
                });
                
                // Clean up basic clip
                if (fs.existsSync(clipPath)) fs.unlinkSync(clipPath);
                resolve();
                return;
              }
              
              if (viralErr) {
                console.error(`Viral caption error for clip ${i + 1}:`, viralErr);
                console.error('Stderr:', viralStderr);
                
                // Add failed clip to results
                viralClips.push({
                  filename: viralFilename,
                  title: `❌ FAILED Clip ${i + 1} - Processing Error`,
                  description: `Failed to add viral captions: ${viralErr.message || 'Unknown error'}`,
                  start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                  end_time: `${Math.floor((startSeconds + duration) / 60)}:${((startSeconds + duration) % 60).toString().padStart(2, '0')}`,
                  captionStyle: captionStyle,
                  fontStyle: fontStyle,
                  fileSize: 0,
                  hook_type: clip.hook_type || 'unknown',
                  viral_score: clip.viral_score || 0,
                  analysis_method: viralAnalysis.success ? 'AI Intelligence' : 'Random Fallback',
                  // Consistent processing information for ALL clips
                  processing_method: globalProcessingMethod,
                  has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                  content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                  speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                  detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                  // Legacy face tracking info for compatibility
                  face_tracking_enabled: globalProcessingMethod === 'crop',
                  face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                  crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                  vertical_format: true,
                  aspect_ratio: '9:16',
                  failed: true,
                  error: viralStderr || viralErr.message || 'Unknown error during viral caption processing'
                });
                
                // Clean up basic clip
                if (fs.existsSync(clipPath)) fs.unlinkSync(clipPath);
                resolve();
                return;
              }
              
              if (fs.existsSync(viralPath)) {
                const fileSize = fs.statSync(viralPath).size;
                if (fileSize > 100000) { // 100KB minimum
                  console.log(`✅ Viral clip ${i + 1} created successfully: ${viralFilename} (${fileSize} bytes)`);
                  
                  // POST-CREATION ANALYSIS: Verify what we actually created
                  console.log(`🔍 Analyzing created clip ${i + 1}...`);
                  let postAnalysis = { quality_check: "✅ Created", actual_content: "Analyzing..." };
                  
                  try {
                    const { execSync } = require('child_process');
                    const analysisCmd = `/opt/homebrew/bin/python3.10 -c "
from intelligent_clip_analyzer import analyze_created_clip
import json
import sys
result = analyze_created_clip('${viralPath}')
print(json.dumps(result), file=sys.stdout)
"`;
                    const analysisResult = execSync(analysisCmd, { 
                      encoding: 'utf8', 
                      timeout: 15000,
                      stdio: ['pipe', 'pipe', 'pipe']  // Separate stdin, stdout, stderr
                    });
                    
                    try {
                    postAnalysis = JSON.parse(analysisResult);
                    console.log(`📊 Post-analysis complete: ${postAnalysis.quality_check}`);
                    } catch (parseError) {
                      console.error('Failed to parse post-analysis result:', parseError);
                      postAnalysis = { quality_check: "⚠️ Analysis failed", actual_content: "Parse error" };
                    }
                  } catch (error) {
                    console.log(`⚠️ Post-analysis failed: ${error.message}`);
                  }
                  
                  viralClips.push({
                    filename: viralFilename,
                    title: clip.title || `🚀 VIRAL Clip ${i + 1} - ${clip.hook_type?.replace('_', ' ').toUpperCase() || captionStyle.toUpperCase()}`,
                    description: clip.description || `AI-selected ${clip.hook_type || 'viral'} content with ${captionStyle} captions`,
                    start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                    end_time: `${Math.floor((startSeconds + duration) / 60)}:${((startSeconds + duration) % 60).toString().padStart(2, '0')}`,
                    captionStyle: captionStyle,
                    fontStyle: fontStyle,
                    fileSize: fileSize,
                    hook_type: clip.hook_type || 'unknown',
                    viral_score: clip.viral_score || 0,
                    natural_flow_score: clip.natural_flow_score || 0,
                    emotional_intensity: clip.emotional_intensity || 0,
                    pacing_score: clip.pacing_score || 0,
                    platform_optimization: clip.platform_optimization || 0,
                    content_quality: clip.content_quality || 0,
                    quality_rating: clip.quality_rating || '📈 Generated',
                    platform_optimized_for: clip.platform_optimized_for || targetPlatform,
                    is_fallback: clip.is_fallback || false,
                    quality_disclaimer: clip.quality_disclaimer || null,
                    analysis_method: viralAnalysis.success ? 'Next-Generation AI Enhanced Intelligence' : 'Random Fallback',
                    post_analysis: postAnalysis,
                    // Consistent processing information for ALL clips
                    processing_method: globalProcessingMethod,
                    has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                    content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                    speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                    detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                    // Legacy face tracking info for compatibility
                    face_tracking_enabled: globalProcessingMethod === 'crop',
                    face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                    crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                    vertical_format: true,
                    aspect_ratio: '9:16',
                    failed: false
                  });
                } else {
                  console.error(`Viral clip ${i + 1} too small: ${fileSize} bytes`);
                  viralClips.push({
                    filename: viralFilename,
                    title: `❌ FAILED Clip ${i + 1} - File Too Small`,
                    description: `Generated file too small (${fileSize} bytes). Check audio quality.`,
                    start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                    end_time: `${Math.floor((startSeconds + duration) / 60)}:${((startSeconds + duration) % 60).toString().padStart(2, '0')}`,
                    captionStyle: captionStyle,
                    fontStyle: fontStyle,
                    fileSize: fileSize,
                    hook_type: clip.hook_type || 'unknown',
                    viral_score: clip.viral_score || 0,
                    analysis_method: viralAnalysis.success ? 'Next-Generation AI Enhanced Intelligence' : 'Random Fallback',
                    // Consistent processing information for ALL clips
                    processing_method: globalProcessingMethod,
                    has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                    content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                    speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                    detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                    // Legacy face tracking info for compatibility
                    face_tracking_enabled: globalProcessingMethod === 'crop',
                    face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                    crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                    vertical_format: true,
                    aspect_ratio: '9:16',
                    failed: true,
                    error: `Generated file too small (${fileSize} bytes)`
                  });
                }
              } else {
                console.error(`Viral clip ${i + 1} file not created: ${viralPath}`);
                viralClips.push({
                  filename: viralFilename,
                  title: `❌ FAILED Clip ${i + 1} - File Not Created`,
                  description: `Viral caption processing failed - no output file generated`,
                  start_time: `${Math.floor(startSeconds / 60)}:${(startSeconds % 60).toString().padStart(2, '0')}`,
                  end_time: `${Math.floor((startSeconds + duration) / 60)}:${((startSeconds + duration) % 60).toString().padStart(2, '0')}`,
                  captionStyle: captionStyle,
                  fontStyle: fontStyle,
                  fileSize: 0,
                  hook_type: clip.hook_type || 'unknown',
                  viral_score: clip.viral_score || 0,
                  analysis_method: viralAnalysis.success ? 'AI Intelligence' : 'Random Fallback',
                  // Consistent processing information for ALL clips
                  processing_method: globalProcessingMethod,
                  has_visible_speaker: globalSpeakerAnalysis?.has_visible_speaker || false,
                  content_type: globalSpeakerAnalysis?.content_analysis?.likely_content_type || 'unknown',
                  speaker_confidence: globalSpeakerAnalysis?.confidence || 0.0,
                  detection_reasoning: globalSpeakerAnalysis?.reasoning || [],
                  // Legacy face tracking info for compatibility
                  face_tracking_enabled: globalProcessingMethod === 'crop',
                  face_detection_confidence: globalSpeakerAnalysis?.crop_params?.face_detection_confidence || 0.0,
                  crop_method: globalProcessingMethod === 'crop' ? 'enhanced_speaker_detection' : 'resize_to_fit',
                  vertical_format: true,
                  aspect_ratio: '9:16',
                  failed: true,
                  error: 'No output file generated'
                });
              }
              
              // Clean up basic clip
              if (fs.existsSync(clipPath)) {
                fs.unlinkSync(clipPath);
              }
              
              resolve();
            });
        });
      }
      
      // Clean up original video
      if (fs.existsSync(videoPath)) {
        fs.unlinkSync(videoPath);
      }
      
      // Separate successful and failed clips
      const successfulClips = viralClips.filter(clip => !clip.failed);
      const failedClips = viralClips.filter(clip => clip.failed);
      
      console.log(`📊 FINAL SUMMARY: ${clipData.length} clips analyzed, ${successfulClips.length} successful, ${failedClips.length} failed`);
      if (failedClips.length > 0) {
        console.log(`❌ Failed clips: ${failedClips.map(clip => `${clip.title}: ${clip.error}`).join(', ')}`);
      }
      
      // CLEANUP PERSISTENT WHISPER MODEL (MAJOR PERFORMANCE OPTIMIZATION)
      console.log(`🧹 Cleaning up persistent Whisper model after processing all clips...`);
      exec('/opt/homebrew/bin/python3.10 -c "from persistent_whisper_manager import cleanup_persistent_whisper; cleanup_persistent_whisper()"', (cleanupErr) => {
        if (cleanupErr) {
          console.error('Whisper cleanup warning:', cleanupErr);
        } else {
          console.log('✅ Whisper model cleanup completed');
        }
      });
      
      let message = '';
      const analysisType = viralAnalysis?.success ? '🧠 AI-selected' : '📧 Random fallback';
      
      // Analyze viral quality of successful clips
      let viralQualityInfo = '';
      if (successfulClips.length > 0) {
        const highQualityClips = successfulClips.filter(clip => !clip.is_fallback);
        const fallbackClips = successfulClips.filter(clip => clip.is_fallback);
        const viralClips = highQualityClips.filter(clip => clip.viral_score >= 5.0);
        const goodClips = highQualityClips.filter(clip => clip.viral_score >= 3.0 && clip.viral_score < 5.0);
        const decentClips = highQualityClips.filter(clip => clip.viral_score >= 1.0 && clip.viral_score < 3.0);
        
        const scores = successfulClips.map(clip => clip.viral_score).sort((a, b) => b - a);
        const highestScore = scores[0] || 0;
        
        if (viralClips.length > 0) {
          viralQualityInfo = ` (🔥 ${viralClips.length} viral-quality clips`;
          if (fallbackClips.length > 0) {
            viralQualityInfo += `, ⚠️ ${fallbackClips.length} lower-quality clips included)`;
          } else {
            viralQualityInfo += ')';
          }
        } else if (goodClips.length > 0) {
          viralQualityInfo = ` (✨ ${goodClips.length} good clips, highest score: ${highestScore.toFixed(1)}`;
          if (fallbackClips.length > 0) {
            viralQualityInfo += `, ⚠️ ${fallbackClips.length} lower-quality clips included)`;
          } else {
            viralQualityInfo += ')';
          }
        } else {
          viralQualityInfo = ` (📊 Best available content, highest score: ${highestScore.toFixed(1)}`;
          if (fallbackClips.length > 0) {
            viralQualityInfo += `, ⚠️ ${fallbackClips.length} lower-quality clips included)`;
          } else {
            viralQualityInfo += ')';
          }
        }
      }
      
      if (successfulClips.length === 0 && failedClips.length > 0) {
        message = `0 clips created with ${captionStyle} captions! All ${failedClips.length} clips failed. (${analysisType} analysis)`;
      } else if (successfulClips.length > 0 && failedClips.length > 0) {
        message = `Created ${successfulClips.length} ${analysisType} clips with ${captionStyle} captions${viralQualityInfo}! ${failedClips.length} clips failed.`;
      } else if (successfulClips.length > 0) {
        message = `Created ${successfulClips.length} ${analysisType} clips with ${captionStyle} captions${viralQualityInfo}!`;
      } else {
        message = `No clips processed.`;
      }
      
      res.json({
        message: message,
        clips: viralClips,
        successfulClips: successfulClips.length,
        failedClips: failedClips.length,
        captionStyle: captionStyle,
        fontStyle: fontStyle,
        target_platform: targetPlatform,
        analysis_method: viralAnalysis?.success ? 'Enhanced AI Intelligence (Phase 1)' : 'Random Fallback',
        analysis_success: viralAnalysis?.success || false,
        total_viral_clips_found: viralAnalysis?.clips_found || 0,
        errors: failedClips.length > 0 ? failedClips.map(clip => `${clip.title}: ${clip.error}`).join('; ') : null
      });
      
    } catch (error) {
      console.error('Error creating viral clips:', error);
      
      // Cleanup on error too
      console.log(`🧹 Emergency cleanup of persistent Whisper model...`);
      exec('/opt/homebrew/bin/python3.10 -c "from persistent_whisper_manager import cleanup_persistent_whisper; cleanup_persistent_whisper()"', () => {});
      
      res.status(500).json({ error: 'Failed to create viral clips', details: error.message });
    }
  });
});

// Get list of all clips (including viral ones)
app.get('/clips-list', (req, res) => {
  try {
    const files = fs.readdirSync(mediaDir);
    const clips = files
      .filter(file => file.endsWith('.mp4'))
      .map(file => {
        const filePath = path.join(mediaDir, file);
        const stats = fs.statSync(filePath);
        
        return {
          filename: file,
          size: stats.size,
          created: stats.birthtime,
          isViral: file.includes('viral_') || file.includes('VIRAL_'),
          captionStyle: file.includes('single-word') ? 'single-word' : 
                       file.includes('engaging') ? 'engaging' : 'standard',
          url: `http://localhost:5000/clips/${file}`
        };
      })
      .sort((a, b) => new Date(b.created) - new Date(a.created));
    
    res.json({ clips });
  } catch (error) {
    res.status(500).json({ error: 'Failed to list clips', details: error.message });
  }
});

// ================================
// 🎯 VIRAL TITLE GENERATION ENDPOINTS
// ================================

// Generate viral titles for any video or URL
app.post('/generate-titles', async (req, res) => {
  console.log('POST /generate-titles received');
  const { 
    videoUrl, 
    videoFile, 
    platform = 'tiktok', 
    numTitles = 5, 
    style = 'mega_viral' 
  } = req.body;
  
  if (!videoUrl && !videoFile) {
    return res.status(400).json({ 
      error: 'Either videoUrl or videoFile must be provided' 
    });
  }
  
  const timestamp = Date.now();
  let videoPath;
  let tempVideo = false;
  
  try {
    // Handle video source
    if (videoUrl) {
      console.log(`🎯 Generating titles for YouTube video: ${videoUrl}`);
      
      // Download video for analysis
      const tempVideoFile = `temp_title_analysis_${timestamp}.mp4`;
      videoPath = path.join(mediaDir, tempVideoFile);
      tempVideo = true;
      
      const ytDlpCmd = `yt-dlp -f 'best[height<=720]' -o '${videoPath}' -- '${videoUrl}'`;
      
      await new Promise((resolve, reject) => {
        exec(ytDlpCmd, (err, stdout, stderr) => {
          if (err) {
            console.error('yt-dlp error:', err);
            reject(new Error('Failed to download video for analysis'));
          } else {
            console.log('✅ Video downloaded for title analysis');
            resolve();
          }
        });
      });
    } else {
      // Use existing video file
      videoPath = path.join(mediaDir, videoFile);
      
      if (!fs.existsSync(videoPath)) {
        return res.status(404).json({ 
          error: 'Video file not found' 
        });
      }
      
      console.log(`🎯 Generating titles for existing video: ${videoFile}`);
    }
    
    // Generate viral titles using Python integration
    console.log(`🧠 Running AI title generation for ${platform} (${style} style)...`);
    
    const titleCmd = `/opt/homebrew/bin/python3.10 -c "
import asyncio
import sys
import json
sys.path.append('.')
from intelligent_clip_analyzer import generate_viral_titles_for_video

async def main():
    try:
        result = await generate_viral_titles_for_video(
            '${videoPath}',
            '${platform}',
            ${numTitles},
            '${style}'
        )
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))

asyncio.run(main())
"`;
    
    const titleResult = await new Promise((resolve, reject) => {
      exec(titleCmd, { maxBuffer: 1024 * 1024 * 10 }, (err, stdout, stderr) => {
        if (err) {
          console.error('Title generation error:', err);
          console.error('Title generation stderr:', stderr);
          reject(new Error('Title generation failed'));
        } else {
          try {
            const result = JSON.parse(stdout.trim());
            resolve(result);
          } catch (parseErr) {
            console.error('Failed to parse title generation result:', parseErr);
            console.error('Raw output:', stdout);
            reject(new Error('Failed to parse title generation output'));
          }
        }
      });
    });
    
    // Clean up temporary video if needed
    if (tempVideo && fs.existsSync(videoPath)) {
      fs.unlinkSync(videoPath);
      console.log('🧹 Cleaned up temporary video file');
    }
    
    // Return results
    if (titleResult.status === 'success') {
      console.log(`✅ Generated ${titleResult.total_titles} viral titles successfully!`);
      
      res.json({
        success: true,
        message: `Generated ${titleResult.total_titles} viral titles for ${platform}`,
        platform: platform,
        style: style,
        totalTitles: titleResult.total_titles,
        titles: titleResult.titles,
        optimizationRecommendations: titleResult.optimization_recommendations,
        performancePredictions: titleResult.performance_predictions,
        contentAnalysis: titleResult.content_analysis_summary,
        generationTime: new Date().toISOString()
      });
    } else {
      console.log('⚠️ Title generation fell back to basic mode');
      
      res.json({
        success: true,
        message: 'Generated basic titles (revolutionary system unavailable)',
        platform: platform,
        style: 'basic',
        totalTitles: titleResult.total_titles || 0,
        titles: titleResult.titles || [],
        optimizationRecommendations: titleResult.optimization_recommendations || [],
        performancePredictions: titleResult.performance_predictions || {},
        contentAnalysis: titleResult.content_analysis_summary || {},
        generationTime: new Date().toISOString(),
        fallbackMode: true
      });
    }
    
  } catch (error) {
    console.error('Title generation failed:', error);
    
    // Clean up temporary video if needed
    if (tempVideo && videoPath && fs.existsSync(videoPath)) {
      fs.unlinkSync(videoPath);
    }
    
    res.status(500).json({
      success: false,
      error: 'Title generation failed',
      details: error.message
    });
  }
});

// Generate titles for existing clip
app.post('/generate-titles-for-clip', async (req, res) => {
  console.log('POST /generate-titles-for-clip received');
  const { 
    clipFilename, 
    platform = 'tiktok', 
    numTitles = 5, 
    style = 'mega_viral' 
  } = req.body;
  
  if (!clipFilename) {
    return res.status(400).json({ 
      error: 'No clip filename provided' 
    });
  }
  
  const clipPath = path.join(mediaDir, clipFilename);
  
  if (!fs.existsSync(clipPath)) {
    return res.status(404).json({ 
      error: 'Clip file not found' 
    });
  }
  
  try {
    console.log(`🎯 Generating titles for clip: ${clipFilename}`);
    
    // Simple Node.js-based title generation
    const titleResult = generateSimpleTitles(clipFilename, platform, numTitles, style);
    
    console.log(`✅ Generated ${titleResult.titles.length} viral titles for clip!`);
    
    res.json({
      success: true,
      message: `Generated ${titleResult.titles.length} viral titles for clip`,
      clipFilename: clipFilename,
      platform: platform,
      style: style,
      totalTitles: titleResult.titles.length,
      titles: titleResult.titles,
      optimizationRecommendations: titleResult.optimizationRecommendations,
      performancePredictions: titleResult.performancePredictions,
      contentAnalysis: titleResult.contentAnalysis,
      generationTime: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Title generation failed:', error);
    
    res.status(500).json({
      success: false,
      error: 'Title generation failed',
      details: error.message
    });
  }
});

// Simple Node.js title generation function
function generateSimpleTitles(clipFilename, platform, numTitles, style) {
  // Extract content hints from filename
  const contentHints = clipFilename
    .replace('.mp4', '')
    .replace('VIRAL_', '')
    .replace('single-word_', '')
    .replace(/\d+_/g, '')
    .replace(/_/g, ' ')
    .trim() || 'content';
  
  // Platform-specific viral templates
  const platformTemplates = {
    tiktok: {
      mega_viral: [
        "POV: You Won't Believe What Happens Next 😱",
        "This Changes Everything You Know About Success 🤯",
        "Tell Me You're Mind-Blown Without Telling Me 💀",
        "Wait Until You See The Plot Twist 🔥",
        "Nobody Told Me This Secret Would Work 🚨",
        "This Is Your Sign To Stop Scrolling 🛑",
        "How Is This Even Possible? 🤨",
        "The Way This Hit Different Though 💯",
        "NOT Me Watching This 10 Times 👀",
        "This Just Broke The Internet 🌐"
      ],
      high_viral: [
        "You Need To See This Right Now 👁️",
        "This Actually Works Every Time ✅",
        "Why Nobody Talks About This 🤐",
        "Plot Twist: It Gets Better 📈",
        "The Secret They Don't Want You To Know 🔒",
        "This Hit Too Close To Home 🎯",
        "When You Finally Understand Life 💡",
        "The Glow Up Is Real ✨",
        "Main Character Energy Only 👑",
        "That's Enough Internet For Today 📱"
      ]
    },
    youtube: {
      mega_viral: [
        "I Tried This For 30 Days - The Results Will Shock You",
        "Scientists HATE This One Simple Trick",
        "The Truth They Don't Want You To Know",
        "Why Everyone Is Switching To This Method",
        "The Mistake 99% Of People Make",
        "How To Change Your Life In 24 Hours",
        "The Hidden Secret That Changes Everything",
        "Why This Is Going Viral Right Now",
        "The Most Important Video You'll Watch Today",
        "How I Went From Zero To Hero Using This"
      ],
      high_viral: [
        "The Ultimate Guide To Success",
        "What Experts Don't Tell You",
        "The Revolutionary Method That Works",
        "How To Master Anything Fast",
        "The Game-Changing Strategy Everyone Needs",
        "Why This Method Is Taking Over",
        "The Science Behind Viral Success",
        "How To Level Up Your Life",
        "The Secret Formula Revealed",
        "Why This Changes Everything"
      ]
    },
    instagram: {
      mega_viral: [
        "That Girl Energy ✨",
        "Soft Life Vibes Only 🌸",
        "Main Character Moment 👑",
        "Living My Best Life 💫",
        "Glow Up Season 🌟",
        "Self Care Sunday Mood 🧘‍♀️",
        "Aesthetic Lifestyle Goals 📸",
        "Mindset Shift In Progress 🧠",
        "Manifesting This Energy 🔮",
        "Hot Girl Walk Mode 🚶‍♀️"
      ],
      high_viral: [
        "Viral Moment Captured 📱",
        "This Aesthetic Though 📷",
        "Mood For The Week 💭",
        "Life Update Incoming ⭐",
        "New Chapter Loading 📖",
        "Growth Era Activated 🌱",
        "Confidence Level: Maximum 💪",
        "Living Rent Free In My Mind 🏠",
        "The Plot Twist We Needed 🔄",
        "Character Development Arc 📚"
      ]
    }
  };
  
  // Get templates for platform and style
  const templates = platformTemplates[platform]?.[style] || platformTemplates.tiktok.mega_viral;
  
  // Generate titles
  const titles = [];
  const selectedTemplates = templates.slice(0, numTitles);
  
  for (let i = 0; i < selectedTemplates.length; i++) {
    const template = selectedTemplates[i];
    const viralScore = 9.5 - (i * 0.2); // Decreasing scores
    const ctr = (0.15 - (i * 0.01)); // Decreasing CTR
    const engagement = (0.25 - (i * 0.02)); // Decreasing engagement
    
    // Determine hook type based on template
    let hookType = 'viral_template';
    if (template.includes('POV:') || template.includes('Tell Me')) hookType = 'social_media_trend';
    else if (template.includes('Secret') || template.includes('Truth')) hookType = 'curiosity_gap';
    else if (template.includes('Won\'t Believe') || template.includes('Shock')) hookType = 'disbelief_trigger';
    else if (template.includes('How') || template.includes('Why')) hookType = 'educational_hook';
    else if (template.includes('Changes Everything')) hookType = 'transformation_promise';
    
    titles.push({
      rank: i + 1,
      title: template,
      viral_score: Math.round(viralScore * 10) / 10,
      predicted_ctr: `${(ctr * 100).toFixed(1)}%`,
      predicted_engagement: `${(engagement * 100).toFixed(1)}%`,
      hook_type: hookType,
      platform_optimized: platform,
      style: style,
      length: template.length,
      word_count: template.split(' ').length,
      quality_scores: {
        viral_potential: Math.round((viralScore * 0.9) * 10) / 10,
        psychological_impact: Math.round((viralScore * 0.85) * 10) / 10,
        platform_optimization: Math.round((viralScore * 0.95) * 10) / 10,
        emotional_resonance: Math.round((viralScore * 0.8) * 10) / 10,
        curiosity_factor: Math.round((viralScore * 0.9) * 10) / 10,
        clarity: Math.round(8.5 * 10) / 10
      }
    });
  }
  
  // Generate optimization recommendations
  const optimizationRecommendations = [
    `Optimize for ${platform} algorithm by posting during peak hours`,
    `Use trending hashtags relevant to your ${contentHints} content`,
    `Add eye-catching thumbnails with high contrast colors`,
    `Include a strong call-to-action in the first 3 seconds`,
    `Test different posting times for maximum engagement`
  ].slice(0, 3);
  
  // Generate performance predictions
  const bestTitle = titles[0];
  const avgViralScore = titles.reduce((sum, t) => sum + t.viral_score, 0) / titles.length;
  const bestCtr = titles[0] ? parseFloat(titles[0].predicted_ctr) / 100 : 0.15;
  const bestEngagement = titles[0] ? parseFloat(titles[0].predicted_engagement) / 100 : 0.25;
  
  const performancePredictions = {
    viral_potential: avgViralScore > 8.5 ? 'high' : avgViralScore > 7.0 ? 'moderate' : 'standard',
    best_title_ctr: bestCtr,
    best_title_engagement: bestEngagement,
    average_score: avgViralScore,
    platform_match: platform === 'tiktok' ? 0.95 : platform === 'youtube' ? 0.90 : 0.85
  };
  
  // Generate content analysis
  const contentAnalysis = {
    content_length: clipFilename.length,
    segment_count: 1,
    key_topics: [contentHints, platform + ' content', style + ' style'],
    viral_potential: performancePredictions.viral_potential
  };
  
  return {
    titles,
    optimizationRecommendations,
    performancePredictions,
    contentAnalysis
  };
}

// Helper function to convert time format (MM:SS) to seconds
function timeToSeconds(timeStr) {
  const parts = timeStr.split(':');
  if (parts.length === 2) {
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
  } else if (parts.length === 3) {
    return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
  }
  return 0;
}

// Test rescaling endpoint for debugging
app.post('/test-rescale', async (req, res) => {
  const { testVideo } = req.body;
  if (!testVideo) {
    return res.status(400).json({ error: 'No test video provided' });
  }
  
  console.log('🧪 TESTING RESCALE MODE');
  const timestamp = Date.now();
  const testOutput = path.join(mediaDir, `test_rescale_${timestamp}.mp4`);
  
  // Test the exact rescaling command we use in production
  const testCmd = `ffmpeg -i '${testVideo}' -i '../logo-removebg-preview.png' -ss 0 -t 10 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[v];[1:v]scale=150:-1,format=rgba,colorchannelmixer=aa=0.4[logo];[v][logo]overlay=W-w-20:(H-h)/2:format=auto,format=yuv420p[out]" -map "[out]" -map 0:a -c:a copy '${testOutput}' -y`;
  
  console.log('🧪 TEST COMMAND:', testCmd);
  
  exec(testCmd, (err, stdout, stderr) => {
    if (err) {
      console.error('🚨 TEST RESCALE FAILED:', err);
      res.status(500).json({ error: 'Test rescale failed', details: stderr });
    } else {
      console.log('✅ TEST RESCALE SUCCESS');
      res.json({ message: 'Test rescale completed', output: path.basename(testOutput) });
    }
  });
});

// ================================
// 🚀 YOUTUBE SHORTS UPLOAD ENDPOINTS
// ================================

// Initialize YouTube upload manager
const youtubeManager = new YouTubeUploadManager();

// Get YouTube authentication URL
app.get('/auth/youtube/url', (req, res) => {
  try {
    const authUrl = youtubeManager.generateAuthUrl();
    res.json({ 
      success: true, 
      authUrl: authUrl,
      message: 'Use this URL to authenticate with YouTube'
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: 'Failed to generate auth URL: ' + error.message 
    });
  }
});

// Handle YouTube OAuth callback
app.get('/auth/youtube/callback', async (req, res) => {
  const { code } = req.query;
  
  if (!code) {
    // Redirect to error page instead of JSON
    return res.redirect('http://localhost:3000/youtube-auth-error?error=no_code');
  }

  try {
    const result = await youtubeManager.handleAuthCallback(code);
    
    if (result.success) {
      // 🎉 AUTOMATIC REDIRECT - Much better UX!
      console.log('✅ YouTube authentication successful - redirecting to success page');
      res.redirect('http://localhost:3000/youtube-auth-success');
    } else {
      // Redirect to error page with error details
      const errorMsg = encodeURIComponent(result.message || 'Authentication failed');
      res.redirect(`http://localhost:3000/youtube-auth-error?error=${errorMsg}`);
    }
  } catch (error) {
    console.error('YouTube authentication error:', error);
    const errorMsg = encodeURIComponent('Authentication failed: ' + error.message);
    res.redirect(`http://localhost:3000/youtube-auth-error?error=${errorMsg}`);
  }
});

const port = process.env.PORT || 5000;
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
