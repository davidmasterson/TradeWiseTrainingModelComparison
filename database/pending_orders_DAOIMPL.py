from database import database_connection_utility as dcu
from datetime import datetime
import logging



def get_all_pending_orders(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM pending_orders
            WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        pending_orders = cur.fetchall()
        if pending_orders:
            return pending_orders
        return []
    except Exception as e:
         logging.info( f'{datetime.now()}:Unable to get pending orders for user {user_id} due to : {e}')
    finally:
        cur.close()
        conn.close()

def get_pending_order_by_client_order_id_and_user_id(client_order_id,user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM pending_orders
            WHERE user_id = %s AND client_order_id = %s'''
    vals = [user_id, client_order_id]
    try:
        cur.execute(sql, vals)
        pending_orders = cur.fetchone()
        if pending_orders:
            return pending_orders
        return []
    except Exception as e:
         logging.info( f'{datetime.now()}:Unable to get pending orders for user {user_id} with client order id {client_order_id} due to : {e}')
    finally:
        cur.close()
        conn.close()

def get_pending_sell_orders_by_user_id_and_client_order_id(user_id, client_order_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM pending_orders
            WHERE user_id = %s AND side=%s AND client_order_id = %s'''
    vals = [user_id, 'sell', client_order_id]
    try:
        cur.execute(sql, vals)
        pending_orders = cur.fetchone()
        if pending_orders:
            return pending_orders
        return []
    except Exception as e:
         logging.info( f'{datetime.now()}:Unable to get pending orders for user {user_id} with client order id {client_order_id} due to : {e}')
    finally:
        cur.close()
        conn.close()

def get_pending_buy_orders_by_user_id_and_client_order_id(user_id, client_order_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT * FROM pending_orders
            WHERE user_id = %s AND side=%s AND client_order_id=%s'''
    vals = [user_id, 'buy', client_order_id]
    try:
        cur.execute(sql, vals)
        pending_orders = cur.fetchone()
        if pending_orders:
            return pending_orders
        return []
    except Exception as e:
         logging.info( f'{datetime.now()}:Unable to get pending orders for user {user_id} with client order id {client_order_id} due to : {e}')
    finally:
        cur.close()
        conn.close()



def insert_pending_order(client_order_id, user_id,side,purchase_string = None, trans_id = None):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO pending_orders(
        client_order_id,
        user_id,
        side,
        purchase_string,
        trans_id)VALUES(%s,%s,%s,%s,%s)'''
    vals = [client_order_id,user_id,side, purchase_string, trans_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        poid = cur.lastrowid
        if side == 'buy':
            logging.info(f"{datetime.now()}:{cur.rowcount}, record inserted pending buy order :{client_order_id}")
            return poid
        elif side == 'sell':
            logging.info(f'{datetime.now()} pending sell order with id: {client_order_id} and purhase string {purchase_string}: for transaction: {trans_id} successfully entered.')
    except Exception as e:
        if side == 'buy':
            logging.exception( f'{datetime.now()}:Unable to insert pending order {client_order_id} due to : {e}')
        else:
            logging.exception( f'{datetime.now()}:Unable to insert pending sell order {client_order_id} for transaction {trans_id} due to : {e}')   
    finally:
        cur.close()
        conn.close()
        
def delete_pending_order_after_fill(id, side, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DELETE FROM pending_orders
            WHERE id = %s AND side = %s AND user_id = %s'''
    vals = [id, side, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f'{datetime.now()}: Pending {side} order {id} has been deleted for user {user_id} ')
    except Exception as e:
        logging.info(f'{datetime.now()}: Unable to delete Pending {side} order {id} for user {user_id} due to {e}')
        return None
    finally:
        conn.close()
        cur.close()


def truncate_pending_orders_at_eod():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''TRUNCATE table pending_orders'''
    try:
        cur.execute(sql)
        conn.commit()
        logging.info(f'{datetime.now()}: Pending orders have been deleted ')
    except Exception as e:
        logging.info(f'{datetime.now()}: Unable to delete Pending orders due to {e}')
        return None
    finally:
        cur.close()