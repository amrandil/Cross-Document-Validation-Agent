"""Configuration management for the fraud detection agent."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4o", description="OpenAI model to use")
    openai_temperature: float = Field(
        default=0.2, description="LLM temperature for consistency")

    # Application Configuration
    app_name: str = Field(default="Multi-Document Fraud Detection Agent")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")

    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)

    # Agent Configuration
    max_iterations: int = Field(
        default=10, description="Maximum ReAct iterations")
    max_execution_time: int = Field(
        default=300, description="Maximum execution time in seconds")
    confidence_threshold: float = Field(
        default=0.7, description="Fraud confidence threshold")

    # Logging Configuration
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
