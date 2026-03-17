"""
LLM Provider Abstraction
Support for OpenAI, Claude, Ollama with fallback capabilities
"""

from typing import Optional, List
from abc import ABC, abstractmethod
import logging
from config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[dict], max_tokens: int = 1000) -> str:
        """Chat interface with message history"""
        pass
    
    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 and GPT-3.5 provider"""
    
    def __init__(self):
        try:
            import openai
            openai.api_key = settings.openai_api_key
            self.model = "gpt-3.5-turbo"  # Using turbo since gpt-4 may not be available
            logger.info("✅ OpenAI provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate response using OpenAI"""
        try:
            import openai
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in OpenAI generation: {e}")
            raise
    
    def chat(self, messages: List[dict], max_tokens: int = 1000) -> str:
        """Chat with message history"""
        try:
            import openai
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in OpenAI chat: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using OpenAI"""
        try:
            import openai
            embeddings = []
            for text in texts:
                response = openai.Embedding.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                embeddings.append(response["data"][0]["embedding"])
            return embeddings
        except Exception as e:
            logger.error(f"Error getting OpenAI embeddings: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = "claude-3-sonnet-20240229"
            logger.info("✅ Anthropic provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate response using Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error in Claude generation: {e}")
            raise
    
    def chat(self, messages: List[dict], max_tokens: int = 1000) -> str:
        """Chat with Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error in Claude chat: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Claude doesn't provide embeddings, use fallback"""
        logger.warning("Claude doesn't provide embeddings, using sentence-transformers")
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise


class OllamaProvider(LLMProvider):
    """Local Ollama provider (free, offline)"""
    
    def __init__(self):
        try:
            import requests
            # Test connection
            requests.get(f"{settings.ollama_base_url}/api/tags", timeout=2)
            self.base_url = settings.ollama_base_url
            self.model = "mistral"  # Or llama2
            logger.info("✅ Ollama provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate using Ollama"""
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error in Ollama generation: {e}")
            raise
    
    def chat(self, messages: List[dict], max_tokens: int = 1000) -> str:
        """Chat with Ollama"""
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
            )
            return response.json()["message"]["content"]
        except Exception as e:
            logger.error(f"Error in Ollama chat: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from Ollama"""
        try:
            import requests
            embeddings = []
            for text in texts:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                embeddings.append(response.json()["embedding"])
            return embeddings
        except Exception as e:
            logger.error(f"Error getting Ollama embeddings: {e}")
            raise


class LLMManager:
    """Manager for multiple LLM providers with fallback"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        # Try OpenAI
        if settings.openai_api_key:
            try:
                self.providers["openai"] = OpenAIProvider()
                if settings.default_llm == "openai":
                    self.default_provider = self.providers["openai"]
                logger.info("✅ OpenAI provider available")
            except Exception as e:
                logger.warning(f"⚠️  OpenAI not available: {e}")
        
        # Try Anthropic
        if settings.anthropic_api_key:
            try:
                self.providers["anthropic"] = AnthropicProvider()
                if settings.default_llm == "anthropic":
                    self.default_provider = self.providers["anthropic"]
                logger.info("✅ Anthropic provider available")
            except Exception as e:
                logger.warning(f"⚠️  Anthropic not available: {e}")
        
        # Try Ollama
        try:
            self.providers["ollama"] = OllamaProvider()
            if settings.default_llm == "ollama":
                self.default_provider = self.providers["ollama"]
            logger.info("✅ Ollama provider available")
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        
        # Set default if not set
        if not self.default_provider and self.providers:
            self.default_provider = list(self.providers.values())[0]
            logger.info(f"✅ Using {list(self.providers.keys())[0]} as default provider")
        
        if not self.default_provider:
            logger.warning("⚠️  No LLM providers configured! Starting with basic services. Configure OpenAI/Anthropic API key in .env")
    
    def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate text with fallback support"""
        if not self.default_provider and not self.providers:
            logger.error("No LLM providers available")
            return "ERROR: No LLM provider configured. Please add OPENAI_API_KEY to .env"
        
        selected_provider = provider or settings.default_llm
        
        if selected_provider in self.providers:
            try:
                return self.providers[selected_provider].generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"{selected_provider} failed, trying fallback: {e}")
        
        # Fallback to any available provider
        for name, prov in self.providers.items():
            if name != selected_provider:
                try:
                    logger.info(f"Falling back to {name}")
                    return prov.generate(prompt, **kwargs)
                except Exception as e:
                    logger.warning(f"{name} also failed: {e}")
        
        raise RuntimeError("All LLM providers failed")
    
    def chat(self, messages: List[dict], provider: Optional[str] = None, **kwargs) -> str:
        """Chat with fallback support"""
        selected_provider = provider or settings.default_llm
        
        if selected_provider in self.providers:
            try:
                return self.providers[selected_provider].chat(messages, **kwargs)
            except Exception as e:
                logger.warning(f"{selected_provider} failed: {e}")
        
        # Fallback
        for name, prov in self.providers.items():
            if name != selected_provider:
                try:
                    return prov.chat(messages, **kwargs)
                except Exception as e:
                    logger.warning(f"{name} also failed: {e}")
        
        raise RuntimeError("All LLM providers failed")
    
    def get_embeddings(self, texts: List[str], provider: Optional[str] = None) -> List[List[float]]:
        """Get embeddings with fallback"""
        selected_provider = provider or settings.default_llm
        
        if selected_provider in self.providers:
            try:
                return self.providers[selected_provider].get_embeddings(texts)
            except Exception as e:
                logger.warning(f"Embeddings failed for {selected_provider}: {e}")
        
        # Fallback
        for name, prov in self.providers.items():
            if name != selected_provider:
                try:
                    return prov.get_embeddings(texts)
                except Exception as e:
                    logger.warning(f"Embeddings failed for {name}: {e}")
        
        raise RuntimeError("Embeddings generation failed")


# Global LLM manager instance
llm_manager = LLMManager()
