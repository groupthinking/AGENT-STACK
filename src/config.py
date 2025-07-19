"""Configuration management for MCP Agent Stack."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = Field(default="MCP Agent Stack", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Agent settings
    max_summary_length: int = Field(default=100, description="Maximum summary length")
    enable_optimization: bool = Field(default=True, description="Enable content optimization")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Performance settings
    max_concurrent_agents: int = Field(default=10, description="Maximum concurrent agents")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # Security settings
    enable_input_validation: bool = Field(default=True, description="Enable input validation")
    max_input_size: int = Field(default=10000, description="Maximum input size in characters")
    
    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=8000, description="Metrics server port")
    
    # External services (for future integration)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()