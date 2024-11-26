from database import database_connection_utility as dcu
from datetime import datetime
import logging

def create_training_scripts_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DROP TABLE IF EXISTS training_scripts'''
    sql2 = '''CREATE TABLE training_scripts(
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_type VARCHAR(100) NOT NULL,
                script_name VARCHAR(100) NOT NULL,
                script_description VARCHAR(100) NOT NULL,
                script_data BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT NOT NULL)'''
    try:
        cur.execute(sql)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()}: User({user_id}) successfully created training scripts table')
    except Exception as e:
        logging.info(f'{datetime.now()}: User({user_id}) Unable to create training scripts table due to {e}')
        return None
    finally:
        conn.close()
        cur.close()
        
        
def select_training_scripts_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM training_scripts
            WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        scripts = cur.fetchall()
        if scripts:
            return scripts
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get training scripts for user {user_id} due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_all_training_scripts_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT id, model_type, script_name, script_data, script_description , created_at
        FROM training_scripts
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
        logging.error(f'{datetime.now()}: Unable to get training scripts for user {user_id} due to {e}')
    finally:
        cur.close()
        conn.close()

def select_training_script_by_id(script_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT script_data FROM training_scripts
            WHERE id = %s'''
    vals = [script_id]
    try:
        cur.execute(sql, vals)
        script = cur.fetchone()
        if script:
            return script[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get training script data due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
def get_training_script_data_by_id(training_script_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        SELECT script_data 
        FROM training_scripts
        WHERE id = %s
    '''
    try:
        cur.execute(sql, (training_script_id,))
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        cur.close()
        conn.close()

def insert_training_script(training_script):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO training_scripts(
            model_type,
            script_name,
            script_description,
            script_data,
            created_at,
            user_id)
            VALUES
            (%s,%s,%s,%s,%s,%s)'''
    vals = [
        training_script.model_type,
        training_script.script_name,
        training_script.script_description,
        training_script.script_data,
        training_script.created_at,
        training_script.user_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, training script {training_script.script_name} successfully inserted for user {training_script.user_id}")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert preprocessing script {training_script.script_name} for user {training_script.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()


def update_training_script(training_script,ts_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE training_scripts SET
            model_type = %s,
            script_name = %s,
            script_description = %s,
            script_data = %s,
            created_at = %s,
            user_id = %s
            WHERE id = %s'''
    vals = [
        training_script.model_type,
        training_script.script_name,
        training_script.script_description,
        training_script.script_data,
        training_script.created_at,
        training_script.user_id,
        ts_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, training script {training_script.script_name} successfully updated for user {training_script.user_id}")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to update preprocessing script {training_script.script_name} for user {training_script.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def delete_training_script(t_script_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        DELETE 
        FROM training_scripts
        WHERE id = %s
    '''
    vals = [t_script_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
    except Exception as e:
        logging.error(f'Unable to delete training script with id {t_script_id} due to {e}')
    finally:
        cur.close()
        conn.close()