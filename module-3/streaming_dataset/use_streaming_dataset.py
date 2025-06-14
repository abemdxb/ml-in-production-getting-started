#!/usr/bin/env python3
"""
StreamingDataset Usage Example

This script demonstrates how to use the StreamingDataset format for data loading.
"""

import os
import sys
import argparse
import time
import torch
from torch.utils.data import DataLoader

# Import streaming library
try:
    from streaming import StreamingDataset
except ImportError:
    print("Error: MosaicML streaming library not found.")
    print("Please install it with: pip install mosaicml-streaming")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Use StreamingDataset')
    parser.add_argument('--data-dir', type=str, default='data/streaming',
                        help='Directory containing the StreamingDataset (default: data/streaming)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for data loading (default: 32)')
    parser.add_argument('--num-workers', type=int, default=2,
                        help='Number of workers for data loading (default: 2)')
    parser.add_argument('--num-batches', type=int, default=5,
                        help='Number of batches to load (default: 5)')
    return parser.parse_args()

def main():
    """Main function to demonstrate StreamingDataset usage."""
    args = parse_args()
    
    print("=" * 50)
    print("STREAMINGDATASET USAGE EXAMPLE")
    print("=" * 50)
    
    # Create StreamingDataset
    print(f"Creating StreamingDataset from {args.data_dir}...")
    dataset = StreamingDataset(
        local=args.data_dir,  # Local path for the dataset
        remote=None,          # No remote path for this example
        shuffle=True,         # Shuffle the dataset
        batch_size=args.batch_size  # Batch size
    )
    
    # Print dataset information
    print(f"Dataset created with {len(dataset)} samples")
    
    # Get column names from the first sample
    first_sample = dataset[0]
    print(f"Dataset columns: {list(first_sample.keys())}")
    
    # Create DataLoader
    print(f"Creating DataLoader with batch_size={args.batch_size}, num_workers=0...")
    dataloader = DataLoader(
        dataset,
        batch_size=None,  # Batch size is handled by StreamingDataset
        num_workers=0  # Use single process to avoid pickling issues
    )
    
    # Load and print a few batches
    print(f"Loading {args.num_batches} batches...")
    start_time = time.time()
    
    for i, batch in enumerate(dataloader):
        if i >= args.num_batches:
            break
        
        # Print batch information
        print(f"\nBatch {i+1}:")
        print(f"  Batch keys: {list(batch.keys())}")
        
        # Print a few samples from the batch
        for key in list(batch.keys())[:3]:  # Print first 3 columns
            print(f"  {key}: {batch[key][:3]}")  # Print first 3 values
    
    end_time = time.time()
    print(f"\nLoaded {args.num_batches} batches in {end_time - start_time:.4f} seconds")
    
    # Demonstrate random access
    print("\nDemonstrating random access:")
    sample_idx = 42  # Access sample at index 42
    sample = dataset[sample_idx]
    print(f"Sample at index {sample_idx}:")
    for key in list(sample.keys())[:5]:  # Print first 5 keys
        print(f"  {key}: {sample[key]}")
    
    print("\nStreamingDataset usage example completed!")

if __name__ == "__main__":
    main()
