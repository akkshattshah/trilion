#!/bin/bash

# Google Cloud Deployment Script for Trilion
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}

echo "🚀 Deploying Trilion to Google Cloud..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
    exit 1
fi

# Set project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable youtube.googleapis.com

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Update frontend app.yaml with correct backend URL
echo "📝 Updating frontend configuration..."
sed -i.bak "s/YOUR_PROJECT_ID/$PROJECT_ID/g" frontend-app.yaml
sed -i.bak "s/REGION/$REGION/g" frontend-app.yaml

# Deploy backend
echo "🚀 Deploying backend to App Engine..."
gcloud app deploy app.yaml --quiet

# Deploy frontend
echo "🚀 Deploying frontend to App Engine..."
gcloud app deploy frontend-app.yaml --quiet

# Get URLs
echo "✅ Deployment complete!"
echo ""
echo "🌐 Backend URL: https://trilion-backend-dot-$PROJECT_ID.$REGION.r.appspot.com"
echo "🌐 Frontend URL: https://trilion-frontend-dot-$PROJECT_ID.$REGION.r.appspot.com"
echo ""
echo "📊 View in Console: https://console.cloud.google.com/appengine?project=$PROJECT_ID" 