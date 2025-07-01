#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "🎬 South Park Animator - Quick Start"
echo "====================================="
echo ""

# Kill any process using port 5000
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing existing process on port 5000..."
    kill $(lsof -Pi :5000 -sTCP:LISTEN -t) 2>/dev/null
    sleep 2
fi

# Check if ffmpeg is available
echo -n "Checking ffmpeg... "
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "Warning: ffmpeg not found. MP3 files may not work."
    echo "Install with: brew install ffmpeg"
fi

echo ""
echo "Starting South Park Animator..."
echo "==============================="
echo ""

# Start the app
cd backend

# Try to run the app and catch any import errors
if python3 -c "import flask, flask_cors, cv2, numpy, PIL, pydub" 2>/dev/null; then
    echo "All packages found! Starting server..."
    python3 app_simple.py
else
    echo -e "${RED}Missing required packages!${NC}"
    echo ""
    echo "Please install the required packages:"
    echo "pip install flask flask-cors opencv-python numpy Pillow pydub"
    echo ""
    echo "Or try running the full setup script: ./run_simple.sh"
    exit 1
fi