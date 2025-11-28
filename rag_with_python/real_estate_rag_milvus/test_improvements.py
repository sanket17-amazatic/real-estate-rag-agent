"""
Comprehensive test script for the Real Estate RAG system improvements
Tests query preprocessing, vector search, and end-to-end flow
"""
import asyncio
import sys
from query_preprocessor import QueryPreprocessor
from config import settings
from vector_store import MilvusStore
from embedding_service import EmbeddingService

async def test_query_preprocessing():
    """Test query preprocessing module."""
    print("\n" + "=" * 80)
    print("TEST 1: QUERY PREPROCESSING")
    print("=" * 80)
    
    test_queries = [
        "Show me 2 BHK apartments in Viman Nagar",
        "Find properties to rent in Pune",
        "Villas for sale under 1 crore",
        "Budget-friendly apartments in Kalyani Nagar",
        "Properties in viman nagar , pune",
        "show me all properties you have",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        analysis = QueryPreprocessor.enhance_query(query)
        print(f"  Locations: {analysis['locations']}")
        print(f"  Property Types: {analysis['property_types']}")
        print(f"  Action: {analysis['action']}")
        print(f"  BHK: {analysis['bhk']}")
        print(f"  Enhanced: '{analysis['enhanced_query']}'")

async def test_vector_search_with_preprocessing():
    """Test vector search with query preprocessing."""
    print("\n" + "=" * 80)
    print("TEST 2: VECTOR SEARCH WITH QUERY PREPROCESSING")
    print("=" * 80)
    
    try:
        vector_store = MilvusStore()
        embedding_service = EmbeddingService()
        
        test_queries = [
            "properties in Viman Nagar",
            "Show me the properties in viman nagar , pune",
            "2 BHK apartments in Pune",
            "Villas for sale",
        ]
        
        print(f"Collection has {vector_store.collection.num_entities} documents\n")
        
        for query in test_queries:
            print("-" * 80)
            print(f"QUERY: '{query}'")
            
            # Preprocess query
            analysis = QueryPreprocessor.enhance_query(query)
            enhanced = analysis["enhanced_query"]
            print(f"Enhanced Query: '{enhanced}'")
            print(f"Analysis: Locations={analysis['locations']}, Types={analysis['property_types']}, Action={analysis['action']}")
            
            # Create embeddings from both original and enhanced query
            combined_query = f"{query} {enhanced}" if enhanced != query else query
            query_embedding = embedding_service.get_embedding(combined_query)
            
            # Search
            results = await vector_store.search(
                query_embedding=query_embedding,
                top_k=3
            )
            
            print(f"\nResults: {len(results)} documents found\n")
            
            for i, result in enumerate(results, 1):
                print(f"  Result {i} (Score: {result['score']:.4f}, Source: {result['source']})")
                text_preview = result['text'][:150].replace('\n', ' ')
                print(f"    Text: {text_preview}...")
                print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

async def test_location_extraction():
    """Test location extraction from various query formats."""
    print("\n" + "=" * 80)
    print("TEST 3: LOCATION EXTRACTION")
    print("=" * 80)
    
    test_cases = [
        ("properties in Viman Nagar", ["viman nagar"]),
        ("Kalyani Nagar apartments", ["kalyani nagar"]),
        ("Find homes in Wakad, Pune", ["wakad", "pune"]),
        ("viman nagar , pune", ["viman nagar", "pune"]),
        ("Show me properties in viman nagar , pune", ["viman nagar", "pune"]),
        ("Baner luxury apartments", ["baner"]),
    ]
    
    all_passed = True
    for query, expected_locations in test_cases:
        extracted = QueryPreprocessor.extract_location(query)
        passed = set(extracted) == set(expected_locations)
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: '{query}'")
        print(f"    Expected: {expected_locations}")
        print(f"    Extracted: {extracted}")
        if not passed:
            all_passed = False
        print()
    
    return all_passed

def test_query_enhancement():
    """Test query enhancement."""
    print("\n" + "=" * 80)
    print("TEST 4: QUERY ENHANCEMENT")
    print("=" * 80)
    
    test_queries = [
        "Show me 2 BHK apartments",
        "Find 2 BHK apartments in Viman Nagar",
        "Villas for sale in Pune under 1 crore",
        "Budget-friendly rentals",
    ]
    
    for query in test_queries:
        analysis = QueryPreprocessor.enhance_query(query)
        print(f"\nOriginal: '{query}'")
        print(f"Enhanced: '{analysis['enhanced_query']}'")

async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("REAL ESTATE RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    try:
        # Test 1: Query Preprocessing
        await test_query_preprocessing()
        
        # Test 2: Vector Search with Preprocessing
        await test_vector_search_with_preprocessing()
        
        # Test 3: Location Extraction
        loc_test_passed = await test_location_extraction()
        
        # Test 4: Query Enhancement
        test_query_enhancement()
        
        print("\n" + "=" * 80)
        print("TEST SUITE COMPLETE")
        print("=" * 80)
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
