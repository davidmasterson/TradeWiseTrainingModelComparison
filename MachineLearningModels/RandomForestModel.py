



import os
import sys
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model, user

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
df = pd.read_csv('dataset.csv')

# Assume you have columns 'tp1', 'sop', and a method to check if tp1 is hit before sop within 12 days
def check_target_hit(row):
    try:
        date_purchased = pd.to_datetime(row['date_purchased'])
        date_sold = pd.to_datetime(row['date_sold'])
        if date_sold.year == 0:  # Assuming pandas converts '0000-00-00' to year 0
            return None  # or return a default value or drop these rows altogether
    except Exception as e:
        print(f"Error parsing date for record: {row}")
        return None

    actual_return = row['actual_return']
    

    # Proceed if both dates are valid
    if date_sold > date_purchased:  # Simple check to ensure sold date is after purchased date
        days_difference = (date_sold - date_purchased).days
        if actual_return >= 0.00 and days_difference <= 12:
            return 1
    return 0

# Assuming df is your dataframe
df['date_purchased'] = pd.to_datetime(df['date_purchased'], errors='coerce')
df['date_sold'] = pd.to_datetime(df['date_sold'], errors='coerce')

# Filter out entries where dates could not be converted
df = df.dropna(subset=['date_purchased', 'date_sold'])

# Now apply your function
df['hit_tp1_within_12'] = df.apply(check_target_hit, axis=1)

# Calculate technical indicators
df['RSI'] = calculate_rsi(df['purchased_pps'], 14)
df['SMA'] = calculate_sma(df['purchased_pps'], 20)
df['EMA'] = calculate_ema(df['purchased_pps'], 20)
df['Momentum'] = calculate_momentum(df['purchased_pps'], 10)

df.fillna(0, inplace=True)

# Drop unnecessary columns
df = df.drop(columns=[ 'date_sold','sold_pps', 'total_sell_price', 'sell_string', 
                      'expected_return', 'percentage_roi', 'actual_return',
                      'stop_loss_price', 'tp2', 'purchase_string',
                      'symbol', 'date_purchased'])  # Including 'tp1' if it's not used as a feature

# Calculate technical indicators
df['RSI'] = calculate_rsi(df['purchased_pps'], 14)
df['SMA'] = calculate_sma(df['purchased_pps'], 20)
df['EMA'] = calculate_ema(df['purchased_pps'], 20)
df['Momentum'] = calculate_momentum(df['purchased_pps'], 10)

df.fillna(0, inplace=True)  # Handling NaN values after computing indicators

# Prepare features and target
X = df.drop(columns=['tp1', 'sop', 'hit_tp1_within_12'])  # Features excluding the target column and identifiers
y = df['hit_tp1_within_12']  # Binary target

# Continue with your scaling and training as before
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Initialize the Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the classifier
rf_classifier.fit(X_train, y_train)

# Predict on the test set
y_pred = rf_classifier.predict(X_test)

# Evaluate the classifier
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1}")

# Save and serialize the model
with open("rf_classifier.pkl", "wb") as model_file:
    pickle.dump(rf_classifier, model_file)

# Load and serialize the model for database storage
with open("rf_classifier.pkl", "rb") as model_file:
    model_binary = model_file.read()

user_id = int(user_id)
# Insert the model into the database
new_model = model.Model("RandomForestModel", model_binary,user_id,selected = False)
model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(new_model.model_name,user_id)
if model_exists:
    model_id = models_DAOIMPL.update_model_for_user(new_model,int(model_exists[0]))
else:
    model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
