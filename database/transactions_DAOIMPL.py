import pymysql
from datetime import date, datetime
from database import database_connection_utility as dcu
import logging


import csv

def get_qty_for_transaction(pstring,user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT qty FROM transactions
                WHERE pstring = %s and user_id=%s'''
    vals = [pstring, user_id]
    try:
        cur.execute(sql, vals)
        trans = cur.fetchone()
        if trans:
            return trans[0]
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_transactions_from_db():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM transactions'''
    
    try:
        cur.execute(sql)
        trans = cur.fetchall()
        
        if trans:
            # Fetch column names from the cursor
            column_names = [i[0] for i in cur.description]
            
            # Write data to CSV
            with open('Model_Training/transactions.csv', 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write the header (column names)
                csvwriter.writerow(column_names)
                
                # Write the transaction data
                csvwriter.writerows(trans)
                
            logging.info("Transactions have been exported to 'transactions.csv'.")
        else:
            logging.info("No transactions found.")
        
    except Exception as e:
        logging.info(f"An error occurred: {e}")
        
    finally:
        cur.close()
        conn.close()


def read_in_transactions(file):
    global progress
    get_transactions_from_db()
    path = '/home/ubuntu/LSTMStockPricePredictor'
    filepath = path+file
    with open(filepath, 'r') as trans_reader:
        lines = trans_reader.readlines()
        return [trans_reader, lines]
    
def convert_lines_to_transaction_info_for_DF(reader, lines):
    trans_df_initial_data = []
    count = 0
    for line in lines:
        
        seperated_line = line.split(',')
        if count != 0:
            symbol = seperated_line[1]
            purchase_date_string = seperated_line[2].split('-')
            purchase_price = float(seperated_line[3])
            sell_date_string = seperated_line[7].split('-') if seperated_line[8] != 'N/A' else 'N/A'
            sell_price = float(seperated_line[8]) if seperated_line[8] != 'N/A' else 'N/A'
            actual = float(seperated_line[13]) if seperated_line[8] != 'N/A' else 'N/A'
            purchase_date = date(int(purchase_date_string[0]),int(purchase_date_string[1]), int(purchase_date_string[2]))
            sell_date = date(int(sell_date_string[0]), int(sell_date_string[1]), int(sell_date_string[2])) if sell_price != 'N/A' else 'N/A'
            days_to_sell = (sell_date - purchase_date).days if seperated_line[8] != 'N/A' else 'N/A'
            take_profit = float(purchase_price + (purchase_price * .03))
            stop_price = float(purchase_price - (purchase_price * .01))
            hit_take_profit = 1 if actual != 'N/A' and actual > 0.00 else 0
            trans_df_initial_data.append([symbol,purchase_date,purchase_price,sell_date,sell_price,actual,days_to_sell,
                                        take_profit,stop_price,hit_take_profit])
        count += 1
    reader.close()
    return trans_df_initial_data

def get_project_training_transactions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'''SELECT * FROM transactions WHERE user_id={user_id}'''
    
    try:
        cur.execute(sql)
        rows = cur.fetchall()  # Fetch all rows as tuples
        
        # Get the column names from the cursor description
        columns = [col[0] for col in cur.description]
        
        # Convert each row into a dictionary
        transactions = [dict(zip(columns, row)) for row in rows]
        
        return transactions if transactions else []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_project_training_most_recent_5_transactions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'''SELECT * FROM transactions WHERE user_id=%s ORDER BY id DESC LIMIT 5 '''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        rows = cur.fetchall()  # Fetch all rows as tuples
        
        # Get the column names from the cursor description
        columns = [col[0] for col in cur.description]
        
        # Convert each row into a dictionary
        transactions = [dict(zip(columns, row)) for row in rows]
        
        return transactions if transactions else []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()


def calculate_average_days_to_close_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'''SELECT AVG(DATEDIFF(STR_TO_DATE(ds, '%Y-%m-%d'), STR_TO_DATE(dp, '%Y-%m-%d'))) AS avg_days_to_close
                FROM transactions
                WHERE sstring !='N/A'
                AND prediction = 1
                AND prediction = result
                AND user_id = {user_id}'''
    try:
        cur.execute(sql)
        avg = cur.fetchone()
        if avg:
            return avg[0]
        return None
    except Exception as e:
        logging.info(e)
        return None
    finally:
        conn.close()
        cur.close()

def calculate_cumulative_profit_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT sum(actual) from transactions WHERE actual > 0 and result = 1 AND user_id = {user_id}'
    try:
        cur.execute(sql)
        profit = cur.fetchone()
        if profit:
            return profit[0]
        return 0.00
    except Exception as e:
        logging.info(e)
        return 0.00
    finally:
        conn.close()
        cur.close()

def calculate_cumulative_loss_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT sum(actual) from transactions WHERE actual < 0 AND result = 0 AND user_id={user_id}'
    try:
        cur.execute(sql)
        loss = cur.fetchone()
        if loss:
            return loss[0]
        return 0.00
    except Exception as e:
        logging.info(e)
        return 0.00
    finally:
        conn.close()
        cur.close()

def calculate_correct_predictions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'''SELECT COUNT(*) FROM transactions 
            WHERE actual > 0 AND user_id={user_id}'''
    try:
        cur.execute(sql)
        count = cur.fetchone()
        if count:
            return count[0]
        return 0
    except Exception as e:
        logging.info(e)
        return 0
    finally:
        conn.close()
        cur.close()

def calculate_incorrect_predictions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT COUNT(*) FROM transactions WHERE actual < 0 user_id={user_id}'
    try:
        cur.execute(sql)
        count = cur.fetchone()
        if count:
            return count[0]
        return 0
    except Exception as e:
        logging.info(e)
        return 0
    finally:
        conn.close()
        cur.close()
# Get open transactions
def get_open_transactions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM transactions
                WHERE ds=%s
                AND user_id = %s
                '''
    vals = ['N/A', user_id]
    try:
        cur.execute(sql, vals)
        trans = cur.fetchall()
        if trans:
            return trans
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_all_pstrings_for_open_transactions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT pstring FROM transactions
                WHERE ds=%s
                AND user_id = %s
                '''
    vals = [None, user_id]
    try:
        cur.execute(sql, vals)
        trans = cur.fetchall()
        if trans:
            return trans
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_open_transaction_by_pstring_for_user(pstring,user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'''SELECT * FROM transactions
                WHERE pstring = %s
                AND user_id={user_id}'''
    vals = [pstring]
    try:
        cur.execute(sql,vals)
        transaction = cur.fetchone()
        if transaction:
            return transaction
        return []
    except Exception as e:
        logging.info(f'Unable to get_open_transaction_by_pstring({pstring}) due to : {e}')
        return []
    finally:
        cur.close()
        conn.close()
        
# Sector breakdown aggregations
def select_model_sector_profits_symbols_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT symbol from transactions WHERE actual > 0 and result = 1 AND user_id={user_id}'
    try:
        cur.execute(sql)
        symbols = cur.fetchall()
        if symbols:
            return symbols
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def select_model_sector_loss_symbols_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT symbol from transactions WHERE actual < 0 and result = 0 AND user_id={user_id}'
    try:
        cur.execute(sql)
        symbols = cur.fetchone()
        if symbols:
            return symbols
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def select_model_sector_recommended_symbols(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT symbol from transactions WHERE user_id={user_id}'
    try:
        cur.execute(sql)
        symbols = cur.fetchone()
        if symbols:
            return symbols[0]
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def select_model_sector_not_recommended_symbols(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'SELECT symbol from transactions WHERE user_id={user_id}'
    try:
        cur.execute(sql)
        symbols = cur.fetchone()
        if symbols:
            return symbols[0]
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_last_transaction(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM transactions
            WHERE user_id = %s ORDER ASC
            LIMIT 1'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        id = cur.fetchone()
        if id:
            return id
        return None 
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to get transaction id due to : {e}')
    finally:
        cur.close()
        conn.close()    
def insert_transactions(transactions):
    for transaction in transactions:
        insert_transaction(transaction)


def insert_transaction(transaction):
    from database import pending_orders_DAOIMPL
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            INSERT INTO transactions
            (
            symbol,
            dp,
            ppps,
            qty,
            total_buy,
            pstring,
            ds,
            spps,
            tsp,
            sstring,
            expected,
            proi,
            actual,
            tp1,
            sop,
            confidence,
            result,
            user_id,
            sector
            ) VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s
            )
            '''
    vals = [transaction.symbol,
            transaction.dp,
            transaction.ppps,
            transaction.qty,
            transaction.total_buy,
            transaction.pstring,
            transaction.ds,
            transaction.spps,
            transaction.tsp,
            transaction.sstring,
            transaction.expected,
            transaction.proi,
            transaction.actual,
            transaction.tp1,
            transaction.sop,
            transaction.sentiment,
            transaction.result,
            transaction.user_id,
            transaction.sector]
    try:
        cur.execute(sql,vals)
        conn.commit()
        id = cur.lastrowid()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
        pending_orders_DAOIMPL.delete_pending_order_after_fill(id)
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to insert transaction {transaction.symbol, transaction.ppps} due to : {e}')
    finally:
        cur.close()
        conn.close()

def update_transaction(transaction_id, values):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            UPDATE transactions
            SET
            ds = %s,
            spps = %s,
            tsp = %s,
            sstring = %s,
            proi = %s,
            actual = %s,
            result = %s
            WHERE
            id = %s
        '''
    vals = [values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            values[5],
            values[6],
            transaction_id
            ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated transaction {datetime.now()}id:{transaction_id}")
        else:
            logging.info(f"{datetime.now()}:No record {transaction_id} has not been updated.")
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to update transaction {transaction_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
