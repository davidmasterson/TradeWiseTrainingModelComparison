import sys
import os
import time
import threading
from datetime import date, datetime
from database import transactions_DAOIMPL, database_connection_utility, pending_orders_DAOIMPL, user_DAOIMPL
import alpaca_request_methods
from flask import session
import order_methods
from pytz import timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def check_positions_in_background(username, user_id):
    today = date.today()
    conn = alpaca_request_methods.create_alpaca_api(username)
    est = timezone('America/New_York')  # Define EST timezone
    
    # Make sure to open the DB connection only once
    db_conn = database_connection_utility.get_db_connection()
    
    try:
        while True:
            # Check if current time in EST is past 3:30 PM
            current_time_est = datetime.now(est)
            if current_time_est >= current_time_est.replace(hour=15, minute=30, second=0, microsecond=0):
                print("Market close reached. Exiting position monitoring.")
                break
            
            # Retrieve and process positions
            poss = conn.list_poss()
            if poss:
                for pos in poss:
                    transact = transactions_DAOIMPL.get_open_transactions_for_user_by_symbol_with_db_conn(pos.symbol, user_id, db_conn)
                    if transact:
                        for trans in transact:
                            tp1 = float(trans[14])
                            sop = float(trans[15])
                            qty = int(trans[4])
                            buy_string = trans[6]
                            print(f'Position: {pos.symbol}, Price: {pos.current_price}, Take Profit: {tp1}, Stop Out: {sop}')
                            
                            if float(pos.current_price) >= tp1 or float(pos.current_price) <= sop:
                                order_methods.place_sell_order(pos.symbol, qty, round(float(pos.current_price), 2), username, buy_string, user_id)
            else:
                print("No open positions found.")
            
            # Log the loop iteration time
            print(f"Loop iteration at: {current_time_est}")
            
            # Wait for 60 seconds before checking positions again
            time.sleep(60)

    finally:
        # After exiting the loop, cancel any open orders and truncate pending orders table
        conn.cancel_all_orders()
        pending_orders_DAOIMPL.truncate_pending_orders_at_eod(db_conn)
        db_conn.close()
        print("End of day: All open orders canceled and pending orders truncated.")
