#!/usr/bin/env python3
"""
Dataset Generator Script

This script generates a synthetic dataset with various data types for testing
the StreamingDataset conversion process.
"""

import os
import numpy as np
import pandas as pd
import random
import string
from datetime import datetime, timedelta
import argparse
from tqdm import tqdm

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a synthetic dataset')
    parser.add_argument('--rows', type=int, default=10000,
                        help='Number of rows in the dataset (default: 10000)')
    parser.add_argument('--cols', type=int, default=50,
                        help='Number of columns in the dataset (default: 50)')
    parser.add_argument('--output-dir', type=str, default='data/raw',
                        help='Output directory for the dataset (default: data/raw)')
    parser.add_argument('--format', type=str, default='csv',
                        choices=['csv', 'parquet', 'json'],
                        help='Output format for the dataset (default: csv)')
    return parser.parse_args()

def generate_dataset(rows=10000, cols=50):
    """
    Generate a synthetic dataset with specified number of rows and columns.
    
    Args:
        rows (int): Number of rows in the dataset
        cols (int): Number of columns in the dataset
        
    Returns:
        pandas.DataFrame: Generated dataset
    """
    print(f"Generating dataset with {rows} rows and {cols} columns...")
    
    # Create a dictionary to hold our data
    data = {}
    
    # Generate numeric columns (50% of columns)
    num_numeric = cols // 2
    for i in range(num_numeric):
        if i % 2 == 0:
            # Integer column
            data[f'int_col_{i}'] = np.random.randint(0, 1000, size=rows)
        else:
            # Float column
            data[f'float_col_{i}'] = np.random.random(size=rows) * 1000
    
    # Generate string columns (30% of columns)
    num_string = int(cols * 0.3)
    for i in range(num_string):
        # Generate random strings of length 10
        data[f'str_col_{i}'] = [''.join(random.choices(string.ascii_letters, k=10)) for _ in range(rows)]
    
    # Generate datetime columns (10% of columns)
    num_datetime = int(cols * 0.1)
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    delta = (end_date - start_date).total_seconds()
    
    for i in range(num_datetime):
        random_seconds = np.random.randint(0, delta, size=rows)
        data[f'date_col_{i}'] = [start_date + timedelta(seconds=int(sec)) for sec in random_seconds]
    
    # Generate boolean columns (10% of columns)
    num_bool = cols - num_numeric - num_string - num_datetime
    for i in range(num_bool):
        data[f'bool_col_{i}'] = np.random.choice([True, False], size=rows)
    
    # Add a unique ID column
    data['id'] = [f"id_{i}" for i in range(rows)]
    
    return pd.DataFrame(data)

def save_dataset(df, output_dir, format='csv'):
    """
    Save the dataset to disk in the specified format.
    
    Args:
        df (pandas.DataFrame): Dataset to save
        output_dir (str): Directory to save the dataset
        format (str): Format to save the dataset (csv, parquet, json)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if format == 'csv':
        output_path = os.path.join(output_dir, 'dataset.csv')
        df.to_csv(output_path, index=False)
    elif format == 'parquet':
        output_path = os.path.join(output_dir, 'dataset.parquet')
        df.to_parquet(output_path, index=False)
    elif format == 'json':
        output_path = os.path.join(output_dir, 'dataset.json')
        df.to_json(output_path, orient='records', lines=True)
    
    print(f"Dataset saved to {output_path}")
    print(f"Dataset shape: {df.shape}")
    print(f"Dataset memory usage: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")
    print(f"Dataset columns: {', '.join(df.columns[:5])}... (total: {len(df.columns)})")

def main():
    """Main function to generate the dataset."""
    args = parse_args()
    
    # Generate the dataset
    df = generate_dataset(rows=args.rows, cols=args.cols)
    
    # Save the dataset
    save_dataset(df, args.output_dir, args.format)
    
    print("Dataset generation complete!")

if __name__ == "__main__":
    main()
