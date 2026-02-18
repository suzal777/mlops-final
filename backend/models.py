from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
import torch
from logger_config import logger
from config import settings

class EmbeddingModel:
    def __init__(self):
        """Initialize the embedding model using HuggingFace"""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            
            # Determine device
            device = "cpu"
            if torch.cuda.is_available():
                try:
                    # Try to allocate a small tensor to test if CUDA actually works
                    test_tensor = torch.tensor([1.0]).cuda()
                    del test_tensor
                    torch.cuda.empty_cache()
                    device = "cuda"
                    logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
                    logger.info(
                        f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB"
                    )
                except Exception as e:
                    logger.warning(f"CUDA error: {e}. Falling back to CPU")
                    device = "cpu"
            else:
                logger.info("CUDA not available, using CPU")
            
            logger.info(f"Initializing embeddings with model: {settings.EMBEDDING_MODEL_NAME} on device: {device}")
            
            # Initialize HuggingFace embeddings
            self.model = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={"device": device}
            )
            
            # Get embedding dimension by encoding a test string
            test_embedding = self.model.embed_query("test")
            self.dimension = len(test_embedding)
            
            logger.info(f"Embedding model loaded. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts):
        """Generate embeddings for texts"""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            # Use embed_documents for batch encoding
            if len(texts) > 1:
                embeddings = self.model.embed_documents(texts)
            else:
                embeddings = [self.model.embed_query(texts[0])]
            
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise

class LLMModel:
    def __init__(self):
        """Initialize the LLM model using Ollama"""
        try:
            logger.info(f"Initializing LLM: {settings.LLM_MODEL} (temp={settings.LLM_TEMPERATURE})")
            self.llm = ChatOllama(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                base_url=settings.OLLAMA_BASE_URL,
            )
            logger.info("LLM model initialized successfully with Ollama")
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {e}")
            raise
    
    def generate(self, prompt: str, max_length: int = 512) -> str:
        """Generate response from the model"""
        try:
            logger.info("Generating response with Ollama...")
            
            # Stream the response from Ollama
            response = self.llm.stream(prompt)
            
            logger.info("LLM response received, processing stream...")
            
            # Collect the streamed response
            response_content = ""
            for chunk in response:
                if hasattr(chunk, "content") and isinstance(chunk.content, str):
                    response_content += chunk.content
            
            logger.info(f"Generated response of length: {len(response_content)}")
            return response_content.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
