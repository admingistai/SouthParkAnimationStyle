#!/bin/bash

echo "Starting South Park Animator..."

# Start backend in background
echo "Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend server..."
cd ../
python start_frontend.py &
FRONTEND_PID=$!

echo ""
echo "==================================="
echo "App is running!"
echo "Frontend: http://localhost:5500"
echo "Backend: http://localhost:5000"
echo "==================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait