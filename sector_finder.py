import yfinance as yf
import re

def get_stock_sector(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return info.get('sector', 'Sector not available')


def get_stock_company_name(symbol):
    stock = yf.Ticker(symbol)
    try:
        info = stock.info['shortName']
        types = ['Inc.','LLC.', 'DBA.']
        for type in types:
            if type in info:
                info = info.split()[0]
                break
        return info.lower()
    except Exception as e:
        return symbol.lower()

