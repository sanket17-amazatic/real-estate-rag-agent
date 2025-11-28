import os
import re
import logging
from typing import List, Dict, Any
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        try:
            # Split by sentences for better chunking
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                sentence_length = len(sentence.split())
                
                if current_length + sentence_length > chunk_size and current_chunk:
                    # Add the current chunk
                    chunks.append({
                        "text": " ".join(current_chunk),
                        "metadata": {}
                    })
                    
                    # Start new chunk with overlap
                    overlap_words = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
                    current_chunk = overlap_words.copy()
                    current_length = len(" ".join(current_chunk).split())
                
                current_chunk.append(sentence)
                current_length += sentence_length
            
            # Add the last chunk if not empty
            if current_chunk:
                chunks.append({
                    "text": " ".join(current_chunk),
                    "metadata": {}
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise

    @staticmethod
    def process_pdf(file_path: str, source_name: str = None) -> List[Dict[str, Any]]:
        """Process a PDF file into chunks with metadata."""
        try:
            if not source_name:
                source_name = os.path.basename(file_path)
                
            # Extract text
            text = DocumentProcessor.extract_text_from_pdf(file_path)
            if not text.strip():
                raise ValueError(f"No text extracted from {file_path}")
            
            # Chunk text
            chunks = DocumentProcessor.chunk_text(text)
            
            # Add source metadata
            for chunk in chunks:
                chunk["source"] = source_name
                chunk["page"] = 0  # Page number not available with PyPDF2's page extraction
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise
