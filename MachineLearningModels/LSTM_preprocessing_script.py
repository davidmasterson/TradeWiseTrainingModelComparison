# lstm_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from io import BytesIO
from database import dataset_DAOIMPL
import logging
from datetime import datetime
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")
logging.info(f"Dataset ID received: {sys.argv[2]}")
# Function to prepare data
def prepare_data(df, target_column, time_steps):
    # Ensure non-numeric columns are excluded
    numeric_df = df.select_dtypes(include=['float64', 'int64'])

    # Scaling the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(numeric_df)

    X, y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i-time_steps:i])
        y.append(scaled_data[i, target_column])

    X, y = np.array(X), np.array(y)
    return X, y, scaler

# Example condition: hitting target price within 12 days
def calculate_hit_tp1_within_12(row):
    date_purchased = pd.to_datetime(row['date_purchased'])
    date_sold = pd.to_datetime(row['date_sold'])
    actual_return = row['actual_return']
    
    if pd.isnull(date_sold) or (date_sold - date_purchased).days > 12:
        return 0
    return 1 if actual_return >= 0 else 0


# Load dataset and preprocess
def preprocess_data(output_path, dataset_id):
    try:
        logging.info("Fetching dataset...")
        dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
        
        # Confirm dataset retrieval
        if dataset_data:
            logging.debug("Dataset successfully retrieved.")
        else:
            logging.error("Failed to retrieve dataset.")
            return None

        df = pd.read_csv(BytesIO(dataset_data), encoding='ISO-8859-1')
        logging.info("Data loaded into DataFrame.")
        
        # Add additional debug logging around key processing steps
        logging.debug(f"Initial DataFrame columns: {df.columns}")
        logging.debug(f"DataFrame shape: {df.shape}")

        # Check required columns
        if 'purchased_pps' not in df.columns:
            raise KeyError("'purchased_pps' column is missing from the dataset.")

        # Convert all columns to numeric, setting errors='coerce' to handle non-numeric entries
        df = df.apply(pd.to_numeric, errors='coerce')

        # Fill NaN values (or you can choose to drop them)
        df = df.fillna(0)  # or df.dropna()
        target_column = 3  # Specify the column index for the target variable
        time_steps = 60  # Define the number of time steps

        # Prepare the input data (X) and target column (y)
        X, y, scaler = prepare_data(df, target_column, time_steps)
        
        # Split data
        train_size = int(0.8 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Serialize preprocessed data
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler,
            'structure': 'train_test_split'  # Correct structure type
        }
        with open(output_path, 'wb') as f:
            pickle.dump(preprocessed_data, f)
            
        logging.debug("Serialized preprocessed data with structure: train_test_split.")

        print(f"Preprocessing complete. Data saved to {output_path}")
        
        return preprocessed_data
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None

# If run directly, preprocess data and save to binary file
if __name__ == "__main__":
    output_path = sys.argv[1]
    dataset_id = sys.argv[2]
    preprocess_data(output_path, dataset_id)
    
