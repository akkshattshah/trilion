# Trilion - Viral Video Generator

Transform YouTube videos into viral social media clips using AI analysis.

## 🚀 Quick Deploy to Google Cloud

### Prerequisites
1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. [Node.js 18+](https://nodejs.org/)
3. Google Cloud Project with billing enabled

### One-Click Deployment

```bash
# Clone and setup
git clone <your-repo>
cd trilion-app

# Deploy to Google Cloud (replace with your project ID)
./deploy.sh YOUR_PROJECT_ID us-central1
```

### Manual Deployment

1. **Setup Google Cloud Project**
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable youtube.googleapis.com
```

2. **Build Frontend**
```bash
cd frontend
npm install
npm run build
cd ..
```

3. **Deploy Backend**
```bash
gcloud app deploy app.yaml
```

4. **Deploy Frontend**
```bash
gcloud app deploy frontend-app.yaml
```

## 🔧 Environment Variables

Create a `.env` file in the `server/` directory:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
NODE_ENV=production
PORT=8080
```

## 📁 Project Structure

```
trilion-app/
├── frontend/                 # React frontend
├── server/                   # Node.js backend
├── app.yaml                  # Backend App Engine config
├── frontend-app.yaml         # Frontend App Engine config
├── cloudbuild.yaml           # CI/CD configuration
├── deploy.sh                 # Deployment script
└── README.md                 # This file
```

## 🎯 Features

- **AI-Powered Analysis**: Uses OpenAI Whisper and Claude for content analysis
- **Viral Clip Generation**: Automatically identifies viral moments
- **Multi-Platform Support**: Optimized for TikTok, Instagram, YouTube
- **YouTube Integration**: Direct upload to YouTube
- **Real-time Processing**: Fast video processing and clip creation

## 🔗 API Endpoints

- `POST /analyze` - Analyze YouTube video and generate clips
- `GET /clips-list` - List all generated clips
- `GET /clips/:filename` - Stream video clip
- `GET /download/:filename` - Download video clip
- `POST /upload-to-youtube` - Upload clip to YouTube
- `GET /health` - Health check

## 🛠️ Development

```bash
# Install dependencies
npm run install:all

# Start backend (development)
cd server && npm run dev

# Start frontend (development)
cd frontend && npm start
```

## 📊 Monitoring

- **App Engine Console**: https://console.cloud.google.com/appengine
- **Cloud Build**: https://console.cloud.google.com/cloud-build
- **Logs**: `gcloud app logs tail -s trilion-backend`

## 🔒 Security

- Content Security Policy (CSP) headers configured
- CORS properly configured for production
- Environment variables for sensitive data
- HTTPS enforced on App Engine

## 🚀 Scaling

- Automatic scaling configured
- Backend: 1-10 instances
- Frontend: 1-5 instances
- CPU and memory optimized

## 📈 Performance

- Video processing optimized with ffmpeg
- Caching for repeated requests
- Efficient file handling
- CDN-ready static assets

## 🐛 Troubleshooting

### Common Issues

1. **YouTube Download Fails**
   - Check if video is public
   - Verify YouTube API quota
   - Try different video URL

2. **AI Analysis Fails**
   - Verify API keys are set
   - Check API quotas
   - Ensure video has audio

3. **Deployment Fails**
   - Verify Google Cloud SDK is installed
   - Check project permissions
   - Ensure billing is enabled

### Logs

```bash
# View backend logs
gcloud app logs tail -s trilion-backend

# View frontend logs
gcloud app logs tail -s trilion-frontend
```

## 📄 License

ISC License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Made with ❤️ for viral content creators** 