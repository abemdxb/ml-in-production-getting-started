#!/usr/bin/env python3
"""
Run Script

This script provides a simple way to run the entire StreamingDataset workflow.
"""

import os
import sys
import argparse
import subprocess
import time

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run StreamingDataset workflow')
    parser.add_argument('--rows', type=int, default=10000,
                        help='Number of rows in the dataset (default: 10000)')
    parser.add_argument('--cols', type=int, default=50,
                        help='Number of columns in the dataset (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for data loading (default: 32)')
    parser.add_argument('--skip-generate', action='store_true',
                        help='Skip dataset generation step')
    parser.add_argument('--skip-convert', action='store_true',
                        help='Skip dataset conversion step')
    parser.add_argument('--skip-benchmark', action='store_true',
                        help='Skip benchmarking step')
    parser.add_argument('--minio-upload', action='store_true',
                        help='Upload dataset to MinIO')
    parser.add_argument('--bucket-name', type=str, default='streaming-dataset',
                        help='MinIO bucket name (default: streaming-dataset)')
    return parser.parse_args()

def run_command(command, description):
    """
    Run a command and print its output.
    
    Args:
        command (list): Command to run
        description (str): Description of the command
    """
    print(f"\n{'=' * 50}")
    print(f"{description}")
    print(f"{'=' * 50}")
    print(f"Running: {' '.join(command)}")
    
    start_time = time.time()
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    end_time = time.time()
    
    print(f"\nCommand completed in {end_time - start_time:.2f} seconds")
    print(f"{'=' * 50}")
    
    if process.returncode != 0:
        print(f"Error: Command failed with return code {process.returncode}")
        sys.exit(1)

def main():
    """Main function to run the workflow."""
    args = parse_args()
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    raw_dir = os.path.join(data_dir, 'raw')
    streaming_dir = os.path.join(data_dir, 'streaming')
    
    # Ensure directories exist
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(streaming_dir, exist_ok=True)
    
    # Step 1: Generate dataset
    if not args.skip_generate:
        generate_cmd = [
            sys.executable,
            os.path.join(script_dir, 'generate_dataset.py'),
            '--rows', str(args.rows),
            '--cols', str(args.cols),
            '--output-dir', raw_dir,
            '--format', 'csv'
        ]
        run_command(generate_cmd, "STEP 1: GENERATE DATASET")
    
    # Step 2: Convert dataset to StreamingDataset format
    if not args.skip_convert:
        convert_cmd = [
            sys.executable,
            os.path.join(script_dir, 'convert_dataset.py'),
            '--input-path', os.path.join(raw_dir, 'dataset.csv'),
            '--output-dir', streaming_dir,
            '--compression', 'zstd'
        ]
        run_command(convert_cmd, "STEP 2: CONVERT DATASET TO STREAMINGDATASET FORMAT")
    
    # Step 3: Benchmark StreamingDataset vs. standard loading
    if not args.skip_benchmark:
        benchmark_cmd = [
            sys.executable,
            os.path.join(script_dir, 'benchmark.py'),
            '--standard-path', os.path.join(raw_dir, 'dataset.csv'),
            '--streaming-path', streaming_dir,
            '--batch-size', str(args.batch_size),
            '--iterations', '5',
            '--output-dir', script_dir
        ]
        run_command(benchmark_cmd, "STEP 3: BENCHMARK STREAMINGDATASET VS. STANDARD LOADING")
    
    # Step 4: Upload to MinIO (optional)
    if args.minio_upload:
        minio_cmd = [
            sys.executable,
            os.path.join(script_dir, 'minio_integration.py'),
            '--local-dir', streaming_dir,
            '--bucket-name', args.bucket_name,
            '--batch-size', str(args.batch_size),
            '--upload'
        ]
        run_command(minio_cmd, "STEP 4: UPLOAD STREAMINGDATASET TO MINIO")
    
    print("\nWorkflow completed successfully!")
    print("\nTo use the StreamingDataset in your code:")
    print("\n```python")
    print("from streaming import StreamingDataset")
    print(f"dataset = StreamingDataset(local='{streaming_dir}', remote=None, batch_size={args.batch_size})")
    print("for batch in dataset:")
    print("    # Process batch")
    print("    pass")
    print("```")

if __name__ == "__main__":
    main()
