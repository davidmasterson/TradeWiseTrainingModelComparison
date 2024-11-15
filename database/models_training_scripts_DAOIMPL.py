from database import database_connection_utility as dcu
from datetime import datetime
import logging

def create_models_training_scripts_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS models_training_scripts''')
    conn.commit()
    sql = '''CREATE TABLE models_training_scripts(
            model_id INT PRIMARY KEY,
            training_script_id INT PRIMARY KEY,
            FOREIGN KEY (model_id) REFERENCES models(id),
            FOREIGN KEY (training_script_id) REFERENCES training_scripts(id))'''
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f'{datetime.now()}: User({user_id}) successfully created models_training_scripts union table')
    except Exception as e:
        logging.info(f'{datetime.now()}: User({user_id}) Unable to create models_training_scripts union table due to {e}')
        return None
    finally:
        conn.close()
        cur.close()
        
def get_model_name_by_training_script_id(trainscript_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT model_name as mn FROM models_training_scripts AS mts
                INNER JOIN models ON mts.model_id = models.id
                WHERE mts.training_script_id = %s'''
    vals = [trainscript_id]           
    try:
        cur.execute(sql, vals)
        name = cur.fetchone()
        if name:
            return name[0]
        return []
    except Exception as e:
        return []
    finally:
        conn.close()
        cur.close()
        
def get_entry_by_model_id(model_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * from models_training_scripts WHERE model_id = %s'''
    vals = [
        model_id
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
        
def insert_into_models_training_scripts_table(model_ts_object):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO models_training_scripts(
                model_id,
                training_script_id)
                VALUES(
                    %s,%s)'''
    vals = [
        model_ts_object.model_id,
        model_ts_object.training_script_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, model training script object successfully inserted ")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert models training script object due to : {e}')
    finally:
        cur.close()
        conn.close()
        
        
def update_models_training_script_table(model_ts_object):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE models_training_scripts SET
                model_id = %s,
                training_script_id = %s
                WHERE model_id=%s'''
    vals = [
        model_ts_object.model_id,
        model_ts_object.training_script_id,
        model_ts_object.model_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, models training script successfully updated")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to update models training script due to : {e}')
    finally:
        cur.close()
        conn.close()
        