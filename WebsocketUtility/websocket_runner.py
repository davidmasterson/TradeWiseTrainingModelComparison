import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import threading
from alpaca_trade_api.stream import Stream
from database import user_DAOIMPL , pending_orders_DAOIMPL, transactions_DAOIMPL
import logging
import sector_finder
from Models import transaction
import MachineLearningModels
from datetime import datetime, date
import json
import websocket
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')





# Start a persistent event loop in a separate thread
def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()




def add_new_user(username, user_id, alpaca_key, alpaca_secret, alpaca_endpoint):
    # Schedule the synchronous WebSocket connection to run in a separate thread
    loop.run_in_executor(executor, start_user_websocket, username, user_id, alpaca_key, alpaca_secret, alpaca_endpoint)
    websocket_tasks[user_id] = executor






import time

async def monitor_new_users(interval=10):
    while True:
        users = user_DAOIMPL.get_all_users()
        for user in users:
            # {'id': user['id'], 'alpaca_key': user['alpaca_key'], 'alpaca_secret': user['alpaca_secret'], 
            #                    'alpaca_endpoint': user['alpaca_endpoint'], 'user_name': user['user_name']}
            
            if user['id'] not in websocket_tasks:
                add_new_user(user['id'], user['alpaca_key'], user['alpaca_secret'], user['alpaca_endpoint'], user['user_name'])
        await asyncio.sleep(interval)  # Wait for the specified interval before checking again




# Asynchronous message handler
async def on_message_async(ws, message, username, user_id):
    data = json.loads(message)
    if data['stream'] == 'authorization':
        if data['data']['status'] == 'authorized':
            subscribe_to_data_streams(ws, username)
    elif data['stream'] == 'trade_updates':
        handle_trade_updates(ws, data['data']['event'], data['data'], username, user_id)


def on_message(ws, message, username, user_id):
    asyncio.run(on_message_async(ws, message, username, user_id))


def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket closed with status: {close_status_code}, message: {close_msg}")


def on_open(ws, username, alpaca_key, alpaca_secret):
    logging.info(f"WebSocket opened for user: {username}")
    
    # Send authentication data
    auth_data = {
        "action": "authenticate",
        "data": {
            "key_id": alpaca_key,
            "secret_key": alpaca_secret
        }
    }
    ws.send(json.dumps(auth_data))
    logging.info(f"Authentication sent for user {username}")

    # After authentication, subscribe to trade_updates
    subscribe_data = {
        "action": "listen",
        "data": {
            "streams": ["trade_updates"]
        }
    }
    ws.send(json.dumps(subscribe_data))
    logging.info(f"Subscribed to trade_updates for user {username}")


# Subscribe to trade updates stream
def subscribe_to_data_streams(ws, username):
    subscribe_data = {
        "action": "listen",
        "data": {
            "streams": ["trade_updates"]
        }
    }
    ws.send(json.dumps(subscribe_data))


def start_user_websocket(username,user_id, alpaca_key, alpaca_secret, alpaca_endpoint):
    websocket.enableTrace(True)
    if alpaca_endpoint == 'https://api.alpaca.markets':
        stream_endpoint = 'wss://api.alpaca.markets/stream'
    else:
        stream_endpoint = 'wss://paper-api.alpaca.markets/stream'
    # Initialize WebSocketApp and pass the API key and secret to on_open
    ws = websocket.WebSocketApp(
        stream_endpoint,
        on_open=lambda ws: on_open(ws, username, alpaca_key, alpaca_secret),
        on_message=lambda ws, message: on_message(ws, message, username, user_id),
        on_error=on_error,
        on_close=on_close
    )
    
    logging.info(f'WebSocket is running for user {username}')
    ws.run_forever()
    
    
async def handle_trade_updates(ws, event, data, username, user_id):
        if data['event'] == 'fill':  # Ensure the event is 'fill'
            logging.info(f'''Trade update received: Symbol: {data['order']['symbol']} Quantity: {data['order']['qty']} Price: {data['order']['filled_avg_price']}
                        Side: {data['order']['side']} Client order ID: {data['order']['client_order_id']}''')

            symbol = data['order']['symbol']
            filled_qty = int(data['order']['qty'])
            filled_avg_price = float(data['order']['filled_avg_price'])
            side = data['order']['side']
            client_order_id = data['order']['id']
            logging.info(client_order_id)
            
            if side == 'buy':
                # Handle buy side
                try:
                    logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
                    total_buy = float(filled_avg_price) * int(filled_qty)
                    tp1 = (float(filled_avg_price) * .03) + float(filled_avg_price)
                    sop = float(filled_avg_price) - (float(filled_avg_price) * .01)
                    expected = total_buy * .03
                    
                    
                    new_trans = transaction.transaction(
                        symbol=symbol,
                        dp=date.today(),
                        ppps=filled_avg_price,
                        qty=filled_qty,
                        total_buy=total_buy,
                        pstring=client_order_id,
                        user_id=user_id,
                        expected=expected,
                        tp1=tp1,
                        sop=sop
                    )
                    # Insert the transaction
                    
                    # pending_orders_DAOIMPL.insert_pending_order(client_order_id,user_id,side)
                    pending = pending_orders_DAOIMPL.get_pending_buy_orders_by_user_id_and_client_order_id(user_id, client_order_id)
                    if pending:
                        pending = pending[0]
                    transactions_DAOIMPL.insert_transaction(new_trans, pending)
                    logging.info(f"{datetime.now()}: Deleting pending transaction")
                except Exception as e:
                    logging.error(f"{datetime.now()}: Unable to insert transaction or delete pending transaction {client_order_id} due to {e}")
            elif side == 'sell':
                # Handle sell side
                logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
                pending_order = pending_orders_DAOIMPL.get_pending_sell_orders_by_user_id_and_client_order_id(user_id,client_order_id)
                if pending_order:
                    purchase_string = pending_order[4]
                    pending_order_id = int(pending_order[0])
                transaction2 = transactions_DAOIMPL.get_open_transaction_by_pstring_for_user(purchase_string, user_id)
                if transaction2:
                    ds = date.today()
                    spps = filled_avg_price
                    tsp = filled_avg_price * filled_qty
                    total_purchase = float(transaction2[5])
                    actual = tsp - total_purchase
                    proi = round(actual / total_purchase, 2)
                    result = 'loss' if actual <= 0 else 'profit'
                    sstring = f"{client_order_id}~sell({datetime.now()})"
                    transaction_id = int(transaction2[0])
                    pol_neu_close, pol_pos_close, pol_neg_close = MachineLearningModels.manual_alg_requisition_script.process_daily_political_sentiment()
                    
                    info = MachineLearningModels.manual_alg_requisition_script.request_articles(symbol)
                    sa_neu_close, sa_pos_close, sa_neg_close = MachineLearningModels.manual_alg_requisition_script.process_phrase_for_sentiment(info)
                    
                    values = [ds, spps, tsp, sstring, proi, actual, result,pol_neu_close,pol_pos_close,pol_neg_close,sa_neu_close,sa_pos_close,sa_neg_close ]
                    transactions_DAOIMPL.update_transaction(transaction_id, values)
                    pending_orders_DAOIMPL.delete_pending_order_after_fill(pending_order_id)
        else:
            logging.warning(f"Unhandled event: {event}")
            
            
if __name__ == "__main__":
    websocket_tasks = {}
    executor = ThreadPoolExecutor()
    # Initialize a new event loop for WebSocket management
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_event_loop, args=(loop,))
    t.start()
    # Initialize existing users' WebSocket connections
    existing_users = []
    users = user_DAOIMPL.get_all_users()
    if users:
        for user in users:
            existing_users.append({
                'user_name': user['user_name'], 
                'id': user['id'], 
                'alpaca_key': user['alpaca_key'], 
                'alpaca_secret': user['alpaca_secret'], 
                'alpaca_endpoint': user['alpaca_endpoint']
            })
    
    # Add WebSocket connections for each existing user
    for user in existing_users:
        add_new_user(user['user_name'], user['id'], user['alpaca_key'], user['alpaca_secret'], user['alpaca_endpoint'])

    # Start monitoring for new users in the background
    loop.create_task(monitor_new_users())
    