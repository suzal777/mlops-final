from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import uuid
from logger_config import logger
from config import settings

class QdrantManager:
    def __init__(self):
        """Initialize Qdrant client and create collection if needed"""
        try:
            # Connect using URL format like the reference
            qdrant_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
            self.client = QdrantClient(url=qdrant_url)
            logger.info(f"Connected to Qdrant at {qdrant_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    def create_collection(self, vector_size: int):
        """Create a collection if it doesn't exist"""
        try:
            # Check if collection exists using collection_exists method
            if not self.client.collection_exists(settings.QDRANT_COLLECTION_NAME):
                logger.warning(f"Collection '{settings.QDRANT_COLLECTION_NAME}' doesn't exist. Creating it...")
                self.client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Collection '{settings.QDRANT_COLLECTION_NAME}' created successfully.")
            else:
                logger.info(f"Using existing collection: {settings.QDRANT_COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_documents(self, texts: List[str], embeddings: List[List[float]], metadata: List[Dict]):
        """Add documents to Qdrant"""
        try:
            points = []
            for idx, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                point_id = str(uuid.uuid4())
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "text": text,
                            "chunk_id": idx,
                            **meta
                        }
                    )
                )
            
            self.client.upsert(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points=points
            )
            logger.info(f"Successfully uploaded {len(points)} document chunks to Qdrant collection '{settings.QDRANT_COLLECTION_NAME}'")
            return len(points)
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, query_embedding: List[float], top_k: int = None) -> List[Dict]:
        """Search for similar documents"""
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            results = self.client.search(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query_vector=query_embedding,
                limit=top_k
            )
            
            documents = []
            for result in results:
                documents.append({
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                })
            
            logger.info(f"Found {len(documents)} relevant documents")
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
