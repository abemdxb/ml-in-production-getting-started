"""
MinIO CRUD Client Package

This package provides a client for performing CRUD operations on a MinIO server.
"""

from .minio_crud_client import MinioCrudClient
from .config import get_config

__all__ = ["MinioCrudClient", "get_config"]
