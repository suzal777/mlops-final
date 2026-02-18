from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Model settings
    LLM_MODEL_NAME: str = "Qwen/Qwen2.5-0.5B-Instruct"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    
    # Qdrant settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "documents"
    
    # Processing settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 3
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "../logs/backend.log"
    
    class Config:
        env_file = ".env"

settings = Settings()
