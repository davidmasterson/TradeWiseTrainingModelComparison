from database import database_connection_utility as dcu
import logging 
from datetime import datetime


def create_models_table():
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS models(
            id INT AUTO_INCREMENT,
            model_name VARCHAR(100) NOT NULL,
            model_data blob NOT NULL,
            user_id INT NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT users_models FOREIGN KEY (user_id) REFERENCES users(id))'''
            
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f'{datetime.now()} - Models Table created successfully')
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to create models table due to:{e}')
    finally:
        conn.close()
        cur.close()
        
def get_trained_model_for_user(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT model_data FROM models WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        model = cur.fetchone()[0]
        if model:
            return model
        return []
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to get trained model for user: {user_id} due to : {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def insert_model_into_models_for_user(model):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO models(
                model_name,
                model_data,
                user_id)VALUES(
                    %s,%s,%s)'''
    vals = [model.model_name,
            model.model_data,
            model.user_id]
    
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to insert transaction {model.model_name}, for user {model.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def update_model_for_user(model, model_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE models SET
                model_name = %s,
                model_data = %s
            WHERE id = %s
            '''
    vals = [model.model_name,
            model.model_data,
            model_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated model {datetime.now()}id:{model_id}")
        else:
            logging.info(f"{datetime.now()}:No model record {model_id} has not been updated.")
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to update model {model_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        