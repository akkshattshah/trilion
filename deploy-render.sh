#!/bin/bash

# Trilion App Deployment Script for Render
echo "🚀 Starting Trilion App Deployment to Render..."

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

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this script from the project root."
    exit 1
fi

print_status "Checking current git status..."
git status

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "There are uncommitted changes. Committing them..."
    git add .
    git commit -m "Auto-commit before deployment: $(date)"
fi

print_status "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    print_success "Code pushed to GitHub successfully!"
else
    print_error "Failed to push to GitHub. Please check your git configuration."
    exit 1
fi

print_status "Deployment Steps:"
echo ""
print_status "1. Go to https://render.com/dashboard"
print_status "2. Click 'New +' and select 'Blueprint'"
print_status "3. Connect your GitHub repository: https://github.com/akkshattshah/trilion.git"
print_status "4. Render will detect the render.yaml file automatically"
print_status "5. Set the following environment variables in Render:"
echo ""
echo "   Backend Service (trilion-backend):"
echo "   - OPENAI_API_KEY=your_openai_api_key_here"
echo "   - ANTHROPIC_API_KEY=your_anthropic_api_key_here"
echo "   - YOUTUBE_CLIENT_ID=your_youtube_client_id_here"
echo "   - YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here"
echo "   - NODE_ENV=production"
echo "   - PORT=10000"
echo "   - CORS_ORIGIN=https://trilion-frontend.onrender.com"
echo ""
echo "   Frontend Service (trilion-frontend):"
echo "   - REACT_APP_API_URL=https://trilion-backend.onrender.com"
echo ""
print_status "6. Click 'Apply' to start the deployment"
print_status "7. Monitor the build logs for any issues"
echo ""
print_success "Deployment script completed! Follow the steps above to deploy on Render."
print_status "Your app will be available at:"
print_status "- Frontend: https://trilion-frontend.onrender.com"
print_status "- Backend: https://trilion-backend.onrender.com" 