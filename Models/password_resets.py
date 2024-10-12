import bcrypt
import secrets
from datetime import datetime, timedelta
from database import reset_password_DAOIMPL

class PasswordResets:
    
    def __init__(self, user_id, token, expiration_time, hashed_token):
        self.user_id = user_id
        self.token = token
        self.expiration_time = expiration_time
        self.hashed_token = hashed_token
        
        
    def create_reset_token(self, user_id):
        token = secrets.token_urlsafe(32)
        hashed_token = bcrypt.hashpw(token.encode(), bcrypt.gensalt())
        expiration_time = datetime.now() + timedelta(minutes=15)
        new_token = PasswordResets(user_id,token, expiration_time, hashed_token)
        return_token = reset_password_DAOIMPL.insert_password_reset_token(new_token)
        return return_token
    
    def validate_token(self, user_id, provided_token):
        result = reset_password_DAOIMPL.get_hashed_token_and_expiration_for_user(user_id)
        if not result:
            return False #token not found
        hashed_token, expiration_time = result
        if datetime.now() > expiration_time:
            return False #token has expired
        #verify hashed token with provided token
        if bcrypt.checkpw(provided_token.encode(), hashed_token.encode()):
            return True #token valid
        else:
            return False #token is invalid
        
    def invalidate_password_reset_token(self, user_id):
        #Delete reset token once password is reset
        reset_password_DAOIMPL.delete_user_password_reset_token(user_id)
        
        
        
        
    