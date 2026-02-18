from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from logger_config import logger
from config import settings

class EmbeddingModel:
    def __init__(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts):
        """Generate embeddings for texts"""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist() if len(texts) > 1 else [embeddings.tolist()]
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise

class LLMModel:
    def __init__(self):
        """Initialize the LLM model"""
        try:
            logger.info(f"Loading LLM model: {settings.LLM_MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL_NAME)
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.LLM_MODEL_NAME,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            raise
    
    def generate(self, prompt: str, max_length: int = 512) -> str:
        """Generate response from the model"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ]
            
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            if "<|im_start|>assistant" in response:
                response = response.split("<|im_start|>assistant")[-1]
            if "<|im_end|>" in response:
                response = response.split("<|im_end|>")[0]
            
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
