import logging

class TradeSetting:
    
    def __init__(self, user_id, min_price, max_price, risk_tolerance, confidence_threshold):
        self.user_id = user_id
        self.min_price = min_price
        self.max_price = max_price
        self.risk_tolerance = risk_tolerance
        self.confidence_threshold = confidence_threshold