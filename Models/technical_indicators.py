from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd


def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

def calculate_momentum(data, period=14):
    return data.diff(period)

def prepare_data_with_indicators_and_target(df, time_steps, target_horizon=12, target_increase=0.05):
    # Calculate indicators
    df['RSI'] = calculate_rsi(df['close'], 14)
    df['SMA'] = calculate_sma(df['close'], 20)
    df['EMA'] = calculate_ema(df['close'], 20)
    df['Momentum'] = calculate_momentum(df['close'], 10)
    
    # Ensure no NaN values after indicator calculations
    df.fillna(0, inplace=True)
    
    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[['open', 'high', 'low', 'close', 'volume', 'RSI', 'SMA', 'EMA', 'Momentum']])
    
    X, y = [], []
    
    # Prepare sequences and target (whether price will hit the target in 12 days)
    for i in range(time_steps, len(scaled_data) - target_horizon):
        # Prepare the input sequence
        X.append(scaled_data[i-time_steps:i])
        
        # Calculate the target price based on the current close price + expected increase
        target_price = scaled_data[i, 3] * (1 + target_increase)
        
        # Check if the max future price within the next 'target_horizon' days hits the target
        future_max_price = np.max(scaled_data[i:i + target_horizon, 3])  # Column 3 is 'close' price
        y.append(1 if future_max_price >= target_price else 0)
    
    X, y = np.array(X), np.array(y)
    
    return X, y, scaler

