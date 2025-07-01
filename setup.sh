#!/bin/bash

echo "Setting up South Park Animator..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p models temp output

# Download Rhubarb (optional - will work without it)
echo "Note: To enable better lip sync, download Rhubarb from:"
echo "https://github.com/DanielSWolf/rhubarb-lip-sync/releases"
echo "Place the 'rhubarb' executable in the 'models' directory"

echo ""
echo "Setup complete! To run the app:"
echo "1. Start the backend: cd backend && python app.py"
echo "2. Open frontend/index.html in your browser"
echo ""
echo "Make sure you have ffmpeg installed: brew install ffmpeg"