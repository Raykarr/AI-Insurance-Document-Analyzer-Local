#!/bin/bash

# 🚀 AI Insurance Document Analyzer - Heroku Deployment Script
# This script automates the deployment process to Heroku

set -e  # Exit on any error

echo "🚀 Starting Heroku deployment..."

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

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI is not installed. Please install it first:"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    print_warning "You are not logged in to Heroku. Please login first:"
    heroku login
fi

# Get app name from user
read -p "Enter your Heroku app name (or press Enter to auto-generate): " APP_NAME

if [ -z "$APP_NAME" ]; then
    print_status "Creating Heroku app with auto-generated name..."
    APP_NAME=$(heroku create --json | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    print_success "Created app: $APP_NAME"
else
    print_status "Creating Heroku app: $APP_NAME"
    heroku create $APP_NAME
fi

# Set stack to heroku-22
print_status "Setting stack to heroku-22..."
heroku stack:set heroku-22 --app $APP_NAME

# Check if GROQ_API_KEY is provided
if [ -z "$GROQ_API_KEY" ]; then
    print_warning "GROQ_API_KEY environment variable not set."
    read -p "Enter your Groq API key: " GROQ_API_KEY
fi

# Set environment variables
print_status "Setting environment variables..."
heroku config:set GROQ_API_KEY="$GROQ_API_KEY" --app $APP_NAME
heroku config:set PYTHON_VERSION=3.11.7 --app $APP_NAME

# Add PostgreSQL if not already added
print_status "Checking for PostgreSQL addon..."
if ! heroku addons --app $APP_NAME | grep -q "postgresql"; then
    print_status "Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:mini --app $APP_NAME
else
    print_success "PostgreSQL already configured"
fi

# Deploy the backend
print_status "Deploying backend to Heroku..."
git subtree push --prefix backend heroku main

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 10

# Check if deployment was successful
print_status "Checking deployment status..."
if heroku ps --app $APP_NAME | grep -q "up"; then
    print_success "Backend deployed successfully!"
    
    # Get the app URL
    APP_URL=$(heroku info --app $APP_NAME | grep "Web URL" | awk '{print $3}')
    print_success "Your backend is available at: $APP_URL"
    
    # Test the health endpoint
    print_status "Testing health endpoint..."
    if curl -s "$APP_URL/health" | grep -q "healthy"; then
        print_success "Health check passed!"
    else
        print_warning "Health check failed. Check logs with: heroku logs --tail --app $APP_NAME"
    fi
    
else
    print_error "Deployment failed. Check logs with: heroku logs --tail --app $APP_NAME"
    exit 1
fi

# Frontend deployment instructions
echo ""
print_status "🎉 Backend deployment complete!"
echo ""
print_status "Next steps for frontend deployment:"
echo ""
echo "1. Deploy frontend to Vercel:"
echo "   - Go to https://vercel.com"
echo "   - Import your GitHub repository"
echo "   - Set build command: cd frontend && npm install && npm run build"
echo "   - Set output directory: frontend/dist"
echo "   - Add environment variable: VITE_API_BASE_URL=$APP_URL"
echo ""
echo "2. Or deploy to Netlify:"
echo "   - Go to https://netlify.com"
echo "   - Import your GitHub repository"
echo "   - Set build command: cd frontend && npm install && npm run build"
echo "   - Set publish directory: frontend/dist"
echo "   - Add environment variable: VITE_API_BASE_URL=$APP_URL"
echo ""
echo "3. Monitor your app:"
echo "   - View logs: heroku logs --tail --app $APP_NAME"
echo "   - Check status: heroku ps --app $APP_NAME"
echo "   - Open app: heroku open --app $APP_NAME"
echo ""

print_success "Deployment script completed! 🚀" 