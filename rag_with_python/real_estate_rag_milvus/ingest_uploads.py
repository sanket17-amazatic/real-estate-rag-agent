"""
Script to process all PDFs in the uploads directory and ingest them into Milvus.
"""
import os
from document_processor import DocumentProcessor
from embedding_service import EmbeddingService
from vector_store import MilvusStore

UPLOADS_DIR = "uploads"

def ingest_all_pdfs():
    vector_store = MilvusStore()
    document_processor = DocumentProcessor()
    embedding_service = EmbeddingService()

    for filename in os.listdir(UPLOADS_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(UPLOADS_DIR, filename)
            print(f"Processing {file_path}...")
            try:
                chunks = document_processor.process_pdf(file_path, source_name=filename)
                if not chunks:
                    print(f"No valid text extracted from {filename}")
                    continue
                texts = [chunk["text"] for chunk in chunks]
                embeddings = embedding_service.get_embeddings(texts)
                import asyncio
                asyncio.run(vector_store.insert_documents(chunks, embeddings))
                print(f"Ingested {len(chunks)} chunks from {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def main():
    ingest_all_pdfs()
    print("All PDFs processed and ingested.")

if __name__ == "__main__":
    main()
