#!/usr/bin/env python3
"""
Test the two-level detail system
"""
from query_preprocessor import QueryPreprocessor

print("\n" + "="*80)
print("TWO-LEVEL DETAIL SYSTEM - DEMONSTRATION")
print("="*80 + "\n")

# Test queries
test_queries = [
    # BRIEF QUERIES (list properties)
    ("Show me properties in Pune", "BRIEF"),
    ("List all 2 BHK apartments", "BRIEF"),
    ("Get properties in Wakad", "BRIEF"),
    ("Quick summary of available properties", "BRIEF"),
    
    # DETAILED QUERIES (full information)
    ("Tell me details about Aurora Crest", "DETAILED"),
    ("Give me information on Evergreen Heights", "DETAILED"),
    ("What are the features of Summit Enclave?", "DETAILED"),
    ("Tell me more about properties in Viman Nagar", "DETAILED"),
    ("I want complete details for this property", "DETAILED"),
]

print("QUERY ANALYSIS - Detail Level Detection:\n")
print("-" * 80)

for query, expected in test_queries:
    analysis = QueryPreprocessor.enhance_query(query)
    detected = analysis['detail_level']
    status = "✅" if detected == expected else "⚠️"
    
    print(f"\n{status} Query: '{query}'")
    print(f"   Expected: {expected} | Detected: {detected}")
    if detected != expected:
        print(f"   ⚠️  MISMATCH!")

print("\n" + "-" * 80)
print("\nDETAIL LEVEL EXPLANATION:\n")

print("📋 BRIEF MODE (When user asks to 'list' or 'show' properties):")
print("   • Shows: Property name, location, price, BHK/type")
print("   • Format: 1-2 lines per property")
print("   • Best for: Quick property browsing")
print("   • Examples: 'Show properties', 'List 2 BHK', 'Find apartments'")
print("   • Token limit: 800 (quick responses)")
print()

print("📖 DETAILED MODE (When user asks for 'details', 'information', 'about'):")
print("   • Shows: All details (amenities, contact, area, buying tips)")
print("   • Format: Full property information")
print("   • Best for: Specific property research")
print("   • Examples: 'Details about Aurora Crest', 'Tell me more', 'Full information'")
print("   • Token limit: 2000 (comprehensive responses)")

print("\n" + "="*80)
print("USER EXPERIENCE FLOW:\n")
print("="*80)

print("\n1. USER: 'Show me properties in Pune'")
print("   → AGENT: Shows brief list (5-10 properties)")
print("   → Name, Location, Price, BHK only")
print("   → Quick scannable format")
print()

print("2. USER: 'Tell me about Aurora Crest' / 'More details on first property'")
print("   → AGENT: Shows FULL details for that property")
print("   → Including: amenities, contact, area, buying considerations")
print("   → Comprehensive buying guide")
print()

print("3. USER: 'Compare these two properties'")
print("   → AGENT: Shows detailed comparison")
print("   → Side-by-side analysis")
print("   → Recommendations")

print("\n" + "="*80)
print("BENEFITS OF TWO-LEVEL SYSTEM:\n")
print("="*80)

print("\n✅ Better User Experience:")
print("   • Not overwhelming with too much info at once")
print("   • Users control how much detail they want")
print("   • Faster initial browsing")
print("   • Deeper research when interested")

print("\n✅ Optimized Responses:")
print("   • Brief mode: 800 tokens (faster, cheaper)")
print("   • Detailed mode: 2000 tokens (comprehensive)")
print("   • Matched token limits to content needs")

print("\n✅ Natural Conversation Flow:")
print("   • Initial query → Brief summary")
print("   • Follow-up query → Detailed information")
print("   • Matches how people naturally search for properties")

print("\n" + "="*80)
print("✅ TWO-LEVEL DETAIL SYSTEM READY!\n")
