




import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import model_metrics_history_DAOIMPL, models_DAOIMPL
from Models import model_metrics_history, model
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load your dataset
df = pd.read_csv('/home/ubuntu/TradeWiseTrainingModelComparison/dataset.csv')

# Remove rows where 'date_sold' is '0000-00-00'
df = df[df['date_sold'] != '0000-00-00']

# Determine whether a trade was profitable
# 1 if actual_return > 0, 0 otherwise
df['profit'] = (df['actual_return'] > 0).astype(int)

# The manual algorithm predicted all trades as profitable (so y_pred is all 1s)
y_pred = [1] * len(df)

# The actual result based on profit
y_true = df['profit']

# Calculate the metrics
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

# Output the results
print(f"Manual Algorithm (Profit) - Accuracy: {accuracy}")
print(f"Manual Algorithm (Profit) - Precision: {precision}")
print(f"Manual Algorithm (Profit) - Recall: {recall}")
print(f"Manual Algorithm (Profit) - F1-Score: {f1}")

from datetime import datetime

# Serialize model to binary
with open("/home/ubuntu/TradeWiseTrainingModelComparison/MachineLearningModels/Manual_Algorithm.py", "rb") as model_file:
    model_binary = model_file.read()

user_id = 1
# Insert the model into the database
if len(sys.argv) > 1:
        user_id = sys.argv[1]

user_id = int(user_id)
model_name = 'Manual_Algorithm'
model_description = 'Manually configured stocksbot trading algorithm'
# Insert the model into the database
model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name,user_id)
if model_exists:
    new_model = model.Model(model_exists[1], model_exists[2], model_binary,user_id,selected = 1)
    model_id = models_DAOIMPL.update_model_for_user(new_model,int(model_exists[0]))
else:
    new_model = model.Model(model_name, model_description, model_binary,user_id,selected = 1)
    model_id = models_DAOIMPL.insert_model_into_models_for_user(new_model)
new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
model_metrics_history_DAOIMPL.insert_metrics_history(new_history)