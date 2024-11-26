import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
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
import pickle
import alpaca_request_methods
from HistoricalFetcherAndScraper import scraper


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/home/ubuntu/TradeWiseTrainingModelComparison/logs/websocket.log"),
        logging.StreamHandler()
    ]
)

logging.info("WebSocket service started.")





# Start a persistent event loop in a separate thread
def start_event_loop(loop):
    try:
        asyncio.set_event_loop(loop)
        loop.run_forever()
        logging.info('Started event loop successfully')
    except Exception as e:
        logging.error(f'Unable to start event loop')




def add_new_user(username, user_id, alpaca_key, alpaca_secret, alpaca_endpoint, max_retries=None, delay=None):
    try:
    # Schedule the synchronous WebSocket connection to run in a separate thread
        logging.info(f'Attempting to add a new user {username}')
        loop.run_in_executor(executor, start_user_websocket, username, user_id, alpaca_key, alpaca_secret, alpaca_endpoint)
        websocket_tasks[user_id] = executor
        logging.info(f'Added new user {username} to this websocket')
    except Exception as e:
        logging.error(f'Unable to add new user {username} due to {e}')






import time

async def monitor_new_users(interval=10):
    while True:
        try:
            users = user_DAOIMPL.get_all_users()
            logging.info(f"Fetched {len(users)} users from the database.")
            
            for user in users:
                try:
                    user_id = user.get("id")
                    username = user.get("user_name")
                    alpaca_key = user.get("alpaca_key")
                    alpaca_secret = user.get("alpaca_secret")
                    alpaca_endpoint = user.get("alpaca_endpoint")
                    
                    if user_id not in websocket_tasks:
                        logging.info(f"Adding new user {username} (ID: {user_id}) to WebSocket tasks.")
                        try:
                            add_new_user(username, user_id, alpaca_key, alpaca_secret, alpaca_endpoint)
                            logging.info(f"Successfully added user {username} (ID: {user_id}) to WebSocket tasks.")
                        except Exception as e:
                            logging.error(f"Failed to add user {username} (ID: {user_id}) to WebSocket: {e}")
                except Exception as e:
                    logging.error(f"Error processing user data: {e}")
        
            logging.info(f"Sleeping for {interval} seconds before checking for new users.")
            await asyncio.sleep(interval)
        
        except Exception as e:
            logging.error(f"Critical error in monitor_new_users loop: {e}. Continuing to monitor.")





# Asynchronous message handler
async def on_message_async(ws, message, username, user_id):
    try:
        try:
            data_string = message.decode('utf-8')
        except UnicodeDecodeError as e:
            logging.error(f"Message decoding failed for user {username}: {e}")
            return

        try:
            data = json.loads(data_string)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding failed for user {username}: {e}")
            return

        logging.info(f'WebSocket received new message for {username}. Message: {message}')

        stream = data.get('stream')
        if stream == 'authorization':
            status = data.get('data', {}).get('status')
            if status == 'authorized':
                logging.info(f'Authorization for Alpaca WebSocket was successful for user {username}')
                try:
                    subscribe_to_data_streams(ws, username)
                    logging.info(f'User: {username} successfully subscribed to trade updates data stream.')
                except Exception as e:
                    logging.error(f"Error subscribing user {username} to data streams: {e}")
        elif stream == 'trade_updates':
            logging.info(f'User {username} received a trade_updates message. Processing...')
            try:
                event = data.get('data', {}).get('event')
                trade_data = data.get('data', {})
                if event:
                    testing = await handle_trade_updates(ws, event, trade_data, username, user_id)
                    logging.info(f"Trade updates handled successfully for user {username}. Result: {testing}")
                else:
                    logging.warning(f"Trade update event missing for user {username}. Data: {trade_data}")
            except Exception as e:
                logging.error(f"Error handling trade updates for user {username}: {e}")
    except Exception as e:
        logging.error(f'Error in on_message_async for user {username}: {e}')



def on_message(ws, message, username, user_id):
    asyncio.run(on_message_async(ws, message, username, user_id))


def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")
    if hasattr(ws, 'user_id') and hasattr(ws, 'username'):
        logging.info(f"Attempting to reconnect for user {ws.username} (ID: {ws.user_id})")
        reconnect_user(ws.user_id)

def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket closed with status: {close_status_code}, message: {close_msg}")
    if hasattr(ws, 'user_id') and hasattr(ws, 'username'):
        logging.info(f"Attempting to reconnect for user {ws.username} (ID: {ws.user_id})")
        reconnect_user(ws.user_id)


def on_open(ws, username, alpaca_key, alpaca_secret):
    logging.info(f"WebSocket opened for user: {username}")
    try:
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
    except Exception as e:
        logging.error(f'Unable to open websocke for {username}')

    # After authentication, subscribe to trade_updates
    subscribe_data = {
        "action": "listen",
        "data": {
            "streams": ["trade_updates"]
        }
    }
    try:
        ws.send(json.dumps(subscribe_data))
        logging.info(f"Subscribed to trade_updates for user {username}")
    except Exception as e:
        logging.error(f' Unable to subscribe to trade_updates for user {username}')


# Subscribe to trade updates stream
def subscribe_to_data_streams(ws, username):
    subscribe_data = {
        "action": "listen",
        "data": {
            "streams": ["trade_updates"]
        }
    }
    try:
        ws.send(json.dumps(subscribe_data))
    except Exception as e:
        logging.error(f'Issue with subscribe to data stream function for {username} due to {e}')


def start_user_websocket(username, user_id, alpaca_key, alpaca_secret, alpaca_endpoint, max_retries=5, delay=5):
    retry_count = 0
    while retry_count < max_retries:
        try:
            websocket.enableTrace(True)
            stream_endpoint = (
                'wss://api.alpaca.markets/stream' if alpaca_endpoint == 'https://api.alpaca.markets'
                else 'wss://paper-api.alpaca.markets/stream'
            )

            ws = websocket.WebSocketApp(
                stream_endpoint,
                on_open=lambda ws: on_open(ws, username, alpaca_key, alpaca_secret),
                on_message=lambda ws, message: on_message(ws, message, username, user_id),
                on_error=on_error,
                on_close=on_close
            )

            # Attach user details to the WebSocket instance
            ws.username = username
            ws.user_id = user_id

            logging.info(f"Starting WebSocket for user {username}")
            ws.run_forever(ping_interval=30, ping_timeout=10)
            logging.warning(f"WebSocket for user {username} disconnected. Retrying...")
        except Exception as e:
            logging.error(f"Error with WebSocket for user {username}: {e}")

        retry_count += 1
        if retry_count < max_retries:
            logging.info(f"Retrying WebSocket for user {username} in {delay} seconds (Attempt {retry_count}/{max_retries})")
            time.sleep(delay)
        else:
            logging.error(f"Max retries reached for user {username}. WebSocket will not reconnect.")
            break
    
async def handle_trade_updates(ws, event, data, username, user_id):
        logging.error('Inside the handle trade updates method')
        try:
            logging.info(f"Starting handle_trade_updates for user {username}, event: {event}")
            if data['event'] == 'fill':  # Ensure the event is 'fill'
                logging.info(f"Processing fill event for symbol: {data['order']['symbol']}, user: {username}")
                logging.info(f'''Trade update received: Symbol: {data['order']['symbol']} Quantity: {data['order']['filled_qty']} Price: {data['order']['filled_avg_price']}
                            Side: {data['order']['side']} Client order ID: {data['order']['client_order_id']}''')

                symbol = data['order']['symbol']
                filled_qty = int(data['order']['filled_qty'])
                filled_avg_price = float(data['order']['filled_avg_price'])
                side = data['order']['side']
                client_order_id = data['order']['id']
                logging.info(f"Extracted details - Symbol: {symbol}, Quantity: {filled_qty}, Price: {filled_avg_price}, Side: {side}, Order ID: {client_order_id}")
                logging.info(f'Logging client order id for user{username} due to new fill')
                
                if side == 'buy':
                    logging.info(f' User: {username} had a new buy total fill')
                    # Handle buy side
                    try:
                        logging.info(f"Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}. For USER: {user_id}")
                        total_buy = float(filled_avg_price) * int(filled_qty)
                        tp1 = (float(filled_avg_price) * .03) + float(filled_avg_price)
                        sop = float(filled_avg_price) - (float(filled_avg_price) * .01)
                        expected = total_buy * .03
                        logging.info(f' Initial variables created for user {username}\'s new filled order')
                        
                        logging.info(f'Attempting to create new transaction object.')
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
                        logging.info(f'New transaction object has been created for {username} due to new transaction purchase fill')
                        # Insert the transaction
                        
                        # pending_orders_DAOIMPL.insert_pending_order(client_order_id,user_id,side)
                        logging.info(f'Fetching pending order for {symbol} for user {username} ')
                        try:
                            pending = pending_orders_DAOIMPL.get_pending_buy_orders_by_user_id_and_client_order_id(user_id, client_order_id)
                            if pending:
                                logging.info(f'Pending order found')
                            else:
                                logging.warning(f' Pending order was not found for {symbol} {filled_qty} for user {username}')
                        except Exception as e:
                            logging.error(f"Error fetching pending orders: {e}")
                        try:
                            logging.info(f'Attempting to add new transaction to database for user {username}')
                            transactions_DAOIMPL.insert_transaction(new_trans, pending)
                            logging.info(f'Transaction has been successfully added to database for user {username}')
                        except Exception as e:
                            logging.error(f'Error inserting transaction due to {e}')
                        logging.info(f"{datetime.now()}: Deleting pending transaction")
                    except Exception as e:
                        logging.error(f"{datetime.now()}: Unable to insert transaction or delete pending transaction {client_order_id} due to {e}")
                elif side == 'sell':
                    # Handle sell side
                    logging.info(f" Filled sell order has been filled for user {username} Order {client_order_id} filled for {filled_qty} shares of {symbol} at {filled_avg_price}.")
                    logging.info(f'Attempting to get pending order for {symbol} {filled_qty} for user {username}')
                    pending_order = pending_orders_DAOIMPL.get_pending_sell_orders_by_user_id_and_client_order_id(user_id,client_order_id)
                    if pending_order:
                        logging.info(f' Pending order found for {symbol} {filled_qty} for user {username}')
                        purchase_string = pending_order[4]
                        logging.info(f'Purchase string is {purchase_string}')
                        pending_order_id = int(pending_order[0])
                        logging.info(f'Pending order id is {pending_order_id}')
                    logging.info(f' Getting open transactions for {purchase_string} for user {username}')    
                    transaction2 = transactions_DAOIMPL.get_open_transaction_by_pstring_for_user(purchase_string, user_id)
                    if transaction2:
                        logging.info(f'Open transaction has been found for {purchase_string} for user {username}')
                        ds = date.today().strftime("%Y-%m-%d")
                        logging.info({ds})
                        spps = filled_avg_price
                        logging.info({filled_avg_price})
                        tsp = filled_avg_price * filled_qty
                        logging.info({tsp})
                        total_purchase = float(transaction2[5])
                        logging.info({total_purchase})
                        actual = tsp - total_purchase
                        logging.info({actual})
                        proi = round(actual / total_purchase, 2)
                        logging.info({proi})
                        result = 'loss' if actual <= 0 else 'profit'
                        logging.info({result})
                        sstring = f"{client_order_id}~sell({datetime.now()})"
                        logging.info({sstring})
                        transaction_id = int(transaction2[0])
                        logging.info({transaction_id})
                        pol_neu_close, pol_pos_close, pol_neg_close = MachineLearningModels.manual_alg_requisition_script.process_daily_political_sentiment()
                        logging.info(f'Political scores{pol_neu_close, pol_pos_close, pol_neg_close}')
                        logging.info(f'Fetching SA articles for user {username} Transaction {transaction_id}')
                        logging.info(f'SA articles found for user {username} Transaction {transaction_id}')
                        non_string_date = datetime.strptime(ds, "%Y-%m-%d")
                        sa_neu_close, sa_pos_close, sa_neg_close = scraper.get_sa(non_string_date,symbol,user_id)
                        logging.info(f'SA scores {sa_neu_close, sa_pos_close, sa_neg_close} for {username} Transaction {transaction_id}')
                        
                        values = [ds, spps, tsp, sstring, proi, actual, result,pol_neu_close,pol_pos_close,pol_neg_close,sa_neu_close,sa_pos_close,sa_neg_close ]
                        logging.info(f' Updating transaction Symbol:{symbol} Transaction ID:{transaction_id}')
                        transactions_DAOIMPL.update_transaction(transaction_id, values)
                        logging.info(f'Successfully updated transaction. Now deleting pending order {pending_order_id}')
                        pending_orders_DAOIMPL.delete_pending_order_after_fill(pending_order[0], pending_order[3], pending_order[2])
                        logging.info(f'Pending order id {pending_order_id} successfully deleted')
            else:
                logging.warning(f"Unhandled event: {event}")
        except Exception as e:
            logging.error(f'Unable to handle trade updates due to {e}')

def reconnect_user(user_id, max_retries=5, delay=5):
    retries = 0
    while retries < max_retries:
        try:
            if user_id in websocket_tasks:
                logging.info(f"Attempting to reconnect WebSocket for user ID: {user_id} (Retry {retries + 1}/{max_retries})")
                user = user_DAOIMPL.get_user_by_user_id(user_id)
                if user:
                    add_new_user(
                    username=user[4],
                    user_id=user[0],
                    alpaca_key=user[6],
                    alpaca_secret=user[7],
                    alpaca_endpoint=user[8],
                    max_retries=3,
                    delay=10
                )
                    logging.info(f"Successfully reconnected WebSocket for user ID: {user_id}")
                    return
                else:
                    logging.warning(f"User with ID {user_id} not found in database for reconnection.")
            else:
                logging.warning(f"No WebSocket task found for user ID: {user_id}")
            break
        except Exception as e:
            logging.error(f"Error reconnecting WebSocket for user ID: {user_id} on attempt {retries + 1}: {e}")
        retries += 1
        time.sleep(delay)

    if retries == max_retries:
        logging.error(f"Failed to reconnect WebSocket for user ID: {user_id} after {max_retries} attempts.")
           
            
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
    