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
    
def calculate_sentiment(symbol):
    try:
        info = manual_alg_requisition_script.request_articles(symbol)
        avg_neu, avg_pos, avg_neg = manual_alg_requisition_script.process_phrase_for_sentiment(info)
        logging.info(f'Sentiment is {avg_neu, avg_pos, avg_neg}')
        
        return avg_neu, avg_pos, avg_neg  
    except Exception as e:
        logging.error(f'Error calculating sentiment: {e}')
        return 0, 0, 0

def calculate_historical_sentiment(symbol, date_requirement):
    from datetime import datetime
    from HistoricalFetcherAndScraper import scraper
    import json
    article_texts = []
    try:
        # date_object = datetime.strptime(date_requirement, '%Y-%m-%d').date()
        
        response_text = scraper.search(date_requirement,symbol,user_id)
        response_json = json.loads(response_text)
        articles = response_json.get("news", [])
        if not response_text:
            return 0, 0, 0
        for article in articles:
            summary = article.get("headline", "No summary available")
            article_texts.append(summary)
        sa_neu, sa_pos, sa_neg = manual_alg_requisition_script.process_phrase_for_sentiment(article_texts)
        
        return sa_neu, sa_pos, sa_neg  
    except Exception as e:
        logging.error(f'Error calculating sentiment: {e}')
        return 0, 0, 0
    
def calculate_historical_political_climate(date_requirement):
    from Selenium import selenium_file
    from datetime import datetime
    # date_requirement = datetime.strptime(date_requirement, '%Y-%m-%d')
    selenium_return = selenium_file.get_historical_political_sentiment_scores(date_requirement)
    try:
        if selenium_return:
            pol_neu, pol_pos, pol_neg = selenium_return[0][0], selenium_return[0][1], selenium_return[0][2]
    except:
        pol_neu, pol_pos, pol_neg = selenium_return[0], selenium_return[1], selenium_return[2]
        return pol_neu, pol_pos, pol_neg
    else:
        return 0, 0, 0
       
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
def preprocess_first_dataframe_with_unprocessed(user_id, required_models):
    try:
        # Fetch and create DataFrame
        
        try:
            required_models = [mod[0] for mod in models_DAOIMPL.get_selected_model_names_for_user(user_id)]
            transactions = transaction_model_status_DAOIMPL.get_transactions_needing_processing(user_id, required_models)
        except Exception as e:
            logging.error(f"Error fetching transactions for user {user_id}: {e}")
            return None

        print(transactions[0])
        columns = ['id','symbol','dp','ppps','qty','total_buy','pstring','ds','spps','tsp','sstring','expected',
                   'proi','actual','tp1','sop','confidence','result','user_id','sector', 'processed','pol_neu_open',
                   'pol_pos_open','pol_neg_open','sa_neu_open','sa_pos_open','sa_neg_open','pol_neu_close',
                   'pol_pos_close','pol_neg_close','sa_neu_close','sa_pos_close','sa_neg_close']
        df1 = pd.DataFrame(data=transactions, columns=columns)
        # Drop rows with missing 'ds' and apply transformations
        df1.dropna(subset=['ds'], inplace=True)
        df1['result'] = df1['result'].apply(lambda x: 0 if x == 'loss' else 1) 
        logging.info("First dataset processed successfully.")
        return [df1,transactions]
    except Exception as e:
        logging.error(f"Error in first dataset preprocessing: {e}")
        return None

def handle_transaction_status(transaction_id, user_id, model_name, required_models):
    try:
        transaction_model_status_DAOIMPL.mark_transaction_processed(transaction_id, model_name, user_id)
    except Exception as e:
        logging.error(f"Error marking transaction {transaction_id} as processed: {e}")
    if transaction_model_status_DAOIMPL.check_all_models_processed(transaction_id, user_id, required_models):
        transactions_DAOIMPL.update_processed_status_after_training(transaction_id, user_id)
        logging.info(f"Transaction {transaction_id} fully processed.")
    else:
        logging.info(f"Transaction {transaction_id} pending for other models.")

# Main preprocessing function
def preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name):
    user_id = int(user_id)
    dataset_id = int(dataset_id)
    script_id = int(script_id)
    if not model_name:
        logging.error("Model name is required but not provided.")
        return None
    required_models = models_DAOIMPL.get_selected_model_names_for_user(user_id)
    try:
        df1 = preprocess_first_dataframe_with_unprocessed(user_id, required_models) 
        if df1 is not None:
            df = df1[0] 
            transactions = df1[1]
        
        
            
            # Parallel processing for technical indicators
            logging.info("Starting parallel processing for check1sl.")
            df['check1sl'] = parallel_apply_single_arg(df['symbol'], calculate_first_check)
            logging.info("Starting parallel processing for check2rev.")
            df['check2rev'] = parallel_apply_single_arg(df['symbol'], calculate_second_check)
            logging.info("Starting parallel processing for check3fib.")
            df['check3fib'] = parallel_apply_single_arg(df['symbol'], calculate_third_check)
            logging.info("Calculated slopes, reversals, and fibs.")
            # Calculate final confidence score
            logging.info("Calculated confidence scores.")
            df = df.dropna()
            df[['sa_neu_open', 'sa_pos_open', 'sa_neg_open']] = df.apply(lambda row: pd.Series(calculate_historical_sentiment(row['symbol'], row['dp'])), axis=1)
            
            df['pol_neu_open'], df['pol_pos_open'], df['pol_neg_open'] = zip(*df['dp'].apply(calculate_historical_political_climate))
            df['check5con'] = df[['check1sl', 'check2rev', 'check3fib']].sum(axis=1)
            
            df['pol_neu_close'], df['pol_pos_close'], df['pol_neg_close'] = zip(*df['ds'].apply(calculate_historical_political_climate))
            df[['sa_neu_close', 'sa_pos_close', 'sa_neg_close']] = df.apply(lambda row: pd.Series(calculate_historical_sentiment(row['symbol'], row['ds'])), axis=1)
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
            # Combine Datasets Now
            old_ds = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
            if old_ds:
                old_df = pickle.loads(old_ds)
            else:
                old_df = pd.DataFrame()
            df_final = pd.concat([df, old_df], ignore_index=True)
            
            
            
            df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]

            
            
            # Encoding categorical features
            label_encoder = LabelEncoder()
            df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
            df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
            
            new_dataset = df_final.copy()
            
            df_final.drop(['sector', 'symbol'], axis=1, inplace=True)
            logging.info("Encoded categorical features.")


            # Convert columns to numeric as needed
            df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
            target_column = 3  # Column index for the target variable
            time_steps = 60  # Define the number of time steps
            df['hit_tp1'] = df.apply(calculate_target)
            # Prepare the input data (X) and target variable (y)
            X, y, scaler = prepare_data(df, target_column, time_steps)
            # Split data into training and testing sets
            train_size = int(0.8 * len(X))
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Ensure feature names are consistent during scaling
            scaler = MinMaxScaler(feature_range=(0, 1))
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            # Convert scaled data back to DataFrame to preserve column names
            X_train_df = pd.DataFrame(X_train_scaled, columns=X.columns)
            X_test_df = pd.DataFrame(X_test_scaled, columns=X.columns)
            
            # Package preprocessed data
            preprocessed_data = {
                'X_train': X_train_df,          # Scaled training data as DataFrame
                'X_test': X_test_df,            # Scaled testing data as DataFrame
                'y_train': y_train.reset_index(drop=True),  # Training labels
                'y_test': y_test.reset_index(drop=True),    # Testing labels
                'scaler': scaler,               # Scaler used for preprocessing
                'structure': 'train_test_split', # Metadata for structure description
                'columns' : X_train_df.columns.to_list()  # Ouput the column names for feature importance call.
            }
            logging.info("Preprocessing complete. Packaged data for modeling.")
            
            output_data = {
                "preprocessing_object": preprocessed_data,
                "dataset": new_dataset
            }   
            for transaction in transactions:
                handle_transaction_status(transaction[0], user_id, model_name, required_models)
            # Serialize the combined object using pickle
            try:
                output_data_bin = pickle.dumps(output_data)
                
                with open(output_data_path, 'wb') as bin_writer:
                    bin_writer.write(output_data_bin)
            except IOError as e:
                print(f"Error writing to file: {e}")
        else:
            old_ds = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
            if old_ds:
                old_df = pickle.loads(old_ds)
            else:
                old_df = pd.DataFrame()
            df_final = old_df
            
            
            
            df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]

            
            
            # Encoding categorical features
            label_encoder = LabelEncoder()
            df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
            df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
            
            new_dataset = df_final.copy()
            
            df_final.drop(['sector', 'symbol'], axis=1, inplace=True)
            logging.info("Encoded categorical features.")


            # Convert columns to numeric as needed
            # df_final = df_final.apply(pd.to_numeric, errors='coerce').fillna(0)
            target_column = 27 # Column index for the target variable
            time_steps = 60  # Define the number of time steps
            df_final['hit_tp1'] = df_final.apply(calculate_target)
            # Prepare the input data (X) and target variable (y)
            X, y, scaler = prepare_data(df_final, target_column, time_steps)
            # Split data into training and testing sets
            train_size = int(0.8 * len(X))
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
           # Flatten the time steps and features for scaling
            n_samples, n_time_steps, n_features = X_train.shape
            X_train_reshaped = X_train.reshape(-1, n_features)
            X_test_reshaped = X_test.reshape(-1, n_features)

            # Create a scaler instance and fit_transform the training data
            scaler = MinMaxScaler(feature_range=(0, 1))
            X_train_scaled = scaler.fit_transform(X_train_reshaped)

            # Transform the testing data
            X_test_scaled = scaler.transform(X_test_reshaped)

            # Reshape the scaled data back to 3D
            X_train_scaled = X_train_scaled.reshape(n_samples, n_time_steps, n_features)
            X_test_scaled = X_test_scaled.reshape(X_test.shape[0], n_time_steps, n_features)
            # Convert scaled data back to DataFrame to preserve column names
            
            
            # Package preprocessed data
            preprocessed_data = {
                'X_train': X_train_scaled,          # Scaled training data as DataFrame
                'X_test': X_test_scaled,            # Scaled testing data as DataFrame
                'y_train': y_train,  # Training labels
                'y_test': y_test,    # Testing labels
                'scaler': scaler,               # Scaler used for preprocessing
                'structure': 'train_test_split', # Metadata for structure description
                
            }
            logging.info("Preprocessing complete. Packaged data for modeling.")
            
            output_data = {
                "preprocessing_object": preprocessed_data,
                "dataset": new_dataset
            }   
            # Serialize the combined object using pickle
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

