#!/usr/bin/env python3
"""
Benchmark Script

This script benchmarks the performance of standard dataset loading vs. StreamingDataset.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from tabulate import tabulate
import psutil
import torch
from torch.utils.data import Dataset, DataLoader
import platform

# Import streaming library
try:
    from streaming import StreamingDataset
except ImportError:
    print("Error: MosaicML streaming library not found.")
    print("Please install it with: pip install mosaicml-streaming")
    sys.exit(1)

class StandardDataset(Dataset):
    """Standard PyTorch dataset for loading data from disk."""
    
    def __init__(self, data_path):
        """
        Initialize the dataset.
        
        Args:
            data_path (str): Path to the dataset file
        """
        if data_path.endswith('.csv'):
            self.df = pd.read_csv(data_path)
        elif data_path.endswith('.parquet'):
            self.df = pd.read_parquet(data_path)
        elif data_path.endswith('.json'):
            self.df = pd.read_json(data_path, lines=True)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
    
    def __len__(self):
        """Return the number of samples in the dataset."""
        return len(self.df)
    
    def __getitem__(self, idx):
        """
        Get a sample from the dataset.
        
        Args:
            idx (int): Index of the sample
            
        Returns:
            dict: Sample as a dictionary
        """
        return self.df.iloc[idx].to_dict()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Benchmark StreamingDataset vs. standard loading')
    parser.add_argument('--standard-path', type=str, default='data/raw/dataset.csv',
                        help='Path to the standard dataset file (default: data/raw/dataset.csv)')
    parser.add_argument('--streaming-path', type=str, default='data/streaming',
                        help='Path to the StreamingDataset directory (default: data/streaming)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for data loading (default: 32)')
    parser.add_argument('--num-workers', type=int, default=4,
                        help='Number of workers for data loading (default: 4)')
    parser.add_argument('--iterations', type=int, default=10,
                        help='Number of iterations for benchmarking (default: 10)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory for benchmark results (default: .)')
    return parser.parse_args()

def benchmark_standard_loading(data_path, batch_size, num_workers, iterations):
    """
    Benchmark standard dataset loading.
    
    Args:
        data_path (str): Path to the dataset file
        batch_size (int): Batch size for data loading
        num_workers (int): Number of workers for data loading
        iterations (int): Number of iterations for benchmarking
        
    Returns:
        dict: Benchmark results
    """
    print(f"Benchmarking standard dataset loading from {data_path}...")
    
    # Create dataset and dataloader
    dataset = StandardDataset(data_path)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers
    )
    
    # Measure memory usage before loading
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Benchmark loading time
    start_time = time.time()
    
    # Iterate through the dataloader for the specified number of iterations
    for i in range(iterations):
        batch_start = time.time()
        for batch_idx, batch in enumerate(dataloader):
            # Process the batch (just access a few items to ensure it's loaded)
            _ = list(batch.keys())
            if batch_idx >= iterations:
                break
        batch_end = time.time()
        print(f"  Iteration {i+1}/{iterations}: {batch_end - batch_start:.4f} seconds")
    
    end_time = time.time()
    
    # Measure memory usage after loading
    memory_after = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Calculate results
    total_time = end_time - start_time
    avg_time_per_iteration = total_time / iterations
    memory_usage = memory_after - memory_before
    
    results = {
        'method': 'Standard Loading',
        'total_time': total_time,
        'avg_time_per_iteration': avg_time_per_iteration,
        'memory_usage': memory_usage,
        'dataset_size': len(dataset)
    }
    
    print(f"  Total time: {total_time:.4f} seconds")
    print(f"  Average time per iteration: {avg_time_per_iteration:.4f} seconds")
    print(f"  Memory usage: {memory_usage:.2f} MB")
    
    return results

def benchmark_streaming_loading(data_path, batch_size, num_workers, iterations):
    """
    Benchmark StreamingDataset loading.
    
    Args:
        data_path (str): Path to the StreamingDataset directory
        batch_size (int): Batch size for data loading
        num_workers (int): Number of workers for data loading
        iterations (int): Number of iterations for benchmarking
        
    Returns:
        dict: Benchmark results
    """
    print(f"Benchmarking StreamingDataset loading from {data_path}...")
    
    # Create StreamingDataset and dataloader
    dataset = StreamingDataset(
        local=data_path,  # Local path for caching
        remote=None,      # No remote path for this benchmark
        shuffle=True,
        batch_size=batch_size
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=None,  # Batch size is handled by StreamingDataset
        num_workers=num_workers
    )
    
    # Measure memory usage before loading
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Benchmark loading time
    start_time = time.time()
    
    # Iterate through the dataloader for the specified number of iterations
    for i in range(iterations):
        batch_start = time.time()
        for batch_idx, batch in enumerate(dataloader):
            # Process the batch (just access a few items to ensure it's loaded)
            _ = list(batch.keys())
            if batch_idx >= iterations:
                break
        batch_end = time.time()
        print(f"  Iteration {i+1}/{iterations}: {batch_end - batch_start:.4f} seconds")
    
    end_time = time.time()
    
    # Measure memory usage after loading
    memory_after = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Calculate results
    total_time = end_time - start_time
    avg_time_per_iteration = total_time / iterations
    memory_usage = memory_after - memory_before
    
    results = {
        'method': 'StreamingDataset',
        'total_time': total_time,
        'avg_time_per_iteration': avg_time_per_iteration,
        'memory_usage': memory_usage,
        'dataset_size': len(dataset)
    }
    
    print(f"  Total time: {total_time:.4f} seconds")
    print(f"  Average time per iteration: {avg_time_per_iteration:.4f} seconds")
    print(f"  Memory usage: {memory_usage:.2f} MB")
    
    return results

def plot_results(results, output_dir):
    """
    Plot benchmark results.
    
    Args:
        results (list): List of benchmark results
        output_dir (str): Output directory for the plot
    """
    # Extract data for plotting
    methods = [r['method'] for r in results]
    times = [r['avg_time_per_iteration'] for r in results]
    memory = [r['memory_usage'] for r in results]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot average time per iteration
    ax1.bar(methods, times, color=['blue', 'green'])
    ax1.set_ylabel('Average Time per Iteration (s)')
    ax1.set_title('Loading Time Comparison')
    
    # Add time labels on top of bars
    for i, v in enumerate(times):
        ax1.text(i, v + 0.01, f'{v:.4f}s', ha='center')
    
    # Plot memory usage
    ax2.bar(methods, memory, color=['blue', 'green'])
    ax2.set_ylabel('Memory Usage (MB)')
    ax2.set_title('Memory Usage Comparison')
    
    # Add memory labels on top of bars
    for i, v in enumerate(memory):
        ax2.text(i, v + 0.5, f'{v:.2f} MB', ha='center')
    
    # Add overall title
    plt.suptitle('StreamingDataset vs. Standard Loading Benchmark')
    plt.tight_layout()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, 'benchmark_results.png')
    plt.savefig(plot_path)
    print(f"Benchmark plot saved to {plot_path}")

def save_results(results, output_dir):
    """
    Save benchmark results to a file.
    
    Args:
        results (list): List of benchmark results
        output_dir (str): Output directory for the results
    """
    # Prepare results for tabulation
    table_data = []
    for r in results:
        table_data.append([
            r['method'],
            f"{r['total_time']:.4f}",
            f"{r['avg_time_per_iteration']:.4f}",
            f"{r['memory_usage']:.2f}",
            r['dataset_size']
        ])
    
    # Calculate speedup
    if len(results) == 2:
        standard_time = results[0]['avg_time_per_iteration']
        streaming_time = results[1]['avg_time_per_iteration']
        speedup = standard_time / streaming_time
    else:
        speedup = "N/A"
    
    # Get system information
    system_info = {
        "OS": platform.system() + " " + platform.release(),
        "Python Version": platform.python_version(),
        "CPU": f"{psutil.cpu_count(logical=False)} physical cores, {psutil.cpu_count(logical=True)} logical cores",
        "Memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
    }
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results to file
    results_path = os.path.join(output_dir, 'benchmark_results.txt')
    with open(results_path, 'w') as f:
        f.write("# StreamingDataset vs. Standard Loading Benchmark Results\n\n")
        
        f.write("## Results\n")
        f.write(tabulate(
            table_data,
            headers=['Method', 'Total Time (s)', 'Avg Time/Iteration (s)', 'Memory Usage (MB)', 'Dataset Size'],
            tablefmt='grid'
        ))
        f.write("\n\n")
        
        f.write(f"Speedup (Standard/Streaming): {speedup:.2f}x\n\n")
        
        f.write("## System Information\n")
        for key, value in system_info.items():
            f.write(f"{key}: {value}\n")
    
    print(f"Benchmark results saved to {results_path}")

def main():
    """Main function to run the benchmark."""
    args = parse_args()
    
    print("=" * 50)
    print("STREAMINGDATASET VS. STANDARD LOADING BENCHMARK")
    print("=" * 50)
    
    # Run benchmarks
    standard_results = benchmark_standard_loading(
        args.standard_path,
        args.batch_size,
        args.num_workers,
        args.iterations
    )
    
    print("\n" + "-" * 50 + "\n")
    
    streaming_results = benchmark_streaming_loading(
        args.streaming_path,
        args.batch_size,
        args.num_workers,
        args.iterations
    )
    
    # Combine results
    results = [standard_results, streaming_results]
    
    # Plot results
    plot_results(results, args.output_dir)
    
    # Save results
    save_results(results, args.output_dir)
    
    print("\n" + "=" * 50)
    print("Benchmark completed!")

if __name__ == "__main__":
    main()
