# xgb_training.py
import sys
import pickle
import xgboost as xgb
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime
from database import models_DAOIMPL, model_metrics_history_DAOIMPL
from Models import model, model_metrics_history

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Convert predictions to binary based on target threshold
def convert_to_binary_with_tp1(predictions, tp1_values):
    return (predictions >= tp1_values).astype(int)

# Evaluate model based on future sell data
def evaluate_with_sell_data(df_test, predictions, time_steps=60):
    accuracy_list, precision_list, recall_list, f1_list = [], [], [], []
    
    for i in range(len(predictions)):
        sell_price = df_test['sold_pps'].iloc[i + time_steps]
        tp1_price = df_test['tp1'].iloc[i + time_steps]
        predicted_hit = max(predictions[i:i+12]) >= tp1_price
        y_pred = 1 if predicted_hit else 0
        y_true = 1 if sell_price >= tp1_price else 0

        accuracy_list.append(accuracy_score([y_true], [y_pred]))
        precision_list.append(precision_score([y_true], [y_pred], zero_division=0))
        recall_list.append(recall_score([y_true], [y_pred], zero_division=0))
        f1_list.append(f1_score([y_true], [y_pred], zero_division=0))
    
    avg_accuracy = np.mean(accuracy_list)
    avg_precision = np.mean(precision_list)
    avg_recall = np.mean(recall_list)
    avg_f1 = np.mean(f1_list)
    
    return avg_accuracy, avg_precision, avg_recall, avg_f1

# Train XGBoost model
def train_xgb_model(model_name, user_id):
    preprocessed_data = load_preprocessed_data()
    X_train = preprocessed_data['X_train']
    X_test = preprocessed_data['X_test']
    y_train = preprocessed_data['y_train']
    y_test = preprocessed_data['y_test']

    # Initialize and train the model
    xgb_model = xgb.XGBRegressor(objective="reg:squarederror", eval_metric="rmse")
    xgb_model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = xgb_model.predict(X_test)

    # Evaluate model
    avg_accuracy, avg_precision, avg_recall, avg_f1 = evaluate_with_sell_data(df_test, y_pred, time_steps=60)
    print(f"Accuracy: {avg_accuracy}, Precision: {avg_precision}, Recall: {avg_recall}, F1-Score: {avg_f1}")

    # Save model and store in database
    xgb_model.save_model('xgb_model.json')
    with open('xgb_model.json', 'rb') as model_file:
        model_binary = model_file.read()

    new_model = model.Model(model_name, "Base metrics XGBoost model", model_binary, user_id, selected=1)
    model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
    model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0])) if model_exists else models_DAOIMPL.insert_model_into_models_for_user(new_model)

    # Insert model metrics into the database
    new_history = model_metrics_history.Model_Metrics_History(model_id, avg_accuracy, avg_precision, avg_recall, avg_f1, '{}', datetime.now())
    model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
    print("Model training and metrics storage complete.")

# Main execution
if __name__ == "__main__":
    model_name = 'XGBoost'
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])  # Convert argument to integer
    else:
        raise ValueError("User ID not provided. Please pass the user ID as a command-line argument.")

    train_xgb_model(model_name, user_id)
