# rf_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from database import dataset_DAOIMPL
from io import BytesIO
import logging 
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")
logging.info(f"Dataset ID received: {sys.argv[2]}")
# Technical Indicator Calculations
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    return 100 - (100 / (1 + RS))

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

def calculate_momentum(data, period=14):
    return data.diff(period)

# Main Preprocessing Function
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
        
        # Ensure all columns are numeric
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Calculate technical indicators on 'purchased_pps'
        df['RSI'] = calculate_rsi(df['purchased_pps'])
        df['SMA'] = calculate_sma(df['purchased_pps'], 20)
        df['EMA'] = calculate_ema(df['purchased_pps'], 20)
        df['Momentum'] = calculate_momentum(df['purchased_pps'], 10)
        df.fillna(0, inplace=True)
        
        # Drop unnecessary columns (if present)
        drop_cols = ['date_sold', 'sold_pps', 'total_sell_price', 'sell_string', 
                     'expected_return', 'percentage_roi', 'actual_return',
                     'stop_loss_price', 'tp2', 'sop', 'purchase_string', 
                     'symbol', 'date_purchased']
        df = df.drop(columns=[col for col in drop_cols if col in df.columns])

        # Validate target columns
        if 'hit_tp1_within_12' not in df.columns:
            logging.warning("The 'hit_tp1_within_12' column is missing. Adding default values (0).")
            df['hit_tp1_within_12'] = 0  # or set based on your target criteria

        # Split features (X) and target (y)
        X = df.drop(columns=['tp1', 'hit_tp1_within_12'])
        y = df['hit_tp1_within_12']
        
        # Scale features
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Prepare the serialized data
        preprocessed_data = {
            'X_scaled': X_scaled,
            'y': y,
            'scaler': scaler,
            'structure': 'scaled'
        }
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'wb') as f:
            pickle.dump(preprocessed_data, f)
        
        logging.info(f"Preprocessing complete. Data saved to {output_path}")
        
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None

# Execution check
if __name__ == "__main__":
    output_path = sys.argv[1]  # Adjust the order of arguments
    dataset_id = sys.argv[2]  # Expect dataset_id instead of dataset_path
    preprocess_data(output_path, dataset_id)
