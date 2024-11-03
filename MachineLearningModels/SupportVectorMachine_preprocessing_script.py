# svm_preprocessing.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle
from io import BytesIO
from database import dataset_DAOIMPL, preprocessing_scripts_DAOIMPL
import logging
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")
logging.info(f"Dataset ID received: {sys.argv[2]}")
# Load and preprocess dataset
def preprocess_data(output_path, dataset_id, user_id, model_name, script_id):
    try:
        dataset_id = int(dataset_id)
        logging.info("Fetching dataset...")
        dataset_id = int(dataset_id)
        dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
        
        if not dataset_data:
            logging.error("Failed to retrieve dataset.")
            return None

        df = pickle.loads(dataset_data)
        logging.info("Data loaded into DataFrame.")
        
        # Add additional debug logging around key processing steps
        logging.debug(f"Initial DataFrame columns: {df.columns}")
        logging.debug(f"DataFrame shape: {df.shape}")
        df = df.apply(pd.to_numeric, errors='coerce')
        df.fillna(0, inplace=True)  # Or use another method to handle missing data if necessary

       

        # Drop non-numeric columns
        df = df.drop(columns=['symbol', 'sector'], axis=1)

        # Prepare features and target
        X = df.drop(columns=['hit_tp1_within_12'])  # Features
        y = df['hit_tp1_within_12']  # Target

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
            'y_test': y_test,
            'scaler': scaler,
            'structure': 'train_test_split'  # Explicitly set the structure
        }
        preprocessed_bin = pickle.dumps(preprocessed_data)
        preprocessing_scripts_DAOIMPL.update_preprocessed_data_for_user(script_id,preprocessed_bin)
        logging.info(f'Preprocessed data updated for user')
                
        return preprocessed_data
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None


# If this script is run directly, preprocess data and print confirmation
if __name__ == "__main__":
    output_path =  sys.argv[0]  
    dataset_id =  sys.argv[1]  
    user_id = sys.argv[2]  
    model_name = sys.argv[3]
    script_id = sys.argv[4]
    preprocess_data(output_path, dataset_id, user_id, model_name, script_id)
