"""
Configuration module for MinIO client.

This module provides configuration settings for connecting to a MinIO server.
It supports loading configuration from environment variables or direct parameter passing.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default MinIO configuration
DEFAULT_CONFIG = {
    "endpoint": "localhost:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "secure": False,  # Set to True for HTTPS
    "region": None,
}


def get_config(
    endpoint: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    secure: Optional[bool] = None,
    region: Optional[str] = None,
) -> Dict[str, any]:
    """
    Get MinIO configuration with priority:
    1. Explicitly passed parameters
    2. Environment variables
    3. Default values

    Args:
        endpoint: MinIO server endpoint (host:port)
        access_key: MinIO access key
        secret_key: MinIO secret key
        secure: Whether to use HTTPS
        region: MinIO region

    Returns:
        Dict containing MinIO configuration
    """
    config = DEFAULT_CONFIG.copy()

    # Override with environment variables if available
    if os.getenv("MINIO_ENDPOINT"):
        config["endpoint"] = os.getenv("MINIO_ENDPOINT")
    if os.getenv("MINIO_ACCESS_KEY"):
        config["access_key"] = os.getenv("MINIO_ACCESS_KEY")
    if os.getenv("MINIO_SECRET_KEY"):
        config["secret_key"] = os.getenv("MINIO_SECRET_KEY")
    if os.getenv("MINIO_SECURE"):
        config["secure"] = os.getenv("MINIO_SECURE").lower() in ("true", "1", "yes")
    if os.getenv("MINIO_REGION"):
        config["region"] = os.getenv("MINIO_REGION")

    # Override with explicitly passed parameters if provided
    if endpoint is not None:
        config["endpoint"] = endpoint
    if access_key is not None:
        config["access_key"] = access_key
    if secret_key is not None:
        config["secret_key"] = secret_key
    if secure is not None:
        config["secure"] = secure
    if region is not None:
        config["region"] = region

    return config
