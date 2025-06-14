#!/usr/bin/env python3
"""
Dataset Conversion Script

This script converts a dataset to the StreamingDataset format (MDS) from MosaicML.
"""

import os
import sys
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm
import uuid
import json
from datetime import datetime
import time

# Import streaming library for MDS format
try:
    from streaming import MDSWriter
except ImportError:
    print("Error: MosaicML streaming library not found.")
    print("Please install it with: pip install mosaicml-streaming")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Convert dataset to StreamingDataset format')
    parser.add_argument('--input-path', type=str, default='data/raw/dataset.csv',
                        help='Path to the input dataset (default: data/raw/dataset.csv)')
    parser.add_argument('--output-dir', type=str, default='data/streaming',
                        help='Output directory for the StreamingDataset (default: data/streaming)')
    parser.add_argument('--compression', type=str, default='zstd',
                        choices=['zstd', 'lz4', 'none'],
                        help='Compression algorithm to use (default: zstd)')
    parser.add_argument('--hashes', type=int, default=10,
                        help='Number of hashes for sharding (default: 10)')
    parser.add_argument('--size-limit', type=int, default=1024*1024*16,
                        help='Size limit for each shard in bytes (default: 16MB)')
    return parser.parse_args()

def load_dataset(input_path):
    """
    Load the dataset from disk.
    
    Args:
        input_path (str): Path to the input dataset
        
    Returns:
        pandas.DataFrame: Loaded dataset
    """
    print(f"Loading dataset from {input_path}...")
    
    if input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    elif input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    elif input_path.endswith('.json'):
        df = pd.read_json(input_path, lines=True)
    else:
        raise ValueError(f"Unsupported file format: {input_path}")
    
    print(f"Dataset loaded with shape: {df.shape}")
    return df

def get_column_types(df):
    """
    Determine the column types for the dataset.
    
    Args:
        df (pandas.DataFrame): Dataset
        
    Returns:
        dict: Dictionary mapping column names to their types
    """
    column_types = {}
    
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            column_types[col] = 'int'
        elif pd.api.types.is_float_dtype(df[col]):
            column_types[col] = 'float'
        elif pd.api.types.is_bool_dtype(df[col]):
            column_types[col] = 'bool'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            column_types[col] = 'datetime'
        else:
            column_types[col] = 'str'
    
    return column_types

def convert_to_mds(df, output_dir, compression='zstd', hashes=10, size_limit=1024*1024*16):
    """
    Convert the dataset to MDS format.
    
    Args:
        df (pandas.DataFrame): Dataset to convert
        output_dir (str): Output directory for the MDS dataset
        compression (str): Compression algorithm to use
        hashes (int): Number of hashes for sharding
        size_limit (int): Size limit for each shard in bytes
    """
    print(f"Converting dataset to MDS format...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get column types
    column_types = get_column_types(df)
    print(f"Column types: {json.dumps(column_types, indent=2)}")
    
    # Create columns dictionary for MDSWriter
    columns = {}
    for col, col_type in column_types.items():
        if col_type == 'int':
            columns[col] = 'int'
        elif col_type == 'float':
            columns[col] = 'float32'  # Use float32 encoding
        elif col_type == 'bool':
            columns[col] = 'int'  # Store booleans as integers (0 or 1)
        elif col_type == 'datetime':
            columns[col] = 'str'  # Store datetimes as strings
        else:
            columns[col] = 'str'
    
    # Create MDSWriter
    print(f"Creating MDSWriter with output directory: {output_dir}")
    writer = MDSWriter(
        out=output_dir,
        columns=columns,
        compression=compression,
        # Use default hashes parameter
        size_limit=size_limit
    )
    
    # Convert each row to a sample
    print(f"Writing {len(df)} samples to MDS format...")
    start_time = time.time()
    
    with writer as out:
        for _, row in tqdm(df.iterrows(), total=len(df)):
            # Convert row to dictionary
            sample = {}
            for col, value in row.items():
                if column_types[col] == 'datetime':
                    # Convert datetime to ISO format string
                    sample[col] = value.isoformat() if pd.notna(value) else None
                elif column_types[col] == 'bool':
                    # Convert boolean to integer (0 or 1)
                    sample[col] = int(value) if pd.notna(value) else 0
                else:
                    sample[col] = value
            
            # Write sample to MDS
            out.write(sample)
    
    end_time = time.time()
    print(f"Conversion completed in {end_time - start_time:.2f} seconds")
    print(f"MDS dataset saved to {output_dir}")

def main():
    """Main function to convert the dataset."""
    args = parse_args()
    
    # Load the dataset
    df = load_dataset(args.input_path)
    
    # Convert to MDS format
    convert_to_mds(
        df,
        args.output_dir,
        compression=args.compression,
        hashes=args.hashes,
        size_limit=args.size_limit
    )
    
    print("Dataset conversion complete!")

if __name__ == "__main__":
    main()
