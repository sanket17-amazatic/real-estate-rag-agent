"""
Configuration settings for Real Estate RAG System
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Real Estate RAG System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # GPT-4o Mini model
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Milvus Zilliz Cloud Settings (Serverless)
    # For Zilliz Cloud, use URI and TOKEN (API key) authentication
    # Get these from Zilliz Cloud console "Connect" panel
    MILVUS_URI: str = ""
    MILVUS_TOKEN: str = ""
    
    # Optional: Traditional auth (if not using token)
    MILVUS_USER: str = "db_admin"
    MILVUS_PASSWORD: str = ""
    MILVUS_DB: str = "default"
    MILVUS_COLLECTION: str = "real_estate_properties"  # Collection name
    
    # Internal collection settings
    MILVUS_DIMENSION: int = 384  # text-embedding-3-small dimension
    
    # LLM Provider Settings
    DEFAULT_LLM_PROVIDER: str = "openai"  # Can be extended to anthropic, azure, etc.
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    
    # Text Processing Settings
    CHUNK_SIZE: int = 500  # tokens per chunk
    CHUNK_OVERLAP: int = 100  # token overlap between chunks
    
    # RAG Settings
    TOP_K_RESULTS: int = 5  # Number of top results to retrieve from Milvus
    SIMILARITY_THRESHOLD: float = 0.7  # Minimum similarity score
    
    # PDF Storage
    PDF_UPLOAD_DIR: str = "data/pdfs"
    PDF_PROCESSED_DIR: str = "data/processed"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields in .env without errors
    )


# Singleton instance
settings = Settings()
