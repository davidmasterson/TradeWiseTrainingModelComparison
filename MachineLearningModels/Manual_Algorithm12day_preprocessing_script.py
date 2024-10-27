# xgb_preprocessing.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pickle
from io import BytesIO
from database import dataset_DAOIMPL, transactions_DAOIMPL
import alpaca_request_methods
import logging
logging.basicConfig(filename='/home/ubuntu/TradeWiseTrainingModelComparison/app_debug.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sample logging statements
logging.debug("Starting preprocessing script.")
logging.info(f"Dataset ID received: {sys.argv[2]}")
# Function to calculate target based on hitting tp1 within 12 days
def calculate_target(row):
    date_purchased = pd.to_datetime(row['dp'])
    date_sold = pd.to_datetime(row['ds'])
    actual_return = row['actual']
    
    if pd.isnull(date_sold) or (date_sold - date_purchased).days > 12:
        return 0
    return 1 if actual_return >= 0 else 0

# RSI calculation
def calculate_rsi(series, window=14):
    if not isinstance(series, (pd.Series, list)):
        return np.nan
    if isinstance(series, list):
        series = pd.Series(series)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI.iloc[-1] if not RSI.empty else np.nan

# Adjusted Momentum calculation
def calculate_momentum(series, period=10):
    if not isinstance(series, (pd.Series, list)):
        return np.nan
    if isinstance(series, list):
        series = pd.Series(series)
    momentum = series.diff(period)
    return momentum.iloc[-1] if not momentum.empty else np.nan

# Adjusted SMA calculation with series check
def calculate_sma(series, window=5):
    if not isinstance(series, (pd.Series, list)):
        return np.nan
    if isinstance(series, list):
        series = pd.Series(series)
    sma = series.rolling(window=window).mean()
    return sma.iloc[-1] if not sma.empty else np.nan

# Adjusted Slope calculation
def calculate_slope(sma, window=4):
    if not isinstance(sma, pd.Series):
        return np.nan
    return sma.diff(window) / window if not sma.empty else np.nan
def calculate_slope(sma, window=4):
    if not isinstance(sma, pd.Series):
        return np.nan
    return sma.diff(window) / window if not sma.empty else np.nan
  # Adjust if columns differ between datasets

# Function to calculate result based on date difference
def calculate_result(row):
    if pd.notna(row['ds']) and (row['ds'] - row['dp']).days <= 12:
        return 'profit'
    return 'loss'

def preprocess_first_dataframe():
    from sector_finder import get_stock_sector
    try:
        # Fetch and create DataFrame
        transactions = transactions_DAOIMPL.get_all_transaction()
        columns = ['id','symbol','dp','ppps','qty','total_buy','pstring','ds','spps','tsp','sstring','expected','proi','actual','tp1','sop','confidence','result','user_id','sector']
        df1 = pd.DataFrame(data=transactions, columns=columns)
        logging.info(f' First Datafram columns list {df1.columns.to_list()}')
        
        # Drop rows with missing 'ds' and apply transformations
        df1.dropna(subset=['ds'], inplace=True)
        df1['dp'] = pd.to_datetime(df1['dp'], errors='coerce')
        df1['ds'] = pd.to_datetime(df1['ds'], errors='coerce')
        df1['sector'] = df1['symbol'].apply(get_stock_sector)
        df1['result'] = df1.apply(calculate_result, axis=1)
        
        logging.info("First dataset processed successfully.")
        return df1

    except Exception as e:
        logging.error(f"Error in first dataset preprocessing: {e}")
        return pd.DataFrame()

def preprocess_second_dataframe(dataset_id):
    from sector_finder import get_stock_sector
    try:
        dataset_id = int(dataset_id)
        dataset_data= dataset_DAOIMPL.get_dataset_data_by_id(dataset_id)
        
        
        df = pd.read_csv(BytesIO(dataset_data), encoding='ISO-8859-1')
        logging.info(f"Original Columns in DataFrame: {df.columns.tolist()}")

        # Rename columns as needed
        column_rename_map = {
            'symbol': 'symbol',
            'date_purchased': 'dp',
            'purchased_pps': 'ppps',
            'qty': 'qty',
            'total_buy_price': 'total_buy',
            'purchase_string': 'pstring',
            'date_sold': 'ds',
            'sold_pps': 'spps',
            'total_sell_price': 'tsp',
            'sell_string': 'sstring',
            'expected_return': 'expected',
            'percentage_roi': 'proi',
            'actual_return': 'actual',
            'tp1': 'tp1',
            'sop': 'sop'
        }

        # Apply renaming
        df = df.rename(columns=column_rename_map)

        # Drop columns not needed
        columns_to_drop = ['stop_loss_price', 'tp2', 'user_id']
        df = df.drop(columns=columns_to_drop, errors='ignore')
        
        df['dp'] = pd.to_datetime(df['dp'], errors='coerce')
        df['ds'] = pd.to_datetime(df['ds'], errors='coerce')

        # Calculate the 'result' column based on days between dp and ds
        df['result'] = df.apply(lambda row: 'profit' if (row['ds'] - row['dp']).days <= 12 else 'loss', axis=1)

        # Log the addition of the result column
        logging.info(f"Result column calculated based on days between dp and ds.")

        # Add missing columns with default values
        df['confidence'] = None  # or set default if known
        
        df['sector'] = df['symbol'].apply(lambda x: get_stock_sector(str(x)) if pd.notna(x) else None)

        # Verify the changes
        logging.info(f"Updated Columns in DataFrame: {df.columns.tolist()}")
    except Exception as e:
        logging.info(f'Unable to preprocess original dataset due to {e}')
        logging.info(f'Original Dataframe new columns is {df.columns.to_list()}')
    return df
        
        
# Main preprocessing function
def preprocess_data(output_path, dataset_id):
    
    # transactions = transactions_DAOIMPL.get_all_transaction()
    # columns = ['id','symbol','dp','ppps','qty','total_buy','pstring','ds','spps','tsp','sstring','expected','proi','actual','tp1','sop','confidence','result','user_id','sector']
    # df1 = pd.DataFrame(data=transactions, columns=columns)
  
    try:
        df1 = preprocess_first_dataframe()
        df2 = preprocess_second_dataframe(dataset_id)
        df = pd.concat([df1, df2], ignore_index=True)

        # Calculate target variable
        df['hit_tp1_within_12'] = df.apply(calculate_target, axis=1)

        # Calculate technical indicators
        df['Momentum'] = df['spps'].apply(lambda x: calculate_momentum(x, period=10))
        df['RSI'] = df['spps'].apply(lambda x: calculate_rsi(x, window=14))
        df['SMA5'] = df['spps'].apply(lambda x: calculate_sma(x, window=5))
        df['SMA20'] = df['spps'].apply(lambda x: calculate_sma(x, window=20))
        df['SMA5_Slope'] = df['SMA5'].apply(lambda x: calculate_slope(pd.Series(x)))
        df['SMA20_Slope'] = df['SMA20'].apply(lambda x: calculate_slope(pd.Series(x)))
        logging.info("Calculated technical indicators.")

        # Encode categorical features
        label_encoder = LabelEncoder()
        df['symbol_encoded'] = label_encoder.fit_transform(df['symbol'])
        df['sector_encoded'] = label_encoder.fit_transform(df['sector'])
        logging.info("Encoded categorical features.")

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

        # Summary statistics and feature selection
        df['SMA5_last'] = df['SMA5'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
        df['SMA20_last'] = df['SMA20'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
        df['SMA5_Slope_last'] = df['SMA5_Slope'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
        df['SMA20_Slope_last'] = df['SMA20_Slope'].apply(lambda x: x[-1] if isinstance(x, list) else np.nan)
        logging.info("Computed summary statistics.")

        # Drop unnecessary columns
        df = df.drop(['SMA5', 'SMA20', 'SMA5_Slope', 'SMA20_Slope', 'symbol', 'dp', 'ds'], axis=1)
        logging.info("Dropped unnecessary columns.")

        # Separate features and target
        X = df.drop(['hit_tp1_within_12'], axis=1)
        y = df['hit_tp1_within_12']
        logging.info("Separated features and target.")

        # Ensure all data in X is numeric
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Scale features
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X)

        # Train-test split for modeling
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Package preprocessed data
        preprocessed_data = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler,
            'structure': 'train_test_split'
        }
        logging.info("Packaged preprocessed data successfully.")

        with open(output_path, 'wb') as f:
            pickle.dump(preprocessed_data, f)
        
        logging.info(f"Preprocessing complete. Data saved to {output_path}")
        return preprocess_data
        
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None

# Execution check
if __name__ == "__main__":
    output_path = sys.argv[1]  # Adjust the order of arguments
    dataset_id = sys.argv[2]  # Expect dataset_id instead of dataset_path
    preprocess_data(output_path, dataset_id)
