from datetime import timedelta, date

import yfinance as yf

# Fetch historical data for the S&P 500
def get_s_and_p_value_on_specific_date(date):
    sp500 = yf.Ticker("^GSPC")
    
    for i in range(0, 8):
        adjusted_date = date - timedelta(days=i)
        next_day = adjusted_date + timedelta(days=1)
        
        # Fetch historical data for the adjusted date
        historical_data = sp500.history(start=adjusted_date.strftime("%Y-%m-%d"), end=next_day.strftime("%Y-%m-%d"))
        
        # Check if we have any data returned
        if not historical_data.empty:
            # Return the closing price of the adjusted date
            return round(historical_data['Close'].iloc[0],2)

def get_vanguard_value_on_specific_date(date):
    sp500 = yf.Ticker("VTSAX")
    
    for i in range(0, 8):
        adjusted_date = date - timedelta(days=i)
        next_day = adjusted_date + timedelta(days=1)
        
        # Fetch historical data for the adjusted date
        historical_data = sp500.history(start=adjusted_date.strftime("%Y-%m-%d"), end=next_day.strftime("%Y-%m-%d"))
        
        # Check if we have any data returned
        if not historical_data.empty:
            # Return the closing price of the adjusted date
            return round(historical_data['Close'].iloc[0],2)

def get_open_and_close_for_s_and_p_value_now(date = date.today()):
    sp500 = yf.Ticker("^GSPC")
    
    for i in range(0, 8):
        adjusted_date = date - timedelta(days=i)
        next_day = adjusted_date + timedelta(days=1)
        
        # Fetch historical data for the adjusted date
        historical_data = sp500.history(start=adjusted_date.strftime("%Y-%m-%d"), end=next_day.strftime("%Y-%m-%d"))
        
        # Check if we have any data returned
        if not historical_data.empty:
            # Return the closing price of the adjusted date
            return [round(historical_data['Open'].iloc[0],2),round(historical_data['Close'].iloc[0],2)]
    
    # If no data is found, return None or handle the case accordingly
    return None
def get_open_and_close_for_NASDAQ_value_now(date = date.today()):
    nasdaq = yf.Ticker("^IXIC")
    
    for i in range(0, 8):
        adjusted_date = date - timedelta(days=i)
        next_day = adjusted_date + timedelta(days=1)
        
        # Fetch historical data for the adjusted date
        historical_data = nasdaq.history(start=adjusted_date.strftime("%Y-%m-%d"), end=next_day.strftime("%Y-%m-%d"))
        
        # Check if we have any data returned
        if not historical_data.empty:
            # Return the closing price of the adjusted date
            return [round(historical_data['Open'].iloc[0],2),round(historical_data['Close'].iloc[0],2)]
    
    # If no data is found, return None or handle the case accordingly
    return None
def get_open_and_close_for_NYSE_value_now(date = date.today()):
    nyse = yf.Ticker("^NYA")
    
    for i in range(0, 8):
        adjusted_date = date - timedelta(days=i)
        next_day = adjusted_date + timedelta(days=1)
        
        # Fetch historical data for the adjusted date
        historical_data = nyse.history(start=adjusted_date.strftime("%Y-%m-%d"), end=next_day.strftime("%Y-%m-%d"))
        
        # Check if we have any data returned
        if not historical_data.empty:
            # Return the closing price of the adjusted date
            return [round(historical_data['Open'].iloc[0],2),round(historical_data['Close'].iloc[0],2)]
    
    # If no data is found, return None or handle the case accordingly
    return None

