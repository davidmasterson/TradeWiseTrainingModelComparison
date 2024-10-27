# xgb_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle
import logging
from io import BytesIO
from database import dataset_DAOIMPL
import logging
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")
logging.info(f"Dataset ID received: {sys.argv[2]}")

# Function to calculate technical indicators
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

def calculate_momentum(data, period=14):
    return data.diff(period)

# Load and preprocess dataset
def preprocess_data(output_path, dataset_id):
    try:
        dataset_id = int(dataset_id)
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
        df = df.apply(pd.to_numeric, errors='coerce')
        df.fillna(0, inplace=True)  # Or use another method to handle missing data if necessary
        # Remove unnecessary features
        df = df.drop(columns=['date_sold', 'sold_pps', 'total_sell_price', 'sell_string', 
                            'expected_return', 'percentage_roi', 'actual_return', 
                            'stop_loss_price', 'tp2', 'sop', 'purchase_string'])

        # Drop non-numeric columns
        df = df.drop(columns=['symbol', 'date_purchased'])

        # Calculate technical indicators
        df['RSI'] = calculate_rsi(df['purchased_pps'], 14)
        df['SMA'] = calculate_sma(df['purchased_pps'], 20)
        df['EMA'] = calculate_ema(df['purchased_pps'], 20)
        df['Momentum'] = calculate_momentum(df['purchased_pps'], 10)

        # Fill NaN values
        df.fillna(0, inplace=True)

        # Prepare features and target
        X = df.drop(columns=['tp1'])  # Features (excluding target column)
        y = df['tp1']  # Target (continuous values of `tp1`)

        # Scale features
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Serialize the preprocessed data
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler,  # Add scaler here
            'structure': 'train_test_split' # Explicitly set the structure
        }
        with open(output_path, 'wb') as f:
                pickle.dump(preprocessed_data, f)
        logging.debug(f"Serialized preprocessed data with structure: {preprocessed_data.get('structure')}")
                    
        logging.debug("Serialized preprocessed data with structure: train_test_split.")
        print(f"Preprocessing complete. Data saved to {output_path}")
                
        return preprocessed_data
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None


# If this script is run directly, preprocess data and print confirmation
if __name__ == "__main__":
    output_path = sys.argv[1]
    dataset_id = sys.argv[2]
    preprocess_data(output_path, dataset_id)
