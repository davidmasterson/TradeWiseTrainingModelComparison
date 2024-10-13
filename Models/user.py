
import bcrypt
import logging
from database import user_DAOIMPL, roles_DAOIMPL
from flask import session


class User(): # Inherit from flask UserMixin class for authentication and session management

    def __init__(self, first,last,user_name,password,email,alpaca_key, alpaca_secret):
        self.first = first
        self.last = last
        self.user_name = user_name
        self.password = password
        self.email = email
        self.alpaca_key = alpaca_key
        self.alpaca_secret = alpaca_secret
        
        
    def check_logged_in():
        logging.info(session)
        if session.get('logged_in'):
            return True
        return False
    
    # Password hashing function
    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password
    
    def get_current_user_role():
        if User.check():
            user_id = session.get('user_id')
            current_user_role = roles_DAOIMPL.get_user_role_by_user_id(user_id)
            if current_user_role:
                return current_user_role
        return None
    
    def get_id():
        if User.check_logged_in():
            id = session.get('user_id')
            if id:
                return id
        return None