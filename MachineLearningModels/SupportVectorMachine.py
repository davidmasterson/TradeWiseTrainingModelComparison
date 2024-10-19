



import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Load dataset
df = pd.read_csv('101524-transactiondata.csv')

# Remove unwanted features
df = df.drop(columns=['date_sold', 'sold_pps', 'total_sell_price', 'sell_string', 
                      'expected_return', 'percentage_roi', 'actual_return', 
                      'stop_loss_price', 'tp2', 'sop', 'purchase_string'])

# Drop non-numeric columns
df = df.drop(columns=['symbol', 'date_purchased'])

# Prepare features and target
X = df.drop(columns=['tp1'])  # Features
y = df['tp1']  # Target

# Scale the features
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train SVM model (regression mode)
svm_model = svm.SVR()
svm_model.fit(X_train, y_train)

# Predict on the test set
y_pred = svm_model.predict(X_test)

# Convert to binary for classification-style evaluation
def convert_to_binary_with_tp1(predictions, tp1_values):
    return (predictions >= tp1_values).astype(int)

y_pred_binary = convert_to_binary_with_tp1(y_pred, y_test)
y_test_binary = convert_to_binary_with_tp1(y_test, y_test)

# Evaluate the model
accuracy = accuracy_score(y_test_binary, y_pred_binary)
precision = precision_score(y_test_binary, y_pred_binary)
recall = recall_score(y_test_binary, y_pred_binary)
f1 = f1_score(y_test_binary, y_pred_binary)

print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1-Score: {f1}")

# Save the SVM model
import joblib
from datetime import datetime
joblib.dump(svm_model, 'svm_model.pkl')

# Insert into the database
with open('svm_model.pkl', 'rb') as model_file:
    model_binary = model_file.read()

if len(sys.argv) > 1:
        user_id = sys.argv[1]


user_id = int(user_id)
# Insert the model into the database
new_model = model.Model("SupportVectorMachine", model_binary,user_id,selected = False)
model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(new_model.model_name,user_id)
if model_exists:
    model_id = models_DAOIMPL.update_model_for_user(new_model,int(model_exists[0]))
else:
    model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)