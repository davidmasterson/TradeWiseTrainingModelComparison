import alpaca_request_methods
from database import user_DAOIMPL
import logging
from datetime import datetime
from flask import session
def submit_limit_order(username, order):
    try:
        conn = alpaca_request_methods.create_alpaca_api(username)
        this_user = user_DAOIMPL.get_user_by_username(username)[0]
        order = conn.submit_order(
            symbol=order['symbol'],  # Example stock symbol
            qty=order['qty'],  # Quantity of shares to buy
            side=order['side'],  # "buy" or "sell"
            type=order['type'],
            limit_price=order['limit_price'],# Order type: "market" or "limit"
            time_in_force=order['tif'],  # Good 'til canceled
            client_order_id=f"{datetime.now()}{order['symbol']}{order['qty']} {order['limit_price']}/{this_user['id']}"
        )
        logging.info(f"Order submitted: {order}")
    except Exception as e:
        logging.info(f"Error placing order: {e}")
 
def place_sell_order(symbol, qty, price, transaction_id, username):
    """
    Place a sell order on Alpaca with a unique client_order_id based on transaction_id.
    """
    
    try:
        api = alpaca_request_methods.create_alpaca_api(username)
        limit_price = alpaca_request_methods.get_symbol_current_price(symbol)
        sell_order = api.submit_order(
            symbol=symbol,
            qty=qty,  # Quantity to sell
            side='sell',
            type='limit',
            limit_price= price,
            time_in_force='day',  # day
            client_order_id=f"sell-{symbol}-{qty}-{limit_price}-{datetime.now().strftime('%Y-%M-%d %H:%m:%S')}/{username} "  # Unique identifier for the order
        )
        print(f"Sell order placed for {symbol}. Transaction ID: {transaction_id}")
        return sell_order
    except Exception as e:
        print(f"Error placing sell order for {symbol}: {e}")
        return None
    
