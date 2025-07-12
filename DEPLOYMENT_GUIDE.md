# Trilion App Deployment Guide - Render Blueprint

## Overview
This guide will help you deploy the Trilion app to Render using their Blueprint feature. The app consists of a Node.js backend and a React frontend.

## Prerequisites
- GitHub repository: https://github.com/akkshattshah/trilion.git
- Render account
- Environment variables ready

## Environment Variables Required

### Backend Environment Variables (to be set in Render dashboard)
```
NODE_ENV=production
PORT=10000
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY
YOUTUBE_CLIENT_ID=YOUR_YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET=YOUR_YOUTUBE_CLIENT_SECRET
CORS_ORIGIN=https://trilion-frontend.onrender.com
```

### Frontend Environment Variables (automatically set by render.yaml)
```
REACT_APP_API_URL=https://trilion-backend.onrender.com
```

## Deployment Steps

### 1. Connect Repository to Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub account if not already connected
4. Select the repository: `akkshattshah/trilion`
5. Render will automatically detect the `render.yaml` file

### 2. Configure Environment Variables
1. In the Render dashboard, go to your backend service
2. Navigate to "Environment" tab
3. Add all the backend environment variables listed above
4. Make sure to mark sensitive variables as "Secret"

### 3. Deploy
1. Click "Create Blueprint Instance"
2. Render will automatically:
   - Build the backend service
   - Build the frontend service
   - Set up the necessary networking
   - Deploy both services

### 4. Verify Deployment
1. Check that both services are running (green status)
2. Test the backend: `https://trilion-backend.onrender.com/`
3. Test the frontend: `https://trilion-frontend.onrender.com/`

## Local Development

### Backend
```bash
cd server
npm install
node index.js
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## File Structure
```
/
├── render.yaml          # Render Blueprint configuration
├── server/              # Backend Node.js application
│   ├── index.js         # Main server file
│   ├── package.json     # Backend dependencies
│   └── media/           # Temporary file storage
└── frontend/            # React frontend application
    ├── package.json     # Frontend dependencies
    ├── src/             # React source code
    └── public/          # Static assets
```

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure CORS_ORIGIN is set correctly
2. **API Key Errors**: Verify all environment variables are set
3. **Build Failures**: Check Node.js version compatibility
4. **Port Issues**: Ensure PORT is set to 10000

### Logs
- Check Render logs in the dashboard for each service
- Backend logs will show API requests and processing
- Frontend logs will show build status

## Security Notes
- All API keys are stored as environment variables
- CORS is configured for production domains only
- No sensitive data is committed to the repository

## Support
If you encounter issues:
1. Check Render service logs
2. Verify environment variables are set correctly
3. Ensure all dependencies are properly installed
4. Test locally before deploying 