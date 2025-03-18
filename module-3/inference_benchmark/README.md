# Inference Performance Benchmark

This benchmark compares the performance of machine learning model inference using single process versus multiple processes.

## Overview

The benchmark:
1. Creates a simple machine learning model (Random Forest)
2. Generates synthetic data for inference
3. Runs inference in single-process mode
4. Runs the same inference using multiple processes (utilizing Python's multiprocessing)
5. Measures and compares execution times

## Python Concurrency: Single vs. Multiple Processes

- **Single Process**: Runs code sequentially in one process. Python's Global Interpreter Lock (GIL) means that even with threads, CPU-bound tasks can only execute one at a time within a process.

- **Multiple Processes**: Uses Python's `multiprocessing` module to create separate Python processes. Each process has its own Python interpreter and memory space, allowing true parallel execution on multiple CPU cores. This bypasses the GIL limitation.

For ML inference tasks:
- Single process is simpler but limited to one CPU core
- Multiple processes can utilize all available CPU cores, potentially speeding up batch inference significantly

## Usage

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the benchmark:
   ```
   python benchmark.py
   ```
   
   For a quicker test with a smaller dataset:
   ```
   python quick_test.py
   ```

3. View the results in the console output and in `results.txt` (when running the full benchmark)

## Parameters

You can modify the following parameters in the benchmark script:
- `n_samples`: Number of samples to generate for inference
- `n_features`: Number of features in the synthetic data
- `n_processes`: Number of processes to use for multiprocessing
- `batch_size`: Size of batches for processing

## Results Interpretation

The benchmark reports:
- Time taken for single-process inference
- Time taken for multi-process inference
- Speedup ratio (single-process time / multi-process time)
- Efficiency (speedup / number of processes)
