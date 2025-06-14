# StreamingDataset Conversion

This module demonstrates how to convert a dataset into the StreamingDataset format for efficient data loading.

## Overview

The StreamingDataset format is designed for efficient, scalable, and distributed training of large models. It provides:

- Fast, cheap, and scalable training on large datasets from cloud storage
- Support for multi-node, distributed training
- Elastic determinism for reproducibility
- Instant mid-epoch resumption
- High throughput with low latency
- Effective shuffling for model convergence

## Components

This module includes:

1. **generate_dataset.py**: Creates a synthetic dataset with various data types
2. **convert_dataset.py**: Converts the dataset to StreamingDataset format (MDS)
3. **benchmark.py**: Benchmarks the performance of StreamingDataset vs. standard loading
4. **minio_integration.py**: Demonstrates integration with MinIO object storage
5. **ml_example.py**: Shows how to use StreamingDataset in a machine learning workflow
6. **run.py**: Provides a simple way to run the entire workflow

### Custom Implementation

Due to dependency issues with the MosaicML streaming library, we've also provided a custom implementation:

1. **custom_streaming.py**: A simplified implementation of StreamingDataset without complex dependencies
2. **custom_example.py**: Example usage of the custom StreamingDataset implementation
3. **custom_requirements.txt**: Minimal dependencies for the custom implementation
4. **setup_venv.bat**: Script to set up a virtual environment with the required dependencies

## Usage

### Option 1: Using MosaicML's StreamingDataset (Original Implementation)

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Generate a Sample Dataset

```bash
python generate_dataset.py
```

This will create a synthetic dataset in the `data/raw` directory.

#### 3. Convert to StreamingDataset Format

```bash
python convert_dataset.py
```

This will convert the raw dataset to MDS format in the `data/streaming` directory.

#### 4. Run Benchmark

```bash
python benchmark.py
```

This will compare the performance of standard dataset loading vs. StreamingDataset.

### Option 2: Using Custom StreamingDataset Implementation

#### 1. Set Up Virtual Environment

```bash
# Create and set up the virtual environment
python -m venv venv
setup_venv.bat
```

#### 2. Run the Custom Example

```bash
# Activate the virtual environment
venv\Scripts\activate.bat

# Run the example
python module-3\streaming_dataset\custom_example.py --input-path data\raw\dataset.csv --output-dir data\custom_streaming
```

This will convert the dataset to the custom streaming format and demonstrate its usage.

## Integration with MinIO

The StreamingDataset format can be used with MinIO for object storage. The S3 compatibility allows for seamless integration with MinIO.

## Troubleshooting

If you encounter dependency issues with the original implementation, try the custom implementation which has minimal dependencies and provides similar functionality.

## References

- [MosaicML Streaming Documentation](https://streaming.docs.mosaicml.com/)
- [GitHub Repository](https://github.com/mosaicml/streaming)
- [PyTorch DataLoader Documentation](https://pytorch.org/docs/stable/data.html)
