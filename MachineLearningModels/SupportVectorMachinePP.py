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
from MachineLearningModels import manual_alg_requisition_script
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
    
def calculate_sentiment(symbol, date_of_lookup):
    from datetime import datetime
    from Selenium import selenium_file
    date_of_lookup = datetime.strptime(date_of_lookup, "%Y-%m-%d")
    try:
        info = selenium_file.get_historical_stock_specific_sentiment_scores(symbol, date_of_lookup)
        avg_neu = info[0][0]
        avg_pos = info[0][1]
        avg_neg = info[0][2]
        
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
        df = pd.read_csv('historical_ds_base.csv')
        # df[['sa_neu_open', 'sa_pos_open', 'sa_neg_open']] = df.apply(lambda row: pd.Series(calculate_sentiment(row['symbol'], row['dp'])), axis=1)
            
        # df[['pol_neu_open'], df['pol_pos_open'], df['pol_neg_open']] = df.apply(lambda row: pd.Series(calculate_historical_political_climate(row['symbol'], row['dp'])), axis=1)
        # df['check5con'] = df[['check1sl', 'check2rev', 'check3fib']].sum(axis=1)
        
        # df['pol_neu_close'], df['pol_pos_close'], df['pol_neg_close'] = df.apply(lambda row: pd.Series(calculate_historical_political_climate(row['symbol'], row['dp'])), axis=1)
        # df[['sa_neu_close', 'sa_pos_close', 'sa_neg_close']] = df.apply(lambda row: pd.Series(calculate_sentiment(row['symbol'], row['dp'])), axis=1)
        # # Date-based feature engineering
            
        df = df.dropna() 
        # # Date-based feature engineering
        # df['dp'] = pd.to_datetime(df['dp'])
        # df['purchase_day'] = df['dp'].dt.day
        # df['purchase_month'] = df['dp'].dt.month
        # df['purchase_year'] = df['dp'].dt.year
        # df['ds'] = pd.to_datetime(df['ds'])
        # df['sell_day'] = df['ds'].dt.day
        # df['sell_month'] = df['ds'].dt.month
        # df['sell_year'] = df['ds'].dt.year
        # logging.info("Performed date-based feature engineering.")
        
        # Add target column
        df['hit_tp1'] = df.apply(calculate_target, axis=1)
        # Drop unnecessary columns
       
        
        # Combine Datasets Now
        df_final = df.copy()
        df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
        # Encoding categorical features
        label_encoder = LabelEncoder()
        df_final['symbol_encoded'] = label_encoder.fit_transform(df_final['symbol'])
        df_final['sector_encoded'] = label_encoder.fit_transform(df_final['sector'])
        new_dataset = df_final.copy()
        df_final.to_csv('completelyFreshBaseDS.csv')
        
        df_final.drop(['sector', 'symbol', 'ds', 'dp'], axis=1, inplace=True)
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
