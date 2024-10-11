
import bcrypt
import logging

class User:

    def __init__(self, first,last,user_name,password,email,alpaca_key, alpaca_secret):
        self.first = first
        self.last = last
        self.user_name = user_name
        self.password = password
        self.email = email
        self.alpaca_key = alpaca_key
        self.alpaca_secret = alpaca_secret
        
        
    def check_logged_in(session=None):
        logging.info(session)
        if session.get('logged_in'):
            return True
        return False
    
    # Password hashing function
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password