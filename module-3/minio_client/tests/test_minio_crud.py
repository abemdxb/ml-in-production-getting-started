"""
Tests for the MinIO CRUD Client

This module contains tests for the MinIO CRUD client, covering all CRUD operations
(Create, Read, Update, Delete) for both buckets and objects.

To run these tests, you need a running MinIO server. You can use the following
environment variables to configure the connection:

- MINIO_ENDPOINT: MinIO server endpoint (default: localhost:9000)
- MINIO_ACCESS_KEY: MinIO access key (default: minioadmin)
- MINIO_SECRET_KEY: MinIO secret key (default: minioadmin)
- MINIO_SECURE: Whether to use HTTPS (default: False)

Example:
    $ export MINIO_ENDPOINT=localhost:9000
    $ export MINIO_ACCESS_KEY=minioadmin
    $ export MINIO_SECRET_KEY=minioadmin
    $ pytest -xvs tests/test_minio_crud.py
"""

import os
import io
import uuid
import pytest
from pathlib import Path
import tempfile

from minio.error import S3Error

from minio_client import MinioCrudClient


# Test bucket and object names with unique prefixes to avoid conflicts
TEST_BUCKET_PREFIX = "test-bucket-"
TEST_OBJECT_PREFIX = "test-object-"


# Fixture for the MinIO client
@pytest.fixture
def minio_client():
    """Create a MinIO client for testing."""
    client = MinioCrudClient()
    
    # Check if the client can connect to the MinIO server
    if not client.is_connected():
        pytest.skip("MinIO server is not available")
    
    return client


# Fixture for a test bucket
@pytest.fixture
def test_bucket(minio_client):
    """Create a test bucket and clean it up after the test."""
    bucket_name = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    minio_client.create_bucket(bucket_name)
    
    yield bucket_name
    
    # Clean up: remove the bucket and all objects in it
    try:
        minio_client.remove_bucket(bucket_name, force=True)
    except S3Error:
        pass


# Fixture for a test object
@pytest.fixture
def test_object(minio_client, test_bucket):
    """Create a test object and clean it up after the test."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    content = "Test content"
    
    minio_client.upload_object(test_bucket, object_name, content)
    
    yield test_bucket, object_name, content
    
    # Clean up: remove the object
    try:
        minio_client.remove_object(test_bucket, object_name)
    except S3Error:
        pass


# Fixture for a test file
@pytest.fixture
def test_file():
    """Create a temporary test file."""
    # Get the path to the sample.txt file
    sample_file_path = Path(__file__).parent / "test_data" / "sample.txt"
    
    # Check if the file exists
    if not sample_file_path.exists():
        pytest.skip("Sample file not found")
    
    return str(sample_file_path)


# ===== Bucket Tests =====

def test_create_bucket(minio_client):
    """Test creating a bucket."""
    bucket_name = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    
    # Create the bucket
    result = minio_client.create_bucket(bucket_name)
    assert result is True
    
    # Verify the bucket exists
    assert minio_client.bucket_exists(bucket_name)
    
    # Clean up
    minio_client.remove_bucket(bucket_name)


def test_list_buckets(minio_client, test_bucket):
    """Test listing buckets."""
    # Get the list of buckets
    buckets = minio_client.list_buckets()
    
    # Verify the test bucket is in the list
    bucket_names = [bucket["name"] for bucket in buckets]
    assert test_bucket in bucket_names


def test_bucket_exists(minio_client, test_bucket):
    """Test checking if a bucket exists."""
    # Verify the test bucket exists
    assert minio_client.bucket_exists(test_bucket)
    
    # Verify a non-existent bucket doesn't exist
    non_existent_bucket = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    assert not minio_client.bucket_exists(non_existent_bucket)


def test_remove_bucket(minio_client):
    """Test removing a bucket."""
    bucket_name = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    
    # Create the bucket
    minio_client.create_bucket(bucket_name)
    
    # Verify the bucket exists
    assert minio_client.bucket_exists(bucket_name)
    
    # Remove the bucket
    result = minio_client.remove_bucket(bucket_name)
    assert result is True
    
    # Verify the bucket no longer exists
    assert not minio_client.bucket_exists(bucket_name)


# ===== Object Tests =====

def test_upload_object_string(minio_client, test_bucket):
    """Test uploading a string object."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    content = "Test content"
    
    # Upload the object
    result = minio_client.upload_object(test_bucket, object_name, content)
    
    # Verify the result
    assert "etag" in result
    
    # Verify the object exists
    assert minio_client.object_exists(test_bucket, object_name)
    
    # Clean up
    minio_client.remove_object(test_bucket, object_name)


def test_upload_object_bytes(minio_client, test_bucket):
    """Test uploading a bytes object."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    content = b"Test content as bytes"
    
    # Upload the object
    result = minio_client.upload_object(test_bucket, object_name, content)
    
    # Verify the result
    assert "etag" in result
    
    # Verify the object exists
    assert minio_client.object_exists(test_bucket, object_name)
    
    # Clean up
    minio_client.remove_object(test_bucket, object_name)


def test_upload_object_file(minio_client, test_bucket, test_file):
    """Test uploading a file object."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    
    # Open the file
    with open(test_file, "rb") as f:
        # Upload the object
        result = minio_client.upload_object(test_bucket, object_name, f)
    
    # Verify the result
    assert "etag" in result
    
    # Verify the object exists
    assert minio_client.object_exists(test_bucket, object_name)
    
    # Clean up
    minio_client.remove_object(test_bucket, object_name)


def test_upload_object_with_metadata(minio_client, test_bucket):
    """Test uploading an object with metadata."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    content = "Test content"
    metadata = {"custom-key": "custom-value"}
    
    # Upload the object with metadata
    result = minio_client.upload_object(
        test_bucket, object_name, content, metadata=metadata
    )
    
    # Verify the result
    assert "etag" in result
    
    # Get the object metadata
    obj_metadata = minio_client.get_object_metadata(test_bucket, object_name)
    
    # Verify the metadata (note: MinIO adds the x-amz-meta- prefix)
    assert "custom-key" in obj_metadata
    
    # Clean up
    minio_client.remove_object(test_bucket, object_name)


def test_download_object(minio_client, test_object):
    """Test downloading an object."""
    bucket_name, object_name, original_content = test_object
    
    # Download the object
    data, metadata = minio_client.download_object(bucket_name, object_name)
    
    # Verify the content
    assert data.decode("utf-8") == original_content
    
    # Verify the metadata
    assert "content_type" in metadata
    assert "etag" in metadata


def test_list_objects(minio_client, test_bucket):
    """Test listing objects in a bucket."""
    # Create multiple objects
    object_names = []
    for i in range(3):
        object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
        object_names.append(object_name)
        minio_client.upload_object(test_bucket, object_name, f"Content {i}")
    
    # List the objects
    objects = minio_client.list_objects(test_bucket)
    
    # Verify all objects are in the list
    listed_names = [obj["name"] for obj in objects]
    for name in object_names:
        assert name in listed_names
    
    # Clean up
    for name in object_names:
        minio_client.remove_object(test_bucket, name)


def test_object_exists(minio_client, test_object):
    """Test checking if an object exists."""
    bucket_name, object_name, _ = test_object
    
    # Verify the object exists
    assert minio_client.object_exists(bucket_name, object_name)
    
    # Verify a non-existent object doesn't exist
    non_existent_object = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    assert not minio_client.object_exists(bucket_name, non_existent_object)


def test_get_object_metadata(minio_client, test_object):
    """Test getting object metadata."""
    bucket_name, object_name, _ = test_object
    
    # Get the object metadata
    metadata = minio_client.get_object_metadata(bucket_name, object_name)
    
    # Verify the metadata
    assert "size" in metadata
    assert "etag" in metadata
    assert "last_modified" in metadata
    assert "content_type" in metadata


def test_update_object(minio_client, test_object):
    """Test updating an object."""
    bucket_name, object_name, original_content = test_object
    
    # Update the object with new content
    new_content = "Updated content"
    result = minio_client.update_object(bucket_name, object_name, new_content)
    
    # Verify the result
    assert "etag" in result
    
    # Download the object and verify the content
    data, _ = minio_client.download_object(bucket_name, object_name)
    assert data.decode("utf-8") == new_content


def test_copy_object(minio_client, test_object):
    """Test copying an object."""
    source_bucket, source_object, original_content = test_object
    dest_bucket = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    dest_object = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    
    # Create the destination bucket
    minio_client.create_bucket(dest_bucket)
    
    # Copy the object
    result = minio_client.copy_object(
        source_bucket, source_object, dest_bucket, dest_object
    )
    
    # Verify the result
    assert "etag" in result
    
    # Verify the object exists in the destination
    assert minio_client.object_exists(dest_bucket, dest_object)
    
    # Download the object and verify the content
    data, _ = minio_client.download_object(dest_bucket, dest_object)
    assert data.decode("utf-8") == original_content
    
    # Clean up
    minio_client.remove_object(dest_bucket, dest_object)
    minio_client.remove_bucket(dest_bucket)


def test_remove_object(minio_client, test_bucket):
    """Test removing an object."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    content = "Test content"
    
    # Upload the object
    minio_client.upload_object(test_bucket, object_name, content)
    
    # Verify the object exists
    assert minio_client.object_exists(test_bucket, object_name)
    
    # Remove the object
    result = minio_client.remove_object(test_bucket, object_name)
    assert result is True
    
    # Verify the object no longer exists
    assert not minio_client.object_exists(test_bucket, object_name)


def test_remove_objects(minio_client, test_bucket):
    """Test removing multiple objects."""
    # Create multiple objects
    object_names = []
    for i in range(3):
        object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
        object_names.append(object_name)
        minio_client.upload_object(test_bucket, object_name, f"Content {i}")
    
    # Verify the objects exist
    for name in object_names:
        assert minio_client.object_exists(test_bucket, name)
    
    # Remove the objects
    errors = minio_client.remove_objects(test_bucket, object_names)
    assert len(errors) == 0
    
    # Verify the objects no longer exist
    for name in object_names:
        assert not minio_client.object_exists(test_bucket, name)


# ===== Utility Tests =====

def test_get_presigned_url(minio_client, test_object):
    """Test generating a presigned URL."""
    bucket_name, object_name, _ = test_object
    
    # Generate a presigned URL
    url = minio_client.get_presigned_url(bucket_name, object_name, expires=60)
    
    # Verify the URL
    assert url.startswith("http")
    assert bucket_name in url
    assert object_name in url


def test_is_connected(minio_client):
    """Test checking if the client is connected."""
    # Verify the client is connected
    assert minio_client.is_connected()


# ===== Error Handling Tests =====

def test_error_handling_non_existent_bucket(minio_client):
    """Test error handling for a non-existent bucket."""
    non_existent_bucket = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    
    # Try to list objects in a non-existent bucket
    with pytest.raises(S3Error):
        minio_client.list_objects(non_existent_bucket)


def test_error_handling_non_existent_object(minio_client, test_bucket):
    """Test error handling for a non-existent object."""
    non_existent_object = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    
    # Try to download a non-existent object
    with pytest.raises(S3Error):
        minio_client.download_object(test_bucket, non_existent_object)


# ===== Integration Tests =====

def test_full_crud_workflow(minio_client):
    """Test a full CRUD workflow."""
    # Create a bucket
    bucket_name = f"{TEST_BUCKET_PREFIX}{uuid.uuid4()}"
    minio_client.create_bucket(bucket_name)
    
    # Create an object
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    original_content = "Original content"
    minio_client.upload_object(bucket_name, object_name, original_content)
    
    # Read the object
    data, metadata = minio_client.download_object(bucket_name, object_name)
    assert data.decode("utf-8") == original_content
    
    # Update the object
    updated_content = "Updated content"
    minio_client.update_object(bucket_name, object_name, updated_content)
    
    # Read the updated object
    data, metadata = minio_client.download_object(bucket_name, object_name)
    assert data.decode("utf-8") == updated_content
    
    # Delete the object
    minio_client.remove_object(bucket_name, object_name)
    
    # Verify the object is deleted
    assert not minio_client.object_exists(bucket_name, object_name)
    
    # Delete the bucket
    minio_client.remove_bucket(bucket_name)
    
    # Verify the bucket is deleted
    assert not minio_client.bucket_exists(bucket_name)


def test_large_file_handling(minio_client, test_bucket):
    """Test handling large files."""
    object_name = f"{TEST_OBJECT_PREFIX}{uuid.uuid4()}"
    
    # Create a large file (5 MB)
    size_mb = 5
    content = b"0" * (size_mb * 1024 * 1024)
    
    # Upload the large file
    result = minio_client.upload_object(test_bucket, object_name, content)
    
    # Verify the result
    assert "etag" in result
    
    # Get the object metadata
    metadata = minio_client.get_object_metadata(test_bucket, object_name)
    
    # Verify the size
    assert metadata["size"] == size_mb * 1024 * 1024
    
    # Clean up
    minio_client.remove_object(test_bucket, object_name)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
