# System Architecture Diagrams

## 1. Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│  (Postman / cURL / Frontend App / test_api.py)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                         (main.py)                                │
│                                                                   │
│  Endpoints:                                                       │
│  • POST /ingest/pdf                                              │
│  • POST /query/rag                                               │
│  • POST /query/agent                                             │
│  • POST /query/auto                                              │
│  • POST /search/properties                                       │
│  • GET  /health, /stats                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Layer                            │
│                (agent_orchestrator.py)                           │
│                                                                   │
│  Intent Detection → Route to:                                    │
│  • Direct RAG (knowledge queries)                                │
│  • BuyAgent (purchase queries)                                   │
│  • RentAgent (rental queries)                                    │
│  • DetailsAgent (info queries)                                   │
└────┬────────────────────┬────────────────────┬──────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
┌──────────┐      ┌──────────┐      ┌──────────────────┐
│BuyAgent  │      │RentAgent │      │PropertyDetails   │
│          │      │          │      │Agent             │
└────┬─────┘      └────┬─────┘      └────┬─────────────┘
     │                 │                  │
     └─────────────────┴──────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Tools Layer                               │
│                   (property_tools.py)                            │
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  search_tool     │              │ property_rag_tool│         │
│  │                  │              │                  │         │
│  │ • Property DB    │              │ • Milvus Search  │         │
│  │ • Filter logic   │              │ • LLM Generation │         │
│  └──────────────────┘              └──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Services Layer                              │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ LLMProcessor     │  │ MilvusService    │  │ PDFIngestion  │ │
│  │ (Factory+        │  │ (Singleton)      │  │ Service       │ │
│  │  Singleton)      │  │                  │  │               │ │
│  │                  │  │ • Connect        │  │ • Extract     │ │
│  │ • OpenAI API     │  │ • Create Coll.   │  │ • Chunk       │ │
│  │ • Completions    │  │ • Insert         │  │ • Embed       │ │
│  │ • Embeddings     │  │ • Search         │  │ • Insert      │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐    ┌─────────────────────┐
│   OpenAI API     │    │  Milvus/Zilliz      │
│                  │    │  Cloud              │
│ • GPT-4 Nano     │    │                     │
│ • Embeddings     │    │ • Vector Store      │
└──────────────────┘    │ • Similarity Search │
                        └─────────────────────┘
```

## 2. Query Flow - Auto Routing

```
User Query: "What amenities are in Wakad?"
     │
     ▼
┌──────────────────────────────────┐
│  POST /query/auto                │
│  Orchestrator.route_query()      │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Intent Detection                │
│  LLM analyzes query              │
│  → Returns: "knowledge"          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Direct RAG Path                 │
│  (High confidence knowledge)     │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  property_rag_tool.execute()     │
│  1. Generate query embedding     │
│  2. Search Milvus (top_k=5)      │
│  3. Retrieve relevant docs       │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Context Assembly                │
│  Combine retrieved documents     │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  LLM Generation                  │
│  System: "You are a real estate  │
│           assistant..."          │
│  Context: [Retrieved docs]       │
│  Question: User query            │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Response to User                │
│  {                               │
│    "answer": "...",              │
│    "sources": [...],             │
│    "method": "direct_rag"        │
│  }                               │
└──────────────────────────────────┘
```

## 3. Query Flow - Agent with Tools

```
User Query: "I want to buy a 2 BHK in Wakad under 80 lakhs"
     │
     ▼
┌──────────────────────────────────┐
│  POST /query/auto                │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Intent Detection                │
│  → Returns: "buy"                │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Route to BuyAgent               │
│  agent.process_message()         │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  BuyAgent - Initial LLM Call     │
│  System Prompt + Tools           │
│  → Decides to use search_tool    │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Tool Call: search_properties    │
│  {                               │
│    "locality": "Wakad",          │
│    "bedrooms": 2,                │
│    "max_price": 8000000          │
│  }                               │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  search_tool.execute()           │
│  Filter property database        │
│  → Returns matching properties   │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Agent - Second LLM Call         │
│  System + Conversation + Tool    │
│  Result → Generate final answer  │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Response to User                │
│  "I found 3 properties in Wakad  │
│   matching your criteria..."     │
│  + Property details              │
└──────────────────────────────────┘
```

## 4. PDF Ingestion Pipeline

```
┌──────────────────────────────────┐
│  User uploads PDF                │
│  POST /ingest/pdf                │
│  + file                          │
│  + locality (optional)           │
│  + property_type (optional)      │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  1. Save PDF                     │
│  data/pdfs/filename.pdf          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  2. Text Extraction              │
│  PyPDF2.PdfReader                │
│  Extract text from all pages     │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  3. Metadata Extraction          │
│  Parse text for:                 │
│  • Locality (Wakad, Baner...)    │
│  • Property type (Apartment...)  │
│  • Merge with user metadata      │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  4. Text Chunking                │
│  Split into 500-token chunks     │
│  with 100-token overlap          │
│  → Creates N chunks              │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  5. Generate Embeddings          │
│  For each chunk:                 │
│  LLMProcessor.generate_embedding │
│  → 1536-dim vector               │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  6. Insert to Milvus             │
│  MilvusService.insert_vectors    │
│  Data:                           │
│  • embeddings                    │
│  • texts                         │
│  • filenames                     │
│  • localities                    │
│  • property_types                │
│  • chunk_indices                 │
│  • metadata_jsons                │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  7. Move to Processed            │
│  data/processed/filename.pdf     │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  Return Success Response         │
│  {                               │
│    "success": true,              │
│    "chunks_created": N,          │
│    "vectors_inserted": N         │
│  }                               │
└──────────────────────────────────┘
```

## 5. LLM Processor Factory Pattern

```
┌─────────────────────────────────────────────────────┐
│           LLMProcessorFactory                       │
│           (Singleton Pattern)                       │
│                                                     │
│  _instances = {                                     │
│    "openai_gpt-4o-nano": <OpenAIProcessor>         │
│  }                                                  │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ get_processor(provider, model)               │ │
│  │                                              │ │
│  │ 1. Check if instance exists                 │ │
│  │ 2. Return existing OR create new            │ │
│  │ 3. Store in _instances dict                 │ │
│  └──────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────────┘
               │
               ├─→ OpenAIProcessor
               │   • generate_completion()
               │   • generate_embedding()
               │
               ├─→ AnthropicProcessor (future)
               │
               └─→ AzureOpenAIProcessor (future)

Usage:
  processor = LLMProcessorFactory.get_processor()
  # Returns singleton instance

  same = LLMProcessorFactory.get_processor()
  # Returns SAME instance (not new)
```

## 6. Milvus Collection Schema

```
Collection: real_estate_properties
Index: IVF_FLAT (L2 distance)

┌──────────────────────────────────────────────┐
│ Field Name      │ Type              │ Notes  │
├──────────────────────────────────────────────┤
│ id              │ INT64             │ PK, AutoID │
│ embedding       │ FLOAT_VECTOR[1536]│ Indexed    │
│ text            │ VARCHAR(65535)    │ Chunk text │
│ filename        │ VARCHAR(512)      │ Source PDF │
│ locality        │ VARCHAR(256)      │ Filterable │
│ property_type   │ VARCHAR(256)      │ Filterable │
│ chunk_index     │ INT64             │ Sequence   │
│ metadata_json   │ VARCHAR(2048)     │ Extra data │
└──────────────────────────────────────────────┘

Search Query:
1. User query → embedding (1536-dim)
2. Milvus similarity search (top_k=5)
3. Returns: documents with lowest L2 distance
4. Convert distance to score: 1/(1+distance)
```

## 7. Agent Tool Calling Flow

```
Agent receives: "Show me properties in Wakad"
     │
     ▼
┌──────────────────────────────────────────┐
│  LLM Call with Tools Definition          │
│  messages = [                            │
│    {role: "system", content: prompt},    │
│    {role: "user", content: query}        │
│  ]                                       │
│  tools = [search_tool, rag_tool]        │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  LLM Response                            │
│  {                                       │
│    "tool_calls": [{                      │
│      "function": {                       │
│        "name": "search_properties",      │
│        "arguments": "{                   │
│          'locality': 'Wakad',            │
│          'transaction_type': 'buy'       │
│        }"                                │
│      }                                   │
│    }]                                    │
│  }                                       │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  Execute Tool                            │
│  tool_result = search_tool.execute(...)  │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  Second LLM Call                         │
│  messages = [                            │
│    ...previous messages,                 │
│    {role: "assistant", tool_calls: ...}, │
│    {role: "tool", content: result}       │
│  ]                                       │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  Final Response                          │
│  LLM generates natural language response │
│  using tool results                      │
└──────────────────────────────────────────┘
```

---

These diagrams illustrate the complete architecture and data flow of the Real Estate RAG System.
