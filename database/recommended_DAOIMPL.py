from database import database_connection_utility as dcu
from datetime import datetime
import logging


def create_recommended_table():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DROP TABLE IF EXISTS recommended'''
    sql2 = '''CREATE TABLE recommended(
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        price float NOT NULL,
        confidence INT NOT NULL)'''
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f'{datetime.now()}: recommended table created successfully')
    except Exception as e:
        logging.error(f'{datetime.now()}: Was unable to create recommended table due to {e}')
    finally:
        conn.close()
        cur.close()
        
        
def get_recommended_by_price(max_price, min_price):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM recommended
            WHERE price >= %s AND price is <= %s'''
    vals = [min_price, max_price]
    try:
        cur.execute(sql,vals)
        recommendations = cur.fetchall()
        if recommendations:
            return recommendations
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get recommendations due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
        
def insert_recommendation(recommendation):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO recommended(
            symbol,
            price,
            confidence)
            VALUES(
                %s,%s,%s)'''
    vals = [recommendation.symbol,
            recommendation.price,
            recommendation.confidence]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f'{datetime.now()}: Successfully entered recommendation {recommendation.symbol,recommendation.price,recommendation.confidence} into recommended table.')
    except Exception as e:
        logging.error(f'{datetime.now()}: Was unable to insert recommendation {recommendation.symbol,recommendation.price,recommendation.confidence} in recommended table due to {e}')
    finally:
        conn.close()
        cur.close()