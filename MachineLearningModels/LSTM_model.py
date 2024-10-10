from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

# TensorFlow Keras imports


from tf.keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping

# Data Preparation: X (features), y (target)
def prepare_data(df, target_column, time_steps):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df)

    X, y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i-time_steps:i])
        y.append(scaled_data[i, target_column])
        
    X, y = np.array(X), np.array(y)
    return X, y, scaler

# Build the LSTM Model
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(input_shape[1], input_shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))  # Predict the stock price
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Train the LSTM model
def train_lstm_model(model, X_train, y_train, epochs=20, batch_size=32):
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)
    return model

# Predict using the trained model
def predict_lstm_model(model, X_test, scaler):
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)  # Inverse scale back to original values
    return predictions

# Evaluate the model using accuracy, precision, recall, and F1-score
def evaluate_model(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1}")
    
    return accuracy, precision, recall, f1

# Prepare data and train the model
time_steps = 60  # 60 previous time steps for each prediction
df = pd.read_csv('stock_data.csv')  # Load your dataset here
X, y, scaler = prepare_data(df, target_column=3, time_steps=time_steps)  # Example with 3rd column as target

X_train, X_test = X[:int(0.8 * len(X))], X[int(0.8 * len(X)):]
y_train, y_test = y[:int(0.8 * len(X))], y[int(0.8 * len(X)):]

# Create and train the LSTM model
lstm_model = create_lstm_model(X_train.shape)
lstm_model = train_lstm_model(lstm_model, X_train, y_train)

# Get predictions
predictions = predict_lstm_model(lstm_model, X_test, scaler)

# Convert predictions to binary (classification) based on a threshold, if necessary
y_pred_binary = (predictions > 0.5).astype(int)  # Adjust threshold if necessary

# Evaluate the model using metrics
accuracy, precision, recall, f1 = evaluate_model(y_test, y_pred_binary)

# Now you can save accuracy, precision, recall, and F1 score to the database as described before.
