"""
Test OpenAI API
"""
from services.llm_processor import get_default_llm_processor
from config.settings import settings

print("=== Testing OpenAI API ===\n")

try:
    # Get LLM processor
    llm = get_default_llm_processor()
    print(f"✓ LLM processor initialized")
    print(f"   Model: {settings.OPENAI_MODEL}")
    print(f"   Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
    
    # Test embedding generation
    print(f"\nGenerating embedding for test text...")
    test_text = "This is a test property in Wakad, Pune with 2 BHK configuration."
    
    embedding = llm.generate_embedding(test_text)
    print(f"✓ Embedding generated successfully")
    print(f"   Dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Verify dimension
    if len(embedding) == settings.MILVUS_DIMENSION:
        print(f"✓ Embedding dimension matches Milvus dimension ({settings.MILVUS_DIMENSION})")
    else:
        print(f"❌ Dimension mismatch! Got {len(embedding)}, expected {settings.MILVUS_DIMENSION}")
    
    print("\n✅ OpenAI API test PASSED!")
    
except Exception as e:
    print(f"\n❌ OpenAI API test FAILED!")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
