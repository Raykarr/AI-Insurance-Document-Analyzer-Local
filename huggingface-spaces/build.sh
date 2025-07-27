#!/bin/bash

# 🚀 Hugging Face Spaces Build Script
# This script builds the frontend and prepares for deployment

set -e

echo "🚀 Building for Hugging Face Spaces..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
print_status "Building frontend..."
cd frontend

# Install dependencies
print_status "Installing frontend dependencies..."
npm install

# Build the frontend
print_status "Building frontend for production..."
npm run build

print_success "Frontend built successfully!"

# Copy the built frontend to the huggingface-spaces directory
print_status "Copying built frontend..."
cd ..
cp -r frontend/dist/* huggingface-spaces/frontend/dist/

print_success "Build completed successfully!"
echo ""
echo "🎉 Your app is ready for Hugging Face Spaces deployment!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Create a new Space on Hugging Face"
echo "3. Connect your GitHub repository"
echo "4. Set the GROQ_API_KEY environment variable"
echo "5. Deploy!" 