"""
Configuration management for AI Content Growth Platform
"""

from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/ai_content"
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm: str = "openai"  # Can be: openai, anthropic, ollama
    ollama_base_url: str = "http://localhost:11434"
    
    # LinkedIn
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None
    auto_post_enabled: bool = True
    post_schedule: str = "daily"  # daily, 3times_weekly, weekly
    linkedin_api_key: Optional[str] = None  # For official API (if using)
    
    # Buffer API (Official LinkedIn Automation)
    buffer_access_token: Optional[str] = None
    
    # Google Search API
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Server
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Settings
    debug: bool = True
    log_level: str = "INFO"
    jwt_secret: str = "your-secret-key"
    
    # Content Settings
    optimal_post_time_est: str = "09:00"  # Best posting time
    posts_per_week: int = 4
    topics_to_learn_per_week: int = 1
    
    # AI Settings
    max_research_sources: int = 20
    max_content_variations: int = 4
    engagement_optimization_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Verify API keys are set
def validate_settings():
    """Validate that required settings are configured"""
    if settings.debug:
        print("⚠️  Running in DEBUG mode")
    
    if not settings.openai_api_key and settings.default_llm == "openai":
        print("⚠️  Warning: OpenAI API key not set. Set OPENAI_API_KEY in .env")
    
    if not settings.linkedin_email or not settings.linkedin_password:
        print("⚠️  Warning: LinkedIn credentials not set. Auto-posting will be disabled.")
    
    return True
