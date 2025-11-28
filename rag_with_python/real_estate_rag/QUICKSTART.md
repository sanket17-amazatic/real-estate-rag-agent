# Quick Start Guide - Real Estate RAG System

## Step-by-Step Setup

### Step 1: Install Dependencies

```powershell
# Navigate to project directory
cd c:\Users\AH012\OneDrive\Desktop\DEMO\real_estate_rag

# Install main dependencies
pip install -r requirements.txt

# Install PDF conversion utility (optional, for converting text to PDF)
pip install -r requirements-pdf.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root with your credentials:

```powershell
# Copy the example file
Copy-Item .env.example .env

# Edit .env with your actual credentials
notepad .env
```

Add your credentials:
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Zilliz Cloud - Get from "Connect" panel in Zilliz console
MILVUS_URI=https://in03-xxxxx.api.gcp-us-west1.zillizcloud.com
MILVUS_TOKEN=your_zilliz_api_key_here

# Optional auth
MILVUS_USER=db_admin
MILVUS_PASSWORD=your_password
MILVUS_DB=default
```

### Step 3: Convert Your Mock Data to PDF (Optional)

If you want to convert your text file to PDF:

```powershell
python convert_to_pdf.py "NewLaunches_MockData (1).txt"
```

This will create `data/pdfs/NewLaunches_Complete.pdf`

### Step 4: Start the FastAPI Server

```powershell
python main.py
```

Or with uvicorn:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Connected to Milvus at your-endpoint
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Access the API

Open your browser: **http://localhost:8000**

You'll see the API documentation.

Interactive docs: **http://localhost:8000/docs**

### Step 6: Ingest Your PDF Documents

#### Option A: Using curl
```powershell
curl -X POST "http://localhost:8000/ingest/pdf" `
  -F "file=@data/pdfs/NewLaunches_Complete.pdf" `
  -F "locality=Wakad" `
  -F "property_type=Apartment"
```

#### Option B: Using Python
```python
import requests

with open("data/pdfs/NewLaunches_Complete.pdf", "rb") as f:
    files = {"file": f}
    data = {"locality": "Wakad", "property_type": "Apartment"}
    response = requests.post("http://localhost:8000/ingest/pdf", files=files, data=data)
    print(response.json())
```

#### Option C: Using FastAPI Docs
1. Go to http://localhost:8000/docs
2. Find `/ingest/pdf` endpoint
3. Click "Try it out"
4. Upload your PDF file
5. Execute

### Step 7: Test the System

Run the test suite:
```powershell
python test_api.py
```

Or test individual endpoints:

#### Test RAG Query
```powershell
curl -X POST "http://localhost:8000/query/rag" `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What are the amenities in Wakad?\", \"top_k\": 5}'
```

#### Test Buy Agent
```powershell
curl -X POST "http://localhost:8000/query/agent" `
  -H "Content-Type: application/json" `
  -d '{\"agent_type\": \"buy\", \"message\": \"I want a 2 BHK in Wakad under 80 lakhs\"}'
```

#### Test Auto-Routing
```powershell
curl -X POST "http://localhost:8000/query/auto?query=Tell%20me%20about%20Wakad%20locality"
```

## API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/stats` | GET | Collection statistics |
| `/ingest/pdf` | POST | Upload and ingest PDF |
| `/query/rag` | POST | Direct RAG query |
| `/query/agent` | POST | Query specific agent |
| `/query/auto` | POST | Auto-route query |
| `/search/properties` | POST | Search properties |

## Example Usage Scenarios

### Scenario 1: Upload Property Brochures

```powershell
# Upload multiple PDFs
curl -X POST "http://localhost:8000/ingest/pdf" -F "file=@wakad_property.pdf"
curl -X POST "http://localhost:8000/ingest/pdf" -F "file=@baner_property.pdf"
curl -X POST "http://localhost:8000/ingest/pdf" -F "file=@hinjewadi_property.pdf"
```

### Scenario 2: Query About Locality

```json
POST /query/rag
{
  "query": "What are the connectivity options in Wakad?",
  "top_k": 5
}
```

### Scenario 3: Search for Properties to Buy

```json
POST /query/agent
{
  "agent_type": "buy",
  "message": "Show me 2 BHK apartments in Wakad under 1 crore"
}
```

### Scenario 4: Find Rental Properties

```json
POST /query/agent
{
  "agent_type": "rent",
  "message": "Looking for a furnished 2 BHK in Hinjewadi under 30k monthly"
}
```

### Scenario 5: Get Property Details

```json
POST /query/agent
{
  "agent_type": "details",
  "message": "Tell me about Evergreen Heights amenities and specifications"
}
```

### Scenario 6: Let System Auto-Route

```
POST /query/auto?query=What schools are near Wakad?
```

The orchestrator will automatically determine this is a knowledge query and use RAG.

## Verification Checklist

- [ ] Dependencies installed successfully
- [ ] `.env` file configured with credentials
- [ ] Server starts without errors
- [ ] Milvus connection successful (check logs)
- [ ] PDF ingestion works
- [ ] RAG queries return results
- [ ] Agents respond to queries
- [ ] Auto-routing works correctly

## Common Issues & Solutions

### Issue 1: Milvus Connection Failed
**Solution:** 
- Verify your Zilliz Cloud credentials in `.env`
- Check if your IP is whitelisted in Zilliz Cloud console
- Ensure `secure=True` in connection

### Issue 2: OpenAI API Error
**Solution:**
- Verify API key is correct
- Check if you have API credits
- Ensure you have access to GPT-4 models

### Issue 3: PDF Ingestion Fails
**Solution:**
- Ensure PDF is not encrypted
- Check if PDF has extractable text
- Verify file is not corrupted

### Issue 4: No Results from RAG Query
**Solution:**
- First ingest some PDFs
- Check collection stats: `GET /stats`
- Verify documents were inserted

### Issue 5: Import Errors
**Solution:**
```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Next Steps

1. **Upload All Your Property PDFs**
   - Organize PDFs in `data/pdfs/` folder
   - Use batch upload script (create if needed)

2. **Customize Agents**
   - Modify system prompts in `agents/real_estate_agents.py`
   - Add custom tools as needed

3. **Extend Mock Property Database**
   - Update `tools/property_tools.py`
   - Connect to real database/API

4. **Monitor Performance**
   - Check logs for errors
   - Monitor Milvus collection size
   - Track API response times

5. **Deploy to Production**
   - Use Docker for containerization
   - Deploy on cloud (AWS, Azure, GCP)
   - Add authentication/authorization
   - Set up monitoring and logging

## Support

For issues or questions:
1. Check the main README.md
2. Review FastAPI docs at `/docs`
3. Check server logs for errors
4. Verify all credentials are correct

## Architecture Overview

```
User Query
    ↓
FastAPI Endpoint (/query/auto)
    ↓
Orchestrator (Intent Detection)
    ↓
├─→ Direct RAG (Knowledge Queries)
│       ↓
│   RAG Tool → Milvus Search → LLM Generation
│
├─→ BuyAgent (Purchase Queries)
│       ↓
│   Search Tool + RAG Tool
│
├─→ RentAgent (Rental Queries)
│       ↓
│   Search Tool + RAG Tool
│
└─→ DetailsAgent (Information Queries)
        ↓
    RAG Tool (Detailed Retrieval)
```

Good luck! 🚀
