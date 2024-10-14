from database import database_connection_utility as dcu
from datetime import datetime 
import logging

def create_recommender_progress_table():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql1 = '''DROP TABLE IF EXISTS recommender_progress'''
    sql2 = '''CREATE TABLE recommender_progress(
            id INT AUTO_INCREMENT PRIMARY KEY,
            recommender_progress int default 0)
            '''
            
    try:
        cur.execute(sql1)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()} - recommender_progress Table created successfully by user: ')
    except Exception as e:
        logging.info(f'{datetime.now()} - User:  Unable to create recommender_progress table due to:{e}')
    finally:
        conn.close()
        cur.close()
        
def get_recommender_progress():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM
            recommender_progress'''
    try:
        cur.execute(sql)
        progress = cur.fetchone()
        if progress:
            return progress
        return False
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to retrieve recommender progress due to {e}')
        return False
    finally:
        conn.close()
        cur.close()
        
def insert_recommender_progress(progress):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO recommender_progress(
                progress)
                VALUES(%s)'''
    vals = [progress]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to insert recommender progresss for user  due to : {e}')
    finally:
        cur.close()
        conn.close()
    
def update_recommender_progress(new_progress, progress_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE recommender_progress SET
                progress = %s
            WHERE id = %s
            '''
    vals = [new_progress,
            progress_id
            ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated recommender progress {datetime.now()}id:{progress_id}")
        else:
            logging.info(f"{datetime.now()}:No progression record {progress_id} has not been updated.")
        return progress_id
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to update progression {progress_id} due to : {e}')
    finally:
        cur.close()
        conn.close()