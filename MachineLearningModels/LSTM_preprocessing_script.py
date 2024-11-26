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

logging.basicConfig(
    filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to prepare data for LSTM
def prepare_data(df, target_column, time_steps):
    # Ensure only numeric columns are used
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

# Condition to determine target variable
def calculate_target(row):
    """
    Determines if tp1 was hit before sop based on 'actual'.
    - Returns 1 if 'actual' > 0 (tp1 hit before sop).
    - Returns 0 if 'actual' <= 0 (sop hit before tp1 or no profit).
    """
    try:
        actual = row['actual']
        
        if pd.isnull(actual):
            return 0  # Default to 0 if 'actual' is missing
        
        return 1 if actual > 0 else 0
    except Exception as e:
        logging.error(f"Error calculating target for row {row}: {e}")
        return 0

# Main preprocessing function
def preprocess_data(output_path, dataset_id):
    try:
        logging.info("Fetching dataset...")
        dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
        
        if not dataset_data:
            logging.error("Failed to retrieve dataset.")
            return None

        df = pickle.loads(dataset_data)
        logging.info("Data loaded into DataFrame.")
        
        # Basic DataFrame checks
        logging.debug(f"Initial DataFrame columns: {df.columns}")
        logging.debug(f"DataFrame shape: {df.shape}")

        # Ensure required columns are present
        if 'purchased_pps' not in df.columns:
            raise KeyError("'purchased_pps' column is missing from the dataset.")

        # Convert columns to numeric as needed
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        target_column = 3  # Column index for the target variable
        time_steps = 60  # Define the number of time steps
        df['hit_tp1'] = df.apply()
        # Prepare the input data (X) and target variable (y)
        X, y, scaler = prepare_data(df, target_column, time_steps)
        # Split data into training and testing sets
        train_size = int(0.8 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Prepare standardized output structure
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler,
            'structure': 'train_test_split'
        }
        
        # Save preprocessed data to output path
        with open(output_path, 'wb') as f:
            pickle.dump(preprocessed_data, f)
            
        logging.info(f"Preprocessing complete. Data saved to {output_path}")
        
        return preprocessed_data
    
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None

# If script is run directly
if __name__ == "__main__":
    output_path = sys.argv[1]
    dataset_id = sys.argv[2]
    preprocess_data(output_path, dataset_id)
