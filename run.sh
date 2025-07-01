#!/bin/bash

echo "Starting South Park Animator..."
echo ""

# Check if port 5500 is already in use
if lsof -Pi :5500 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ Frontend server already running on port 5500 (probably VS Code)"
    echo "  Open: http://localhost:5500/frontend/index.html"
else
    echo "❌ No frontend server detected on port 5500"
    echo "  Please start VS Code Live Server or run a local server"
fi

echo ""
echo "Starting backend server on port 5000..."
cd backend
python app.py