import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import database_connection_utility as dcu
from datetime import datetime
from Models import user
import logging

def create_user_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DROP TABLE IF EXISTS users'''
    sql2 = '''CREATE TABLE users(
            id INT AUTO_INCREMENT,
            first VARCHAR(50) NOT NULL,
            last VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            user_name VARCHAR(20) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            alpaca_key VARCHAR(255) NOT NULL,
            alpaca_secret VARCHAR(255) NOT NULL,
            alpaca_endpoint VARCHAR(255) NOT NULL,
            PRIMARY KEY (id))
            '''
    try:
        cur.execute(sql)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        logging.info( f'{datetime.now()}:User: {user_id} Unable to create users table due to : {e}')
    finally:
        cur.close()
        conn.close()


def get_user_by_username(user_name):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users WHERE user_name = %s'''
    vals = [user_name]
    try:
        cur.execute(sql, vals)
        rows = cur.fetchall()  # Fetch all rows as tuples
        if rows:
            # Get the column names from the cursor description
            columns = [col[0] for col in cur.description]
            
            # Convert each row into a dictionary
            user = [dict(zip(columns, row)) for row in rows]
            return user
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_user_by_email_address(email):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users WHERE email = %s'''
    vals = [email]
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

def get_user_by_user_id(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users WHERE id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        id = cur.fetchone()
        if id:
            return id
        return None
        
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()
        
def get_user_by_email(email):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users WHERE email = %s'''
    vals = [email]
    try:
        cur.execute(sql, vals)
        count = cur.fetchone()
        if count:
            return count
        return None
        
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_total_number_of_users():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT count(*) FROM users'''
    
    try:
        cur.execute(sql)
        count = cur.fetchone()
        if count:
            return count[0]
        return None
        
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_username_by_user_id_with_db_conn(user_id, conn):
    cur = conn.cursor()
    sql = '''SELECT user_name FROM users WHERE id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        id = cur.fetchone()
        if id:
            return id
        return None
        
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()

def get_all_users():
    conn = dcu.get_db_connection()
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
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO users(
                first,
                last,
                email,
                user_name,
                password,
                alpaca_key,
                alpaca_secret,
                alpaca_endpoint
                )
                VALUES(
                %s,%s,%s,%s,%s,
                %s,%s,%s)'''
    vals = [user.first,
            user.last,
            user.email,
            user.user_name,
            user.password,
            user.alpaca_key,
            user.alpaca_secret,
            user.alpaca_endpoint
            ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        user_id = cur.lastrowid
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
        return user_id
    except Exception as e:
        logging.error(f'{datetime.now()} unable to insert user {user.first} due to : {e} ')
    finally:
        cur.close()
        conn.close()
        
def delete_user(id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = f'''DELETE FROM users
            WHERE id=%s'''
    vals = [id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record deleted")
    except Exception as e:
        logging.info(e)
        return None
    finally:
        conn.close()
        cur.close()


def update_user_alpaca_keys(key, secret_key, id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE users SET
            alpaca_key = %s,
            alpaca_secret = %s,
            alpaca_endpoint=%s
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

def update_user(user, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE users SET
            first = %s,
            last = %s,
            email = %s,
            password = %s,
            alpaca_key = %s,
            alpaca_secret = %s,
            alpaca_endpoint = %s,
            WHERE 
            id = %s'''
    vals = [
        user.first,
        user.last,
        user.email,
        user.password,
        user.alpaca_key,
        user.alpaca_secret,
        user.alpaca_endpoint,
        user_id
    ] 
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f" {datetime.now()} {cur.rowcount}, record(s) affected updated user {user_id}")
            return True
        else:
            logging.error(f"{datetime.now()}:No user has been updated for user {user_id}.")
    except Exception as e:
        logging.error(f'{datetime.now()} Unable to update user {user_id} due to {e}')
    finally:
        cur.close()
        conn.close()       
    
def update_user_password(user_id, password_hash):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE users SET
            password = %s
            WHERE 
            id = %s'''
    vals = [password_hash,user_id]
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f" {datetime.now()} {cur.rowcount}, record(s) affected updated user password for user {user_id}")
            return True
        else:
            logging.info(f"{datetime.now()}:No password has been updated for user {user_id}.")
    except Exception as e:
        logging.error(f'{datetime.now()} Unable to update user password for user {user_id} due to {e}')
        return False
    finally:
        cur.close()
        conn.close()

def update_user_email(user_id, email):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE users SET
            email = %s
            WHERE 
            id = %s'''
    vals = [email,user_id]
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f" {datetime.now()} {cur.rowcount}, record(s) affected updated email for user {user_id}")
            return True
        else:
            logging.info(f"{datetime.now()}:No email has been updated for user {user_id}.")
    except Exception as e:
        logging.error(f'{datetime.now()} Unable to update user email address for user {user_id} due to {e}')
        return False
    finally:
        cur.close()
        conn.close()