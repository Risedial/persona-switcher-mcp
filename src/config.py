"""Configuration management from environment variables."""

import os
from pathlib import Path


class Config:
    """Server configuration from environment variables."""

    # Personas directory
    PERSONAS_DIR = Path(os.getenv("PERSONAS_DIR", "./personas"))

    # Logging level
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Auto-reload file changes
    AUTO_RELOAD = os.getenv("AUTO_RELOAD", "false").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate configuration and normalize values."""
        # Resolve personas directory to absolute path
        if not cls.PERSONAS_DIR.is_absolute():
            cls.PERSONAS_DIR = cls.PERSONAS_DIR.resolve()

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if cls.LOG_LEVEL.upper() not in valid_levels:
            cls.LOG_LEVEL = "INFO"
        else:
            cls.LOG_LEVEL = cls.LOG_LEVEL.upper()
