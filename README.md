# RAG Microservice - Automated Deployment

A production-grade Retrieval-Augmented Generation (RAG) system with automated CI/CD deployment.

## 🏗️ Architecture

- **LLM**: Qwen-0.5B-Instruct
- **Embedding Model**: BAAI/bge-small-en-v1.5
- **Vector Database**: Qdrant (self-hosted)
- **Backend**: FastAPI with Langchain
- **Frontend**: Streamlit
- **CI/CD**: GitHub Actions

## 📋 Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- Git

## 🚀 Quick Start

### Local Development

1. **Start Qdrant Vector Database**
```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

2. **Setup Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Setup Frontend**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Docker Deployment

```bash
docker-compose up -d
```

This will start:
- Qdrant on port 6333
- Backend API on port 8000
- Frontend UI on port 8501

## 📁 Project Structure

```
mlops_final/
├── backend/               # FastAPI backend
│   ├── main.py           # Main API endpoints
│   ├── models.py         # LLM and Embedding models
│   ├── qdrant_manager.py # Vector DB operations
│   ├── document_processor.py # Text extraction and chunking
│   ├── config.py         # Configuration
│   ├── logger_config.py  # Logging setup
│   └── requirements.txt
├── frontend/             # Streamlit UI
│   ├── app.py
│   └── requirements.txt
├── data/                 # Documents to index
├── logs/                 # Application logs
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml
```

## 🔌 API Endpoints

### Health Check
```bash
GET /
```

### Index Document
```bash
POST /index
Content-Type: multipart/form-data
Body: file (PDF or TXT)
```

### Chat
```bash
POST /chat
Content-Type: application/json
Body: {
  "query": "Your question here",
  "max_length": 512
}
```

## 📊 Usage Examples

### Using cURL

**Index a document:**
```bash
curl -X POST "http://localhost:8000/index" \
  -H "accept: application/json" \
  -F "file=@data/document.pdf"
```

**Ask a question:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

### Using the Web UI

1. Navigate to `http://localhost:8501`
2. Upload a document using the sidebar
3. Ask questions in the chat interface

## �� EC2 Deployment

### Setup EC2 Instance

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.large (minimum for running models)
   - Storage: 50GB
   - Security Groups: Allow ports 22, 80, 443, 6333, 8000, 8501

2. **Install Dependencies**
```bash
ssh ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Clone repository
git clone <your-repo-url>
cd mlops_final
```

3. **Deploy**
```bash
docker-compose up -d
```

### GitHub Actions Secrets

Add these secrets to your GitHub repository:
- `EC2_SSH_KEY`: Your EC2 private key
- `EC2_HOST`: EC2 instance public IP
- `EC2_USER`: EC2 username (usually `ubuntu`)

## 🔧 Configuration

Edit `backend/config.py` or create a `.env` file:

```env
LLM_MODEL_NAME=Qwen/Qwen2.5-0.5B-Instruct
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
QDRANT_HOST=localhost
QDRANT_PORT=6333
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3
```

## 📝 Logging

Logs are stored in `logs/backend.log` and include:
- API requests and responses
- Document indexing operations
- Model inference times
- Errors and exceptions

## 🧪 Testing

### Test Backend
```bash
cd backend
python -m pytest tests/
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/

# Expected: {"status":"healthy","message":"RAG Microservice is running"}
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Runs linting and code quality checks
2. Tests backend and frontend
3. Deploys to EC2 on merge to main branch

## 🛠️ Troubleshooting

### Models not loading
- Ensure you have enough RAM (8GB minimum)
- Check `logs/backend.log` for errors
- Try using CPU if GPU memory is insufficient

### Qdrant connection issues
- Verify Qdrant is running: `docker ps | grep qdrant`
- Check Qdrant logs: `docker logs <qdrant-container-id>`

### Port already in use
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

## 📈 Performance Optimization

- Use GPU for faster inference
- Increase `CHUNK_SIZE` for larger context windows
- Adjust `TOP_K_RESULTS` based on accuracy needs
- Use caching for frequently accessed documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## �� License

MIT License

## 👥 Authors

Your Name - MLOps Assignment 2026
