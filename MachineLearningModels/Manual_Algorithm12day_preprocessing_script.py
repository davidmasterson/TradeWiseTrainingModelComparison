

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pickle
from database import dataset_DAOIMPL, transactions_DAOIMPL
from MachineLearningModels import manual_alg_requisition_script
import sector_finder
import concurrent.futures
import logging
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")

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

# Function to calculate result based on date difference
def calculate_result(row):
    if pd.notna(row['ds']) and (row['ds'] - row['dp']).days <= 12:
        return 'profit'
    return 'loss'

def calculate_first_check(symbol):
    try:
        if manual_alg_requisition_script.first_condition_slope_checks(symbol):
            return 20
        return 0
    except:
        return 0
    
    
def calculate_second_check(symbol): 
    try:  
        if manual_alg_requisition_script.second_check_engulfing_candle_with_reversal(symbol):
            return 10
        return 0
    except:
        return 0
    
def calculate_third_check(symbol):
    try:
        sma_list = manual_alg_requisition_script.get_last_25_day_closes(symbol)
        if manual_alg_requisition_script.third_check_fibonacci_condition(sma_list,symbol):
            return 20
        return 0
    except:
        return 0
    


def parallel_apply(symbols, func, max_workers=4):
    """ Helper function to apply a calculation in parallel. """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, symbols))
    return results 
    
def preprocess_first_dataframe(user_id):
    from sector_finder import get_stock_sector
    try:
        # Fetch and create DataFrame
        
        transactions = transactions_DAOIMPL.get_all_closed_unprocessed_transactions_for_user(user_id)
        print(transactions[0])
        columns = ['id','symbol','dp','ppps','qty','total_buy','pstring','ds','spps','tsp','sstring','expected',
                   'proi','actual','tp1','sop','confidence','result','user_id','sector', 'processed','pol_neu_open',
                   'pol_pos_open','pol_neg_open','sa_neu_open','sa_pos_open','sa_neg_open','pol_neu_close',
                   'pol_pos_close','pol_neg_close','sa_neu_close','sa_pos_close','sa_neg_close']
        df1 = pd.DataFrame(data=transactions, columns=columns)
        
        # Drop rows with missing 'ds' and apply transformations
        df1.dropna(subset=['ds'], inplace=True)
        df1['dp'] = pd.to_datetime(df1['dp'], errors='coerce')
        df1['ds'] = pd.to_datetime(df1['ds'], errors='coerce')
        df1['result'] = df1['result'].apply(lambda x: 0 if x == 'loss' else 1)
        
        
        logging.info("First dataset processed successfully.")
        return [df1,transactions]

    except Exception as e:
        logging.error(f"Error in first dataset preprocessing: {e}")
        return None
        
# Main preprocessing function
# Main preprocessing function
def preprocess_data(output_path, dataset_id, user_id, model_name, script_id):
    from sector_finder import get_stock_sector
    from database import preprocessing_scripts_DAOIMPL, dataset_DAOIMPL
    from flask import flash
    from Models import preprocessing_script, dataset
    from io import BytesIO
    from datetime import datetime, date
    user_id = int(user_id)
    dataset_id = int(dataset_id)
    script_id = int(script_id)
    try:
        df1 = preprocess_first_dataframe(user_id) 
        if df1 is not None:
            df = df1[0] 
            transactions = df1[1] 
            
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            logging.info("Calculated technical indicators.")
            
            # Parallel processing for technical indicators
            logging.info("Starting parallel processing for check1sl.")
            df['check1sl'] = parallel_apply(df['symbol'], calculate_first_check)
            logging.info("Starting parallel processing for check2rev.")
            df['check2rev'] = parallel_apply(df['symbol'], calculate_second_check)
            logging.info("Starting parallel processing for check3fib.")
            df['check3fib'] = parallel_apply(df['symbol'], calculate_third_check)
            logging.info("Calculated slopes, reversals, and fibs.")

            # Calculate final confidence score
            df['check5con'] = df[['check1sl', 'check2rev', 'check3fib']].sum(axis=1)
            logging.info("Calculated confidence scores.")

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
                'id', 'pstring', 'spps', 'tsp', 'sstring', 'expected', 
                'result', 'user_id', 'processed', 'dp', 'confidence', 
                'ds', 'actual', 'proi'
            ]
            df = df.drop(columns=drop_columns, errors='ignore')
            logging.info(f"Dropped unnecessary columns: {drop_columns}.")

            # Combine with finalized dataset
            finalized_dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
            if finalized_dataset_data:
                finalized_dataset_data = pickle.loads(finalized_dataset_data)
                logging.info("Loaded finalized dataset.")
                df_final = pd.concat([df, finalized_dataset_data], axis=0).drop_duplicates()
            else:
                df_final = df
            df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]

            # Encode categorical features
            label_encoder = LabelEncoder()
            df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
            df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
            new_dataset = df_final
            df_final.drop(['sector','symbol'], axis=1, inplace=True)
            logging.info("Encoded categorical features.")

            # Define feature groups
            training_only_features = [
                'ppps', 'qty', 'total_buy', 'tp1', 'sop', 
                'symbol_encoded', 'sector_encoded',
                'check1sl', 'check2rev', 
                'check3fib', 'check5con', 'purchase_day', 'purchase_month', 
                'purchase_year',
                'sell_day','sell_month', 'sell_year'
            ]
            testing_only_features = [
                'ppps', 'qty', 'total_buy', 'tp1', 'sop', 
                'symbol_encoded', 'sector_encoded',
                'check1sl', 'check2rev', 
                'check3fib', 'check5con', 'purchase_day', 'purchase_month', 
                'purchase_year'
            ]
            
            X_full = df_final[training_only_features]  # Full feature set for scaling
            y = df_final['hit_tp1']                   # Target variable
            
            

            # Train-test split for modeling
            X_train_full, X_test_full, y_train, y_test = train_test_split(X_full, y, test_size=0.2, random_state=42)

            # Scale test features separately using the same scaler
            scaler = MinMaxScaler(feature_range=(0, 1))

            # Scale training and testing features
            X_train_scaled = scaler.fit_transform(X_train_full)
            X_test_scaled = scaler.transform(X_test_full)
            
            X_train_df = pd.DataFrame(X_train_scaled, columns=training_only_features)
            X_test_df = pd.DataFrame(X_test_scaled, columns=training_only_features)

            # Filter testing features
            X_test_filtered = X_test_df[testing_only_features].values

            # Log final shapes
            logging.info(f"Shape of X_train: {X_train_full.shape}")
            logging.info(f"Shape of X_test: {X_test_full.shape}")
            logging.info(f"Number of testing features: {len(testing_only_features)}")

            # Package preprocessed data
            preprocessed_data = {
                'X_train': X_train_scaled,                # Scaled training data (all features)
                'X_test': X_test_filtered,         # Scaled testing data (filtered features)
                'y_train': y_train,                # Training labels
                'y_test': y_test,                  # Testing labels
                'scaler': scaler,                  # Scaler used for preprocessing
                'training_features': training_only_features,
                'testing_features': testing_only_features,
                'structure': 'train_test_split'    # Metadata for structure description
            }
            
            output_data = {
                "preprocessing_object": preprocessed_data,
                "dataset": new_dataset
            }
            
            # Serialize the combined object using pickle
            sys.stdout.buffer.write(pickle.dumps(output_data))
            

            # Mark transactions as processed
            for transaction in transactions:
                transactions_DAOIMPL.update_processed_status_after_training(transaction[0], user_id)
            logging.info("Updated transaction processed statuses.")
        else:
            logging.info("No need for retraining, no new positions closed.")
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None



# # # Execution check
if __name__ == "__main__":
    output_path =  sys.argv[0]  
    dataset_id =  sys.argv[1]  
    user_id = sys.argv[2]  
    model_name = sys.argv[3]
    script_id = sys.argv[4]
    preprocess_data(output_path, dataset_id, user_id, model_name, script_id)
