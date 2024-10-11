import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
from sklearn.metrics import accuracy_score, precision_score, f1_score
import pandas as pd
from datetime import datetime

# Load the dataset
df = pd.read_csv('trans.csv')

# Convert date columns to datetime, invalid dates ('0000-00-00') will be set to NaT
df['date_purchased'] = pd.to_datetime(df['date_purchased'], errors='coerce')
df['date_sold'] = pd.to_datetime(df['date_sold'], errors='coerce')

# Remove rows where 'date_purchased' or 'date_sold' is NaT (i.e., invalid dates like '0000-00-00')
df = df.dropna(subset=['date_purchased', 'date_sold'])

# Calculate the number of days between purchase and sell
df['days_held'] = (df['date_sold'] - df['date_purchased']).dt.days

# Create the 'manual_prediction' column (since the algorithm always predicts 'buy')
df['manual_prediction'] = 1  # All trades are predicted as profitable

# Define success as: if actual return > 0 AND sold within 12 days
df['actual'] = df.apply(lambda row: 1 if row['actual_return'] > 0 and row['days_held'] <= 12 else 0, axis=1)

# Calculate accuracy, precision, and F1-Score based on this new 'actual' column
accuracy = accuracy_score(df['actual'], df['manual_prediction'])
precision = precision_score(df['actual'], df['manual_prediction'])
f1 = f1_score(df['actual'], df['manual_prediction'])

# Output the results
print(f"Manual Algorithm - Accuracy: {accuracy}")
print(f"Manual Algorithm - Precision: {precision}")
print(f"Manual Algorithm - F1-Score: {f1}")

# Save the model and store it in the database

from datetime import datetime

# Serialize model to binary
with open("MachineLearningModels/Manual_Algorithm12day.py", "rb") as model_file:
    model_binary = model_file.read()

# Insert the model into the database
new_model = model.Model("Manual_Algorithm12", model_binary)
model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)

# Insert the metrics into the metrics history table
new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, 0.00, f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
