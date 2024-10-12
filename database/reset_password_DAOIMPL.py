import logging
from database import database_connection_utility as dcu
from datetime import datetime, timedelta 



def get_hashed_token_and_expiration_for_user(user_id):
    
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT hashed_token, expiration_time FROM password_resets WHERE user_id = %s'''
    vals = [user_id]  # Ensure it's a tuple
    try:
        cur.execute(sql, vals)  # Pass tuple directly
        results = cur.fetchone()
        if results:
            # Optionally, you can directly return a named tuple or a dictionary for better field access
            return results  # This will return a tuple or None if no results
        return None
    except Exception as e:
        logging.error(f'{datetime.now()} unable to retrieve hashed token and expiration time for user {user_id} due to {e}')
        return None
    finally:
        cur.close()
        conn.close()  # Ensure cursor is closed before connection

def get_user_id_by_token(token):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT user_id from password_resets WHERE reset_token = %s'''
    vals = [token]
    try:
        cur.execute(sql, vals)
        results = cur.fetchone()
        if results:
            return results
        return None
    except Exception as e:
        logging.error(f'{datetime.now()} unable to retrieve user id for token {token} due to {e}')
        return None
    finally:
        conn.close()
        cur.close()

def insert_password_reset_token(token):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = ''' INSERT INTO password_resets(
                user_id,
                reset_token,
                expiration_time,
                hashed_token)VALUES(%s,%s,%s,%s)'''
    vals = [
        token.user_id,
        token.token,
        token.expiration_time,
        token.hashed_token
    ]
    
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f'{datetime.now()} Password reset token was generated for user {token.user_id} successfully it will expire at {token.expiration_time}')
        return token.token
    except Exception as e:
        logging.error(f'{datetime.now()} Unable to create password reset token for user {token.user_id} due to {e}')
    finally:
        conn.close()
        cur.close()
        
def delete_user_password_reset_token(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DELETE from password_resets WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected deleted password reset {datetime.now()} for user: {user_id}")
        else:
            logging.error(f"{datetime.now()}:No password reset record for user {user_id} has not been deleted.")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to delete password reset for user {user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()