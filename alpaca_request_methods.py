from datetime import datetime, timedelta
import pandas as pd
import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv



load_dotenv()
# Function to return api connection object
def get_alpaca_connection():
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    BASE_URL = os.getenv('BASE_URL')
    print(ALPACA_API_KEY)

    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
    return api

# Function to get historical data for a list of symbols
def fetch_stock_data(symbols, years=5):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    all_data = []
    connection = get_alpaca_connection()

    for symbol in symbols:
        print(f"Fetching data for {symbol}")
        barset = connection.get_bars(symbol, '1Day', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        data = {
            'date': [bar.t.date() for bar in barset],
            'close': [bar.c for bar in barset],
            'symbol': symbol
        }
        df = pd.DataFrame(data)
        print(df)
        df.sort_values(by='date', ascending=False, inplace=True)
        print(df)
        all_data.append(df)
    
    all_data_df = pd.concat(all_data)
    all_data_df.to_csv('stock_prices.csv', index=False)
    return all_data_df