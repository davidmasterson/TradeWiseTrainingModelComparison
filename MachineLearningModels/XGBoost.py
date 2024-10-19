



import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import MinMaxScaler

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
df = pd.read_csv('101524-transactiondata.csv')

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
y = df['tp1']  # Target (continuous tp1 values)

# Scale the features using MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Initialize the XGBoost regression model
xgb_model = xgb.XGBRegressor(objective="reg:squarederror", eval_metric="rmse")

# Train the model
xgb_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = xgb_model.predict(X_test)

# Evaluation phase using future data (date_sold and sold_pps)
df_test = pd.read_csv('dataset.csv')  # Reload the dataset for testing phase

# Convert `y_pred` to binary by checking if it hits or exceeds the actual `tp1` values in y_test
def convert_to_binary_with_tp1(predictions, tp1_values):
    return (predictions >= tp1_values).astype(int)

# Prepare future columns (date_sold and sold_pps) for evaluation
# Compare the predictions with actual tp1 hit within 12 days
def evaluate_with_sell_data(df_test, predictions, time_steps):
    accuracy_list, precision_list, recall_list, f1_list = [], [], [], []
    
    for i in range(len(predictions)):
        sell_price = df_test['sold_pps'].iloc[i + time_steps]  # Actual sell price
        sell_date = df_test['date_sold'].iloc[i + time_steps]  # Actual sell date
        tp1_price = df_test['tp1'].iloc[i + time_steps]  # Target price
        
        # Evaluate if the max predicted price within 12 days hits tp1
        predicted_hit = max(predictions[i:i+12]) >= tp1_price
        
        # Binary outcome: 1 if target hit, 0 otherwise
        y_pred = 1 if predicted_hit else 0
        
        # Compare with actual sell price and date_sold
        if sell_price >= tp1_price:  # If actual sell price hit tp1, it's a "hit"
            y_true = 1
        else:
            y_true = 0
        
        # Calculate metrics
        accuracy = accuracy_score([y_true], [y_pred])
        precision = precision_score([y_true], [y_pred], zero_division=0)
        recall = recall_score([y_true], [y_pred], zero_division=0)
        f1 = f1_score([y_true], [y_pred], zero_division=0)
        
        # Store metrics
        accuracy_list.append(accuracy)
        precision_list.append(precision)
        recall_list.append(recall)
        f1_list.append(f1)
    
    # Aggregate metrics over the entire test set
    avg_accuracy = np.mean(accuracy_list)
    avg_precision = np.mean(precision_list)
    avg_recall = np.mean(recall_list)
    avg_f1 = np.mean(f1_list)
    
    return avg_accuracy, avg_precision, avg_recall, avg_f1

# Now evaluate the model using the actual future sell data
avg_accuracy, avg_precision, avg_recall, avg_f1 = evaluate_with_sell_data(df_test, y_pred, time_steps=60)

# Output the results
print(f"Accuracy: {avg_accuracy}")
print(f"Precision: {avg_precision}")
print(f"Recall: {avg_recall}")
print(f"F1-Score: {avg_f1}")

# Save the XGBoost model
xgb_model.save_model('xgb_model.json')

# Insert into the database (like LSTM example)
with open('xgb_model.json', 'rb') as model_file:
    model_binary = model_file.read()

if len(sys.argv) > 1:
        user_id = sys.argv[1]
user_id = int(user_id)
# Insert the model into the database
new_model = model.Model("XGBoost", model_binary,user_id,selected = False)
model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(new_model.model_name,user_id)
if model_exists:
    model_id = models_DAOIMPL.update_model_for_user(new_model,int(model_exists[0]))
else:
    model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
new_history = model_metrics_history.Model_Metrics_History(model_id, avg_accuracy, avg_precision, avg_recall, avg_f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
