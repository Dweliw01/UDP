"""Configuration management for Ultra Deep Research."""

from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    perplexity_api_key: str = os.getenv("PERPLEXITY_API_KEY", "")

    # Model Configuration
    query_model: str = os.getenv("QUERY_MODEL", "claude-haiku-4-5")
    synthesis_model: str = os.getenv("SYNTHESIS_MODEL", "claude-sonnet-4-5")

    # Search Configuration
    max_concurrent_searches: int = 15
    search_timeout: int = 30
    retry_attempts: int = 3

    # Query Configuration
    default_num_queries: int = 100

    # Output Configuration
    default_output_file: str = "research_report.md"

    def validate(self) -> bool:
        """Validate that required config is present."""
        return bool(self.anthropic_api_key and self.perplexity_api_key)


config = Config()
