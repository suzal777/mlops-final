#!/bin/bash

# Script to run RAG system locally without Docker

echo "🚀 Starting RAG Microservice (Local Mode)..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Using Python $python_version"

# Start Qdrant in Docker
echo "🗄️  Starting Qdrant vector database..."
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

echo "⏳ Waiting for Qdrant to be ready..."
sleep 5

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Start backend in background
echo "🔧 Starting backend API..."
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
pip install -r requirements.txt

# Start frontend
echo "🎨 Starting frontend UI..."
echo "Frontend will open in your browser..."
streamlit run app.py

# Cleanup on exit
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID; docker stop qdrant; docker rm qdrant" EXIT
