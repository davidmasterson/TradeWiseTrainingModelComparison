from database import database_connection_utility as dcu
import logging 
from datetime import datetime
import tensorflow as tf
from Models import user


def create_models_table():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql1 = '''DROP TABLE IF EXISTS models'''
    sql2 = '''CREATE TABLE models(
            id INT AUTO_INCREMENT,
            model_name VARCHAR(100) NOT NULL,
            model_data MEDIUMBLOB NOT NULL,
            user_id INT NOT NULL,
            selected BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES users(id))
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

def get_model_from_db_by_model_name_and_user_id(model_name, user_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM models WHERE model_name = %s AND user_id = %s"
    vals = [model_name, user_id]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchone()
        if result:
            return result
        return False
    except Exception as e:
        return e
    finally:
        conn.close()
        cursor.close()

def get_model_blob_from_db_by_model_name_and_user_id(model_name, user_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT model_data FROM models WHERE model_name = %s AND user_id = %s"
    vals = [model_name, user_id]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchone()
        if result:
            return result[0]
        return False
    except Exception as e:
        return e
    finally:
        conn.close()
        cursor.close()

def get_models_for_user_by_user_id(user_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM models WHERE user_id = %s"
    vals = [user_id]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchall()
        if result:
            return result
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cursor.close()

def get_model_name_for_model_by_model_id(model_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT model_name FROM models WHERE id = %s"
    vals = [model_id]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchone()
        if result:
            return result[0]
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cursor.close()

def get_model_id_for_model_by_model_name(model_name):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id FROM models WHERE model_name = %s"
    vals = [model_name]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchone()
        if result:
            return result[0]
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cursor.close()

def get_selected_models_for_user(user_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM models WHERE user_id = %s AND selected = 1"
    vals = [user_id]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchall()
        if result:
            return result
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cursor.close()

def get_models_for_user_by_model_id(model_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM models WHERE id = %s"
    vals = [model_id]
    try:
        cursor.execute(query, vals)
        result = cursor.fetchone()
        if result:
            return result
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cursor.close()


        
def insert_model_into_models_for_user(model):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    try:
        sql = '''INSERT INTO models(
                    model_name,
                    model_description,
                    model_data,
                    user_id,
                    selected
                    )VALUES(
                        %s,%s,%s,%s,%s)'''
        vals = [model.model_name,
                model.model_description,
                model.model_data,
                model.user_id,
                model.selected
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
    except Exception as e:
        return False
        
def update_model_for_user(model, model_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE models SET
                model_name = %s,
                model_description = %s,
                model_data = %s,
                user_id = %s,
                selected = %s
            WHERE id = %s
            '''
    vals = [model.model_name,
            model.model_description,
            model.model_data,
            model.user_id,
            model.selected,
            model_id
            ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated model {datetime.now()}id:{model_id}")
        else:
            logging.info(f"{datetime.now()}:No model record {model_id} has not been updated.")
        return model_id
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
        
def update_selected_status(selected_status, model_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    selected_status = 1 if selected_status == '1' else 0
    sql = '''UPDATE models
                SET selected = %s
            WHERE id = %s'''
    vals = [selected_status, model_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) updated for user : {model_id}")
        else:
            logging.info(f"No model records updated for user ")
    except Exception as e:
        logging.error(f"Unable to update model for user  due to: {e}")
    finally:
        cur.close()
        conn.close()
        
def update_model_data_by_name(model_name, model_data, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE models
                SET model_data = %s
            WHERE model_name = %s
            AND user_id = %s'''
    vals = [model_data, model_name, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, model_data updated for user : {user_id}")
        else:
            logging.info(f"No model records updated for user ")
    except Exception as e:
        logging.error(f"Unable to update model for user  due to: {e}")
    finally:
        cur.close()
        conn.close()
    
def delete_model_by_id(model_id):
    conn = dcu.get_db_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM models WHERE id = %s"
    vals = [model_id]
    try:
        cursor.execute(sql, vals)
        conn.commit()
    except Exception as e:
        logging.error(f'Unable to delete model {model_id} due to {e}')
    finally:
        conn.close()
        cursor.close()