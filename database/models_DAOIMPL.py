from database import database_connection_utility as dcu
import logging 
from datetime import datetime
import tensorflow as tf


def create_models_table():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql1 = '''DROP TABLE IF EXISTS models'''
    sql2 = '''CREATE TABLE models(
            id INT AUTO_INCREMENT,
            model_name VARCHAR(100) NOT NULL,
            model_data blob NOT NULL,
            PRIMARY KEY (id),
            selected BOOLEAN DEFAULT FALSE
            '''
            
    try:
        cur.execute(sql1)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()} - Models Table created successfully by user: ')
    except Exception as e:
        logging.info(f'{datetime.now()} - User:  Unable to create models table due to:{e}')
    finally:
        conn.close()
        cur.close()
        
# Function to retrieve the model from the database
def load_model_from_db(model_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT model_data FROM models WHERE model_id = %s"
    cursor.execute(query, model_id)
    result = cursor.fetchone()
    cursor.close()

    model_binary = result[0]
    
    # Save the binary model to a temporary file
    with open("temp_model.h5", "wb") as temp_file:
        temp_file.write(model_binary)
    
    # Load the model from the temporary file
    model = tf.keras.models.load_model("temp_model.h5")
    return model
        
def insert_model_into_models_for_user(model):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO models(
                model_name,
                model_data
                )VALUES(
                    %s,%s)'''
    vals = [model.model_name,
            model.model_data
    ]
    
    try:
        cur.execute(sql,vals)
        model_id = cur.lastrowid
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted")
        return model_id
    except Exception as e:
        logging.info( f'{datetime.now()}:Unable to insert transaction {model.model_name}, for user  due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def update_model_for_user(model, model_id):
    conn = dcu.get_db_connection()
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
        
def update_selected_models_for_user( model_name1=None, model_name2=None):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    
    # Unselect all models first
    sql_unselect_all = '''
        UPDATE models
        SET selected = 0
    '''
    cur.execute(sql_unselect_all)
    conn.commit()
    
    # Create base query for updating selected models
    sql_select = '''UPDATE models 
                    SET selected = 1
                    WHERE model_name IN (%s, %s)
                 '''
    
    # Handle one or two models
    if model_name1 and model_name2:
        vals = ( model_name1, model_name2)
    elif model_name1:  # If only one model provided
        sql_select = '''UPDATE models 
                        SET selected = 1
                        WHERE model_name = %s
                     '''
        vals = ( model_name1)
    else:
        logging.error(f"No valid model names provided for user ")
        return
    
    # Execute the selection update
    try:
        cur.execute(sql_select, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) updated for user : {model_name1} or {model_name2}")
        else:
            logging.info(f"No model records updated for user ")
    except Exception as e:
        logging.error(f"Unable to update model for user  due to: {e}")
    finally:
        cur.close()
        conn.close()
