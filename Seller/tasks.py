import sys
import os
import time
import threading
from datetime import date, datetime
from database import transactions_DAOIMPL, database_connection_utility, pending_orders_DAOIMPL
import alpaca_request_methods
from flask import session
import order_methods

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_positions_in_background(username, user_id):
    today = date.today()
    conn = alpaca_request_methods.create_alpaca_api(username)
    
    # Make sure to open the DB connection only once
    db_conn = database_connection_utility.get_db_connection()
    
    while datetime.now() <= datetime(today.year, today.month, today.day, 15, 30, 0):
        positions = conn.list_positions()
        for position in positions:
            transactions = transactions_DAOIMPL.get_open_transactions_for_user_by_symbol_with_db_conn(position.symbol, user_id, db_conn)
            position_price_now = float(position.current_price)
            for transaction in transactions:
                transaction_sell_price = float(transaction[14])
                transaction_stop_price = float(transaction[15])
                trans_qty = int(transaction[4])
                trans_purchase_string = transaction[6]
                
                if position_price_now >= transaction_sell_price or position_price_now <= transaction_stop_price:
                    order_methods.place_sell_order(position.symbol, trans_qty, position_price_now, transaction[0], username, trans_purchase_string)
        
        # Wait for 60 seconds before checking positions again
        time.sleep(60)
    
    # Cancel any open orders at the end of the trading day
    conn.cancel_all_orders()

    # Close the database connection at the end
    db_conn.close()