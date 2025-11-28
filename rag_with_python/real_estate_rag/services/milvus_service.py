"""
Milvus Service for Vector Database Operations
Handles connection, collection management, ingestion, and search
"""
import logging
from typing import List, Dict, Any, Optional
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from config.settings import settings

logger = logging.getLogger(__name__)


class MilvusService:
    """Singleton service for Milvus operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MilvusService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.collection_name = settings.MILVUS_COLLECTION
            self.dimension = settings.MILVUS_DIMENSION
            self.collection = None
            self._initialized = True
            logger.info("MilvusService instance created")
    
    def connect(self):
        """Connect to Milvus Zilliz Cloud"""
        try:
            # Zilliz Cloud: Use URI + Token (API key) authentication
            connection_params = {
                "alias": "default",
                "uri": settings.MILVUS_URI,
            }
            
            # Prefer token authentication if available
            if settings.MILVUS_TOKEN:
                connection_params["token"] = settings.MILVUS_TOKEN
                logger.info(f"Connecting to Zilliz Cloud with API token at {settings.MILVUS_URI}")
            else:
                # Fallback to username/password
                connection_params["user"] = settings.MILVUS_USER
                connection_params["password"] = settings.MILVUS_PASSWORD
                logger.info(f"Connecting to Zilliz Cloud with username/password at {settings.MILVUS_URI}")
            
            connections.connect(**connection_params)
            logger.info(f"Successfully connected to Milvus Zilliz Cloud")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {str(e)}")
            raise
    
    def disconnect(self):
        """Disconnect from Milvus"""
        try:
            connections.disconnect("default")
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {str(e)}")
    
    def create_collection(self, drop_existing: bool = False):
        """
        Create Milvus collection for property documents
        
        Schema:
        - id: primary key (auto-generated)
        - embedding: vector field
        - text: original text content
        - filename: source PDF filename
        - locality: property locality
        - property_type: type of property
        - metadata: JSON metadata
        """
        try:
            # Drop existing collection if requested
            if drop_existing and utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"Dropped existing collection: {self.collection_name}")
            
            # Check if collection already exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                logger.info(f"Collection {self.collection_name} already exists, using existing collection")
                return self.collection
            
            # Define schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="locality", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="property_type", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="chunk_index", dtype=DataType.INT64),
                FieldSchema(name="metadata_json", dtype=DataType.VARCHAR, max_length=2048)
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="Real Estate Property Documents Collection"
            )
            
            # Create collection
            self.collection = Collection(
                name=self.collection_name,
                schema=schema,
                using='default'
            )
            
            logger.info(f"Created collection: {self.collection_name}")
            
            # Create IVF_FLAT index for vector search with COSINE similarity
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            logger.info("Created index on embedding field")
            
            return self.collection
            
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def insert_vectors(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        filenames: List[str],
        localities: List[str],
        property_types: List[str],
        chunk_indices: List[int],
        metadata_jsons: List[str]
    ) -> int:
        """
        Insert vectors into Milvus collection
        
        Returns:
            Number of vectors inserted
        """
        try:
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            # Prepare data
            data = [
                embeddings,
                texts,
                filenames,
                localities,
                property_types,
                chunk_indices,
                metadata_jsons
            ]
            
            # Insert data
            insert_result = self.collection.insert(data)
            self.collection.flush()
            
            num_inserted = len(insert_result.primary_keys)
            logger.info(f"Inserted {num_inserted} vectors into Milvus")
            
            return num_inserted
            
        except Exception as e:
            logger.error(f"Error inserting vectors: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Milvus
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Optional filter expression
        
        Returns:
            List of search results with metadata
        """
        try:
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            # Load collection into memory
            self.collection.load()
            
            # Define search parameters with COSINE similarity
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Define output fields
            output_fields = [
                "text", 
                "filename", 
                "locality", 
                "property_type", 
                "chunk_index", 
                "metadata_json"
            ]
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=filters,
                output_fields=output_fields
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    # With COSINE, distance is already a similarity score (0-1, higher is better)
                    # Note: Milvus COSINE returns distance = 1 - cosine_similarity
                    similarity_score = 1 - hit.distance if hit.distance <= 1 else 0
                    formatted_results.append({
                        "id": hit.id,
                        "distance": hit.distance,
                        "score": similarity_score,  # Cosine similarity score
                        "text": hit.entity.get("text"),
                        "filename": hit.entity.get("filename"),
                        "locality": hit.entity.get("locality"),
                        "property_type": hit.entity.get("property_type"),
                        "chunk_index": hit.entity.get("chunk_index"),
                        "metadata": hit.entity.get("metadata_json")
                    })
            
            logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching Milvus: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            stats = {
                "collection_name": self.collection_name,
                "num_entities": self.collection.num_entities,
                "schema": str(self.collection.schema)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise


# Singleton instance getter
def get_milvus_service() -> MilvusService:
    """Get the singleton MilvusService instance"""
    return MilvusService()
