"""
Validate environment configuration
"""
from config.settings import settings

print("=== Environment Configuration ===\n")

# Check OpenAI
print(f"OPENAI_API_KEY: {'✓ Set' if settings.OPENAI_API_KEY else '✗ Missing'}")
print(f"OPENAI_MODEL: {settings.OPENAI_MODEL}")
print(f"OPENAI_EMBEDDING_MODEL: {settings.OPENAI_EMBEDDING_MODEL}")

# Check Milvus
print(f"\nMILVUS_URI: {'✓ Set' if settings.MILVUS_URI else '✗ Missing'}")
print(f"MILVUS_TOKEN: {'✓ Set' if settings.MILVUS_TOKEN else '✗ Missing'}")
print(f"MILVUS_COLLECTION: {settings.MILVUS_COLLECTION}")
print(f"MILVUS_DIMENSION: {settings.MILVUS_DIMENSION}")

# Check other settings
print(f"\nDEBUG: {settings.DEBUG}")
print(f"CHUNK_SIZE: {settings.CHUNK_SIZE}")
print(f"CHUNK_OVERLAP: {settings.CHUNK_OVERLAP}")
print(f"TOP_K_RESULTS: {settings.TOP_K_RESULTS}")

print("\n✓ All settings loaded successfully!")
