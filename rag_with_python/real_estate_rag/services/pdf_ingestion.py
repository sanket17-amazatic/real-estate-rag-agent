"""
PDF Ingestion Service
Handles PDF text extraction, chunking, embedding, and Milvus insertion
"""
import logging
import os
import json
from typing import List, Dict, Any, Tuple
import PyPDF2
from pathlib import Path
from services.llm_processor import get_default_llm_processor
from services.milvus_service import get_milvus_service
from config.settings import settings

logger = logging.getLogger(__name__)


class PDFIngestionService:
    """Service for ingesting PDFs into Milvus vector database"""
    
    def __init__(self):
        self.llm_processor = get_default_llm_processor()
        self.milvus_service = get_milvus_service()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            chunk_size: Number of characters per chunk
            overlap: Number of overlapping characters
        
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            i += chunk_size - overlap
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def extract_metadata_from_text(self, text: str, filename: str) -> Dict[str, str]:
        """
        Extract metadata from text content (locality, property type, etc.)
        
        Args:
            text: Document text
            filename: Source filename
        
        Returns:
            Dictionary of extracted metadata
        """
        # Extract locality from text patterns
        locality = "Unknown"
        property_type = "Unknown"
        
        # Common Pune localities (order matters - check more specific first)
        localities = [
            "Pimple Nilakh", "Pimple Saudagar", "Koregaon Park", "Kalyani Nagar",
            "Viman Nagar", "Magarpatta", "Baner", "Wakad", "Hinjewadi", 
            "Kharadi", "Kothrud", "Hadapsar", "Aundh", "Balewadi", 
            "Pimpri", "Chinchwad", "Wagholi", "Katraj", "Kondhwa"
        ]
        
        # Check for locality mentions - find ALL occurrences and pick most frequent
        text_lower = text.lower()
        locality_counts = {}
        for loc in localities:
            count = text_lower.count(loc.lower())
            if count > 0:
                locality_counts[loc] = count
        
        # Pick the most frequently mentioned locality
        if locality_counts:
            locality = max(locality_counts, key=locality_counts.get)
        
        # Check for property types
        if "apartment" in text_lower or "flat" in text_lower:
            property_type = "Apartment"
        elif "villa" in text_lower or "row house" in text_lower:
            property_type = "Villa"
        elif "plot" in text_lower or "land" in text_lower:
            property_type = "Plot"
        elif "commercial" in text_lower or "office" in text_lower:
            property_type = "Commercial"
        
        return {
            "locality": locality,
            "property_type": property_type,
            "source": "pdf_ingestion",
            "filename": filename
        }
    
    def ingest_pdf(
        self, 
        pdf_path: str, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Complete PDF ingestion pipeline
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional additional metadata
        
        Returns:
            Ingestion results
        """
        try:
            filename = Path(pdf_path).name
            logger.info(f"Starting ingestion of PDF: {filename}")
            
            # Step 1: Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text or len(text) < 100:
                raise ValueError(f"Insufficient text extracted from {filename}")
            
            # Step 2: Extract metadata from content
            auto_metadata = self.extract_metadata_from_text(text, filename)
            
            # Merge with provided metadata
            if metadata:
                auto_metadata.update(metadata)
            
            # Step 3: Chunk text
            chunks = self.chunk_text(text)
            
            if not chunks:
                raise ValueError(f"No chunks created from {filename}")
            
            # Step 4: Generate embeddings and extract metadata for each chunk
            embeddings = []
            localities = []
            property_types = []
            metadata_jsons = []
            
            for i, chunk in enumerate(chunks):
                try:
                    # Generate embedding
                    embedding = self.llm_processor.generate_embedding(chunk)
                    embeddings.append(embedding)
                    
                    # Extract metadata from this specific chunk
                    chunk_metadata = self.extract_metadata_from_text(chunk, filename)
                    # Merge with provided metadata (provided metadata takes precedence)
                    if metadata:
                        chunk_metadata.update(metadata)
                    
                    localities.append(chunk_metadata.get("locality", "Unknown"))
                    property_types.append(chunk_metadata.get("property_type", "Unknown"))
                    metadata_jsons.append(json.dumps(chunk_metadata))
                    
                    logger.info(f"Generated embedding for chunk {i+1}/{len(chunks)} - Locality: {chunk_metadata.get('locality')}")
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {i}: {str(e)}")
                    raise
            
            # Step 5: Prepare data for Milvus insertion
            texts = chunks
            filenames = [filename] * len(chunks)
            chunk_indices = list(range(len(chunks)))
            
            # Step 6: Insert into Milvus
            num_inserted = self.milvus_service.insert_vectors(
                embeddings=embeddings,
                texts=texts,
                filenames=filenames,
                localities=localities,
                property_types=property_types,
                chunk_indices=chunk_indices,
                metadata_jsons=metadata_jsons
            )
            
            result = {
                "success": True,
                "filename": filename,
                "chunks_created": len(chunks),
                "vectors_inserted": num_inserted,
                "metadata": auto_metadata,
                "message": f"Successfully ingested {filename} with {num_inserted} vectors"
            }
            
            logger.info(f"Successfully completed ingestion of {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Error in PDF ingestion: {str(e)}")
            return {
                "success": False,
                "filename": Path(pdf_path).name if pdf_path else "unknown",
                "chunks_created": 0,
                "vectors_inserted": 0,
                "message": f"Failed to ingest PDF: {str(e)}"
            }


def get_pdf_ingestion_service() -> PDFIngestionService:
    """Get PDFIngestionService instance"""
    return PDFIngestionService()
