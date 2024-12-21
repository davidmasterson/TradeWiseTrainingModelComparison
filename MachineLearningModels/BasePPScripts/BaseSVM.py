# svm_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import pickle
from io import BytesIO
from database import dataset_DAOIMPL, preprocessing_scripts_DAOIMPL
import logging
import concurrent
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

# Function to calculate result based on date difference

def parallel_apply_single_arg(symbols, func, max_workers=20):
    """
    Helper function to apply a calculation in parallel.
    
    Args:
        symbols (iterable): List or Series of symbols to process.
        func (callable): Function to apply to each symbol.
        max_workers (int): Maximum number of parallel workers.

    Returns:
        List: Results of applying the function to each symbol.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(func, symbols))

# Updated parallel_apply implementation (as provided earlier)
def parallel_apply_multiple_args(args_list, func, max_workers=20):
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(lambda args: func(*args), zip(*args_list)))


# Sample logging statements
logging.debug("Starting preprocessing script.")
logging.info(f"Dataset ID received: {sys.argv[2]}")

# Load and preprocess dataset
def preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name):
    
    user_id = int(user_id)
    dataset_id = int(dataset_id)
    script_id = int(script_id)
    if not model_name:
        logging.error("Model name is required but not provided.")
        return None
    
    try:
        df = pd.read_csv('completelyFreshBaseDS.csv')
            
        df = df.dropna() 
        # Date-based feature engineering
        df['dp'] = pd.to_datetime(df['dp'])
        df['purchase_day'] = df['dp'].dt.day
        df['purchase_month'] = df['dp'].dt.month
        df['purchase_year'] = df['dp'].dt.year
        df['ds'] = pd.to_datetime(df['ds'])
        df['sell_day'] = df['ds'].dt.day
        df['sell_month'] = df['ds'].dt.month
        df['sell_year'] = df['ds'].dt.year
        logging.info("Performed date-based feature engineering.")
        
        # Add target column
        df['hit_tp1'] = df.apply(calculate_target, axis=1)
        # Drop unnecessary columns
        drop_columns = [
            'id', 'ps', 'sstring', 'proi', 'tsp', 'spps', 'stop_loss_price', 'tp2'
        ]
        df = df.drop(columns=drop_columns, errors='ignore')
        logging.info(f"Dropped unnecessary columns: {drop_columns}.")
        # Combine Datasets Now
        df_final = df.copy()
        df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
        # Encoding categorical features
        label_encoder = LabelEncoder()
        df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
        df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
        new_dataset = df_final.copy()
        df_final.to_csv('completelyFreshBaseDS.csv')
        
        df_final.drop(['sector', 'symbol', 'dp', 'ds', 'actual'], axis=1, inplace=True)
        logging.info("Encoded categorical features.")
        # Splitting features and target
        X = df_final.drop(['hit_tp1'], axis=1)  # All features for scaling
        y = df_final['hit_tp1']  # Target variable

        # Scale the features
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X)

        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Serialize the preprocessed data
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }
        
        output_data = {
            "preprocessing_object": preprocessed_data,
            "dataset": new_dataset
        }   
        
        try:
            output_data_bin = pickle.dumps(output_data)
            
            with open(output_data_path, 'wb') as bin_writer:
                bin_writer.write(output_data_bin)
        except IOError as e:
            print(f"Error writing to file: {e}")
            
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None


# If run directly, preprocess data and save to binary file
if __name__ == "__main__":
    output_path =  sys.argv[0]  
    dataset_id =  sys.argv[1]  
    user_id = sys.argv[2]  
    output_data_path = sys.argv[3]
    script_id = sys.argv[4]
    model_name = sys.argv[5]
    preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name)
