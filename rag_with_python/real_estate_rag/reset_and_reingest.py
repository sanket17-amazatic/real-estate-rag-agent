"""
Clear Milvus collection and re-ingest all PDFs with correct metadata
"""
from services.milvus_service import get_milvus_service
import os

print("=== Clearing and Re-ingesting PDFs ===\n")

try:
    # Get Milvus service
    milvus_service = get_milvus_service()
    milvus_service.connect()
    
    # Drop existing collection
    print("Dropping existing collection...")
    milvus_service.create_collection(drop_existing=True)
    print("✓ Collection dropped and recreated\n")
    
    # Move processed PDFs back to pdfs folder
    processed_dir = "data/processed"
    pdfs_dir = "data/pdfs"
    
    if os.path.exists(processed_dir):
        for file in os.listdir(processed_dir):
            if file.endswith('.pdf'):
                src = os.path.join(processed_dir, file)
                dst = os.path.join(pdfs_dir, file)
                os.rename(src, dst)
                print(f"Moved {file} back to pdfs folder")
    
    print("\n✅ Ready to re-ingest! Run: POST /ingest")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    milvus_service.disconnect()
