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
        print(sa_neu, sa_pos, sa_neg)
        return sa_neu, sa_pos, sa_neg  
    except Exception as e:
        logging.error(f'Error calculating sentiment: {e}')
        return 0, 0, 0
    
def calculate_historical_political_climate(date_requirement):
    from Selenium import selenium_file
    from datetime import datetime
    # date_requirement = datetime.strptime(date_requirement, '%Y-%m-%d')
    selenium_return = selenium_file.get_historical_political_sentiment_scores(date_requirement)
    print(selenium_return)
    try:
        if selenium_return:
            try:
                pol_neu, pol_pos, pol_neg = selenium_return[0][0], selenium_return[0][1], selenium_return[0][2]
                return pol_neu,pol_pos,pol_neg
            except:
                try:
                    pol_neu, pol_pos, pol_neg = selenium_return[0], selenium_return[1], selenium_return[2]
                    return pol_neu, pol_pos, pol_neg
                except:
                    return 0, 0, 0
    except:
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
def preprocess_first_dataframe_with_unprocessed(user_id, required_models, model_name):
    try:
        # Fetch and create DataFrame
        
        try:
            transactions = transaction_model_status_DAOIMPL.get_transaction_ids_unprocessed_for_user_by_model_and_uprocessed_in_transactions(user_id, model_name, required_models )
        except Exception as e:
            logging.error(f"Error fetching transactions for user {user_id}: {e}")
            return None

        print(transactions[0])
        columns = ['id','symbol','dp','ppps','qty','total_buy','pstring','ds','spps','tsp','sstring','expected',
                   'proi','actual','tp1','sop','confidence','result','user_id','sector', 'processed','pol_neu_open',
                   'pol_pos_open','pol_neg_open','sa_neu_open','sa_pos_open','sa_neg_open','pol_neu_close',
                   'pol_pos_close','pol_neg_close','sa_neu_close','sa_pos_close','sa_neg_close','tms_id','transaction_id',
                   'model_name', 'tms_user_id','tms_processed']
        df1 = pd.DataFrame(data=transactions, columns=columns)
        # Drop rows with missing 'ds' and apply transformations
        df1.drop(['tms_id','transaction_id',
                   'model_name', 'tms_user_id','tms_processed'], axis=1, inplace=True)
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

# Load and preprocess dataset
def preprocess_data(output_path, dataset_id, user_id, output_data_path, script_id, model_name):
    try:
        user_id = int(user_id)
        dataset_id = int(dataset_id)
        script_id = int(script_id)
        if not model_name:
            logging.error("Model name is required but not provided.")
            return None
        required_models = [mod[0] for mod in models_DAOIMPL.get_selected_model_names_for_user(user_id)]
        df1 = preprocess_first_dataframe_with_unprocessed(user_id, required_models, model_name) 
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
            # Calculate technical indicators
            df['RSI'] = calculate_rsi(df['ppps'], 14)
            df['SMA'] = calculate_sma(df['ppps'], 20)
            df['EMA'] = calculate_ema(df['ppps'], 20)
            df['Momentum'] = calculate_momentum(df['ppps'], 10)

            df.fillna(0, inplace=True)
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
            

            
            try:
                df_final = df_final.drop(['sector','symbol'], axis=1)
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
            

            
            try:
                df_final = df_final.drop(['sector','symbol'], axis=1)
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

            # Ensure feature names are consistent during scaling
            scaler = MinMaxScaler(feature_range=(0, 1))
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Convert scaled data back to DataFrame to preserve column names
            X_train_df = pd.DataFrame(X_train_scaled, columns=X.columns)
            X_test_df = pd.DataFrame(X_test_scaled, columns=X.columns)
            
            # Serialize preprocessed data
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
            # Serialize the combined object using pickle
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
    
