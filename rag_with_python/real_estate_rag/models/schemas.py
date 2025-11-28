"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class AgentType(str, Enum):
    BUY = "buy"
    RENT = "rent"
    DETAILS = "details"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class PropertySearchRequest(BaseModel):
    query: str = Field(..., description="User query for property search")
    locality: Optional[str] = Field(None, description="Specific locality filter")
    property_type: Optional[str] = Field(None, description="Type of property (apartment, villa, etc.)")
    min_price: Optional[float] = Field(None, description="Minimum price filter")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")


class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="User question for RAG system")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation for context")
    max_history: int = Field(10, description="Maximum number of previous messages to consider")


class AgentRequest(BaseModel):
    agent_type: AgentType = Field(..., description="Type of agent to use")
    message: str = Field(..., description="User message to the agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the agent")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation for context")


class PDFIngestionRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the PDF")


class DocumentChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class RAGResult(BaseModel):
    query: str
    answer: str
    retrieved_documents: List[Dict[str, Any]]
    confidence_score: Optional[float] = None


class AgentResponse(BaseModel):
    agent_type: str
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class PropertySearchResult(BaseModel):
    properties: List[Dict[str, Any]]
    total_count: int
    filters_applied: Dict[str, Any]


class IngestionResponse(BaseModel):
    success: bool
    filename: str
    chunks_created: int
    vectors_inserted: int
    message: str
