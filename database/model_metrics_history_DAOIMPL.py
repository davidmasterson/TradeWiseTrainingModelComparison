from database import database_connection_utility as dcu
import logging
from datetime import datetime



def create_model_metrics_history_table(user_id):
    conn = dcu.get_db_connection()
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
            metrics_history.timestamp
            ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert metrics history, due to : {e}')
    finally:
        cur.close()
        conn.close()