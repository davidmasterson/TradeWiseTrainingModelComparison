

class UserPreferences:
    
    
    def __init__(self, min_investment, max_investment, min_price_per_share, max_price_per_share, user_id, risk_tolerance):
        self.min_investment = min_investment
        self.max_investment = max_investment
        self.min_price_per_share = min_price_per_share
        self.max_price_per_share = max_price_per_share
        self.user_id = user_id
        self.risk_tolerance = risk_tolerance