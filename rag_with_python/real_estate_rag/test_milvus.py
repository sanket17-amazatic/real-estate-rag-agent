"""
Test Milvus connection
"""
from services.milvus_service import get_milvus_service
from config.settings import settings

print("=== Testing Milvus Connection ===\n")

try:
    # Get service
    milvus_service = get_milvus_service()
    print("✓ Milvus service initialized")
    
    # Connect
    print(f"\nConnecting to: {settings.MILVUS_URI}")
    milvus_service.connect()
    print("✓ Successfully connected to Zilliz Cloud")
    
    # Create/load collection
    print(f"\nCreating/loading collection: {settings.MILVUS_COLLECTION}")
    milvus_service.create_collection(drop_existing=False)
    print("✓ Collection ready")
    
    # Get stats
    stats = milvus_service.get_collection_stats()
    print(f"\n📊 Collection Statistics:")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Entities: {stats['num_entities']}")
    
    print("\n✅ Milvus connection test PASSED!")
    
except Exception as e:
    print(f"\n❌ Milvus connection test FAILED!")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    try:
        milvus_service.disconnect()
        print("\n✓ Disconnected from Milvus")
    except:
        pass
