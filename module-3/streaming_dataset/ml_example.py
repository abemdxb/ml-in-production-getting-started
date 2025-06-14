#!/usr/bin/env python3
"""
Machine Learning Example with StreamingDataset

This script demonstrates how to use StreamingDataset in a machine learning workflow.
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import time
from tqdm import tqdm

# Import streaming library
try:
    from streaming import StreamingDataset
except ImportError:
    print("Error: MosaicML streaming library not found.")
    print("Please install it with: pip install mosaicml-streaming")
    sys.exit(1)

class SimpleModel(nn.Module):
    """A simple neural network model for regression."""
    
    def __init__(self, input_size, hidden_size=64):
        """
        Initialize the model.
        
        Args:
            input_size (int): Number of input features
            hidden_size (int): Size of the hidden layer
        """
        super(SimpleModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )
    
    def forward(self, x):
        """Forward pass."""
        return self.network(x)

class StreamingDataProcessor:
    """Process data from StreamingDataset for model training."""
    
    def __init__(self, numeric_cols=None, target_col='int_col_0'):
        """
        Initialize the processor.
        
        Args:
            numeric_cols (list): List of numeric columns to use as features
            target_col (str): Target column for prediction
        """
        self.numeric_cols = numeric_cols
        self.target_col = target_col
    
    def process_batch(self, batch):
        """
        Process a batch of data.
        
        Args:
            batch (dict): Batch of data from StreamingDataset
            
        Returns:
            tuple: (features, targets)
        """
        # If numeric_cols is not specified, use all int and float columns
        if self.numeric_cols is None:
            self.numeric_cols = [col for col in batch.keys() 
                                if col.startswith('int_col_') or col.startswith('float_col_')]
            # Remove target column from features
            if self.target_col in self.numeric_cols:
                self.numeric_cols.remove(self.target_col)
        
        # Extract features
        features = []
        for col in self.numeric_cols:
            if col in batch:
                features.append(batch[col])
        
        # Stack features into a tensor
        features = torch.stack(features, dim=1).float()
        
        # Extract target
        targets = batch[self.target_col].float().unsqueeze(1)
        
        return features, targets

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='ML example with StreamingDataset')
    parser.add_argument('--data-dir', type=str, default='data/streaming',
                        help='Directory containing the StreamingDataset (default: data/streaming)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training (default: 32)')
    parser.add_argument('--epochs', type=int, default=5,
                        help='Number of epochs for training (default: 5)')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                        help='Learning rate for optimizer (default: 0.001)')
    parser.add_argument('--hidden-size', type=int, default=64,
                        help='Size of hidden layers in the model (default: 64)')
    return parser.parse_args()

def train_model(dataset, model, processor, epochs=5, learning_rate=0.001):
    """
    Train a model using StreamingDataset.
    
    Args:
        dataset (StreamingDataset): Dataset for training
        model (nn.Module): Model to train
        processor (StreamingDataProcessor): Data processor
        epochs (int): Number of epochs for training
        learning_rate (float): Learning rate for optimizer
        
    Returns:
        list: Training losses
    """
    # Create dataloader
    dataloader = DataLoader(
        dataset,
        batch_size=None,  # Batch size is handled by StreamingDataset
        num_workers=2
    )
    
    # Set up optimizer and loss function
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    
    # Training loop
    model.train()
    losses = []
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        batch_count = 0
        
        print(f"Epoch {epoch+1}/{epochs}")
        for batch in tqdm(dataloader):
            # Process batch
            features, targets = processor.process_batch(batch)
            
            # Zero gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(features)
            
            # Calculate loss
            loss = criterion(outputs, targets)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            # Update statistics
            epoch_loss += loss.item()
            batch_count += 1
        
        # Calculate average loss for the epoch
        avg_epoch_loss = epoch_loss / batch_count
        losses.append(avg_epoch_loss)
        print(f"  Average loss: {avg_epoch_loss:.6f}")
    
    return losses

def main():
    """Main function."""
    args = parse_args()
    
    print("=" * 50)
    print("MACHINE LEARNING EXAMPLE WITH STREAMINGDATASET")
    print("=" * 50)
    
    # Create StreamingDataset
    print(f"Loading StreamingDataset from {args.data_dir}...")
    dataset = StreamingDataset(
        local=args.data_dir,
        remote=None,
        shuffle=True,
        batch_size=args.batch_size
    )
    print(f"Dataset loaded with {len(dataset)} samples")
    
    # Create data processor
    processor = StreamingDataProcessor()
    
    # Create model
    # We'll determine the input size from the first batch
    first_batch = next(iter(dataset))
    features, _ = processor.process_batch(first_batch)
    input_size = features.shape[1]
    
    model = SimpleModel(input_size=input_size, hidden_size=args.hidden_size)
    print(f"Created model with input size {input_size}")
    
    # Train model
    print("\nTraining model...")
    start_time = time.time()
    losses = train_model(
        dataset,
        model,
        processor,
        epochs=args.epochs,
        learning_rate=args.learning_rate
    )
    end_time = time.time()
    
    print(f"\nTraining completed in {end_time - start_time:.2f} seconds")
    print(f"Final loss: {losses[-1]:.6f}")
    
    # Save model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, 'model.pt')
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
