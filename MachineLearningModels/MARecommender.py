

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pickle
from MachineLearningModels import manual_alg_requisition_script
import logging
from sector_finder import get_stock_sector
from database import  trade_settings_DAOIMPL, dataset_DAOIMPL, models_DAOIMPL
import concurrent.futures
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sector_finder import get_stock_sector
from datetime import datetime
from HistoricalFetcherAndScraper import scraper
from Selenium import selenium_file
    

logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")


'''------------------------------Preprocessing helper functions-------------------------------------------------------'''
# Function to calculate target based on hitting tp1 within 12 days
def calculate_target(row):
    date_purchased = pd.to_datetime(row['dp'])
    date_sold = pd.to_datetime(row['ds'])
    actual_return = row['actual']
    
    if pd.isnull(date_sold) or (date_sold - date_purchased).days > 12:
        return 0
    return 1 if actual_return >= 0 else 0

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
            return 20
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
    
def calculate_historical_sentiment(symbol, date_requirement):
    
    import json
    article_texts = []
    try:
        date_object = datetime.strptime(date_requirement, '%Y-%m-%d').date()
        
        response_text = scraper.search(date_object,symbol,user_id)
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
    
    date_requirement = datetime.strptime(date_requirement, '%Y-%m-%d')
    selenium_return = selenium_file.get_historical_political_sentiment_scores(date_requirement)
    try:
        if selenium_return:
            pol_neu, pol_pos, pol_neg = selenium_return[0][0], selenium_return[0][1], selenium_return[0][2]
    except:
        pol_neu, pol_pos, pol_neg = selenium_return[0], selenium_return[1], selenium_return[2]
        return pol_neu, pol_pos, pol_neg
    else:
        return 0, 0, 0
    
def get_stock_sector_for_df_symbol(symbol):
    """
    Fetches the stock sector for a given symbol.
    Logs an error and returns None if the fetch fails.
    """
    try:
        return get_stock_sector(symbol)  # Replace with your actual API or logic to fetch the sector
    except Exception as e:
        logging.error(f"Error getting stock sector for symbol '{symbol}': {e}")
        return None


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


''' ---------------------------END PREPROCESSING HELPER FUNCTIONS-------------------------------------------------------------------'''


def preprocess_and_train(user_id, output_file_path, dataset_id, model_id):
    try:
        model_id = int(model_id)
        prebuilt_model = models_DAOIMPL.get_models_for_user_by_model_id(model_id)
        prebuilt_model_bin = prebuilt_model[3]
        prebuilt_model_bin = pickle.loads(prebuilt_model_bin)
        
        
        # Load trade settings and dataset
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        trade_settings = trade_settings_DAOIMPL.get_trade_settings_by_user(user_id)
        confidence_threshold = int(trade_settings[5])
        logging.info(f"Loaded trade settings with confidence threshold: {confidence_threshold}")

        df = pd.read_csv('Hypothetical_Predictor/transactions.csv')
        logging.info("Data loaded successfully.")

        # Process indicators in parallel (Assuming parallel_apply is defined elsewhere)
        df['check1sl'] = parallel_apply_single_arg(df['symbol'], calculate_first_check)
        df['check2rev'] = parallel_apply_single_arg(df['symbol'], calculate_second_check)
        df['check3fib'] = parallel_apply_single_arg(df['symbol'], calculate_third_check)
        df['sector'] = parallel_apply_single_arg(df['symbol'], get_stock_sector_for_df_symbol)
        # Assuming df['symbol'] has all the symbols
                
        df['ds'] = '1900-1-1'
        logging.info("Technical indicators calculated.")
        df[['sa_neu_open', 'sa_pos_open', 'sa_neg_open']] = df.apply(lambda row: pd.Series(calculate_historical_sentiment(row['symbol'], row['dp'])), axis=1)
        pol_neu_open, pol_pos_open, pol_neg_open = calculate_historical_political_climate(df.loc[0, 'dp'])
        df['pol_neu_open'], df['pol_pos_open'], df['pol_neg_open'] = pol_neu_open, pol_pos_open, pol_neg_open

        # Calculate confidence score and process dates
        df['dp'] = pd.to_datetime(df['dp'])
        df['purchase_day'] = df['dp'].dt.day
        df['purchase_month'] = df['dp'].dt.month
        df['purchase_year'] = df['dp'].dt.year
        df['ds'] = pd.to_datetime(df['ds'])
        df['sell_day'] = df['ds'].dt.day
        df['sell_month'] = df['ds'].dt.month
        df['sell_year'] = df['ds'].dt.year
        logging.info("Processed dates and confidence scores.")
        df['sa_neu_close'], df['sa_pos_close'], df['sa_neg_close'] = 0, 0, 0
        df['pol_neu_close'], df['pol_pos_close'], df['pol_neg_close'] = 0, 0, 0
        df['check5con'] = df[['check1sl', 'check2rev', 'check3fib']].sum(axis=1)

        # Drop unnecessary columns

        # Combine with additional dataset
        finalized_dataset_data = dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
        if finalized_dataset_data:
            finalized_dataset_data = pickle.loads(finalized_dataset_data)
            df = pd.concat([df, finalized_dataset_data], axis=0).drop_duplicates()
            logging.info("Combined with finalized dataset.")

        drop_columns = ['id', 'pstring', 'spps', 'tsp', 'sstring', 'expected', 
                        'result', 'user_id', 'processed', 'dp', 'confidence', 
                        'ds', 'actual', 'proi']
        df = df.drop(columns=drop_columns, errors='ignore')
        logging.info("Unnecessary columns dropped.")
        # Encode categorical features and normalize data
        label_encoder = LabelEncoder()
        df['symbol_encoded'] = label_encoder.fit_transform(df['symbol'])
        df['sector_encoded'] = label_encoder.fit_transform(df['sector'])
        symbol_backup = df['symbol']
        sector_backup = df['sector']
        df.drop(['symbol', 'sector'], axis=1, inplace=True)

        # Now I need to split the train, test, prediction sets
        X = df.drop('hit_tp1', axis=1)  # Features for entire dataset
        y = df['hit_tp1']               # Target for entire dataset

        # Scaling features (if needed)
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        
        known_indices = y.notna()
        unknown_indices = y.isna()
        
        X_known_scaled = X_scaled[known_indices]
        y_known = y[known_indices]

        X_unknown_scaled = X_scaled[unknown_indices]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X_known_scaled, y_known, test_size=0.2, random_state=42)

        print(np.bincount(y_train))

        # Predict future values for the data where the target is unknown
        predictions = prebuilt_model_bin.predict(X_unknown_scaled)
        probabilities = prebuilt_model_bin.predict_proba(X_unknown_scaled)[:, 1]  # Get probabilities for the positive class
        # Add predictions and probabilities to DataFrame
        df.loc[unknown_indices, 'Prediction'] = predictions
        df.loc[unknown_indices, 'Probability'] = probabilities

        df['symbol'] = symbol_backup
        df['sector'] = sector_backup
        symbols = df['symbol'].tolist()
        sectors = df['sector'].tolist()
        confidence_scores = df['check5con'].tolist()
        trade_settings = trade_settings_DAOIMPL.get_trade_settings_by_user(user_id)  # example threshold, set as needed
        confidence_threshold = trade_settings[5]
        results = [{'Symbol': symbol, 'Prediction': pred, 'Probability': prob, 'Confidence': con, 'Sector': sector}
                   for symbol, pred, prob, con, sector in zip(symbols, predictions, probabilities, confidence_scores, sectors) if (pred == 1 and prob >= .5)]


        
        try:
            output_data_bin = pickle.dumps(results)
            
            with open(output_file_path, 'wb') as bin_writer:
                bin_writer.write(output_data_bin)
        except IOError as e:
            print(f"Error writing to file {e}")
        
       

    except Exception as e:
        logging.exception(f"Error during preprocessing and training: {e}")
        return None



# # # Execution check
if __name__ == "__main__":
    output_path =  sys.argv[0]    
    user_id = sys.argv[1]  
    tempfile_path2 = sys.argv[2]
    dataset_id = sys.argv[3]
    model_id = sys.argv[4]
    preprocess_and_train(user_id,tempfile_path2,dataset_id, model_id)
