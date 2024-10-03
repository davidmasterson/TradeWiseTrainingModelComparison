import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import database_connection_utility as dcu
from datetime import datetime
from Models import user
import logging



def get_user_by_username(user_name):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users WHERE user_name = %s'''
    vals = [user_name]
    try:
        cur.execute(sql, vals)
        rows = cur.fetchall()  # Fetch all rows as tuples
        
        # Get the column names from the cursor description
        columns = [col[0] for col in cur.description]
        
        # Convert each row into a dictionary
        user = [dict(zip(columns, row)) for row in rows]
        
        return user if user else []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_all_users():
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users'''
    try:
        cur.execute(sql)
        rows = cur.fetchall()  # Fetch all rows as tuples
        
        # Get the column names from the cursor description
        columns = [col[0] for col in cur.description]
        
        # Convert each row into a dictionary
        user = [dict(zip(columns, row)) for row in rows]
        
        return user if user else []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def insert_user(user):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO users(
                first,
                last,
                user_name,
                password,
                alpaca_key,
                alpaca_secret,
                email
                )
                VALUES(
                %s,%s,%s,%s,%s,
                %s,%s)'''
    vals = [user.first,
            user.last,
            user.user_name,
            user.password,
            user.alpaca_key,
            user.alpaca_secret,
            user.email
            ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
        return cur.rowcount
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()
        
def delete_user(id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = f'''DELETE FROM users
            WHERE id={id}'''
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record deleted")
    except Exception as e:
        logging.info(e)
        return None
    finally:
        conn.close()
        cur.close()


def update_user_alpaca_keys(key, secret_key, id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE users SET
            alpaca_key = %s,
            alpaca_secret = %s
            WHERE 
            id = %s'''
    vals = [key,secret_key,id]
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated transaction {datetime.now()}")
        else:
            logging.info(f"{datetime.now()}:No record has not been updated.")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()