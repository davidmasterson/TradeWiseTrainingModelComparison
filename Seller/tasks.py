import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from database import transactions_DAOIMPL, database_connection_utility, pending_orders_DAOIMPL, user_DAOIMPL
import alpaca_request_methods
import order_methods
import time

'''Script for running websocket for all users in the background'''
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_positions_for_user(username, user_id):
    connection = alpaca_request_methods.create_alpaca_api(username)
    db_conn = database_connection_utility.get_db_connection()
    logging.info(f'{datetime.now()}: Started sell loop for user {username}')
    
    try:
        while True:
            # Get current time in UTC and convert to EST
            now_utc = datetime.utcnow()
            now_est = now_utc - timedelta(hours=5)  # Adjusting for EST
            
            # Set the EST start and end times for trading
            market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now_est.replace(hour=15, minute=30, second=0, microsecond=0)
            
            # Check if today is a weekday and if the current time is within trading hours
            if now_est.weekday() >= 5 or now_est < market_open or now_est >= market_close:
                print(f"Market closed or outside trading hours for user {username}. Exiting monitoring.")
                logging.info(f"Market closed or outside trading hours for user {username}. Exiting monitoring.")
                break

            # Retrieve and process positions
            poss = connection.list_positions()
            if poss:
                for pos in poss:
                    transact = transactions_DAOIMPL.get_open_transactions_for_user_by_symbol_with_db_conn(pos.symbol, user_id, db_conn)
                    if transact:
                        for trans in transact:
                            tp1 = float(trans[14])
                            sop = float(trans[15])
                            qty = int(trans[4])
                            buy_string = trans[6]
                            logging.info(f'Position: {pos.symbol}, Price: {pos.current_price}, Take Profit: {tp1}, Stop Out: {sop}')
                            
                            if float(pos.current_price) >= tp1 or float(pos.current_price) <= sop:
                                order_methods.place_sell_order(pos.symbol, qty, round(float(pos.current_price), 2), username, buy_string, user_id)
                logging.info(f'{datetime.now()}: Finished running seller loop for {username}')
            else:
                logging.info(f"No open positions found for user {username}.")
            
            # Log the loop iteration time
            logging.info(f"Loop iteration for user {username} at: {datetime.now()}")
            
            # Wait for 60 seconds before checking positions again
            time.sleep(60)
    
    except Exception as e:
        logging.error(f"Exception encountered for user {username}: {e}")

    finally:   
        db_conn.close()
        logging.info(f"End of day: All open orders canceled and pending orders truncated for user {username}.")
        

def monitor_all_users():
    users = user_DAOIMPL.get_all_users()  # Retrieve all users from the database

    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers based on system resources
        # Submit a job for each user to the thread pool
        futures = {executor.submit(check_positions_for_user, user['user_name'], user['id']): user['user_name'] for user in users}
        
        # Wait for all tasks to complete
        for future in as_completed(futures, timeout=60):
            user_name = futures[future]
            try:
                future.result()  # Retrieve the result of the function
            except TimeoutError:
                print("Monitoring tasks timed out.")
            except Exception as e:
                print(f"Error occurred: {e}")

if __name__ == "__main__":
    monitor_all_users()
