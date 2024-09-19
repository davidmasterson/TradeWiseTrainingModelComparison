import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import database_connection_utility as dcu
from datetime import datetime
from Models import user


def get_user_by_username(username):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * from users WHERE user = %s '''
    vals = [username]
    try:
        cur.execute(sql, vals)
        user = cur.fetchone()
        if user:
            return user
        return None
    except Exception as e:
        print(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_user_by_username(user_name):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM users WHERE user = %s'''
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
        print(e)
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
                user,
                password,
                email,
                min_investment,
                max_investment,
                min_price,
                max_price,
                risk_tolerance)
                VALUES(
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s)'''
    vals = [user.first,
            user.last,
            user.user,
            user.password,
            user.email,
            user.min_investment,
            user.max_investment,
            user.min_price,
            user.max_price,
            user.risk_tolerance]
    try:
        cur.execute(sql, vals)
        conn.commit()
        print(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()

