# lstm_training.py
import sys
import pickle
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from database import models_DAOIMPL, model_metrics_history_DAOIMPL
from Models import model, model_metrics_history
from datetime import datetime

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_lstm_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Build LSTM model
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(input_shape[1], input_shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Train and evaluate LSTM model
def train_lstm_model(model_name, user_id):
    # Load preprocessed data
    preprocessed_data = load_preprocessed_data()
    X_train = preprocessed_data['X_train']
    X_test = preprocessed_data['X_test']
    y_train = preprocessed_data['y_train']
    y_test = preprocessed_data['y_test']
    scaler = preprocessed_data['scaler']

    # Create and train LSTM model
    lstm_model = create_lstm_model(X_train.shape)
    lstm_model.fit(X_train, y_train, epochs=20, batch_size=32)

    # Get predictions
    y_pred = lstm_model.predict(X_test)

    # Convert predictions for evaluation
    y_pred_binary = (y_pred >= y_test.mean()).astype(int)
    y_test_binary = (y_test >= y_test.mean()).astype(int)

    # Calculate metrics
    accuracy = accuracy_score(y_test_binary, y_pred_binary)
    precision = precision_score(y_test_binary, y_pred_binary)
    recall = recall_score(y_test_binary, y_pred_binary)
    f1 = f1_score(y_test_binary, y_pred_binary)

    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1-Score: {f1}")

    # Save model
    lstm_model.save('lstm_model.h5')
    with open("lstm_model.h5", "rb") as model_file:
        model_binary = model_file.read()

    # Insert model and metrics into the database
    new_model = model.Model(model_name, "Base metrics LSTM model", model_binary, user_id, selected=1)
    model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
    model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0])) if model_exists else models_DAOIMPL.insert_model_into_models_for_user(new_model)
    
    # Insert model metrics into database
    new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
    model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
    print("Model training and metrics storage complete.")

# Main execution block
if __name__ == "__main__":
    model_name = 'LSTM'
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])  # Convert argument to integer
    else:
        raise ValueError("User ID not provided. Please pass the user ID as a command-line argument.")

    train_lstm_model(model_name, user_id)
