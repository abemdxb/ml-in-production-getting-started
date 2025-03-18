#!/usr/bin/env python3
"""
Quick test script for the inference benchmark with a smaller dataset.
"""

import os
import sys
import time
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
import multiprocessing as mp
from functools import partial

# Smaller parameters for quick testing
N_SAMPLES = 10000  # Reduced number of samples
N_FEATURES = 10    # Reduced number of features
N_PROCESSES = min(mp.cpu_count(), 4)  # Limit to 4 processes to reduce overhead
BATCH_SIZE = N_SAMPLES // N_PROCESSES

def create_model():
    """Create and train a simple Random Forest model."""
    print("Creating and training model...")
    X_train, y_train = make_regression(
        n_samples=1000, 
        n_features=N_FEATURES, 
        noise=0.1, 
        random_state=42
    )
    
    model = RandomForestRegressor(n_estimators=10, random_state=42)  # Reduced n_estimators
    model.fit(X_train, y_train)
    
    return model

def generate_inference_data():
    """Generate synthetic data for inference."""
    print(f"Generating {N_SAMPLES} samples for inference...")
    X_test, _ = make_regression(
        n_samples=N_SAMPLES, 
        n_features=N_FEATURES, 
        noise=0.1, 
        random_state=24
    )
    return X_test

def single_process_inference(model, data):
    """Run inference using a single process."""
    print("Running single-process inference...")
    start_time = time.time()
    predictions = model.predict(data)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Single-process inference completed in {elapsed_time:.4f} seconds")
    
    return elapsed_time, predictions

def process_batch(model, batch):
    """Process a batch of data (used by multiprocessing)."""
    return model.predict(batch)

def multi_process_inference(model, data):
    """Run inference using multiple processes."""
    print(f"Running multi-process inference with {N_PROCESSES} processes...")
    
    # Warm up the CPU and initialize resources
    _ = model.predict(data[:100])
    
    # Split data into batches
    data_batches = np.array_split(data, N_PROCESSES)
    
    start_time = time.time()
    # Use a context manager to ensure proper cleanup
    with mp.get_context('spawn').Pool(processes=N_PROCESSES) as pool:
        process_func = partial(process_batch, model)
        results = pool.map(process_func, data_batches)
    
    predictions = np.concatenate(results)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Multi-process inference completed in {elapsed_time:.4f} seconds")
    
    return elapsed_time, predictions

def main():
    """Main function to run the quick test."""
    print("=" * 50)
    print("QUICK TEST - INFERENCE PERFORMANCE BENCHMARK")
    print("=" * 50)
    print(f"Comparing single process vs. {N_PROCESSES} processes")
    print("-" * 50)
    
    # Create model
    model = create_model()
    
    # Generate inference data
    data = generate_inference_data()
    
    # Run single-process inference
    single_time, single_predictions = single_process_inference(model, data)
    
    # Run multi-process inference
    multi_time, multi_predictions = multi_process_inference(model, data)
    
    # Verify results
    is_equal = np.allclose(single_predictions, multi_predictions)
    print(f"Results verification: {'PASSED' if is_equal else 'FAILED'}")
    
    # Calculate speedup
    speedup = single_time / multi_time
    print(f"Speedup: {speedup:.2f}x")
    print(f"Efficiency: {speedup / N_PROCESSES:.2f}")
    
    print("-" * 50)
    print("Quick test completed!")

if __name__ == "__main__":
    main()
