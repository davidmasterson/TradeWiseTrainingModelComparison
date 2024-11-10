from database import database_connection_utility as dcu
from datetime import datetime
import logging

def get_all_metrics_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = 'SELECT * FROM metrics WHERE user_id = %s'
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_metrics_dates_by_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT date_of_metric FROM metrics WHERE user_id=%s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_accuracies_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT accuracy FROM metrics WHERE user_id=%s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_error_rates_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT error_rate FROM metrics WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_cumlative_correct_predictions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_correct_pred FROM metrics WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_cumlative_incorrect_predictions_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_incorrect_pred FROM metrics WHERE user_id = %s'''
    vals = [user_id]
    
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_times_to_close_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT time_to_close_correct_pred FROM metrics WHERE user_id = %s'''
    vals = [user_id]
    
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_cumlative_profits_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_profit FROM metrics WHERE user_id = %s'''
    vals = [user_id]
    
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metrics_cumlative_losses_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_loss FROM metrics WHERE user_id = %s'''
    vals = [user_id]
    
    try:
        cur.execute(sql, vals)
        dates = cur.fetchall()
        if dates:
            return dates
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        conn.close()
        cur.close()

def get_metric_by_date_by_user(date,user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM metrics WHERE str_to_date(date_of_metric,'%Y-%m-%d') = %s and user_id = %s"
    vals = [date,user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.info(e)
        return []
    finally:
        cur.close()
        conn.close()

def get_metrics_by_user_id(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM metrics WHERE user_id = %s"
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.info(f'unable to get metrics for user: {user_id} due to: {e}')
        return []
    finally:
        cur.close()
        conn.close()

def get_last_sector_breakdown_profit_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT sector_bd_profit FROM metrics WHERE user_id = %s ORDER BY id DESC limit 1 "
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchone()
        if metrics:
            return metrics
        return {}
    except Exception as e:
        logging.info(e)
        return {}
    finally:
        cur.close()
        conn.close()

def get_last_metric_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM metrics WHERE user_id=%s ORDER BY id DESC limit 1"
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        metrics = cur.fetchone()
        if metrics:
            return metrics
        return {}
    except Exception as e:
        logging.info(e)
        return {}
    finally:
        cur.close()
        conn.close()

def get_last_sector_breakdown_loss_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT sector_bd_loss FROM metrics WHERE user_id = %s ORDER BY id DESC limit 1 "
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchone()
        if metrics:
            return metrics
        return {}
    except Exception as e:
        logging.info(e)
        return {}
    finally:
        cur.close()
        conn.close()

def get_all_last_sector_breakdowns_for_user(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT 
            sector_bd_profit,
            sector_bd_loss
            FROM metrics 
            WHERE user_id=%s
            ORDER BY id 
            DESC 
            limit 1 
            '''
    vals = [user_id]
    try:
        cur.execute(sql,vals)
        metrics = cur.fetchone()
        if metrics:
            return metrics
        return [{},{}]
    except Exception as e:
        logging.info(e)
        return [{},{}]
    finally:
        cur.close()
        conn.close()



def insert_metric(metric):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT into metrics
            (
                accuracy,
                error_rate,
                cumulative_correct_pred,
                cumulative_incorrect_pred,
                time_to_close_correct_pred,
                cumulative_profit,
                cumulative_loss,
                sector_bd_profit,
                sector_bd_loss,
                date_of_metric,
                user_id) VALUES (
                %s,%s,%s,%s,
                %s,%s,%s,%s,
                %s,%s,%s,%s,%s)
                '''
    vals = [metric.accuracy,
            metric.error_rate,
            metric.cumulative_correct_predictions,
            metric.cumulative_incorrect_predictions,
            metric.time_to_close_correct_predictions,
            metric.cumulative_profit,
            metric.cumulative_loss,
            metric.sector_breakdown_profit,
            metric.sector_breakdown_loss,
            metric.date,
            metric.user_id]
    try:
        cur.execute(sql,vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected inserted transaction {datetime.now()}")
        else:
            logging.info(f"{datetime.now()}:No record has not been inserted.")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()


def update_metric(metric, id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE metrics SET 
                accuracy = %s,
                error_rate = %s,
                cumulative_correct_pred = %s,
                cumulative_incorrect_pred = %s,
                time_to_close_correct_pred = %s,
                cumulative_profit = %s,
                cumulative_loss = %s,
                sector_bd_profit = %s,
                sector_bd_loss = %s,
                date_of_metric = %s,
                user_id = %s
                WHERE
                id = %s'''
    vals = [metric.accuracy,
            metric.error_rate,
            metric.cumulative_correct_predictions,
            metric.cumulative_incorrect_predictions,
            metric.time_to_close_correct_predictions,
            metric.cumulative_profit,
            metric.cumulative_loss,
            metric.sector_breakdown_profit,
            metric.sector_breakdown_loss,
            metric.date,
            metric.user_id,
            id[0]]
    try:
        cur.execute(sql, vals)
        conn.commit()
        if cur.rowcount > 0:
            logging.info(f"{cur.rowcount}, record(s) affected updated transaction {datetime.now()}")
        else:
            logging.info(f"{datetime.now()}:No record has not been updated.")
    except Exception as e:
        return e
    finally:
        cur.close()
        conn.close()