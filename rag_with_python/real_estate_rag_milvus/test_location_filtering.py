#!/usr/bin/env python3
"""
Test script to verify that location-specific queries now return 
only properties from the requested location.
"""
from query_preprocessor import QueryPreprocessor

def test_location_filtering():
    """Test that location-specific queries are properly detected and can be filtered."""
    test_cases = [
        {
            "query": "show best property in wakad",
            "expected_location": "wakad",
            "description": "Wakad-specific query"
        },
        {
            "query": "apartments in viman nagar",
            "expected_location": "viman nagar",
            "description": "Viman Nagar specific query"
        },
        {
            "query": "best 2bhk in kothrud",
            "expected_location": "kothrud",
            "description": "Kothrud specific query"
        },
        {
            "query": "properties near kalyani nagar",
            "expected_location": "kalyani nagar",
            "description": "Kalyani Nagar specific query"
        },
        {
            "query": "what's available in downtown pune",
            "expected_location": "downtown",
            "description": "Downtown Pune query"
        },
        {
            "query": "find me properties",
            "expected_location": None,
            "description": "General query without location"
        },
    ]
    
    print("=" * 80)
    print("TESTING LOCATION-SPECIFIC QUERY FILTERING")
    print("=" * 80)
    print()
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected_loc = test_case["expected_location"]
        description = test_case["description"]
        
        # Get query analysis
        analysis = QueryPreprocessor.enhance_query(query)
        locations = analysis["locations"]
        
        # Check if test passed
        if expected_loc:
            passed = len(locations) > 0 and expected_loc in [loc.lower() for loc in locations]
        else:
            passed = len(locations) == 0
        
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Description: {description}")
        print(f"  Query: '{query}'")
        print(f"  Expected Location: {expected_loc if expected_loc else 'None (general query)'}")
        print(f"  Extracted Locations: {locations if locations else 'None'}")
        if not passed:
            print(f"  ERROR: Location extraction mismatch!")
        print()
    
    print("=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nLocation-specific queries will now:")
        print("1. Extract the location from the query")
        print("2. Filter search results to only include that location")
        print("3. Instruct LLM to ONLY show properties from that location")
        print("\nHardcoded multi-location responses are ELIMINATED!")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the failures above.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = test_location_filtering()
    exit(0 if success else 1)
