import mysql.connector
from mysql.connector import Error
from os import getenv
import logging

def get_db_connection():
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host= getenv('HOST'),  # or '127.0.0.1'
            database= getenv('DB'),
            user= getenv('DB_USER'),
            password= getenv('DB_PASS')
        )
        
        if connection.is_connected():
            logging.info("Connected to MySQL database")
        return connection

    except Error as e:
        logging.info(f"Error while connecting to MySQL: {e}")


def get_aws_db_connection(db = 'fsproject'):
    logging.info(getenv('AWSHOST'))
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host = getenv('AWSHOST'),
            user = getenv('AWSDB_USER'),
            password = getenv('AWSDB_PASS'),
            database = db
        )

        if connection.is_connected():
            logging.info("Connected to AWS MySQL database")
        return connection
    
    except Error as e:
        logging.info(f"Error while connecting to MySQL: {e}")
        


def create_database(db_name):
    conn = get_aws_db_connection()
    cur = conn.cursor()
    sql = f'CREATE DATABASE IF NOT EXISTS `{db_name}`'  # Use f-string for dynamic SQL
    try:
        cur.execute(sql)
        logging.info(f"Database {db_name} has been created successfully")
    except Error as e:
        logging.info(f'Unable to create database {db_name} due to {e}')
    finally:
        cur.close()  # Close cursor before closing the connection
        conn.close()  # Close connection last
        
def create_initial_tables():
    try:
        conn = get_aws_db_connection()
        cur = conn.cursor()

        # SQL script containing the CREATE TABLE statements
        sql_script = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT,
            first VARCHAR(50) NOT NULL,
            last VARCHAR(50) NOT NULL,
            user_name VARCHAR(13) NOT NULL,
            password VARCHAR(100) NOT NULL,
            alpaca_key VARCHAR(150),
            alpaca_secret VARCHAR(150),
            PRIMARY KEY (id)
        );

        CREATE TABLE IF NOT EXISTS metrics(
            id INT AUTO_INCREMENT,
            accuracy DECIMAL(10,2),
            error_rate DECIMAL(10,2),
            cumulative_correct_pred INT,
            cumulative_incorrect_pred INT,
            time_to_close_correct_pred INT,
            cumulative_profit DECIMAL(10,2),
            cumulative_loss DECIMAL(10,2),
            sector_bd_profit JSON,
            sector_bd_loss JSON,
            sector_bd_rec JSON,
            sector_bd_nrec JSON,
            date_of_metric DATE,
            user_id INT,
            PRIMARY KEY (id),
            CONSTRAINT users_metrics FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS manual_metrics(
            id INT AUTO_INCREMENT,
            accuracy DECIMAL(10,2),
            error_rate DECIMAL(10,2),
            cumulative_correct_pred INT,
            cumulative_incorrect_pred INT,
            time_to_close_correct_pred INT,
            cumulative_profit DECIMAL(10,2),
            cumulative_loss DECIMAL(10,2),
            sector_bd_profit JSON,
            sector_bd_loss JSON,
            sector_bd_rec JSON,
            date_of_metric DATE,
            user_id INT,
            PRIMARY KEY (id),
            CONSTRAINT users_manual_metrics FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS transactions(
            id INT AUTO_INCREMENT,
            symbol VARCHAR(50) NOT NULL,
            dp VARCHAR(50) NOT NULL,
            ppps DECIMAL(10,2) NOT NULL,
            qty INT NOT NULL,
            total_buy DECIMAL(10,2) NOT NULL,
            pstring VARCHAR(100) NOT NULL,
            ds VARCHAR(50),
            spps DECIMAL(10,2),
            tsp DECIMAL(10,2),
            sstring VARCHAR(100),
            expected DECIMAL(10,2) NOT NULL,
            proi DECIMAL(10,2),
            actual DECIMAL(10,2),
            tp1 DECIMAL(10,2) NOT NULL,
            sop DECIMAL(10,2) NOT NULL,
            prediction INT NOT NULL,
            result INT,
            user_id INT,
            PRIMARY KEY (id),
            CONSTRAINT users_transactions FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS user_preferences(
            id INT AUTO_INCREMENT,
            min_pps DECIMAL(10,2) NOT NULL,
            max_pps DECIMAL(10,2) NOT NULL,
            min_inv_per_sym DECIMAL(10,2) NOT NULL,
            max_inv_per_sym DECIMAL(10,2) NOT NULL,
            user_id INT,
            PRIMARY KEY (id),
            CONSTRAINT users_users_preferences FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """

        # Split the SQL script into individual statements
        sql_statements = sql_script.strip().split(';')

        # Execute each SQL statement
        for statement in sql_statements:
            if statement.strip():  # Ensure it's not an empty statement
                cur.execute(statement)

        logging.info("Tables created successfully")
    except Error as e:
        logging.info(f"Error: {e}")
    finally:
        if cur:
            cur.close()  # Close cursor
        if conn:
            conn.close()  # Close connection

def show_tables():
    conn = get_aws_db_connection()
    cur = conn.cursor()
    sql = '''SHOW TABLES'''
    try:
        cur.execute(sql)
        tables = cur.fetchall()
        if tables:
            return tables
        return None
    except Exception as e:
        return e
    finally:
        conn.close()
        cur.close()

def show_table_columns(table):
    conn = get_aws_db_connection()
    cur = conn.cursor()
    sql = f"SHOW COLUMNS FROM `{table}`"
    try:
        cur.execute(sql)
        description = cur.fetchall()
        if description:
            return description
        return None
    except Exception as e:
        return e
    finally:
        conn.close()
        cur.close()

def alter_table_columns():
    conn = get_aws_db_connection()
    cur = conn.cursor()
    sql = f"ALTER TABLE user_preferences ADD COLUMN risk_tolerance ENUM('safe','moderate','risky') NOT NULL"
    try:
        cur.execute(sql)
    except Exception as e:
        return e
    finally:
        conn.close()
        cur.close()

def truncate_table_columns(table):
    conn = get_aws_db_connection()
    cur = conn.cursor()
    sql = f"DELETE FROM {table}"
    sql2 = f"ALTER TABLE {table} AUTO_INCREMENT=1"
    try:
        cur.execute(sql)
        conn.commit()
        # cur.execute(sql2)
        # conn.commit()
    except Exception as e:
        logging.info(e)
    finally:
        conn.close()
        cur.close()
        
        
