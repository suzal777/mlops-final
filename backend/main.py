from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
from typing import Optional

from config import settings
from logger_config import logger
from models import EmbeddingModel, LLMModel
from qdrant_manager import QdrantManager
from document_processor import DocumentProcessor

# Initialize FastAPI app
app = FastAPI(title="RAG Microservice", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models (loaded once at startup)
embedding_model = None
llm_model = None
qdrant_manager = None
doc_processor = None

# Pydantic models
class ChatRequest(BaseModel):
    query: str
    max_length: Optional[int] = 512

class ChatResponse(BaseModel):
    answer: str
    sources: list

class IndexResponse(BaseModel):
    message: str
    chunks_indexed: int

@app.on_event("startup")
async def startup_event():
    """Initialize models and connections on startup"""
    global embedding_model, llm_model, qdrant_manager, doc_processor
    
    try:
        logger.info("Starting RAG Microservice...")
        
        # Initialize components
        embedding_model = EmbeddingModel()
        llm_model = LLMModel()
        qdrant_manager = QdrantManager()
        doc_processor = DocumentProcessor()
        
        # Create Qdrant collection
        qdrant_manager.create_collection(vector_size=embedding_model.dimension)
        
        logger.info("RAG Microservice started successfully!")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "RAG Microservice is running"}

@app.post("/index", response_model=IndexResponse)
async def index_document(file: UploadFile = File(...)):
    """
    Index a document (PDF or TXT) into the vector database
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and TXT files are supported"
            )
        
        logger.info(f"Indexing file: {file.filename}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document
            chunks, metadata = doc_processor.process_file(tmp_file_path)
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = embedding_model.encode(chunks)
            
            # Store in Qdrant
            logger.info("Storing in Qdrant...")
            num_indexed = qdrant_manager.add_documents(chunks, embeddings, metadata)
            
            return IndexResponse(
                message=f"Successfully indexed {file.filename}",
                chunks_indexed=num_indexed
            )
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer a query using RAG (Retrieval-Augmented Generation)
    """
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Generate query embedding
        query_embedding = embedding_model.encode([request.query])[0]
        
        # Search for relevant documents
        relevant_docs = qdrant_manager.search(query_embedding)
        
        if not relevant_docs:
            return ChatResponse(
                answer="I don't have enough context to answer this question. Please index some documents first.",
                sources=[]
            )
        
        # Prepare context from retrieved documents
        context = "\n\n".join([doc["text"] for doc in relevant_docs])
        
        # Create prompt for LLM
        prompt = f"""Context information is below:
---------------------
{context}
---------------------

Based on the context above, please answer the following question. If the answer cannot be found in the context, say so.

Question: {request.query}

Answer:"""
        
        # Generate response
        logger.info("Generating response...")
        answer = llm_model.generate(prompt, max_length=request.max_length)
        
        # Prepare sources         
        sources = [
            {
                "text": doc["text"][:200] + "...",
                "score": doc["score"],
                "source": doc["metadata"].get("source", "unknown")
            }
            for doc in relevant_docs
        ]
        
        return ChatResponse(answer=answer, sources=sources)
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
