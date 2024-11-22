from database import database_connection_utility as dcu
from datetime import datetime
import logging

def create_trade_settings_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DROP TABLE IF EXISTS trade_settings'''
    sql2 = '''CREATE TABLE trade_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                min_price DECIMAL(10,2),
                max_price DECIMAL(10,2),
                risk_tolerance ENUM('low', 'medium', 'high'),
                confidence_threshold INT,
                min_total float not null,
                max_total float not null,
                FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
            )'''
    try:
        cur.execute(sql)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()}: User {user_id} dropped and created a new trade_settings table')
    except Exception as e:
        logging.error(f'{datetime.now()}: User {user_id} was unsuccessful at creating a new trade_settings table due to {e}')
    finally:
        conn.close()
        cur.close()
        
def get_trade_settings_by_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM trade_settings 
                WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        trade_settings = cur.fetchone()
        if trade_settings:
            logging.info(f"{datetime.now()}: trade settings successfully retrieved for user {user_id}")
            return trade_settings
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: could not retrieve trade setttins for user {user_id} due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_trade_settings_for_test_users():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM trade_settings 
                WHERE user_id BETWEEN 1 AND 6
                GROUP BY user_id'''
    
    try:
        cur.execute(sql)
        trade_settings = cur.fetchall()
        if trade_settings:
            logging.info(f"{datetime.now()}: trade settings successfully retrieved for testing account users")
            return trade_settings
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: could not retrieve trade setttins for testing account users due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def insert_trade_setting(trade_setting):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO trade_settings(
                user_id,
                min_price,
                max_price,
                risk_tolerance,
                confidence_threshold,
                min_total,
                max_total)
                
                VALUES(%s,%s,%s,%s,%s,%s,%s)'''
    vals = [
        trade_setting.user_id,
        trade_setting.min_price,
        trade_setting.max_price,
        trade_setting.risk_tolerance,
        trade_setting.confidence_threshold,
        trade_setting.min_total,
        trade_setting.max_total
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{datetime.now()}: {cur.rowcount}, record(s) affected inserted trade settings for user {trade_setting.user_id}")
        else:
            logging.info(f"{datetime.now()}:No record trade settings has not been updated for user {trade_setting.user_id}.")
        return True
    except Exception as e:
        logging.error(f'{datetime.now()}: trade setting could not be updated for user: {trade_setting.user_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()

def update_min_price(min_price, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE trade_settings SET
                min_price = %s
                WHERE user_id = %s'''
    vals = [min_price, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{datetime.now()}: {cur.rowcount}, record(s) affected updated min price {min_price} for user {user_id}")
        else:
            logging.info(f"{datetime.now()}:No record trade settings min pice {min_price} has not been updated for user {user_id}.")
        return True
    except Exception as e:
        logging.error(f'{datetime.now()}: min price could not be updated for user: {user_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()

def update_max_price(max_price, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE trade_settings SET
                max_price = %s
                WHERE user_id = %s'''
    vals = [max_price, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{datetime.now()}: {cur.rowcount}, record(s) affected updated max price {max_price} for user {user_id}")
        else:
            logging.info(f"{datetime.now()}:No record trade settings max price {max_price} has not been updated for user {user_id}.")
        return True
    except Exception as e:
        logging.error(f'{datetime.now()}: max price could not be updated for user: {user_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()

def update_risk_tolerance(risk_tolerance, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE trade_settings SET
                risk_tolerance = %s
                WHERE user_id = %s'''
    vals = [risk_tolerance, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{datetime.now()}: {cur.rowcount}, record(s) affected updated risk tolerance {risk_tolerance} for user {user_id}")
        else:
            logging.info(f"{datetime.now()}:No record trade settings risk tolerance {risk_tolerance} has not been updated for user {user_id}.")
        return True
    except Exception as e:
        logging.error(f'{datetime.now()}: risk tolerance could not be updated for user: {user_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()

def update_confidence_threshold(confidence_threshold, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE trade_settings SET
                confidence_threshold = %s
                WHERE user_id = %s'''
    vals = [confidence_threshold, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{datetime.now()}: {cur.rowcount}, record(s) affected updated confidence threshold {confidence_threshold} for user {user_id}")
        else:
            logging.info(f"{datetime.now()}:No record trade settings confidence threshold {confidence_threshold} has not been updated for user {user_id}.")
        return True
    except Exception as e:
        logging.error(f'{datetime.now()}: confidence threshold could not be updated for user: {user_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()

def update_trade_settings_for_user(trade_settings, trade_settings_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE trade_settings SET
                user_id = %s,
                min_price =%s,
                max_price = %s,
                risk_tolerance = %s,
                confidence_threshold = %s,
                min_total = %s,
                max_total = %s
                WHERE id = %s'''
    vals = [trade_settings.user_id,
            trade_settings.min_price,
            trade_settings.max_price,
            trade_settings.risk_tolerance,
            trade_settings.confidence_threshold,
            trade_settings.min_total,
            trade_settings.max_total,
            trade_settings_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{datetime.now()}: {cur.rowcount}, record(s) affected updated trade settings for user {trade_settings.user_id}")
        else:
            logging.info(f"{datetime.now()}:No record trade settings trade settings  has not been updated for user {trade_settings.user_id}.")
        return True
    except Exception as e:
        logging.error(f'{datetime.now()}: trade settings could not be updated for user: {trade_settings.user_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()
        
        
