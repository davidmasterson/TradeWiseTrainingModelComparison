from datetime import date


class DailyBalance:
    
    def __init__(self, dt, balance, user_id):
        self.dt = dt
        self.balance = balance
        self.user_id = user_id
        
        
    def set_balance(self, balance):
        self.balance = balance
        return self
    
    def set_date_and_balance(self, balance, new_date):
        self.balance = balance
        self.dt = new_date
        return self
    
    def get_balance(self):
        return self.balance
    
    def get_date(self):
        return self.dt
    
    def get_user_id(self):
        return self.user_id
        