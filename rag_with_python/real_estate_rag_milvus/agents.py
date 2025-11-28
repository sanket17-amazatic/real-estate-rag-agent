"""
Agent and Tool interfaces/classes for Real Estate RAG system.
"""
from typing import Any, Dict, Optional, List


# Mock property API
class MockPropertyAPI:
    """A mock property API for search and booking flows."""
    def __init__(self):
        # Example property data
        self.properties = [
            {"id": 1, "type": "apartment", "action": "buy", "location": "Downtown", "price": 120000, "bedrooms": 2},
            {"id": 2, "type": "house", "action": "rent", "location": "Suburb", "price": 1500, "bedrooms": 3},
            {"id": 3, "type": "apartment", "action": "rent", "location": "Downtown", "price": 1800, "bedrooms": 2},
            {"id": 4, "type": "villa", "action": "buy", "location": "Beachside", "price": 350000, "bedrooms": 4},
            {"id": 5, "type": "apartment", "action": "buy", "location": "Midtown", "price": 95000, "bedrooms": 1},
        ]

    def search(self, action: str = None, location: str = None, min_price: int = None, max_price: int = None, bedrooms: int = None) -> List[Dict[str, Any]]:
        results = self.properties
        if action:
            results = [p for p in results if p["action"] == action]
        if location:
            results = [p for p in results if location.lower() in p["location"].lower()]
        if min_price:
            results = [p for p in results if p["price"] >= min_price]
        if max_price:
            results = [p for p in results if p["price"] <= max_price]
        if bedrooms:
            results = [p for p in results if p["bedrooms"] == bedrooms]
        return results

# Tool interfaces
class SearchTool:
    """Tool to query property API (mock implementation)."""
    def __init__(self, property_api: MockPropertyAPI):
        self.property_api = property_api

    def search(self, query: str) -> Dict[str, Any]:
        # Very basic query parsing for demo purposes
        q = query.lower()
        action = None
        if "buy" in q:
            action = "buy"
        elif "rent" in q:
            action = "rent"
        location = None
        for loc in ["downtown", "suburb", "beachside", "midtown"]:
            if loc in q:
                location = loc.capitalize()
        # Optionally parse price/bedrooms from query (not implemented here)
        results = self.property_api.search(action=action, location=location)
        return {"results": results, "query": query}

class PropertyRAGTool:
    """Retriever over property brochures, locality guides, market reports."""
    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        # TODO: Integrate with Milvus retriever
        return {"result": f"Mock RAG result for: {query}"}

# Agent base class
class BaseAgent:
    def __init__(self, name: str, search_tool: SearchTool, rag_tool: PropertyRAGTool):
        self.name = name
        self.search_tool = search_tool
        self.rag_tool = rag_tool

    def handle(self, query: str) -> Dict[str, Any]:
        raise NotImplementedError

# BuyAgent
class BuyAgent(BaseAgent):
    def handle(self, query: str) -> Dict[str, Any]:
        # Example: Use search_tool for transactional, rag_tool for static
        if "buy" in query.lower():
            return self.search_tool.search(query)
        return self.rag_tool.retrieve(query)

# RentAgent
class RentAgent(BaseAgent):
    def handle(self, query: str) -> Dict[str, Any]:
        if "rent" in query.lower():
            return self.search_tool.search(query)
        return self.rag_tool.retrieve(query)

# PropertyDetailsAgent
class PropertyDetailsAgent(BaseAgent):
    def handle(self, query: str) -> Dict[str, Any]:
        # Use RAG for details queries
        return self.rag_tool.retrieve(query)

# Orchestrator
class Orchestrator:
    def __init__(self, buy_agent: BuyAgent, rent_agent: RentAgent, details_agent: PropertyDetailsAgent):
        self.buy_agent = buy_agent
        self.rent_agent = rent_agent
        self.details_agent = details_agent

    def route(self, query: str) -> Dict[str, Any]:
        # Simple rule-based intent detection
        q = query.lower()
        if any(word in q for word in ["buy", "purchase"]):
            return self.buy_agent.handle(query)
        elif any(word in q for word in ["rent", "lease"]):
            return self.rent_agent.handle(query)
        elif any(word in q for word in ["details", "brochure", "guide", "amenities", "policy", "rules", "faq", "manual", "terms"]):
            return self.details_agent.handle(query)
        else:
            # Default to details agent (RAG)
            return self.details_agent.handle(query)