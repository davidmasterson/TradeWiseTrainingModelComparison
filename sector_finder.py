import yfinance as yf

def get_stock_sector(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return info.get('sector', 'Sector not available')

