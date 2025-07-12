const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const OpenAI = require('openai');

// YouTube API configuration - Use environment variables
const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
const CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const REDIRECT_URI = process.env.YOUTUBE_REDIRECT_URI || 'https://trilion-backend.onrender.com/auth/youtube/callback';

// Validate YouTube API configuration
if (!CLIENT_ID || !CLIENT_SECRET) {
  console.warn('⚠️  YouTube API credentials not configured. YouTube upload features will be disabled.');
  console.warn('   Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables to enable.');
}

// OAuth2 client
const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  REDIRECT_URI
);

// YouTube API client
const youtube = google.youtube({
  version: 'v3',
  auth: oauth2Client
});

// Store tokens (in production, use a database)
const userTokens = new Map();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

class YouTubeUploadManager {
  constructor() {
    this.mediaDir = path.join(__dirname, 'media');
  }

  // Generate OAuth URL for user authentication
  generateAuthUrl() {
    const scopes = [
      'https://www.googleapis.com/auth/youtube.upload',
      'https://www.googleapis.com/auth/youtube'
    ];

    return oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes,
      prompt: 'consent'
    });
  }

  // Handle OAuth callback and get tokens
  async handleAuthCallback(code) {
    try {
      const { tokens } = await oauth2Client.getToken(code);
      oauth2Client.setCredentials(tokens);
      
      // Store tokens (in production, save to database)
      const userId = 'default_user'; // You can implement user management
      userTokens.set(userId, tokens);
      
      return {
        success: true,
        message: 'YouTube authentication successful!',
        tokens: tokens
      };
    } catch (error) {
      console.error('OAuth callback error:', error);
      return {
        success: false,
        message: 'Authentication failed: ' + error.message
      };
    }
  }

  // Upload video to YouTube Shorts
  async uploadShorts(videoPath, title, description = '', tags = [], originalVideoUrl = '') {
    try {
      console.log(`🎬 Starting YouTube Shorts upload: ${path.basename(videoPath)}`);
      
      // Set credentials for the upload
      const userId = 'default_user';
      const tokens = userTokens.get(userId);
      if (!tokens) {
        throw new Error('User not authenticated. Please authenticate with YouTube first.');
      }
      oauth2Client.setCredentials(tokens);

      // --- Extract SRT and Generate AI Title ---
      let aiTitle = title;
      try {
        // Assume SRT file has same base name as video but .srt extension
        const srtPath = videoPath.replace(/\.mp4$/, '.srt');
        let srtText = '';
        if (fs.existsSync(srtPath)) {
          const srtContent = fs.readFileSync(srtPath, 'utf-8');
          // Remove SRT numbers and timestamps, keep only text
          srtText = srtContent.replace(/\d+\n/g, '').replace(/\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n/g, '').replace(/\n+/g, ' ').trim();
        }
        if (srtText.length > 0) {
          const prompt = `You are a viral video expert. Read the following transcript and generate a catchy, viral YouTube Shorts title (max 60 characters, use emojis if appropriate, make it irresistible to click):\n\nTranscript: ${srtText}`;
          const aiResult = await openai.chat.completions.create({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 32,
          });
          if (aiResult.choices && aiResult.choices[0] && aiResult.choices[0].message) {
            aiTitle = aiResult.choices[0].message.content.trim().replace(/\n/g, ' ');
            // Truncate if too long
            if (aiTitle.length > 60) aiTitle = aiTitle.slice(0, 57) + '...';
          }
        }
      } catch (err) {
        console.error('AI title generation failed:', err.message);
      }
      if (!aiTitle) aiTitle = title;

      // --- AI-Generated Hashtags ---
      let aiHashtags = [];
      try {
        const prompt = `Generate 5 catchy, viral hashtags for a YouTube Short with the following title and description. Only return the hashtags, separated by spaces.\n\nTitle: ${aiTitle}\nDescription: ${description}`;
        const aiResult = await openai.chat.completions.create({
          model: 'gpt-3.5-turbo',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 32,
        });
        if (aiResult.choices && aiResult.choices[0] && aiResult.choices[0].message) {
          aiHashtags = aiResult.choices[0].message.content.match(/#[\w]+/g) || [];
        }
      } catch (err) {
        console.error('AI hashtag generation failed:', err.message);
      }
      if (aiHashtags.length === 0) {
        aiHashtags = ['#viral', '#shorts', '#trending'];
      }
      // Merge AI hashtags with provided tags (deduped)
      const allTags = Array.from(new Set([...(tags || []), ...aiHashtags.map(h => h.replace('#',''))]));

      // --- Build Description ---
      let finalDescription = description;
      // Add hashtags at the end
      finalDescription += '\n\n' + aiHashtags.join(' ');
      // Add credit if original video link is provided
      if (originalVideoUrl) {
        finalDescription += `\n\nCredit: ${originalVideoUrl}`;
      }

      // Prepare video metadata
      const videoMetadata = {
        snippet: {
          title: aiTitle,
          description: finalDescription,
          tags: allTags,
          categoryId: '22', // People & Blogs category
          defaultLanguage: 'en',
          defaultAudioLanguage: 'en'
        },
        status: {
          privacyStatus: 'public', // Force public
          selfDeclaredMadeForKids: false
        }
      };

      // Create upload parameters
      const uploadParams = {
        part: ['snippet', 'status'],
        requestBody: videoMetadata,
        media: {
          body: fs.createReadStream(videoPath)
        }
      };

      console.log('📤 Uploading to YouTube...');
      const response = await youtube.videos.insert(uploadParams);

      const videoId = response.data.id;
      const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
      const shortsUrl = `https://youtube.com/shorts/${videoId}`;

      // --- Failsafe: Explicitly set to public after upload ---
      try {
        await youtube.videos.update({
          part: ['status'],
          requestBody: {
            id: videoId,
            status: {
              privacyStatus: 'public',
              selfDeclaredMadeForKids: false
            }
          }
        });
        console.log('✅ Explicitly set video to public after upload');
      } catch (err) {
        console.error('Failsafe public update failed:', err.message);
      }

      console.log('✅ YouTube Shorts upload successful!');
      console.log(`📺 Video ID: ${videoId}`);
      console.log(`🔗 Regular URL: ${videoUrl}`);
      console.log(`📱 Shorts URL: ${shortsUrl}`);

      return {
        success: true,
        videoId: videoId,
        videoUrl: videoUrl,
        shortsUrl: shortsUrl,
        title: aiTitle,
        privacyStatus: 'public'
      };

    } catch (error) {
      console.error('❌ YouTube upload failed:', error);
      return {
        success: false,
        error: error.message,
        details: error.response?.data || null
      };
    }
  }

  // Upload multiple clips as batch
  async uploadBatchShorts(clips, titles, descriptions = [], tags = []) {
    const results = [];
    
    for (let i = 0; i < clips.length; i++) {
      console.log(`\n📦 Processing clip ${i + 1}/${clips.length}`);
      
      const clipPath = path.join(this.mediaDir, clips[i]);
      const title = titles[i] || `Viral Clip ${i + 1}`;
      const description = descriptions[i] || '';
      const clipTags = tags[i] || tags;
      
      const result = await this.uploadShorts(clipPath, title, description, clipTags);
      results.push({
        clip: clips[i],
        ...result
      });
      
      // Add delay between uploads to avoid rate limiting
      if (i < clips.length - 1) {
        console.log('⏳ Waiting 2 seconds before next upload...');
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    return results;
  }

  // Make video public (after review)
  async makePublic(videoId) {
    try {
      const response = await youtube.videos.update({
        part: ['status'],
        requestBody: {
          id: videoId,
          status: {
            privacyStatus: 'public'
          }
        }
      });

      return {
        success: true,
        message: 'Video is now public!',
        videoId: videoId
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get upload status
  async getUploadStatus(videoId) {
    try {
      const response = await youtube.videos.list({
        part: ['snippet', 'status', 'statistics'],
        id: [videoId]
      });

      if (response.data.items.length === 0) {
        return { success: false, error: 'Video not found' };
      }

      const video = response.data.items[0];
      return {
        success: true,
        videoId: videoId,
        title: video.snippet.title,
        privacyStatus: video.status.privacyStatus,
        viewCount: video.statistics?.viewCount || 0,
        likeCount: video.statistics?.likeCount || 0,
        uploadDate: video.snippet.publishedAt
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Generate viral title using AI (placeholder)
  generateViralTitle(originalTitle, hookType = 'viral') {
    const viralPrefixes = {
      viral: ['🚀', '💥', '🔥', '⚡', '🎯'],
      shocking: ['😱', '💀', '🚨', '⚠️', '😤'],
      money: ['💰', '💎', '🏆', '💸', '🤑'],
      fitness: ['💪', '🏃‍♂️', '🔥', '⚡', '🎯']
    };

    const prefixes = viralPrefixes[hookType] || viralPrefixes.viral;
    const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    
    // Convert to uppercase for viral effect
    const viralTitle = originalTitle.toUpperCase();
    
    return `${randomPrefix} ${viralTitle}`;
  }

  // Check if user is authenticated
  isAuthenticated() {
    const userId = 'default_user';
    return userTokens.has(userId);
  }

  // Get authentication status
  getAuthStatus() {
    const userId = 'default_user';
    const tokens = userTokens.get(userId);
    
    return {
      authenticated: !!tokens,
      hasRefreshToken: !!tokens?.refresh_token,
      expiresAt: tokens?.expiry_date || null
    };
  }
}

module.exports = YouTubeUploadManager; 