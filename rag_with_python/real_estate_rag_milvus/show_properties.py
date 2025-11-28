#!/usr/bin/env python3
"""
Clean property listing display for Pune real estate
"""
import asyncio
import sys
from config import settings
from vector_store import MilvusStore
from embedding_service import EmbeddingService

async def get_pune_properties():
    """Retrieve and display Pune properties in a simple format."""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PROPERTIES FOR SALE IN PUNE" + " "*31 + "║")
    print("║" + " "*15 + "Welcome Apurv! Here are all available listings" + " "*20 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    try:
        # Initialize services
        vector_store = MilvusStore()
        embedding_service = EmbeddingService()
        
        # Get properties with location keywords
        search_queries = [
            "properties in Pune",
            "2 BHK apartments",
            "3 BHK apartments", 
            "1.5 BHK apartments",
            "Viman Nagar",
            "Wakad",
            "Kharadi",
            "Aurora Crest",
            "Evergreen Heights",
        ]
        
        all_results = []
        seen_texts = set()
        
        # Suppress debug output
        import io
        import contextlib
        
        for query in search_queries:
            with contextlib.redirect_stdout(io.StringIO()):
                query_embedding = embedding_service.get_embedding(query)
                results = await vector_store.search(
                    query_embedding=query_embedding,
                    top_k=15
                )
            
            for result in results:
                text_key = result['text'][:100]
                if text_key not in seen_texts:
                    all_results.append(result)
                    seen_texts.add(text_key)
        
        all_results = sorted(all_results, key=lambda x: x['score'], reverse=True)
        
        print(f"📍 TOTAL LISTINGS AVAILABLE: {len(all_results)} properties\n")
        print("─" * 80)
        
        # Display properties
        for idx, result in enumerate(all_results, 1):
            # Clean up the text
            text = result['text'].replace('±', '-').strip()
            
            # Extract key info
            lines = text.split('\n')
            summary = ' '.join([line.strip() for line in lines if line.strip()])[:400]
            
            print(f"\n📌 PROPERTY {idx}")
            print(f"   {summary}...")
            print()
        
        print("─" * 80)
        print(f"\n✓ Total Properties Listed: {len(all_results)}")
        print("\n" + "="*80)
        print("For more details about any property, please ask me directly!")
        print("Example: 'Show me details about Aurora Crest' or '2 BHK in Viman Nagar'")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(get_pune_properties())
