#!/bin/bash

echo "🚀 Railway Deployment Script for Trilion Video Clipper"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_error "Railway CLI is not installed. Installing now..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    print_warning "You need to login to Railway first."
    print_status "Please run: railway login"
    print_status "Then run this script again."
    exit 1
fi

print_success "Railway CLI is ready!"

# Deploy Backend
echo ""
print_status "Deploying Backend..."
cd server

if [ ! -f ".railway" ]; then
    print_status "Initializing Railway project for backend..."
    railway init --name trilion-backend
fi

print_status "Deploying backend to Railway..."
railway up

BACKEND_URL=$(railway domain)
print_success "Backend deployed at: $BACKEND_URL"

# Set backend environment variables
print_status "Setting backend environment variables..."
echo ""
print_warning "You need to set these environment variables manually:"
echo ""
echo "railway variables set OPENAI_API_KEY=your_openai_api_key_here"
echo "railway variables set ANTHROPIC_API_KEY=your_anthropic_api_key_here"
echo "railway variables set YOUTUBE_CLIENT_ID=your_youtube_client_id_here"
echo "railway variables set YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here"
echo "railway variables set NODE_ENV=production"
echo "railway variables set CORS_ORIGIN=https://your-frontend-url.railway.app"
echo ""

# Deploy Frontend
echo ""
print_status "Deploying Frontend..."
cd ../video-clipper

if [ ! -f ".railway" ]; then
    print_status "Initializing Railway project for frontend..."
    railway init --name trilion-frontend
fi

print_status "Deploying frontend to Railway..."
railway up

FRONTEND_URL=$(railway domain)
print_success "Frontend deployed at: $FRONTEND_URL"

# Set frontend environment variables
print_status "Setting frontend environment variables..."
railway variables set REACT_APP_API_URL=$BACKEND_URL

print_success "Frontend environment variables set!"

# Final summary
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
print_success "Backend URL: $BACKEND_URL"
print_success "Frontend URL: $FRONTEND_URL"
echo ""
print_warning "Don't forget to set your API keys in the backend:"
echo "railway variables set OPENAI_API_KEY=your_key_here"
echo "railway variables set ANTHROPIC_API_KEY=your_key_here"
echo "railway variables set YOUTUBE_CLIENT_ID=your_client_id"
echo "railway variables set YOUTUBE_CLIENT_SECRET=your_client_secret"
echo ""
print_success "Your app should now be live! 🚀" 