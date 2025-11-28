"""
Test script to diagnose vector search issues
"""
import asyncio
import sys
from config import settings
from vector_store import MilvusStore
from embedding_service import EmbeddingService

async def test_search():
    """Test if search is working correctly."""
    
    print("=" * 80)
    print("VECTOR SEARCH DIAGNOSTIC TEST")
    print("=" * 80)
    
    try:
        # Initialize services
        vector_store = MilvusStore()
        embedding_service = EmbeddingService()
        
        # Test queries
        test_queries = [
            "properties in Viman Nagar",
            "Find 2 BHK apartments",
            "Properties in Pune",
            "Villas for sale",
            "Budget-friendly rentals",
            "Aurora Crest",
            "Viman Nagar",
            "2 BHK",
            "apartments",
            "Riya Kulkarni"
        ]
        
        print(f"\nCollection: {vector_store.collection_name}")
        print(f"Collection loaded: {vector_store.collection.num_entities}")
        print(f"Total documents in collection: {vector_store.collection.num_entities}\n")
        
        for query in test_queries:
            print("-" * 80)
            print(f"QUERY: '{query}'")
            print("-" * 80)
            
            # Generate embedding
            query_embedding = embedding_service.get_embedding(query)
            print(f"Query embedding generated (dim: {len(query_embedding)})")
            print(f"Embedding sample (first 5 values): {query_embedding[:5]}\n")
            
            # Search
            results = await vector_store.search(
                query_embedding=query_embedding,
                top_k=3
            )
            
            print(f"Found {len(results)} results:\n")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"  Score: {result['score']:.4f}")
                    print(f"  Source: {result['source']}")
                    print(f"  Text: {result['text'][:200]}...")
                    print()
            else:
                print("❌ NO RESULTS FOUND")
            
            print()
        
        print("=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_search())
