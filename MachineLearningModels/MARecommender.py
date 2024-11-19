

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
import logging
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")

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
        avg_neut, avg_pos, avg_neg = manual_alg_requisition_script.process_phrase_for_sentiment(info)
        logging.info(f'Sentiment is {avg_neut, avg_pos, avg_neg}')
        
        return avg_neut, avg_pos, avg_neg  
    except Exception as e:
        logging.error(f'Error calculating sentiment: {e}')
        return 0, 0, 0
    

        
import concurrent.futures
import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pickle
from database import dataset_DAOIMPL, transactions_DAOIMPL
from MachineLearningModels import manual_alg_requisition_script
import sector_finder

logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parallel_apply(symbols, func, max_workers=20):
    """ Helper function to apply a calculation in parallel. """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, symbols))
    return results

# Main preprocessing function
def preprocess_data(user_id, model_name):
    from sector_finder import get_stock_sector
    from database import preprocessing_scripts_DAOIMPL
    from flask import flash
    from Models import preprocessing_script
    
    try:
        # Load the CSV file
        df = pd.read_csv('Hypothetical_Predictor/transactions.csv')
        
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        logging.info("Calculated technical indicators.")
        df['sector'] = df['symbol'].apply(get_stock_sector)
        
        # Calculate Stocksbot manual algo checks in parallel
        logging.info("Starting parallel processing for check1sl.")
        df['check1sl'] = parallel_apply(df['symbol'], calculate_first_check)
        logging.info("Calculated slopes.")

        logging.info("Starting parallel processing for check2rev.")
        df['check2rev'] = parallel_apply(df['symbol'], calculate_second_check)
        logging.info("Calculated reversals.")

        logging.info("Starting parallel processing for check3fib.")
        df['check3fib'] = parallel_apply(df['symbol'], calculate_third_check)
        logging.info("Calculated fibs.")
        
        try:
            df['sa_neu'], df['sa_pos'], df['sa_neg'] = zip(*parallel_apply(df['symbol'], calculate_sentiment))
        except Exception as e:
            logging.error(f"Unable to unpack values for symbol sentiment analysis due to {e}")
        logging.info("Calculated symbol-specific sentiment.")
        # Calculate the political sentiment scores once, as they apply to all rows
        try:
            pol_neu, pol_pos, pol_neg = manual_alg_requisition_script.process_daily_political_sentiment()
            df['pol_neu'], df['pol_pos'], df['pol_neg'] = pol_neu, pol_pos, pol_neg
            logging.info("Calculated and applied daily political sentiment scores to all rows.")
        except Exception as e:
            logging.error(f"Error calculating political sentiment: {e}")
        # Calculate final confidence score
        df['check5con'] = df[['check1sl', 'check2rev', 'check3fib']].sum(axis=1)
        logging.info("Calculated confidence.")

        # Drop unnecessary columns
        # df.dropna(inplace=True)
        df['dp'] = pd.to_datetime(df['dp'])
        df['purchase_day'] = df['dp'].dt.day
        df['purchase_month'] = df['dp'].dt.month
        df['purchase_year'] = df['dp'].dt.year
        df['ds'] = pd.to_datetime(df['ds'])
        df['sell_day'] = df['ds'].dt.day
        df['sell_month'] = df['ds'].dt.month
        df['sell_year'] = df['ds'].dt.year
        logging.info("Performed date-based feature engineering.")

        # Drop more unnecessary columns
        df = df.drop(['id', 'pstring','ds', 'spps', 'tsp', 'sstring', 'expected', 'proi', 'result', 'user_id',
                      'processed', 'sell_day', 'sell_month', 'sell_year'], axis=1)
        logging.info("Dropped unnecessary columns.")
       
        # Encode categorical features
        label_encoder = LabelEncoder()
        symdf = pd.DataFrame(df['symbol'])
        secdf = pd.DataFrame(df['sector'])
        df['symbol_encoded'] = label_encoder.fit_transform(df['symbol'])
        df['sector_encoded'] = label_encoder.fit_transform(df['sector'])
        df.drop(['sector', 'dp', 'symbol', 'actual'], axis=1, inplace=True)
        logging.info("Encoded categorical features.")
        df['hit_tp1'] = None

        X = df.drop(['hit_tp1'], axis=1)
        logging.error(f'X = {X.columns.to_list()}')
        logging.error(f'DF = {df.columns.to_list()}')
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)  # Ensure all data in X is numeric

        # Scale features
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X)

        from database import models_DAOIMPL
        model_blob = models_DAOIMPL.get_model_blob_from_db_by_model_name_and_user_id(model_name, user_id)
        model = pickle.loads(model_blob)  # Deserialize model

        # Make predictions using the trained model
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)[:, 1]  # Probability of hitting the target (class 1 probability)
        confidence_scores = df['check5con'].tolist()
        # Filter symbols based on probability threshold (e.g., >= 0.7 for recommendation)
        symbols = symdf['symbol'].tolist()
        sectors = secdf['sector'].tolist()
        results = [{'Symbol': symbol, 'Prediction': pred, 'Probability': prob, 'Confidence': con, 'Sector': sector}
                   for symbol, pred, prob, con, sector in zip(symbols, predictions, probabilities, confidence_scores, sectors) if pred == 1 and prob >= .5]

        logging.info("Predictions and probabilities calculated successfully.")
        
        return results  # Return only recommended symbols with high probability
        
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None



