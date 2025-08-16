#!/bin/bash
# EasyChatbox Startup Script for Linux

echo "Starting EasyChatbox..."

# Start the backend server
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait a few seconds for backend to start
sleep 5

# Start the frontend server
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "EasyChatbox servers starting..."
echo "Backend should be available at http://localhost:8000"
echo "Frontend should be available at http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID
wait $FRONTEND_PID
