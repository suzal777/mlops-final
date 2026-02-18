#!/bin/bash

# EC2 Setup Script for RAG Microservice

echo "🔧 Setting up EC2 instance for RAG Microservice..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔨 Installing Docker Compose..."
sudo apt install docker-compose -y

# Install other dependencies
echo "📚 Installing additional dependencies..."
sudo apt install -y git curl nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 6333
sudo ufw allow 8000
sudo ufw allow 8501

# Create application directory
echo "📁 Creating application directory..."
mkdir -p ~/mlops_final
cd ~/mlops_final

echo ""
echo "✅ EC2 setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone <your-repo-url>"
echo "2. Navigate to project: cd mlops_final"
echo "3. Run deployment: ./deploy.sh"
echo ""
echo "⚠️  Remember to log out and back in for Docker group changes to take effect!"
