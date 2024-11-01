from database import database_connection_utility as dcu
from datetime import datetime
import logging

def create_models_preprocessing_scripts_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS models_preprocessing_scripts''')
    conn.commit()
    sql = '''CREATE TABLE models_preprocessing_scripts(
            model_id INT PRIMARY KEY,
            preprocessing_script_id INT PRIMARY KEY,
            FOREIGN KEY (model_id) REFERENCES models(id),
            FOREIGN KEY (preprocessing_script_id) REFERENCES preprocessing_scripts(id))'''
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f'{datetime.now()}: User({user_id}) successfully created models_preprocessing_scripts union table')
    except Exception as e:
        logging.info(f'{datetime.now()}: User({user_id}) Unable to create models_preprocessing_scripts union table due to {e}')
        return None
    finally:
        conn.close()
        cur.close()
        
def get_model_id_by_pp_script_id(pp_script_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT model_id from model_preprocessing_scripts WHERE preprocessing_script_id = %s'''
    vals = [
        pp_script_id
    ]
    try:
        cur.execute(sql, vals)
        model_id = cur.fetchone()
        if model_id:
            return model_id[0]
        return []
    except Exception as e:
        logging.error( f'{datetime.now()}: Unable to get model id due to {e}')
    finally:
        cur.close()
        conn.close()
        
def insert_into_models_preprocessing_scripts_table(model_ps_object):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO models_preprocessing_scripts(
                model_id,
                preprocessing_script_id)
                VALUES(
                    %s,%s)'''
    vals = [
        model_ps_object.model_id,
        model_ps_object.preprocessing_script_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, model preprocessing script object successfully inserted ")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert models preprocessing script object due to : {e}')
    finally:
        cur.close()
        conn.close()
        
        
def update_models_preprocessing_script_table(model_ps_object):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE models_preprocessing_scripts SET
                models_id = %s,
                preprocessing_script_id = %s'''
    vals = [
        model_ps_object.model_id,
        model_ps_object.preprocessing_script_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, models preprocessing script successfully updated")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to update models preprocessing script due to : {e}')
    finally:
        cur.close()
        conn.close()
        