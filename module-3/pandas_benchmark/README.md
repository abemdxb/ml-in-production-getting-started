# Pandas Format Benchmarking

This project benchmarks various Pandas data formats in terms of data saving and loading performance. It measures and compares the time it takes to save and load data in different formats.

## Overview

The benchmark script generates a synthetic dataset with 1000 rows and 100 columns, containing a mix of data types:
- Numeric data (integers and floats)
- String data
- Datetime data
- Boolean data

It then saves and loads this dataset in various formats, measuring the time taken for each operation.

## Formats Benchmarked

The following formats are benchmarked:

1. **CSV** (.csv) - Comma-separated values, a text-based format
2. **Parquet** (.parquet) - A columnar storage format optimized for analytics
3. **HDF5** (.h5) - Hierarchical Data Format, designed for storing large amounts of numerical data
4. **Feather** (.feather) - A fast on-disk format for data frames
5. **Pickle** (.pkl) - Python's native serialization format
6. **JSON** (.json) - JavaScript Object Notation, a text-based data interchange format
7. **Excel** (.xlsx) - Microsoft Excel spreadsheet format

## Metrics Measured

The benchmark measures two key metrics:
- **Save Time**: Time taken to write the dataset to disk in each format
- **Load Time**: Time taken to read the dataset from disk in each format

Each operation is performed multiple times (5 iterations by default) to get more reliable average times.

## Running the Benchmark

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

### Execution

Run the benchmark script:

```bash
python benchmark.py
```

## Interpreting Results

The results are displayed in a table format, sorted by total time (save time + load time) from fastest to slowest. This makes it easy to identify which formats are most efficient for data I/O operations.

Example output:

```
Benchmark Results:
+----------+---------------+---------------+----------------+
| Format   | Save Time (s) | Load Time (s) | Total Time (s) |
+----------+---------------+---------------+----------------+
| Parquet  | 0.0123        | 0.0045        | 0.0168         |
| Feather  | 0.0134        | 0.0056        | 0.0190         |
| Pickle   | 0.0156        | 0.0078        | 0.0234         |
| HDF5     | 0.0189        | 0.0067        | 0.0256         |
| CSV      | 0.0345        | 0.0234        | 0.0579         |
| JSON     | 0.0567        | 0.0345        | 0.0912         |
| Excel    | 0.1234        | 0.0789        | 0.2023         |
+----------+---------------+---------------+----------------+
```

## Notes

- The benchmark results may vary depending on the hardware, operating system, and the specific versions of the libraries used.
- The dataset size and composition can significantly impact the relative performance of different formats.
- Some formats may be more efficient for specific data types or use cases.
