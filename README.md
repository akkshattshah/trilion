# Trilion - AI-Powered Viral Video Generator

A full-stack application that automatically analyzes YouTube videos, identifies viral moments, and creates engaging clips optimized for social media platforms like TikTok, Instagram Reels, and YouTube Shorts.

## 🚀 Features

- **AI-Powered Analysis**: Uses OpenAI Whisper for transcription and Claude/GPT for viral content detection
- **Automatic Clip Generation**: Creates optimized clips with viral hooks and emotional triggers
- **YouTube Integration**: Direct upload to YouTube Shorts with AI-generated titles and hashtags
- **Cross-Platform Optimization**: Generates content suitable for TikTok, Instagram, and YouTube
- **Real-time Processing**: Fast video analysis and clip generation
- **Modern UI**: Beautiful, responsive React frontend

## 🛠️ Tech Stack

### Backend
- **Node.js** with Express.js
- **OpenAI API** for transcription and content analysis
- **Anthropic Claude** for viral content detection
- **YouTube Data API** for video uploads
- **FFmpeg** for video processing
- **yt-dlp** for YouTube video downloading

### Frontend
- **React** with TypeScript
- **Modern CSS** with responsive design
- **Real-time updates** and progress tracking

## 📋 Prerequisites

- Node.js 16+ 
- FFmpeg installed on the system
- yt-dlp installed on the system
- API keys for:
  - OpenAI
  - Anthropic
  - YouTube Data API

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/akkshattshah/triliongame.git
   cd triliongame
   ```

2. **Install dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install server dependencies
   cd server && npm install
   
   # Install frontend dependencies
   cd ../frontend && npm install
   ```

3. **Set up environment variables**
   Create a `.env` file in the server directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   YOUTUBE_CLIENT_ID=your_youtube_client_id
   YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
   NODE_ENV=development
   PORT=5000
   CORS_ORIGIN=http://localhost:3000
   ```

4. **Start the development servers**
   ```bash
   # Terminal 1: Start backend
   cd server && npm start
   
   # Terminal 2: Start frontend
   cd frontend && npm start
   ```

5. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5000

## 🌐 Deployment

### Render Blueprint Deployment

This app is configured for easy deployment on Render using Blueprint.

1. **Fork or clone this repository**
2. **Go to [Render Dashboard](https://render.com/dashboard)**
3. **Click "New +" → "Blueprint"**
4. **Connect your GitHub repository**
5. **Set environment variables:**

   **Backend Service:**
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `NODE_ENV=production`
   - `PORT=10000`
   - `CORS_ORIGIN=https://trilion-frontend.onrender.com`

   **Frontend Service:**
   - `REACT_APP_API_URL=https://trilion-backend.onrender.com`

6. **Click "Apply" to deploy**

### Manual Deployment

1. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy backend to your preferred platform**
   - Set environment variables
   - Run `npm start` in the server directory

3. **Deploy frontend to a static hosting service**
   - Upload the `frontend/build` directory

## 📖 API Endpoints

### Core Endpoints
- `GET /` - Server status and health check
- `GET /health` - Health check endpoint
- `GET /test` - Test endpoint with API key status

### Video Analysis
- `POST /analyze` - Basic video analysis
- `POST /analyze` - Advanced viral content analysis
- `GET /clips-list` - List all generated clips

### YouTube Integration
- `GET /auth/youtube/url` - Get YouTube OAuth URL
- `GET /auth/youtube/callback` - Handle OAuth callback
- `GET /auth/youtube/status` - Check authentication status
- `POST /upload/youtube-shorts` - Upload single clip
- `POST /upload/youtube-batch` - Upload multiple clips
- `POST /upload/youtube/make-public` - Make video public
- `GET /upload/youtube/status/:videoId` - Get upload status

### Title Generation
- `POST /generate-titles` - Generate viral titles for YouTube videos
- `POST /generate-titles-for-clip` - Generate titles for existing clips

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for transcription and analysis | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key for content analysis | Yes |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | No (for uploads) |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth client secret | No (for uploads) |
| `NODE_ENV` | Environment (development/production) | Yes |
| `PORT` | Server port | Yes |
| `CORS_ORIGIN` | Allowed CORS origin | Yes |

### Video Processing Settings

The app supports various video processing modes:
- **Auto**: Automatic detection and optimization
- **Crop**: Crop videos to focus on speakers
- **Resize**: Resize videos for different platforms

## 🎯 Usage

1. **Enter a YouTube URL** in the input field
2. **Configure settings**:
   - Number of clips to generate
   - Clip duration
   - Caption style
   - Processing mode
3. **Click "Generate Viral Clips"**
4. **Review generated clips** with viral scores and analysis
5. **Download clips** or upload directly to YouTube Shorts

## 🔒 Security

- All API keys are stored as environment variables
- No hardcoded secrets in the codebase
- CORS properly configured for production
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the deployment logs for errors
- Verify all environment variables are set correctly

## 🔄 Updates

The app automatically:
- Updates dependencies
- Implements security patches
- Adds new features for viral content detection
- Optimizes for different social media platforms

---

**Built with ❤️ for content creators who want to go viral!**
