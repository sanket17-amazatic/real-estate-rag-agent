# Real Estate RAG System

A comprehensive Real Estate Property Search and Retrieval-Augmented Generation (RAG) system built with FastAPI, OpenAI GPT-4 Nano, and Milvus vector database.

## Features

- **Multi-Agent System**: Specialized agents for buying, renting, and property details
- **RAG Integration**: Semantic search over property brochures and market reports
- **Intelligent Routing**: Automatic query routing to appropriate agents
- **PDF Ingestion**: Upload and process property documents into vector database
- **Milvus Vector Store**: Cloud-based vector storage with Zilliz Cloud
- **LLM Factory Pattern**: Extensible LLM processor with singleton pattern

## Architecture

```
├── agents/                 # Real estate agents (Buy, Rent, Details)
├── tools/                  # Search and RAG tools
├── services/              # LLM processor, Milvus, PDF ingestion
├── orchestrator/          # Intent detection and routing
├── models/                # Pydantic schemas
├── config/                # Settings and configuration
├── data/
│   ├── pdfs/             # Uploaded PDFs
│   └── processed/        # Processed PDFs
└── main.py               # FastAPI application
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Zilliz Cloud Configuration (Serverless)
# Get URI and TOKEN from Zilliz Cloud console "Connect" panel
MILVUS_URI=https://in03-xxxxx.api.gcp-us-west1.zillizcloud.com
MILVUS_TOKEN=your_zilliz_api_key_here

# Optional: username/password auth (if not using token)
MILVUS_USER=db_admin
MILVUS_PASSWORD=your_password
MILVUS_DB=default
MILVUS_COLLECTION=real_estate_properties
```

### 3. Run the Application

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Health & Stats

- `GET /` - API information
- `GET /health` - Health check
- `GET /stats` - Collection statistics

### PDF Ingestion

```bash
POST /ingest/pdf
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- locality (optional): Property locality
- property_type (optional): Property type
```

**Example:**
```bash
curl -X POST "http://localhost:8000/ingest/pdf" \
  -F "file=@property_brochure.pdf" \
  -F "locality=Wakad" \
  -F "property_type=Apartment"
```

### RAG Query

```bash
POST /query/rag
Content-Type: application/json

{
  "query": "What are the amenities in Wakad locality?",
  "top_k": 5,
  "include_context": true
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/query/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about Evergreen Heights amenities",
    "top_k": 5
  }'
```

### Agent Query

```bash
POST /query/agent
Content-Type: application/json

{
  "agent_type": "buy",  # or "rent", "details"
  "message": "I want to buy a 2 BHK in Wakad under 80 lakhs"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/query/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "buy",
    "message": "Show me 2 BHK apartments in Wakad"
  }'
```

### Auto-Route Query

```bash
POST /query/auto?query=What are the connectivity options in Hinjewadi?
```

**Example:**
```bash
curl -X POST "http://localhost:8000/query/auto?query=Tell%20me%20about%20Wakad%20locality"
```

### Property Search

```bash
POST /search/properties
Content-Type: application/json

{
  "query": "2 BHK in Wakad",
  "locality": "Wakad",
  "min_price": 5000000,
  "max_price": 10000000,
  "bedrooms": 2
}
```

## Agent Types

### 1. BuyAgent
Specializes in property buying queries, searches, and investment advice.

**Use Cases:**
- Finding properties to purchase
- Investment recommendations
- New launches and pricing

### 2. RentAgent
Handles rental property queries and tenant requirements.

**Use Cases:**
- Rental property search
- Lease terms and agreements
- Furnishing options

### 3. PropertyDetailsAgent
Provides detailed information about properties and localities.

**Use Cases:**
- Locality information
- Project amenities and specifications
- Market trends and analysis

## Tools

### search_tool
Searches property database for available properties based on filters.

### property_rag_tool
Retrieves information from property documents using semantic search.

## LLM Processor

The system uses a factory pattern with singleton instances:

```python
from services.llm_processor import LLMProcessorFactory

# Get OpenAI processor (default)
processor = LLMProcessorFactory.get_processor(
    provider="openai",
    model="gpt-4o-nano"
)

# Generate completion
response = processor.generate_completion(messages)

# Generate embedding
embedding = processor.generate_embedding(text)
```

## Milvus Collection Schema

```
Collection: real_estate_properties
Fields:
- id (INT64, auto_id): Primary key
- embedding (FLOAT_VECTOR[1536]): Text embeddings
- text (VARCHAR): Original text chunk
- filename (VARCHAR): Source PDF filename
- locality (VARCHAR): Property locality
- property_type (VARCHAR): Type of property
- chunk_index (INT64): Chunk sequence number
- metadata_json (VARCHAR): Additional metadata
```

## Example Usage Flow

### 1. Ingest Property Brochures

Upload your property PDF brochures to the system. The mock data file you have can be converted to PDF or you can upload it directly.

```bash
# Upload PDF
curl -X POST "http://localhost:8000/ingest/pdf" \
  -F "file=@NewLaunches_MockData.pdf" \
  -F "locality=Wakad"
```

### 2. Query for Information

```bash
# Ask about locality
curl -X POST "http://localhost:8000/query/auto?query=What%20are%20the%20amenities%20in%20Wakad?"

# Search for properties to buy
curl -X POST "http://localhost:8000/query/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "buy",
    "message": "I want a 2 BHK in Wakad under 1 crore"
  }'

# Get property details
curl -X POST "http://localhost:8000/query/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "details",
    "message": "Tell me about Evergreen Heights project"
  }'
```

## Orchestrator Logic

The orchestrator automatically determines:

1. **Knowledge queries** → Direct RAG retrieval
   - "What amenities are in Wakad?"
   - "Tell me about connectivity in Hinjewadi"

2. **Buy queries** → BuyAgent
   - "I want to buy a property"
   - "Show me apartments for sale"

3. **Rent queries** → RentAgent
   - "Looking for rental properties"
   - "2 BHK for rent"

4. **Details queries** → PropertyDetailsAgent
   - "Project specifications"
   - "Floor plans and configurations"

## Development

### Project Structure

```
real_estate_rag/
├── main.py                 # FastAPI app
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── .env.example           # Example env file
├── agents/
│   └── real_estate_agents.py
├── tools/
│   └── property_tools.py
├── services/
│   ├── llm_processor.py
│   ├── milvus_service.py
│   └── pdf_ingestion.py
├── orchestrator/
│   └── agent_orchestrator.py
├── models/
│   └── schemas.py
├── config/
│   └── settings.py
└── data/
    ├── pdfs/
    └── processed/
```

### Adding New LLM Providers

Extend the `BaseLLMProcessor` class:

```python
class NewLLMProcessor(BaseLLMProcessor):
    def generate_completion(self, messages, tools=None, ...):
        # Implementation
        pass
    
    def generate_embedding(self, text):
        # Implementation
        pass
```

Register in factory:

```python
# In LLMProcessorFactory.get_processor()
elif provider.lower() == "newprovider":
    processor = NewLLMProcessor(...)
```

## Notes

- The system uses GPT-4 Nano model for cost-effective operations
- Embeddings use `text-embedding-3-small` (1536 dimensions)
- Text chunks are 500 tokens with 100 token overlap
- Milvus uses IVF_FLAT index for efficient similarity search
- All agents use Chat Completion approach (not Assistant API)

## Troubleshooting

1. **Milvus Connection Error**
   - Verify Zilliz Cloud credentials in `.env`
   - Check network connectivity to Milvus endpoint

2. **OpenAI API Error**
   - Verify API key in `.env`
   - Check API quota and billing

3. **PDF Ingestion Fails**
   - Ensure PDF is not encrypted or corrupted
   - Check PDF has extractable text (not scanned images)

## License

MIT License
