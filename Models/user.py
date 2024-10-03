
from flask import session
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