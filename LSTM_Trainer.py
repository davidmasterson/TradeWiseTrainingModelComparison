import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.api.models import Sequential
from keras.api.layers import LSTM, Dense

def train_lstm(data, update_progress, num_predictions=5):
    symbols = data['symbol'].unique()
    predictions = []
    total_steps = len(symbols) * 5  # Assuming 5 major steps per symbol
    current_step = 0

    for symbol in symbols:
        df = data[data['symbol'] == symbol]
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df['close'].values.reshape(-1, 1))
        train_size = int(len(scaled_data) * 0.8)
        train_data = scaled_data[:train_size]
        test_data = scaled_data[train_size:]

        def create_sequences(data, sequence_length):
            sequences = []
            for i in range(len(data) - sequence_length):
                sequences.append(data[i:i+sequence_length])
            return np.array(sequences)

        sequence_length = 60
        x_train = create_sequences(train_data, sequence_length)
        y_train = train_data[sequence_length:]
        x_test = create_sequences(test_data, sequence_length)
        y_test = test_data[sequence_length:]

        current_step += 1
        update_progress(current_step, total_steps)

        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(sequence_length, 1)))
        model.add(LSTM(units=50))
        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, epochs=10, batch_size=32)

        current_step += 1
        update_progress(current_step, total_steps)

        symbol_predictions = model.predict(x_test)
        
        current_step += 1
        update_progress(current_step, total_steps)
        
        # Take only the next num_predictions prices
        symbol_predictions = symbol_predictions[:num_predictions]
        print(symbol_predictions)
        predicted_prices = scaler.inverse_transform(symbol_predictions).flatten().tolist()
        print(predicted_prices)
        
        current_step += 1
        update_progress(current_step, total_steps)
        
        predictions.append({symbol: predicted_prices})

        current_step += 1
        update_progress(current_step, total_steps)
    
    return predictions
