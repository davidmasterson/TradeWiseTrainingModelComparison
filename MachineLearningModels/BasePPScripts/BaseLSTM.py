# lstm_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pickle
from io import BytesIO
from database import dataset_DAOIMPL, models_DAOIMPL, transaction_model_status_DAOIMPL, transactions_DAOIMPL
import logging
from datetime import datetime
from MachineLearningModels import manual_alg_requisition_script
import concurrent

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

# Function to calculate target based on hitting tp1 within 12 days
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

'''------------------------------------------------------------------------------------------------------------------------------'''    


# Main preprocessing function
def preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name):
    user_id = int(user_id)
    dataset_id = int(dataset_id)
    script_id = int(script_id)
    if not model_name:
        logging.error("Model name is required but not provided.")
        return None
    
    try:
        
        df = pd.read_csv('completelyFreshBaseDS.csv')
          
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
        df_final = df.copy()
        df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
        
        
        # Encoding categorical features
        label_encoder = LabelEncoder()
        df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
        df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
        
        new_dataset = df_final.copy()
        
        df_final.drop(['sector', 'symbol', 'actual'], axis=1, inplace=True)
        logging.info("Encoded categorical features.")
        # Convert columns to numeric as needed
        df_final = df_final.apply(pd.to_numeric, errors='coerce').fillna(0)
        target_column = 14  # Column index for the target variable
        time_steps = 60  # Define the number of time steps
        df_final['hit_tp1'] = df_final.apply(calculate_target)
        # Prepare the input data (X) and target variable (y)
        
        X, y, _ = prepare_data(df, target_column, time_steps)

        # Split data into training and testing sets
        train_size = int(0.8 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Initialize and use MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[2])).reshape(X_train.shape)
        X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[2])).reshape(X_test.shape)

        # Package preprocessed data
        preprocessed_data = {
            'X_train': X_train_scaled,    # Scaled training data
            'X_test': X_test_scaled,      # Scaled testing data
            'y_train': y_train,           # Training labels
            'y_test': y_test,             # Testing labels
            'scaler': scaler,             # Scaler used for preprocessing
            'structure': 'train_test_split' # Metadata for structure description
        }
        logging.info("Preprocessing complete. Packaged data for modeling.")

        # Output data preparation
        output_data = {
            "preprocessing_object": preprocessed_data,
            "dataset": df  # or new_dataset if you have further processed the DataFrame
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

# # # Execution check
if __name__ == "__main__":
    output_path =  sys.argv[0]  
    dataset_id =  sys.argv[1]  
    user_id = sys.argv[2]  
    output_data_path = sys.argv[3]
    script_id = sys.argv[4]
    model_name = sys.argv[5]
    preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name)

