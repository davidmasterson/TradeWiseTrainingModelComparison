from datetime import datetime, timedelta, date
import pandas as pd
import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from database import transactions_DAOIMPL



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
def fetch_stock_data(years=5):
    trans = transactions_DAOIMPL.read_in_transactions('/david-transactions-data.csv')
    trans_data = transactions_DAOIMPL.convert_lines_to_transaction_info_for_DF(trans[0], trans[1])
    df_data = {
            'symbol':[],
            'historical_dates': [],
            'open':[],
            'close':[],
            'purchase_date':[],
            'purchase_price':[],
            'sell_date':[],
            'sell_price': [],
            'actual_return' : [],
            'days_to_sell': [],
            'take_profit_price':[],
            'stop_out_price':[],
            'hit_take_profit': [],
            # 'slope5': [],
            # 'slope20': [],
            # 'slope200': [],
            # 'sma5': [],
            # 'sma20': [],
            # 'sma200': []
        }
    

    for trans in trans_data:
        end_date = trans[1]
        start_date = end_date - timedelta(days=years*365)
        symbol = trans[0]
        purchase_date = trans[1]
        purchase_price = trans[2]
        sell_date = trans[3]
        sell_price = trans[4]
        actual_return = trans[5]
        days_to_sell = trans[6]                          
        take_profit = trans[7]
        stop_price = trans[8]
        hit_take_profit = trans[9]
        connection = get_alpaca_connection()
        
        
        print(f"Fetching data for {symbol}")
        barset = connection.get_bars(symbol, '1Day', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        data = {
            'date': [date(bar.t.year, bar.t.month, bar.t.day) for bar in barset],
            'close': [bar.c for bar in barset],
            'open': [bar.o for bar in barset],
        }
        print(len(data['close']), len(data['open']))

        
        
        df_data['symbol'].append(symbol)
        df_data['historical_dates'].append(data['date'])
        df_data['open'].append(data['open'])
        df_data['close'].append(data['close'])
        df_data['purchase_date'].append(purchase_date)
        df_data['purchase_price'].append(purchase_price)
        df_data['sell_date'].append(sell_date)
        df_data['sell_price'].append(sell_price)
        df_data['actual_return'].append(actual_return)
        df_data['days_to_sell'].append(days_to_sell)
        df_data['take_profit_price'].append(take_profit)
        df_data['stop_out_price'].append(stop_price)
        df_data['hit_take_profit'].append(hit_take_profit)

        # print(df)
        # df.sort_values(by='date', ascending=False, inplace=True)
        # print(df)
        # all_data.append(df)
        connection.close()
    
    df = pd.DataFrame(df_data)
    df.to_csv('stock_trans_data.csv', index=False)
    return df_data

