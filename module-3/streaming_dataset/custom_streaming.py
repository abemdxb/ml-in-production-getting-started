#!/usr/bin/env python3
"""
Custom StreamingDataset Implementation

This module provides a simplified implementation of a streaming dataset
that doesn't rely on external libraries with complex dependencies.
"""

import os
import json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, IterableDataset
import random
from typing import Dict, List, Optional, Union, Any, Tuple


class CustomStreamingDataset(IterableDataset):
    """
    A custom implementation of a streaming dataset that loads data in chunks.
    
    This implementation is designed to be a simpler alternative to the MosaicML
    StreamingDataset, without the complex dependencies.
    """
    
    def __init__(
        self,
        data_path: str,
        batch_size: int = 32,
        shuffle: bool = True,
        seed: Optional[int] = None,
        chunk_size: int = 1000
    ):
        """
        Initialize the CustomStreamingDataset.
        
        Args:
            data_path: Path to the data file or directory
            batch_size: Number of samples per batch
            shuffle: Whether to shuffle the data
            seed: Random seed for reproducibility
            chunk_size: Number of samples to load at once
        """
        self.data_path = data_path
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.chunk_size = chunk_size
        
        # Determine the data format
        if os.path.isdir(data_path):
            # Check if it's a directory with our custom format
            if os.path.exists(os.path.join(data_path, 'index.json')):
                self.format = 'custom_streaming'
                self._load_index()
            else:
                raise ValueError(f"Unsupported directory format: {data_path}")
        elif data_path.endswith('.csv'):
            self.format = 'csv'
            self._get_csv_length()
        elif data_path.endswith('.parquet'):
            self.format = 'parquet'
            self._get_parquet_length()
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        # Initialize random generator
        self.rng = random.Random(self.seed)
    
    def _load_index(self):
        """Load the index file for custom streaming format."""
        index_path = os.path.join(self.data_path, 'index.json')
        with open(index_path, 'r') as f:
            self.index = json.load(f)
        
        self.length = self.index.get('samples', 0)
        self.columns = self.index.get('columns', {})
        self.shards = self.index.get('shards', [])
    
    def _get_csv_length(self):
        """Get the number of samples in a CSV file."""
        # Use pandas to get the number of rows without loading the entire file
        self.length = sum(1 for _ in open(self.data_path)) - 1  # Subtract header
    
    def _get_parquet_length(self):
        """Get the number of samples in a Parquet file."""
        # Use pyarrow to get the number of rows without loading the entire file
        import pyarrow.parquet as pq
        self.length = pq.read_metadata(self.data_path).num_rows
    
    def __len__(self):
        """Return the number of samples in the dataset."""
        return self.length
    
    def _load_chunk(self, start_idx: int, end_idx: int) -> pd.DataFrame:
        """
        Load a chunk of data.
        
        Args:
            start_idx: Start index of the chunk
            end_idx: End index of the chunk
            
        Returns:
            DataFrame containing the chunk
        """
        if self.format == 'csv':
            # Load a chunk from CSV
            return pd.read_csv(self.data_path, skiprows=range(1, start_idx + 1), nrows=end_idx - start_idx)
        elif self.format == 'parquet':
            # Load a chunk from Parquet
            return pd.read_parquet(self.data_path, engine='pyarrow')
        elif self.format == 'custom_streaming':
            # Load from our custom format
            # For simplicity, we'll load the entire shard
            # In a real implementation, you would load only the needed samples
            shard_path = os.path.join(self.data_path, self.shards[0])
            
            if shard_path.endswith('.zstd'):
                # Decompress the zstd file
                import zstandard as zstd
                with open(shard_path, 'rb') as f_in:
                    dctx = zstd.ZstdDecompressor()
                    decompressed_data = dctx.decompress(f_in.read())
                    
                    # Create a temporary file for the decompressed data
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as f_out:
                        f_out.write(decompressed_data)
                        temp_path = f_out.name
                
                # Load the decompressed parquet file
                df = pd.read_parquet(temp_path)
                
                # Remove the temporary file
                os.unlink(temp_path)
                
                return df
            else:
                # Load the shard as a pandas DataFrame
                return pd.read_parquet(shard_path)
    
    def __iter__(self):
        """
        Iterate through the dataset in batches.
        
        Yields:
            Batch of samples as a dictionary of tensors
        """
        # Create indices for the entire dataset
        indices = list(range(self.length))
        
        # Shuffle indices if requested
        if self.shuffle:
            self.rng.shuffle(indices)
        
        # Process data in chunks to avoid loading the entire dataset
        for chunk_start in range(0, self.length, self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size, self.length)
            chunk_indices = indices[chunk_start:chunk_end]
            
            # Load the chunk
            chunk_data = self._load_chunk(min(chunk_indices), max(chunk_indices) + 1)
            
            # Create batches from the chunk
            for batch_start in range(0, len(chunk_indices), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(chunk_indices))
                batch_indices = chunk_indices[batch_start:batch_end]
                
                # Extract batch data
                batch = {}
                for col in chunk_data.columns:
                    # Convert to appropriate tensor type
                    col_data = chunk_data[col].iloc[batch_indices].values
                    
                    if pd.api.types.is_numeric_dtype(chunk_data[col]):
                        # Convert numeric data to float tensor
                        batch[col] = torch.tensor(col_data, dtype=torch.float32)
                    else:
                        # Keep non-numeric data as numpy array
                        batch[col] = col_data
                
                yield batch
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """
        Get a single sample from the dataset.
        
        Args:
            idx: Index of the sample
            
        Returns:
            Sample as a dictionary
        """
        if idx < 0 or idx >= self.length:
            raise IndexError(f"Index {idx} out of range for dataset with length {self.length}")
        
        # Load a small chunk containing the requested sample
        chunk_start = (idx // self.chunk_size) * self.chunk_size
        chunk_end = min(chunk_start + self.chunk_size, self.length)
        chunk_data = self._load_chunk(chunk_start, chunk_end)
        
        # Extract the sample
        sample = {}
        for col in chunk_data.columns:
            sample[col] = chunk_data[col].iloc[idx - chunk_start]
        
        return sample


def convert_to_streaming_format(
    input_path: str,
    output_dir: str,
    compression: str = 'zstd',
    chunk_size: int = 1000
):
    """
    Convert a dataset to our custom streaming format.
    
    Args:
        input_path: Path to the input dataset
        output_dir: Output directory for the streaming dataset
        compression: Compression algorithm to use
        chunk_size: Number of samples per shard
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the dataset
    if input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    elif input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    elif input_path.endswith('.json'):
        df = pd.read_json(input_path, lines=True)
    else:
        raise ValueError(f"Unsupported file format: {input_path}")
    
    # Get column types
    columns = {}
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            columns[col] = 'int'
        elif pd.api.types.is_float_dtype(df[col]):
            columns[col] = 'float'
        elif pd.api.types.is_bool_dtype(df[col]):
            columns[col] = 'bool'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            columns[col] = 'datetime'
        else:
            columns[col] = 'str'
    
    # Split the dataset into shards
    shards = []
    for i in range(0, len(df), chunk_size):
        shard_df = df.iloc[i:i+chunk_size]
        shard_name = f"shard.{i//chunk_size:05d}.parquet"
        shard_path = os.path.join(output_dir, shard_name)
        
        # Save the shard
        shard_df.to_parquet(shard_path, index=False)
        
        # Compress the shard if requested
        if compression == 'zstd':
            import zstandard as zstd
            with open(shard_path, 'rb') as f_in:
                with open(f"{shard_path}.zstd", 'wb') as f_out:
                    compressor = zstd.ZstdCompressor(level=3)
                    f_out.write(compressor.compress(f_in.read()))
            
            # Remove the uncompressed shard
            os.remove(shard_path)
            shard_name = f"{shard_name}.zstd"
        
        shards.append(shard_name)
    
    # Create index file
    index = {
        'samples': len(df),
        'columns': columns,
        'shards': shards
    }
    
    # Save index file
    with open(os.path.join(output_dir, 'index.json'), 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"Converted dataset with {len(df)} samples to streaming format at {output_dir}")
    print(f"Created {len(shards)} shards")


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Custom StreamingDataset')
    parser.add_argument('--input-path', type=str, required=True,
                        help='Path to the input dataset')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Output directory for the streaming dataset')
    parser.add_argument('--compression', type=str, default='zstd',
                        choices=['zstd', 'none'],
                        help='Compression algorithm to use')
    parser.add_argument('--chunk-size', type=int, default=1000,
                        help='Number of samples per shard')
    
    args = parser.parse_args()
    
    convert_to_streaming_format(
        args.input_path,
        args.output_dir,
        args.compression,
        args.chunk_size
    )
