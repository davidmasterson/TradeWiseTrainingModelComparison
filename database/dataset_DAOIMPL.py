from database import database_connection_utility as dcu
from datetime import datetime
import logging



def get_datasets_by_user_id(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM datasets
            WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        datasets = cur.fetchall()
        if datasets:
            return datasets
        return []
    except Exception as e:
         logging.info( f'{datetime.now()}:Unable to get datasets for user {user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()

def get_dataset_data_by_id(dataset_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT dataset_data FROM datasets
            WHERE id = %s'''
    vals = [dataset_id]
    try:
        cur.execute(sql, vals)
        dataset = cur.fetchone()
        if dataset:
            return dataset[0]
        return []
    except Exception as e:
         logging.info( f'{datetime.now()}:Unable to get dataset {dataset_id} due to : {e}')
    finally:
        cur.close()
        conn.close()

def insert_dataset(dataset):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO datasets(
                dataset_name,
                dataset_description,
                dataset_data,
                uploaded_at,
                user_id)
                VALUES(
                    %s,%s,%s,%s,%s)'''
    vals = [
        dataset.dataset_name,
        dataset.dataset_description,
        dataset.dataset_data,
        dataset.uploaded_at,
        dataset.user_id
    ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, dataset object successfully inserted ")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to insert dataset object due to : {e}')
    finally:
        cur.close()
        conn.close()


def update_dataset(dataset, dataset_id):
    import json
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE datasets SET
                dataset_name = %s,
                dataset_description = %s,
                dataset_data = %s,
                uploaded_at = %s,
                user_id = %s
                WHERE id = %s'''
    vals = [
        dataset.dataset_name,
        dataset.dataset_description,
        dataset.dataset_data,
        dataset.uploaded_at,
        dataset.user_id,
        dataset_id
    ]
    try:
        cur.execute(sql,vals)
        conn.commit()
        logging.info(f"{datetime.now()}:{cur.rowcount}, dataset object successfully updated {dataset.datset_name} ")
    except Exception as e:
        logging.error( f'{datetime.now()}:Unable to update dataset object {dataset.dataset_name} due to : {e}')
    finally:
        cur.close()
        conn.close()