from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "real_estate_new_data")
ZILLIZ_URI = os.getenv("ZILLIZ_URI")
ZILLIZ_TOKEN = os.getenv("ZILLIZ_TOKEN")
ZILLIZ_USER = os.getenv("ZILLIZ_USER")
ZILLIZ_PASSWORD = os.getenv("ZILLIZ_PASSWORD")

# Set your embedding dimension here
EMBEDDING_DIM = 384

# Connect to Zilliz Cloud
connections.connect(
    alias="default",
    uri=ZILLIZ_URI,
    token=ZILLIZ_TOKEN,
    user=ZILLIZ_USER,
    password=ZILLIZ_PASSWORD,
    secure=True
)

# Drop collection if exists
if Collection.exists(COLLECTION_NAME):
    Collection.drop(COLLECTION_NAME)

# Define fields
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="page", dtype=DataType.INT64)
]

schema = CollectionSchema(fields, description="Real estate document collection with embeddings")

# Create collection
collection = Collection(name=COLLECTION_NAME, schema=schema)

print(f"Collection '{COLLECTION_NAME}' created with schema:")
for field in fields:
    print(f"- {field.name}: {field.dtype}, max_length={getattr(field, 'max_length', None)}, dim={getattr(field, 'dim', None)}")
