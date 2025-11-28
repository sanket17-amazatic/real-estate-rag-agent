import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "real_eastat_vector")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "1536"))
ZILLIZ_URI = os.getenv("ZILLIZ_URI")
ZILLIZ_TOKEN = os.getenv("ZILLIZ_TOKEN")
ZILLIZ_USER = os.getenv("ZILLIZ_USER")
ZILLIZ_PASSWORD = os.getenv("ZILLIZ_PASSWORD")

# Connect to Milvus/Zilliz
connections.connect(
    alias="default",
    uri=ZILLIZ_URI,
    token=ZILLIZ_TOKEN,
    user=ZILLIZ_USER,
    password=ZILLIZ_PASSWORD,
    secure=True
)

# Define schema if collection does not exist
def create_collection():
    from pymilvus import utility
    if not utility.has_collection(COLLECTION_NAME):
        fields = [
            FieldSchema(name="primary_key", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields, description="Cosine search test collection")
        collection = Collection(COLLECTION_NAME, schema, shards_num=2)
        index_params = {"index_type": "AUTOINDEX", "metric_type": "IP", "params": {}}
        collection.create_index(field_name="vector", index_params=index_params)
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection {COLLECTION_NAME} already exists.")


def insert_chunks(chunks):
    collection = Collection(COLLECTION_NAME)
    # Ensure each chunk uses 'vector' as the key for the vector
    for chunk in chunks:
        if 'embedding' in chunk:
            chunk['vector'] = chunk.pop('embedding')
    insert_result = collection.insert(chunks)
    collection.flush()
    print(f"Inserted {len(chunks)} chunks.")
    return insert_result


def cosine_search(query_vector, top_k=5):
    collection = Collection(COLLECTION_NAME)
    collection.load()
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_vector],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields=["text"]
    )
    for hits in results:
        for hit in hits:
            print(f"Score: {hit.distance:.4f} | Text: {hit.entity.get('text')}")
    return results


if __name__ == "__main__":
    # 1. Create collection (run once)
    create_collection()

    # 2. Insert test chunks (edit or repeat as needed)
    # Example: 3 random vectors
    test_chunks = [
        {"vector": np.random.rand(VECTOR_DIM).tolist(), "text": "First test chunk.", "source": "test"},
        {"vector": np.random.rand(VECTOR_DIM).tolist(), "text": "Second test chunk.", "source": "test"},
        {"vector": np.random.rand(VECTOR_DIM).tolist(), "text": "Third test chunk.", "source": "test"},
    ]
    insert_chunks(test_chunks)

    # 3. Search with a random query vector
    query_vec = np.random.rand(VECTOR_DIM).tolist()
    print("\nCosine search results:")
    cosine_search(query_vec, top_k=3)
