"""
Configuration module for YouTube Archive Agent.

Manages all configuration settings with validation.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)


class Config(BaseModel):
    """Configuration settings for the YouTube Archive Agent."""

    # YouTube watchlist URL
    WATCHLIST_URL: str = Field(
        default="",
        description="YouTube playlist or watch-later URL"
    )

    # Directory paths
    DOWNLOAD_DIR: Path = Field(
        default=Path("downloads"),
        description="Directory for raw video downloads"
    )

    COMPRESS_DIR: Path = Field(
        default=Path("compressed"),
        description="Directory for compressed videos"
    )

    # Database settings
    DATABASE_PATH: Path = Field(
        default=Path("archive.db"),
        description="Path to SQLite database file"
    )

    # rclone settings
    RCLONE_REMOTE: str = Field(
        default="gdrive:/youtube_archive/",
        description="rclone remote path for Google Drive"
    )

    # Agent loop settings
    CHECK_INTERVAL: int = Field(
        default=3600,
        description="Interval between checks in seconds (default: 1 hour)"
    )

    # Compression settings
    MAX_RESOLUTION: str = Field(
        default="720",
        description="Maximum video resolution (e.g., '720', '1080')"
    )

    VIDEO_CODEC: str = Field(
        default="libx264",
        description="Video codec for compression"
    )

    AUDIO_CODEC: str = Field(
        default="aac",
        description="Audio codec for compression"
    )

    VIDEO_PRESET: str = Field(
        default="slow",
        description="FFmpeg encoding preset (faster = larger file, slower = smaller file)"
    )

    CRF: int = Field(
        default=28,
        description="Constant Rate Factor (18-28, higher = smaller file, lower quality)"
    )

    AUDIO_BITRATE: str = Field(
        default="128k",
        description="Audio bitrate"
    )

    # Retry settings
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed operations"
    )

    RETRY_DELAY: int = Field(
        default=10,
        description="Delay between retries in seconds"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    LOG_FILE: Optional[Path] = Field(
        default=Path("youtube_archive.log"),
        description="Path to log file (None for console only)"
    )

    # Cleanup settings
    DELETE_AFTER_UPLOAD: bool = Field(
        default=True,
        description="Delete local files after successful upload"
    )

    @field_validator('DOWNLOAD_DIR', 'COMPRESS_DIR')
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator('CHECK_INTERVAL', 'MAX_RETRIES', 'RETRY_DELAY', 'CRF')
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Ensure positive integers."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v

    class Config:
        """Pydantic configuration."""
        validate_assignment = True


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables or config file.

    Args:
        config_file: Optional path to Python config file

    Returns:
        Config object with settings
    """
    config_dict = {}

    # Load from config file if provided
    if config_file and os.path.exists(config_file):
        logger.info(f"Loading configuration from {config_file}")
        with open(config_file) as f:
            exec(f.read(), config_dict)

    # Override with environment variables if present
    env_vars = {
        'WATCHLIST_URL': os.getenv('YT_WATCHLIST_URL'),
        'DOWNLOAD_DIR': os.getenv('YT_DOWNLOAD_DIR'),
        'COMPRESS_DIR': os.getenv('YT_COMPRESS_DIR'),
        'DATABASE_PATH': os.getenv('YT_DATABASE_PATH'),
        'RCLONE_REMOTE': os.getenv('YT_RCLONE_REMOTE'),
        'CHECK_INTERVAL': os.getenv('YT_CHECK_INTERVAL'),
        'MAX_RESOLUTION': os.getenv('YT_MAX_RESOLUTION'),
        'LOG_LEVEL': os.getenv('YT_LOG_LEVEL'),
        'LOG_FILE': os.getenv('YT_LOG_FILE'),
    }

    # Filter out None values and update config_dict
    for key, value in env_vars.items():
        if value is not None:
            config_dict[key] = value

    return Config(**config_dict)


def get_default_config() -> Config:
    """Get default configuration instance."""
    return Config()
