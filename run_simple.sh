#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "🎬 South Park Animator Launcher"
echo "==============================="
echo ""

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Please install Python 3: https://www.python.org/downloads/"
    exit 1
fi

# Check pip packages
echo -n "Checking required packages... "
MISSING_PACKAGES=""

# Check each package with correct import names
if ! python3 -c "import flask" &> /dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES flask"
fi
if ! python3 -c "import flask_cors" &> /dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES flask-cors"
fi
if ! python3 -c "import cv2" &> /dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES opencv-python"
fi
if ! python3 -c "import numpy" &> /dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES numpy"
fi
if ! python3 -c "import PIL" &> /dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES Pillow"
fi
if ! python3 -c "import pydub" &> /dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES pydub"
fi

if [ -z "$MISSING_PACKAGES" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "Missing packages:$MISSING_PACKAGES"
    echo ""
    echo "Installing missing packages..."
    pip install$MISSING_PACKAGES
fi

# Check ffmpeg
echo -n "Checking ffmpeg (for MP3 support)... "
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
    echo ""
    echo "ffmpeg not found. MP3 files may not work properly."
    echo "To install ffmpeg:"
    echo "  macOS:  brew install ffmpeg"
    echo "  Ubuntu: sudo apt-get install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    echo "Press Enter to continue anyway..."
    read
fi

# Kill any process using port 5000
echo -n "Checking port 5000... "
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}in use${NC}"
    echo "Killing existing process on port 5000..."
    kill $(lsof -Pi :5000 -sTCP:LISTEN -t)
    sleep 1
else
    echo -e "${GREEN}✓${NC}"
fi

# Start the app
echo ""
echo "Starting South Park Animator..."
echo "==============================="
echo ""

cd backend
python3 app_simple.py