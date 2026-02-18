#!/bin/bash

# Script to setup Ollama with the required model

echo "🦙 Setting up Ollama for RAG Microservice..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo "📥 Install Ollama with: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama service is not running"
    echo "🚀 Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

echo "✅ Ollama service is running"

# Pull the required model
echo "📥 Pulling Qwen model: qwen2.5:0.5b"
ollama pull qwen2.5:0.5b

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "📍 Ollama is running at: http://localhost:11434"
echo "🤖 Model loaded: qwen2.5:0.5b"
echo ""
echo "Test your model with: ollama run qwen2.5:0.5b"
