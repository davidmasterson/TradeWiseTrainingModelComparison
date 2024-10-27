# knn_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle
from database import dataset_DAOIMPL
from io import BytesIO

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
    
    dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)

    # Load dataset into a DataFrame
    df = pd.read_csv(BytesIO(dataset_data), encoding='ISO-8859-1')  # Adjust encoding if needed

    # Convert all columns to numeric, setting errors='coerce' to handle non-numeric entries
    df = df.apply(pd.to_numeric, errors='coerce')

    # Fill NaN values (or you can choose to drop them)
    df = df.fillna(0)  # or df.dropna()

    # Drop unnecessary columns
    df = df.drop(columns=['date_sold', 'sold_pps', 'total_sell_price', 'sell_string', 
                          'expected_return', 'percentage_roi', 'actual_return', 
                          'stop_loss_price', 'tp2', 'sop', 'purchase_string', 
                          'symbol', 'date_purchased'])

    # Calculate technical indicators
    df['RSI'] = calculate_rsi(df['purchased_pps'], 14)
    df['SMA'] = calculate_sma(df['purchased_pps'], 20)
    df['EMA'] = calculate_ema(df['purchased_pps'], 20)
    df['Momentum'] = calculate_momentum(df['purchased_pps'], 10)

    df.fillna(0, inplace=True)

    # Prepare features and target
    X = df.drop(columns=['tp1'])  # Exclude target column 'tp1'
    y_continuous = df['tp1']  # Target

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
    with open(output_path, 'wb') as f:
        pickle.dump(preprocessed_data, f)

    print(f"Preprocessing complete. Data saved to {output_path}")
    
    return preprocessed_data

# If run directly, preprocess data and save to binary file
if __name__ == "__main__":
    dataset_path = sys.argv[1]
    output_path = sys.argv[2]
    preprocess_data(dataset_path, output_path)
    
