#!/usr/bin/env python3
"""
Custom StreamingDataset Example

This script demonstrates how to use the custom StreamingDataset implementation.
"""

import os
import sys
import argparse
import time
import torch
from torch.utils.data import DataLoader

# Import our custom implementation
from custom_streaming import CustomStreamingDataset, convert_to_streaming_format

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Custom StreamingDataset Example')
    parser.add_argument('--input-path', type=str, default='data/raw/dataset.csv',
                        help='Path to the input dataset (default: data/raw/dataset.csv)')
    parser.add_argument('--output-dir', type=str, default='data/custom_streaming',
                        help='Output directory for the streaming dataset (default: data/custom_streaming)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for data loading (default: 32)')
    parser.add_argument('--num-batches', type=int, default=5,
                        help='Number of batches to load (default: 5)')
    parser.add_argument('--skip-conversion', action='store_true',
                        help='Skip dataset conversion step')
    return parser.parse_args()

def main():
    """Main function to demonstrate CustomStreamingDataset usage."""
    args = parse_args()
    
    print("=" * 50)
    print("CUSTOM STREAMINGDATASET EXAMPLE")
    print("=" * 50)
    
    # Convert dataset to streaming format if needed
    if not args.skip_conversion:
        print(f"Converting dataset from {args.input_path} to {args.output_dir}...")
        convert_to_streaming_format(
            args.input_path,
            args.output_dir,
            compression='zstd',
            chunk_size=1000
        )
    
    # Create CustomStreamingDataset
    print(f"Creating CustomStreamingDataset from {args.output_dir}...")
    dataset = CustomStreamingDataset(
        data_path=args.output_dir,
        batch_size=args.batch_size,
        shuffle=True,
        chunk_size=1000
    )
    
    # Print dataset information
    print(f"Dataset created with {len(dataset)} samples")
    
    # Get column names from the first sample
    first_sample = dataset[0]
    print(f"Dataset columns: {list(first_sample.keys())}")
    
    # Create DataLoader
    print(f"Creating DataLoader with batch_size={args.batch_size}...")
    dataloader = DataLoader(
        dataset,
        batch_size=None,  # Batch size is handled by CustomStreamingDataset
        num_workers=0     # Use single process to avoid pickling issues
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
            if isinstance(batch[key], torch.Tensor):
                print(f"  {key}: {batch[key][:3].tolist()}")  # Print first 3 values
            else:
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
    
    print("\nCustom StreamingDataset example completed!")

if __name__ == "__main__":
    main()
