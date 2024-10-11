import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# Function to calculate technical indicators
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

# Load dataset
df = pd.read_csv('trans.csv')

# Remove specified columns
df = df.drop(columns=['date_sold', 'sold_pps', 'total_sell_price', 'sell_string', 
                      'expected_return', 'percentage_roi', 'actual_return', 
                      'stop_loss_price', 'tp2', 'sop', 'purchase_string'])

# Drop 'symbol' and 'date_purchased' columns
df = df.drop(columns=['symbol', 'date_purchased'])

# Calculate technical indicators
df['RSI'] = calculate_rsi(df['purchased_pps'], 14)
df['SMA'] = calculate_sma(df['purchased_pps'], 20)
df['EMA'] = calculate_ema(df['purchased_pps'], 20)
df['Momentum'] = calculate_momentum(df['purchased_pps'], 10)

# Ensure no NaN values after indicator calculations
df.fillna(0, inplace=True)

# Prepare features and target
X = df.drop(columns=['tp1'])  # Features (excluding the target column 'tp1')
y = df['tp1']  # Continuous target (tp1)

# Scale the features using MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Initialize the Random Forest Regressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
rf_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_model.predict(X_test)

# Convert predictions to binary by checking if it hits or exceeds the actual `tp1` values in y_test
def convert_to_binary_with_tp1(predictions, tp1_values):
    return (predictions >= tp1_values).astype(int)

# Convert predictions and actual values to binary
y_pred_binary = convert_to_binary_with_tp1(y_pred, y_test)
y_test_binary = convert_to_binary_with_tp1(y_test, y_test)

# Calculate evaluation metrics based on binary classification
accuracy = accuracy_score(y_test_binary, y_pred_binary)
precision = precision_score(y_test_binary, y_pred_binary)
recall = recall_score(y_test_binary, y_pred_binary)
f1 = f1_score(y_test_binary, y_pred_binary)

# Output the results
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1}")

# Save the model and store it in the database as described before


# Save the model and store it in the database
import pickle
from datetime import datetime
with open("rf_model.pkl", "wb") as model_file:
    pickle.dump(rf_model, model_file)

# Serialize model to binary
with open("rf_model.pkl", "rb") as model_file:
    model_binary = model_file.read()

# Insert the model into the database
new_model = model.Model("RandomForestModel", model_binary)
model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)

# Insert the metrics into the metrics history table
new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
