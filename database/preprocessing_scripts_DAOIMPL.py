from database import database_connection_utility as dcu
from datetime import date, datetime
import logging


def create_preprocessing_scripts_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS preprocessing_scripts')
    conn.commit()
    sql =   ''' 
                CREATE TABLE preprocessing_scripts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                script_name VARCHAR(255) NOT NULL,
                script BLOB NOT NULL,
                user_id INT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                script_description VARCHAR(1000) NOT NULL,
                preprocessed_data LONGBLOB,
                CONSTRAINT preprocessing_scripts_users FOREIGN KEY (user_id) REFERENCES users(id)
                )
            '''
    
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f'{datetime.now()}: User({user_id}) successfully created preprocessing scripts table')
    except Exception as e:
        logging.info(f'{datetime.now()}: User({user_id}) Unable to create preprocessing scripts table due to {e}')
        return None
    finally:
        conn.close()
        cur.close()
        
def get_preprocessing_script_and_data_from_db(model_name, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT script_data, preprocessed_data FROM preprocessing_scripts
        INNER JOIN model_preprocessing_scripts ON preprocessing_scripts.id = model_preprocessing_scripts.preprocessing_script_id
        INNER JOIN models on model_preprocessing_scripts.model_id = model.id WHERE models.model_name = %s AND model.user_id = %s
    '''
    vals = [model_name, user_id]
    try:
        cur.execute(sql, vals)
        result = cur.fetchone()
        if result:
            result = result[0]
            script_content = result[0]
            preprocessed_data_binary = result[1]  # This could be None if not yet preprocessed
            return script_content, preprocessed_data_binary
        return None, None
    except Exception as e:
        logging.error(f"Error retrieving preprocessing script and data for {model_name}: {e}")
        return None, None
    finally:
        cur.close()
        conn.close()

def get_preprocessing_script_id_for_user_by_user_id_and_script_name(preprocessing_script):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT id
        FROM preprocessing_scripts
        WHERE user_id = %s AND script_name = %s
    '''
    vals = [preprocessing_script.user_id,
            preprocessing_script.script_name]
    try:
        cur.execute(sql, vals)
        results = cur.fetchone()
        if results:
            return results[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get preprocessed script id by script name {preprocessing_script.script_name} for user {preprocessing_script.user_id} due to {e}')
        return []
    finally:
        cur.close()
        conn.close()
                
def get_model_name_for_preprocessing_scripts_preprocessing_script_id(preprocessing_script_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT m.model_name FROM models AS m
        INNER JOIN model_preprocessing_scripts AS mps ON mps.model_id = m.id
        INNER JOIN preprocessing_scripts AS ps ON ps.id = mps.preprocessing_script_id
        WHERE ps.id = %s
    '''
    vals = [preprocessing_script_id]
    try:
        cur.execute(sql, vals)
        result = cur.fetchone()
        if result:
            return result[0]
        return None
    except Exception as e:
        logging.error(f"Error retrieving model name for preprocessing script {preprocessing_script_id}: due to {e}")
        return None
    finally:
        cur.close()
        conn.close()


        
def get_preprocessed_script_and_data_by_id(selected_preprocessing_script_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT script_data, preprocessed_data FROM preprocessing_scripts WHERE id = %s'''
    vals = [selected_preprocessing_script_id]
    try:
        cur.execute(sql, vals)
        datapresent = cur.fetchone()
        logging.info(f'{datetime.now()}: Datapresent {datapresent}')
        
        # Ensure function returns both script_data and preprocessed_data, even if one is None
        if datapresent:
            return datapresent[0], datapresent[1]  # Return both columns as a tuple
        return None, None  # Return None values if no data is found
    except Exception as e:
        logging.info(f'{datetime.now()}: Unable to get preprocessing script data and preprocessed data due to {e}')
        return None, None  # Ensure consistent return format
    finally:
        conn.close()
        cur.close()
        
def get_all_preprocessed_data_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT id, script_name, preprocessed_data, upload_date 
        FROM preprocessing_scripts
        WHERE user_id = %s
    '''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        results = cur.fetchall()
        if results:
            return results
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get preprocessed data for user {user_id} due to {e}')
        return []
    finally:
        cur.close()
        conn.close()
    
        
def get_preprocessing_script_names_and_dates_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT script_name, upload_date FROM preprocessing_scripts WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        script_names = cur.fetchall()
        if script_names:
            return script_names
        return []
    except Exception as e:
        logging.info(f'{datetime.now()}: Unable to get preprocessing script names for user({user_id}) due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_preprocessing_script_encrypted_fernet_key_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT encrypted_fernet_key FROM preprocessing_scripts WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        e_fernet_key = cur.fetchall()
        if e_fernet_key:
            return e_fernet_key
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get preprocessing script encrypted fernet key for user({user_id}) due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_encrypted_preprocessing_script_for_user(user_id, script_name):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT script FROM preprocessing_scripts WHERE user_id = %s and script_name=%s'''
    vals = [user_id, script_name]
    try:
        cur.execute(sql,vals)
        e_fernet_key = cur.fetchone()
        if e_fernet_key:
            return e_fernet_key
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get encrypted preprocessing script for user({user_id}) due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_preprocessing_scripts_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM preprocessing_scripts WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        scripts = cur.fetchall()
        if scripts:
            return scripts
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get scripts for user({user_id}) due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def insert_preprocessing_script_for_user(script):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO preprocessing_scripts(
                script_name,
                script_description,
                script_data,
                user_id,
                upload_date,
                preprocessed_data)
                VALUES(%s,%s,%s,%s,%s,%s)'''
    vals = [
        script.script_name,
        script.script_description,
        script.script_data,
        script.user_id,
        script.upload_date,
        script.preprocessed_data
    ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, script {script.script_name} successfully inserted for user {script.user_id}")
        return cur.lastrowid
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert preprocessing script {script.script_name} for user {script.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def update_preprocessed_data_for_user(script_name, user_id, preprocessed_data_binary):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        UPDATE preprocessing_scripts
        SET preprocessed_data = %s, upload_date = NOW()
        WHERE script_name = %s AND user_id = %s
    '''
    try:
        cur.execute(sql, (preprocessed_data_binary, script_name, user_id))
        conn.commit()
        print(f"Preprocessed data for {script_name} updated successfully.")
    except Exception as e:
        print(f"Error updating preprocessed data: {e}")
    finally:
        cur.close()
        conn.close()
        
def get_scripts_by_user_id(user_id):
    query = "SELECT * FROM preprocessing_scripts WHERE user_id = %s"
    with dcu.get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            scripts = cursor.fetchall()
    return scripts
        
def delete_user_preprocessing_script(script_row_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DELETE FROM preprocessing_scripts
                WHERE id=%s'''
    vals = [script_row_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, script successfully removed")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to delete preprocessing script due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def save_preprocessing_script_and_data_to_db(model_name, script_content, preprocessed_data_binary):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        INSERT INTO preprocessing_scripts (model_name, script_data, preprocessed_data)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE script_data = %s, preprocessed_data = %s
    '''
    try:
        cur.execute(sql, (model_name, script_content, preprocessed_data_binary, script_content, preprocessed_data_binary))
        conn.commit()
        logging.info(f"Preprocessing script and data for {model_name} saved successfully.")
    except Exception as e:
        logging.error(f"Error saving preprocessing script and data for {model_name}: {e}")
        raise e
    finally:
        cur.close()
        conn.close()