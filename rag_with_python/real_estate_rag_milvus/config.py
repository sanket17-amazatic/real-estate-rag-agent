# config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Zilliz Cloud Configuration
    ZILLIZ_URI: str = os.getenv("ZILLIZ_URI")
    ZILLIZ_TOKEN: str = os.getenv("ZILLIZ_TOKEN")
    ZILLIZ_USER: str = os.getenv("ZILLIZ_USER")
    ZILLIZ_PASSWORD: str = os.getenv("ZILLIZ_PASSWORD")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "real_estate_new_data")
    
    # Embedding model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")

settings = Settings()