from sector_finder import get_stock_sector


class Recommended:
    
    
    def __init__(self, symbol, price, confidence, user_id):
        self.symbol = symbol
        self.price = price
        self. confidence = confidence
        self.user_id = user_id
        self.sector = get_stock_sector(symbol)