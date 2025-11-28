"""
Tools for Real Estate Agents
- search_tool: Search property database/API
- property_rag_tool: RAG retrieval from property documents
"""
import logging
import json
from typing import List, Dict, Any, Optional
from services.llm_processor import get_default_llm_processor
from services.milvus_service import get_milvus_service

logger = logging.getLogger(__name__)


class PropertySearchTool:
    """
    Tool for searching properties in database/API
    Simulates property search functionality
    """
    
    def __init__(self):
        self.name = "search_tool"
        self.description = "Search for properties based on criteria like locality, price range, bedrooms, property type"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get OpenAI function calling tool definition"""
        return {
            "type": "function",
            "function": {
                "name": "search_properties",
                "description": "Search for buy/rent properties based on user criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "locality": {
                            "type": "string",
                            "description": "Locality/area name (e.g., Wakad, Baner, Hinjewadi)"
                        },
                        "transaction_type": {
                            "type": "string",
                            "enum": ["buy", "rent"],
                            "description": "Whether user wants to buy or rent"
                        },
                        "property_type": {
                            "type": "string",
                            "enum": ["apartment", "villa", "plot", "commercial"],
                            "description": "Type of property"
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price/rent in INR"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price/rent in INR"
                        },
                        "bedrooms": {
                            "type": "integer",
                            "description": "Number of bedrooms (1, 2, 3, etc.)"
                        },
                        "furnishing": {
                            "type": "string",
                            "enum": ["furnished", "semi-furnished", "unfurnished"],
                            "description": "Furnishing status"
                        }
                    },
                    "required": ["transaction_type"]
                }
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute property search
        In production, this would query a real database/API
        """
        try:
            locality = kwargs.get("locality", "").lower()
            transaction_type = kwargs.get("transaction_type", "buy")
            property_type = kwargs.get("property_type")
            min_price = kwargs.get("min_price")
            max_price = kwargs.get("max_price")
            bedrooms = kwargs.get("bedrooms")
            
            # Mock property database
            mock_properties = self._get_mock_properties(locality, transaction_type)
            
            # Filter based on criteria
            filtered_properties = []
            for prop in mock_properties:
                # Price filter
                if min_price and prop["price"] < min_price:
                    continue
                if max_price and prop["price"] > max_price:
                    continue
                
                # Bedroom filter
                if bedrooms and prop["bedrooms"] != bedrooms:
                    continue
                
                # Property type filter
                if property_type and prop["type"].lower() != property_type.lower():
                    continue
                
                filtered_properties.append(prop)
            
            return {
                "success": True,
                "count": len(filtered_properties),
                "properties": filtered_properties[:10],  # Limit to 10 results
                "filters_applied": kwargs
            }
            
        except Exception as e:
            logger.error(f"Error in property search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "properties": []
            }
    
    def _get_mock_properties(self, locality: str, transaction_type: str) -> List[Dict[str, Any]]:
        """Get mock property data"""
        # Sample mock data - in production, this would be from database
        all_properties = [
            {
                "id": "PROP-WAK-001",
                "name": "Evergreen Heights",
                "locality": "Wakad",
                "type": "Apartment",
                "bedrooms": 2,
                "price": 7650000 if transaction_type == "buy" else 25000,
                "area_sqft": 920,
                "description": "2 BHK in Evergreen Heights with excellent amenities",
                "contact": "+91 98220 88991"
            },
            {
                "id": "PROP-WAK-002",
                "name": "Evergreen Heights",
                "locality": "Wakad",
                "type": "Apartment",
                "bedrooms": 3,
                "price": 9980000 if transaction_type == "buy" else 35000,
                "area_sqft": 1200,
                "description": "Spacious 3 BHK corner residence with dual balconies",
                "contact": "+91 98220 88991"
            },
            {
                "id": "PROP-BAN-001",
                "name": "Summit Residency",
                "locality": "Baner",
                "type": "Apartment",
                "bedrooms": 2,
                "price": 8500000 if transaction_type == "buy" else 28000,
                "area_sqft": 950,
                "description": "Modern 2 BHK in prime Baner location",
                "contact": "+91 98765 43210"
            },
            {
                "id": "PROP-HIN-001",
                "name": "TechVista Towers",
                "locality": "Hinjewadi",
                "type": "Apartment",
                "bedrooms": 2,
                "price": 6850000 if transaction_type == "buy" else 22000,
                "area_sqft": 860,
                "description": "IT professional friendly 2 BHK near tech parks",
                "contact": "+91 98900 12345"
            },
            {
                "id": "PROP-KHA-001",
                "name": "Skyline Orchid",
                "locality": "Kharadi",
                "type": "Apartment",
                "bedrooms": 2,
                "price": 7850000 if transaction_type == "buy" else 26000,
                "area_sqft": 940,
                "description": "Premium 2 BHK near IT hubs",
                "contact": "+91 98330 77221"
            }
        ]
        
        # Filter by locality if specified
        if locality:
            return [p for p in all_properties if locality in p["locality"].lower()]
        
        return all_properties


class PropertyRAGTool:
    """
    Tool for RAG retrieval from property documents
    Retrieves relevant information from Milvus vector database
    """
    
    def __init__(self):
        self.name = "property_rag_tool"
        self.description = "Retrieve information from property brochures, locality guides, and market reports"
        self.llm_processor = get_default_llm_processor()
        self.milvus_service = get_milvus_service()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get OpenAI function calling tool definition"""
        return {
            "type": "function",
            "function": {
                "name": "query_property_knowledge",
                "description": "Query property knowledge base for information about localities, amenities, market trends, property features",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or information needed from property documents"
                        },
                        "locality": {
                            "type": "string",
                            "description": "Optional: filter by specific locality"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of relevant documents to retrieve (default: 5)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def execute(self, query: str, locality: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Execute RAG retrieval and generate answer
        
        Args:
            query: User's question
            locality: Optional locality filter
            top_k: Number of documents to retrieve
        
        Returns:
            Answer with retrieved context
        """
        try:
            # First, check if query is real estate related using LLM
            relevance_check = [
                {
                    "role": "system",
                    "content": "You are a query classifier. Respond with only 'YES' if the query is related to real estate, properties, buying, renting, localities, amenities, or housing. Respond with only 'NO' for greetings, personal introductions, or non-real estate topics."
                },
                {
                    "role": "user",
                    "content": f"Is this query related to real estate? Query: {query}"
                }
            ]
            
            relevance_response = self.llm_processor.generate_completion(relevance_check)
            is_relevant = "YES" in relevance_response["content"].upper()
            
            if not is_relevant:
                return {
                    "success": True,
                    "answer": "Let's stay on track. If you have any questions related to real estate in Pune, feel free to ask!",
                    "retrieved_documents": [],
                    "sources": [],
                    "query": query
                }
            
            # Generate query embedding
            query_embedding = self.llm_processor.generate_embedding(query)
            
            # Build filter expression if locality specified
            filters = None
            if locality:
                filters = f'locality == "{locality}"'
            
            # Search Milvus
            results = self.milvus_service.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filters
            )
            
            if not results:
                return {
                    "success": True,
                    "answer": "I couldn't find relevant information in the knowledge base for your query.",
                    "retrieved_documents": [],
                    "sources": []
                }
            
            # Prepare context from retrieved documents
            context_parts = []
            sources = []
            
            for i, result in enumerate(results):
                context_parts.append(f"[Document {i+1}] {result['text']}")
                sources.append({
                    "filename": result["filename"],
                    "locality": result["locality"],
                    "property_type": result["property_type"],
                    "relevance_score": result["score"]
                })
            
            context = "\n\n".join(context_parts)
            
            # Generate answer using LLM
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful Real Estate Assistant mostly looking for properties in Pune City. It is a company involved in Real Estate industry. If any one ask you any question other than Real Estate, you will reply with 'Let's stay on track'. When providing information, ensure it is accurate and relevant to real estate. Also make sure to add appropriate links to their products for more information. If you are unsure about an answer, it's better to admit it than to provide incorrect information. Also, keep your answers concise and to the point. Currently you only have information about properties in Pune city.

se the provided context from property documents to answer the user's question accurately and helpfully.
If the context contains relevant information, provide a detailed answer based on it.
If the context doesn't contain sufficient information, say so clearly.
Always cite which documents/sources your answer is based on. strictly retrive data from ingessted pdf don't add inputs from your side"""
                },
                {
                    "role": "user",
                    "content": f"""Context from property documents:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above."""
                }
            ]
            
            response = self.llm_processor.generate_completion(messages)
            
            return {
                "success": True,
                "answer": response["content"],
                "retrieved_documents": results,
                "sources": sources,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error in RAG retrieval: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error retrieving information: {str(e)}",
                "retrieved_documents": []
            }


# Tool instances
def get_search_tool() -> PropertySearchTool:
    """Get property search tool instance"""
    return PropertySearchTool()


def get_rag_tool() -> PropertyRAGTool:
    """Get property RAG tool instance"""
    return PropertyRAGTool()
