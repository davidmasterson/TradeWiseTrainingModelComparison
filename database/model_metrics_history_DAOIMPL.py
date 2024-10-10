from database import database_connection_utility as dcu
import logging
from datetime import datetime



def create_model_metrics_history_table(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql1 = '''DROP TABLE IF EXISTS model_metrics_history'''
    sql2 = '''CREATE TABLE model_metrics_history(
            id INT AUTO_INCREMENT,
            model_id INT NOT NULL,
            accuracy DECIMAL(10,2) NOT NULL,
            `precision` DECIMAL(10,2) NOT NULL,
            recall DECIMAL(10,2) NOT NULL,
            f1_score DECIMAL(10,2) NOT NULL,
            top_features JSON NOT NULL,
            timestamp DATETIME NOT NULL,
            user_id INT NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (model_id) REFERENCES models(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
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
 
def get_most_recent_metric_for_user_selected_models(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql ='''SELECT mmh.model_id, m.model_name, mmh.accuracy, mmh.precision, 
            mmh.recall, mmh.f1_score, mmh.top_features, mmh.timestamp
            FROM model_metrics_history mmh
            JOIN models m ON mmh.model_id = m.id
            WHERE m.user_id = %s
            AND m.selected = 1
            ORDER BY mmh.timestamp DESC
            LIMIT 2'''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.error(f'Unable to get selected model metrics for user: {user_id} due to :{e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_all_metrics_history_for_selected_models(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql ='''SELECT mmh.model_id, m.model_name, mmh.accuracy, mmh.precision, 
            mmh.recall, mmh.f1_score, mmh.top_features, mmh.timestamp
            FROM model_metrics_history mmh
            JOIN models m ON mmh.model_id = m.id
            WHERE m.user_id = %s
            AND m.selected = 1
            ORDER BY mmh.timestamp ASC
            '''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.error(f'Unable to get selected model metrics for user: {user_id} due to :{e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_all_model_metrics_for_user(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM model_metrics_history WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.error(f'Unable to get historical metrics for user : {user_id} due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def insert_metrics_history(metrics_history):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO model_metrics_history(
                model_id,
                accuracy,
                `precision`,
                recall,
                f1_score,
                top_features,
                timestamp,
                user_id)VALUES(
                    %s,%s,%s,%s,
                    %s,%s,%s,%s)'''
    vals = [metrics_history.model_id,
            metrics_history.accuracy,
            metrics_history.precision,
            metrics_history.recall,
            metrics_history.f1_score,
            metrics_history.top_features,
            metrics_history.timestamp,
            metrics_history.user_id]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert metrics history, for user {metrics_history.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()