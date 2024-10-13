from database import database_connection_utility as dcu
from datetime import datetime
import logging

def create_roles_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DROP TABLE IF EXISTS roles'''
    sql2 = '''CREATE TABLE roles(
                id INT AUTO_INCREMENT PRIMARY KEY,
                role_name VARCHAR(50) NOT NULL)'''
    try:
        cur.execute(sql)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()}: User {user_id} successfully created new roles table')
    except Exception as e:
        logging.error(f'{datetime.now()}: User {user_id} tried to create a new roles table but was unccessful due to {e}')
    finally:
        conn.close()
        cur.close()
        
def get_all_roles(requestor_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT role_name FROM roles
            '''
    try:
        cur.execute(sql)
        role = cur.fetchall()
        if role:
            logging.info(f'{datetime.now()}: User {requestor_id} successfully retrieved all user roles.')
            return role
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: User {requestor_id} Unable to get all role name  due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_user_role_by_user_id(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT role_name FROM roles
                JOIN user_roles ON
            user_roles.role_id = roles.id
            WHERE user_roles.user_id = %s
            '''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        role = cur.fetchone()
        if role:
            return role[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: Unable to get user role by user is {user_id} due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_role_id_by_role_name(role_name, requestor_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT id FROM roles
                WHERE role_name = %s
            '''
    vals = [role_name]
    try:
        cur.execute(sql, vals)
        role = cur.fetchone()
        if role:
            logging.info(f'{datetime.now()}: User {requestor_id} successfully retrieved role id for role name {role_name}')
            return role[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: User {requestor_id} Unable to get role id by user role name {role_name} due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
        
        
def get_all_users_and_roles(requestor_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT users.id, users.user_name, users.email,
            GROUP_CONCAT(roles.role_name) as roles
            FROM users
            JOIN user_roles ON users.id=user_roles.user_id
            JOIN roles ON user_roles.role_id = roles.id
            GROUP BY users.id, users.user_name, users.email'''
    try:
        cur.execute(sql)
        users = cur.fetchall()
        if users:
            return users
        logging.info(f'{datetime.now()}: User {requestor_id} successfully retrieved user roles for all users')
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: User {requestor_id} was unsuccessful in retrieving all roles for users due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
            
def insert_role(role, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO roles(
                role_name)
                VALUES(%s)'''
    vals = [
        role.role_name
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f'{datetime.now()}: Role {role.role_name} successfully entered into database')
    except Exception as e:
        logging.error(f'{datetime.now()}: User {user_id} was unsuccessful in inserting role {role.role_name} into roles table due to {e}')    
    finally:
        conn.close()
        cur.close()
        
