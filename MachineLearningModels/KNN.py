

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime


if len(sys.argv) > 1:
        user_id = sys.argv[1]
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
df = pd.read_csv('/home/ubuntu/TradeWiseTrainingModelComparison/dataset.csv')

# Remove features you specified earlier
df = df.drop(columns=['date_sold', 'sold_pps', 'total_sell_price', 'sell_string', 
                      'expected_return', 'percentage_roi', 'actual_return', 
                      'stop_loss_price', 'tp2', 'sop', 'purchase_string'])

# Drop the 'symbol' and 'date_purchased' columns because they are non-numeric
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
y_continuous = df['tp1']  # Target (continuous tp1 values)

# **Binning/Encoding the `tp1` values**:
# You can define custom bins or use equal-width bins.
# Example: Divide tp1 into 10 bins (adjust the number of bins based on your data)
num_bins = 10  # Set the number of bins
y_binned, bin_edges = pd.cut(y_continuous, bins=num_bins, labels=False, retbins=True)

print(f"Binning edges: {bin_edges}")  # Optional: Print bin ranges for reference

# Scale the features using MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_binned, test_size=0.2, random_state=42)

# Initialize the KNN model
knn_model = KNeighborsClassifier(n_neighbors=5)

# Train the KNN model using the binned target labels
knn_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = knn_model.predict(X_test)

# Calculate evaluation metrics based on classification
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')  # Use 'weighted' for multi-class precision
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# Output the results
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1}")



# Save the KNN model (you can pickle the model instead)
import pickle
with open('knn_model.pkl', 'wb') as model_file:
    pickle.dump(knn_model, model_file)

# Insert into the database (like LSTM example)
with open('knn_model.pkl', 'rb') as model_file:
    model_binary = model_file.read()

if len(sys.argv) > 1:
        user_id = sys.argv[1]
model_name = 'KNN'
model_description = 'Base metrics KNN model'
user_id = int(user_id)

# Retrieve blob from database and 
stored_model = models_DAOIMPL.get_model_blob_from_db_by_model_name_and_user_id(model_name, user_id)

# Insert the model into the database
new_model = model.Model(model_name,model_description, model_binary,user_id,selected = 1)
model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(new_model.model_name,user_id)
if model_exists:
    model_id = models_DAOIMPL.update_model_for_user(new_model,int(model_exists[0]))
else:
    model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, 1, f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)