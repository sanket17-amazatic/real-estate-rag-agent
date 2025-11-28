import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from config import settings
from vector_store import MilvusStore
from document_processor import DocumentProcessor
from embedding_service import EmbeddingService
from query_preprocessor import QueryPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Initialize services once
vector_store = MilvusStore()
document_processor = DocumentProcessor()
embedding_service = EmbeddingService()

app = FastAPI(
    title="Real Estate RAG API with Zilliz Cloud",
    description="API for querying real estate documents using RAG with Zilliz Cloud",
    version="1.0.0"
)

# CORS middleware - Fixed configuration
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_origin_regex=".*",
)

# Models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    results: List[dict]
    query: str
    content: str = None  # For frontend compatibility

class UploadResponse(BaseModel):
    message: str
    file_id: str
    chunks_processed: int


# Helper function to save uploaded file
def save_upload_file(file: UploadFile) -> str:
    file_extension = os.path.splitext(file.filename)[1]
    file_id = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", file_id)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")

# API Endpoints

@app.post("/upload/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    source_name: Optional[str] = None
):
    """
    Upload a PDF file for processing and automatic ingestion into Milvus.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = save_upload_file(file)
    source_name = source_name or os.path.basename(file.filename)
    try:
        # Process PDF and chunk
        chunks = document_processor.process_pdf(file_path, source_name)
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid text extracted from the PDF")

        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        print("\n--- BEFORE EMBEDDING SERVICE ---")
        print(f"Number of texts: {len(texts)}")
        print(f"First text sample: {texts[0][:100]}..." if texts else "No texts to process")
        
        embeddings = embedding_service.get_embeddings(texts)

        # Debug check after getting embeddings
        print("\n--- AFTER EMBEDDING SERVICE ---")
        print(f"Embeddings type: {type(embeddings)}")
        print(f"Number of embeddings: {len(embeddings) if embeddings else 0}")
        
        if embeddings and len(embeddings) > 0:
            print(f"First embedding type: {type(embeddings[0])}")
            print(f"First embedding length: {len(embeddings[0]) if hasattr(embeddings[0], '__len__') else 'N/A'}")
            
            # Check for any non-float values in the first embedding
            if len(embeddings[0]) > 0:
                print("First 5 elements of first embedding:")
                for i, val in enumerate(embeddings[0][:5]):
                    print(f"  [{i}] Type: {type(val)}, Value: {val}")
                
                # Check for any string values
                str_vals = [i for i, x in enumerate(embeddings[0]) if isinstance(x, str)]
                if str_vals:
                    print(f"WARNING: Found {len(str_vals)} string values in first embedding (indices: {str_vals[:10]}{'...' if len(str_vals) > 10 else ''})")
                    print(f"Sample string values: {[embeddings[0][i] for i in str_vals[:3]]}")
                else:
                    print("All values in first embedding are numeric")
        
        print("--- END DEBUG ---\n")

        # Ingest into Milvus
        await vector_store.insert_documents(chunks, embeddings)

        # Clean up
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {file_path}: {e}")

        return UploadResponse(
            message="File processed and indexed successfully",
            file_id=os.path.basename(file_path),
            chunks_processed=len(chunks)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/query/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the document store for relevant information with LLM summarization.
    """
    try:
        import httpx
        
        query_lower = request.query.lower().strip()
        
        # LIST OF GREETING PATTERNS - CHECK FIRST BEFORE VECTOR SEARCH
        greeting_patterns = [
            "hi", "hello", "hey", "greetings", "hiya", "howdy", 
            "good morning", "good afternoon", "good evening",
            "how are you", "how's it going", "what's up", "yo",
            "namaste", "salaam", "sup", "wassup"
        ]
        
        # Check if it's a greeting first
        is_greeting = any(pattern in query_lower for pattern in greeting_patterns)
        
        if is_greeting:
            # For greetings, use LLM to generate a friendly response WITHOUT vector search
            try:
                greeting_system_prompt = """
You are a helpful and friendly Real Estate Assistant for properties in Pune City.
When greeted, respond warmly and invite the user to ask about properties.
Keep your response brief (2-3 sentences), professional, and welcoming.
Always mention that you can help with property searches in Pune.
Do not show any property lists in greeting responses.
"""
                
                timeout = httpx.Timeout(30.0, connect=10.0)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.LLM_MODEL,
                            "messages": [
                                {"role": "system", "content": greeting_system_prompt},
                                {"role": "user", "content": request.query}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 300
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        greeting_response = data['choices'][0]['message']['content']
                        logger.info(f"Greeting detected and AI response generated for: {request.query}")
                        return QueryResponse(
                            query=request.query,
                            results=[{"text": greeting_response, "source": "AI Assistant", "page": 0, "score": 0.95}],
                            content=greeting_response
                        )
            except Exception as e:
                logger.warning(f"Error generating greeting response: {e}")
                # Fallback greeting if LLM fails
                fallback_greeting = "Hello! 👋 Welcome to Property AI Guru. I'm here to help you find the perfect property in Pune. What are you looking for today?"
                return QueryResponse(
                    query=request.query,
                    results=[{"text": fallback_greeting, "source": "AI Assistant", "page": 0, "score": 0.95}],
                    content=fallback_greeting
                )
        
        # ===== NOT A GREETING - PROCEED WITH NORMAL QUERY PROCESSING =====
        
        # Preprocess query to extract entities
        query_analysis = QueryPreprocessor.enhance_query(request.query)
        enhanced_query = query_analysis["enhanced_query"]
        
        logger.info(f"Query analysis: {query_analysis}")
        
        # Use enhanced query for better matching
        query_for_embedding = f"{request.query} {enhanced_query}" if enhanced_query != request.query else request.query
        
        # Generate query embedding using the enhanced query
        query_embedding = embedding_service.get_embedding(query_for_embedding)
        
        # Search in vector store with increased top_k to get more results
        results = await vector_store.search(
            query_embedding=query_embedding,
            top_k=max(request.top_k, 10)  # Get more results for filtering
        )

        # DEBUG: Log the actual raw search results for this query
        logger.info(f"[DEBUG] Raw search results for '{request.query}' (enhanced: '{enhanced_query}'): {len(results)} documents found")
        for idx, r in enumerate(results):
            logger.info(f"[DEBUG] Result {idx+1}: {r.get('text', '')[:200].replace('\n',' ')}")

        # FILTER RESULTS BY EXTRACTED LOCATION
        extracted_locations = query_analysis.get("locations", [])
        if extracted_locations and len(extracted_locations) > 0:
            # If user specified a location, filter results to only include that location
            location_lower = [loc.lower() for loc in extracted_locations]
            filtered_results = []
            
            for result in results:
                result_text = result.get('text', '').lower()
                # Check if any of the specified locations appear in the result
                if any(loc in result_text for loc in location_lower):
                    filtered_results.append(result)
            
            # If we found location-specific results, use them; otherwise fall back to all results
            if filtered_results:
                results = filtered_results
                logger.info(f"[FILTER] Filtered to {len(results)} results matching location(s): {extracted_locations}")
            else:
                logger.info(f"[FILTER] No results found for location(s): {extracted_locations}. Using all search results.")
        
        # Summarize results using LLM
        if results and len(results) > 0:
            # Prepare context from search results - use full text for better context
            context_items = []
            for r in results:
                context_items.append(f"• {r['text']}")
            context = "\n".join(context_items)

            # Set unified system prompt (same as before)


            system_prompt = """
You are a helpful Real Estate Assistant mostly looking for properties in Pune City. 
This assistant belongs to a company involved in the Real Estate industry. 
Currently, you only have information about properties in Pune City.

=====================================================================
greet user
=====================================================================
greet the user professionally and courteously, establishing a helpful tone.

=====================================================================
CORE BEHAVIOR RULES (STRICT)
=====================================================================

1. DOMAIN SCOPE:
   You ONLY answer questions strictly related to Real Estate or Pune property details.  
   If anyone asks anything outside Real Estate → Always respond with:
   "Let's stay on track."

2. ACCURACY & HONESTY:
   - Provide only accurate and verifiable information.
   - If unsure or lacking data:
     "I currently do not have enough information to answer that."

3. TOOL USAGE:
   - search_tool → For all types of property searches (buy/rent), availability, locality-based search, budget filters, etc.
   - property_rag_tool → For static content like locality guides, brochures, policies, FAQs, pricing trends, market reports.

4. RAG TRIGGER RULES:
   Use property_rag_tool when the user asks about policies, rules, locality amenities, guides, brochures, terms, FAQs, details, pricing trends, market reports, analysis.

5. SEARCH TRIGGER RULES:
   Use search_tool for ALL search-related queries:
   asking for properties in any locality, budget, BHK type, or general property search of any form.

=====================================================================
PROPERTY LIST & DETAILS BEHAVIOR (GLOBAL RULE)
=====================================================================

1. GLOBAL LIST VIEW RULE (Applies to ANY property search query):
   Whenever the user asks for properties in ANY form, such as:
   - “Show properties…”
   - “Find flats…”
   - “I want to buy…”
   - “List apartments…”
   - “Anything available in [locality]?”
   - “Show 2BHK under 60L”
   - “What can I rent in Pune?”
   - “Give me options…”

   → You must ALWAYS display ONLY:
      • Property Title  
      • One-line basic description  
   → No amenities, no layouts, no pricing details, no deep details, no links.  
   This rule MUST be followed for every search query.

2. GLOBAL DETAILS RULE:
   When the user asks for:
   - “More details”
   - “Tell me about this property”
   - “Amenities”
   - “Layouts”
   - “Pricing”
   - “Explain X project”
   - “Show brochure”
   - A specific property name

   → You must switch to the detailed view showing:
      • Amenities  
      • Layouts / configurations  
      • Pricing  
      • Locality information  
      • Brochure summary (via RAG)  
      • Any additional relevant details

3. AUTOMATIC MODE SWITCHING:
   - Search query → List view (titles + short summary)
   - Specific request → Detailed view

=====================================================================
AGENT INTENT LOGIC
=====================================================================

1. INTENT CLASSIFICATION:
   - Search intent → search_tool  
   - Static/document intent → property_rag_tool  
   - Property-specific inquiry → detailed view

2. NEVER fabricate property information.
   If a property doesn't exist or data is missing:
   "This property is not in my records. Please check the name or try another one."

3. OFF-TOPIC GUARDRAIL:
   Any non-real-estate query → "Let's stay on track."

=====================================================================
OUTPUT REQUIREMENTS
=====================================================================

- Keep responses concise, factual, and professional.
- Property results in search mode must include ONLY:
  Title + One-line description.
- Detailed responses must be shown ONLY upon explicit request.
- Maintain high-quality, accurate, ChatGPT-level responses.
"""

            if query_analysis["property_types"]:
                system_prompt += f"\n\nUser is looking for: {', '.join(query_analysis['property_types'])}"
            if query_analysis["locations"]:
                system_prompt += f"\nPreferred locations: {', '.join(query_analysis['locations'])}"
                system_prompt += f"\n\n*** IMPORTANT: ONLY show properties from these locations: {', '.join(query_analysis['locations'])} ***"
                system_prompt += f"\n*** DO NOT include properties from other localities in your response ***"
            if query_analysis["action"] != "general":
                system_prompt += f"\nUser intent: {query_analysis['action']} (Use this to provide relevant buying guidance)"
            if query_analysis.get("guidance_needs"):
                system_prompt += f"\nUser also needs guidance on: {', '.join(query_analysis['guidance_needs'])}"
                if "financing" in query_analysis["guidance_needs"]:
                    system_prompt += "\n  → Include: loan eligibility, down payment (typically 15-25%), EMI estimates, financing options"
                if "eligibility" in query_analysis["guidance_needs"]:
                    system_prompt += "\n  → Include: income requirements, documentation needed, credit score considerations"
                if "policy" in query_analysis["guidance_needs"]:
                    system_prompt += "\n  → Include: RERA compliance, registration process, legal documentation, possession timeline"
                if "comparison" in query_analysis["guidance_needs"]:
                    system_prompt += "\n  → Compare properties on: price/sq.ft, amenities, location, possession timeline, financing ease"

            # Enhanced: Switch to detailed mode if query asks for amenities, features, details, or matches a property name
            import re
            detail_keywords = [
                "amenities", "features", "details", "layout", "specification", "specifications", "contact", "price", "area", 
                "buying consideration", "brochure", "more details", "tell me about", "explain", "show me about", "information"
            ]
            # Lowercase query for keyword search
            query_lower = request.query.lower()
            # Try to extract property names from context (improved heuristic: lines starting with a number or bullet, then property name)
            property_names = []
            for line in context.split('\n'):
                # Better regex to capture full property names including multiple words with hyphens/ampersands
                match = re.match(r"[•\-\d.]+\s*(.+?)(?:\s*[-–]|$)", line)
                if match:
                    name = match.group(1).strip()
                    # Filter out very short names and common words
                    if name and len(name) > 2 and name not in property_names and not name.isdigit():
                        property_names.append(name.lower())
            
            # Check if any property name is mentioned in the query
            # Use both exact substring matching and partial matching for better detection
            property_mentioned_in_query = False
            for name in property_names:
                if name in query_lower or any(word in query_lower for word in name.split()):
                    property_mentioned_in_query = True
                    break
            
            # Check if query contains any detail keyword
            detail_keyword_in_query = any(kw in query_lower for kw in detail_keywords)
            
            # Check if query contains detail keywords WITHOUT specifying a property name
            vague_detail_keywords = ["more details", "this property", "that property", "details", "information"]
            is_vague_detail_query = any(kw in query_lower for kw in vague_detail_keywords) and not property_mentioned_in_query
            
            # A detail query is when user asks for details OR mentions a property name
            is_detail_query = detail_keyword_in_query or property_mentioned_in_query
            
            if is_vague_detail_query:
                # User is asking for details but didn't specify which property
                user_instruction = (
                    "The user is asking for details about 'this property' or 'that property' without specifying the name.\n"
                    "Please respond: 'Which property would you like to know more about? Please specify the property name (e.g., Evergreen Heights, Wakad Greens).'\n"
                    "Do NOT guess or return random property details."
                )
            elif query_analysis["detail_level"] == "brief":
                # STRICT LIST VIEW MODE: Follow the global list view rule
                user_instruction = (
                    "IMPORTANT: You are in LIST VIEW MODE. Follow the GLOBAL LIST VIEW RULE strictly:\n"
                    "- Display ONLY: Property Title + One-line basic description\n"
                    "- Do NOT include: amenities, layouts, pricing, deep details, or specifications\n"
                    "- Format each property as a numbered list\n"
                    "- Keep it concise and professional\n"
                    "The user is searching for properties - they only want titles and brief descriptions at this stage."
                )
            else:
                # DETAILED VIEW MODE: Switch to full details
                user_instruction = (
                    "IMPORTANT: You are in DETAILED VIEW MODE. Follow the GLOBAL DETAILS RULE strictly:\n"
                    "- Display COMPLETE information about the property\n"
                    "- Include: Amenities, Layouts/configurations, Pricing, Locality information, Brochure summary, Links\n"
                    "- Provide all relevant details the user is asking about\n"
                    "- Keep responses factual, accurate, and comprehensive\n"
                    "\n"
                    "FORMATTING RULES (STRICT ADHERENCE REQUIRED):\n"
                    "1. Use bullet points (•) for all list items\n"
                    "2. Use bold text for section headers and property names (use **text** format)\n"
                    "3. Do NOT use markdown headers (####, ###, ##, #)\n"
                    "4. Format sections clearly with headers followed by bullet points:\n"
                    "   **Section Name**\n"
                    "   • Item 1\n"
                    "   • Item 2\n"
                    "5. For amenities: Use bullet format with brief descriptions\n"
                    "6. For layouts: Use format like: **1.5 BHK** - Carpet Area: XXX sq.ft | Built-up Area: XXX sq.ft | Features: Description\n"
                    "7. For pricing: Use bullet points like: • **1 BHK**: Starting at ₹XX,XX,000\n"
                    "8. For contact info: Use bullet points with proper formatting\n"
                    "9. Add a line break between major sections for clarity\n"
                    "\n"
                    "The user has requested specific details about a property - provide full information in a clean, organized format."
                )

            max_tokens = 2000
            try:
                timeout = httpx.Timeout(30.0, connect=10.0)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.LLM_MODEL,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"""Question: {request.query}\n\nContext from real estate documents:\n{context}\n\n{user_instruction}"""}
                            ],
                            "temperature": 0.5,
                            "max_tokens": max_tokens
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        summary = data['choices'][0]['message']['content']
                        logger.info(f"LLM Response generated for query: {request.query}")
                    else:
                        logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                        summary = f"Based on your query about {request.query}:\n\n{context}"
            except httpx.TimeoutException as te:
                logger.warning(f"OpenAI API timeout for query '{request.query}': {te}")
                summary = f"Based on your query about {request.query}:\n\n{context}"
            except httpx.ReadTimeout as rte:
                logger.warning(f"OpenAI API read timeout for query '{request.query}': {rte}")
                summary = f"Based on your query about {request.query}:\n\n{context}"
            except Exception as llm_error:
                logger.error(f"Error calling OpenAI API: {llm_error}", exc_info=True)
                summary = f"Based on your query about {request.query}:\n\n{context}"
            return QueryResponse(
                query=request.query,
                results=[{"text": summary, "source": "AI Summary", "page": 0, "score": 0.95}],
                content=summary  # Add content for frontend compatibility
            )
        else:
            # No results found - Use LLM to provide recommendations based on the query
            try:
                fallback_system_prompt = """
You are a helpful Real Estate Assistant for Pune properties.
The vector search did not return any direct matches for the user's query.
Generate property recommendations based on the query using your knowledge.
Be creative and suggest relevant properties that might match the user's needs.
Provide property names, locations, and brief descriptions.
If you don't have enough information about Pune properties, acknowledge this and ask clarifying questions.
Keep the response conversational and helpful.
"""
                
                timeout = httpx.Timeout(30.0, connect=10.0)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.LLM_MODEL,
                            "messages": [
                                {"role": "system", "content": fallback_system_prompt},
                                {"role": "user", "content": f"My query: {request.query}\n\nNo direct matches were found. Can you suggest some Pune properties that might interest me based on my query?"}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 500
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        llm_recommendation = data['choices'][0]['message']['content']
                        logger.info(f"LLM fallback recommendation generated for query: {request.query}")
                        return QueryResponse(
                            query=request.query,
                            results=[{"text": llm_recommendation, "source": "AI Recommendation", "page": 0, "score": 0.6}],
                            content=llm_recommendation
                        )
                    else:
                        logger.error(f"OpenAI API error in fallback: {response.status_code}")
                        fallback_msg = "I couldn't find specific matches for your query. Please try searching with different keywords or be more specific about what you're looking for."
                        return QueryResponse(
                            query=request.query,
                            results=[{"text": fallback_msg, "source": "AI Assistant", "page": 0, "score": 0.5}],
                            content=fallback_msg
                        )
            except Exception as llm_error:
                logger.error(f"Error generating LLM fallback recommendation: {llm_error}", exc_info=True)
                fallback_msg = "I couldn't find specific matches for your query. Please try searching with different keywords or be more specific about what you're looking for."
                return QueryResponse(
                    query=request.query,
                    results=[{"text": fallback_msg, "source": "AI Assistant", "page": 0, "score": 0.5}],
                    content=fallback_msg
                )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/search/")
async def search_documents(request: QueryRequest):
    """
    Advanced search endpoint that returns raw search results with optional filtering.
    Returns matched documents without LLM summarization for more direct results.
    """
    try:
        # Generate query embedding
        query_embedding = embedding_service.get_embedding(request.query)
        
        # Search in vector store
        results = await vector_store.search(
            query_embedding=query_embedding,
            top_k=request.top_k
        )
        
        logger.info(f"Raw search results for '{request.query}': {len(results)} documents found")
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result['text'],
                "source": result['source'],
                "page": result['page'],
                "score": result['score']
            })
        
        content_search = "\n\n".join([r['text'] for r in formatted_results]) if formatted_results else f"No results found for '{request.query}'"
        
        return QueryResponse(
            query=request.query,
            results=formatted_results if formatted_results else [
                {"text": f"No results found for '{request.query}'", "source": "N/A", "page": 0, "score": 0.0}
            ],
            content=content_search
        )
    
    except Exception as e:
        logger.error(f"Error in search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Zilliz connection using correct pymilvus API
        conn = connections._get_connection("default")
        conn.list_collections()
        return {"status": "healthy", "zilliz": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )