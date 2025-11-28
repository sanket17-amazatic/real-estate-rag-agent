#!/usr/bin/env python3
"""
Test script to verify that budget queries now trigger LLM responses
instead of hardcoded list view responses.
"""
from query_preprocessor import QueryPreprocessor

def test_budget_queries():
    """Test that budget queries are detected as 'detailed' level."""
    test_cases = [
        {
            "query": "my budget is 50 lakh",
            "expected_detail_level": "detailed",
            "description": "Budget query with rupees in lakh"
        },
        {
            "query": "I have budget of 1 crore",
            "expected_detail_level": "detailed",
            "description": "Budget query with rupees in crore"
        },
        {
            "query": "what can I afford with 75 lakh",
            "expected_detail_level": "detailed",
            "description": "Affordability query"
        },
        {
            "query": "show properties under 50 lakh",
            "expected_detail_level": "detailed",
            "description": "Price constraint query - should still be detailed"
        },
        {
            "query": "price range is 30-60 lakh",
            "expected_detail_level": "detailed",
            "description": "Price range specification"
        },
        {
            "query": "list all 2bhk apartments",
            "expected_detail_level": "brief",
            "description": "Simple list query - should remain brief"
        },
        {
            "query": "show me apartments in viman nagar",
            "expected_detail_level": "brief",
            "description": "Location-based list query - should remain brief"
        },
        {
            "query": "tell me about apartment amenities",
            "expected_detail_level": "detailed",
            "description": "Details request - should be detailed"
        }
    ]
    
    print("=" * 80)
    print("TESTING BUDGET QUERY FIX")
    print("=" * 80)
    print()
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected_detail_level"]
        description = test_case["description"]
        
        # Get actual detail level
        analysis = QueryPreprocessor.enhance_query(query)
        actual = analysis["detail_level"]
        
        # Check if test passed
        passed = actual == expected
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Description: {description}")
        print(f"  Query: '{query}'")
        print(f"  Expected: {expected}")
        print(f"  Actual: {actual}")
        if not passed:
            print(f"  ERROR: Detail level mismatch!")
        print()
    
    print("=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nBudget queries will now trigger detailed LLM responses instead of")
        print("brief list-view responses. The issue is FIXED!")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the failures above.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = test_budget_queries()
    exit(0 if success else 1)
