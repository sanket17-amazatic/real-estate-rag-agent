"""
Test PDF ingestion endpoint
"""
import requests
import os

def test_pdf_ingestion():
    """Test uploading and ingesting a PDF"""
    
    # API endpoint
    url = "http://localhost:8000/ingest/pdf"
    
    # PDF file path
    pdf_path = "data/pdfs/Wakad_Properties_Sample.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"📤 Uploading PDF: {pdf_path}")
    
    # Prepare the multipart form data
    with open(pdf_path, 'rb') as f:
        files = {
            'file': ('Wakad_Properties_Sample.pdf', f, 'application/pdf')
        }
        data = {
            'locality': 'Wakad',
            'property_type': 'Residential'
        }
        
        try:
            response = requests.post(url, files=files, data=data)
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📄 Response Body:")
            print(response.json())
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Ingestion successful!")
                print(f"   - Chunks created: {result.get('chunks_created', 'N/A')}")
                print(f"   - Vectors inserted: {result.get('vectors_inserted', 'N/A')}")
            else:
                print(f"\n❌ Ingestion failed!")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Is it running?")
            print("   Start server with: uvicorn main:app --reload --host localhost --port 8000")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_pdf_ingestion()
