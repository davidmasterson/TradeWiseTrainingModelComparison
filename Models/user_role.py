from flask import session
from database import roles_DAOIMPL

class UserRole:
    
    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id
        
        
    def check_if_admin():
        user_id = session.get('user_id')
        user_role = roles_DAOIMPL.get_user_role_by_user_id(user_id)
        if user_role == 'admin':
            return True
        return False