# 🚀 Complete Railway Deployment Guide

## Prerequisites
- Railway account (free at [railway.app](https://railway.app))
- Your API keys ready

## Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

## Step 2: Login to Railway
```bash
railway login
```
This will open your browser to authenticate.

## Step 3: Deploy Backend

### 3.1 Navigate to server directory
```bash
cd server
```

### 3.2 Initialize Railway project
```bash
railway init --name trilion-backend
```

### 3.3 Deploy backend
```bash
railway up
```

### 3.4 Get backend URL
```bash
railway domain
```
Note this URL - you'll need it for the frontend.

### 3.5 Set backend environment variables
```bash
railway variables set OPENAI_API_KEY=your_openai_api_key_here
railway variables set ANTHROPIC_API_KEY=your_anthropic_api_key_here
railway variables set YOUTUBE_CLIENT_ID=your_youtube_client_id_here
railway variables set YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
railway variables set NODE_ENV=production
```

## Step 4: Deploy Frontend

### 4.1 Navigate to frontend directory
```bash
cd ../video-clipper
```

### 4.2 Initialize Railway project
```bash
railway init --name trilion-frontend
```

### 4.3 Deploy frontend
```bash
railway up
```

### 4.4 Get frontend URL
```bash
railway domain
```

### 4.5 Set frontend environment variables
```bash
railway variables set REACT_APP_API_URL=https://your-backend-url.railway.app
```

## Step 5: Update Backend CORS

### 5.1 Go back to backend directory
```bash
cd ../server
```

### 5.2 Set CORS origin to your frontend URL
```bash
railway variables set CORS_ORIGIN=https://your-frontend-url.railway.app
```

## Step 6: Test Your Deployment

### 6.1 Test backend
Visit your backend URL: `https://your-backend-url.railway.app/`
Should show: `{"message":"Server is running!","status":"active",...}`

### 6.2 Test frontend
Visit your frontend URL: `https://your-frontend-url.railway.app/`
Should load your React app

### 6.3 Test integration
Try generating clips from the frontend

## Troubleshooting

### If backend fails to deploy:
1. Check logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Check Python dependencies in logs

### If frontend fails to deploy:
1. Check logs: `railway logs`
2. Verify build process
3. Check environment variables

### If CORS errors:
1. Verify CORS_ORIGIN is set correctly
2. Check that frontend URL matches exactly

## Useful Commands

```bash
# View logs
railway logs

# View environment variables
railway variables

# Redeploy
railway up

# Open in browser
railway open

# Check status
railway status
```

## Expected URLs
- Backend: `https://trilion-backend-production-xxxx.up.railway.app`
- Frontend: `https://trilion-frontend-production-xxxx.up.railway.app`

## Success Indicators
✅ Backend responds with server status  
✅ Frontend loads without errors  
✅ Can generate clips from frontend  
✅ No CORS errors in browser console  

Your app is now live on Railway! 🎉 