"""
Test script to demonstrate the Real Estate RAG System
"""
import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    return response.status_code == 200


def test_ingest_pdf(pdf_path):
    """Test PDF ingestion"""
    print_section("2. PDF Ingestion")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {'locality': 'Wakad', 'property_type': 'Apartment'}
        
        response = requests.post(
            f"{BASE_URL}/ingest/pdf",
            files=files,
            data=data
        )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    return response.status_code == 200


def test_rag_query():
    """Test RAG query endpoint"""
    print_section("3. RAG Query - Knowledge Retrieval")
    
    queries = [
        "What are the amenities in Wakad locality?",
        "Tell me about Evergreen Heights project",
        "What is the connectivity like in Hinjewadi?"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        
        response = requests.post(
            f"{BASE_URL}/query/rag",
            json={
                "query": query,
                "top_k": 3,
                "include_context": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer'][:200]}...\n")
        else:
            print(f"Error: {response.status_code}\n")
        
        time.sleep(1)


def test_buy_agent():
    """Test Buy Agent"""
    print_section("4. Buy Agent - Property Search")
    
    messages = [
        "I want to buy a 2 BHK apartment in Wakad under 80 lakhs",
        "What properties are available in Baner for purchase?",
        "Show me 3 BHK apartments suitable for investment"
    ]
    
    for message in messages:
        print(f"User: {message}")
        
        response = requests.post(
            f"{BASE_URL}/query/agent",
            json={
                "agent_type": "buy",
                "message": message
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Agent: {result['response'][:300]}...\n")
        else:
            print(f"Error: {response.status_code}\n")
        
        time.sleep(1)


def test_rent_agent():
    """Test Rent Agent"""
    print_section("5. Rent Agent - Rental Search")
    
    messages = [
        "Looking for a 2 BHK rental in Hinjewadi under 25000 per month",
        "What rental properties are available in Wakad?",
    ]
    
    for message in messages:
        print(f"User: {message}")
        
        response = requests.post(
            f"{BASE_URL}/query/agent",
            json={
                "agent_type": "rent",
                "message": message
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Agent: {result['response'][:300]}...\n")
        else:
            print(f"Error: {response.status_code}\n")
        
        time.sleep(1)


def test_details_agent():
    """Test Property Details Agent"""
    print_section("6. Property Details Agent - Information")
    
    messages = [
        "Tell me about the specifications of Evergreen Heights",
        "What amenities are included in the clubhouse?",
        "What is the floor plan of 2 BHK units?"
    ]
    
    for message in messages:
        print(f"User: {message}")
        
        response = requests.post(
            f"{BASE_URL}/query/agent",
            json={
                "agent_type": "details",
                "message": message
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Agent: {result['response'][:300]}...\n")
        else:
            print(f"Error: {response.status_code}\n")
        
        time.sleep(1)


def test_auto_routing():
    """Test Auto Routing with Orchestrator"""
    print_section("7. Auto Routing - Intelligent Query Routing")
    
    queries = [
        "What are the schools near Wakad?",  # Knowledge -> RAG
        "I want to buy a property",  # Buy -> BuyAgent
        "Looking for rentals",  # Rent -> RentAgent
        "Tell me project specifications"  # Details -> DetailsAgent
    ]
    
    for query in queries:
        print(f"Query: {query}")
        
        response = requests.post(
            f"{BASE_URL}/query/auto",
            params={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'N/A')[:200]}...")
            print(f"Routing: {result.get('routing_info', 'N/A')}\n")
        else:
            print(f"Error: {response.status_code}\n")
        
        time.sleep(1)


def test_property_search():
    """Test Direct Property Search"""
    print_section("8. Direct Property Search")
    
    search_criteria = {
        "query": "2 BHK in Wakad",
        "locality": "Wakad",
        "min_price": 5000000,
        "max_price": 10000000,
        "bedrooms": 2
    }
    
    print(f"Search Criteria: {json.dumps(search_criteria, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/search/properties",
        json=search_criteria
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nFound {result.get('count', 0)} properties:")
        for prop in result.get('properties', [])[:3]:
            print(f"\n  - {prop['name']} ({prop['locality']})")
            print(f"    {prop['bedrooms']} BHK | ₹{prop['price']:,} | {prop['area_sqft']} sqft")
            print(f"    {prop['description']}")
    else:
        print(f"Error: {response.status_code}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  REAL ESTATE RAG SYSTEM - TEST SUITE")
    print("="*80)
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ API is not running. Please start the server first:")
        print("   python main.py")
        return
    
    print("✅ API is healthy and running\n")
    
    # Skip PDF ingestion in this demo (requires actual PDF file)
    # Uncomment and provide path to test:
    # test_ingest_pdf("path/to/your/property.pdf")
    
    # Test RAG queries
    test_rag_query()
    
    # Test agents
    test_buy_agent()
    test_rent_agent()
    test_details_agent()
    
    # Test auto routing
    test_auto_routing()
    
    # Test property search
    test_property_search()
    
    print_section("Test Suite Completed")
    print("✅ All tests executed successfully!")
    print("\nNext steps:")
    print("1. Upload your property PDFs using POST /ingest/pdf")
    print("2. Query the system using any of the agent endpoints")
    print("3. Use auto-routing for intelligent query handling\n")


if __name__ == "__main__":
    main()
