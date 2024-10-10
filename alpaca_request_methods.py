from datetime import datetime, timedelta, date
import pandas as pd
import os
import alpaca_trade_api as tradeapi
from alpaca_trade_api import Stream
from dotenv import load_dotenv
from database import transactions_DAOIMPL, user_DAOIMPL
import app
import sector_finder
import logging
import time
from Models import transaction
from flask import session
import order_methods
import asyncio
import websocket
import json


alpaca_api_datastream = "wss://paper-api.alpaca.markets/stream"

load_dotenv()




# Function to return api connection object
def get_alpaca_connection():
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    BASE_URL = os.getenv('BASE_URL')

    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
    return api




def get_alpaca_stream_connection(username):
    
    this_user = user_DAOIMPL.get_user_by_username(username)[0]
    alpaca_key = this_user['alpaca_key']
    alpaca_secret_key = this_user['alpaca_secret']
    alpaca_base_url = "https://paper-api.alpaca.markets"  # Base URL for paper trading

    # Remove 'data_stream' argument
    conn = Stream(alpaca_key, alpaca_secret_key, base_url=alpaca_base_url)
    return conn

    
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
        logging.info(trans)
        percent = int((i / total_iterations) * 100)
      
        
        end_date = trans[3]
        symbol = trans[0]
        purchase_date = trans[1]
        purchase_price = trans[2]
        sell_date = trans[3]
        sell_price = trans[4]
        actual_return = trans[5]
        logging.info(type(end_date))
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
        
def connect_to_user_alpaca_account(user_name):
    this_user = user_DAOIMPL.get_user_by_username(user_name)[0]
    try:
        user_alpaca_account_key = this_user['alpaca_key']
        user_alpaca_secret_key = this_user['alpaca_secret']
        # api = tradeapi.REST(user_alpaca_account_key, user_alpaca_secret_key, 'paper-api.alpaca.markets', api_version='v2')
        conn = tradeapi.stream.Stream(user_alpaca_account_key, user_alpaca_secret_key, base_url='paper-api.alpaca.markets')
        return conn
    except Exception as e:
        logging.error(f'Unable to connect to user alpaca account due to : {e}')

def create_alpaca_api(username):
    this_user = user_DAOIMPL.get_user_by_username(username)[0]
    try:
        user_alpaca_account_key = this_user['alpaca_key']
        user_alpaca_secret_key = this_user['alpaca_secret']
        api = tradeapi.REST(user_alpaca_account_key, user_alpaca_secret_key, 'https://paper-api.alpaca.markets', api_version='v2')
        return api
    except Exception as e:
        logging.error(f'Unable to connect to user alpaca account due to : {e}')
        
# Function to handle trade updates
def handle_trade_updates(ws, event, data ):
    if data['order']['status'] == 'filled':  # Use dot notation for 'event'
        logging.info(f'''Trade update received: Symbol:{data['order']['symbol']} Quantity: {data['order']['qty']} Price:{data['order']['filled_avg_price']}
                     Side:{data['order']['side']} Client order ID: {data['order']['client_order_id']}''')

    # Access attributes using dot notation instead of dictionary-style indexing
        
        symbol = data['order']['symbol']
        filled_qty = int(data['order']['qty'])
        filled_avg_price = float(data['order']['filled_avg_price'])
        side = data['order']['side']  # 'buy' or 'sell'
        client_order_id = data['order']['client_order_id']
        logging.info(client_order_id)
        user_id = client_order_id.split('/')[1]
        username = session.get('user_name')
        if side == 'buy':
            logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
            total_buy = float(filled_avg_price) * int(filled_qty)
            tp1 = (float(filled_avg_price) * .03)  + float(filled_avg_price)
            sop = float(filled_avg_price) - (float(filled_avg_price) * .01) 
            expected = total_buy * .03
            new_trans = transaction.transaction(symbol, date.today(), filled_avg_price, filled_qty, total_buy, client_order_id, user_id, expected=expected,tp1 = tp1, sop=sop)
            # insert into the transactions table
            transactions_DAOIMPL.insert_transaction(new_trans)
            logging.info("Reconnecting WebSocket for new transactions...")
            # Stop and reinitialize the connection
            stop_websocket(ws)  # This should stop the current connection
            run_alpaca_websocket(username)  # Re-initialize the websocket with updated transactions
        elif side == 'sell':
            logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
            transaction2 = transactions_DAOIMPL.get_transaction_by_bstring(client_order_id)
            if transaction2:
                ds = date.today()
                spps = filled_avg_price
                tsp = float(filled_avg_price) * int(filled_qty)
                total_purchase = float(transaction2[5])
                actual = tsp - total_purchase
                proi = actual / total_purchase
                result = 1 
                if actual > 0:
                    result = 0
                sstring = f"{client_order_id}~sell({datetime.now()})"
                transaction_id = int(transaction2[0])
                values = [ds,spps,tsp,sstring,proi,actual,result]
                transactions_DAOIMPL.update_transaction(transaction_id,values)
    else:
        logging.warning(f"Unhandled event: {event}")


def quote_management(data, username):
    transactions = transactions_DAOIMPL.get_open_transactions_for_user(7)
    transactions_dict = {}
    for transaction in transactions:
        transactions_dict[transaction[1]] = {
            'id': transaction[0],
            'symbol': transaction[1],
            'client_order_id': f'{transaction[6]}~sell',
            'take_profit': float(transaction[14]),
            'stop_price': float(transaction[15]),
            'quantity': int(transaction[4])
        }
    transaction = transactions_dict.get(data.symbol, None)
    if transaction:
        # Check for take profit or stop out
        if data.askprice >= transaction['take_profit']:
            logging.info(f"Take Profit hit for {data.symbol} at {data.askprice}.")
            order_methods.place_sell_order(transaction['symbol'], int(transaction['quantity']), float(data.askprice), int(transaction['id']), username)
        elif data.bidprice <= transaction['stop_price']:
            logging.info(f"Stop Out hit for {data.symbol} at {data.bidprice}.")
            order_methods.place_sell_order(transaction['symbol'], int(transaction['quantity']), float(data.bidprice), int(transaction['id']), username)



def run_alpaca_websocket(username):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('wss://paper-api.alpaca.markets/stream',
                                on_open=lambda ws: on_open(ws, username),
                                on_message=lambda ws, message: on_message(ws, message, username),
                                on_error=on_error,
                                on_close=on_close)
    logging.info(f'Websocket is running for user {username}')
    ws.run_forever()

def on_message(ws,message, username):
    data = json.loads(message)
    logging.info(data['data'])
    if data['stream'] == "trade_updates":
        event = data['data']['event']
        # Pass the action and price to your trade update handler
        handle_trade_updates(ws, data['data'], event )
    elif data['stream']== 'authorization':
        if data['data']['status']== 'authorized':
            logging.info('WebSocket authenticated successfully.')
            subscribe_to_data_streams(ws, username)
    else:
        print(data['data'])
    


def stop_websocket(ws):
    if ws:
        print("Closing WebSocket connection.")
        ws.close()
        
def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws, username):
    # Authenticate
    user = user_DAOIMPL.get_user_by_username(username)
    if user:
        user = user[0]
        alpaca_key = os.getenv('ALPACA_API_KEY')
        alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    auth_data = {
        "action": "auth",
        "key": alpaca_key,
        "secret": alpaca_secret
    }
    ws.send(json.dumps(auth_data))

    # Subscribe to data streams
def subscribe_to_data_streams(ws,username):
    user = user_DAOIMPL.get_user_by_username(username)
    if user:
        user = user[0]
    transactions = transactions_DAOIMPL.get_open_transactions_for_user(user['id'])
    transactions_dict = {}
    for transaction in transactions:
        transactions_dict[transaction[1]] = {
            'id': transaction[0],
            'symbol': transaction[1],
            'client_order_id': f'{transaction[6]}~sell',
            'take_profit': float(transaction[14]),
            'stop_price': float(transaction[15]),
            'quantity': int(transaction[4])
        }
        
    symbols = list(transactions_dict.keys())
    print(symbols)
    subscribe_data = {
                    "action": "listen",
                    "data": {
                        "streams": ["trade_updates"]
                    }
                    }
    
    ws.send(json.dumps(subscribe_data))
    