#!/bin/bash

# Deployment script for RAG Microservice

echo "🚀 Starting RAG Microservice Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data

# Copy environment variables if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
fi

# Pull latest images
echo "🐳 Pulling Docker images..."
docker-compose pull

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Pull Ollama model
echo "🦙 Pulling Ollama model (qwen2.5:0.5b)..."
docker-compose exec -T ollama ollama pull qwen2.5:0.5b

# Wait a bit more for everything to settle
sleep 5

# Check service health
echo "🏥 Checking service health..."

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not responding"
fi

# Check Qdrant
if curl -s http://localhost:6333/health > /dev/null; then
    echo "✅ Qdrant is running"
else
    echo "❌ Qdrant is not responding"
fi

# Check Backend
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not responding"
fi

# Check Frontend
if curl -s http://localhost:8501/ > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📍 Access points:"
echo "   Frontend UI: http://localhost:8501"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Qdrant Dashboard: http://localhost:6333/dashboard"
echo "   Ollama API: http://localhost:11434"
echo ""
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
