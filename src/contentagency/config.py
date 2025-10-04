"""
Application configuration using Pydantic Settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_version: str = "v1"
    api_title: str = "ContentAgency API"
    api_description: str = "REST API for content brainstorming and trend research"

    # CORS Configuration
    _cors_origins_str: Optional[str] = None

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        if self._cors_origins_str:
            return [origin.strip() for origin in self._cors_origins_str.split(',') if origin.strip()]
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8000"
        ]

    # Default User Configuration
    default_user_id: str = "user_001"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Output Configuration
    output_dir: str = "output"
    trend_research_file: str = "trend_research.md"
    brainstorm_file: str = "brainstorm_suggestions.md"
    report_file: str = "report.md"

    # Model Configuration (inherit from parent .env if exists)
    openai_api_key: str = ""
    model: str = "gpt-4o"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
