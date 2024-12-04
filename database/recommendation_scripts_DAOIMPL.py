from database import database_connection_utility as dcu
import logging
from datetime import datetime


def get_recommendation_scripts_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM recommendations_scripts WHERE user_id = %s'''
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

def get_recommendation_script_by_script_id(id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM recommendations_scripts WHERE id = %s'''
    vals = [id]
    try:
        cur.execute(sql,vals)
        scripts = cur.fetchall()
        if scripts:
            return scripts
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get scripts ({id}) due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def insert_recommendation_script_for_user(script):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO recommendations_scripts(
                name,
                description,
                script,
                user_id,
                updated)
                VALUES(%s,%s,%s,%s,%s)'''
    vals = [
        script.script_name,
        script.script_description,
        script.script,
        script.user_id,
        script.updated,
    ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, script {script.script_name} successfully inserted for user {script.user_id}")
        return cur.lastrowid
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert recommendations script {script.script_name} for user {script.user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()
        
def update_preprocessed_data_for_user(script_id,script_bin):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
        UPDATE preprocessing_scripts
        SET script = %s, upload_date = NOW()
        WHERE id = %s
    '''
    vals = [script_bin,script_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        print(f"Preprocessed data for {script_id} updated successfully.")
    except Exception as e:
        print(f"Error updating recommendations script data: {e}")
    finally:
        cur.close()
        conn.close()
        
def get_scripts_by_user_id(user_id):
    query = "SELECT * FROM recommendations_scripts WHERE user_id = %s"
    with dcu.get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            scripts = cursor.fetchall()
    return scripts
        
def delete_user_recommendations_script(script_row_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DELETE FROM recommendations_scripts
                WHERE id=%s'''
    vals = [script_row_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, script successfully removed")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to delete recommendation script due to : {e}')
    finally:
        cur.close()
        conn.close()