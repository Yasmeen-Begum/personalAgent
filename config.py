"""Configuration management for the Personal Life Automation Agent System."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Storage Configuration
    MEMORY_BANK_PATH: Path = Path(os.getenv("MEMORY_BANK_PATH", "./data/memory_bank"))
    STATE_PERSISTENCE_PATH: Path = Path(os.getenv("STATE_PERSISTENCE_PATH", "./data/state"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Create storage directories if they don't exist
        cls.MEMORY_BANK_PATH.mkdir(parents=True, exist_ok=True)
        cls.STATE_PERSISTENCE_PATH.mkdir(parents=True, exist_ok=True)


# Singleton instance
config = Config()
