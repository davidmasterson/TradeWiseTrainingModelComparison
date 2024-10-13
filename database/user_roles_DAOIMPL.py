from database import database_connection_utility as dcu
import logging 
from datetime import datetime


def create_user_roles_table(user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DROP TABLE IF EXISTS user_roles'''
    sql2 = '''CREATE TABLE user_roles(
            user_id INT NOT NULL,
            role_id INT NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id))'''
    try:
        cur.execute(sql)
        conn.commit()
        cur.execute(sql2)
        conn.commit()
        logging.info(f'{datetime.now()}: User {user_id} successfully created a new user roles table')
    except Exception as e:
        logging.error(f'{datetime.now()}: User {user_id} was unsuccessful in creating a new user roles table due to {e}')
    finally:
        conn.close()
        cur.close()

def get_user_role_id_by_role_name(name, requestor_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT id FROM user_roles
            WHERE role_name = %s'''
    vals = [name]
    try:
        cur.execute(sql, vals)
        role = cur.fetchone()
        if role:
            logging.info(f'{datetime.now()}: User {requestor_id} requested user roles ')
            return role[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: User {requestor_id} was unsuccessful at requesting user roles due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_user_role_id_by_user_id(user_id, requestor_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT id FROM user_roles
            WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        role = cur.fetchone()
        if role:
            logging.info(f'{datetime.now()}: User {requestor_id} requested user roles ')
            return role[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: User {requestor_id} was unsuccessful at requesting user roles due to {e}')
        return []
    finally:
        conn.close()
        cur.close()

def get_role_name_by_user_id(user_id, requestor_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''SELECT role_name FROM roles
            INNER JOIN roles ON user_roles.role_id = roles.id
            WHERE user_id = %s'''
    vals = [user_id]
    try:
        cur.execute(sql, vals)
        role = cur.fetchone()
        if role:
            logging.info(f'{datetime.now()}: User {requestor_id} requested user roles ')
            return role[0]
        return []
    except Exception as e:
        logging.error(f'{datetime.now()}: User {requestor_id} was unsuccessful at requesting user roles due to {e}')
        return []
    finally:
        conn.close()
        cur.close()
       
def insert_user_role(user_role, inserter_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''INSERT INTO user_roles(
            user_id,
            role_id)
            VALUES(
                %s,%s)'''
    vals = [
        user_role.user_id,
        user_role.role_id
    ]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f'{datetime.now()}: User {inserter_id} created a new user_role')
    except Exception as e:
        logging.error(f'{datetime.now()}: User {inserter_id} was unsuccessful at creating a new user_role for {user_role.user_id} due to {e}')
    finally:
        conn.close()
        cur.close()
        
def update_user_role(user_id, role_id, updater_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''UPDATE user_roles 
                INNER JOIN users ON
                users.id = user_roles.user_id
                SET user_roles.role_id = %s
                WHERE user_roles.user_id = %s
                '''
    sql2 = '''SELECT role_name from roles
                WHERE id = %s'''
    vals = [role_id, user_id]
    vals2 = [role_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        cur.execute(sql2, vals2)
        role_name = cur.fetchone()
        if role_name:
            role_name = role_name[0]
        logging.info(f'{datetime.now()}: {updater_id} successfully updated user {user_id} role to {role_name}')
    except Exception as e:
        logging.error(f'{datetime.now()}: User {updater_id} was unsuccessful when trying to update user {user_id} role to {role_name} due to {e}')
    finally:
        conn.close()
        cur.close()
        
def delete_user_role(user_role_id, deleter_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''DELETE FROM user_roles
            WHERE id = %s'''
    vals = [user_role_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
        logging.info(f'{datetime.now()} User {deleter_id} Deleted user role {user_role_id}')
        return True
    except Exception as e:
        logging.error(f'{datetime.now()} User {deleter_id} was unsuccessful at deleteing user role {user_role_id} due to {e}')
        return False
    finally:
        conn.close()
        cur.close()