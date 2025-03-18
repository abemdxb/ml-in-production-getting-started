"""
Example script demonstrating how to use the MinIO CRUD client.

This script shows basic usage of the MinIO CRUD client for common operations.
"""

import os
import logging
from minio_client import MinioCrudClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run the example script."""
    # Create a client with default configuration
    client = MinioCrudClient()
    
    # Check if the client is connected to the MinIO server
    if not client.is_connected():
        logger.error("Could not connect to MinIO server. Make sure it's running.")
        return
    
    logger.info("Connected to MinIO server")
    
    # Create a test bucket
    bucket_name = "example-bucket"
    if client.create_bucket(bucket_name):
        logger.info(f"Created bucket: {bucket_name}")
    else:
        logger.info(f"Bucket already exists: {bucket_name}")
    
    # List all buckets
    buckets = client.list_buckets()
    logger.info(f"Available buckets: {', '.join(bucket['name'] for bucket in buckets)}")
    
    # Upload a text object
    text_object_name = "hello.txt"
    text_content = "Hello, MinIO!"
    result = client.upload_object(bucket_name, text_object_name, text_content)
    logger.info(f"Uploaded text object: {text_object_name}, ETag: {result['etag']}")
    
    # Upload a binary object
    binary_object_name = "binary.dat"
    binary_content = b"\x00\x01\x02\x03\x04\x05"
    result = client.upload_object(bucket_name, binary_object_name, binary_content)
    logger.info(f"Uploaded binary object: {binary_object_name}, ETag: {result['etag']}")
    
    # Upload an object with metadata and tags
    metadata_object_name = "metadata.txt"
    metadata_content = "This object has metadata and tags"
    metadata = {"created-by": "example-script", "purpose": "demonstration"}
    tags = {"category": "example", "version": "1.0"}
    
    result = client.upload_object(
        bucket_name,
        metadata_object_name,
        metadata_content,
        metadata=metadata,
        tags=tags,
    )
    logger.info(f"Uploaded object with metadata: {metadata_object_name}")
    
    # List objects in the bucket
    objects = client.list_objects(bucket_name)
    logger.info(f"Objects in bucket {bucket_name}:")
    for obj in objects:
        logger.info(f"  - {obj['name']} ({obj['size']} bytes)")
    
    # Download an object
    data, metadata = client.download_object(bucket_name, text_object_name)
    logger.info(f"Downloaded object {text_object_name}: {data.decode('utf-8')}")
    logger.info(f"Object metadata: {metadata}")
    
    # Get object metadata
    metadata = client.get_object_metadata(bucket_name, metadata_object_name)
    logger.info(f"Metadata for {metadata_object_name}: {metadata}")
    
    # Update an object
    updated_content = "Updated content"
    client.update_object(bucket_name, text_object_name, updated_content)
    logger.info(f"Updated object: {text_object_name}")
    
    # Download the updated object
    data, _ = client.download_object(bucket_name, text_object_name)
    logger.info(f"Updated object content: {data.decode('utf-8')}")
    
    # Generate a presigned URL
    url = client.get_presigned_url(bucket_name, text_object_name, expires=3600)
    logger.info(f"Presigned URL for {text_object_name}: {url}")
    
    # Copy an object
    copy_object_name = "hello-copy.txt"
    result = client.copy_object(bucket_name, text_object_name, bucket_name, copy_object_name)
    logger.info(f"Copied {text_object_name} to {copy_object_name}")
    
    # Remove an object
    client.remove_object(bucket_name, text_object_name)
    logger.info(f"Removed object: {text_object_name}")
    
    # Remove multiple objects
    client.remove_objects(bucket_name, [binary_object_name, metadata_object_name, copy_object_name])
    logger.info("Removed multiple objects")
    
    # Remove the bucket
    client.remove_bucket(bucket_name, force=True)
    logger.info(f"Removed bucket: {bucket_name}")


if __name__ == "__main__":
    main()
