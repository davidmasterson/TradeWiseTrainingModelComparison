import sys
import os
import time
import threading
from datetime import date, datetime
from database import transactions_DAOIMPL, database_connection_utility, pending_orders_DAOIMPL, user_DAOIMPL
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
        poss = conn.list_poss()
        if poss:
            for pos in poss:
                transactions = transactions_DAOIMPL.get_open_transactions_for_user_by_symbol_with_db_conn(pos.symbol, user_id, db_conn)
                pos_price_now = float(pos.current_price)
                for trans in transactions:
                    tp1 = float(trans[14])
                    sop = float(trans[15])
                    qty = int(trans[4])
                    buy_string = trans[6]
                    user_id = int(trans[18])
                    print(f'Position: {pos.symbol}, Price: {pos.current_price}, Take Profit: {tp1}, Stop Out: {sop}')
                    if pos_price_now >= tp1 or pos_price_now <= sop:
                        order_methods.place_sell_order(pos.symbol, qty, pos_price_now, username, buy_string)
            
            # Wait for 60 seconds before checking positions again
            time.sleep(60)
        
        # Cancel any open orders at the end of the trading day
    conn.cancel_all_orders()

    # Close the database connection at the end
    db_conn.close()