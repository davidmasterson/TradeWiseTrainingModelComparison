from datetime import datetime, timedelta, date
import pandas as pd
import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from database import transactions_DAOIMPL
import socketio
import sector_finder




load_dotenv()

# This will hold the reference to SocketIO instance passed from app.py
sio = None

def set_socketio_instance(socketio_instance):
    global sio
    sio = socketio_instance
# Function to return api connection object
def get_alpaca_connection():
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    BASE_URL = os.getenv('BASE_URL')

    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
    return api

# Function to get historical data for a list of symbols
def fetch_stock_data(years=5):
    percent = 0
    trans = transactions_DAOIMPL.read_in_transactions('/Model_Training/transactions.csv')
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
            'sector':[]
        }
    
    total_iterations = len(trans_data)
    for i, trans in enumerate(trans_data):
        percent = int((i / total_iterations) * 100)
        sio.emit('update progress', {'percent': percent, 'type': 'model'})
        
        end_date = trans[3]
        symbol = trans[0]
        purchase_date = trans[1]
        purchase_price = trans[2]
        sell_date = trans[3]
        sell_price = trans[4]
        actual_return = trans[5]
        print(type(end_date))
        if sell_date == 'N/A':
            start_date = date.today() - timedelta(days=years*365)
            end_date = date.today()
        else:
            start_date = end_date - timedelta(days=years*365)
        days_to_sell = trans[6]                          
        take_profit = trans[7]
        stop_price = trans[8]
        hit_take_profit = trans[9]
        sector = sector_finder.get_stock_sector(symbol)
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
        df_data['sector'].append(sector)
        connection.close()
    
    df = pd.DataFrame(df_data)
    df.to_csv('Model_Training/stock_trans_data.csv', index=False)
    
    sio.emit('update progress', {'percent': percent, 'type': 'model'})
    return df_data


def get_symbol_current_price(symbol):
    try:
        conn = get_alpaca_connection()
        asset = conn.get_latest_bar(symbol)
        return asset.c
    except Exception as e:
        return []
    finally:
        conn.close()