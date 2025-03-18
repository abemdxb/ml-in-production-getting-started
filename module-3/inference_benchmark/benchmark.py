#!/usr/bin/env python3
"""
Benchmark script to compare inference performance between single and multiple processes.
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
import multiprocessing as mp
from functools import partial
import psutil

# Parameters
N_SAMPLES = 500000  # Increased number of samples for inference
N_FEATURES = 50     # Increased number of features
N_PROCESSES = min(mp.cpu_count(), 4)  # Limit to 4 processes to reduce overhead
BATCH_SIZE = N_SAMPLES // N_PROCESSES  # Batch size for multiprocessing

def create_model():
    """Create and train a simple Random Forest model."""
    print("Creating and training model...")
    # Generate synthetic training data
    X_train, y_train = make_regression(
        n_samples=10000, 
        n_features=N_FEATURES, 
        noise=0.1, 
        random_state=42
    )
    
    # Train a Random Forest model with more trees to increase CPU workload
    model = RandomForestRegressor(n_estimators=50, max_depth=20, random_state=42)
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
    
    # Split data into larger batches to reduce overhead
    data_batches = np.array_split(data, N_PROCESSES)
    
    # Create a pool of processes
    start_time = time.time()
    
    # Use a context manager to ensure proper cleanup
    # Use 'fork' on Linux/Mac or 'spawn' on Windows
    context = 'spawn' if os.name == 'nt' else 'fork'
    with mp.get_context(context).Pool(processes=N_PROCESSES) as pool:
        # Map the process_batch function to each batch
        process_func = partial(process_batch, model)
        results = pool.map(process_func, data_batches)
    
    # Combine results
    predictions = np.concatenate(results)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Multi-process inference completed in {elapsed_time:.4f} seconds")
    
    return elapsed_time, predictions

def verify_results(single_predictions, multi_predictions):
    """Verify that both methods produce the same results."""
    is_equal = np.allclose(single_predictions, multi_predictions)
    print(f"Results verification: {'PASSED' if is_equal else 'FAILED'}")
    return is_equal

def plot_results(single_time, multi_time):
    """Create a bar chart comparing the performance."""
    labels = ['Single Process', f'Multi Process ({N_PROCESSES} cores)']
    times = [single_time, multi_time]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, times, color=['blue', 'green'])
    
    # Add time labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.4f}s', ha='center', va='bottom')
    
    plt.ylabel('Time (seconds)')
    plt.title('Inference Performance Comparison')
    plot_path = os.path.join(os.path.dirname(__file__), 'inference_performance.png')
    plt.savefig(plot_path)
    print(f"Performance chart saved as '{plot_path}'")

def save_results(single_time, multi_time, verification_passed):
    """Save benchmark results to a file."""
    speedup = single_time / multi_time
    efficiency = speedup / N_PROCESSES
    
    system_info = {
        "CPU": f"{psutil.cpu_count(logical=False)} physical cores, {psutil.cpu_count(logical=True)} logical cores",
        "Memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "Python Version": platform.python_version(),
    }
    
    results = {
        "Parameters": {
            "Samples": N_SAMPLES,
            "Features": N_FEATURES,
            "Processes": N_PROCESSES,
            "Batch Size": BATCH_SIZE
        },
        "Results": {
            "Single Process Time (s)": single_time,
            "Multi Process Time (s)": multi_time,
            "Speedup": speedup,
            "Efficiency": efficiency,
            "Verification": "PASSED" if verification_passed else "FAILED"
        },
        "System Info": system_info
    }
    
    # Convert to DataFrame for nice formatting
    params_df = pd.DataFrame(list(results["Parameters"].items()), columns=["Parameter", "Value"])
    results_df = pd.DataFrame(list(results["Results"].items()), columns=["Metric", "Value"])
    system_df = pd.DataFrame(list(results["System Info"].items()), columns=["Component", "Specification"])
    
    # Save to text file
    results_path = os.path.join(os.path.dirname(__file__), "results.txt")
    with open(results_path, "w") as f:
        f.write("# Inference Performance Benchmark Results\n\n")
        
        f.write("## Parameters\n")
        f.write(params_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("## Results\n")
        f.write(results_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("## System Information\n")
        f.write(system_df.to_string(index=False))
    
    print(f"Results saved to '{results_path}'")
    
    return results

def main():
    """Main function to run the benchmark."""
    print("=" * 50)
    print("INFERENCE PERFORMANCE BENCHMARK")
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
    verification_passed = verify_results(single_predictions, multi_predictions)
    
    # Calculate speedup
    speedup = single_time / multi_time
    print(f"Speedup: {speedup:.2f}x")
    print(f"Efficiency: {speedup / N_PROCESSES:.2f}")
    
    # Plot results
    try:
        plot_results(single_time, multi_time)
    except Exception as e:
        print(f"Could not create plot: {e}")
    
    # Save results
    save_results(single_time, multi_time, verification_passed)
    
    print("-" * 50)
    print("Benchmark completed!")

if __name__ == "__main__":
    import platform  # Import here to avoid circular import in save_results
    main()
