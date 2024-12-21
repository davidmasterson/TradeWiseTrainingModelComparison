# rf_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pickle
import logging
logging.basicConfig(
    filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
def preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name):
    try:
        logging.info("Fetching dataset...")
        dataset_id = int(dataset_id)
        df = pd.read_csv('completelyFreshBaseDS.csv')
        
        

        # Convert all columns to numeric and fill NaN values
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        df.fillna(0, inplace=True)
        new_dataset = df.copy()
        # Drop unnecessary columns
        drop_cols = [
            'sector','symbol', 'dp','ds'
        ]
        df = df.drop(columns=[col for col in drop_cols if col in df.columns])

       
        # Split features (X) and target (y)
        X = df.drop(columns=['hit_tp1'])
        columns = X.columns.to_list()
        y = df['hit_tp1']

        # Scale features
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        # Train-test split for modeling
        train_size = int(0.8 * len(X_scaled))
        X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Standardized output structure
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler,
            'structure': 'train_test_split',
            'columns':columns
        }
        
        logging.info("Preprocessing complete. Packaged data for modeling.")

            
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

        return preprocessed_data

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
