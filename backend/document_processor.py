from PyPDF2 import PdfReader
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from logger_config import logger
from config import settings
import os

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            logger.info(f"Extracted text from PDF: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from a TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Extracted text from TXT: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
    
    def process_file(self, file_path: str) -> tuple[List[str], List[Dict]]:
        """Process a file and return chunks with metadata"""
        try:
            # Extract text based on file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_extension == '.txt':
                text = self.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Create metadata for each chunk
            metadata = [
                {
                    "source": os.path.basename(file_path),
                    "chunk_id": idx,
                    "file_type": file_extension
                }
                for idx in range(len(chunks))
            ]
            
            return chunks, metadata
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise
