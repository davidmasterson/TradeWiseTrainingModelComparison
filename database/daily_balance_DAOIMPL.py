from database import database_connection_utility as dcu
import logging
from datetime import datetime


def create_daily_balances_table():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            CREATE TABLE daily_balances(
                id INT PRIMARY KEY AUTO_INCREMENT,
                date DATE NOT NULL,
                balance FLOAT NOT NULL,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id))'''
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        logging.exception(f'{datetime.now()}:Unable to create daily balances table: {e}')
    finally:
        cur.close()
        conn.close()
        
        
def get_daily_balances_for_user(user_id:int):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            SELECT * FROM daily_balances
            WHERE user_id = %s
            '''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        balances = cur.fetchall()
        if balances:
            return balances
        return None
    except Exception as e:
        logging.exception(f'{datetime.now()}:Unable to get balances for user : {e}')
        return None
    finally:
        cur.close()
        conn.close()

def get_daily_balances_for_user_by_date(user_id:int, date:str):
    ''' Returns a list of Balance rows or None'''
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            SELECT * FROM daily_balances
            WHERE user_id = %s
            AND str_to_date(date, "%Y-%m-%d") = %s
            '''
    vals = [user_id, date]
    try:
        cur.execute(sql, vals)
        balances = cur.fetchall()
        if balances:
            return balances
        return None
    except Exception as e:
        logging.exception(f'{datetime.now()}:Unable to get balances for user by date : {e}')
    finally:
        cur.close()
        conn.close()

def insert_balance(balance):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            INSERT INTO daily_balances(
                date,
                closing_balance, 
                user_id
            ) VALUES (%s,%s,%s)
            '''
    vals = [balance.dt,
            balance.balance,
            balance.user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, balance record inserted")
        return cur.lastrowid
    except Exception as e:
        logging.exception(f'{datetime.now()}:Unable to insert balance for user {balance.user_id}: {e}')
    finally:
        cur.close()
        conn.close()
        
def update_balance(balance_amount:float, id:int):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            UPDATE daily_balances
            SET closing_balance = %s
            WHERE id = %s
            '''
    vals = [balance_amount, id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f'{datetime.now()}:{cur.rowcount}, blance record updated')
        return cur.lastrowid
    except Exception as e:
        logging.exception(f'{datetime.now()}: Unable to update balance id {id}: {e}')
    finally:
        cur.close()
        conn.close()
        
def get_first_balance_for_all_users():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            SELECT user_id, MIN(date) AS first_date, balance
            FROM daily_balances
            GROUP BY user_id
            '''
    try:
        cur.execute(sql)
        first_balances = cur.fetchall()
        return first_balances
    except Exception as e:
        logging.exception(f'{datetime.now()}: Unable to get first balances for all users: {e}')
        return None
    finally:
        cur.close()
        conn.close()
        
def get_first_balance_for_specific_endpoint(alpaca_endpoint:str):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            SELECT db.user_id, MIN(db.date) AS first_date, db.closing_balance
            FROM daily_balances db
            JOIN users u ON db.user_id = u.id
            WHERE u.alpaca_endpoint = %s
            GROUP BY db.user_id
            '''
    vals = [alpaca_endpoint]
    try:
        cur.execute(sql, vals)
        first_balances = cur.fetchall()
        return first_balances
    except Exception as e:
        logging.exception(f'{datetime.now()}: Unable to get first balances for users with specific endpoint {alpaca_endpoint}: {e}')
        return None
    finally:
        cur.close()
        conn.close()