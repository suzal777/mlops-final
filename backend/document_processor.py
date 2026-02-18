from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
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
            add_start_index=True,  # This adds character position metadata
        )
    
    def extract_text_from_pdf(self, file_path: str) -> tuple[List[str], List[Dict]]:
        """Extract text from a PDF file using LangChain"""
        try:
            # Load PDF using LangChain
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add additional metadata to documents
            for i, doc in enumerate(documents):
                # PyPDFLoader already adds page number, but let's ensure it's there
                if "page" not in doc.metadata:
                    doc.metadata["page"] = i
                # Add more metadata
                doc.metadata["source_file"] = os.path.basename(file_path)
                doc.metadata["document_type"] = "pdf"
            
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            
            # Add chunk-specific metadata
            chunks = []
            metadata = []
            for i, chunk in enumerate(texts):
                chunks.append(chunk.page_content)
                chunk_meta = {
                    "source": os.path.basename(file_path),
                    "chunk_id": i,
                    "chunk_size": len(chunk.page_content),
                    "file_type": ".pdf",
                    "page": chunk.metadata.get("page", 0),
                    "document_type": "pdf"
                }
                # Preserve and enhance existing metadata
                if "start_index" in chunk.metadata:
                    chunk_meta["char_start"] = chunk.metadata["start_index"]
                
                metadata.append(chunk_meta)
            
            logger.info(f"Extracted {len(chunks)} chunks from PDF: {len(''.join(chunks))} characters")
            return chunks, metadata
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> tuple[List[str], List[Dict]]:
        """Extract text from a TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Extracted text from TXT: {len(text)} characters")
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create metadata for each chunk
            metadata = [
                {
                    "source": os.path.basename(file_path),
                    "chunk_id": idx,
                    "chunk_size": len(chunk),
                    "file_type": ".txt",
                    "document_type": "text"
                }
                for idx, chunk in enumerate(chunks)
            ]
            
            return chunks, metadata
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
    
    def process_file(self, file_path: str) -> tuple[List[str], List[Dict]]:
        """Process a file and return chunks with metadata"""
        try:
            # Extract text based on file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                chunks, metadata = self.extract_text_from_pdf(file_path)
            elif file_extension == '.txt':
                chunks, metadata = self.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            logger.info(f"Split document into {len(chunks)} chunks")
            
            return chunks, metadata
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise
