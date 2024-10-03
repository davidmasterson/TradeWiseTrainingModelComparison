import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import database_connection_utility as dcu
from datetime import datetime
import logging


def insert_user_preferance(up):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO user_preferences(
            min_pps,
            max_pps,
            min_inv_per_sym,
            max_inv_per_sym,
            user_id,
            risk_tolerance)
            VALUES(
                %s,%s,%s,
                %s,%s,%s)
          '''
    vals = [up.min_price_per_share,
            up.max_price_per_share,
            up.min_investment,
            up.max_investment,
            up.user_id,
            up.risk_tolerance]
    
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()
        

    
def get_all_preferences():
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM user_preferences'''
             
    try:
        cur.execute(sql)
        preferences = cur.fetchall()
        if preferences:
            return preferences
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cur.close()

def get_user_preferences(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM user_preferences
                WHERE user_id = %s'''
    vals = [user_id]           
    try:
        cur.execute(sql,vals)
        preferences = cur.fetchone()
        if preferences:
            return preferences
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cur.close()

def update_user_preferences_limits_for_user(user_id, minpps,maxpps,min_inv,max_inv):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE user_preferences
            SET
            min_pps = %s,
            max_pps = %s,
            min_inv_per_sym = %s,
            max_inv_per_sym = %s
            WHERE user_id = %s'''
    vals = [minpps,maxpps,min_inv,max_inv,user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated transaction {datetime.now()}id:{user_id}")
        else:
            logging.info(f"{datetime.now()}:No record {user_id} has not been updated.")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()        
