import mysql.connector
from mysql.connector import Error
from os import getenv


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
            print("Connected to MySQL database")
        return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")


def get_aws_db_connection():
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host = getenv('AWSHOST'),
            database = getenv('AWSDB'),
            user = getenv('AWSDB_USER'),
            password = getenv('AWSDB_PASS')
        )

        if connection.is_connected():
            print("Connected to AWS MySQL database")
        return connection
    
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")