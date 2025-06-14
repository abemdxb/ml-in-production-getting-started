#!/usr/bin/env python3
"""
MinIO Integration Example

This script demonstrates how to use StreamingDataset with MinIO for object storage.
"""

import os
import sys
import argparse
import pandas as pd
from tqdm import tqdm
import time

# Import streaming library
try:
    from streaming import StreamingDataset
except ImportError:
    print("Error: MosaicML streaming library not found.")
    print("Please install it with: pip install mosaicml-streaming")
    sys.exit(1)

# Import MinIO client
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from minio_client.minio_crud_client import MinioCRUDClient
    from minio_client.config import Config
except ImportError:
    print("Error: MinIO client not found.")
    print("Please ensure the minio_client module is available.")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='StreamingDataset with MinIO integration')
    parser.add_argument('--local-dir', type=str, default='data/streaming',
                        help='Local directory for StreamingDataset (default: data/streaming)')
    parser.add_argument('--bucket-name', type=str, default='streaming-dataset',
                        help='MinIO bucket name (default: streaming-dataset)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for data loading (default: 32)')
    parser.add_argument('--upload', action='store_true',
                        help='Upload local StreamingDataset to MinIO')
    parser.add_argument('--download', action='store_true',
                        help='Download StreamingDataset from MinIO')
    return parser.parse_args()

def upload_to_minio(local_dir, bucket_name):
    """
    Upload a StreamingDataset to MinIO.
    
    Args:
        local_dir (str): Local directory containing the StreamingDataset
        bucket_name (str): MinIO bucket name
    """
    print(f"Uploading StreamingDataset from {local_dir} to MinIO bucket {bucket_name}...")
    
    # Initialize MinIO client
    config = Config()
    minio_client = MinioCRUDClient(config)
    
    # Create bucket if it doesn't exist
    if not minio_client.bucket_exists(bucket_name):
        print(f"Creating bucket {bucket_name}...")
        minio_client.create_bucket(bucket_name)
    
    # Upload all files in the local directory
    for root, _, files in os.walk(local_dir):
        for file in tqdm(files, desc="Uploading files"):
            local_path = os.path.join(root, file)
            # Create object name relative to local_dir
            object_name = os.path.relpath(local_path, local_dir)
            
            # Upload file to MinIO
            minio_client.upload_file(bucket_name, object_name, local_path)
    
    print(f"Upload complete. StreamingDataset available in MinIO bucket {bucket_name}")

def download_from_minio(local_dir, bucket_name):
    """
    Download a StreamingDataset from MinIO.
    
    Args:
        local_dir (str): Local directory to store the StreamingDataset
        bucket_name (str): MinIO bucket name
    """
    print(f"Downloading StreamingDataset from MinIO bucket {bucket_name} to {local_dir}...")
    
    # Initialize MinIO client
    config = Config()
    minio_client = MinioCRUDClient(config)
    
    # Check if bucket exists
    if not minio_client.bucket_exists(bucket_name):
        print(f"Error: Bucket {bucket_name} does not exist.")
        return
    
    # Create local directory if it doesn't exist
    os.makedirs(local_dir, exist_ok=True)
    
    # List all objects in the bucket
    objects = minio_client.list_objects(bucket_name)
    
    # Download all objects
    for obj in tqdm(objects, desc="Downloading files"):
        object_name = obj.object_name
        local_path = os.path.join(local_dir, object_name)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download file from MinIO
        minio_client.download_file(bucket_name, object_name, local_path)
    
    print(f"Download complete. StreamingDataset available at {local_dir}")

def use_streaming_dataset(local_dir, batch_size):
    """
    Use StreamingDataset with MinIO integration.
    
    Args:
        local_dir (str): Local directory containing the StreamingDataset
        batch_size (int): Batch size for data loading
    """
    print(f"Using StreamingDataset from {local_dir}...")
    
    # Create StreamingDataset
    # For MinIO, we can use the S3 URL format: s3://bucket-name/path
    # But for this example, we'll use the local directory
    dataset = StreamingDataset(
        local=local_dir,
        remote=None,  # No remote path for this example
        shuffle=True,
        batch_size=batch_size
    )
    
    print(f"StreamingDataset created with {len(dataset)} samples")
    
    # Iterate through the dataset
    print("Iterating through the dataset...")
    start_time = time.time()
    
    for i, batch in enumerate(dataset):
        if i < 5:  # Print first 5 batches
            print(f"Batch {i+1}:")
            # Print a few keys from the batch
            keys = list(batch.keys())
            print(f"  Keys: {keys[:5]}...")
            # Print the first sample
            first_key = keys[0]
            print(f"  First sample {first_key}: {batch[first_key]}")
        
        if i >= 9:  # Only process 10 batches for this example
            break
    
    end_time = time.time()
    print(f"Processed 10 batches in {end_time - start_time:.4f} seconds")

def main():
    """Main function."""
    args = parse_args()
    
    if args.upload:
        upload_to_minio(args.local_dir, args.bucket_name)
    
    if args.download:
        download_from_minio(args.local_dir, args.bucket_name)
    
    # Use StreamingDataset
    use_streaming_dataset(args.local_dir, args.batch_size)

if __name__ == "__main__":
    main()
