#!/usr/bin/env python3
"""
Script to retrieve and display all properties in Pune in a simple, readable format
"""
import asyncio
import sys
from config import settings
from vector_store import MilvusStore
from embedding_service import EmbeddingService

async def get_all_properties():
    """Retrieve all Pune properties and display them."""
    
    print("\n" + "="*80)
    print("ALL PROPERTIES IN PUNE - REAL ESTATE LISTINGS")
    print("="*80 + "\n")
    
    try:
        # Initialize services
        vector_store = MilvusStore()
        embedding_service = EmbeddingService()
        
        print(f"Total documents in database: {vector_store.collection.num_entities}\n")
        
        # Search queries to get comprehensive property listings
        search_queries = [
            "properties in Pune",
            "2 BHK apartments in Pune",
            "3 BHK apartments in Pune",
            "1.5 BHK apartments in Pune",
            "Viman Nagar properties",
            "Wakad properties",
            "Kharadi properties",
            "Hinjewadi properties",
            "Baner properties",
            "Kalyani Nagar properties",
            "residential apartments Pune",
            "villas for sale in Pune",
            "commercial property Pune",
        ]
        
        all_results = []
        seen_texts = set()
        
        for query in search_queries:
            # Generate embedding
            query_embedding = embedding_service.get_embedding(query)
            
            # Search with higher top_k to get more results
            results = await vector_store.search(
                query_embedding=query_embedding,
                top_k=10
            )
            
            # Add unique results
            for result in results:
                text_key = result['text'][:100]  # Use first 100 chars as key
                if text_key not in seen_texts:
                    all_results.append(result)
                    seen_texts.add(text_key)
        
        # Remove duplicates and sort by score
        all_results = sorted(all_results, key=lambda x: x['score'], reverse=True)
        
        # Display properties
        print(f"FOUND {len(all_results)} UNIQUE PROPERTY LISTINGS\n")
        print("-"*80 + "\n")
        
        for idx, result in enumerate(all_results[:50], 1):  # Show top 50
            print(f"{idx}. PROPERTY LISTING")
            print(f"   Source: {result['source']}")
            print(f"   Relevance Score: {result['score']:.2f}")
            print(f"   Details:")
            print(f"   {result['text'][:300]}...")
            print()
        
        print("-"*80)
        print(f"\nTotal Properties Displayed: {min(50, len(all_results))}")
        print(f"Total Properties Available: {len(all_results)}")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(get_all_properties())
