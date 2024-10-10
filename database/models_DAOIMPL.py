from database import database_connection_utility as dcu
import logging 
from datetime import datetime


def create_models_table(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql1 = '''DROP TABLE IF EXISTS models'''
    sql2 = '''CREATE TABLE models(
            id INT AUTO_INCREMENT,
            model_name VARCHAR(100) NOT NULL,
            model_data blob NOT NULL,
            user_id INT NOT NULL,
            PRIMARY KEY (id),
            selected BOOLEAN DEFAULT FALSE,
            CONSTRAINT users_models FOREIGN KEY (user_id) REFERENCES users(id))'''
            
    try:
        cur.execute(sql1)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()} - Models Table created successfully by user: {user_id}')
    except Exception as e:
        logging.info(f'{datetime.now()} - User: {user_id} Unable to create models table due to:{e}')
    finally:
        conn.close()
        cur.close()
        
def get_trained_models_id_for_user_by_name(user_id, model_name):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT id FROM models WHERE user_id = %s AND model_name=%s'''
    vals = [user_id, model_name]
    try:
        cur.execute(sql, vals)
        id = cur.fetchone()[0]
        if id:
            return id
        return []
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to get trained model id for user: {user_id} due to : {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_trained_model_for_user_by_model_name(user_id, model_name):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT model_data FROM models WHERE user_id = %s AND model_name = %s'''
    vals = [user_id, model_name]
    try:
        cur.execute(sql, vals)
        model = cur.fetchone()[0]
        if model:
            return model
        return []
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to get trained model for user: {user_id} with model name {model_name} due to : {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_trained_model_names_for_user(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT model_name FROM models WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        model = cur.fetchall()
        if model:
            return model
        return []
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to get trained models for user: {user_id}  due to : {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_comparison_trained_models_for_user(user_id):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SELECT model_data FROM models WHERE user_id = %s AND selected = TRUE'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        model = cur.fetchall()
        if model:
            return model
        return []
    except Exception as e:
        logging.info(f'{datetime.now()} - Unable to get trained models for user: {user_id} due to : {e}')
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
        
def update_selected_models_for_user(user_id, model_name1=None, model_name2=None):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    
    # Unselect all models first
    sql_unselect_all = '''
        UPDATE models
        SET selected = 0
        WHERE user_id = %s
    '''
    cur.execute(sql_unselect_all, (user_id,))
    conn.commit()
    
    # Create base query for updating selected models
    sql_select = '''UPDATE models 
                    SET selected = 1
                    WHERE user_id = %s
                    AND model_name IN (%s, %s)
                 '''
    
    # Handle one or two models
    if model_name1 and model_name2:
        vals = (user_id, model_name1, model_name2)
    elif model_name1:  # If only one model provided
        sql_select = '''UPDATE models 
                        SET selected = 1
                        WHERE user_id = %s
                        AND model_name = %s
                     '''
        vals = (user_id, model_name1)
    else:
        logging.error(f"No valid model names provided for user {user_id}")
        return
    
    # Execute the selection update
    try:
        cur.execute(sql_select, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) updated for user {user_id}: {model_name1} or {model_name2}")
        else:
            logging.info(f"No model records updated for user {user_id}")
    except Exception as e:
        logging.error(f"Unable to update model for user {user_id} due to: {e}")
    finally:
        cur.close()
        conn.close()
