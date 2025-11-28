# vector_store.py
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from config import settings

logger = logging.getLogger(__name__)

class MilvusStore:
    def __init__(self):
        self.collection_name = settings.COLLECTION_NAME
        self.dim = 384  # Dimension for all-MiniLM-L6-v2 embeddings
        self._connect()
        self._create_collection_if_not_exists()

    def _connect(self):
        """Establish connection to Zilliz Cloud."""
        try:
            connections.connect(
                alias="default",
                uri=settings.ZILLIZ_URI,
                token=settings.ZILLIZ_TOKEN,
                user=settings.ZILLIZ_USER,
                password=settings.ZILLIZ_PASSWORD,
                secure=True
            )
            logger.info("Successfully connected to Zilliz Cloud")
        except Exception as e:
            logger.error(f"Failed to connect to Zilliz Cloud: {e}")
            raise

    def _create_collection_if_not_exists(self):
        """Create collection if it doesn't exist."""
        try:
            if not utility.has_collection(self.collection_name):
                # Define fields
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim),
                    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="page", dtype=DataType.INT64),
                ]

                # Create schema
                schema = CollectionSchema(
                    fields=fields,
                    description="Real Estate Documents",
                    enable_dynamic_field=True
                )
                
                # Create collection
                self.collection = Collection(
                    name=self.collection_name, 
                    schema=schema,
                    using="default",
                    shards_num=2
                )
                
                # Create index
                index_params = {
                    "index_type": "AUTOINDEX",
                    "metric_type": "COSINE",
                    "params": {}
                }
                self.collection.create_index(
                    field_name="embedding",
                    index_params=index_params,
                    index_name="embedding_index"
                )
                
                logger.info(f"Created new collection: {self.collection_name}")
            else:
                self.collection = Collection(self.collection_name)
                self.collection.load()
                logger.info(f"Loaded existing collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error in collection setup: {e}")
            raise

    async def insert_documents(self, documents: List[Dict[str, Any]], embeddings: List[Any]):
        """Insert documents into the collection."""
        try:
            # Prepare data for insertion - ORDER MUST MATCH SCHEMA
            texts = [str(doc["text"]) for doc in documents]  # Ensure strings
            sources = [str(doc.get("source", "unknown")) for doc in documents]  # Ensure strings
            pages = [int(doc.get("page", 0)) for doc in documents]  # Ensure INT16
            
            # Import required modules
            import numpy as np
            
            # Debug: Print input types
            print(f"\n=== DEBUG: Input Types ===")
            print(f"Number of documents: {len(documents)}")
            print(f"Embeddings type: {type(embeddings)}")
            if embeddings:
                print(f"Number of embeddings: {len(embeddings)}")
                print(f"First embedding type: {type(embeddings[0])}")
                if hasattr(embeddings[0], '__len__'):
                    print(f"First embedding length: {len(embeddings[0])}")
                    if len(embeddings[0]) > 0:
                        first_val = embeddings[0][0]
                        print(f"First value type: {type(first_val)}, value: {first_val}")
            print("==========================\n")
            
            # Convert all embeddings to list of floats
            processed_embeddings = []
            for i, emb in enumerate(embeddings):
                # Convert to list if it's a numpy array
                if hasattr(emb, 'tolist'):
                    emb = emb.tolist()
                
                # Ensure it's a list
                if not isinstance(emb, (list, tuple)):
                    emb = [emb]
                
                # Convert all values to float and ensure they're not strings
                float_emb = []
                for j, val in enumerate(emb):
                    if isinstance(val, str):
                        try:
                            val = float(val)
                        except (ValueError, TypeError) as e:
                            print(f"Error converting value at embedding[{i}][{j}]: {val} (type: {type(val)})")
                            raise
                    float_emb.append(float(val))
                
                processed_embeddings.append(float_emb)
                
                # Print first embedding as sample
                if i == 0:
                    print(f"First processed embedding (first 5 values): {float_emb[:5]}")
                    print(f"First embedding types: {[type(x) for x in float_emb[:5]]}")
            
            print(f"Processed {len(processed_embeddings)} embeddings")
            print("============================\n")

            # Convert all embeddings to list of floats
            processed_embeddings = []
            
            print("\n=== PROCESSING EMBEDDINGS ===")
            for i, emb in enumerate(embeddings):
                # Convert numpy array to list if needed
                if hasattr(emb, 'tolist'):
                    emb = emb.tolist()
                
                # Ensure it's a list
                if not isinstance(emb, (list, tuple)):
                    emb = [emb]
                
                # Convert all values to float
                try:
                    float_emb = [float(x) for x in emb]
                    processed_embeddings.append(float_emb)
                except (ValueError, TypeError) as e:
                    print(f"Error processing embedding {i}: {e}")
                    print(f"Problematic embedding: {emb}")
                    raise ValueError(f"Could not convert embedding to float: {e}")
                
                # Print first embedding as sample
                if i == 0:
                    print(f"First embedding (first 5 values): {float_emb[:5]}")
                    print(f"First embedding types: {[type(x) for x in float_emb[:5]]}")
            
            print(f"Processed {len(processed_embeddings)} embeddings")
            print("============================\n")

            # Ensure embeddings are a list of list of floats
            import numpy as np
            import json
            
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
                print("✓ Converted numpy array to list")
            elif isinstance(embeddings, list):
                if not embeddings:
                    raise ValueError("Embeddings list is empty")
                
                # Check first element type
                first_elem = embeddings[0]
                print(f"First element type: {type(first_elem)}, value sample: {str(first_elem)[:100]}")
                
                if isinstance(first_elem, str):
                        # Try to parse as JSON array
                        print("⚠ Detected string embeddings, attempting to parse")
                        try:
                            # First try to parse the entire string as a JSON array
                            if first_elem.startswith('[') and first_elem.endswith(']'):
                                try:
                                    parsed = json.loads(first_elem)
                                    if isinstance(parsed, list) and all(isinstance(x, (int, float)) for x in parsed):
                                        # If successfully parsed as a list of numbers, apply to all embeddings
                                        print("✓ Successfully parsed string embeddings as JSON array")
                                        embeddings = [json.loads(e) if isinstance(e, str) else e for e in embeddings]
                                        # Ensure all elements are floats
                                        embeddings = [[float(x) for x in emb] for emb in embeddings]
                                    else:
                                        raise json.JSONDecodeError("Not a list of numbers", "", 0)
                                except json.JSONDecodeError:
                                    # If not a valid JSON array, try other formats
                                    raise
                            
                            # If we get here, try parsing as space-separated or comma-separated values
                            print("⚠ String is not a JSON array, trying space/comma separated values")
                            parsed_embeddings = []
                            for e in embeddings:
                                if not isinstance(e, str):
                                    parsed_embeddings.append(e)
                                    continue
                                    
                                # Clean the string
                                e_clean = e.strip('[]{}()')
                                # Try splitting by comma first, then by space
                                parts = [x.strip() for x in e_clean.replace(',', ' ').split() if x.strip()]
                                try:
                                    # Convert all parts to float
                                    float_emb = [float(x) for x in parts]
                                    parsed_embeddings.append(float_emb)
                                except ValueError as ve:
                                    print(f"⚠ Could not parse embedding string: {e[:100]}...")
                                    raise ValueError(f"Invalid embedding format: {str(ve)}")
                            
                            embeddings = parsed_embeddings
                            print(f"✓ Successfully parsed {len(embeddings)} embeddings from string format")
                        except Exception as e:
                            print(f"Error parsing embeddings: {e}")
                            raise
                            
                elif isinstance(first_elem, (list, tuple)):
                    # Ensure all elements are floats and convert any numpy arrays
                    new_embeddings = []
                    for e in embeddings:
                        if isinstance(e, np.ndarray):
                            e = e.tolist()
                        # Ensure all elements in the embedding are floats
                        float_emb = [float(x) for x in e]
                        new_embeddings.append(float_emb)
                    embeddings = new_embeddings
                    print("✓ Converted embeddings to list of float lists")
                    
                elif isinstance(first_elem, np.ndarray):
                    embeddings = [e.tolist() for e in embeddings]
                    print("✓ Converted numpy arrays to lists")
                else:
                    raise ValueError(f"Unknown embedding element type: {type(first_elem)}")
            else:
                raise ValueError(f"Embeddings must be a list or numpy array, got {type(embeddings)}")

            # Final validation and conversion of embeddings
            final_embeddings = []
            for emb in embeddings:
                if isinstance(emb, (list, tuple)):
                    # Convert all elements to float
                    final_embeddings.append([float(x) for x in emb])
                elif isinstance(emb, np.ndarray):
                    final_embeddings.append([float(x) for x in emb.tolist()])
                else:
                    # Try to convert to float if it's a single value
                    try:
                        final_embeddings.append([float(emb)])
                    except (TypeError, ValueError):
                        raise ValueError(f"Cannot convert embedding to float: {emb}")

            print(f"Final embedding type: {type(final_embeddings[0]) if final_embeddings else None}")
            print(f"First embedding sample: {final_embeddings[0][:5] if final_embeddings else None}")
            print(f"Number of embeddings: {len(final_embeddings)}")
            print(f"Number of texts: {len(texts)}")
            print(f"Schema field order: text, embedding, source, page")

            # Final validation before insertion
            print("\n--- VALIDATING DATA BEFORE INSERT ---")
            
            # Check that we have the same number of items in each list
            if not (len(texts) == len(processed_embeddings) == len(sources) == len(pages)):
                error_msg = f"Mismatched list lengths: texts={len(texts)}, embeddings={len(processed_embeddings)}, sources={len(sources)}, pages={len(pages)}"
                print(f"ERROR: {error_msg}")
                raise ValueError(error_msg)
            
            # Double-check that all embeddings are lists of floats
            for i, emb in enumerate(processed_embeddings):
                if not isinstance(emb, (list, tuple)):
                    error_msg = f"Embedding at index {i} is not a list/tuple: {type(emb)}"
                    print(f"ERROR: {error_msg}")
                    raise ValueError(error_msg)
                
                for j, val in enumerate(emb):
                    if not isinstance(val, (int, float)):
                        error_msg = f"Found non-float value at embedding[{i}][{j}]: {val} (type: {type(val)})"
                        print(f"ERROR: {error_msg}")
                        raise ValueError(error_msg)
            
            print("✓ All data validated")
            print(f"Number of documents to insert: {len(texts)}")
            print(f"Number of embeddings: {len(processed_embeddings)}")
            print(f"Embedding dimension: {len(processed_embeddings[0]) if processed_embeddings else 0}")
            print("--- END VALIDATION ---\n")
            
            # Prepare data for insertion - ensure all lists are plain Python lists
            try:
                # Create a list of dictionaries in the format expected by Milvus
                entities = []
                for i in range(len(texts)):
                    # Create a dictionary with field names matching the schema
                    entity = {
                        "text": str(texts[i]),
                        "embedding": [float(x) for x in processed_embeddings[i]],  # Ensure all values are Python floats
                        "source": str(sources[i]),
                        "page": int(pages[i])
                    }
                    entities.append(entity)
                
                # Debug: Print the types of the first entity
                if entities:
                    first_entity = entities[0]
                    print("\n--- FIRST ENTITY DATA TYPES ---")
                    print(f"Text type: {type(first_entity['text'])}")
                    print(f"Embedding type: {type(first_entity['embedding'])}")
                    print(f"  First embedding value type: {type(first_entity['embedding'][0]) if first_entity['embedding'] else 'N/A'}")
                    print(f"  First 5 values: {first_entity['embedding'][:5]}")
                    print(f"Source type: {type(first_entity['source'])}")
                    print(f"Page type: {type(first_entity['page'])}")
                    print("------------------------------\n")
                
                print("Attempting to insert into Milvus...")
                
                # Insert data using the entity-based approach
                insert_result = self.collection.insert(entities)
                print("✓ Insert successful")
                
            except Exception as e:
                print(f"\n!!! MILVUS INSERT ERROR !!!")
                print(f"Error type: {type(e).__name__}")
                print(f"Error details: {str(e)}")
                
                # Print more detailed error information
                if hasattr(e, 'details') and hasattr(e.details, 'get'):
                    print(f"\nError details:")
                    for key, value in e.details.items():
                        print(f"  {key}: {value}")
                
                # Print information about the first entity
                if entities and len(entities) > 0:
                    first_entity = entities[0]
                    print("\nFirst entity structure:")
                    for key, value in first_entity.items():
                        if key == 'embedding' and isinstance(value, (list, tuple)) and len(value) > 5:
                            print(f"  {key}: List of length {len(value)}. First 5 values: {value[:5]}")
                            print(f"     Types: {[type(x) for x in value[:5]]}")
                        else:
                            print(f"  {key}: {value} (type: {type(value)})")
                
                # Print schema information for debugging
                try:
                    collection_info = self.collection.describe()
                    print("\nCollection schema:")
                    for field in collection_info.fields:
                        print(f"  {field.name}: {field.dtype} (is_primary: {field.is_primary})")
                except Exception as schema_err:
                    print(f"\nCould not retrieve collection schema: {schema_err}")
                
                raise
            self.collection.flush()
            print(f"✓ Inserted {len(documents)} documents into Milvus\n")
            logger.info(f"Inserted {len(documents)} documents into collection")
            return insert_result
        except Exception as e:
            print(f"✗ Error inserting documents: {e}\n")
            logger.error(f"Error inserting documents: {e}", exc_info=True)
            raise

    async def search(self, query_embedding: List[float], top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Load collection
            self.collection.load()
            
            # Execute search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["text", "source", "page"]
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append({
                        "text": hit.entity.get("text"),
                        "source": hit.entity.get("source"),
                        "page": hit.entity.get("page"),
                        "score": hit.distance
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def close(self):
        """Close the connection."""
        connections.disconnect("default")
        logger.info("Disconnected from Zilliz Cloud")