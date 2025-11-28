"""
Query preprocessing utilities for better location and property type extraction
"""
import re
from typing import Dict, List, Tuple

class QueryPreprocessor:
    """Extract and normalize location and property type information from queries."""
    
    # Known locations in the datasets
    LOCATIONS = {
        "viman nagar": ["viman nagar", "viman"],
        "kalyani nagar": ["kalyani nagar", "kalyani"],
        "wakad": ["wakad"],
        "pune": ["pune", "pmc"],
        "baner": ["baner"],
        "kothrud": ["kothrud"],
        "downtown": ["downtown"],
        "beachside": ["beachside"],
        "suburb": ["suburb"],
        "midtown": ["midtown"],
    }
    
    # Property types
    PROPERTY_TYPES = {
        "apartment": ["apartment", "apt", "flat", "bhk", "bhk apartment"],
        "villa": ["villa", "villas"],
        "house": ["house", "bungalow"],
        "residential": ["residential", "home", "residence"],
    }
    
    # Actions (rent/buy/sell)
    ACTIONS = {
        "rent": ["rent", "rental", "lease", "to rent"],
        "buy": ["buy", "purchase", "sale", "for sale", "list all", "show me"],
        "sell": ["sell", "sale"],
    }
    
    # Guidance keywords (financing, eligibility, etc.)
    GUIDANCE_NEEDS = {
        "financing": ["loan", "mortgage", "emi", "down payment", "financing", "home loan", "housing finance"],
        "eligibility": ["eligible", "eligibility", "qualify", "requirements", "can i afford"],
        "policy": ["policy", "regulation", "rera", "documentation", "process", "procedure", "approval"],
        "comparison": ["compare", "vs", "versus", "difference", "which is better", "recommend"],
    }
    
    # Detail level keywords (brief vs detailed)
    DETAIL_KEYWORDS = {
        "brief": ["list", "show me", "list all", "quick", "summary", "overview", "brief"],
        "detailed": ["details", "about", "tell me more", "information", "complete", "full", "all details", "specifications", "specs", "amenities", "features"],
    }
    
    @classmethod
    def extract_location(cls, query: str) -> List[str]:
        """Extract location names from query."""
        query_lower = query.lower()
        locations = []
        
        for location_key, aliases in cls.LOCATIONS.items():
            for alias in aliases:
                if alias in query_lower:
                    if location_key not in locations:
                        locations.append(location_key)
                    break
        
        return locations
    
    @classmethod
    def extract_property_types(cls, query: str) -> List[str]:
        """Extract property types from query."""
        query_lower = query.lower()
        types = []
        
        for ptype_key, aliases in cls.PROPERTY_TYPES.items():
            for alias in aliases:
                if alias in query_lower:
                    if ptype_key not in types:
                        types.append(ptype_key)
                    break
        
        return types
    
    @classmethod
    def extract_action(cls, query: str) -> str:
        """Extract buy/rent/sell action from query."""
        query_lower = query.lower()
        
        for action_key, aliases in cls.ACTIONS.items():
            for alias in aliases:
                if alias in query_lower:
                    return action_key
        
        return "general"  # Default action
    
    @classmethod
    def extract_guidance_needs(cls, query: str) -> List[str]:
        """Extract guidance topics (financing, eligibility, policy, comparison)."""
        query_lower = query.lower()
        needs = []
        
        for guidance_key, aliases in cls.GUIDANCE_NEEDS.items():
            for alias in aliases:
                if alias in query_lower:
                    if guidance_key not in needs:
                        needs.append(guidance_key)
                    break
        
        return needs
    
    @classmethod
    def detect_detail_level(cls, query: str) -> str:
        """Detect if user wants brief summary or detailed information.
        Returns: 'brief' or 'detailed' (default: 'brief' for listings)"""
        query_lower = query.lower()
        
        # Budget queries should always be detailed - user wants recommendations and analysis
        if any(word in query_lower for word in ["budget", "lakh", "crore", "price", "cost", "afford", "can i buy"]):
            return "detailed"
        
        # Check for detailed keywords
        for keyword in cls.DETAIL_KEYWORDS["detailed"]:
            if keyword in query_lower:
                return "detailed"
        
        # Check for brief keywords
        for keyword in cls.DETAIL_KEYWORDS["brief"]:
            if keyword in query_lower:
                return "brief"
        
        # Default: if asking to "show" or "list" properties, return brief
        if any(word in query_lower for word in ["show", "list", "find", "get"]):
            return "brief"
        
        # Default: if asking about specific property or details, return detailed
        if any(word in query_lower for word in ["tell", "what", "which", "why"]):
            return "detailed"
        
        return "brief"  # Default to brief for property listings
    
    @classmethod
    def extract_bhk(cls, query: str) -> str:
        """Extract BHK specification from query."""
        # Match patterns like "2 BHK", "3-BHK", "1.5bhk", etc.
        match = re.search(r'(\d+\.?\d*)\s*-?bhk', query.lower())
        if match:
            return match.group(1) + " BHK"
        return None
    
    @classmethod
    def extract_price_range(cls, query: str) -> Tuple[float, float]:
        """Extract price range from query."""
        # Match patterns like "under 50 lakh", "between 30-50 lakh", etc.
        query_lower = query.lower()
        
        # Look for numbers followed by lakh/crore
        numbers = re.findall(r'(\d+\.?\d*)\s*(lakh|crore)', query_lower)
        
        if not numbers:
            return None, None
        
        prices = []
        for num_str, unit in numbers:
            num = float(num_str)
            if unit == "crore":
                num *= 100  # Convert crore to lakh
            prices.append(num)
        
        if prices:
            return min(prices), max(prices)
        
        return None, None
    
    @classmethod
    def enhance_query(cls, query: str) -> Dict[str, any]:
        """
        Analyze query and return enhanced search parameters.
        Returns a dictionary with extracted information.
        """
        return {
            "original_query": query,
            "locations": cls.extract_location(query),
            "property_types": cls.extract_property_types(query),
            "action": cls.extract_action(query),
            "guidance_needs": cls.extract_guidance_needs(query),
            "detail_level": cls.detect_detail_level(query),
            "bhk": cls.extract_bhk(query),
            "price_range": cls.extract_price_range(query),
            "enhanced_query": cls.build_enhanced_query(query)
        }
    
    @classmethod
    def build_enhanced_query(cls, query: str) -> str:
        """Build an enhanced query string for better semantic matching."""
        parts = []
        
        locations = cls.extract_location(query)
        property_types = cls.extract_property_types(query)
        action = cls.extract_action(query)
        bhk = cls.extract_bhk(query)
        
        if bhk:
            parts.append(f"{bhk} properties")
        
        if property_types:
            parts.extend(property_types)
        
        if action != "general":
            parts.append(f"for {action}")
        
        if locations:
            parts.append(f"in {', '.join(locations)}")
        
        enhanced = " ".join(parts) if parts else query
        
        return enhanced if enhanced != query else query


# Example usage:
if __name__ == "__main__":
    test_queries = [
        "Show me 2 BHK apartments in Viman Nagar",
        "Find properties to rent in Pune",
        "Villas for sale under 1 crore",
        "Budget-friendly apartments in Kalyani Nagar",
    ]
    
    for query in test_queries:
        result = QueryPreprocessor.enhance_query(query)
        print(f"\nQuery: {query}")
        print(f"Enhanced Analysis: {result}")
