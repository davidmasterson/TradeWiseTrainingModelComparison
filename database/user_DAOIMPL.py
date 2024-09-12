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


def insert_user(user):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO users(
                first,
                last,
                user,
                pass,
                alpaca_key,
                alpaca_secret)
                VALUES(
                %s,%s,%s,%s,%s,%s)'''
    vals = [user.first_name,
            user.last_name,
            user.username,
            user.password,
            user.alpaca_key,
            user.alpaca_secret]
    try:
        cur.execute(sql, vals)
        conn.commit()
        print(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()

