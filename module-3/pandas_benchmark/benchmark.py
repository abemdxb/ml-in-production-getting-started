#!/usr/bin/env python3
"""
Pandas Format Benchmarking Script

This script benchmarks various Pandas formats for data saving and loading operations,
focusing on measuring load time and save time.
"""

import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import string
import random
from tabulate import tabulate

# Create output directory if it doesn't exist
OUTPUT_DIR = "output_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_dataset(rows=1000, cols=100):
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
        data[f'date_col_{i}'] = [start_date + pd.Timedelta(seconds=sec) for sec in random_seconds]
    
    # Generate boolean columns (10% of columns)
    num_bool = cols - num_numeric - num_string - num_datetime
    for i in range(num_bool):
        data[f'bool_col_{i}'] = np.random.choice([True, False], size=rows)
    
    return pd.DataFrame(data)

def benchmark_format(df, format_name, save_func, load_func, iterations=5):
    """
    Benchmark saving and loading operations for a specific format.
    
    Args:
        df (pandas.DataFrame): Dataset to use for benchmarking
        format_name (str): Name of the format being benchmarked
        save_func (callable): Function to save the dataframe
        load_func (callable): Function to load the dataframe
        iterations (int): Number of iterations to run for averaging
        
    Returns:
        dict: Dictionary containing benchmark results
    """
    save_times = []
    load_times = []
    
    for i in range(iterations):
        # Benchmark save operation
        start_time = time.time()
        save_func(df)
        save_time = time.time() - start_time
        save_times.append(save_time)
        
        # Benchmark load operation
        start_time = time.time()
        load_func()
        load_time = time.time() - start_time
        load_times.append(load_time)
    
    # Calculate average times
    avg_save_time = sum(save_times) / iterations
    avg_load_time = sum(load_times) / iterations
    
    return {
        'format': format_name,
        'save_time': avg_save_time,
        'load_time': avg_load_time,
        'total_time': avg_save_time + avg_load_time
    }

def run_benchmarks(df, iterations=5):
    """
    Run benchmarks for all formats.
    
    Args:
        df (pandas.DataFrame): Dataset to use for benchmarking
        iterations (int): Number of iterations to run for averaging
        
    Returns:
        list: List of dictionaries containing benchmark results
    """
    results = []
    
    # CSV format
    csv_path = os.path.join(OUTPUT_DIR, 'data.csv')
    results.append(benchmark_format(
        df, 
        'CSV',
        lambda df: df.to_csv(csv_path, index=False),
        lambda: pd.read_csv(csv_path),
        iterations
    ))
    
    # Parquet format
    parquet_path = os.path.join(OUTPUT_DIR, 'data.parquet')
    results.append(benchmark_format(
        df, 
        'Parquet',
        lambda df: df.to_parquet(parquet_path, index=False),
        lambda: pd.read_parquet(parquet_path),
        iterations
    ))
    
    # HDF5 format
    hdf_path = os.path.join(OUTPUT_DIR, 'data.h5')
    results.append(benchmark_format(
        df, 
        'HDF5',
        lambda df: df.to_hdf(hdf_path, key='data', mode='w'),
        lambda: pd.read_hdf(hdf_path, key='data'),
        iterations
    ))
    
    # Feather format
    feather_path = os.path.join(OUTPUT_DIR, 'data.feather')
    results.append(benchmark_format(
        df, 
        'Feather',
        lambda df: df.to_feather(feather_path),
        lambda: pd.read_feather(feather_path),
        iterations
    ))
    
    # Pickle format
    pickle_path = os.path.join(OUTPUT_DIR, 'data.pkl')
    results.append(benchmark_format(
        df, 
        'Pickle',
        lambda df: df.to_pickle(pickle_path),
        lambda: pd.read_pickle(pickle_path),
        iterations
    ))
    
    # JSON format
    json_path = os.path.join(OUTPUT_DIR, 'data.json')
    results.append(benchmark_format(
        df, 
        'JSON',
        lambda df: df.to_json(json_path, orient='records'),
        lambda: pd.read_json(json_path, orient='records'),
        iterations
    ))
    
    # Excel format
    excel_path = os.path.join(OUTPUT_DIR, 'data.xlsx')
    results.append(benchmark_format(
        df, 
        'Excel',
        lambda df: df.to_excel(excel_path, index=False),
        lambda: pd.read_excel(excel_path),
        iterations
    ))
    
    return results

def display_results(results):
    """
    Display benchmark results in a table.
    
    Args:
        results (list): List of dictionaries containing benchmark results
    """
    # Sort results by total time
    sorted_results = sorted(results, key=lambda x: x['total_time'])
    
    # Prepare table data
    table_data = []
    for result in sorted_results:
        table_data.append([
            result['format'],
            f"{result['save_time']:.4f}",
            f"{result['load_time']:.4f}",
            f"{result['total_time']:.4f}"
        ])
    
    # Display table
    headers = ['Format', 'Save Time (s)', 'Load Time (s)', 'Total Time (s)']
    print("\nBenchmark Results:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def main():
    """Main function to run the benchmark."""
    # Generate dataset
    df = generate_dataset(rows=1000, cols=100)
    print(f"Dataset shape: {df.shape}")
    print(f"Dataset memory usage: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")
    
    # Run benchmarks
    print("\nRunning benchmarks...")
    results = run_benchmarks(df, iterations=5)
    
    # Display results
    display_results(results)
    
    print(f"\nBenchmark data saved to {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()
