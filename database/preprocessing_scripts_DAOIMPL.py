from database import database_connection_utility as dcu
from datetime import date, datetime
import logging


def create_preprocessing_scripts_table(user_id):
    conn = dcu.get_aws_db_connection()
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
                user_alias VARCHAR(25) NOT NULL,
                encrypted_fernet_key VARCHAR(1024),
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
        

        
def get_preprocessing_script_names_and_dates_for_user(user_id):
    conn = dcu.get_aws_db_connection()
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
    conn = dcu.get_aws_db_connection()
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
    conn = dcu.get_aws_db_connection()
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
        
        
def insert_preprocessing_script_for_user(script):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO preprocessing_scripts(
                script_name,
                script,
                user_id,
                upload_date,
                script_description,
                user_alias,
                encrypted_fernet_key)
                VALUES(%s,%s,%s,%s,%s,%s,%s)'''
    vals = [
        script.script_name,
        script.script,
        script.user_id,
        script.upload_date,
        script.script_description,
        script.user_alias,
        script.encrypted_fernet_key
    ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, script {script.script_name} successfully inserted for user {script.user_id}")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert preprocessing script {script.script_name} for user {script.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def update_preprocessing_script_row_for_user(preprocessing_script):
    conn = dcu.get_aws_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE preprocessing_scripts SET
                encrypted_fernet_key = %s
                WHERE user_id = %s'''
    vals = [preprocessing_script.encrypted_fernet_key, 
            preprocessing_script.user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, script {preprocessing_script.script_name} successfully updated for user {preprocessing_script.user_id}")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to update preprocessing script {preprocessing_script.script_name} for user {preprocessing_script.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def delete_user_preprocessing_script(script_row_id):
    conn = dcu.get_aws_db_connection()
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