# MinIO CRUD Client

A comprehensive Python client for performing CRUD (Create, Read, Update, Delete) operations on a MinIO object storage server.

## Features

- **Complete CRUD Operations**: Full support for creating, reading, updating, and deleting both buckets and objects
- **Flexible Configuration**: Configure via environment variables, direct parameters, or configuration files
- **Comprehensive Error Handling**: Detailed error reporting and logging
- **Type Hints**: Full type annotation for better IDE support
- **Extensive Testing**: Comprehensive test suite covering all functionality

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The client can be configured in multiple ways:

### Environment Variables

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export MINIO_SECURE=false
export MINIO_REGION=us-east-1
```

### Direct Parameters

```python
from minio_client import MinioCrudClient

client = MinioCrudClient(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
    region="us-east-1"
)
```

### Default Configuration

If no configuration is provided, the client will use the following defaults:

- **endpoint**: localhost:9000
- **access_key**: minioadmin
- **secret_key**: minioadmin
- **secure**: False
- **region**: None

## Usage Examples

### Initialize the Client

```python
from minio_client import MinioCrudClient

# Create a client with default configuration
client = MinioCrudClient()

# Or with custom configuration
client = MinioCrudClient(
    endpoint="minio.example.com:9000",
    access_key="your-access-key",
    secret_key="your-secret-key",
    secure=True
)
```

### Bucket Operations

```python
# Create a bucket
client.create_bucket("my-bucket")

# List all buckets
buckets = client.list_buckets()
for bucket in buckets:
    print(f"Bucket: {bucket['name']}, Created: {bucket['creation_date']}")

# Check if a bucket exists
if client.bucket_exists("my-bucket"):
    print("Bucket exists")

# Remove a bucket (and all objects in it)
client.remove_bucket("my-bucket", force=True)
```

### Object Operations

```python
# Upload a string
client.upload_object("my-bucket", "text-object.txt", "Hello, MinIO!")

# Upload bytes
client.upload_object("my-bucket", "bytes-object.bin", b"\x00\x01\x02\x03")

# Upload a file
with open("local-file.txt", "rb") as f:
    client.upload_object("my-bucket", "file-object.txt", f)

# Upload with metadata and tags
client.upload_object(
    "my-bucket",
    "metadata-object.txt",
    "Content with metadata",
    metadata={"created-by": "minio-client"},
    tags={"category": "documentation", "version": "1.0"}
)

# Download an object
data, metadata = client.download_object("my-bucket", "text-object.txt")
print(data.decode("utf-8"))  # "Hello, MinIO!"

# List objects in a bucket
objects = client.list_objects("my-bucket")
for obj in objects:
    print(f"Object: {obj['name']}, Size: {obj['size']}")

# Check if an object exists
if client.object_exists("my-bucket", "text-object.txt"):
    print("Object exists")

# Get object metadata
metadata = client.get_object_metadata("my-bucket", "metadata-object.txt")
print(f"Content type: {metadata['content_type']}")
print(f"Size: {metadata['size']}")

# Update an object
client.update_object("my-bucket", "text-object.txt", "Updated content")

# Copy an object
client.copy_object(
    "my-bucket", "text-object.txt",
    "backup-bucket", "text-object-backup.txt"
)

# Remove an object
client.remove_object("my-bucket", "text-object.txt")

# Remove multiple objects
client.remove_objects("my-bucket", ["object1.txt", "object2.txt"])
```

### Utility Operations

```python
# Generate a presigned URL (for temporary access)
url = client.get_presigned_url("my-bucket", "private-object.txt", expires=3600)
print(f"Access the object at: {url}")

# Check if the client is connected to the MinIO server
if client.is_connected():
    print("Connected to MinIO server")
```

## Error Handling

The client provides detailed error handling. All operations that interact with the MinIO server can raise `S3Error` exceptions, which should be caught and handled appropriately:

```python
from minio.error import S3Error

try:
    client.download_object("non-existent-bucket", "object.txt")
except S3Error as e:
    print(f"Error: {e.code} - {e.message}")
```

## Running Tests

The client includes a comprehensive test suite. To run the tests:

```bash
# Make sure a MinIO server is running
pytest -xvs minio_client/tests/test_minio_crud.py
```
