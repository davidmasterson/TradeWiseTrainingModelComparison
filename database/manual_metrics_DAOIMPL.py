from database import database_connection_utility as dcu
from datetime import datetime
import logging

def get_all_metrics():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = 'SELECT * FROM manual_metrics'
    try:
        cur.execute(sql)
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

def get_metrics_dates():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT date FROM manual_metrics'''
    try:
        cur.execute(sql)
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

def get_manual_metrics_accuracies():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT accuracy FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_manual_metrics_error_rates():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT error_rate FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_manual_metrics_cumlative_correct_predictions():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_correct_predictions FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_manual_metrics_cumlative_incorrect_predictions():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_incorrect_predictions FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_manual_metrics_times_to_close():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT time_to_close_correct_predictions FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_manual_metrics_cumlative_profits():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_profit FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_manual_metrics_cumlative_losses():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT cumulative_loss FROM manual_metrics'''
    
    try:
        cur.execute(sql)
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

def get_metric_by_date(date):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM manual_metrics WHERE date = %s"
    vals = [date]
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
    sql = "SELECT * FROM manual_metrics WHERE user_id = %s"
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        metrics = cur.fetchall()
        if metrics:
            return metrics
        return []
    except Exception as e:
        logging.info(f'unable to get manual_metrics for user: {user_id} due to: {e}')
        return []
    finally:
        cur.close()
        conn.close()

def get_last_sector_breakdown_profit():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT sector_breakdown_profit FROM manual_metrics ORDER BY id DESC limit 1 "
    try:
        cur.execute(sql)
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

def get_last_sector_breakdown_loss():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT sector_breakdown_loss FROM manual_metrics ORDER BY id DESC limit 1 "
    try:
        cur.execute(sql)
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

def get_last_sector_breakdown_rec():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = "SELECT sector_breakdown_rec FROM manual_metrics ORDER BY id DESC limit 1 "
    try:
        cur.execute(sql)
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

def get_all_last_sector_breakdowns():
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT 
            sector_breakdown_profit,
            sector_breakdown_loss,
            sector_breakdown_rec
            FROM manual_metrics 
            ORDER BY id 
            DESC 
            limit 1 
            '''
    try:
        cur.execute(sql)
        metrics = cur.fetchone()
        if metrics:
            return metrics
        return [{},{},{},{}]
    except Exception as e:
        logging.info(e)
        return [{},{},{},{}]
    finally:
        cur.close()
        conn.close()

def insert_metric(metric):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT into manual_metrics
            (
                accuracy,
                error_rate,
                cumulative_correct_predictions,
                cumulative_incorrect_predictions,
                time_to_close_correct_predictions,
                cumulative_profit,
                cumulative_loss,
                sector_breakdown_profit,
                sector_breakdown_loss,
                sector_breakdown_rec,
                date,
                user_id) VALUES (
                %s,%s,%s,%s,
                %s,%s,%s,%s,
                %s,%s,%s,%s)
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
            metric.sector_breakdown_rec,
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
    sql = '''UPDATE manual_metrics SET 
                accuracy = %s,
                error_rate = %s,
                cumulative_correct_predictions = %s,
                cumulative_incorrect_predictions = %s,
                time_to_close_correct_predictions = %s,
                cumulative_profit = %s,
                cumulative_loss = %s,
                sector_breakdown_profit = %s,
                sector_breakdown_loss = %s,
                sector_breakdown_rec = %s,
                date = %s,
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
            metric.sector_breakdown_rec,
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