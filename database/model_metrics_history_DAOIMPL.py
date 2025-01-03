from database import database_connection_utility as dcu
import logging
from datetime import datetime
from Models import user



def create_model_metrics_history_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql1 = '''DROP TABLE IF EXISTS model_metrics_history'''
    sql2 = '''CREATE TABLE model_metrics_history(
                id INT AUTO_INCREMENT,
                model_id INT NOT NULL,
                accuracy FLOAT NOT NULL,
                `precision` FLOAT NOT NULL,
                recall FLOAT NOT NULL,
                f1_score FLOAT NOT NULL,
                top_features JSON NOT NULL,
                timestamp DATETIME NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (model_id) REFERENCES models(id)
            )'''
    try:
        cur.execute(sql1)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()} - model_metrics_history Table created successfully for user: {user_id}')
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to create model_metrics_history table for user: {user_id} due to:{e}')
    finally:
        conn.close()
        cur.close()
 
def get_most_recent_metric_history_for_all_ml_models():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT m.model_name, mmh.accuracy, mmh.precision, mmh.recall, mmh.f1_score, mmh.top_features, mmh.timestamp
        FROM model_metrics_history mmh
        JOIN models m ON mmh.model_id = m.id
        WHERE mmh.id IN (
            SELECT MAX(id) FROM model_metrics_history GROUP BY model_id
        )
        ORDER BY mmh.timestamp DESC
    '''
    try:
        cur.execute(sql)
        results = cur.fetchall()
        logging.info(f'{datetime.now()} - Successfully retrieved most recent metric history for all ML models')
        return results
    except Exception as e:
        logging.error(f'{datetime.now()} - Failed to retrieve most recent metric history due to: {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_most_recent_metric_history_for_all_selected_ml_models():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT m.model_name, mmh.accuracy, mmh.precision, mmh.recall, mmh.f1_score, mmh.top_features, mmh.timestamp
        FROM model_metrics_history mmh
        JOIN models m ON mmh.model_id = m.id
        WHERE m.selected = 1 AND mmh.id IN (
            SELECT MAX(id) FROM model_metrics_history GROUP BY model_id
        )
        ORDER BY mmh.timestamp DESC
    '''
    try:
        cur.execute(sql)
        results = cur.fetchall()
        logging.info(f'{datetime.now()} - Successfully retrieved most recent metric history for all ML models')
        return results
    except Exception as e:
        logging.error(f'{datetime.now()} - Failed to retrieve most recent metric history due to: {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_all_metrics_history_for_all_models_sorted_by_model():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT m.model_name, mmh.accuracy, mmh.precision, mmh.recall, mmh.f1_score, mmh.top_features, mmh.timestamp
        FROM model_metrics_history mmh
        JOIN models m ON mmh.model_id = m.id
        ORDER BY m.model_name, mmh.timestamp DESC
    '''
    try:
        cur.execute(sql)
        results = cur.fetchall()
        logging.info(f'{datetime.now()} - Successfully retrieved all metric history for all ML models sorted by model')
        return results
    except Exception as e:
        logging.error(f'{datetime.now()} - Failed to retrieve all metric history due to: {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_all_metrics_history_for_all_selected_models_for_user_sorted_by_model(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT m.model_name, mmh.accuracy, mmh.precision, mmh.recall, mmh.f1_score, mmh.top_features, mmh.timestamp
        FROM model_metrics_history mmh
        JOIN models m ON mmh.model_id = m.id
        WHERE m.selected = 1 AND m.user_id = %s
        ORDER BY m.model_name, mmh.timestamp DESC
    '''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        results = cur.fetchall()
        logging.info(f'{datetime.now()} - Successfully retrieved all metric history for all ML models sorted by model')
        return results
    except Exception as e:
        logging.error(f'{datetime.now()} - Failed to retrieve all metric history due to: {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_most_recent_mmh_for_model(model_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT MONTH(timestamp) AS month, DAY(timestamp) AS day FROM model_metrics_history
                WHERE model_id = %s
                ORDER BY timestamp DESC
                LIMIT 1'''
    vals = [model_id]
    try:
        cur.execute(sql, vals)
        results = cur.fetchone()
        if results:
            return results[0]
        return []
    except Exception as e:
        print(f"Error fetching last trained date for model {model_id}: {e}")
    finally:
        cur.close()
        conn.close()
    

def get_last_trained_dates():
    conn = dcu.get_db_connection()  
    cur = conn.cursor()
    sql = '''SELECT models.user_id,MAX(model_metrics_history.timestamp) AS last_trained
                FROM model_metrics_history
                JOIN models 
                ON model_metrics_history.model_id = models.id
                WHERE models.user_id BETWEEN 1 AND 6
                GROUP BY models.user_id;
    '''
    try:
        cur.execute(sql)
        results = cur.fetchall()
        if results:
            return results
        return []
    except Exception as e:
        print(f"Error fetching last trained dates: {e}")
    finally:
        cur.close()
        conn.close()
            
def insert_metrics_history(metrics_history):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO model_metrics_history(
                model_id,
                accuracy,
                `precision`,
                recall,
                f1_score,
                top_features,
                timestamp
                )VALUES(
                    %s,%s,%s,%s,
                    %s,%s,%s)'''
    vals = [metrics_history.model_id,
            metrics_history.accuracy,
            metrics_history.precision,
            metrics_history.recall,
            metrics_history.f1_score,
            metrics_history.top_features,
            metrics_history.timestamp,
            
            ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
        return True
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert metrics history, due to : {e}')
        return False
    finally:
        cur.close()
        conn.close()