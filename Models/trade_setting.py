import logging

class TradeSetting:
    
    def __init__(self, user_id, min_price, max_price, risk_tolerance, confidence_threshold, min_total, max_total):
        self.user_id = user_id
        self.min_price = min_price
        self.max_price = max_price
        self.risk_tolerance = risk_tolerance
        self.confidence_threshold = confidence_threshold
        self.min_total = min_total
        self.max_total = max_total