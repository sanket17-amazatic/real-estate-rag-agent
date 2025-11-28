"""
LLM Processor with Factory Pattern and Singleton Implementation
Supports multiple LLM providers (OpenAI, Anthropic, Azure, etc.)
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseLLMProcessor(ABC):
    """Abstract base class for LLM processors"""
    
    @abstractmethod
    def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a chat completion"""
        pass
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        pass


class OpenAIProcessor(BaseLLMProcessor):
    """OpenAI LLM Processor"""
    
    def __init__(self, api_key: str, model: str, embedding_model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = embedding_model
        logger.info(f"Initialized OpenAI Processor with model: {model}")
    
    def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate chat completion using OpenAI API"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or settings.LLM_TEMPERATURE,
                "max_tokens": max_tokens or settings.LLM_MAX_TOKENS
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (response.choices[0].message.tool_calls or [])
                ],
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"Error in OpenAI completion: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise


class AnthropicProcessor(BaseLLMProcessor):
    """Anthropic Claude LLM Processor (placeholder for future implementation)"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized Anthropic Processor with model: {model}")
        raise NotImplementedError("Anthropic processor not yet implemented")
    
    def generate_completion(self, messages, tools=None, temperature=None, max_tokens=None):
        raise NotImplementedError()
    
    def generate_embedding(self, text: str):
        raise NotImplementedError()


class AzureOpenAIProcessor(BaseLLMProcessor):
    """Azure OpenAI LLM Processor (placeholder for future implementation)"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        logger.info(f"Initialized Azure OpenAI Processor with deployment: {deployment}")
        raise NotImplementedError("Azure OpenAI processor not yet implemented")
    
    def generate_completion(self, messages, tools=None, temperature=None, max_tokens=None):
        raise NotImplementedError()
    
    def generate_embedding(self, text: str):
        raise NotImplementedError()


class LLMProcessorFactory:
    """Factory class for creating LLM processors with Singleton pattern"""
    
    _instances: Dict[str, BaseLLMProcessor] = {}
    
    @classmethod
    def get_processor(
        cls, 
        provider: str = None, 
        model: str = None,
        **kwargs
    ) -> BaseLLMProcessor:
        """
        Get or create an LLM processor instance (Singleton pattern)
        
        Args:
            provider: LLM provider name (openai, anthropic, azure)
            model: Model name to use
            **kwargs: Additional provider-specific configuration
        
        Returns:
            BaseLLMProcessor instance
        """
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        model = model or settings.OPENAI_MODEL
        
        # Create unique key for this configuration
        instance_key = f"{provider}_{model}"
        
        # Return existing instance if available
        if instance_key in cls._instances:
            logger.info(f"Returning existing LLM processor instance: {instance_key}")
            return cls._instances[instance_key]
        
        # Create new instance based on provider
        logger.info(f"Creating new LLM processor instance: {instance_key}")
        
        if provider.lower() == "openai":
            processor = OpenAIProcessor(
                api_key=kwargs.get("api_key", settings.OPENAI_API_KEY),
                model=model,
                embedding_model=kwargs.get("embedding_model", settings.OPENAI_EMBEDDING_MODEL)
            )
        elif provider.lower() == "anthropic":
            processor = AnthropicProcessor(
                api_key=kwargs.get("api_key"),
                model=model
            )
        elif provider.lower() == "azure":
            processor = AzureOpenAIProcessor(
                endpoint=kwargs.get("endpoint"),
                api_key=kwargs.get("api_key"),
                deployment=model
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        # Store instance
        cls._instances[instance_key] = processor
        return processor
    
    @classmethod
    def clear_instances(cls):
        """Clear all singleton instances (useful for testing)"""
        cls._instances.clear()
        logger.info("Cleared all LLM processor instances")


# Convenience function to get default processor
def get_default_llm_processor() -> BaseLLMProcessor:
    """Get the default LLM processor based on settings"""
    return LLMProcessorFactory.get_processor()
