# svm_training.py
import sys
import pickle
from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime
import joblib
from database import models_DAOIMPL, model_metrics_history_DAOIMPL
from Models import model, model_metrics_history

# Load preprocessed data
def load_preprocessed_data():
    with open('preprocessed_data.pkl', 'rb') as f:
        preprocessed_data = pickle.load(f)
    return preprocessed_data

# Convert predictions to binary based on a threshold
def convert_to_binary_with_tp1(predictions, tp1_values):
    return (predictions >= tp1_values).astype(int)

# Train the SVM model
def train_svm_model(model_name, user_id):
    # Load preprocessed data
    preprocessed_data = load_preprocessed_data()
    X_train = preprocessed_data['X_train']
    X_test = preprocessed_data['X_test']
    y_train = preprocessed_data['y_train']
    y_test = preprocessed_data['y_test']

    # Initialize and train the SVM model
    svm_model = svm.SVR()
    svm_model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = svm_model.predict(X_test)

    # Convert to binary for classification-style evaluation
    y_pred_binary = convert_to_binary_with_tp1(y_pred, y_test)
    y_test_binary = convert_to_binary_with_tp1(y_test, y_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test_binary, y_pred_binary)
    precision = precision_score(y_test_binary, y_pred_binary)
    recall = recall_score(y_test_binary, y_pred_binary)
    f1 = f1_score(y_test_binary, y_pred_binary)

    print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1-Score: {f1}")

    # Save the SVM model
    joblib.dump(svm_model, 'svm_model.pkl')
    with open('svm_model.pkl', 'rb') as model_file:
        model_binary = model_file.read()

    # Insert or update the model in the database
    new_model = model.Model(model_name, "Base metric SVM", model_binary, user_id, selected=1)
    model_exists = models_DAOIMPL.get_model_from_db_by_model_name_and_user_id(model_name, user_id)
    model_id = models_DAOIMPL.update_model_for_user(new_model, int(model_exists[0])) if model_exists else models_DAOIMPL.insert_model_into_models_for_user(new_model)

    # Insert model metrics into the database
    new_history = model_metrics_history.Model_Metrics_History(model_id, accuracy, precision, recall, f1, '{}', datetime.now())
    model_metrics_history_DAOIMPL.insert_metrics_history(new_history)
    print("Model training and metrics storage complete.")

# Main execution
if __name__ == "__main__":
    model_name = 'SupportVectorMachine'
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])  # Convert argument to integer
    else:
        raise ValueError("User ID not provided. Please pass the user ID as a command-line argument.")

    train_svm_model(model_name, user_id)
