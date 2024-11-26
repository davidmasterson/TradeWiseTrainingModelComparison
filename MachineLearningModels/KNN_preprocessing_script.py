# knn_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
from database import dataset_DAOIMPL, preprocessing_scripts_DAOIMPL
import logging
logging.basicConfig(
    filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
def preprocess_data(output_path, dataset_id, user_id, model_name, script_id):
    try:
        logging.info("Fetching dataset...")
        dataset_id = int(dataset_id)
        dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
        
        if not dataset_data:
            logging.error("Failed to retrieve dataset.")
            return None

        df = pickle.loads(dataset_data)
        logging.info("Data loaded into DataFrame.")

        # Drop unnecessary columns
        try:
            df = df.drop(['sector','symbol'], axis=1)
        except:
            pass
        

        # Calculate technical indicators
        df['RSI'] = calculate_rsi(df['ppps'], 14)
        df['SMA'] = calculate_sma(df['ppps'], 20)
        df['EMA'] = calculate_ema(df['ppps'], 20)
        df['Momentum'] = calculate_momentum(df['ppps'], 10)

        df.fillna(0, inplace=True)

        # Prepare features and target
        X = df.drop(columns=['hit_tp1'])  # Exclude target column 'tp1'
        y_continuous = df['hit_tp1']  # Target

        # Binning the target variable
        num_bins = 10
        y_binned, bin_edges = pd.cut(y_continuous, bins=num_bins, labels=False, retbins=True)
        
        # Scale the features
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_binned, test_size=0.2, random_state=42)

        # Serialize preprocessed data
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }
        preprocessed_bin = pickle.dumps(preprocessed_data)
        preprocessing_scripts_DAOIMPL.update_preprocessed_data_for_user(script_id,preprocessed_bin)
        logging.info(f'Preprocessed data updated for user')

        return preprocessed_data
    except Exception as e:
        raise

# If run directly, preprocess data and save to binary file
if __name__ == "__main__":
    output_path =  sys.argv[0]  
    dataset_id =  sys.argv[1]  
    user_id = sys.argv[2]  
    model_name = sys.argv[3]
    script_id = sys.argv[4]
    preprocess_data(output_path, dataset_id, user_id, model_name, script_id)
    
