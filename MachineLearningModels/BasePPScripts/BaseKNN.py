# knn_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
from database import dataset_DAOIMPL, preprocessing_scripts_DAOIMPL, transaction_model_status_DAOIMPL, transactions_DAOIMPL, models_DAOIMPL
import logging
import concurrent
from datetime import date
from MachineLearningModels import manual_alg_requisition_script

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




# Load and preprocess dataset
def preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name):
    try:
        user_id = int(user_id)
        dataset_id = int(dataset_id)
        script_id = int(script_id)
        if not model_name:
            logging.error("Model name is required but not provided.")
            return None
        
        df = pd.read_csv('dataset.csv')
        
        
        drop_columns = [
            'id', 'ps', 'sstring', 'proi', 'tsp', 'spps', 'stop_loss_price', 'tp2'
        ] 
        df = df[(df['dp'] != '0000-00-00') & (df['ds'] != '0000-00-00')] 
        
        from sector_finder import get_stock_sector
        df['sector'] = df['symbol'].apply(get_stock_sector)
        df.drop(columns=drop_columns, axis=1, inplace=True)  
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
        
        
        # Calculate technical indicators
        df['RSI'] = calculate_rsi(df['ppps'], 14)
        df['SMA'] = calculate_sma(df['ppps'], 20)
        df['EMA'] = calculate_ema(df['ppps'], 20)
        df['Momentum'] = calculate_momentum(df['ppps'], 10)
        
        
        df_final = df.copy()
        
        df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
        
        
        # Encoding categorical features
        label_encoder = LabelEncoder()
        df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
        df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
        df_final = df_final.dropna()
        new_dataset = df_final.copy() 
        df_final.to_csv('completelyFreshBaseDS.csv')   
        
        
        try:
            df_final = df_final.drop(['sector','symbol', 'dp', 'ds', 'actual'], axis=1)
        except:
            pass
        
        # Prepare features and target
        X = df_final.drop(columns=['hit_tp1'])  # Exclude target column 'tp1'
        y_continuous = df_final['hit_tp1']  # Target
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
        raise

# If run directly, preprocess data and save to binary file
if __name__ == "__main__":
    output_path =  sys.argv[0]  
    dataset_id =  sys.argv[1]  
    user_id = sys.argv[2]  
    output_data_path = sys.argv[3]
    script_id = sys.argv[4]
    model_name = sys.argv[5]
    preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name)
    
